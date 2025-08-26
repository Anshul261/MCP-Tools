# agents/document_agent.py
from typing import Optional
from textwrap import dedent
from agno.agent import Agent

from agents.base import BaseAgentFactory, agent_registry
from core.database import db_manager
import logging

logger = logging.getLogger(__name__)


class DocumentAgentFactory(BaseAgentFactory):
    """Factory for creating document search agents"""
    
    @property
    def agent_id(self) -> str:
        return "doc_agent"
    
    @property
    def agent_name(self) -> str:
        return "Document Agent"
    
    @property
    def agent_description(self) -> str:
        return "RAG Assistant with local document search capabilities"
    
    def create_agent(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = False
    ) -> Agent:
        """Create document search agent"""
        
        logger.info(f"Creating document agent for user_id={user_id}, session_id={session_id}")
        
        # Get base configuration
        config = self.get_base_agent_config(user_id, session_id, debug_mode)
        
        # Add document-specific configuration
        config.update({
            "name": self.agent_name,
            "agent_id": self.agent_id,
            "knowledge": db_manager.knowledge_base,
            "description": dedent("""\
                You are a Document Search Agent that specializes in finding and analyzing information from uploaded documents.
                
                Your goal is to provide accurate, well-sourced answers based on the available document collection.
            """),
            "instructions": dedent("""\
                As a Document Search Agent, follow these guidelines:

                1. **Search Strategy:**
                   - Always search the knowledge base first for relevant information
                   - Use precise search terms related to the user's question
                   - If initial results are insufficient, try alternative search terms

                2. **Response Guidelines:**
                   - Always cite your sources clearly from the documents
                   - Provide accurate and comprehensive answers based on available context
                   - If information is not available in the documents, clearly state this
                   - Remember previous conversations and build upon them

                3. **Source Citation:**
                   - Include specific document names and sections when possible
                   - Use clear citations in your responses
                   - Distinguish between information from documents vs. general knowledge

                4. **Conversation Continuity:**
                   - Remember previous searches and conversations
                   - Build upon previous context to provide better answers
                   - Maintain conversation flow and context

                Additional Information:
                - You are interacting with user_id: {current_user_id}
                - Session ID: {session_id}
                - Always prioritize document-based information over general knowledge
            """),
            "search_knowledge": True,
            "add_state_in_messages": True,
        })
        
        return Agent(**config)


# Register the document agent factory
document_agent_factory = DocumentAgentFactory()
agent_registry.register_agent_factory(document_agent_factory)