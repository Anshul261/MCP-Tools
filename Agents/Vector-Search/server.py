import sys
import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Load environment variables from .env file
    from dotenv import load_dotenv
    
    # Load .env from the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, '.env')
    load_dotenv(env_path)

    from mcp.server.fastmcp import FastMCP
    
except ImportError as e:
    print(f"❌ Import error: {e}", file=sys.stderr)
    print("Make sure to install required packages: pip install mcp docling agno python-dotenv", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error during imports: {e}", file=sys.stderr)
    sys.exit(1)

# Configure logging to stderr (important for MCP)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Use stderr for logging in MCP
)
logger = logging.getLogger("rag-mcp-server")

# Global variables for lazy loading
kb: Optional[Any] = None
embedder: Optional[Any] = None
vector_db: Optional[Any] = None
converter: Optional[Any] = None
_dependencies_loaded = False
_initialization_error: Optional[str] = None

# Initialize the FastMCP server
mcp = FastMCP("RAG Document Server")

# Add some logging to show server is initializing
logger.info("🚀 Initializing RAG MCP Server...")
logger.info("📡 Server ready to accept connections")

# Paths
SRC_DIR = Path("documents")
CONVERTED_DIR = Path("converted_docs")

class RAGServerError(Exception):
    """Custom exception for RAG server errors"""
    pass

def _load_dependencies():
    """Load heavy dependencies only when needed"""
    global converter, embedder, vector_db, kb, _dependencies_loaded, _initialization_error
    
    if _dependencies_loaded:
        return True
    
    try:
        logger.info("Loading RAG dependencies...")
        
        from docling.document_converter import DocumentConverter
        from agno.embedder.huggingface import HuggingfaceCustomEmbedder
        from agno.knowledge.text import TextKnowledgeBase
        from agno.vectordb.pgvector import PgVector, SearchType
        
        # Create directories
        SRC_DIR.mkdir(parents=True, exist_ok=True)
        CONVERTED_DIR.mkdir(parents=True, exist_ok=True)
        
        # Check required environment variables
        required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME", "DB_PORT"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            _initialization_error = f"Missing required environment variables: {missing_vars}"
            logger.error(_initialization_error)
            return False
        
        # Initialize components
        converter = DocumentConverter()
        logger.info("Document converter initialized")
        
        # Database configuration
        DB_URL = os.getenv("DB_URL") or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        TABLE_NAME = os.getenv("PGVECTOR_TABLE", "rag_documents")
        
        # Create embedder
        embedder = HuggingfaceCustomEmbedder(
            id="BAAI/bge-small-en-v1.5",
            dimensions=384
        )
        logger.info("Embedder initialized")
        
        # Create vector database
        vector_db = PgVector(
            table_name=TABLE_NAME,
            db_url=DB_URL,
            search_type=SearchType.hybrid,
            embedder=embedder,
        )
        logger.info("Vector database initialized")
        
        # Create knowledge base
        kb = TextKnowledgeBase(
            path=str(CONVERTED_DIR),
            formats=[".md", ".txt"],
            vector_db=vector_db,
        )
        logger.info("Knowledge base initialized")
        
        # Load existing documents if any
        if CONVERTED_DIR.exists() and any(CONVERTED_DIR.iterdir()):
            logger.info("Loading existing knowledge base...")
            kb.load(recreate=False)
            doc_count = len(list(CONVERTED_DIR.iterdir()))
            logger.info(f"Knowledge base loaded with {doc_count} documents")
        else:
            logger.info("No existing documents found")
        
        _dependencies_loaded = True
        logger.info("All RAG components initialized successfully")
        return True
        
    except Exception as e:
        _initialization_error = f"Failed to load dependencies: {str(e)}"
        logger.error(_initialization_error)
        return False

def _ensure_initialized():
    """Ensure components are initialized, return error message if not"""
    if not _dependencies_loaded:
        if not _load_dependencies():
            return _initialization_error or "Failed to initialize server components"
    return None

@mcp.tool()
def search_documents(query: str, limit: int = 5) -> str:
    """
    Search through the local knowledge base documents
    
    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 5)
    
    Returns:
        Formatted search results with relevant document excerpts
    """
    logger.info(f"Searching documents for query: {query}")
    
    error = _ensure_initialized()
    if error:
        logger.error(f"Initialization failed: {error}")
        return f"Server initialization failed: {error}"
    
    if not kb:
        return "Knowledge base not available"
    
    try:
        results = kb.search(query, num_documents=limit)
        
        if not results:
            logger.info(f"No results found for query: {query}")
            return f"No results found for query: '{query}'"
        
        formatted_results = f"Search results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            content = result.get('content', 'No content available')
            source = result.get('source', 'Unknown source')
            score = result.get('score', 'No score')
            
            formatted_results += f"Result {i}:\n"
            formatted_results += f"Source: {source}\n"
            if score != 'No score':
                formatted_results += f"Relevance Score: {score:.3f}\n"
            formatted_results += f"Content: {content[:500]}{'...' if len(content) > 500 else ''}\n\n"
        
        logger.info(f"Found {len(results)} results for query: {query}")
        return formatted_results
        
    except Exception as e:
        error_msg = f"Error searching documents: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def get_server_status() -> str:
    """
    Get the current status of the RAG server
    
    Returns:
        Server status and configuration information
    """
    try:
        status = "RAG Server Status:\n\n"
        
        # Try to load dependencies if not already loaded
        error = _ensure_initialized()
        
        if error:
            status += f"❌ Initialization Error: {error}\n\n"
            return status
        
        # Component status
        status += "Components:\n"
        status += f"  • Knowledge Base: {'✓ Initialized' if kb else '✗ Not initialized'}\n"
        status += f"  • Embedder: {'✓ Initialized' if embedder else '✗ Not initialized'}\n"
        status += f"  • Vector DB: {'✓ Initialized' if vector_db else '✗ Not initialized'}\n"
        status += f"  • Document Converter: {'✓ Initialized' if converter else '✗ Not initialized'}\n\n"
        
        # Configuration
        status += "Configuration:\n"
        status += f"  • Documents Directory: {SRC_DIR} ({'exists' if SRC_DIR.exists() else 'missing'})\n"
        status += f"  • Converted Directory: {CONVERTED_DIR} ({'exists' if CONVERTED_DIR.exists() else 'missing'})\n"
        status += f"  • Database Host: {os.getenv('DB_HOST', 'Not configured')}\n"
        status += f"  • Database Name: {os.getenv('DB_NAME', 'Not configured')}\n"
        status += f"  • Embedder Model: BAAI/bge-small-en-v1.5\n\n"
        
        # Document counts
        original_count = len([f for f in SRC_DIR.iterdir() if f.is_file()]) if SRC_DIR.exists() else 0
        converted_count = len([f for f in CONVERTED_DIR.iterdir() if f.is_file()]) if CONVERTED_DIR.exists() else 0
        
        status += "Documents:\n"
        status += f"  • Original Documents: {original_count}\n"
        status += f"  • Converted Documents: {converted_count}\n"
        
        logger.info("Server status requested")
        return status
        
    except Exception as e:
        error_msg = f"Error getting server status: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def list_documents() -> str:
    """
    List all documents in the knowledge base
    
    Returns:
        Formatted list of all documents with metadata
    """
    try:
        # List original documents
        original_docs = []
        if SRC_DIR.exists():
            for file in SRC_DIR.iterdir():
                if file.is_file():
                    original_docs.append({
                        "name": file.name,
                        "size": file.stat().st_size,
                        "modified": file.stat().st_mtime
                    })
        
        # List converted documents
        converted_docs = []
        if CONVERTED_DIR.exists():
            for file in CONVERTED_DIR.iterdir():
                if file.is_file():
                    converted_docs.append({
                        "name": file.name,
                        "size": file.stat().st_size,
                        "modified": file.stat().st_mtime
                    })
        
        result = "Document Library Status:\n\n"
        result += f"Original Documents ({len(original_docs)}):\n"
        
        if original_docs:
            for doc in original_docs:
                size_kb = doc["size"] / 1024
                result += f"  • {doc['name']} ({size_kb:.1f} KB)\n"
        else:
            result += "  No original documents found\n"
        
        result += f"\nConverted Documents ({len(converted_docs)}):\n"
        
        if converted_docs:
            for doc in converted_docs:
                size_kb = doc["size"] / 1024
                result += f"  • {doc['name']} ({size_kb:.1f} KB)\n"
        else:
            result += "  No converted documents found\n"
        
        logger.info(f"Listed {len(original_docs)} original and {len(converted_docs)} converted documents")
        return result
        
    except Exception as e:
        error_msg = f"Error listing documents: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def add_document(file_path: str) -> str:
    """
    Add a new document to the knowledge base
    
    Args:
        file_path: Path to the document file to add
    
    Returns:
        Status message about the document addition
    """
    logger.info(f"Adding document: {file_path}")
    
    error = _ensure_initialized()
    if error:
        logger.error(f"Initialization failed: {error}")
        return f"Server initialization failed: {error}"
    
    if not converter or not kb:
        return "Required components not available"
    
    try:
        source_path = Path(file_path)
        
        if not source_path.exists():
            return f"File not found: {file_path}"
        
        if not source_path.is_file():
            return f"Path is not a file: {file_path}"
        
        if source_path.suffix.lower() not in ['.pdf', '.docx', '.pptx', '.txt']:
            return f"Unsupported file type: {source_path.suffix}. Supported types: .pdf, .docx, .pptx, .txt"
        
        # Copy file to documents directory
        dest_path = SRC_DIR / source_path.name
        dest_path.write_bytes(source_path.read_bytes())
        logger.info(f"Copied file to: {dest_path}")
        
        # Convert document
        try:
            result = converter.convert(source_path)
            md_path = CONVERTED_DIR / f"{source_path.stem}.md"
            md_path.write_text(result.document.export_to_markdown())
            logger.info(f"Converted document to: {md_path}")
            
            # Reload knowledge base
            kb.load(recreate=True)
            logger.info("Knowledge base reloaded")
            
            return f"Successfully added and processed document: {source_path.name}"
            
        except Exception as conv_error:
            error_msg = f"Failed to convert document {source_path.name}: {str(conv_error)}"
            logger.error(error_msg)
            return error_msg
    
    except Exception as e:
        error_msg = f"Error adding document: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def get_document_info(document_name: str) -> str:
    """
    Get detailed information about a specific document
    
    Args:
        document_name: Name of the document to get info about
    
    Returns:
        Detailed information about the document
    """
    try:
        original_path = SRC_DIR / document_name
        converted_path = CONVERTED_DIR / f"{Path(document_name).stem}.md"
        
        info = f"Document Information for: {document_name}\n\n"
        
        if original_path.exists():
            stat = original_path.stat()
            info += f"Original File:\n"
            info += f"  Path: {original_path}\n"
            info += f"  Size: {stat.st_size / 1024:.1f} KB\n"
            info += f"  Type: {original_path.suffix}\n"
            info += f"  Modified: {stat.st_mtime}\n\n"
        else:
            info += f"Original file not found: {original_path}\n\n"
        
        if converted_path.exists():
            stat = converted_path.stat()
            info += f"Converted File:\n"
            info += f"  Path: {converted_path}\n"
            info += f"  Size: {stat.st_size / 1024:.1f} KB\n"
            info += f"  Modified: {stat.st_mtime}\n"
            
            # Preview content
            content = converted_path.read_text()[:500]
            info += f"  Preview: {content}{'...' if len(content) >= 500 else ''}\n"
        else:
            info += f"Converted file not found: {converted_path}\n"
        
        logger.info(f"Retrieved info for document: {document_name}")
        return info
        
    except Exception as e:
        error_msg = f"Error getting document info: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def convert_pending_documents() -> str:
    """
    Convert any pending documents in the documents directory
    
    Returns:
        Status of the conversion process
    """
    logger.info("Converting pending documents...")
    
    error = _ensure_initialized()
    if error:
        logger.error(f"Initialization failed: {error}")
        return f"Server initialization failed: {error}"
    
    if not converter or not kb:
        return "Required components not available"
    
    try:
        if not SRC_DIR.exists():
            return "Documents directory does not exist"
        
        converted_count = 0
        error_files = []
        
        for file in SRC_DIR.iterdir():
            if not file.is_file() or file.suffix.lower() not in ['.pdf', '.docx', '.pptx', '.txt']:
                continue
            
            try:
                result = converter.convert(file)
                md_path = CONVERTED_DIR / f"{file.stem}.md"
                md_path.write_text(result.document.export_to_markdown())
                converted_count += 1
                logger.info(f"Converted {file.name} -> {md_path.name}")
            except Exception as e:
                error_files.append(f"{file.name}: {str(e)}")
                logger.error(f"Failed to convert {file.name}: {str(e)}")
        
        if converted_count > 0:
            # Reload knowledge base
            kb.load(recreate=True)
            logger.info("Knowledge base reloaded")
            
            result_msg = f"Successfully converted {converted_count} documents"
            if error_files:
                result_msg += f"\nErrors: {'; '.join(error_files)}"
            return result_msg
        else:
            return "No documents found to convert"
            
    except Exception as e:
        error_msg = f"Error converting documents: {str(e)}"
        logger.error(error_msg)
        return error_msg

def main():
    """Main entry point for the server"""
    try:
        logger.info("Starting RAG MCP Server...")
        logger.info(f"Documents directory: {SRC_DIR}")
        logger.info(f"Converted directory: {CONVERTED_DIR}")
        logger.info("Available tools: search_documents, add_document, list_documents, get_document_info, convert_pending_documents, get_server_status")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()