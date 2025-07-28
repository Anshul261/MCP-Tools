"""
RAG Agent using Agno framework with Azure OpenAI, Docling, and Brave Search
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from docling.document_converter import DocumentConverter
from agno.agent import Agent
from agno.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.models.azure import AzureOpenAI
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.pgvector import PgVector, SearchType
import requests


class BraveSearchTool:
    """Brave Search integration as an Agno tool"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }
    
    def web_search(self, query: str) -> str:
        """Search the web using Brave Search API"""
        if not self.api_key:
            return "Web search not available - BRAVE_API_KEY not configured"
        
        try:
            params = {
                "q": query,
                "count": 5,
                "country": "US",
                "search_lang": "en"
            }
            
            response = requests.get(
                f"{self.base_url}/web/search",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            results = data.get('web', {}).get('results', [])
            if not results:
                return f"No web results found for: {query}"
            
            search_summary = f"Web search results for '{query}':\n\n"
            for i, result in enumerate(results, 1):
                search_summary += f"{i}. {result.get('title', 'No title')}\n"
                search_summary += f"   {result.get('description', 'No description')}\n"
                search_summary += f"   URL: {result.get('url', 'No URL')}\n\n"
            
            return search_summary
            
        except Exception as e:
            return f"Web search error: {str(e)}"


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


def create_rag_agent():
    """Create and configure the RAG Agent"""
    # Paths
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
        brave_search = BraveSearchTool(brave_api_key)
    
    # Create agent
    agent = Agent(
        model=AzureOpenAI(
            id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        ),
        knowledge=kb,
        tools=[brave_search.web_search] if brave_search else None,
        description="RAG Assistant with local document search and web search capabilities",
        instructions=[
            "You are a helpful AI assistant with access to local documents and web search.",
            "First search through the local knowledge base for relevant information.",
            "If the local documents don't contain sufficient information, use the web_search tool to find current information.",
            "Always cite your sources clearly, indicating whether information comes from local documents or web sources.",
            "Be accurate and provide comprehensive answers based on available context.",
            "When using web search, summarize the key findings from multiple sources."
        ],
        search_knowledge=True,
        show_tool_calls=True,
        markdown=True,
    )
    
    return agent, SRC_DIR, CONVERTED_DIR, kb


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


def interactive_session():
    """Run an interactive Q&A session"""
    print("\n RAG Agent Interactive Session")
    print("Available commands:")
    print("  - Ask any question (e.g., 'What is machine learning?')")
    print("  - 'add <path>' - Add documents from file or directory")
    print("  - 'quit', 'exit', 'q' - End session")
    print("-" * 50)
    
    # Create agent
    try:
        agent, src_dir, converted_dir, kb = create_rag_agent()
        print(" Agent initialized successfully!")
    except Exception as e:
        print(f" Failed to initialize agent: {e}")
        return
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                print("Please enter a question or command.")
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.lower().startswith('add '):
                file_path = user_input[4:].strip()
                if file_path:
                    add_documents(file_path, src_dir, converted_dir, kb)
                else:
                    print("Please provide a file or directory path after 'add'")
                continue
            
            # Check if the input looks like a shell command by mistake
            if user_input.startswith(('ls', 'cd', 'pwd', 'mkdir', 'rm', 'cp', 'mv')):
                print("This looks like a shell command. I'm an AI assistant - please ask me a question instead!")
                print("Example: 'What is machine learning?' or 'Tell me about Python programming'")
                continue
            
            # Process the question
            print("\nAssistant:")
            try:
                agent.print_response(user_input, stream=True)
            except Exception as e:
                print(f"Error generating response: {e}")
                print("Please try rephrasing your question.")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again or type 'quit' to exit.")


def main():
    """Main function"""
    print("RAG Agent with Agno Framework")
    print("=" * 40)
    
    # Check configuration
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY", 
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f" Missing required environment variables: {missing_vars}")
        print("Please check your .env file")
        return
    
    # Show configuration
    print(f"Azure OpenAI Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    print(f"Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}")
    print(f"Database: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
    print(f"Web Search: {'Enabled' if os.getenv('BRAVE_API_KEY') else 'Disabled'}")
    
    # Check documents
    converted_dir = Path("converted_docs")
    if converted_dir.exists() and any(converted_dir.iterdir()):
        doc_count = len(list(converted_dir.iterdir()))
        print(f" Documents: {doc_count} files in knowledge base")
    else:
        print(" No documents found. Add some documents using 'add <path>' command")
    
    print("\n" + "="*40)
    
    # Start interactive session
    interactive_session()


if __name__ == "__main__":
    main()