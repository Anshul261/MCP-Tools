# agents/team_coordinator.py
from typing import Optional
from textwrap import dedent
from agno.team.team import Team
from agno.tools.reasoning import ReasoningTools

from agents.base import BaseTeamFactory, agent_registry
from agents.document_agent import DocumentAgentFactory
from agents.web_agent import WebAgentFactory
import logging

logger = logging.getLogger(__name__)


class ReasoningTeamFactory(BaseTeamFactory):
    """Factory for creating reasoning knowledge teams"""
    
    def __init__(self):
        super().__init__()
        self.doc_agent_factory = DocumentAgentFactory()
        self.web_agent_factory = WebAgentFactory()
    
    @property
    def team_id(self) -> str:
        return "reasoning_team"
    
    @property
    def team_name(self) -> str:
        return "Reasoning Knowledge Team"
    
    @property
    def team_description(self) -> str:
        return "Team that coordinates between document search and web search to provide comprehensive answers"
    
    def create_team(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = False
    ) -> Team:
        """Create reasoning knowledge team"""
        
        logger.info(f"Creating reasoning team for user_id={user_id}, session_id={session_id}")
        
        # Create team members
        doc_agent = self.doc_agent_factory.create_agent(user_id, session_id, debug_mode)
        web_agent = self.web_agent_factory.create_agent(user_id, session_id, debug_mode)
        
        # Get base configuration
        config = self.get_base_team_config(user_id, session_id, debug_mode)
        
        # Add team-specific configuration
        config.update({
            "name": self.team_name,
            "mode": "coordinate",
            "members": [doc_agent, web_agent],
            "tools": [ReasoningTools(add_instructions=True)],
            "description": dedent("""\
                You are a Team Coordinator that manages document search and web search agents.
                
                Your goal is to provide comprehensive answers by leveraging both local documents and web information.
            """),
            "instructions": dedent("""\
                As a Team Coordinator, follow this process:

                1. **Initial Assessment:**
                   - Analyze the user's question to determine information needs
                   - Always search local documents first, if not information is found in documents, then move to web search, or both simultaneously

                2. **Coordination Strategy:**
                   - For specific topics that might be in documents: Start with document search
                   - For current events or recent information: Start with web search
                   - For comprehensive analysis: Use both agents and combine results

                3. **Information Synthesis:**
                   - Combine information from both agents effectively
                   - Resolve any conflicts between sources
                   - Provide a unified, coherent response

                4. **Citation Requirements:**
                   - Always cite sources clearly (documents vs. web sources)
                   - Distinguish between different types of information sources
                   - Maintain transparency about information origins

                5. **Conversation Continuity:**
                   - Remember previous conversations and build upon them
                   - Track what information has been provided before
                   - Avoid unnecessary repetition while maintaining context

                Decision Framework:
                - Documents FIRST: Technical specifications, internal policies like HR documents, historical records
                - Web FIRST: Current events, breaking news, recent developments, and trends in general
                - BOTH: Research topics, comprehensive analysis, fact-checking, code deubugging, and document writing

                Additional Information:
                - You are interacting with user_id: {current_user_id}
                - Session ID: {session_id}
                - Prioritize accuracy and comprehensive coverage
            """),
            "success_criteria": "Complete analysis with proper citations and continuity from previous conversations",
            "add_state_in_messages": True,
        })
        
        return Team(**config)


# Register the reasoning team factory
reasoning_team_factory = ReasoningTeamFactory()
agent_registry.register_team_factory(reasoning_team_factory)