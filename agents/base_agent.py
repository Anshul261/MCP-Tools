"""
Base Agent class for Multi-Agent System
Provides common functionality and memory integration for all agents
"""

import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.storage.sqlite import SqliteStorage

load_dotenv()


class BaseAgent:
    """Base class for all agents in the Multi-Agent System"""
    
    def __init__(
        self,
        name: str,
        agent_id: str,
        instructions: List[str],
        tools: Optional[List] = None,
        knowledge: Optional[Any] = None,
        storage_table: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize base agent with common configuration
        
        Args:
            name: Human-readable agent name
            agent_id: Unique identifier for the agent
            instructions: List of instructions for the agent
            tools: Optional list of tools for the agent
            knowledge: Optional knowledge base for the agent
            storage_table: Optional custom storage table name
            **kwargs: Additional arguments passed to Agent
        """
        self.name = name
        self.agent_id = agent_id
        
        # Setup storage for persistent memory
        if storage_table is None:
            storage_table = f"{agent_id}_sessions"
        
        self.storage = SqliteStorage(
            table_name=storage_table,
            db_file=f"data/{agent_id}_memory.db"
        )
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Common agent configuration following AGNO best practices
        base_instructions = [
            f"You are {name}, a specialized AI agent in a multi-agent system.",
            "You work collaboratively with other agents to solve complex problems.",
            "Always provide clear, accurate, and well-sourced information.",
            "Maintain context awareness and build upon previous interactions.",
            "When uncertain, clearly communicate your limitations and suggest alternatives.",
        ]
        
        # Combine base instructions with specific instructions
        combined_instructions = base_instructions + instructions
        
        # Initialize the AGNO Agent
        self.agent = Agent(
            name=name,
            model=self._get_model(),
            tools=tools or [],
            knowledge=knowledge,
            storage=self.storage,
            instructions=combined_instructions,
            
            # Memory and context settings
            add_history_to_messages=True,
            num_history_runs=20,  # Keep last 20 interactions
            read_chat_history=True,
            
            # UI settings
            markdown=True,
            show_tool_calls=True,
            **kwargs
        )
    
    def _get_model(self) -> AzureOpenAI:
        """Get configured Azure OpenAI model"""
        return AzureOpenAI(
            id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities for coordination"""
        return {
            "name": self.name,
            "agent_id": self.agent_id,
            "tools": [tool.__class__.__name__ if hasattr(tool, '__class__') else str(tool) 
                     for tool in self.agent.tools] if self.agent.tools else [],
            "knowledge": bool(self.agent.knowledge),
            "memory": True,  # All agents have memory
        }
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Process a query with optional context from other agents
        
        Args:
            query: The user query to process
            context: Optional context from other agents or coordinator
            
        Returns:
            Agent's response as string
        """
        # Add context to query if provided
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            enhanced_query = f"Context from other agents:\n{context_str}\n\nUser Query: {query}"
        else:
            enhanced_query = query
        
        # Get response from agent
        response = self.agent.run(enhanced_query)
        return response.content if hasattr(response, 'content') else str(response)
    
    async def aprocess_query(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Async version of process_query for agents with async tools (like MCP)
        
        Args:
            query: The user query to process
            context: Optional context from other agents or coordinator
            
        Returns:
            Agent's response as string
        """
        # Add context to query if provided
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            enhanced_query = f"Context from other agents:\n{context_str}\n\nUser Query: {query}"
        else:
            enhanced_query = query
        
        # Get response from agent using async method
        response = await self.agent.arun(enhanced_query)
        return response.content if hasattr(response, 'content') else str(response)
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of agent's memory for coordination"""
        try:
            # Get recent sessions from storage
            recent_sessions = self.storage.get_sessions(limit=5)
            return {
                "agent_id": self.agent_id,
                "total_sessions": len(recent_sessions) if recent_sessions else 0,
                "last_activity": recent_sessions[0].created_at if recent_sessions else None,
                "memory_active": True
            }
        except Exception as e:
            return {
                "agent_id": self.agent_id,
                "memory_active": False,
                "error": str(e)
            }