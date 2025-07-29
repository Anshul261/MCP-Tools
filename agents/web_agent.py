"""
Web Research Agent - MCP Web Search Specialist
Specializes in online research using the existing Brave Search MCP server
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

from agno.tools.mcp import MCPTools
from agno.agent import Agent

from .base_agent import BaseAgent


class WebAgent(BaseAgent):
    """Agent specialized in web research using existing MCP server"""
    
    def __init__(self, **kwargs):
        """Initialize Web Research Agent with existing MCP server"""
        
        # Store server path for later async setup
        self.server_dir = str(Path(__file__).parent.parent / "Web-Search")
        self.server_path = str(Path(self.server_dir) / "server.py")
        self.mcp_tools = None  # Will be initialized asynchronously
        self.web_agent_with_mcp = None  # MCP-enabled agent created once
        
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
            tools=None,  # No tools during init - will be handled async
            storage_table="web_agent_sessions",
            **kwargs
        )
    
    def get_mcp_command(self) -> str:
        """Get MCP command for server startup"""
        if not os.path.exists(self.server_path):
            raise FileNotFoundError(f"MCP server not found at {self.server_path}")
        
        return f"python {os.path.abspath(self.server_path)}"
    
    async def setup_mcp_agent(self):
        """Setup MCP tools and create agent following working pattern"""
        try:
            # Initialize MCP tools like working example
            mcp_command = self.get_mcp_command()
            self.mcp_tools = MCPTools(command=mcp_command)
            print(f"🔧 Web Agent MCP tools initialized: {mcp_command}")
            return True
        except Exception as e:
            print(f"❌ Failed to setup MCP tools: {e}")
            return False
    
    async def create_mcp_agent(self):
        """Create agent with MCP tools inside context manager - called once"""
        if not self.mcp_tools:
            return False
        
        try:
            # Create agent with MCP tools like working example
            self.web_agent_with_mcp = Agent(
                name="Web Research Specialist",
                model=self.agent.model,
                tools=[self.mcp_tools],
                instructions=self.agent.instructions,
                storage=self.agent.storage,
                add_history_to_messages=True,
                markdown=True,
                show_tool_calls=True,
            )
            print("✅ Web Agent with MCP tools created")
            return True
        except Exception as e:
            print(f"❌ Failed to create MCP agent: {e}")
            return False
    
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
        Uses the exact working pattern from Web-Search/agent.py
        
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
        
        try:
            # Change to server directory like the working example does
            original_cwd = os.getcwd()
            os.chdir(self.server_dir)
            
            try:
                # Use exact pattern from working example - no timeout parameter
                mcp_command = f"python {os.path.abspath('server.py')}"
                mcp_tools = MCPTools(command=mcp_command)
                
                async with mcp_tools as active_tools:
                    # Create agent with MCP tools inside context
                    web_agent = Agent(
                        name="Web Research Specialist",
                        model=self.agent.model,
                        tools=[active_tools],
                        instructions=self.agent.instructions,
                        storage=self.agent.storage,
                        add_history_to_messages=True,
                        markdown=True,
                        show_tool_calls=False,  # Reduce noise for debugging
                    )
                    
                    # Get response like working example
                    response = await web_agent.arun(enhanced_query)
                    return response.content if hasattr(response, 'content') else str(response)
            
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
                
        except Exception as e:
            print(f"⚠️  Web search error: {e}")
            print(f"🔧 Query was: {enhanced_query[:100]}...")
            import traceback
            traceback.print_exc()
            # Fallback to base processing
            return f"Web search unavailable due to MCP connection issue. Please try again or rephrase your query."
    
    def get_mcp_tools_status(self) -> Dict[str, Any]:
        """Check MCP tools availability"""
        server_available = os.path.exists(self.server_path)
        return {
            "mcp_connected": server_available,  # Server file exists
            "available_tools": [
                "web_search",
                "news_search", 
                "smart_search",
                "research_search"
            ] if server_available else [],
            "server_path": self.server_path,
            "server_exists": server_available
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