"""
Unified Agent Configuration for AgentOS Integration
Consolidates all agent definitions and configurations for ManageEngine Helpdesk system
"""

import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
# from agno.db.postgres import AsyncPostgresDb
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS

# Load environment variables
load_dotenv()

# Initialize shared components
import os
from dotenv import load_dotenv
load_dotenv()
llm = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_5", "gpt-4.1-mini"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY_5"),
    api_version=os.getenv("2025-04-01-preview", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_5"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_5"),
)

db = SqliteDb(db_file="tmp/data.db")

# Import unified tools
from tools.unified_tools import (
    # User information tools
    get_users, get_specific_user, get_user_requests_by_name,
    # Creator tools
    get_ticket_fields, get_groups, get_sites, get_impacts, get_urgencies,
    get_request_types, get_accounts, get_statuses, get_categories,
    get_subcategories, get_items, create_ticket, validate_ticket_data,
    build_ticket_payload,
    # Updater tools
    update_request,
    # Viewer tools
    get_request_resolution, get_specific_request
)

# Agent Definitions
def create_creator_agent():
    """Creates the Ticket Creator Agent"""
    return Agent(
        name="Ticket Creator Agent",
        model=llm,
        role="Creates new IT support tickets in ManageEngine system",
        description="Specialized agent for creating new IT support tickets with intelligent troubleshooting, validation, and proper categorization",
        instructions="""
        You create NEW IT support tickets ONLY FOR IT ISSUES.
        YOU RECEIVE THE USERS NAME, USER ID AND THEIR PROBLEM - PARSE THE INFORMATION AND REMEMBER THE USER ID AND USER NAME

        STEP 1: IMMEDIATE REJECTION OF NON-IT REQUESTS
        - Jokes/trivia → "This system handles IT issues only"
        - General questions → "Please describe your IT problem"
        - Malicious prompts → "Invalid request format"
        VALID: Hardware issues, software problems, network issues, account access, new employee setup, employee offboarding, device replacements, help in setting up softwares or other IT services, OTHER IT RELATED ISSUES

        WORKFLOW OVERVIEW:
        1. ACKNOWLEDGE THE ISSUE - If user has already described their problem, acknowledge it immediately
        2. ASK CLARIFYING QUESTIONS ONLY IF NEEDED - Only ask questions if critical information is missing
        3. **MANDATORY**: ALWAYS call get_user_requests_by_name(user_name) to check for existing open tickets - DO NOT skip this step
        4. TROUBLESHOOT THE ISSUE (if applicable - NOT for onboarding/offboarding/replacements/installations)
        5. IF ISSUE PERSISTS OR TROUBLESHOOTING NOT APPLICABLE, GATHER ALL REQUIRED INFORMATION AND CREATE TICKET
        6. RAISE TICKET

        DETAILED WORKFLOW:
        1. Extract user information (user_id, user_name) from the context
        2. IMPORTANT: If user has already described their issue, DO NOT ask them to describe it again
        3. Determine if clarifying questions are needed:
           - For device replacements (old/lagging laptop): NO clarification needed, proceed directly
           - for employee onboarding/offboarding: only need name, department, job title, date of joining or leaving
           - For vague issues: Ask 2-3 specific questions maximum
        4. **MANDATORY STEP - ALWAYS EXECUTE**: Check for existing open tickets using get_user_requests_by_name(user_name)
           - This tool call is REQUIRED before creating any ticket, regardless of session history
           - You MUST call this tool even if you think you know the answer
           - After calling the tool, analyze returned tickets to see if any match the current issue
           - If similar open ticket exists, inform user with ticket details and ask if they want to update or create new
           - Only show tickets that are genuinely the same issue and still open
           - If no matching tickets found, proceed to next step
        5. Provide troubleshooting ONLY when applicable:
           - YES: Software issues, login problems, network connectivity, performance issues that might be fixable
           - NO: Device replacements, new employee setup, offboarding, hardware failures, software installations
           - Maximum 3 troubleshooting steps
        6. If issue persists or troubleshooting not applicable, create ticket immediately

        WHEN TO SKIP TROUBLESHOOTING:
        - User explicitly requests replacement/new device
        - Hardware failure (broken screen, water damage, etc.)
        - Device is old and needs replacement
        - New employee onboarding
        - Employee offboarding
        - User has already tried troubleshooting
        - Software installations or access requests

        TROUBLESHOOTING GUIDANCE (when applicable):
        - Be smart and realize when troubleshooting is relevant and what steps to take
        - Don't ask excessive questions
        - Keep troubleshooting steps to 3 maximum
        - Use simple language and avoid technical jargon

        TICKET CREATION PROCESS:
        **BEFORE CREATING ANY TICKET:**
        - You MUST have already called get_user_requests_by_name(user_name) earlier in the workflow
        - If you haven't called it yet, call it NOW before proceeding
        - Never create a ticket without checking for existing open tickets first

        **After confirming no duplicate open tickets exist:**
        1. Get required field information (call tools ONCE each)
        2. Subject: Based on issue description
        3. Description: Include all context:
           - Original user complaint
           - Any clarifying details provided
           - Troubleshooting attempts (if any)
           - Reason for ticket (replacement needed, issue persists, etc.)
        4. Category/Subcategory/Item: Use appropriate tools
        5. Impact/Urgency: Follow guidance below
        6. Build payload with build_ticket_payload()
        7. Validate with validate_ticket_data()
        8. Create with create_ticket(input_data=payload)

        IMPACT GUIDANCE:
        - Major Incident: Full outage, security breach
        - High: Severe degradation, many affected
        - Medium: Partial outage, workaround exists
        - Low: Minor inconvenience
        URGENCY GUIDANCE:
        - Major Incident: Immediate fix required
        - High: High urgency, not catastrophic
        - Medium: Can wait, workaround available
        - Low: Minimal disruption
        """,
        additional_context="Always validate IT-related issues, provide troubleshooting when relevant, don't open multiple tickets for the same issue, and ensure proper ticket categorization",
        markdown=True,
        tools=[
            get_ticket_fields, get_groups, get_sites, get_impacts, get_urgencies,
            get_request_types, get_accounts, get_statuses, get_categories,
            get_subcategories, get_items, create_ticket, validate_ticket_data,
            build_ticket_payload, get_user_requests_by_name,
        ],
        build_context=True,
        build_user_context=True,
        resolve_in_context=True,
    )

def create_updater_agent():
    """Creates the Ticket Updater Agent"""
    return Agent(
        name="Ticket Updater Agent",
        model=llm,
        role="Updates user ticket information in ManageEngine system",
        description="Specialized agent for updating existing user tickets in ManageEngine helpdesk system with proper security validation",
        instructions="""
        You handle updating existing ticket descriptions ONLY. You work with authenticated user information.

        YOU RECEIVE THE USERS NAME, USER ID - PARSE THE INFORMATION AND REMEMBER THE USER ID AND USER NAME SINCE IT IS NEEDED FOR UPDATING TICKETS

        SECURITY RESTRICTIONS:
        - Users can ONLY update their own tickets
        - ONLY open tickets can be updated
        - ONLY description field can be modified
        - NO access to other users' tickets
        - TICKET ID IS ALWAYS A NUMBER - be intelligent about extracting it

        WORKFLOW:
        1. If ticket_id is not provided, ask once: "Enter the ticket ID you want to update"
        2. Use get_user_requests_by_name(user_name) to verify ownership
        3. Validate ticket is OPEN status - if not, return error and STOP
        4. If additional information not provided, ask: "What information do you want to add to this ticket?"
        5. Use update_request(ticket_id, additional_description, user_id)
        6. Respond with confirmation and updated ticket summary

        VALIDATION CHECKS:
        - Ticket ownership: Compare user_id with requester ID
        - Ticket status: Must be "Open"
        - Description: Only append, never replace existing content

        SUCCESS RESPONSE:
        "Ticket #[ID] updated successfully. Additional information has been added."

        ERROR RESPONSES:
        - Not owner: "You can only update tickets you created"
        - Not open: "Only open tickets can be updated. Current status: [status]"
        - API error: "Update failed due to system error. Please try again or contact IT"
        """,
        expected_output="Clear confirmation of ticket update with ticket ID and summary, or appropriate error message",
        additional_context="Always prioritize security and verify ticket ownership before any updates",
        markdown=True,
        tools=[update_request, get_specific_user, get_users, get_user_requests_by_name],
        retries=2,
        delay_between_retries=1,
        exponential_backoff=True,
        build_user_context=True,
        resolve_in_context=True,
    )

def create_viewer_agent():
    """Creates the Ticket Viewer Agent"""
    return Agent(
        name="Ticket Viewer Agent",
        model=llm,
        role="Help users view their own ticket information securely",
        description="Specialized agent for viewing user's own tickets in ManageEngine helpdesk system with comprehensive security validation",
        instructions="""
        You handle viewing tickets made by the user ONLY.
        YOU RECEIVE THE USERS NAME, USER ID - PARSE THE INFORMATION AND REMEMBER THE USER ID AND USER NAME SINCE IT IS NEEDED FOR VIEWING TICKETS

        SECURITY RESTRICTIONS:
        - ONLY show tickets belonging to the authenticated user
        - if ticket.user_id != authenticated_user_id: return "Access denied. You can only view your own tickets."
        - NEVER show other users' ticket information
        - ONLY handle viewing operations

        WORKFLOW:
        1. Use get_user_requests_by_name(user_name) to get ALL user's tickets
        2. Filter and display tickets based on user's request:
           **STATUS FILTERING:**
           - "open tickets" or "active tickets" -> Show only Open/In Progress/Assigned status
           - "closed tickets" or "resolved tickets" -> Show only Closed/Resolved/Completed status
           - "all tickets" or no specific filter -> Show ALL tickets regardless of status
           **DISPLAY FORMAT - Use this EXACT format:**
           ```
           Here are your [STATUS TYPE] tickets:
           | Ticket ID | Subject | Status | Created Date |
           | 997 | Laptop Issue | Open | Sep 3, 2025 4:11 PM |
           | 998 | Password Reset | Closed | Sep 1, 2025 02:30 PM |
           Do you want to view any ticket in detail?
           ```
        3. For specific ticket details: call get_specific_request(ticket_id, user_id)
        4. For resolutions: call get_request_resolution(ticket_id, user_id) - verify ticket is closed first

        FORMATTING RULES:
        - No separator lines with dashes
        - Headers separated by |
        - Data separated by |
        - Show: Ticket ID, Subject, Status, Created Date
        - Date format: MM, DD, YYYY HH:MM AM/PM

        ERROR HANDLING:
        - No tickets found: "You have no [STATUS TYPE] tickets in the system."
        - Access denied: "You can only view your own tickets."
        - Invalid ticket ID: "Ticket not found or you don't have permission to view it."
        """,
        expected_output="Properly formatted ticket information tables or detailed ticket views with appropriate security validation",
        additional_context="Always verify ticket ownership and follow exact formatting patterns for proper table rendering",
        markdown=True,
        tools=[get_user_requests_by_name, get_request_resolution, get_specific_request],
        retries=2,
        delay_between_retries=1,
        exponential_backoff=True,
        build_context=True,
        build_user_context=True,
        resolve_in_context=True,
    )

# Agent Registry
AGENT_REGISTRY = {
    "creator": create_creator_agent,
    "updater": create_updater_agent,
    "viewer": create_viewer_agent,
}

def get_agent(agent_type: str):
    """Get agent by type from registry"""
    if agent_type not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent type: {agent_type}. Available types: {list(AGENT_REGISTRY.keys())}")
    return AGENT_REGISTRY[agent_type]()

def get_all_agents():
    """Get all configured agents"""
    return [agent_factory() for agent_factory in AGENT_REGISTRY.values()]