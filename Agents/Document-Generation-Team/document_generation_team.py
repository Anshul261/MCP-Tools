import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter
from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.team import Team
from agno.models.azure import AzureOpenAI
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.db.sqlite import SqliteDb

# Note: File generation tools disabled for now - focusing on text output only
# from custom_file_tools import FILE_GENERATION_TOOLS, set_output_directory

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
DOCUMENTS_DIR = BASE_DIR / "documents"
CONVERTED_DIR = BASE_DIR / "converted_docs"
OUTPUT_DIR = BASE_DIR / "output"
TMP_DIR = BASE_DIR / "tmp"

# Ensure directories exist
for dir_path in [DOCUMENTS_DIR, CONVERTED_DIR, OUTPUT_DIR, TMP_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Note: File generation disabled for now
# set_output_directory(str(OUTPUT_DIR))


# ========================================
# OUTPUT SCHEMAS FOR STRUCTURED RESPONSES
# ========================================


class ResearchFindings(BaseModel):
    """Output schema for Research Agent"""

    query_summary: str = Field(..., description="Summary of what was searched")
    key_findings: List[str] = Field(..., description="Key facts and information found")
    sources: List[str] = Field(..., description="Sources from knowledge base")
    gaps: Optional[List[str]] = Field(
        default=None, description="Information gaps identified"
    )


class DocumentStructure(BaseModel):
    """Output schema for Analysis Agent"""

    document_title: str = Field(..., description="Proposed document title")
    document_type: str = Field(
        ..., description="Type of document (e.g., RFP, Technical Spec, Report)"
    )
    executive_summary: str = Field(..., description="Brief executive summary")
    key_themes: List[str] = Field(..., description="Main themes identified")
    recommendations: Optional[List[str]] = Field(
        default=None, description="Strategic recommendations"
    )


class GeneratedDocument(BaseModel):
    """Output schema for Writing Agent"""

    title: str = Field(..., description="Document title")
    executive_summary: str = Field(..., description="Executive summary")
    full_content: str = Field(..., description="Complete document content in markdown")
    word_count: int = Field(..., description="Approximate word count")


class RFPResponse(BaseModel):
    """Comprehensive RFP Response Schema"""

    title: str = Field(..., description="RFP response title")
    company_overview: str = Field(..., description="Company overview section")
    technical_architecture: str = Field(
        ..., description="Technical architecture details"
    )
    implementation_plan: str = Field(
        ..., description="Implementation methodology and timeline"
    )
    security_compliance: str = Field(..., description="Security and compliance details")
    executive_summary: str = Field(..., description="Executive summary")


class TechnicalSpecification(BaseModel):
    """Technical Specification Document Schema"""

    title: str = Field(..., description="Specification document title")
    overview: str = Field(..., description="System overview")
    architecture: str = Field(..., description="Architecture details")
    technical_requirements: List[str] = Field(
        ..., description="Technical requirements list"
    )
    security_features: str = Field(..., description="Security architecture")


class ProjectPlan(BaseModel):
    """Project Plan Document Schema"""

    title: str = Field(..., description="Project plan title")
    project_overview: str = Field(..., description="Project overview")
    phases: List[dict] = Field(..., description="Project phases with timelines")
    milestones: List[dict] = Field(..., description="Key milestones")
    timeline: str = Field(..., description="Overall timeline")


# ========================================
# HELPER FUNCTIONS
# ========================================


def convert_documents(src_dir: Path, out_dir: Path) -> int:
    """Convert documents using Docling"""
    if not src_dir.exists():
        print(f"Source directory {src_dir} doesn't exist. Creating it...")
        src_dir.mkdir(parents=True, exist_ok=True)
        print(f"Please add your documents to {src_dir}")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    converter = DocumentConverter()

    converted_count = 0
    for file in src_dir.iterdir():
        if not file.is_file() or file.suffix.lower() not in [
            ".pdf",
            ".docx",
            ".pptx",
            ".txt",
            ".md",
        ]:
            continue
        try:
            if file.suffix.lower() in [".txt", ".md"]:
                md_path = out_dir / f"{file.stem}.md"
                md_path.write_text(file.read_text())
                print(f"Copied {file.name} -> {md_path.name}")
            else:
                result = converter.convert(file)
                md_path = out_dir / f"{file.stem}.md"
                md_path.write_text(result.document.export_to_markdown())
                print(f"Converted {file.name} -> {md_path.name}")
            converted_count += 1
        except Exception as e:
            print(f"Error converting {file.name}: {e}")

    return converted_count


# Convert documents if any exist
if DOCUMENTS_DIR.exists():
    converted_count = convert_documents(DOCUMENTS_DIR, CONVERTED_DIR)
    if converted_count > 0:
        print(f"Converted {converted_count} documents")


# ========================================
# DATABASE AND KNOWLEDGE BASE SETUP
# ========================================

# Setup SQLite database for persistence
db = SqliteDb(db_file=str(TMP_DIR / "document_team.db"))

# Initialize knowledge base with LanceDB using local HuggingFace embedder
# Using local model to avoid API authentication issues
knowledge_base = Knowledge(
    vector_db=LanceDb(
        uri=str(TMP_DIR / "lancedb"),
        table_name="document_knowledge",
        search_type=SearchType.hybrid,
        embedder=HuggingfaceCustomEmbedder(
            id="BAAI/bge-small-en-v1.5",
            dimensions=384,
            api_key=os.getenv("HUGGINGFACE_HUB_TOKEN"),
        ),
    ),
)

# Load documents into knowledge base
if CONVERTED_DIR.exists() and any(CONVERTED_DIR.iterdir()):
    print("Loading knowledge base...")
    for doc_file in CONVERTED_DIR.iterdir():
        if doc_file.suffix in [".md", ".txt"]:
            knowledge_base.add_content(path=str(doc_file))
    print("Knowledge base loaded")
else:
    print("No documents found in knowledge base")


# Azure OpenAI model configuration
azure_model = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2025-01-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)


# ========================================
# AGENT DEFINITIONS
# ========================================

# Agent 1: Research Agent
research_agent = Agent(
    name="Research Agent",
    role="Search and extract relevant information from knowledge base",
    model=azure_model,
    description="Specialized in searching through documents and extracting key information",
    instructions=[
        "CRITICAL: Only use information DIRECTLY from the knowledge base documents",
        "Search the knowledge base thoroughly for relevant information",
        "Extract key facts, data points, and important details EXACTLY as they appear",
        "Never infer, assume, or use general knowledge - only use document content",
        "If specific information is not found, explicitly state 'Not found in documents'",
        "Always cite the exact source document for every fact",
        "Organize findings in a structured format",
        "Identify gaps in information clearly",
    ],
    output_schema=ResearchFindings,
    markdown=True,
)

# Agent 2: Analysis Agent
analysis_agent = Agent(
    name="Analysis Agent",
    role="Analyze research findings and create document structure",
    model=azure_model,
    description="Specialized in analyzing information and creating structured outlines",
    instructions=[
        "Analyze the research findings provided",
        "Identify key themes and patterns in the data",
        "Create a comprehensive document outline with clear sections",
        "Ensure information is organized hierarchically",
        "Highlight critical insights and recommendations",
    ],
    output_schema=DocumentStructure,
    markdown=True,
)

# Agent 3: Writing Agent
writing_agent = Agent(
    name="Writing Agent",
    role="Write comprehensive, well-structured documents",
    model=azure_model,
    description="Specialized in creating professional, detailed documents and reports",
    instructions=[
        "CRITICAL: Only write based on information provided by the Research Agent",
        "Do NOT add information from your general knowledge or training data",
        "Write clear, professional, and comprehensive content",
        "Follow the structure and outline provided",
        "Expand on key points with detailed explanations using ONLY the research findings",
        "Use appropriate tone and style for the document type",
        "Include executive summaries at the beginning",
        "Ensure content flows logically between sections",
        "Format content using markdown for readability",
        "If information is missing, state it clearly rather than making assumptions",
    ],
    output_schema=GeneratedDocument,
    markdown=True,
)

# Note: File Generation Agent removed - team now focuses on text output only


# ========================================
# TEAM CREATION WITH CUSTOM TOOLS
# ========================================


def create_document_team(output_schema=None):
    """
    Create a document generation team with custom file generation tools

    Args:
        output_schema: Optional Pydantic model for structured output

    Returns:
        Team instance configured for document generation
    """
    return Team(
        name="Document Generation Team",
        model=azure_model,
        members=[research_agent, analysis_agent, writing_agent],
        # tools=FILE_GENERATION_TOOLS,  # Disabled - no file generation for now
        knowledge=knowledge_base,
        db=db,
        description="Multi-agent team for generating comprehensive documents and reports",
        instructions=[
            "Generate comprehensive documents and reports based on knowledge base content",
            "Follow a sequential workflow:",
            "  1. Research Agent: Search knowledge base and gather information",
            "  2. Analysis Agent: Analyze findings and create structure",
            "  3. Writing Agent: Write detailed, well-structured content in markdown",
            "Ensure each agent builds upon the previous agent's work",
            "Always cite sources from the knowledge base",
            "Produce professional, publication-ready text documents",
        ],
        output_schema=output_schema,
        markdown=True,
        show_members_responses=True,
        add_datetime_to_context=True,
        add_history_to_context=True,
        num_history_runs=3,
        enable_user_memories=True,
        enable_session_summaries=True,
    )


# Default team
document_generation_team = create_document_team()


# ========================================
# UTILITY FUNCTIONS
# ========================================


def add_documents(file_or_dir_path: str):
    """Add new documents to the knowledge base"""
    path = Path(file_or_dir_path)
    if not path.exists():
        print(f"ERROR: Path {file_or_dir_path} does not exist")
        return

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    if path.is_file():
        dest = DOCUMENTS_DIR / path.name
        dest.write_bytes(path.read_bytes())
        print(f"Added {path.name} to document collection")
    elif path.is_dir():
        for file in path.iterdir():
            if file.is_file():
                dest = DOCUMENTS_DIR / file.name
                dest.write_bytes(file.read_bytes())
                print(f"Added {file.name} to document collection")

    # Convert new documents
    converted_count = convert_documents(DOCUMENTS_DIR, CONVERTED_DIR)
    if converted_count > 0:
        print("Reloading knowledge base...")
        for doc_file in CONVERTED_DIR.iterdir():
            if doc_file.suffix in [".md", ".txt"]:
                knowledge_base.add_content(path=str(doc_file))
        print("Knowledge base updated")


def get_team_for_document_type(doc_type: str) -> Team:
    """Get a team configured for a specific document type"""
    schema_map = {
        "rfp": RFPResponse,
        "technical": TechnicalSpecification,
        "project": ProjectPlan,
        "default": None,
    }

    output_schema = schema_map.get(doc_type.lower(), None)
    return create_document_team(output_schema=output_schema)


# ========================================
# INTERACTIVE SESSION
# ========================================


def interactive_session():
    """Interactive session for document generation"""
    print("\n" + "=" * 70)
    print("Document Generation Team - Interactive Session")
    print("=" * 70)
    print("\nAvailable commands:")
    print("  - Ask to generate any type of document or report")
    print("  - 'add <path>' - Add documents from file or directory")
    print("  - 'list' - List documents in knowledge base")
    print("  - 'schema <type>' - Set output schema (rfp/technical/project/default)")
    print("  - 'quit', 'exit', 'q' - End session")
    print("-" * 70)

    # Check knowledge base status
    if CONVERTED_DIR.exists() and any(CONVERTED_DIR.iterdir()):
        doc_count = len(list(CONVERTED_DIR.iterdir()))
        print(f"Knowledge base loaded with {doc_count} documents")
    else:
        print("No documents in knowledge base. Use 'add <path>' to add documents.")

    print("-" * 70)

    # Current team
    current_team = document_generation_team
    current_schema = "default"
    print(f"Current output schema: {current_schema}")
    print("-" * 70)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if user_input.lower().startswith("add "):
                file_path = user_input[4:].strip()
                if file_path:
                    add_documents(file_path)
                else:
                    print("ERROR: Please provide a file or directory path")
                continue

            if user_input.lower() == "list":
                if CONVERTED_DIR.exists():
                    docs = list(CONVERTED_DIR.iterdir())
                    if docs:
                        print(f"\nDocuments in knowledge base ({len(docs)}):")
                        for doc in docs:
                            print(f"  - {doc.name}")
                    else:
                        print("No documents in knowledge base")
                continue

            if user_input.lower().startswith("schema "):
                schema_type = user_input[7:].strip()
                if schema_type in ["rfp", "technical", "project", "default"]:
                    current_team = get_team_for_document_type(schema_type)
                    current_schema = schema_type
                    print(f"Switched to '{schema_type}' output schema")
                else:
                    print(
                        "ERROR: Invalid schema type. Choose: rfp, technical, project, default"
                    )
                continue

            # Process document generation request
            print("\n" + "=" * 70)
            print(f"Document Generation Team Working (Schema: {current_schema})...")
            print("=" * 70 + "\n")

            # Get the response
            response = current_team.run(user_input)

            # Print the response
            if response and response.content:
                print(response.content)

                # Save to file
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = OUTPUT_DIR / f"response_{current_schema}_{timestamp}.txt"
                output_file.write_text(str(response.content))
                print(f"\n\nFull response saved to: {output_file}")

            print("\n" + "=" * 70)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback

            traceback.print_exc()
            print("Please try again.")


if __name__ == "__main__":
    interactive_session()
