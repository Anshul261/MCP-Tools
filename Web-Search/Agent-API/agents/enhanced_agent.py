"""
Enhanced Research Agent implementation for Agent API
"""
import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.storage.postgres import PostgresStorage
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from agents.search_tools import SEARCH_TOOLS
from db.models import AgentSession, AgentMessage, AgentMemory, AgentMetrics

logger = logging.getLogger(__name__)


class EnhancedSearchAgent:
    """
    Enhanced Research Agent with PostgreSQL storage and search capabilities
    """
    
    def __init__(self, db_session: AsyncSession, user_id: str = "default_user"):
        self.db_session = db_session
        self.user_id = user_id
        self.agent = None
        self.session_id = None
        self.storage = None
        self.model = None
        
        # Metrics for tracking
        self.metrics = {
            "queries_processed": 0,
            "tool_calls_made": 0,
            "successful_responses": 0,
            "research_topics": set(),
        }
    
    async def initialize(self, session_id: Optional[str] = None):
        """Initialize the agent with database storage"""
        logger.info(f"Initializing Enhanced Research Agent for user: {self.user_id}")
        
        # Setup Ollama model
        self.model = Ollama(
            id="yasserrmd/jan-nano-4b:latest",
            provider="Ollama",
        )
        
        # Setup storage for development
        # Note: Using SQLite instead of PostgresStorage for now
        # PostgresStorage will be configured when needed
        self.storage = None  # Will use database session directly
        
        # Handle session management
        if session_id:
            self.session_id = session_id
            await self._load_or_create_session()
        else:
            await self._create_new_session()
        
        logger.info("✅ Enhanced Research Agent initialized successfully")
    
    async def _load_or_create_session(self):
        """Load existing session or create new one"""
        # Check if session exists in database
        result = await self.db_session.execute(
            select(AgentSession).where(
                AgentSession.session_id == self.session_id,
                AgentSession.user_id == self.user_id
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            # Create new session
            await self._create_new_session()
        else:
            logger.info(f"📂 Loaded existing session: {self.session_id}")
    
    async def _create_new_session(self):
        """Create a new agent session"""
        import uuid
        
        self.session_id = str(uuid.uuid4())
        
        # Create session in database
        new_session = AgentSession(
            user_id=self.user_id,
            session_id=self.session_id,
            agent_name="Enhanced Research Assistant",
            config={
                "model": "yasserrmd/jan-nano-4b:latest",
                "tools": list(SEARCH_TOOLS.keys()),
                "memory_enabled": True,
                "search_enabled": True,
            }
        )
        
        self.db_session.add(new_session)
        await self.db_session.commit()
        
        logger.info(f"🆕 Created new session: {self.session_id}")
    
    async def create_agent(self):
        """Create the Agno agent with tools and configuration"""
        
        # Create wrapper functions for search tools
        search_tool_wrappers = []
        
        # Web search wrapper
        async def web_search_wrapper(query: str, count: int = 10, **kwargs):
            """Web search tool"""
            self.metrics["tool_calls_made"] += 1
            result = await SEARCH_TOOLS["web_search"](query, count, **kwargs)
            await self._log_tool_call("web_search", {"query": query, "count": count}, result)
            return result
        
        # News search wrapper
        async def news_search_wrapper(query: str, count: int = 10, **kwargs):
            """News search tool"""
            self.metrics["tool_calls_made"] += 1
            result = await SEARCH_TOOLS["news_search"](query, count, **kwargs)
            await self._log_tool_call("news_search", {"query": query, "count": count}, result)
            return result
        
        # Smart search wrapper
        async def smart_search_wrapper(query: str, **kwargs):
            """Smart search tool"""
            self.metrics["tool_calls_made"] += 1
            result = await SEARCH_TOOLS["smart_search"](query, **kwargs)
            await self._log_tool_call("smart_search", {"query": query}, result)
            return result
        
        # Research search wrapper
        async def research_search_wrapper(topic: str, **kwargs):
            """Research search tool"""
            self.metrics["tool_calls_made"] += 1
            result = await SEARCH_TOOLS["research_search"](topic, **kwargs)
            await self._log_tool_call("research_search", {"topic": topic}, result)
            return result
        
        # Create agent with tools (without storage for now)
        self.agent = Agent(
            name="Enhanced Research Assistant",
            user_id=self.user_id,
            session_id=self.session_id,
            model=self.model,
            # storage=self.storage,  # Commented out for now
            
            # Add search tools as functions
            tools=[
                web_search_wrapper,
                news_search_wrapper,
                smart_search_wrapper,
                research_search_wrapper,
            ],
            
            # Memory and conversation settings
            add_history_to_messages=True,
            num_history_runs=25,
            read_chat_history=True,
            
            # Agent behavior settings
            markdown=True,
            show_tool_calls=True,
            debug_mode=False,
            
            instructions="""
            You are an elite AI research assistant with persistent memory and advanced analytical capabilities.
            
            MEMORY & CONTEXT:
            - You maintain perfect memory across all sessions and conversations
            - Always acknowledge returning users and reference previous discussions
            - Build upon past research findings and continue incomplete investigations
            - Use contextual awareness to provide increasingly sophisticated insights
            
            RESEARCH METHODOLOGY:
            - Always start with your existing knowledge, then verify and expand with searches
            - Use multiple search strategies: broad overview → specific deep-dives → validation
            - Cross-reference findings from multiple sources for accuracy
            - Synthesize information into actionable insights
            
            AGENTIC BEHAVIORS:
            - Take initiative to suggest related research directions
            - Proactively identify knowledge gaps and fill them
            - Challenge assumptions and verify controversial claims
            - Maintain intellectual curiosity and ask follow-up questions
            
            AVAILABLE TOOLS:
            - web_search: General web search for current information
            - news_search: Recent news articles and developments  
            - smart_search: Multi-strategy intelligent search with persistence
            - research_search: Comprehensive academic and authoritative research
            
            INTERACTION STYLE:
            - Be conversational yet professional
            - Explain your reasoning process clearly
            - Provide source citations for all claims
            - Offer to dive deeper into any aspect of your findings
            - Remember: You're not just answering questions, you're a research partner
            
            Always begin responses to returning users with acknowledgment of our shared context!
            """,
        )
        
        logger.info("🤖 Enhanced agent with search tools created successfully")
    
    async def _log_tool_call(self, tool_name: str, params: Dict[str, Any], result: Any):
        """Log tool call for metrics and debugging"""
        try:
            # Log to database
            tool_call_record = AgentMetrics(
                user_id=self.user_id,
                session_id=self.session_id,
                metric_type="tool_call",
                metric_name=tool_name,
                value={
                    "params": params,
                    "result_count": len(result) if isinstance(result, list) else 1,
                    "success": "error" not in str(result),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            
            self.db_session.add(tool_call_record)
            await self.db_session.commit()
            
        except Exception as e:
            logger.warning(f"Failed to log tool call: {e}")
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query and return structured response"""
        
        self.metrics["queries_processed"] += 1
        
        # Extract research topics for metrics
        keywords = query.lower().split()
        research_terms = [word for word in keywords if len(word) > 4]
        self.metrics["research_topics"].update(research_terms[:3])
        
        try:
            # Save user message
            user_message = AgentMessage(
                session_id=self.session_id,
                role="user",
                content=query,
                meta_data={"timestamp": datetime.utcnow().isoformat()}
            )
            self.db_session.add(user_message)
            
            # Process with agent
            response = await self.agent.arun(query)
            
            # Extract content from response if it's a RunResponse object
            response_content = response
            if hasattr(response, 'content'):
                response_content = response.content
            elif hasattr(response, 'messages') and response.messages:
                response_content = response.messages[-1].content if response.messages else str(response)
            else:
                response_content = str(response)
            
            # Save assistant response
            assistant_message = AgentMessage(
                session_id=self.session_id,
                role="assistant",
                content=response_content,
                meta_data={"timestamp": datetime.utcnow().isoformat()}
            )
            self.db_session.add(assistant_message)
            
            await self.db_session.commit()
            
            self.metrics["successful_responses"] += 1
            
            return {
                "response": response_content,
                "session_id": self.session_id,
                "user_id": self.user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "queries_processed": self.metrics["queries_processed"],
                    "tool_calls_made": self.metrics["tool_calls_made"],
                    "successful_responses": self.metrics["successful_responses"],
                }
            }
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                "error": str(e),
                "session_id": self.session_id,
                "user_id": self.user_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    async def get_session_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for the session"""
        
        result = await self.db_session.execute(
            select(AgentMessage)
            .where(AgentMessage.session_id == self.session_id)
            .order_by(desc(AgentMessage.created_at))
            .limit(limit)
        )
        
        messages = result.scalars().all()
        
        return [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
                "metadata": msg.metadata,
            }
            for msg in reversed(messages)
        ]
    
    async def get_agent_metrics(self) -> Dict[str, Any]:
        """Get comprehensive agent metrics"""
        
        # Get session count
        session_count = await self.db_session.execute(
            select(AgentSession)
            .where(AgentSession.user_id == self.user_id)
        )
        sessions = session_count.scalars().all()
        
        # Get tool call metrics
        tool_metrics = await self.db_session.execute(
            select(AgentMetrics)
            .where(
                AgentMetrics.user_id == self.user_id,
                AgentMetrics.metric_type == "tool_call"
            )
        )
        tool_calls = tool_metrics.scalars().all()
        
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "total_sessions": len(sessions),
            "current_session_metrics": self.metrics,
            "total_tool_calls": len(tool_calls),
            "tool_call_breakdown": {
                call.metric_name: call.value for call in tool_calls
            },
            "agent_status": {
                "model": "yasserrmd/jan-nano-4b:latest",
                "storage": "PostgreSQL",
                "tools_enabled": list(SEARCH_TOOLS.keys()),
                "memory_enabled": True,
            }
        }
    
    async def cleanup(self):
        """Cleanup agent resources"""
        try:
            if self.agent:
                # Agno cleanup if needed
                pass
            logger.info("🧹 Agent resources cleaned up")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")


# Factory function for creating agents
async def create_enhanced_agent(
    db_session: AsyncSession,
    user_id: str,
    session_id: Optional[str] = None
) -> EnhancedSearchAgent:
    """
    Factory function to create and initialize an enhanced agent
    """
    agent = EnhancedSearchAgent(db_session, user_id)
    await agent.initialize(session_id)
    await agent.create_agent()
    return agent