import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, AsyncGenerator, List
from datetime import datetime
import logging

from dotenv import load_dotenv
from docling.document_converter import DocumentConverter

# AGNO imports
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
from agno.storage.sqlite import SqliteStorage

from ..models.requests import AgentType, StreamEventType
from ..models.responses import AgentStatus
from .streaming import StreamingManager, streaming_manager
from .database import db_manager

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AgentSystemManager:
    """Manages the AGNO multi-agent system for API use"""
    
    def __init__(self):
        self.doc_agent = None
        self.web_agent = None
        self.team = None
        self.knowledge_base = None
        self.memory = None
        self.storage = None
        self.initialized = False
        self.streaming_manager = streaming_manager
        
        # Document processing paths
        self.src_dir = Path("documents")
        self.converted_dir = Path("converted_docs")
        
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the complete AGNO system"""
        try:
            # Initialize memory and storage
            self._setup_memory_and_storage()
            
            # Initialize embedder and vector DB
            self._setup_knowledge_base()
            
            # Initialize models
            self._setup_models()
            
            # Initialize agents
            self._setup_agents()
            
            # Initialize team
            self._setup_team()
            
            self.initialized = True
            logger.info("Agent system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent system: {e}")
            raise
    
    def _setup_memory_and_storage(self):
        """Setup memory and storage systems"""
        # Use the same paths as the original system
        memory_db = SqliteMemoryDb(
            table_name="agent_memory",
            db_file="agent_memory.db"
        )
        
        self.memory = Memory(db=memory_db)
        
        self.storage = SqliteStorage(
            table_name="agent_sessions",
            db_file="agent_sessions.db"
        )
    
    def _setup_knowledge_base(self):
        """Setup knowledge base and vector database"""
        # Database configuration
        db_url = os.getenv("DB_URL") or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        table_name = os.getenv("PGVECTOR_TABLE", "rag_documents")
        
        # Create embedder
        embedder = HuggingfaceCustomEmbedder(
            id="BAAI/bge-small-en-v1.5",
            dimensions=384,
            api_key=os.getenv("HUGGINGFACE_HUB_TOKEN")
        )
        
        # Create vector database
        vector_db = PgVector(
            table_name=table_name,
            db_url=db_url,
            search_type=SearchType.hybrid,
            embedder=embedder,
        )
        
        # Create knowledge base
        self.knowledge_base = TextKnowledgeBase(
            path=str(self.converted_dir),
            formats=[".md", ".txt"],
            vector_db=vector_db,
        )
        
        # Load knowledge base if documents exist
        if self.converted_dir.exists() and any(self.converted_dir.iterdir()):
            self.knowledge_base.load(recreate=False)
    
    def _setup_models(self):
        """Setup Azure OpenAI models"""
        self.azure_model = AzureOpenAI(
            id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        )
        
        # Additional models if configured
        if os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_o4"):
            self.azure_model_04 = AzureOpenAI(
                id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_o4"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY_o4"),
                api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_o4"),
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_o4"),
            )
    
    def _setup_agents(self):
        """Setup individual agents"""
        # Document agent
        self.doc_agent = Agent(
            name="Doc Agent",
            role="Handles local document search",
            knowledge=self.knowledge_base,
            model=self.azure_model,
            memory=self.memory,
            storage=self.storage,
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
        
        # Web agent
        self.web_agent = Agent(
            name="Web Agent",
            role="Handles web search and news",
            model=self.azure_model,
            memory=self.memory,
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
    
    def _setup_team(self):
        """Setup the agent team"""
        self.team = Team(
            name="Reasoning Knowledge Team",
            mode="coordinate",
            model=self.azure_model,
            members=[self.web_agent, self.doc_agent],
            tools=[ReasoningTools(add_instructions=True)],
            memory=self.memory,
            storage=self.storage,
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
    
    async def get_agent_response(self, 
                                message: str,
                                user_id: str,
                                session_id: str,
                                agent_type: AgentType = AgentType.TEAM,
                                stream: bool = True,
                                **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Get response from agents with streaming support"""
        
        if not self.initialized:
            raise RuntimeError("Agent system not initialized")
        
        # Select agent based on type
        agent = self._get_agent_by_type(agent_type)
        
        if stream:
            # Stream the response
            async for event in self._stream_agent_response(
                agent, message, user_id, session_id, **kwargs
            ):
                yield event
        else:
            # Get non-streaming response
            try:
                response = agent.run(
                    message,
                    user_id=user_id,
                    session_id=session_id,
                    **kwargs
                )
                yield {
                    "type": "response",
                    "content": response.content,
                    "agent": agent_type.value,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                yield {
                    "type": "error", 
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
    
    async def _stream_agent_response(self,
                                   agent,
                                   message: str,
                                   user_id: str,
                                   session_id: str,
                                   show_reasoning: bool = False,
                                   stream_intermediate_steps: bool = False,
                                   **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream agent response with proper event handling"""
        
        try:
            # For now, we'll simulate streaming by running the agent in a thread
            # In a full implementation, we'd integrate with AGNO's streaming capabilities
            
            yield {
                "type": StreamEventType.STATUS.value,
                "data": {"status": "processing", "agent": agent.name},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Run agent in thread to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: agent.run(
                    message,
                    user_id=user_id,
                    session_id=session_id,
                    stream=False,  # We handle streaming at the API level
                    show_full_reasoning=show_reasoning,
                    stream_intermediate_steps=stream_intermediate_steps,
                    **kwargs
                )
            )
            
            # Stream the response content in chunks
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Split content into chunks for streaming
            chunk_size = 100
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                yield {
                    "type": StreamEventType.CONTENT.value,
                    "data": {"content": chunk, "chunk_index": i // chunk_size},
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Small delay to simulate real streaming
                await asyncio.sleep(0.05)
            
            # Send completion event
            yield {
                "type": StreamEventType.COMPLETE.value,
                "data": {
                    "status": "completed", 
                    "agent": agent.name,
                    "total_content_length": len(content)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            yield {
                "type": StreamEventType.ERROR.value,
                "data": {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "agent": agent.name
                },
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _get_agent_by_type(self, agent_type: AgentType):
        """Get agent instance by type"""
        if agent_type == AgentType.DOC_AGENT:
            return self.doc_agent
        elif agent_type == AgentType.WEB_AGENT:
            return self.web_agent
        elif agent_type == AgentType.TEAM:
            return self.team
        else:
            return self.team  # Default to team
    
    def get_agent_status(self) -> List[AgentStatus]:
        """Get status of all agents"""
        if not self.initialized:
            return []
        
        statuses = []
        
        # Doc Agent status
        if self.doc_agent:
            statuses.append(AgentStatus(
                agent_name="Doc Agent",
                agent_type=AgentType.DOC_AGENT,
                status="healthy" if self.doc_agent else "unhealthy",
                model_info={
                    "model_id": self.azure_model.id if self.azure_model else None,
                    "provider": "azure_openai"
                },
                capabilities=["document_search", "knowledge_base", "memory", "citations"],
                last_activity=None,  # Would track in production
                total_requests=0,
                error_rate=0.0
            ))
        
        # Web Agent status
        if self.web_agent:
            statuses.append(AgentStatus(
                agent_name="Web Agent",
                agent_type=AgentType.WEB_AGENT,
                status="healthy" if self.web_agent else "unhealthy",
                model_info={
                    "model_id": self.azure_model.id if self.azure_model else None,
                    "provider": "azure_openai"
                },
                capabilities=["web_search", "news_search", "brave_search", "memory"],
                last_activity=None,
                total_requests=0,
                error_rate=0.0
            ))
        
        # Team status
        if self.team:
            statuses.append(AgentStatus(
                agent_name="Reasoning Knowledge Team",
                agent_type=AgentType.TEAM,
                status="healthy" if self.team else "unhealthy",
                model_info={
                    "model_id": self.azure_model.id if self.azure_model else None,
                    "provider": "azure_openai"
                },
                capabilities=["coordination", "reasoning", "multi_agent", "memory", "comprehensive_search"],
                last_activity=None,
                total_requests=0,
                error_rate=0.0
            ))
        
        return statuses
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """Get knowledge base information"""
        if not self.knowledge_base:
            return {"status": "not_initialized"}
        
        info = {
            "status": "initialized",
            "documents_path": str(self.converted_dir),
            "formats_supported": [".md", ".txt"],
            "vector_db_configured": bool(self.knowledge_base.vector_db)
        }
        
        # Check if documents exist
        if self.converted_dir.exists():
            docs = list(self.converted_dir.glob("*.md")) + list(self.converted_dir.glob("*.txt"))
            info["document_count"] = len(docs)
            info["documents"] = [doc.name for doc in docs[:10]]  # First 10
        else:
            info["document_count"] = 0
            info["documents"] = []
        
        return info
    
    async def add_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """Add new documents to the knowledge base"""
        if not self.initialized:
            raise RuntimeError("Agent system not initialized")
        
        results = {
            "added_files": [],
            "converted_files": [],
            "errors": [],
            "knowledge_base_updated": False
        }
        
        try:
            # Ensure directories exist
            self.src_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files to source directory
            for file_path in file_paths:
                src_path = Path(file_path)
                if not src_path.exists():
                    results["errors"].append(f"File not found: {file_path}")
                    continue
                
                dest = self.src_dir / src_path.name
                dest.write_bytes(src_path.read_bytes())
                results["added_files"].append(src_path.name)
            
            # Convert documents
            converted_count = await self._convert_documents()
            results["converted_files"] = converted_count
            
            # Reload knowledge base if documents were converted
            if converted_count > 0:
                self.knowledge_base.load(recreate=True)
                results["knowledge_base_updated"] = True
            
        except Exception as e:
            results["errors"].append(str(e))
        
        return results
    
    async def _convert_documents(self) -> int:
        """Convert documents using Docling"""
        if not self.src_dir.exists():
            return 0
        
        self.converted_dir.mkdir(parents=True, exist_ok=True)
        converter = DocumentConverter()
        
        converted_count = 0
        for file_path in self.src_dir.iterdir():
            if not file_path.is_file() or file_path.suffix.lower() not in ['.pdf', '.docx', '.pptx', '.txt']:
                continue
            
            try:
                result = converter.convert(file_path)
                md_path = self.converted_dir / f"{file_path.stem}.md"
                md_path.write_text(result.document.export_to_markdown())
                converted_count += 1
                logger.info(f"Converted {file_path.name} -> {md_path.name}")
            except Exception as e:
                logger.error(f"Error converting {file_path.name}: {e}")
        
        return converted_count
    
    async def rebuild_knowledge_base(self, force: bool = False) -> Dict[str, Any]:
        """Rebuild the knowledge base"""
        if not self.initialized:
            raise RuntimeError("Agent system not initialized")
        
        try:
            start_time = datetime.utcnow()
            
            # Reload knowledge base
            self.knowledge_base.load(recreate=force)
            
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Get updated info
            kb_info = self.get_knowledge_base_info()
            
            return {
                "success": True,
                "processing_time": processing_time,
                "documents_indexed": kb_info.get("document_count", 0),
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Create global agent system manager
agent_system = AgentSystemManager()

# Dependency functions for FastAPI
def get_agent_system():
    """Get the main agent system"""
    return agent_system

def get_knowledge_base():
    """Get the knowledge base system"""
    return agent_system.knowledge_base

def get_document_processor():
    """Get document processor"""
    class DocumentProcessor:
        async def process_document_async(self, document_id: str, file_path: str, kb):
            return await agent_system._convert_documents()
        
        async def process_document(self, file_path: str, kb):
            return await agent_system._convert_documents()
        
        async def reprocess_document(self, document_id: str, file_path: str, kb):
            return await agent_system._convert_documents()
        
        async def reindex_knowledge_base(self, kb, **kwargs):
            return await agent_system.rebuild_knowledge_base()
    
    return DocumentProcessor()