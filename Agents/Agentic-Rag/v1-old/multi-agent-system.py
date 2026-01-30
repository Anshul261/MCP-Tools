import os
from pathlib import Path
from dotenv import load_dotenv
from agno.tools.mcp import MCPTools
import base64

# Load environment variables
load_dotenv()
from agno.storage.sqlite import SqliteStorage
from docling.document_converter import DocumentConverter
from agno.agent import Agent
from agno.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.models.azure import AzureOpenAI
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.pgvector import PgVector, SearchType
from agno.tools.bravesearch import BraveSearchTools
from agno.tools.reasoning import ReasoningTools
from agno.team.team import Team
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.memory.v2.schema import UserMemory
import uuid
from datetime import datetime

from openinference.instrumentation.agno import AgnoInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor


# Create memory database with proper configuration
MEMORY_DB_PATH = "agent_memory.db"
memory_db = SqliteMemoryDb(
    table_name="agent_memory",
    db_file=MEMORY_DB_PATH
)

# Initialize memory with proper configuration
memory = Memory(
    db=memory_db,
)

# Create storage for session persistence
STORAGE_DB_PATH = "agent_sessions.db"
storage = SqliteStorage(
    table_name="agent_sessions",
    db_file=STORAGE_DB_PATH
)


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


# Set environment variables for Langfuse
LANGFUSE_AUTH = base64.b64encode(
    f"{os.getenv('LANGFUSE_PUBLIC_KEY_ag')}:{os.getenv('LANGFUSE_SECRET_KEY_ag')}".encode()
).decode()
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:3000/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
trace_api.set_tracer_provider(tracer_provider=tracer_provider)

AgnoInstrumentor().instrument()

# Database configuration
DB_URL = os.getenv("DB_URL") or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
TABLE_NAME = os.getenv("PGVECTOR_TABLE", "rag_documents")

# Create local embedder using HuggingFace
embedder = HuggingfaceCustomEmbedder(
        id="BAAI/bge-small-en-v1.5",
        dimensions=384,
        api_key=os.getenv("HUGGINGFACE_HUB_TOKEN")
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
    kb.load(recreate=False)
    print("Knowledge base loaded")

# Shared model configuration
azure_model = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

azure_model_04 = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_o4"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY_o4"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_o4"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_o4"),
)

azure_model_5 = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_5"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY_5"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_5"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_5"),
)

# Create document agent with memory
doc_agent = Agent(
    name="Doc Agent",
    role="Handles local document search",
    knowledge=kb,
    model=azure_model,
    memory=memory,
    storage=storage,
    enable_user_memories=True,
    enable_session_summaries=True,
    enable_agentic_memory=True,
    add_history_to_messages=True,
    num_history_runs=6,
    description="RAG Assistant with local document search capabilities",
    instructions=[
        "You are a helpful AI assistant with access to local documents",
        "Search through the local knowledge base for relevant information",
        "Always cite your sources clearly from local documents",
        "Be accurate and provide comprehensive answers based on available context",
        "Remember previous conversations and build upon them"
    ],
    search_knowledge=True,
    show_tool_calls=True,
    markdown=True,
)

# Create web agent with memory
web_agent = Agent(
    name="Web Agent",
    role="Handles web search and news",
    model=azure_model,
    memory=memory,
    enable_user_memories=True,
    enable_session_summaries=True,
    enable_agentic_memory=True,
    add_history_to_messages=True,
    num_history_runs=6,

    tools=[BraveSearchTools()],
    description="News agent that helps users find the latest news",
    instructions=[
        "Given a topic by the user, search for results about that topic",
        "Iteratively search for more news items until you have comprehensive information",
        "Always provide citations for sources used to answer questions",
        "Remember previous searches and conversations to provide better context",
        """Example:
        Question: What is the latest news in the stock market?
        Answer: The latest news in the stock market is that the stock market is up 1% today.
        Citations: [Source 1, Source 2, Source 3]""",
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create team with memory
reasoning_knowledge_team = Team(
    name="Reasoning Knowledge Team",
    mode="coordinate",
    model=azure_model,
    members=[web_agent, doc_agent],
    tools=[ReasoningTools(add_instructions=True)],
    memory=memory,
    storage=storage,
    enable_user_memories=True,
    enable_session_summaries=True,
    enable_agentic_memory=True,
    add_history_to_messages=True,
    num_history_runs=6,

    instructions=[
        "You coordinate between document search and web search agents",
        "First try local documents, then web search if needed",
        "Always cite sources clearly",
        "Remember previous conversations and build upon them",
        "Provide comprehensive answers with proper context"
    ],
    markdown=True,
    show_members_responses=True,
    enable_agentic_context=True,
    add_datetime_to_instructions=True,
    success_criteria="Complete analysis with proper citations and continuity from previous conversations",
)

def check_memory_status():
    """Check memory database status"""
    print(f"\n=== Memory Database Status ===")
    memory_db_path = Path(MEMORY_DB_PATH)
    storage_db_path = Path(STORAGE_DB_PATH)
    
    print(f"Memory DB exists: {memory_db_path.exists()}")
    if memory_db_path.exists():
        print(f"Memory DB size: {memory_db_path.stat().st_size} bytes")
    
    print(f"Storage DB exists: {storage_db_path.exists()}")
    if storage_db_path.exists():
        print(f"Storage DB size: {storage_db_path.stat().st_size} bytes")

def interactive_chat():
    """Interactive chat interface"""
    print("=== AI Assistant Chat Interface ===")
    print("Type 'quit', 'exit', or 'q' to end the session")
    print("Type 'memory' to check memory database status")
    print("Type 'new' to start a new session")
    print("-" * 50)
    
    # Get user ID
    user_id = input("Enter your user ID (or press Enter for default): ").strip()
    if not user_id:
        user_id = "default_user"
    
    # Generate session ID with timestamp
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}")
    print("-" * 50)
    
    while True:
        try:
            # Get user input
            user_question = input("\nYou: ").strip()
            
            # Handle special commands
            if user_question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_question.lower() == 'memory':
                check_memory_status()
                continue
            elif user_question.lower() == 'new':
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
                print(f"Started new session: {session_id}")
                continue
            elif not user_question:
                continue
            
            print("\nAssistant:")
            print("-" * 30)
            
            # Get response from the team
            reasoning_knowledge_team.print_response(
                user_question,
                user_id=user_id,
                session_id=session_id,
                stream=True,
                show_full_reasoning=False,  # Set to True for debugging
                stream_intermediate_steps=False,  # Set to True for debugging
            )
            
        except KeyboardInterrupt:
            print("\n\nChat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")

if __name__ == "__main__":
    interactive_chat()
