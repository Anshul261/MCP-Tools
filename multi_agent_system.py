"""
Multi-Agent System Implementation
Level 4 AGNO Architecture with Document and Web Search Agents
"""

import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage

from agents import DocumentAgent, WebAgent, CoordinatorAgent

load_dotenv()


class MultiAgentSystem:
    """
    Level 4 AGNO Multi-Agent System
    Implements collaborative agents with reasoning and coordination
    """
    
    def __init__(self, documents_path: str = "documents"):
        """
        Initialize the Multi-Agent System
        
        Args:
            documents_path: Path to documents directory for DocumentAgent
        """
        self.documents_path = documents_path
        self.document_agent = None
        self.web_agent = None
        self.coordinator_agent = None
        self.system_memory = None
        
        # Ensure data directories exist
        os.makedirs("data", exist_ok=True)
        Path(documents_path).mkdir(parents=True, exist_ok=True)
        
        print("🚀 Initializing Multi-Agent System...")
        
        # Validate environment variables
        if not self._validate_environment():
            raise ValueError("Missing required environment variables")
    
    def _validate_environment(self) -> bool:
        """Validate required environment variables"""
        required_vars = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT", 
            "AZURE_OPENAI_DEPLOYMENT_NAME",
            "DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME", "DB_PORT"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            print(f"❌ Missing required environment variables: {missing_vars}")
            print("Please check your .env file and ensure all required variables are set")
            return False
        
        # Validate DB_PORT is numeric
        try:
            port = os.getenv('DB_PORT')
            if port:
                int(port)
        except ValueError:
            print(f"❌ DB_PORT must be a valid integer, got: {port}")
            return False
        
        print("✅ Environment variables validated")
        return True
    
    def _setup_system_memory(self):
        """Setup system-wide memory for agent coordination"""
        self.system_memory = SqliteStorage(
            table_name="multi_agent_system_memory",
            db_file="data/system_memory.db"
        )
        print("💾 System memory initialized")
    
    async def initialize_agents(self):
        """Initialize all agents in the system"""
        try:
            print("\n📋 Setting up agents...")
            
            # Initialize Document Agent
            print("📚 Initializing Document Agent...")
            self.document_agent = DocumentAgent(
                documents_path=self.documents_path,
                description="Specialist in local document analysis and knowledge retrieval"
            )
            print("✅ Document Agent ready")
            
            # Initialize Web Agent
            print("🌐 Initializing Web Agent...")
            self.web_agent = WebAgent(
                description="Specialist in web research and current information gathering"
            )
            print("✅ Web Agent ready (MCP will be initialized per query)")
            
            # Initialize Coordinator Agent
            print("🎯 Initializing Coordinator Agent...")
            self.coordinator_agent = CoordinatorAgent(
                document_agent=self.document_agent,
                web_agent=self.web_agent,
                description="Team coordinator for multi-agent collaboration"
            )
            print("✅ Coordinator Agent ready")
            
            # Setup system memory
            self._setup_system_memory()
            
            print("\n🎉 Multi-Agent System initialization complete!")
            self._print_system_status()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize agents: {e}")
            return False
    
    async def shutdown(self):
        """Gracefully shutdown the multi-agent system"""
        print("\n🛑 Shutting down Multi-Agent System...")
        
        try:
            # Deactivate Web Agent MCP connection
            if self.web_agent:
                await self.web_agent.deactivate_mcp_connection()
            
            print("✅ Multi-Agent System shutdown complete")
            
        except Exception as e:
            print(f"⚠️  Error during shutdown: {e}")
    
    def _print_system_status(self):
        """Print current system status"""
        print("\n" + "="*60)
        print("📊 MULTI-AGENT SYSTEM STATUS")
        print("="*60)
        
        if self.coordinator_agent:
            team_status = self.coordinator_agent.get_team_status()
            
            print(f"🎯 Coordinator: {'✅ Active' if team_status['coordinator_active'] else '❌ Inactive'}")
            print(f"📚 Document Agent: {'✅ Ready' if team_status['document_agent']['available'] else '❌ Unavailable'}")
            print(f"🌐 Web Agent: {'✅ Ready' if team_status['web_agent']['available'] else '❌ Unavailable'}")
            
            if team_status['document_agent']['available']:
                doc_caps = team_status['document_agent']['capabilities']
                doc_summary = doc_caps.get('document_summary', {})
                print(f"   📄 Documents: {doc_summary.get('converted_documents', 0)} available")
            
            if team_status['web_agent']['available']:
                web_caps = team_status['web_agent']['capabilities']
                mcp_status = web_caps.get('mcp_server', {})
                print(f"   🔗 MCP Connection: {'✅' if mcp_status.get('mcp_connected') else '❌'}")
        
        print("="*60)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        info = {
            "system_name": "AI-Search Multi-Agent System",
            "architecture": "AGNO Level 4",
            "agents": {},
            "status": "active" if all([self.document_agent, self.web_agent, self.coordinator_agent]) else "partial"
        }
        
        if self.document_agent:
            info["agents"]["document"] = self.document_agent.get_capabilities()
        
        if self.web_agent:
            info["agents"]["web"] = self.web_agent.get_capabilities()
        
        if self.coordinator_agent:
            info["agents"]["coordinator"] = self.coordinator_agent.get_capabilities()
        
        return info
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a query through the multi-agent system
        
        Args:
            query: User query to process
            
        Returns:
            Coordinated response from the system
        """
        if not self.coordinator_agent:
            return {"error": "Multi-agent system not initialized"}
        
        print(f"\n🔍 Processing query: {query}")
        
        try:
            # Let the coordinator handle the query
            response = await self.coordinator_agent.coordinate_response(query)
            
            print(f"✅ Query processed using: {', '.join(response.get('agents_used', []))}")
            
            return response
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return {"error": str(e), "query": query}
    
    def create_playground(self) -> Playground:
        """
        Create AGNO Playground for the multi-agent system
        
        Returns:
            Configured Playground instance
        """
        if not all([self.document_agent, self.web_agent, self.coordinator_agent]):
            raise RuntimeError("Agents must be initialized before creating playground")
        
        # Create playground with all agents
        agents = [
            self.coordinator_agent.agent,  # Primary interface
            self.document_agent.agent,     # Direct access to document agent
            self.web_agent.agent          # Direct access to web agent
        ]
        
        playground = Playground(
            agents=agents,
            user_id="multi_agent_user",
            session_id="multi_agent_session"
        )
        
        print("🎮 Playground created with multi-agent system")
        return playground


async def create_multi_agent_system(documents_path: str = "documents") -> Optional[MultiAgentSystem]:
    """
    Factory function to create and initialize multi-agent system
    
    Args:
        documents_path: Path to documents directory
        
    Returns:
        Initialized MultiAgentSystem or None if initialization fails
    """
    system = MultiAgentSystem(documents_path)
    
    success = await system.initialize_agents()
    if success:
        return system
    else:
        await system.shutdown()
        return None


async def main():
    """Main function for testing the multi-agent system"""
    print("🧪 Testing Multi-Agent System")
    
    # Check required environment variables
    required_vars = [
        "AZURE_OPENAI_API_KEY_o3",
        "AZURE_OPENAI_ENDPOINT_o3", 
        "OPENAI_API_VERSION",
        "DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        return
    
    # Create and test the system
    system = await create_multi_agent_system()
    
    if system:
        # Test query processing
        test_queries = [
            "What is machine learning?",
            "What are the latest developments in AI?",
            "Tell me about our company policies"
        ]
        
        for query in test_queries:
            response = await system.process_query(query)
            print(f"\n🎯 Query: {query}")
            print(f"📝 Classification: {response.get('classification', {}).get('query_type', 'unknown')}")
            print(f"🔀 Routing: {response.get('classification', {}).get('routing_strategy', 'unknown')}")
            print(f"🤖 Agents: {', '.join(response.get('agents_used', []))}")
        
        # Shutdown
        await system.shutdown()
    else:
        print("❌ Failed to create multi-agent system")


if __name__ == "__main__":
    asyncio.run(main())