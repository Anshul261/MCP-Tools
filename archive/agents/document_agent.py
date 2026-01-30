"""
Document Research Agent - Vector Search Specialist
Specializes in searching and analyzing local documents using vector embeddings
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from docling.document_converter import DocumentConverter
from agno.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.pgvector import PgVector, SearchType

from .base_agent import BaseAgent


class DocumentAgent(BaseAgent):
    """Agent specialized in local document search and analysis"""
    
    def __init__(self, documents_path: str = "documents", **kwargs):
        """
        Initialize Document Research Agent
        
        Args:
            documents_path: Path to documents directory
            **kwargs: Additional arguments passed to BaseAgent
        """
        self.documents_path = Path(documents_path)
        self.converted_path = Path("converted_docs")
        
        # Initialize knowledge base
        self.knowledge_base = self._setup_knowledge_base()
        
        # Document agent specific instructions
        instructions = [
            "You are a Document Research Specialist with deep expertise in analyzing local documents.",
            "Your primary role is to search through and analyze documents in the knowledge base.",
            "Always provide detailed citations with specific page numbers, sections, or document references.",
            "When information is outdated or limited, clearly indicate this and suggest updating the knowledge base.",
            "Flag when documents might need additional context or when information appears incomplete.",
            "Prioritize accuracy and provide comprehensive analysis of document contents.",
            "If a query cannot be answered from local documents, clearly state this limitation.",
        ]
        
        super().__init__(
            name="Document Research Agent",
            agent_id="document_agent",
            instructions=instructions,
            knowledge=self.knowledge_base,
            storage_table="document_agent_sessions",
            **kwargs
        )
        
        # Load documents if available
        self._load_documents()
    
    def _setup_knowledge_base(self) -> TextKnowledgeBase:
        """Setup vector database and knowledge base"""
        # Ensure directories exist
        self.documents_path.mkdir(parents=True, exist_ok=True)
        self.converted_path.mkdir(parents=True, exist_ok=True)
        
        # Database configuration
        db_url = os.getenv("DB_URL") or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        
        # Create embedder - using efficient local model
        embedder = HuggingfaceCustomEmbedder(
            id="BAAI/bge-small-en-v1.5",
            dimensions=384
        )
        
        # Create vector database
        vector_db = PgVector(
            table_name=os.getenv("PGVECTOR_TABLE", "document_agent_vectors"),
            db_url=db_url,
            search_type=SearchType.hybrid,
            embedder=embedder,
        )
        
        # Create knowledge base
        return TextKnowledgeBase(
            path=str(self.converted_path),
            formats=[".md", ".txt"],
            vector_db=vector_db,
        )
    
    def _convert_documents(self) -> int:
        """Convert documents using Docling"""
        if not self.documents_path.exists() or not any(self.documents_path.iterdir()):
            return 0
        
        converter = DocumentConverter()
        converted_count = 0
        
        for file in self.documents_path.iterdir():
            if not file.is_file() or file.suffix.lower() not in ['.pdf', '.docx', '.pptx', '.txt']:
                continue
            
            try:
                result = converter.convert(file)
                md_path = self.converted_path / f"{file.stem}.md"
                md_path.write_text(result.document.export_to_markdown())
                print(f"📄 Converted {file.name} ➜ {md_path.name}")
                converted_count += 1
            except Exception as e:
                print(f"❌ Error converting {file.name}: {e}")
        
        return converted_count
    
    def _load_documents(self):
        """Load documents into knowledge base"""
        # Convert documents if any exist
        converted_count = self._convert_documents()
        
        if converted_count > 0:
            print(f"📚 Converted {converted_count} documents for Document Agent")
        
        # Load knowledge base if documents exist
        if self.converted_path.exists() and any(self.converted_path.iterdir()):
            try:
                print("🔄 Loading Document Agent knowledge base...")
                self.knowledge_base.load(recreate=False)
                print("✅ Document Agent knowledge base loaded")
            except Exception as e:
                print(f"❌ Error loading knowledge base: {e}")
    
    def add_documents(self, file_or_dir_path: str) -> Dict[str, Any]:
        """
        Add new documents to the knowledge base
        
        Args:
            file_or_dir_path: Path to file or directory to add
            
        Returns:
            Summary of added documents
        """
        path = Path(file_or_dir_path)
        if not path.exists():
            return {"error": f"Path {file_or_dir_path} does not exist"}
        
        added_files = []
        
        if path.is_file():
            dest = self.documents_path / path.name
            dest.write_bytes(path.read_bytes())
            added_files.append(path.name)
        elif path.is_dir():
            for file in path.iterdir():
                if file.is_file():
                    dest = self.documents_path / file.name
                    dest.write_bytes(file.read_bytes())
                    added_files.append(file.name)
        
        # Convert and reload knowledge base
        converted_count = self._convert_documents()
        
        if converted_count > 0:
            try:
                self.knowledge_base.load(recreate=True)
                return {
                    "added_files": added_files,
                    "converted_count": converted_count,
                    "status": "success",
                    "message": "Documents added and knowledge base updated"
                }
            except Exception as e:
                return {
                    "added_files": added_files,
                    "converted_count": converted_count,
                    "status": "error",
                    "message": f"Error updating knowledge base: {e}"
                }
        
        return {
            "added_files": added_files,
            "converted_count": 0,
            "status": "warning",
            "message": "Files added but no documents were converted"
        }
    
    def get_document_summary(self) -> Dict[str, Any]:
        """Get summary of available documents"""
        try:
            doc_files = list(self.documents_path.glob("*")) if self.documents_path.exists() else []
            converted_files = list(self.converted_path.glob("*")) if self.converted_path.exists() else []
            
            return {
                "source_documents": len([f for f in doc_files if f.is_file()]),
                "converted_documents": len([f for f in converted_files if f.is_file()]),
                "document_types": list(set([f.suffix for f in doc_files if f.is_file()])),
                "knowledge_base_active": bool(self.knowledge_base and converted_files),
                "last_updated": max([f.stat().st_mtime for f in converted_files if f.is_file()]) if converted_files else None
            }
        except Exception as e:
            return {"error": str(e), "knowledge_base_active": False}
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Direct document search for coordination with other agents
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results with metadata
        """
        try:
            if not self.knowledge_base:
                return [{"error": "Knowledge base not available"}]
            
            # This would need to be implemented based on your vector DB setup
            # For now, returning a placeholder structure
            return [{
                "content": "Document search functionality would be implemented here",
                "source": "document_search",
                "confidence": 0.8,
                "metadata": {"agent": "document_agent", "query": query}
            }]
        except Exception as e:
            return [{"error": f"Document search failed: {e}"}]
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Enhanced capabilities for document agent"""
        base_caps = super().get_capabilities()
        doc_summary = self.get_document_summary()
        
        base_caps.update({
            "specialization": "document_research",
            "document_summary": doc_summary,
            "supports_upload": True,
            "search_types": ["semantic", "keyword", "hybrid"],
            "formats_supported": [".pdf", ".docx", ".pptx", ".txt"]
        })
        
        return base_caps