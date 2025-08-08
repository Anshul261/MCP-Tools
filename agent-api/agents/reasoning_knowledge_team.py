import os
from pathlib import Path
from textwrap import dedent
from typing import Optional
from dotenv import load_dotenv

from agno.agent import Agent
from agno.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.models.azure import AzureOpenAI
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.pgvector import PgVector, SearchType
from agno.tools.bravesearch import BraveSearchTools
from agno.tools.reasoning import ReasoningTools
from agno.team.team import Team
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.agent.postgres import PostgresAgentStorage
from docling.document_converter import DocumentConverter

from db.session import db_url

# Load environment variables
load_dotenv()

def setup_knowledge_base() -> TextKnowledgeBase:
    """Setup and return the knowledge base with document processing"""
    
    SRC_DIR = Path("documents")
    CONVERTED_DIR = Path("converted_docs")
    
    def convert_documents(src_dir: Path, out_dir: Path) -> int:
        """Convert documents using Docling"""
        if not src_dir.exists():
            print(f"Source directory {src_dir} doesn't exist. Creating it...")
            src_dir.mkdir(parents=True, exist_ok=True)
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
    
    # Convert documents if any exist
    if SRC_DIR.exists():
        converted_count = convert_documents(SRC_DIR, CONVERTED_DIR)
        if converted_count > 0:
            print(f"Converted {converted_count} documents")
    
    # Create local embedder using HuggingFace
    embedder = HuggingfaceCustomEmbedder(
        id="BAAI/bge-small-en-v1.5",
        dimensions=384
    )
    
    # Create vector database using the same PostgreSQL instance
    vector_db = PgVector(
        table_name="reasoning_team_documents",
        db_url=db_url,
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
    
    return kb

def get_azure_models():
    """Get configured Azure models"""
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
    
    return azure_model, azure_model_04

def get_reasoning_knowledge_team(
    model_id: str = "gpt-4.1",  # This parameter is kept for API compatibility but we use Azure
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Team:
    """Create and return the Reasoning Knowledge Team"""
    
    # Get Azure models
    azure_model, azure_model_04 = get_azure_models()
    
    # Setup knowledge base
    kb = setup_knowledge_base()
    
    # Create memory using PostgreSQL (same as other agents)
    memory = Memory(
        model=azure_model,
        db=PostgresMemoryDb(table_name="reasoning_team_memories", db_url=db_url),
        delete_memories=True,
        clear_memories=True,
    )
    
    # Create storage using PostgreSQL
    storage = PostgresAgentStorage(
        table_name="reasoning_team_sessions", 
        db_url=db_url
    )
    
    # Create document agent
    doc_agent = Agent(
        name="Doc Agent",
        role="Handles local document search",
        knowledge=kb,
        model=azure_model,
        memory=memory,
        storage=storage,
        user_id=user_id,
        session_id=session_id,
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
        show_tool_calls=debug_mode,
        markdown=True,
    )
    
    # Create web agent
    web_agent = Agent(
        name="Web Agent",
        role="Handles web search and news",
        model=azure_model,
        memory=memory,
        storage=storage,
        user_id=user_id,
        session_id=session_id,
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
            dedent("""\
            Example:
            Question: What is the latest news in the stock market?
            Answer: The latest news in the stock market is that the stock market is up 1% today.
            Citations: [Source 1, Source 2, Source 3]
            """),
        ],
        show_tool_calls=debug_mode,
        markdown=True,
    )
    
    # Create team
    reasoning_knowledge_team = Team(
        name="Reasoning Knowledge Team",
        agent_id="reasoning_knowledge_team",
        user_id=user_id,
        session_id=session_id,
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
        show_members_responses=debug_mode,
        enable_agentic_context=True,
        add_datetime_to_instructions=True,
        success_criteria="Complete analysis with proper citations and continuity from previous conversations",
        debug_mode=debug_mode,
    )
    
    return reasoning_knowledge_team

def add_documents(file_or_dir_path: str):
    """Add new documents to the knowledge base (utility function)"""
    SRC_DIR = Path("documents")
    CONVERTED_DIR = Path("converted_docs")
    
    path = Path(file_or_dir_path)
    if not path.exists():
        print(f"Path {file_or_dir_path} does not exist")
        return
    
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    
    if path.is_file():
        dest = SRC_DIR / path.name
        dest.write_bytes(path.read_bytes())
        print(f"Added {path.name} to document collection")
    elif path.is_dir():
        for file in path.iterdir():
            if file.is_file():
                dest = SRC_DIR / file.name
                dest.write_bytes(file.read_bytes())
                print(f"Added {file.name} to document collection")
    
    # Recreate knowledge base to include new documents
    kb = setup_knowledge_base()
    print("Knowledge base updated with new documents")