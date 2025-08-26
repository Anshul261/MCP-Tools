# agents/selector.py
from typing import Optional, List, Dict, Any, Union
from enum import Enum

from agents.base import agent_registry
from agno.agent import Agent
from agno.team.team import Team
import logging

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Enumeration of available agent types"""
    DOC_AGENT = "doc_agent"
    WEB_AGENT = "web_agent"
    REASONING_TEAM = "reasoning_team"


def get_available_agents() -> List[str]:
    """Returns a list of all available agent and team IDs"""
    return agent_registry.list_all()


def get_agent_info(agent_id: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific agent or team"""
    # Try agent first
    info = agent_registry.get_agent_info(agent_id)
    if info:
        return info
    
    # Try team
    info = agent_registry.get_team_info(agent_id)
    if info:
        return info
    
    return None


def list_all_agents_info() -> List[Dict[str, Any]]:
    """Get information about all available agents and teams"""
    agents_info = []
    
    # Add all agents
    for agent_id in agent_registry.list_agents():
        info = agent_registry.get_agent_info(agent_id)
        if info:
            agents_info.append(info)
    
    # Add all teams
    for team_id in agent_registry.list_teams():
        info = agent_registry.get_team_info(team_id)
        if info:
            agents_info.append(info)
    
    return agents_info


def get_agent(
    agent_id: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = False
) -> Union[Agent, Team]:
    """
    Get an agent or team instance by ID
    
    Args:
        agent_id: The identifier of the agent or team
        user_id: Optional user identifier
        session_id: Optional session identifier
        debug_mode: Whether to enable debug mode
    
    Returns:
        Agent or Team instance
    
    Raises:
        ValueError: If agent_id is not found
    """
    try:
        return agent_registry.create_agent_or_team(
            identifier=agent_id,
            user_id=user_id,
            session_id=session_id,
            debug_mode=debug_mode
        )
    except ValueError as e:
        logger.error(f"Failed to create agent {agent_id}: {e}")
        raise


def validate_agent_id(agent_id: str) -> bool:
    """Validate if agent_id exists"""
    return agent_id in get_available_agents()


# Import agent factories to trigger registration
from agents.document_agent import document_agent_factory
from agents.web_agent import web_agent_factory
from agents.team_coordinator import reasoning_team_factory

logger.info(f"Agent selector initialized with agents: {get_available_agents()}")