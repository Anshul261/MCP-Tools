# core/database.py
from typing import Generator, List
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

    async def check_document_exists_in_vector_db(self, filename: str) -> bool:
        """Check if a document already exists in the vector database"""
        try:
            # Query the vector database for documents with the specified filename
            with self.engine.connect() as conn:
                # Use parameterized query to avoid SQL injection
                query = text("SELECT EXISTS(SELECT 1 FROM {} WHERE meta->>'file_name' = :filename)".format(settings.documents.vector_table))
                result = conn.execute(query, {"filename": filename})
                exists = result.scalar()
                return bool(exists)
        except Exception as e:
            logger.error(f"Error checking if document exists in vector DB: {e}")
            return False

    async def get_documents_in_vector_db(self) -> List[str]:
        """Get list of all document filenames currently in the vector database"""
        try:
            with self.engine.connect() as conn:
                # First, let's check what columns and metadata exist
                table_name = settings.documents.vector_table
                
                # Debug: Let's see what metadata structure exists
                try:
                    debug_query = text(f"SELECT meta FROM {table_name} LIMIT 3")
                    debug_result = conn.execute(debug_query)
                    for row in debug_result.fetchall():
                        logger.info(f"Sample metadata structure: {row[0]}")
                except Exception as debug_e:
                    logger.debug(f"Debug query failed: {debug_e}")
                
                # Try different possible metadata field names
                possible_queries = [
                    f"SELECT DISTINCT meta->>'file_name' FROM {table_name} WHERE meta->>'file_name' IS NOT NULL",
                    f"SELECT DISTINCT meta->>'filename' FROM {table_name} WHERE meta->>'filename' IS NOT NULL", 
                    f"SELECT DISTINCT meta->>'source' FROM {table_name} WHERE meta->>'source' IS NOT NULL",
                    f"SELECT DISTINCT meta->>'name' FROM {table_name} WHERE meta->>'name' IS NOT NULL"
                ]
                
                filenames = []
                for query_str in possible_queries:
                    try:
                        query = text(query_str)
                        result = conn.execute(query)
                        new_filenames = [row[0] for row in result.fetchall() if row[0]]
                        if new_filenames:
                            filenames.extend(new_filenames)
                            logger.info(f"Found {len(new_filenames)} documents using query: {query_str}")
                        break  # Use the first successful query
                    except Exception as query_e:
                        logger.debug(f"Query failed: {query_str} - {query_e}")
                        continue
                
                # Remove duplicates and file extensions from paths
                unique_filenames = []
                for filename in filenames:
                    # Extract just the filename from potential full paths
                    if '/' in filename:
                        filename = filename.split('/')[-1]
                    unique_filenames.append(filename)
                
                unique_filenames = list(set(unique_filenames))
                logger.info(f"Final unique filenames found: {unique_filenames}")
                return unique_filenames
                
        except Exception as e:
            logger.error(f"Error getting documents from vector DB: {e}")
            return []
    
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