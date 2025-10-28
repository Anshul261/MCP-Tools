from agno.agent import Agent
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.vectordb.pgvector import PgVector

# 1. Configure vector database with embedder
vector_db = PgVector(
    table_name="company_knowledge",
    db_url="postgresql+psycopg://user:pass@localhost:5432/db",
    embedder=OpenAIEmbedder(
        id="text-embedding-3-small"
    ),  # Optional: defaults to OpenAIEmbedder
)

# 2. Create knowledge base
knowledge = Knowledge(name="Company Documentation", vector_db=vector_db, max_results=10)

# 3. Add content with chunking strategy
knowledge.add_content(
    path="company_docs/employee_handbook.pdf",
    reader=PDFReader(
        chunking_strategy=SemanticChunking(  # Optional: defaults to FixedSizeChunking
            chunk_size=1000, similarity_threshold=0.5
        )
    ),
    metadata={"type": "policy", "department": "hr"},
)

# 4. Create agent with knowledge search enabled
agent = Agent(
    knowledge=knowledge,
    search_knowledge=True,  # Required for automatic search
    knowledge_filters={"type": "policy"},  # Optional filtering
)
