#!/usr/bin/env python3
"""
Memory Diagnostic Tool - Check if Agno agent is actually accessing stored conversations
"""

import os
import sqlite3
import json
from agno.storage.sqlite import SqliteStorage
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def analyze_database_content():
    """Analyze what's actually stored in the database"""
    
    db_file = "data/research_agent.db"
    
    if not os.path.exists(db_file):
        console.print("❌ Database file not found")
        return
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get all sessions
        cursor.execute("""
            SELECT session_id, user_id, memory, created_at, updated_at 
            FROM research_agent_sessions 
            ORDER BY updated_at DESC
        """)
        
        sessions = cursor.fetchall()
        
        console.print(f"\n📊 Found {len(sessions)} sessions in database:")
        
        for session_id, user_id, memory_json, created_at, updated_at in sessions:
            console.print(f"\n🔍 Session: {session_id}")
            console.print(f"   User: {user_id}")
            console.print(f"   Created: {created_at}")
            console.print(f"   Updated: {updated_at}")
            
            if memory_json:
                try:
                    memory_data = json.loads(memory_json)
                    console.print(f"   Memory size: {len(memory_json)} characters")
                    
                    # Analyze memory structure
                    if "runs" in memory_data:
                        runs = memory_data["runs"]
                        console.print(f"   📝 Runs: {len(runs)}")
                        
                        # Count messages
                        total_messages = 0
                        for run in runs:
                            if "messages" in run:
                                total_messages += len(run["messages"])
                        
                        console.print(f"   💬 Total messages: {total_messages}")
                        
                        # Show recent messages
                        if runs and "messages" in runs[-1]:
                            recent_messages = runs[-1]["messages"][-3:]  # Last 3 messages
                            console.print("   🔄 Recent messages:")
                            for msg in recent_messages:
                                role = msg.get("role", "unknown")
                                content = msg.get("content", "")[:100] + "..."
                                console.print(f"      {role}: {content}")
                    else:
                        console.print("   ⚠️ No 'runs' structure found in memory")
                        console.print(f"   📋 Memory keys: {list(memory_data.keys())}")
                        
                except json.JSONDecodeError as e:
                    console.print(f"   ❌ Invalid JSON in memory: {e}")
            else:
                console.print("   ⚠️ No memory data stored")
        
        conn.close()
        
    except Exception as e:
        console.print(f"❌ Database analysis failed: {e}")

def test_storage_retrieval():
    """Test if SqliteStorage can retrieve sessions correctly"""
    
    console.print("\n🧪 Testing Storage Retrieval Methods:")
    
    try:
        storage = SqliteStorage(
            table_name="research_agent_sessions",
            db_file="data/research_agent.db"
        )
        
        # Test get_all_session_ids for different users
        for user_id in ["1", "2"]:
            console.print(f"\n👤 User {user_id}:")
            try:
                sessions = storage.get_all_session_ids(user_id)
                console.print(f"   ✅ Found {len(sessions)} sessions: {sessions}")
                
                if sessions:
                    # Try to get messages for the first session
                    session_id = sessions[0]
                    console.print(f"   🔍 Testing session: {session_id}")
                    
                    # Check if we can access session data
                    try:
                        # Try different methods to get session data
                        if hasattr(storage, 'get_session'):
                            session_data = storage.get_session(user_id, session_id)
                            console.print(f"   📋 Session data available: {session_data is not None}")
                        
                        if hasattr(storage, 'get_messages'):
                            messages = storage.get_messages(user_id, session_id)
                            console.print(f"   💬 Messages available: {messages is not None}")
                            
                    except Exception as e:
                        console.print(f"   ⚠️ Error accessing session data: {e}")
                
            except Exception as e:
                console.print(f"   ❌ Error getting sessions: {e}")
                
    except Exception as e:
        console.print(f"❌ Storage test failed: {e}")

def check_agno_memory_structure():
    """Check how Agno structures memory internally"""
    
    console.print("\n🔬 Agno Memory Structure Analysis:")
    
    # Create a test agent to see memory structure
    try:
        from agno.agent import Agent
        from agno.models.azure.openai_chat import AzureOpenAI
        
        # Create minimal test agent
        test_model = AzureOpenAI(
            api_key="test",
            azure_endpoint="https://test.com",
            api_version="2024-02-01",
            azure_deployment="test"
        )
        
        storage = SqliteStorage(
            table_name="research_agent_sessions",
            db_file="data/research_agent.db"
        )
        
        agent = Agent(
            name="Test Agent",
            user_id="1",
            session_id="4f22b168-f1d8-444f-b22d-fa0ddff359d1",  # Existing session
            model=test_model,
            storage=storage,
            add_history_to_messages=True,
            num_history_responses=25
        )
        
        console.print("✅ Test agent created successfully")
        console.print(f"   Session ID: {agent.session_id}")
        console.print(f"   User ID: {agent.user_id}")
        
        # Check memory attribute
        if hasattr(agent, 'memory'):
            console.print(f"   💭 Memory object exists: {agent.memory is not None}")
            if agent.memory:
                console.print(f"   📊 Memory type: {type(agent.memory)}")
                console.print(f"   🗂️ Memory attributes: {dir(agent.memory)}")
                
                # Check runs
                if hasattr(agent.memory, 'runs'):
                    console.print(f"   🏃 Runs available: {agent.memory.runs is not None}")
                    if agent.memory.runs:
                        console.print(f"   📈 Runs type: {type(agent.memory.runs)}")
                        if isinstance(agent.memory.runs, dict):
                            console.print(f"   🔑 Run keys: {list(agent.memory.runs.keys())}")
        else:
            console.print("   ❌ No memory attribute found")
            
        # Check storage connection
        if hasattr(agent, 'storage'):
            console.print(f"   🗄️ Storage connected: {agent.storage is not None}")
        
    except Exception as e:
        console.print(f"❌ Agno memory analysis failed: {e}")

def diagnose_memory_issue():
    """Main diagnostic function"""
    
    console.print(Panel.fit(
        """
🔍 Memory Diagnostic Tool

This tool will analyze why the agent isn't properly accessing stored conversations.
We'll check:
1. Database content and structure
2. Storage retrieval methods
3. Agno's internal memory structure
        """,
        title="🧪 Memory Investigation",
        border_style="blue"
    ))
    
    # Run all diagnostic tests
    analyze_database_content()
    test_storage_retrieval()
    check_agno_memory_structure()
    
    console.print("\n" + "="*60)
    console.print("📋 DIAGNOSIS SUMMARY:")
    console.print("="*60)
    console.print("""
🎯 Key Things to Check:

1. Are messages actually stored in the database?
2. Can SqliteStorage retrieve them?
3. Is Agno loading them into agent.memory?
4. Are they being included in the LLM context?

If any of these fail, the agent will appear to have memory
but will actually be generating fake responses.
    """)

if __name__ == "__main__":
    diagnose_memory_issue()