from agno.playground import Playground

from agents.agno_assist import get_agno_assist
from agents.finance_agent import get_finance_agent
from agents.web_agent import get_web_agent
from agents.document_agent import get_document_agent, get_web_search_agent
from agents.team_coordinator import get_reasoning_knowledge_team

######################################################
## Routes for the Playground Interface
######################################################

# Get original agents
web_agent = get_web_agent(debug_mode=True)
agno_assist = get_agno_assist(debug_mode=True)
finance_agent = get_finance_agent(debug_mode=True)

# Get your custom agents
document_agent = get_document_agent(debug_mode=True)
web_search_agent = get_web_search_agent(debug_mode=True)
reasoning_team = get_reasoning_knowledge_team(debug_mode=True)

# Create a playground instance with all agents
playground = Playground(agents=[
    web_agent, 
    agno_assist, 
    finance_agent,
    document_agent,
    web_search_agent,
    reasoning_team
])

# Get the router for the playground
playground_router = playground.get_async_router()