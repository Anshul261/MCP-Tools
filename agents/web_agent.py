"""
Web Research Agent - MCP Web Search Specialist
Specializes in online research using the existing Brave Search MCP server
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

from agno.tools.mcp import MCPTools

from .base_agent import BaseAgent


class WebAgent(BaseAgent):
    """Agent specialized in web research using existing MCP server"""
    
    def __init__(self, **kwargs):
        """Initialize Web Research Agent with existing MCP server"""
        
        # Setup MCP tools pointing to existing server
        server_path = str(Path(__file__).parent.parent / "Web-Search" / "server.py")
        self.mcp_tools = self._setup_mcp_tools(server_path)
        
        # Web agent specific instructions
        instructions = [
            "You are a Web Research Specialist using Brave Search API through MCP tools.",
            "You have access to web_search, news_search, smart_search, and research_search tools.",
            "Always prioritize authoritative sources and cross-reference information.",
            "Use smart_search for persistent searching when initial results are insufficient.",
            "Use research_search for comprehensive academic-style investigations.",
            "Use news_search for current events and recent developments.",
            "Provide source URLs and assess information reliability.",
            "When information conflicts, present multiple perspectives clearly.",
        ]
        
        super().__init__(
            name="Web Research Agent",
            agent_id="web_agent",
            instructions=instructions,
            tools=None,  # Don't pass MCP tools to base agent - handle separately
            storage_table="web_agent_sessions",
            **kwargs
        )
    
    def _setup_mcp_tools(self, server_path: str) -> Optional[MCPTools]:
        """Setup connection to existing MCP server"""
        try:
            if not os.path.exists(server_path):
                print(f"⚠️  MCP server not found at {server_path}")
                return None
            
            mcp_tools = MCPTools(command=f"python {os.path.abspath(server_path)}")
            print(f"🔧 Web Agent connected to existing MCP server: {server_path}")
            return mcp_tools
            
        except Exception as e:
            print(f"❌ Failed to connect to MCP server: {e}")
            return None
    
    async def activate_mcp_connection(self):
        """Activate MCP connection"""
        if self.mcp_tools:
            try:
                await self.mcp_tools.__aenter__()
                print("✅ Web Agent MCP connection activated")
                return True
            except Exception as e:
                print(f"❌ Failed to activate MCP connection: {e}")
                return False
        return False
    
    async def deactivate_mcp_connection(self):
        """Deactivate MCP connection"""
        if self.mcp_tools:
            try:
                await self.mcp_tools.__aexit__(None, None, None)
                print("🛑 Web Agent MCP connection deactivated")
            except Exception as e:
                print(f"❌ Failed to deactivate MCP connection: {e}")
    
    async def aprocess_query(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Async query processing for web agent with MCP tools
        
        Args:
            query: The user query to process
            context: Optional context from other agents or coordinator
            
        Returns:
            Agent's response as string
        """
        if not self.mcp_tools:
            # Fallback to synchronous processing if no MCP tools
            return self.process_query(query, context)
        
        # Add context to query if provided
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            enhanced_query = f"Context from other agents:\n{context_str}\n\nUser Query: {query}"
        else:
            enhanced_query = query
        
        try:
            # Use async MCP tools
            async with self.mcp_tools as active_tools:
                # Create temporary agent instance with active MCP tools
                temp_agent = Agent(
                    name=self.agent.name,
                    model=self.agent.model,
                    tools=[active_tools],
                    instructions=self.agent.instructions,
                    storage=self.agent.storage,
                    knowledge=self.agent.knowledge,
                    add_history_to_messages=True,
                    markdown=True,
                    show_tool_calls=True,
                )
                
                # Get response using async method
                response = await temp_agent.arun(enhanced_query)
                return response.content if hasattr(response, 'content') else str(response)
                
        except Exception as e:
            print(f"⚠️  MCP tools error: {e}")
            # Fallback to base processing
            return self.process_query(query, context)
    
    def get_mcp_tools_status(self) -> Dict[str, Any]:
        """Check MCP tools availability"""
        return {
            "mcp_connected": bool(self.mcp_tools),
            "available_tools": [
                "web_search",
                "news_search", 
                "smart_search",
                "research_search"
            ] if self.mcp_tools else [],
            "server_path": str(Path(__file__).parent.parent / "Web-Search" / "server.py")
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Enhanced capabilities for web agent"""
        base_caps = super().get_capabilities()
        mcp_status = self.get_mcp_tools_status()
        
        base_caps.update({
            "specialization": "web_research",
            "mcp_server": mcp_status,
            "supports_real_time": True,
            "search_types": ["web", "news", "smart", "research"],
            "fact_checking": True,
            "academic_search": True
        })
        
        return base_caps