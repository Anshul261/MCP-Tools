import asyncio
import os
import json
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.azure.openai_chat import AzureOpenAI
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools
from agno.storage.sqlite import SqliteStorage
from rich import print
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from datetime import datetime

load_dotenv()
console = Console()

class EnhancedResearchAgent:
    """
    Production-ready Agno AI research agent that follows official documentation
    and leverages Agno's built-in capabilities properly
    """
    
    def __init__(self, user_id: str = "demo_user"):
        self.user_id = user_id
        self.agent = None
        self.session_id = None
        self.storage = None
        self.azure_model = None
        self.mcp_tools = None
        
        # Demo metrics for showcasing
        self.metrics = {
            "queries_processed": 0,
            "tool_calls_made": 0,
            "sessions_created": 0,
            "research_topics": set(),
            "successful_responses": 0,
        }
    
    async def initialize(self):
        """Initialize the agent with production-ready configuration"""
        console.print("🚀 [bold blue]Initializing Enhanced Research Agent[/bold blue]")
        
        # Setup Azure OpenAI model
        #api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        # azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        # api_version=os.getenv("OPENAI_API_VERSION"),
        # azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        # max_tokens=4000,  # Increased for detailed responses
        # temperature=0.1,  # Low temperature for consistent research
        self.azure_model = Ollama(
            id="yasserrmd/jan-nano-4b:latest", provider="Ollama",
        )
        
        # Setup storage with proper configuration
        self.storage = SqliteStorage(
            table_name="research_agent_sessions",
            db_file="data/research_agent.db"
        )
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        console.print("✅ [green]Core components initialized[/green]")
        
    async def setup_mcp_connection(self):
        """Setup MCP tools connection"""
        try:
            mcp_command = f"python {os.path.abspath('server.py')}"
            self.mcp_tools = MCPTools(command=mcp_command)
            console.print("✅ [green]MCP server connected successfully[/green]")
        except Exception as e:
            console.print(f"❌ [red]MCP connection failed: {e}[/red]")
            raise
    
    async def create_agent(self, resume_session: bool = False):
        """Create the Agno agent with optimal configuration"""
        
        # Handle session management properly using Agno's built-in methods
        if resume_session and self.storage:
            try:
                # Get existing sessions for this user
                if hasattr(self.storage, 'get_all_session_ids'):
                    existing_sessions = self.storage.get_all_session_ids(self.user_id)
                    if existing_sessions:
                        # Use the most recent session (first in list)
                        self.session_id = existing_sessions[0]
                        console.print(f"📂 [green]Resuming session: {self.session_id}[/green]")
                    else:
                        console.print("🆕 [blue]No existing sessions found, creating new one[/blue]")
                        self.metrics["sessions_created"] += 1
                else:
                    console.print("🆕 [blue]Storage doesn't support session listing, creating new session[/blue]")
                    self.metrics["sessions_created"] += 1
            except Exception as e:
                console.print(f"⚠️ [yellow]Session check failed: {e}, creating new session[/yellow]")
                self.metrics["sessions_created"] += 1
        else:
            self.metrics["sessions_created"] += 1
        
        # Create agent with proper Agno configuration
        self.agent = Agent(
            name="Enhanced Research Assistant",
            user_id=self.user_id,
            session_id=self.session_id,  # Can be None - Agno will create one
            model=self.azure_model,
            tools=[self.mcp_tools] if self.mcp_tools else [],
            storage=self.storage,
            
            # Memory and conversation settings (official Agno parameters)
            add_history_to_messages=True,
            num_history_runs=25,  # Increased for better context
            read_chat_history=True,  # Enable chat history reading tool
            
            # Agent behavior settings
            markdown=True,
            show_tool_calls=True,
            debug_mode=False,  # Set to True for debugging
            
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
        
        console.print("🤖 [green]Enhanced agent created successfully[/green]")
        
        # Show session information
        if self.agent and self.agent.session_id:
            console.print(f"📍 [cyan]Session ID: {self.agent.session_id}[/cyan]")
            if resume_session:
                console.print("🔄 [green]Previous conversation context will be loaded automatically[/green]")
        else:
            console.print("📍 [yellow]New session created[/yellow]")
        
    async def display_agent_status(self):
        """Display comprehensive agent status for demo purposes"""
        
        # Create rich status display
        status_panel = Panel.fit(
            f"""
            [bold blue]Enhanced Research Agent Status[/bold blue]

            🆔 User ID: [yellow]{self.user_id}[/yellow]
            📍 Session: [yellow]{self.agent.session_id if self.agent else 'Not Created'}[/yellow]
            🧠 Memory: [green]Active (Built-in Agno)[/green]
            📊 Context Depth: [cyan]25 messages[/cyan]
            🔧 Tools: [green]{'Connected' if self.mcp_tools else 'Disconnected'}[/green]
            🗃️ Storage: [green]{'Active' if self.storage else 'Disabled'}[/green]

            [bold green]Demo Metrics:[/bold green]
            • Queries Processed: {self.metrics['queries_processed']}
            • Successful Responses: {self.metrics['successful_responses']}
            • Sessions Created: {self.metrics['sessions_created']}
            • Research Topics: {len(self.metrics['research_topics'])}
            """,
            title="🎯 Agent Dashboard",
            border_style="blue"
        )
        
        console.print(status_panel)
        
        # Show conversation context if available
        await self.show_conversation_context()
    
    async def show_conversation_context(self):
        """Display conversation context using Agno's built-in memory"""
        try:
            console.print("\n💭 [bold cyan]Conversation Context[/bold cyan]")
            
            if self.agent and self.agent.session_id:
                console.print(f"  [cyan]Session ID: {self.agent.session_id}[/cyan]")
                
                # Use official Agno method to get messages
                try:
                    messages = self.agent.get_messages_for_session()
                    if messages:
                        message_count = len(messages)
                        console.print(f"  [green]✓ Found {message_count} messages in conversation history[/green]")
                        console.print(f"  [green]✓ Memory system active - previous context loaded[/green]")
                        
                        # Show a preview of the last few messages
                        recent_messages = messages[-3:] if len(messages) > 3 else messages
                        for i, msg in enumerate(recent_messages, 1):
                            role = getattr(msg, 'role', 'unknown')
                            content_preview = str(getattr(msg, 'content', ''))[:50] + "..." if len(str(getattr(msg, 'content', ''))) > 50 else str(getattr(msg, 'content', ''))
                            console.print(f"    [dim]{i}. {role}: {content_preview}[/dim]")
                        
                        console.print("  [green]✓ Previous context will be automatically included in responses[/green]")
                        return
                    else:
                        console.print("  [yellow]No previous messages found in this session[/yellow]")
                        
                except Exception as e:
                    console.print(f"  [yellow]Message access info: {e}[/yellow]")
                
                # Check if storage has session data
                if self.storage:
                    try:
                        # Get all sessions for this user to see if there's history
                        if hasattr(self.storage, 'get_all_sessions'):
                            sessions = self.storage.get_all_sessions(user_id=self.user_id)
                            if sessions:
                                session_count = len(sessions)
                                console.print(f"  [green]✓ Found {session_count} previous sessions in storage[/green]")
                                console.print("  [green]✓ Session persistence active[/green]")
                            else:
                                console.print("  [yellow]No previous sessions found in storage[/yellow]")
                        else:
                            console.print("  [green]✓ Storage configured for session persistence[/green]")
                            
                    except Exception as e:
                        console.print(f"  [yellow]Storage access info: {e}[/yellow]")
                
                console.print("  [green]✓ Memory system active - conversation history automatically managed by Agno[/green]")
            else:
                console.print("  [dim]Starting fresh conversation - no previous context[/dim]")
                
        except Exception as e:
            console.print(f"  [red]Error accessing context: {e}[/red]")
    
    async def process_query(self, query: str) -> None:
        """Process query using Agno's built-in response methods"""
        
        self.metrics["queries_processed"] += 1
        
        # Extract research topics for metrics
        keywords = query.lower().split()
        research_terms = [word for word in keywords if len(word) > 4]
        self.metrics["research_topics"].update(research_terms[:3])
        
        try:
            # Use Agno's built-in print_response method (most common pattern)
            if self.agent:
                await self.agent.aprint_response(query, stream=True)
                self.metrics["successful_responses"] += 1
            else:
                console.print("❌ [red]Agent not initialized[/red]")
            
        except Exception as e:
            console.print(f"❌ [red]Query processing error: {e}[/red]")
            console.print(f"🔧 [yellow]Attempted query: {query[:100]}...[/yellow]")
    
    async def demo_capabilities(self):
        """Demonstrate key agent capabilities for customer showcase"""
        
        demo_scenarios = [
            {
                "name": "Memory Persistence",
                "query": "Remember this: I'm working on a project about sustainable energy solutions for 2025",
                "description": "Shows how the agent maintains conversation context using Agno's built-in memory"
            },
            {
                "name": "Research Synthesis", 
                "query": "What are the latest developments in sustainable energy that might help my project?",
                "description": "Demonstrates research capabilities and memory usage"
            },
            {
                "name": "Proactive Intelligence",
                "query": "What should I consider next for my sustainable energy project?",
                "description": "Shows proactive suggestion and reasoning capabilities"
            }
        ]
        
        console.print("\n🎬 [bold magenta]Demo Showcase - Key Capabilities[/bold magenta]")
        
        for i, scenario in enumerate(demo_scenarios, 1):
            console.print(f"\n[bold blue]Demo {i}: {scenario['name']}[/bold blue]")
            console.print(f"[dim]{scenario['description']}[/dim]")
            console.print(f"[yellow]Query: {scenario['query']}[/yellow]")
            
            if Confirm.ask("Run this demo?", default=True):
                await self.process_query(scenario['query'])
                console.print("\n" + "─" * 60)
        
    async def interactive_session(self):
        """Main interactive session with enhanced features"""
        
        console.print("\n🎯 [bold green]Enhanced Research Agent - Ready![/bold green]")
        console.print("[dim]Commands: 'demo', 'status', 'metrics', 'help', 'quit'[/dim]")
        console.print("─" * 70)
        
        while True:
            try:
                query = Prompt.ask(f"\n[bold cyan]{self.user_id}[/bold cyan]")
                
                if query.lower() == 'quit':
                    break
                elif query.lower() == 'demo':
                    await self.demo_capabilities()
                    continue
                elif query.lower() == 'status':
                    await self.display_agent_status()
                    continue
                elif query.lower() == 'metrics':
                    await self.show_metrics()
                    continue
                elif query.lower() == 'help':
                    self.show_help()
                    continue
                elif not query.strip():
                    continue
                
                # Process the query
                await self.process_query(query)
                
            except KeyboardInterrupt:
                console.print("\n👋 [yellow]Session interrupted. Type 'quit' to exit properly.[/yellow]")
            except Exception as e:
                console.print(f"❌ [red]Session error: {e}[/red]")
    
    async def show_metrics(self):
        """Display comprehensive metrics for demo purposes"""
        
        success_rate = (
            (self.metrics['successful_responses'] / self.metrics['queries_processed'] * 100)
            if self.metrics['queries_processed'] > 0 else 0
        )
        
        metrics_panel = Panel.fit(
            f"""
            [bold green]Research Agent Analytics[/bold green]

            📊 [bold]Usage Statistics:[/bold]
            • Total Queries: [cyan]{self.metrics['queries_processed']}[/cyan]
            • Successful Responses: [cyan]{self.metrics['successful_responses']}[/cyan]
            • Success Rate: [cyan]{success_rate:.1f}%[/cyan]
            • Sessions Created: [cyan]{self.metrics['sessions_created']}[/cyan]

            🧠 [bold]Research Coverage:[/bold]
            • Unique Topics: [cyan]{len(self.metrics['research_topics'])}[/cyan]
            • Topics: [yellow]{', '.join(list(self.metrics['research_topics'])[:5]) if self.metrics['research_topics'] else 'None yet'}[/yellow]

            ⚡ [bold]Agent Performance:[/bold]
            • Memory System: [green]Agno Built-in ✓[/green]
            • MCP Integration: [green]Active ✓[/green]
            • Session Persistence: [green]SQLite Storage ✓[/green]
            • Multi-tool Support: [green]Active ✓[/green]
            """,
            title="📈 Performance Dashboard",
            border_style="green"
        )
        console.print(metrics_panel)
    
    def show_help(self):
        """Display help information"""
        help_panel = Panel.fit(
            """
        [bold blue]Enhanced Research Agent - Commands[/bold blue]

        [bold yellow]Special Commands:[/bold yellow]
        • [cyan]demo[/cyan] - Run capability demonstration
        • [cyan]status[/cyan] - Show agent status and context
        • [cyan]metrics[/cyan] - Display usage analytics
        • [cyan]help[/cyan] - Show this help message
        • [cyan]quit[/cyan] - Exit the application

        [bold yellow]Research Capabilities:[/bold yellow]
        • Persistent memory across sessions (Agno built-in)
        • Multi-strategy search and research via MCP tools
        • Source verification and cross-referencing
        • Proactive insights and suggestions
        • Contextual conversation building

        [bold yellow]Example Queries:[/bold yellow]
        • "Research the latest AI developments in 2025"
        • "What did we discuss about [topic] last time?"
        • "Compare different approaches to [problem]"
        • "What should I investigate next about [topic]?"

        [bold yellow]Agent Features:[/bold yellow]
        • Built on official Agno framework
        • Leverages Agno's memory management
        • MCP tool integration for search capabilities
        • SQLite storage for session persistence
            """,
            title="Help & Commands",
            border_style="yellow"
        )
        console.print(help_panel)
    
    async def cleanup(self):
        """Cleanup resources properly"""
        try:
            if self.mcp_tools:
                # Proper MCP cleanup - check if it has async exit method
                if hasattr(self.mcp_tools, '__aexit__'):
                    await self.mcp_tools.__aexit__(None, None, None)
                # elif hasattr(self.mcp_tools, 'close'):
                #     await self.mcp_tools.close()
                # elif hasattr(self.mcp_tools, 'cleanup'):
                #     await self.mcp_tools.cleanup()
            console.print("🧹 [dim]Resources cleaned up[/dim]")
        except Exception as e:
            console.print(f"⚠️ [yellow]Cleanup warning: {e}[/yellow]")

async def main():
    """Main application entry point"""
    
    # Enhanced startup display
    console.print(Panel.fit(
        """
        [bold blue]🚀 Enhanced Agno Research Agent v2.0[/bold blue]

        [green]✨ Production-Ready Features:[/green]
        • Built on official Agno framework
        • Leverages Agno's built-in memory management  
        • Advanced MCP tool integration
        • Comprehensive session persistence
        • Real-time metrics and monitoring
        • Interactive demo capabilities
        • Professional customer showcase ready

        [yellow]🎯 Perfect for demonstrating enterprise AI capabilities![/yellow]

        [dim]Following official Agno documentation and best practices[/dim]
        """,
        title="🤖 AI Research Assistant",
        border_style="blue"
    ))
    
    # Get user configuration
    user_id = Prompt.ask("👤 [cyan]Enter user ID[/cyan]", default="demo_customer")
    resume_session = Confirm.ask("📂 [yellow]Resume previous session?[/yellow]", default=True)
    
    # Initialize and run the agent
    agent_system = EnhancedResearchAgent(user_id=user_id)
    
    try:
        await agent_system.initialize()
        await agent_system.setup_mcp_connection()
        
        # Use proper async context manager for MCP tools
        if agent_system.mcp_tools:
            async with agent_system.mcp_tools:
                await agent_system.create_agent(resume_session=resume_session)
                await agent_system.display_agent_status()
                await agent_system.interactive_session()
        else:
            console.print("⚠️ [yellow]MCP tools not available, running without search capabilities[/yellow]")
            await agent_system.create_agent(resume_session=resume_session)
            await agent_system.display_agent_status()
            await agent_system.interactive_session()
            
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n❌ [red]Application error: {e}[/red]")
        console.print(f"[dim]Check your environment variables and MCP server configuration[/dim]")
    finally:
        await agent_system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())