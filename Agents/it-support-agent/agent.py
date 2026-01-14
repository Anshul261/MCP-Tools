import os

from agno.agent import Agent
from agno.guardrails import PromptInjectionGuardrail
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.models.azure import AzureOpenAI
from agno.os import AgentOS
from agno.vectordb.pgvector import PgVector
from dotenv import load_dotenv

load_dotenv()
prompt_injection_guardrail = PromptInjectionGuardrail()
# Embed sentence in database
# embeddings = HuggingfaceCustomEmbedder().get_embedding(
#     "The quick brown fox jumps over the lazy dog."
# )
# 1. Configure vector database with embedder
vector_db = PgVector(
    table_name="it_support_knowledge",
    db_url="postgresql+psycopg://ai:ai@localhost:5533/ai",
    embedder=HuggingfaceCustomEmbedder(
        id="sentence-transformers/all-MiniLM-L6-v2",
        api_key=os.getenv("HUGGINGFACE_HUB_TOKEN"),
        dimensions=384,  # all-MiniLM-L6-v2 produces 384-dim embeddings
    ),
)
from agno.db.sqlite import SqliteDb

db = SqliteDb(
    db_file="it_agent_sessions.db",  # Database file in current directory
    id="it-agent-db",
)
# embedder=OpenAIEmbedder(
#     id="text-embedding-3-small"
# ),  # Optional: defaults to OpenAIEmbedder

# 2. Create knowledge base
knowledge = Knowledge(name="IT Documentation", vector_db=vector_db, max_results=10)

# Create embedder for chunking (same as vector DB for consistency)
chunking_embedder = HuggingfaceCustomEmbedder(
    id="BAAI/bge-small-en-v1.5",
    api_key=os.getenv("HUGGINGFACE_HUB_TOKEN"),
    dimensions=384,
)

# 3. Add content with chunking strategy - load multiple PDFs with individual metadata
pdf_reader = PDFReader(
    chunking_strategy=SemanticChunking(
        embedder=chunking_embedder,
        chunk_size=500,
        similarity_threshold=0.5,
    )
)

# Add each PDF with its specific metadata
pdf_files = [
    # ("IT-L1-Support-Knowledge-Base.pdf", {"type": "IT", "category": "L1-Support", "document": "Knowledge Base"}),
    (
        "IT Heldesk- OneDrive Related issues.pdf",
        {"type": "IT", "category": "OneDrive", "document": "OneDrive Issues"},
    ),
    (
        "IT Helpdesk - Default APP set up.pdf",
        {"type": "IT", "category": "Apps", "document": "App Setup"},
    ),
    (
        "IT Helpdesk - Priner Configuration.pdf",
        {"type": "IT", "category": "Printer", "document": "Printer Configuration"},
    ),
    (
        "IT Helpdesk- Outlook Issues.pdf",
        {"type": "IT", "category": "Outlook", "document": "Outlook Issues"},
    ),
    (
        "IT Helpdesk- Outlook Issues.pdf",
        {"type": "IT", "category": "Outlook", "document": "Outlook Issues"},
    ),
]

llm = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# 4. Create agent with knowledge search enabled
it_support_agent = Agent(
    model=llm,
    name="AISA",
    knowledge=knowledge,
    db=db,
    instructions=[
        "You are an Alpha Data IT support agent. Your task is to provide assistance to users with IT-related issues.\n\n",
        "Use the docs as reference always use the search_knowledge_base tool to find relevant information.",
        "You should cite the source of your information by the section name and Document Name.",
    ],
    search_knowledge=True,
    knowledge_filters={"type": "IT"},
    pre_hooks=[prompt_injection_guardrail],
    enable_agentic_memory=True,
    enable_user_memories=True,
    markdown=True,
    telemetry=False,
    num_history_runs=5,
    add_name_to_context=True,
    stream=True,
    stream_events=True,
)

agent_os = AgentOS(
    id="it-support-agent",
    description="IT Support Agent",
    agents=[it_support_agent],
)

app = agent_os.get_app()

# Add CORS middleware to allow frontend access
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # Load all PDFs into the knowledge base before starting the server
    for pdf_path, metadata in pdf_files:
        knowledge.add_content(
            path=pdf_path,
            reader=pdf_reader,
            metadata=metadata,
            skip_if_exists=True,  # Skip re-uploading if content already in vector DB
        )

    # Default port is 7777; change with port=...
    # Bind to 0.0.0.0 so Windows browser can reach WSL2
    agent_os.serve(app="agent:app", reload=True, host="0.0.0.0")
