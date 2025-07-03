import asyncio
import os
import json
import sqlite3
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.azure.openai_chat import AzureOpenAI
from agno.tools.mcp import MCPTools
from agno.storage.sqlite import SqliteStorage
from rich import print
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from datetime import datetime

load_dotenv()
console = Console()

class MemoryParser:
    """Manual memory parser that works with Agno's actual storage format"""
    
    def __init__(self, db_file: str, table_name: str):
        self.db_file = db_file
        self.table_name = table_name
    
    def get_user_memory(self, user_id: str, session_id: Optional[str]) -> Dict[str, Any]:
        """Get user's memory data directly from database"""
        
        if not session_id:
            return {}
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute(
                f"SELECT memory, session_data FROM {self.table_name} WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                memory_data = json.loads(result[0]) if result[0] else {}
                session_data = json.loads(result[1]) if result[1] else {}
                
                return {
                    "memory": memory_data,
                    "session_data": session_data
                }
            
            return {}
            
        except Exception as e:
            print(f"❌ Error getting memory: {e}")
            return {}
    
    def extract_messages_from_runs(self, memory_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract all messages from the runs array"""
        
        all_messages = []
        
        try:
            runs = memory_data.get("runs", [])
            
            for run_idx, run in enumerate(runs):
                if isinstance(run, dict) and "messages" in run:
                    messages = run["messages"]
                    
                    for msg in messages:
                        if isinstance(msg, dict):
                            # Add run context to message
                            message_copy = msg.copy()
                            message_copy["run_id"] = run_idx + 1
                            all_messages.append(message_copy)
            
            return all_messages
            
        except Exception as e:
            print(f"❌ Error extracting messages: {e}")
            return []
    
    def get_conversation_history(self, user_id: str, session_id: Optional[str]) -> List[Dict[str, str]]:
        """Get complete conversation history for user"""
        
        if not session_id:
            return []
        
        user_memory = self.get_user_memory(user_id, session_id)
        
        if not user_memory:
            return []
        
        memory_data = user_memory.get("memory", {})
        return self.extract_messages_from_runs(memory_data)
    
    def get_conversation_summary(self, user_id: str, session_id: Optional[str]) -> Dict[str, Any]:
        """Get conversation summary and statistics"""
        
        if not session_id:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "topics": []
            }
        
        messages = self.get_conversation_history(user_id, session_id)
        
        if not messages:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "topics": []
            }
        
        # Count by role
        role_counts = {}
        topics = set()
        
        for msg in messages:
            role = msg.get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
            
            # Extract topics from user messages
            if role == "user":
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in ["mcp", "model context protocol", "anthropic"]):
                    topics.add("Model Context Protocol")
                if any(keyword in content for keyword in ["search", "brave", "web"]):
                    topics.add("Search & Research")
        
        return {
            "total_messages": len(messages),
            "user_messages": role_counts.get("user", 0),
            "assistant_messages": role_counts.get("assistant", 0),
            "system_messages": role_counts.get("system", 0),
            "topics": list(topics),
            "role_breakdown": role_counts
        }

def create_working_agent(user: str = "Anshul"):
    """Create agent with working memory parser"""
    
    session_id: Optional[str] = None
    
    # Azure OpenAI model
    azure_model = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    )
    
    # Correct storage configuration
    agent_storage = SqliteStorage(
        table_name="brave_search_sessions",
        db_file="tmp/brave_search_agents.db"
    )
    
    # Create memory parser
    memory_parser = MemoryParser(
        db_file="tmp/brave_search_agents.db",
        table_name="brave_search_sessions"
    )
    
    print(f"👤 User: {user}")
    print(f"📁 Database: tmp/brave_search_agents.db")
    print(f"📋 Table: brave_search_sessions")
    print(f"🧠 Memory Parser: Active")
    
    # Check for existing sessions
    try:
        existing_sessions = agent_storage.get_all_session_ids(user)
        print(f"🔍 Found {len(existing_sessions)} existing session(s) for {user}")
        
        if existing_sessions:
            for i, session in enumerate(existing_sessions, 1):
                print(f"  {i}. {session}")
            
            new_session = Confirm.ask("🔄 Do you want to start a new session?", default=False)
            
            if not new_session:
                session_id = existing_sessions[0]
                print(f"✅ Will continue session: {session_id}")
                
                # Test memory parser immediately
                print(f"\n🧠 Testing memory parser...")
                summary = memory_parser.get_conversation_summary(user, session_id)
                print(f"  📊 Found {summary['total_messages']} stored messages!")
                print(f"  👤 User messages: {summary['user_messages']}")
                print(f"  🤖 Assistant messages: {summary['assistant_messages']}")
                print(f"  🎯 Topics: {summary['topics']}")
        else:
            print("🆕 No existing sessions found - will create new one")
            
    except Exception as e:
        print(f"⚠️ Error checking sessions: {e}")
        print("🆕 Will create new session")
    
    return azure_model, agent_storage, session_id, user, memory_parser

def show_working_memory(memory_parser: MemoryParser, user_id: str, session_id: Optional[str]):
    """Show memory using our working parser"""
    
    print(f"\n🧠 WORKING MEMORY ANALYSIS")
    print("=" * 60)
    
    if not session_id:
        print("❌ No session ID available")
        return
    
    # Get conversation summary
    summary = memory_parser.get_conversation_summary(user_id, session_id)
    
    if summary["total_messages"] == 0:
        print("📝 No messages found in memory")
        return
    
    print(f"✅ MEMORY WORKING! Found {summary['total_messages']} messages")
    print(f"📊 Breakdown: {summary['role_breakdown']}")
    print(f"🎯 Topics discussed: {', '.join(summary['topics'])}")
    
    # Get and display recent messages
    messages = memory_parser.get_conversation_history(user_id, session_id)
    
    if messages:
        print(f"\n💬 Recent Conversation History:")
        
        # Show last 10 messages
        recent_messages = messages[-10:]
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Role", width=10)
        table.add_column("Content", min_width=50)
        table.add_column("Run", width=6)
        
        for i, msg in enumerate(recent_messages, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            run_id = msg.get("run_id", "?")
            
            # Truncate long content
            if len(content) > 80:
                content = content[:80] + "..."
            
            # Color code by role
            if role == "user":
                role_display = f"[blue]{role}[/blue]"
            elif role == "assistant":
                role_display = f"[green]{role}[/green]"
            else:
                role_display = f"[dim]{role}[/dim]"
            
            table.add_row(str(i), role_display, content, str(run_id))
        
        console.print(table)
        
        # Show MCP-related content
        mcp_messages = [msg for msg in messages if "mcp" in msg.get("content", "").lower() or "model context protocol" in msg.get("content", "").lower()]
        
        if mcp_messages:
            print(f"\n🔍 MCP-Related Messages: {len(mcp_messages)}")
            for i, msg in enumerate(mcp_messages[-3:], 1):
                role_emoji = "👤" if msg.get("role") == "user" else "🤖"
                content = msg.get("content", "")[:100] + "..."
                print(f"  {i}. {role_emoji} {content}")

async def main():
    """Main function with working memory"""
    
    print("🎯 WORKING: Brave Search Agent with Manual Memory Parser")
    print("=" * 70)
    
    user = "Anshul"
    
    # Create agent with working memory parser
    azure_model, agent_storage, session_id, user, memory_parser = create_working_agent(user)
    
    # Setup MCP connection
    mcp_command = f"python {os.path.abspath('server.py')}"
    
    async with MCPTools(command=mcp_command) as mcp_tools:
        
        # Create agent
        agent = Agent(
            user_id=user,
            session_id=session_id,
            model=azure_model,
            tools=[mcp_tools],
            storage=agent_storage,
            
            # Memory configuration
            add_history_to_messages=True,        # This works and includes memory
            num_history_responses=15,            # Include more context
            
            instructions="""
            You are an intelligent research assistant with PERSISTENT MEMORY.
            
            🧠 MEMORY BEHAVIOR:
            - You remember ALL previous conversations across sessions
            - Always acknowledge when you recognize returning users and topics
            - Build upon previous research and discussions
            - Reference past searches and findings when relevant
            
            🔍 WHEN RESPONDING:
            - If you recognize the user, say "Welcome back!"
            - If you remember previous topics, reference them explicitly
            - Build upon past conversations rather than starting fresh
            - Use phrases like "As we discussed before..." or "Building on our previous conversation..."
            
            Available tools:
            - web_search: General web search
            - news_search: Recent news articles  
            - smart_search: Multi-strategy intelligent search
            - research_search: Comprehensive research
            
            Always acknowledge your memory and build on previous conversations!
            """,
            markdown=True,
            show_tool_calls=True
        )
        
        # Show session status
        current_session = agent.session_id
        if session_id is None:
            print(f"✅ Created new session: {current_session}")
        else:
            print(f"✅ Resumed session: {current_session}")
        
        print(f"👤 User: {agent.user_id}")
        print(f"🆔 Session: {current_session}")
        
        # Show working memory
        show_working_memory(memory_parser, user, current_session)
        
        # Interactive session
        print(f"\n💬 Working Memory Chat Session")
        print("Commands: 'memory', 'history', 'summary', 'test', 'quit'")
        print("-" * 60)
        
        while True:
            query = Prompt.ask(f"[bold cyan]{user}[/bold cyan]")
            
            if query.lower() == 'quit':
                break
            
            if query.lower() == 'memory':
                show_working_memory(memory_parser, user, current_session)
                continue
            
            if query.lower() == 'history':
                if not current_session:
                    print("❌ No active session for history")
                    continue
                    
                messages = memory_parser.get_conversation_history(user, current_session)
                print(f"\n📚 Full Conversation History ({len(messages)} messages):")
                
                for i, msg in enumerate(messages, 1):
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    run_id = msg.get("run_id", "?")
                    
                    role_emoji = {"user": "👤", "assistant": "🤖", "system": "⚙️"}.get(role, "❓")
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"  {i:2d}. {role_emoji} [Run {run_id}] {preview}")
                
                continue
            
            if query.lower() == 'summary':
                if not current_session:
                    print("❌ No active session for summary")
                    continue
                    
                summary = memory_parser.get_conversation_summary(user, current_session)
                print(f"\n📊 Conversation Summary:")
                print(f"  💬 Total messages: {summary['total_messages']}")
                print(f"  👤 Your messages: {summary['user_messages']}")
                print(f"  🤖 My responses: {summary['assistant_messages']}")
                print(f"  🎯 Topics discussed: {', '.join(summary['topics'])}")
                continue
            
            if query.lower() == 'test':
                print(f"\n🧪 Testing memory recognition...")
                await agent.aprint_response("What have we discussed in our previous conversations? Please acknowledge our conversation history.", stream=True)
                continue
            
            if not query.strip():
                continue
            
            # Process normal query
            await agent.aprint_response(query, stream=True)

if __name__ == "__main__":
    asyncio.run(main())