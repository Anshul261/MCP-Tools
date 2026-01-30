import os
import requests
import urllib3

from agno.agent import Agent
from agno.guardrails import PromptInjectionGuardrail
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.models.azure import AzureOpenAI
from agno.os import AgentOS
from agno.team import Team
from agno.vectordb.pgvector import PgVector
from dotenv import load_dotenv

load_dotenv()

# Suppress SSL warnings for ManageEngine API (self-signed cert)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_requester_by_name(name: str) -> dict:
    """Look up a requester in ManageEngine by name.

    Args:
        name: The name to search for

    Returns:
        dict: Requester details including id and name, or error message
    """
    import json

    api_key = os.getenv("MANAGEENGINE_API_KEY")
    if not api_key:
        return {"error": "MANAGEENGINE_API_KEY environment variable not set"}

    url = f"{os.getenv('MANAGEENGINE_API_BASE')}/users"

    input_data = {
        "list_info": {
            "search_fields": {"name": name},
            "row_count": 5,
        }
    }

    headers = {
        "authtoken": api_key,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    params = {"input_data": json.dumps(input_data)}

    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        data = response.json()

        users = data.get("users", [])
        if users:
            return {
                "found": True,
                "users": [
                    {"id": u.get("id"), "name": u.get("name"), "email": u.get("email_id")}
                    for u in users
                ],
            }
        return {"found": False, "message": f"No user found with name '{name}'"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status_code": getattr(e.response, "status_code", None)}


def get_categories() -> dict:
    """Get list of valid categories with IDs from ManageEngine."""
    api_key = os.getenv("MANAGEENGINE_API_KEY")
    if not api_key:
        return {"error": "MANAGEENGINE_API_KEY environment variable not set"}
    url = f"{os.getenv('MANAGEENGINE_API_BASE')}/categories"
    headers = {"authtoken": api_key}
    try:
        response = requests.get(url, headers=headers, verify=False)
        data = response.json()
        categories = data.get("categories", [])
        return {"categories": [{"id": c.get("id"), "name": c.get("name")} for c in categories]}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_subcategories(category_id: str) -> dict:
    """Get subcategories for a specific category.

    Args:
        category_id: The ID of the category (from get_categories)
    """
    api_key = os.getenv("MANAGEENGINE_API_KEY")
    if not api_key:
        return {"error": "MANAGEENGINE_API_KEY environment variable not set"}
    url = f"{os.getenv('MANAGEENGINE_API_BASE')}/categories/{category_id}/subcategories"
    headers = {"authtoken": api_key}
    try:
        response = requests.get(url, headers=headers, verify=False)
        data = response.json()
        subcategories = data.get("subcategories", [])
        return {"subcategories": [{"id": s.get("id"), "name": s.get("name")} for s in subcategories]}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_items(subcategory_id: str) -> dict:
    """Get items for a specific subcategory.

    Args:
        subcategory_id: The ID of the subcategory (from get_subcategories)
    """
    api_key = os.getenv("MANAGEENGINE_API_KEY")
    if not api_key:
        return {"error": "MANAGEENGINE_API_KEY environment variable not set"}
    url = f"{os.getenv('MANAGEENGINE_API_BASE')}/subcategories/{subcategory_id}/items"
    headers = {"authtoken": api_key}
    try:
        response = requests.get(url, headers=headers, verify=False)
        data = response.json()
        items = data.get("items", [])
        return {"items": [{"id": i.get("id"), "name": i.get("name")} for i in items]}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_support_groups() -> dict:
    """Get list of valid support groups from ManageEngine."""
    api_key = os.getenv("MANAGEENGINE_API_KEY")
    if not api_key:
        return {"error": "MANAGEENGINE_API_KEY environment variable not set"}
    url = f"{os.getenv('MANAGEENGINE_API_BASE')}/support_groups"
    headers = {"authtoken": api_key}
    try:
        response = requests.get(url, headers=headers, verify=False)
        data = response.json()
        groups = data.get("support_groups", [])
        return {"groups": [g.get("name") for g in groups]}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def create_manageengine_ticket(
    subject: str,
    description: str,
    requester_name: str,
    requester_id: str,
    category: str,
    subcategory: str,
    item: str,
    group: str,
    impact: str = "Medium",
    urgency: str = "Medium",
    request_type: str = "Incident",
) -> dict:
    """Create a ticket in ManageEngine ServiceDesk.

    Args:
        subject: The ticket subject/title
        description: Detailed description of the issue
        requester_name: Name of the requester
        requester_id: ID of the requester (from get_requester_by_name)
        category: Category (from get_categories)
        subcategory: Subcategory for the category
        item: Item (from get_items)
        group: Support group (from get_support_groups)
        impact: Impact level - Low, Medium, High
        urgency: Urgency level - Low, Medium, High
        request_type: Type of request - Incident, Service Request, Preventive Maintenance, Security Incident, Security Request, Request for Information, Change Requests.

    Returns:
        dict: API response with ticket details or error message
    """
    import json

    api_key = os.getenv("MANAGEENGINE_API_KEY")
    if not api_key:
        return {"error": "MANAGEENGINE_API_KEY environment variable not set"}

    url = f"{os.getenv('MANAGEENGINE_API_BASE')}/requests"

    input_data = {
        "request": {
            "subject": subject,
            "description": description,
            "requester": {"name": requester_name, "id": requester_id},
            "request_type": {"name": request_type},
            "impact": {"name": impact},
            "urgency": {"name": urgency},
            "category": {"name": category},
            "subcategory": {"name": subcategory},
            "item": {"name": item},
            "group": {"name": group},
        }
    }

    headers = {
        "authtoken": api_key,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"input_data": json.dumps(input_data)}

    try:
        response = requests.post(url, headers=headers, data=data, verify=False)
        result = response.json()
        if response.status_code != 200 and response.status_code != 201:
            return {"error": result, "status_code": response.status_code}
        return result
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status_code": getattr(e.response, "status_code", None)}


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

# 5. Create ManageEngine Ticket Agent
manage_engine_agent = Agent(
    id="manage-engine-agent",
    name="ManageEngine Ticket Agent",
    model=llm,
    role="Create IT support tickets in ManageEngine when issues cannot be resolved",
    tools=[
        get_requester_by_name,
        get_categories,
        get_subcategories,
        get_items,
        get_support_groups,
        create_manageengine_ticket,
    ],
    instructions=[
        "You create IT support tickets in ManageEngine.",
        "IMPORTANT: Category, subcategory, and item are hierarchical. Follow this exact order:",
        "1. Use get_requester_by_name to look up the user's ID",
        "2. Use get_categories to get categories WITH IDs - pick the most appropriate category",
        "3. Use get_subcategories(category_id) with the chosen category's ID to get subcategories",
        "4. Use get_items(subcategory_id) with the chosen subcategory's ID to get items",
        "5. Use get_support_groups to pick an appropriate group",
        "6. Use the users chat messges to provide the description for the ticket and include the details of the issues as mentioned by the user in the chat messages",
        "7. Set the request_type as per the user's request type from the chat messages. The request type can be Incident, Service Request, Preventive Maintenance, Security Incident, Security Request, Request for Information, Change Requests.",
        "8. Call create_manageengine_ticket with all the names (not IDs) for category, subcategory, item",
        "For wifi issues: category='Network & Security', subcategory='Wireless/AP', then pick matching item.",
    ],
    markdown=True,
    telemetry=False,
)

# 6. Create IT Support Team
it_support_team = Team(
    name="IT Support Team",
    id="it-support-team",
    members=[it_support_agent, manage_engine_agent],
    model=llm,
    db=db,
    instructions=[
        "You coordinate IT support for Alpha Data employees.",
        "First, try to answer using the knowledge base via the IT Support Agent.",
        "If the user explicitly asks to log/create a ticket, delegate to ManageEngine Ticket Agent.",
        "IMPORTANT: When delegating to ManageEngine Ticket Agent, include ALL details in the task:",
        "  - Example: 'Create ticket for Howard Stern. Subject: Wifi issues. Description: Wifi not working. Impact: High. Urgency: High'",
        "If the user provides their name and issue details in one message, delegate immediately with all details.",
        "Only ask for missing information if not provided by the user.",
    ],
    pre_hooks=[prompt_injection_guardrail],
    enable_agentic_memory=True,
    enable_user_memories=True,
    stream=True,
    markdown=True,
    num_history_runs=5,
    telemetry=False,
    debug_mode=True,
)

agent_os = AgentOS(
    id="it-support-agent",
    description="IT Support Agent",
    teams=[it_support_team],
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
