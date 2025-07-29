"""
Multi-Agent Playground Application
Integration with AGNO Playground for the Multi-Agent System
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from agno.playground import Playground, serve_playground_app

from multi_agent_system import create_multi_agent_system

load_dotenv()


async def setup_multi_agent_playground():
    """Setup and serve the multi-agent playground"""
    print("🚀 Setting up Multi-Agent Playground...")
    
    # Validate environment
    required_vars = [
        "AZURE_OPENAI_API_KEY_o3",
        "AZURE_OPENAI_ENDPOINT_o3",
        "OPENAI_API_VERSION"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return None
    
    # Create multi-agent system
    system = await create_multi_agent_system()
    if not system:
        print("❌ Failed to initialize multi-agent system")
        return None
    
    # Create playground
    try:
        playground = system.create_playground()
        print("✅ Multi-Agent Playground ready!")
        
        # Print usage information
        print("\n" + "="*60)
        print("🎮 MULTI-AGENT PLAYGROUND")
        print("="*60)
        print("📊 Available Agents:")
        print("   🎯 Coordinator Agent - Main interface for team coordination")
        print("   📚 Document Agent - Direct access to document search")
        print("   🌐 Web Agent - Direct access to web research")
        print("\n💡 Usage Tips:")
        print("   • Start with the Coordinator Agent for intelligent routing")
        print("   • Use Document Agent for specific document queries")
        print("   • Use Web Agent for current information and research")
        print("   • All agents have persistent memory across sessions")
        print("="*60)
        
        return playground, system
        
    except Exception as e:
        print(f"❌ Failed to create playground: {e}")
        await system.shutdown()
        return None


def create_playground_app():
    """Create the playground FastAPI app"""
    async def app_factory():
        result = await setup_multi_agent_playground()
        if result:
            playground, system = result
            
            # Get the FastAPI app
            app = playground.get_app()
            
            # Add startup and shutdown event handlers
            @app.on_event("startup")
            async def startup_event():
                print("🚀 Multi-Agent Playground server starting...")
                # MCP connections are already established during system init
                
            @app.on_event("shutdown")
            async def shutdown_event():
                print("🛑 Multi-Agent Playground server shutting down...")
                await system.shutdown()
            
            # Store system reference for potential use
            app.state.multi_agent_system = system
            
            return app
        else:
            # Create a minimal error app if initialization fails
            from fastapi import FastAPI
            app = FastAPI()
            
            @app.get("/")
            async def root():
                return {"error": "Multi-Agent System initialization failed"}
            
            return app
    
    return app_factory


async def run_interactive_session():
    """Run an interactive command-line session with the multi-agent system"""
    print("\n🎯 Multi-Agent Interactive Session")
    print("Available commands:")
    print("  - Ask any question (routed through Coordinator)")
    print("  - 'doc: <question>' - Direct to Document Agent")
    print("  - 'web: <question>' - Direct to Web Agent")
    print("  - 'status' - Show system status")
    print("  - 'quit', 'exit', 'q' - End session")
    print("-" * 50)
    
    # Initialize system
    system = await create_multi_agent_system()
    if not system:
        print("❌ Failed to initialize system for interactive session")
        return
    
    try:
        while True:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input.lower() == 'status':
                info = system.get_system_info()
                print(f"\n📊 System Status: {info['status']}")
                print(f"🏗️  Architecture: {info['architecture']}")
                print(f"🤖 Active Agents: {len(info['agents'])}")
                for agent_name, agent_info in info['agents'].items():
                    print(f"   • {agent_name}: {agent_info.get('specialization', 'N/A')}")
                continue
            
            # Route commands to specific agents
            if user_input.startswith('doc:'):
                query = user_input[4:].strip()
                if system.document_agent:
                    print("\n📚 Document Agent:")
                    response = system.document_agent.process_query(query)
                    print(response)
                else:
                    print("❌ Document Agent not available")
                continue
            
            if user_input.startswith('web:'):
                query = user_input[4:].strip()
                if system.web_agent:
                    print("\n🌐 Web Agent:")
                    response = system.web_agent.process_query(query)
                    print(response)
                else:
                    print("❌ Web Agent not available")
                continue
            
            # Default: route through coordinator
            print("\n🎯 Coordinator:")
            response = await system.process_query(user_input)
            
            if "error" in response:
                print(f"❌ Error: {response['error']}")
            else:
                print(f"📋 Classification: {response.get('classification', {}).get('query_type', 'unknown')}")
                print(f"🔀 Strategy: {response.get('classification', {}).get('routing_strategy', 'unknown')}")
                print(f"🤖 Agents Used: {', '.join(response.get('agents_used', []))}")
                print(f"\n📝 Response:\n{response.get('synthesis', 'No response generated')}")
    
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted")
    
    finally:
        await system.shutdown()
        print("👋 Goodbye!")


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "interactive":
            # Run interactive session
            asyncio.run(run_interactive_session())
        elif command == "serve":
            # Serve playground
            print("🌐 Starting Multi-Agent Playground Server...")
            app_factory = create_playground_app()
            # Note: This would typically use uvicorn or similar to serve
            print("To serve the playground, use: uvicorn playground_multi_agent:app --reload")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: interactive, serve")
    else:
        # Default: interactive session
        asyncio.run(run_interactive_session())


# For use with uvicorn
async def create_app():
    """Create app for uvicorn"""
    result = await setup_multi_agent_playground()
    if result:
        playground, system = result
        app = playground.get_app()
        app.state.multi_agent_system = system
        return app
    else:
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/")
        async def root():
            return {"error": "Multi-Agent System initialization failed"}
        
        return app


# Create the app instance for uvicorn
app = None

def get_app():
    """Get or create the app instance"""
    global app
    if app is None:
        app = asyncio.run(create_app())
    return app


if __name__ == "__main__":
    main()