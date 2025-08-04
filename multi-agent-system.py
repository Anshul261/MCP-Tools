
import os
from pathlib import Path
from dotenv import load_dotenv
from agno.tools.mcp import MCPTools

# Load environment variables
load_dotenv()
from agno.storage.sqlite import SqliteStorage
from docling.document_converter import DocumentConverter
from agno.agent import Agent
from agno.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.models.azure import AzureOpenAI
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.pgvector import PgVector, SearchType
import requests
from agno.agent import Agent
from agno.tools.bravesearch import BraveSearchTools
from agno.tools.reasoning import ReasoningTools
from agno.team.team import Team
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory

memory_db = SqliteMemoryDb(table_name="memory", db_file="memory.db")
memory = Memory(db=memory_db)

def add_documents(file_or_dir_path: str, src_dir: Path, converted_dir: Path, kb: TextKnowledgeBase):
    """Add new documents to the knowledge base"""
    path = Path(file_or_dir_path)
    if not path.exists():
        print(f"Path {file_or_dir_path} does not exist")
        return
    
    src_dir.mkdir(parents=True, exist_ok=True)
    
    if path.is_file():
        dest = src_dir / path.name
        dest.write_bytes(path.read_bytes())
        print(f"Added {path.name} to document collection")
    elif path.is_dir():
        for file in path.iterdir():
            if file.is_file():
                dest = src_dir / file.name
                dest.write_bytes(file.read_bytes())
                print(f"Added {file.name} to document collection")
    
    # Convert new documents
    converted_count = convert_documents(src_dir, converted_dir)
    if converted_count > 0:
        print("Reloading knowledge base...")
        kb.load(recreate=True)
        print("Knowledge base updated")

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
        if not file.is_file() or file.suffix.lower() not in ['.pdf', '.docx', '.pptx', '.txt']:
            continue
        try:
            result = converter.convert(file)
            md_path = out_dir / f"{file.stem}.md"
            md_path.write_text(result.document.export_to_markdown())
            print(f"Converted {file.name} ➜ {md_path.name}")
            converted_count += 1
        except Exception as e:
            print(f"Error converting {file.name}: {e}")
    
    return converted_count

SRC_DIR = Path("documents")
CONVERTED_DIR = Path("converted_docs")

# Convert documents if any exist
if SRC_DIR.exists():
    converted_count = convert_documents(SRC_DIR, CONVERTED_DIR)
    if converted_count > 0:
        print(f"Converted {converted_count} documents")

# Database configuration
DB_URL = os.getenv("DB_URL") or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
TABLE_NAME = os.getenv("PGVECTOR_TABLE", "rag_documents")

# Create local embedder using HuggingFace
embedder = HuggingfaceCustomEmbedder(
    id="BAAI/bge-small-en-v1.5",  # Fast and efficient local model
    dimensions=384  # BGE small model has 384 dimensions
)

# Create vector database
vector_db = PgVector(
    table_name=TABLE_NAME,
    db_url=DB_URL,
    search_type=SearchType.hybrid,
    embedder=embedder,
)

# Create knowledge base
kb = TextKnowledgeBase(
    path=str(CONVERTED_DIR),
    formats=[".md", ".txt"],
    vector_db=vector_db,
)

# Load knowledge base if documents exist
if CONVERTED_DIR.exists() and any(CONVERTED_DIR.iterdir()):
    print("Loading knowledge base...")
    kb.load(recreate=False)  # Set to True to rebuild
    print("Knowledge base loaded")

# Initialize web search tool
brave_search = None
brave_api_key = os.getenv('BRAVE_API_KEY')
if brave_api_key:
        mcp_command = f"python {os.path.abspath('/home/anshul/Projects/AI-Search-MCP/Web-Search/server.py')}"
        mcp_tools = MCPTools(command=mcp_command)
        print("MCP tools initialized {}".format(mcp_tools))


# Create agent
doc_agent = Agent(
    name="Doc Agent",
    role="Handles local document search",
    knowledge=kb,
    model=AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    ),
    description="RAG Assistant with local document search and web search capabilities",
    instructions=[
        "You are a helpful AI assistant with access to local documents and web search",
        "First search through the local knowledge base for relevant information",
        "If the local documents don't contain sufficient information, use the mcp_tools for online search/web search to find current information",
        "Always cite your sources clearly, indicating whether information comes from local documents or web sources using the research_search or smart_search tools",
        "Be accurate and provide comprehensive answers based on available context",
        "When using web search, summarize the key findings from multiple sources"
    ],
    search_knowledge=True,
    show_tool_calls=True,
    num_history_responses=6,
    markdown=True,
)


web_agent = Agent(
    name="Web Agent",
    role="Handles web search and news",
    model=AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    ),
    tools=[BraveSearchTools()],
    description="You are a news agent that helps users find the latest news.",
    instructions=[
        """Given a topic by the user, respond the results about that topic. 
        Iteratively search for more news items until you have a comprehensive list or a specific answer you have to provide citations for the sources you used to answer the question
        Example:
        Question: What is the latest news in the stock market?
        Answer: The latest news in the stock market is that the stock market is up 1% today.
        Citations: [Source 1, Source 2, Source 3]"""
    ],
    show_tool_calls=True,
    markdown=True,
    num_history_responses=6,
)


reaonsing_knowledge_team = Team(
    name="Reasoning Knowledge Team",
    mode="coordinate",
    model=AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    ),
    members=[web_agent, doc_agent],
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        """You are a helpful AI assistant with access to local documents and web search
        First search through the local knowledge base for relevant information
        If the local documents don't contain sufficient information, use the mcp_tools for online search/web search to find current information
        Always cite your sources clearly, indicating whether information comes from local documents or web sources using the research_search or smart_search tools
        Be accurate and provide comprehensive answers based on available context
        When using web search, summarize the key findings from multiple sources"""
    ],
    markdown=True,
    memory=memory,
    show_members_responses=True,
    enable_agentic_context=True,
    add_datetime_to_instructions=True,
    success_criteria="The team has provided a complete financial analysis with data, visualizations, risk assessment, and actionable investment recommendations supported by quantitative analysis and market research.",
)

if __name__ == "__main__":
    reaonsing_knowledge_team.print_response("""What is the leave policy of the company?""",
        stream=True,
        show_full_reasoning=True,
        stream_intermediate_steps=True,
    )