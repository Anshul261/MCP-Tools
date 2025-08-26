# agents/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from agno.agent import Agent
from agno.team.team import Team

from core.database import db_manager
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class BaseAgentFactory(ABC):
    """Abstract base class for agent factories"""
    
    def __init__(self):
        self.db_manager = db_manager
        self.settings = settings
    
    @abstractmethod
    def create_agent(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = False
    ) -> Agent:
        """Create and return an agent instance"""
        pass
    
    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Return the agent identifier"""
        pass
    
    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return the agent name"""
        pass
    
    @property
    @abstractmethod
    def agent_description(self) -> str:
        """Return the agent description"""
        pass
    
    def get_agent_storage(self, table_suffix: str = None):
        """Get agent storage with proper table naming"""
        table_name = f"{self.agent_id}_sessions"
        if table_suffix:
            table_name += f"_{table_suffix}"
        return self.db_manager.get_agent_storage(table_name)
    
    def get_base_agent_config(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = False
    ) -> Dict[str, Any]:
        """Get base configuration for all agents"""
        return {
            "user_id": user_id,
            "session_id": session_id,
            "model": self.db_manager.azure_model,
            "memory": self.db_manager.memory,
            "storage": self.get_agent_storage(),
            "enable_user_memories": True,
            "enable_session_summaries": True,
            "enable_agentic_memory": True,
            "add_history_to_messages": True,
            "num_history_runs": 6,
            "show_tool_calls": True,
            "markdown": True,
            "debug_mode": debug_mode,
        }


class BaseTeamFactory(ABC):
    """Abstract base class for team factories"""
    
    def __init__(self):
        self.db_manager = db_manager
        self.settings = settings
    
    @abstractmethod
    def create_team(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = False
    ) -> Team:
        """Create and return a team instance"""
        pass
    
    @property
    @abstractmethod
    def team_id(self) -> str:
        """Return the team identifier"""
        pass
    
    @property
    @abstractmethod
    def team_name(self) -> str:
        """Return the team name"""
        pass
    
    @property
    @abstractmethod
    def team_description(self) -> str:
        """Return the team description"""
        pass
    
    def get_team_storage(self, table_suffix: str = None):
        """Get team storage with proper table naming"""
        table_name = f"{self.team_id}_sessions"
        if table_suffix:
            table_name += f"_{table_suffix}"
        return self.db_manager.get_agent_storage(table_name)
    
    def get_base_team_config(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = False
    ) -> Dict[str, Any]:
        """Get base configuration for all teams"""
        return {
            "user_id": user_id,
            "session_id": session_id,
            "model": self.db_manager.azure_model,
            "memory": self.db_manager.memory,
            "storage": self.get_team_storage(),
            "enable_user_memories": True,
            "enable_session_summaries": True,
            "enable_agentic_memory": True,
            "add_history_to_messages": True,
            "num_history_runs": 6,
            "markdown": True,
            "show_members_responses": True,
            "enable_agentic_context": True,
            "add_datetime_to_instructions": True,
            "debug_mode": debug_mode,
        }


class AgentRegistry:
    """Registry for managing agent and team factories"""
    
    def __init__(self):
        self._agent_factories: Dict[str, BaseAgentFactory] = {}
        self._team_factories: Dict[str, BaseTeamFactory] = {}
    
    def register_agent_factory(self, factory: BaseAgentFactory):
        """Register an agent factory"""
        self._agent_factories[factory.agent_id] = factory
        logger.info(f"Registered agent factory: {factory.agent_id}")
    
    def register_team_factory(self, factory: BaseTeamFactory):
        """Register a team factory"""
        self._team_factories[factory.team_id] = factory
        logger.info(f"Registered team factory: {factory.team_id}")
    
    def get_agent_factory(self, agent_id: str) -> Optional[BaseAgentFactory]:
        """Get agent factory by ID"""
        return self._agent_factories.get(agent_id)
    
    def get_team_factory(self, team_id: str) -> Optional[BaseTeamFactory]:
        """Get team factory by ID"""
        return self._team_factories.get(team_id)
    
    def list_agents(self) -> list[str]:
        """List all registered agent IDs"""
        return list(self._agent_factories.keys())
    
    def list_teams(self) -> list[str]:
        """List all registered team IDs"""
        return list(self._team_factories.keys())
    
    def list_all(self) -> list[str]:
        """List all registered agents and teams"""
        return self.list_agents() + self.list_teams()
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, str]]:
        """Get agent information"""
        factory = self.get_agent_factory(agent_id)
        if factory:
            return {
                "id": factory.agent_id,
                "name": factory.agent_name,
                "description": factory.agent_description,
                "type": "agent"
            }
        return None
    
    def get_team_info(self, team_id: str) -> Optional[Dict[str, str]]:
        """Get team information"""
        factory = self.get_team_factory(team_id)
        if factory:
            return {
                "id": factory.team_id,
                "name": factory.team_name,
                "description": factory.team_description,
                "type": "team"
            }
        return None
    
    def create_agent_or_team(
        self,
        identifier: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = False
    ):
        """Create agent or team by identifier"""
        # Try agent factories first
        agent_factory = self.get_agent_factory(identifier)
        if agent_factory:
            return agent_factory.create_agent(user_id, session_id, debug_mode)
        
        # Try team factories
        team_factory = self.get_team_factory(identifier)
        if team_factory:
            return team_factory.create_team(user_id, session_id, debug_mode)
        
        raise ValueError(f"No agent or team factory found for identifier: {identifier}")


# Global agent registry
agent_registry = AgentRegistry()