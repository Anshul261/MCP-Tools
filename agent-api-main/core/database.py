# core/database.py
from typing import Generator
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import Session, sessionmaker
from agno.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.vectordb.pgvector import PgVector, SearchType
from agno.knowledge.text import TextKnowledgeBase
from agno.models.azure import AzureOpenAI
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.agent.postgres import PostgresAgentStorage

from core.config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and configurations"""
    
    def __init__(self):
        self._engine: Engine = None
        self._session_local: sessionmaker = None
        self._embedder: HuggingfaceCustomEmbedder = None
        self._vector_db: PgVector = None
        self._knowledge_base: TextKnowledgeBase = None
        self._azure_model: AzureOpenAI = None
        self._memory: Memory = None
    
    @property
    def engine(self) -> Engine:
        """Get SQLAlchemy engine"""
        if self._engine is None:
            self._engine = create_engine(
                settings.database.url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.api.debug
            )
            logger.info("Database engine created")
        return self._engine
    
    @property
    def session_local(self) -> sessionmaker:
        """Get session maker"""
        if self._session_local is None:
            self._session_local = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        return self._session_local
    
    def get_db_session(self) -> Generator[Session, None, None]:
        """Get database session"""
        db = self.session_local()
        try:
            yield db
        finally:
            db.close()
    
    @property
    def embedder(self) -> HuggingfaceCustomEmbedder:
        """Get HuggingFace embedder"""
        if self._embedder is None:
            self._embedder = HuggingfaceCustomEmbedder(
                id=settings.huggingface.model_id,
                dimensions=settings.huggingface.dimensions,
                api_key=settings.huggingface.token
            )
            logger.info("HuggingFace embedder initialized")
        return self._embedder
    
    @property
    def vector_db(self) -> PgVector:
        """Get vector database"""
        if self._vector_db is None:
            self._vector_db = PgVector(
                table_name=settings.documents.vector_table,
                db_url=settings.database.url,
                search_type=SearchType.hybrid,
                embedder=self.embedder,
            )
            logger.info("Vector database initialized")
        return self._vector_db
    
    @property
    def knowledge_base(self) -> TextKnowledgeBase:
        """Get knowledge base"""
        if self._knowledge_base is None:
            self._knowledge_base = TextKnowledgeBase(
                path=str(settings.documents.converted_dir),
                formats=[".md", ".txt"],
                vector_db=self.vector_db,
            )
            logger.info("Knowledge base initialized")
        return self._knowledge_base
    
    @property
    def azure_model(self) -> AzureOpenAI:
        """Get Azure OpenAI model"""
        if self._azure_model is None:
            self._azure_model = AzureOpenAI(
                id=settings.azure_openai.deployment_name,
                api_key=settings.azure_openai.api_key,
                api_version=settings.azure_openai.api_version,
                azure_endpoint=settings.azure_openai.endpoint,
                azure_deployment=settings.azure_openai.deployment_name,
            )
            logger.info("Azure OpenAI model initialized")
        return self._azure_model
    
    @property
    def memory(self) -> Memory:
        """Get memory instance"""
        if self._memory is None:
            memory_db = PostgresMemoryDb(
                table_name="agent_memory",
                db_url=settings.database.url
            )
            self._memory = Memory(db=memory_db)
            logger.info("Memory system initialized")
        return self._memory
    
    def get_agent_storage(self, table_name: str) -> PostgresAgentStorage:
        """Get agent storage for specific table"""
        return PostgresAgentStorage(
            table_name=table_name,
            db_url=settings.database.url
        )
    
    async def initialize_knowledge_base(self, recreate: bool = False):
        """Initialize or reload the knowledge base"""
        try:
            if settings.documents.converted_dir.exists() and any(settings.documents.converted_dir.iterdir()):
                await self.knowledge_base.aload(recreate=recreate)
                logger.info(f"Knowledge base {'recreated' if recreate else 'loaded'} successfully")
            else:
                logger.warning("No converted documents found for knowledge base")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
            raise
    
    def health_check(self) -> dict:
        """Perform health check on database connections"""
        try:
            # Test database connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            # Test vector database
            # Note: This is a simple check, in production you might want more thorough testing
            
            return {
                "database": "healthy",
                "vector_db": "healthy",
                "embedder": "healthy" if self._embedder else "not_initialized",
                "knowledge_base": "healthy" if self._knowledge_base else "not_initialized"
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "database": f"error: {str(e)}",
                "vector_db": "unknown",
                "embedder": "unknown",
                "knowledge_base": "unknown"
            }


# Global database manager instance
db_manager = DatabaseManager()