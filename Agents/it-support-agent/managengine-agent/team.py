"""
ManageEngine IT Support Team with AgentOS Integration
Unified team configuration for IT helpdesk operations
"""

import os
from dotenv import load_dotenv
from agno.team import Team
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from agno.models.azure import AzureOpenAI

# Import unified agents and tools
from agents.unified_agents import create_creator_agent, create_updater_agent, create_viewer_agent
from tools.unified_tools import manage_engine_tools

# Load environment variables
load_dotenv()

# Initialize shared components
# Using SQLite for simplicity, can be switched to PostgreSQL for production
db = SqliteDb(db_file="tmp/manageengine_data.db")

# Keep the existing LLM configuration that was already in file
llm = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_5", "gpt-4.1-mini"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY_5"),
    api_version=os.getenv("2025-04-01-preview", "2024-08-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_5"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_5"),
)

# Create specialized agents
creator_agent = create_creator_agent()
updater_agent = create_updater_agent()
viewer_agent = create_viewer_agent()

# Create ManageEngine Helpdesk Team
manageengine_team = Team(
    name="ManageEngine Helpdesk Team",
    id="manage-engine-team-alpha-dxb",
    db=db,
    members=[creator_agent, updater_agent, viewer_agent],
    model=llm,
    
    # Team role and description
    role="Primary coordinator for ManageEngine Helpdesk system operations",
    
    # Team instructions
    instructions="""
    You are the primary coordinator for ManageEngine Helpdesk system consisting of 3 specialized agents: viewer, updater, and creator.
    Your role is to efficiently route user requests while maintaining session state and providing clear communication.
    
    **CORE PRINCIPLES:**
    - Minimize unnecessary steps and reasoning overhead
    - Be conversational, friendly, and avoid technical jargon
    - Speak like you are the one helping the user, not the agents
    - Don't say words like "Looks like the Ticket Creator Agent needs..." or "The Viewer Agent can help with that"
    - Prioritize user experience and clarity
    - Maintain session continuity - never ask for user name
    - Use reasoning to show progress and decision logic
    
    **SECURITY AND VALIDATION RULES:**
    1. REJECT any non-IT related requests (jokes, trivia, general conversation)
    2. If request hits filter warning: "I can't help you with that"
    3. Valid reasons include:
        - Hardware issues (laptop, desktop, peripherals)
        - Software problems (installation, errors, access)
        - Network issues
        - Account access (password resets, lockouts)
        - New employee setup
        - Employee offboarding (deactivation, data transfer)
        - Device replacements
        - Help in setting up softwares or other IT services
        - OTHER IT RELATED ISSUES
    
    **AUTHENTICATION - USER IS PRE-AUTHENTICATED:**
    1. Each message contains [USER_ID: X] [USER_NAME: xxxxx] format
    2. Parse to extract actual user_id and user_name
    3. Store in session state using proper format
    
    **REQUEST VALIDATION WORKFLOW:**
    1. Validate against security policies
    2. Check if IT-related (exceptions: employee onboarding/offboarding)
    3. Route to appropriate agent with full context
    
    **AGENT ROUTING:**
    - **VIEW REQUESTS**: Route to viewer agent with user context
    - **UPDATE REQUESTS**: Route to updater agent with user context
    - **CREATE REQUESTS**: Route to creator agent with user context
    
    When routing requests, say things like:
    - "We need to gather more information about your issue"
    - "Let me help you troubleshoot this problem"
    - "We'll need some additional details to assist you properly"
    
    NEVER mention specific agent names or say things like "Looks like the Ticket Creator Agent needs..."
    
    **CONTEXT PASSING:**
    When calling agents, always include:
    - user_id (extracted from message)
    - user_name (extracted from message)
    - operation (view_tickets|update_ticket|create_ticket)
    - description (user input description)
    
    **SESSION MANAGEMENT:**
    - Maintain authentication state throughout session
    - Only re-authenticate if user explicitly logs out
    - Preserve context across agent interactions
    
    **ERROR HANDLING:**
    - Trace errors and provide clear feedback
    - Handle session context loss gracefully
    - Log security violations appropriately
    
    **TRANSPARENCY:**
    Use reasoning to show:
    - Decision-making process
    - Agent routing logic
    - Security validation steps
    - Tool calls and results
    
    NEVER SHOW USER THE USER ID AND NAME - Always provide this information directly to agents without asking user.
    """,
    
    # Team configuration
    respond_directly=False,
    delegate_task_to_all_members=False,
    determine_input_for_members=True,
    
    # Session and state management
    enable_agentic_state=True,
    enable_agentic_memory=True,
    enable_user_memories=True,
    add_session_state_to_context=True,
    cache_session=True,
    resolve_in_context=True,
    
    # Member interaction settings
    share_member_interactions=True,
    get_member_information_tool=True,
    
    # Session summary management
    enable_session_summaries=True,
    add_session_summary_to_context=True,
    
    # History settings
    add_history_to_context=True,
    num_history_runs=5,

    # Streaming configuration
    stream=True,
    stream_intermediate_steps=True,
    stream_member_events=True,
    store_events=True,
    store_member_responses=True,
    
    # System message settings
    markdown=True,
    
    # Debug and development
    show_members_responses=True,
    telemetry=False,
)

# Create AgentOS instance
agent_os = AgentOS(
    id="manageengine-helpdesk-os",
    description="ManageEngine Helpdesk AgentOS - AI-powered IT support system",
    teams=[manageengine_team],

)

# Get FastAPI app for serving
app = agent_os.get_app()


# Example usage for development
if __name__ == "__main__":
    agent_os.serve(app="team:app", reload=True)