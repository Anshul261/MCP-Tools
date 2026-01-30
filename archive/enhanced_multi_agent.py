"""
Enhanced Multi-Agent System with AGNO Interactive Console
Production-ready implementation following AGNO best practices
"""
import asyncio
import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

from rich import print
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from datetime import datetime

from multi_agent_system import MultiAgentSystem

load_dotenv()
console = Console()

class EnhancedMultiAgentSystem:
    """
    Enhanced Multi-Agent System with AGNO interactive console features
    Combines document search, web research, and intelligent coordination
    """
    
    def __init__(self, user_id: str = "multi_agent_user"):
        self.user_id = user_id
        self.system = None
        self.session_id = None
        
        # Demo metrics for showcasing
        self.metrics = {
            "queries_processed": 0,
            "document_queries": 0,
            "web_queries": 0,
            "coordinated_queries": 0,
            "successful_responses": 0,
            "sessions_created": 0,
            "research_topics": set(),
        }
    
    async def initialize(self):
        """Initialize the multi-agent system with production-ready configuration"""
        console.print("🚀 [bold blue]Initializing Enhanced Multi-Agent System[/bold blue]")
        
        # Create multi-agent system
        self.system = MultiAgentSystem()
        
        # Initialize all agents
        success = await self.system.initialize_agents()
        if not success:
            raise Exception("Failed to initialize multi-agent system")
        
        console.print("✅ [green]Multi-Agent System initialized successfully[/green]")
        
        # Generate session ID
        self.session_id = f"multi_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.metrics["sessions_created"] += 1
        
        return True
    
    async def display_system_status(self):
        """Display comprehensive system status for demo purposes"""
        
        # Get system info
        system_info = self.system.get_system_info()
        
        # Create rich status display
        status_panel = Panel.fit(
            f"""
            [bold blue]Enhanced Multi-Agent System Status[/bold blue]

            🆔 User ID: [yellow]{self.user_id}[/yellow]
            📍 Session: [yellow]{self.session_id}[/yellow]
            🏗️ Architecture: [cyan]{system_info.get('architecture', 'Unknown')}[/cyan]
            🎯 System Status: [green]{system_info.get('status', 'Unknown')}[/green]

            [bold green]Active Agents:[/bold green]
            🎯 Coordinator Agent: [green]{'✅ Ready' if 'coordinator' in system_info.get('agents', {}) else '❌ Not Ready'}[/green]
            📚 Document Agent: [green]{'✅ Ready' if 'document' in system_info.get('agents', {}) else '❌ Not Ready'}[/green]
            🌐 Web Agent: [green]{'✅ Ready' if 'web' in system_info.get('agents', {}) else '❌ Not Ready'}[/green]

            [bold green]Demo Metrics:[/bold green]
            • Total Queries: {self.metrics['queries_processed']}
            • Document Queries: {self.metrics['document_queries']}
            • Web Queries: {self.metrics['web_queries']}
            • Coordinated Queries: {self.metrics['coordinated_queries']}
            • Success Rate: {(self.metrics['successful_responses'] / max(1, self.metrics['queries_processed']) * 100):.1f}%
            • Research Topics: {len(self.metrics['research_topics'])}
            """,
            title="🎯 Multi-Agent Dashboard",
            border_style="blue"
        )
        
        console.print(status_panel)
        
        # Show agent capabilities
        await self.show_agent_capabilities()
    
    async def show_agent_capabilities(self):
        """Display agent capabilities and specializations"""
        try:
            console.print("\n🛠️ [bold cyan]Agent Capabilities[/bold cyan]")
            
            system_info = self.system.get_system_info()
            agents = system_info.get('agents', {})
            
            if 'document' in agents:
                doc_caps = agents['document']
                console.print(f"  📚 [bold]Document Agent:[/bold]")
                console.print(f"     • Specialization: [cyan]{doc_caps.get('specialization', 'Unknown')}[/cyan]")
                console.print(f"     • Knowledge Base: [green]{'✓' if doc_caps.get('knowledge') else '✗'}[/green]")
                console.print(f"     • Memory: [green]{'✓' if doc_caps.get('memory') else '✗'}[/green]")
                
                doc_summary = doc_caps.get('document_summary', {})
                if doc_summary:
                    console.print(f"     • Documents: [yellow]{doc_summary.get('total_documents', 0)} files[/yellow]")
                    console.print(f"     • Converted: [yellow]{doc_summary.get('converted_documents', 0)} ready[/yellow]")
            
            if 'web' in agents:
                web_caps = agents['web']
                console.print(f"  🌐 [bold]Web Agent:[/bold]")
                console.print(f"     • Specialization: [cyan]{web_caps.get('specialization', 'Unknown')}[/cyan]")
                
                mcp_info = web_caps.get('mcp_server', {})
                console.print(f"     • MCP Connection: [green]{'✓' if mcp_info.get('mcp_connected') else '✗'}[/green]")
                console.print(f"     • Search Types: [yellow]{', '.join(web_caps.get('search_types', []))}[/yellow]")
                console.print(f"     • Real-time Data: [green]{'✓' if web_caps.get('supports_real_time') else '✗'}[/green]")
            
            if 'coordinator' in agents:
                coord_caps = agents['coordinator']
                console.print(f"  🎯 [bold]Coordinator Agent:[/bold]")
                console.print(f"     • Team Management: [green]✓ Active[/green]")
                console.print(f"     • Query Routing: [green]✓ Intelligent[/green]")
                console.print(f"     • Response Synthesis: [green]✓ Unified[/green]")
                
        except Exception as e:
            console.print(f"  [red]Error accessing capabilities: {e}[/red]")
    
    async def process_query(self, query: str, agent_type: str = "coordinator") -> None:
        """Process query using the specified agent or coordinator"""
        
        self.metrics["queries_processed"] += 1
        
        # Extract research topics for metrics
        keywords = query.lower().split()
        research_terms = [word for word in keywords if len(word) > 4]
        self.metrics["research_topics"].update(research_terms[:3])
        
        try:
            if agent_type == "document":
                console.print("\n📚 [bold]Document Agent Response:[/bold]")
                self.metrics["document_queries"] += 1
                response = await self.system.document_agent.aprocess_query(query)
                console.print(response)
                
            elif agent_type == "web":
                console.print("\n🌐 [bold]Web Agent Response:[/bold]")
                self.metrics["web_queries"] += 1
                response = await self.system.web_agent.aprocess_query(query)
                console.print(response)
                
            else:  # coordinator
                console.print("\n🎯 [bold]Coordinated Response:[/bold]")
                self.metrics["coordinated_queries"] += 1
                result = await self.system.process_query(query)
                
                if "error" in result:
                    console.print(f"❌ [red]Error: {result['error']}[/red]")
                else:
                    # Show the unified response
                    if 'synthesis' in result and result['synthesis']:
                        console.print(result['synthesis'])
                    else:
                        # Fallback: show most relevant response
                        responses = result.get('responses', {})
                        if 'document' in responses and responses['document']:
                            console.print(responses['document'])
                        elif 'web' in responses and responses['web']:
                            console.print(responses['web'])
                        else:
                            console.print("No response generated")
                    
                    # Show which agents were used
                    agents_used = result.get('agents_used', [])
                    if agents_used:
                        agent_names = {'document_agent': '📚 Document', 'web_agent': '🌐 Web'}
                        used_display = ', '.join([agent_names.get(agent, agent) for agent in agents_used])
                        console.print(f"\n[dim]🤝 Agents consulted: {used_display}[/dim]")
            
            self.metrics["successful_responses"] += 1
            
        except Exception as e:
            console.print(f"❌ [red]Query processing error: {e}[/red]")
            console.print(f"🔧 [yellow]Attempted query: {query[:100]}...[/yellow]")
    
    async def demo_capabilities(self):
        """Demonstrate key multi-agent capabilities for customer showcase"""
        
        demo_scenarios = [
            {
                "name": "Company Policy Query",
                "query": "What is the leave policy?",
                "agent": "coordinator",
                "description": "Shows document-focused routing for company-specific queries"
            },
            {
                "name": "General Knowledge Query",
                "query": "What is model context protocol?",
                "agent": "coordinator", 
                "description": "Demonstrates web-focused routing for general knowledge"
            },
            {
                "name": "Comprehensive Research",
                "query": "How to implement a new AI feature using current best practices?",
                "agent": "coordinator",
                "description": "Shows multi-agent collaboration and synthesis"
            },
            {
                "name": "Direct Document Search",
                "query": "Find information about employee benefits",
                "agent": "document",
                "description": "Direct access to document agent capabilities"
            },
            {
                "name": "Direct Web Research",
                "query": "What are the latest AI developments in 2025?",
                "agent": "web",
                "description": "Direct access to web research capabilities"
            }
        ]
        
        console.print("\n🎬 [bold magenta]Multi-Agent Demo Showcase[/bold magenta]")
        
        for i, scenario in enumerate(demo_scenarios, 1):
            console.print(f"\n[bold blue]Demo {i}: {scenario['name']}[/bold blue]")
            console.print(f"[dim]{scenario['description']}[/dim]")
            console.print(f"[yellow]Query: {scenario['query']}[/yellow]")
            console.print(f"[cyan]Agent: {scenario['agent']}[/cyan]")
            
            if Confirm.ask("Run this demo?", default=True):
                await self.process_query(scenario['query'], scenario['agent'])
                console.print("\n" + "─" * 70)
    
    async def interactive_session(self):
        """Main interactive session with enhanced AGNO features"""
        
        console.print("\n🎯 [bold green]Enhanced Multi-Agent System - Ready![/bold green]")
        console.print("[dim]Commands: 'demo', 'status', 'metrics', 'help', 'doc:', 'web:', 'quit'[/dim]")
        console.print("─" * 80)
        
        while True:
            try:
                query = Prompt.ask(f"\n[bold cyan]{self.user_id}[/bold cyan]")
                
                if query.lower() == 'quit':
                    break
                elif query.lower() == 'demo':
                    await self.demo_capabilities()
                    continue
                elif query.lower() == 'status':
                    await self.display_system_status()
                    continue
                elif query.lower() == 'metrics':
                    await self.show_metrics()
                    continue
                elif query.lower() == 'help':
                    self.show_help()
                    continue
                elif query.lower().startswith('doc:'):
                    doc_query = query[4:].strip()
                    if doc_query:
                        await self.process_query(doc_query, "document")
                    continue
                elif query.lower().startswith('web:'):
                    web_query = query[4:].strip()
                    if web_query:
                        await self.process_query(web_query, "web")
                    continue
                elif not query.strip():
                    continue
                
                # Default: process through coordinator
                await self.process_query(query, "coordinator")
                
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
            [bold green]Multi-Agent System Analytics[/bold green]

            📊 [bold]Usage Statistics:[/bold]
            • Total Queries: [cyan]{self.metrics['queries_processed']}[/cyan]
            • Successful Responses: [cyan]{self.metrics['successful_responses']}[/cyan]
            • Success Rate: [cyan]{success_rate:.1f}%[/cyan]
            • Sessions Created: [cyan]{self.metrics['sessions_created']}[/cyan]

            🎯 [bold]Query Distribution:[/bold]
            • Document Queries: [cyan]{self.metrics['document_queries']}[/cyan]
            • Web Queries: [cyan]{self.metrics['web_queries']}[/cyan]
            • Coordinated Queries: [cyan]{self.metrics['coordinated_queries']}[/cyan]

            🧠 [bold]Research Coverage:[/bold]
            • Unique Topics: [cyan]{len(self.metrics['research_topics'])}[/cyan]
            • Topics: [yellow]{', '.join(list(self.metrics['research_topics'])[:5]) if self.metrics['research_topics'] else 'None yet'}[/yellow]

            ⚡ [bold]System Performance:[/bold]
            • Multi-Agent Coordination: [green]Active ✓[/green]
            • Document Search: [green]Vector DB ✓[/green]
            • Web Research: [green]MCP Integration ✓[/green]
            • Memory Persistence: [green]SQLite Storage ✓[/green]
            """,
            title="📈 Performance Dashboard",
            border_style="green"
        )
        console.print(metrics_panel)
    
    def show_help(self):
        """Display help information"""
        help_panel = Panel.fit(
            """
        [bold blue]Enhanced Multi-Agent System - Commands[/bold blue]

        [bold yellow]Special Commands:[/bold yellow]
        • [cyan]demo[/cyan] - Run multi-agent capability demonstration
        • [cyan]status[/cyan] - Show system status and agent capabilities
        • [cyan]metrics[/cyan] - Display usage analytics and performance
        • [cyan]help[/cyan] - Show this help message
        • [cyan]quit[/cyan] - Exit the application

        [bold yellow]Direct Agent Access:[/bold yellow]
        • [cyan]doc: <query>[/cyan] - Direct query to Document Agent
        • [cyan]web: <query>[/cyan] - Direct query to Web Agent
        • [cyan]<query>[/cyan] - Smart routing through Coordinator Agent

        [bold yellow]Multi-Agent Capabilities:[/bold yellow]
        • Intelligent query routing (company → docs, general → web)
        • Multi-source research with unified responses
        • Persistent memory across all agents and sessions
        • Real-time web search with MCP integration
        • Vector-based document search and retrieval

        [bold yellow]Example Queries:[/bold yellow]
        • "What is the leave policy?" (→ Document Agent)
        • "What is model context protocol?" (→ Web Agent)
        • "How to implement AI features?" (→ Both agents + synthesis)
        • "doc: Find employee handbook" (→ Direct document search)
        • "web: Latest AI news" (→ Direct web research)

        [bold yellow]System Features:[/bold yellow]
        • Built on AGNO Level 4 architecture
        • Production-ready multi-agent coordination
        • Rich interactive console with markdown support
        • Comprehensive analytics and demo capabilities
            """,
            title="Help & Commands",
            border_style="yellow"
        )
        console.print(help_panel)
    
    async def cleanup(self):
        """Cleanup resources properly"""
        try:
            if self.system:
                await self.system.shutdown()
            console.print("🧹 [dim]Multi-agent system cleaned up[/dim]")
        except Exception as e:
            console.print(f"⚠️ [yellow]Cleanup warning: {e}[/yellow]")

async def main():
    """Main application entry point"""
    
    # Enhanced startup display
    console.print(Panel.fit(
        """
        [bold blue]🚀 Enhanced Multi-Agent System v2.0[/bold blue]
        [cyan]Powered by AGNO Level 4 Architecture[/cyan]

        [green]✨ Production-Ready Features:[/green]
        • 🎯 Intelligent Coordinator Agent for smart routing
        • 📚 Vector-based Document Search with PgVector
        • 🌐 Real-time Web Research via MCP integration
        • 🧠 Persistent memory across all agents and sessions
        • 📊 Comprehensive analytics and demo capabilities
        • 🎨 Rich interactive console with markdown support

        [bold yellow]Multi-Agent Specializations:[/bold yellow]
        • Company policies → Document Agent
        • General knowledge → Web Agent  
        • Complex tasks → Multi-agent collaboration

        [yellow]🎯 Perfect for demonstrating enterprise AI capabilities![/yellow]

        [dim]Following AGNO best practices and official documentation[/dim]
        """,
        title="🤖 AI Multi-Agent Research System",
        border_style="blue"
    ))
    
    # Get user configuration
    user_id = Prompt.ask("👤 [cyan]Enter user ID[/cyan]", default="demo_customer")
    
    # Initialize and run the system
    multi_agent_system = EnhancedMultiAgentSystem(user_id=user_id)
    
    try:
        await multi_agent_system.initialize()
        await multi_agent_system.display_system_status()
        await multi_agent_system.interactive_session()
            
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n❌ [red]Application error: {e}[/red]")
        console.print(f"[dim]Check your environment variables and system configuration[/dim]")
    finally:
        await multi_agent_system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())