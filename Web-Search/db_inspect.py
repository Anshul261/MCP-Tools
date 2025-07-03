#!/usr/bin/env python3
"""
Memory Verification Script

Let's directly access Anshul's stored memory to see what's actually there.
"""

import sqlite3
import json
from datetime import datetime

def verify_anshul_memory():
    """Directly verify what's in Anshul's stored memory"""
    
    print("🔍 MEMORY VERIFICATION FOR ANSHUL")
    print("=" * 50)
    
    db_path = "tmp/brave_search_agents.db"
    table_name = "brave_search_sessions"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get Anshul's record
        cursor.execute(f"SELECT * FROM {table_name} WHERE user_id = ?", ("Anshul",))
        record = cursor.fetchone()
        
        if not record:
            print("❌ No record found for Anshul")
            return
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        
        print("✅ Found Anshul's record!")
        print(f"📊 Record structure: {col_names}")
        
        # Map record to column names
        record_dict = dict(zip(col_names, record))
        
        print(f"\n📋 Session Details:")
        print(f"  🆔 Session ID: {record_dict.get('session_id')}")
        print(f"  👤 User ID: {record_dict.get('user_id')}")
        print(f"  📅 Created: {datetime.fromtimestamp(record_dict.get('created_at', 0))}")
        print(f"  🔄 Updated: {datetime.fromtimestamp(record_dict.get('updated_at', 0))}")
        
        # Analyze the memory field
        memory_data = record_dict.get('memory')
        if memory_data:
            print(f"\n🧠 MEMORY ANALYSIS:")
            try:
                memory = json.loads(memory_data)
                print(f"  📊 Memory structure: {list(memory.keys())}")
                
                # Check runs (this is where conversations are stored)
                if 'runs' in memory:
                    runs = memory['runs']
                    print(f"  🏃 Runs: {len(runs)} conversation runs")
                    
                    for i, run in enumerate(runs, 1):
                        print(f"\n    📝 Run {i}:")
                        if isinstance(run, dict):
                            print(f"      📄 Content preview: {run.get('content', '')[:100]}...")
                            print(f"      🎯 Content type: {run.get('content_type', 'unknown')}")
                            
                            # Check for messages within the run
                            if 'messages' in run:
                                messages = run['messages']
                                print(f"      💬 Messages in run: {len(messages)}")
                                
                                for j, msg in enumerate(messages[:3], 1):
                                    if isinstance(msg, dict):
                                        role = msg.get('role', 'unknown')
                                        content = msg.get('content', '')
                                        preview = content[:60] + "..." if len(content) > 60 else content
                                        print(f"        {j}. {role}: {preview}")
                
                # Check summaries and memories
                if 'summaries' in memory:
                    summaries = memory['summaries']
                    print(f"  📋 Summaries: {len(summaries) if summaries else 0}")
                
                if 'memories' in memory:
                    memories = memory['memories']
                    print(f"  🧠 Memories: {len(memories) if memories else 0}")
                
            except json.JSONDecodeError:
                print("  ❌ Memory data is not valid JSON")
            except Exception as e:
                print(f"  ❌ Error analyzing memory: {e}")
        else:
            print("  ❌ No memory data found")
        
        # Check session_data
        session_data = record_dict.get('session_data')
        if session_data:
            print(f"\n📋 SESSION DATA:")
            try:
                session = json.loads(session_data)
                print(f"  📊 Session structure: {list(session.keys())}")
                
                if 'session_state' in session:
                    state = session['session_state']
                    print(f"  🎯 Session state: {state}")
                
            except json.JSONDecodeError:
                print("  ❌ Session data is not valid JSON")
            except Exception as e:
                print(f"  ❌ Error analyzing session data: {e}")
        
        conn.close()
        
        print(f"\n🎯 CONCLUSION:")
        print("=" * 50)
        if memory_data:
            print("✅ Memory data EXISTS in database")
            print("🔍 Issue is likely in how get_messages_for_session() parses this data")
            print("💡 The memory format uses 'runs' instead of direct 'messages'")
        else:
            print("❌ No memory data found - storage issue")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def test_agno_storage_access():
    """Test if we can access the memory using Agno's storage directly"""
    
    print(f"\n🧪 TESTING AGNO STORAGE ACCESS")
    print("=" * 40)
    
    try:
        from agno.storage.sqlite import SqliteStorage
        
        # Create storage with exact same config as the working database
        storage = SqliteStorage(
            table_name="brave_search_sessions",
            db_file="tmp/brave_search_agents.db"
        )
        
        print("✅ Created Agno storage instance")
        
        # Test session discovery
        sessions = storage.get_all_session_ids("Anshul")
        print(f"📁 Found {len(sessions)} sessions for Anshul: {sessions}")
        
        if sessions:
            session_id = sessions[0]
            print(f"🎯 Testing session: {session_id}")
            
            # Try to access session data
            # This might need different methods depending on Agno version
            print("🔍 Storage methods available:")
            methods = [method for method in dir(storage) if not method.startswith('_')]
            for method in methods:
                if 'session' in method.lower() or 'message' in method.lower():
                    print(f"  • {method}")
        
    except ImportError:
        print("❌ Cannot import Agno storage")
    except Exception as e:
        print(f"❌ Storage test error: {e}")

if __name__ == "__main__":
    verify_anshul_memory()
    test_agno_storage_access()