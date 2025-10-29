import os

from agno.agent import Agent
from agno.guardrails import PromptInjectionGuardrail
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.models.azure import AzureOpenAI
from agno.vectordb.pgvector import PgVector
from dotenv import load_dotenv
from requests import api

load_dotenv()
prompt_injection_guardrail = PromptInjectionGuardrail()
# Embed sentence in database
# embeddings = HuggingfaceCustomEmbedder().get_embedding(
#     "The quick brown fox jumps over the lazy dog."
# )
# 1. Configure vector database with embedder
vector_db = PgVector(
    table_name="company_knowledge",
    db_url="postgresql+psycopg://ai:ai@localhost:5533/ai",
    embedder=HuggingfaceCustomEmbedder(
        id="sentence-transformers/all-MiniLM-L6-v2",
        api_key=os.getenv("HUGGINGFACE_HUB_TOKEN"),
        dimensions=384,  # all-MiniLM-L6-v2 produces 384-dim embeddings
    ),
)

# embedder=OpenAIEmbedder(
#     id="text-embedding-3-small"
# ),  # Optional: defaults to OpenAIEmbedder

# 2. Create knowledge base
knowledge = Knowledge(name="IT Documentation", vector_db=vector_db, max_results=10)

# Create embedder for chunking (same as vector DB for consistency)
chunking_embedder = HuggingfaceCustomEmbedder(
    id="sentence-transformers/all-MiniLM-L6-v2",
    api_key=os.getenv("HUGGINGFACE_HUB_TOKEN"),
    dimensions=384,  # all-MiniLM-L6-v2 produces 384-dim embeddings
)

# 3. Add content with chunking strategy
knowledge.add_content(
    path="IT-L1-Support-Knowledge-Base.pdf",
    reader=PDFReader(
        chunking_strategy=SemanticChunking(
            embedder=chunking_embedder,
            chunk_size=500,  # Reduced to avoid token length warnings
            similarity_threshold=0.5,
        )
    ),
    metadata={"type": "IT", "Category": "L1-Support"},
)
llm = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# 4. Create agent with knowledge search enabled
agent = Agent(
    model=llm,
    knowledge=knowledge,
    instructions=[
        "You are an IT support agent. Your task is to provide assistance to users with IT-related issues.\n\n",
        "You should cite the source of your information by the section name and Document Name.",
    ],
    search_knowledge=True,
    knowledge_filters={"type": "IT"},
    pre_hooks=[prompt_injection_guardrail],
)


input_text = input("Enter your question: ")

agent.print_response(input_text)
