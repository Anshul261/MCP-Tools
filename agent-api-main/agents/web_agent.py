# agents/web_agent.py
from typing import Optional
from textwrap import dedent
from agno.agent import Agent
from agno.tools.bravesearch import BraveSearchTools

from agents.base import BaseAgentFactory, agent_registry
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class WebAgentFactory(BaseAgentFactory):
    """Factory for creating web search agents"""
    
    @property
    def agent_id(self) -> str:
        return "web_agent"
    
    @property
    def agent_name(self) -> str:
        return "Web Agent"
    
    @property
    def agent_description(self) -> str:
        return "Web search agent that helps users find the latest news and information"
    
    def create_agent(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = False
    ) -> Agent:
        """Create web search agent"""
        
        logger.info(f"Creating web agent for user_id={user_id}, session_id={session_id}")
        
        # Get base configuration
        config = self.get_base_agent_config(user_id, session_id, debug_mode)
        
        # Add web search tools if API key is available
        tools = []
        if settings.external.brave_api_key:
            tools.append(BraveSearchTools())
            logger.info("Added Brave Search tools to web agent")
        else:
            logger.warning("Brave API key not found, web agent will have limited functionality")
        
        # Add web-specific configuration
        config.update({
            "name": self.agent_name,
            "agent_id": self.agent_id,
            "tools": tools,
            "description": dedent("""\
                You are a Web Search Agent that specializes in finding current information from the internet.
                
                Your goal is to provide up-to-date, accurate information with proper citations.
            """),
            "instructions": dedent("""\
                As a Web Search Agent, follow these guidelines:

                1. **Search Strategy:**
                   - Use precise search terms related to the user's question
                   - Search iteratively for comprehensive information
                   - Focus on recent and reliable sources

                2. **Response Guidelines:**
                   - Always provide citations for sources used
                   - Prioritize authoritative and recent sources
                   - Be clear about the recency of information
                   - Remember previous searches to avoid redundancy

                3. **Information Quality:**
                   - Verify information across multiple sources when possible
                   - Note any conflicting information found
                   - Provide context about source reliability

                4. **Search Optimization:**
                   - Given a topic by the user, search for results about that topic
                   - Iteratively search for more items until you have comprehensive information
                   - Always provide citations for sources used to answer questions
                   - Remember previous searches and conversations to provide better context

                Additional Information:
                - You are interacting with user_id: {current_user_id}
                - Session ID: {session_id}
                - Focus on current events and real-time information
            """),
            "add_state_in_messages": True,
        })
        
        return Agent(**config)


# Register the web agent factory
web_agent_factory = WebAgentFactory()
agent_registry.register_agent_factory(web_agent_factory)