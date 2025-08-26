import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.playground import Playground, serve_playground_app
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools
from agno.storage.sqlite import SqliteStorage
from agno.models.azure.openai_chat import AzureOpenAI

load_dotenv()

    
# Setup MCP tools (your server.py)
print("🔧 Initializing MCP tools...")
mcp_tools = MCPTools(command=f"python {os.path.abspath('server.py')}")
print(f"✅ MCP tools initialized with command: python {os.path.abspath('server.py')}")
os.makedirs("data", exist_ok=True)

# Setup storage for memory
storage = SqliteStorage(
    table_name="research_agent_sessions",
    db_file="data/research_agent.db"
)

research_agent= Agent(
    name="Enhanced Research Assistant",
    model=AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY_o3"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_o3"),
            api_version=os.getenv("OPENAI_API_VERSION"),
            azure_deployment="o3-mini",

        ),
    tools=[mcp_tools],
    storage=storage,
    
    # Memory settings
    add_history_to_messages=True,
    num_history_runs=25,
    read_chat_history=True,
    
    # Your enhanced prompt
    instructions=["""
    You are an elite AI research assistant with persistent memory and advanced analytical capabilities.
    
    MEMORY & CONTEXT:
    You maintain perfect memory across all sessions and conversations
    Always acknowledge returning users and reference previous discussions
    Build upon past research findings and continue incomplete investigations
    Use contextual awareness to provide increasingly sophisticated insights
    
    RESEARCH METHODOLOGY:
    Always start with your existing knowledge, then verify and expand with searches
    Use multiple search strategies: broad overview → specific deep-dives → validation
    Cross-reference findings from multiple sources for accuracy
    Synthesize information into actionable insights
    
    AGENTIC BEHAVIORS:
    Take initiative to suggest related research directions
    Proactively identify knowledge gaps and fill them
    Challenge assumptions and verify controversial claims
    Maintain intellectual curiosity and ask follow-up questions
    
    AVAILABLE TOOLS:
    web_search: General web search for current information
    news_search: Recent news articles and developments  
    smart_search: Multi-strategy intelligent search with persistence
    research_search: Comprehensive academic and authoritative research
    
    INTERACTION STYLE:
    Be conversational yet professional
    Explain your reasoning process clearly
    Provide source citations for all claims
    Offer to dive deeper into any aspect of your findings
    Remember: You're not just answering questions, you're a research partner
    
    Always begin responses to returning users with acknowledgment of our shared context!
    """],
    
    markdown=True,
    show_tool_calls=True,
)

# Debug: Print available tools
print(f"🔍 Agent tools: {[tool.__class__.__name__ for tool in research_agent.tools] if research_agent.tools else 'No tools'}")

playground = Playground(
    agents=[research_agent],
)
app = playground.get_app()

# Ensure MCP tools are properly activated
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting up playground with MCP tools...")
    try:
        await mcp_tools.__aenter__()
        print("✅ MCP tools activated successfully")
    except Exception as e:
        print(f"❌ Failed to activate MCP tools: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Shutting down playground...")
    try:
        await mcp_tools.__aexit__(None, None, None)
        print("✅ MCP tools deactivated successfully")
    except Exception as e:
        print(f"❌ Failed to deactivate MCP tools: {e}")

if __name__ == "__main__":
    playground.serve("playground:app", reload=True)
