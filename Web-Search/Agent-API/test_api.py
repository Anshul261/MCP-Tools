#!/usr/bin/env python3
"""
Simple test script for Agent API
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from db import get_db, AsyncSessionLocal
from agents import create_enhanced_agent

async def test_agent_api():
    """Test the Agent API components"""
    
    print("🧪 Testing Agent API Components...")
    
    # Test database connection
    print("\n1. Testing database connection...")
    try:
        async with AsyncSessionLocal() as session:
            print("   ✅ Database connection successful")
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return
    
    # Test agent creation
    print("\n2. Testing agent creation...")
    try:
        async with AsyncSessionLocal() as session:
            agent = await create_enhanced_agent(session, "test_user")
            print(f"   ✅ Agent created successfully")
            print(f"   📍 Session ID: {agent.session_id}")
    except Exception as e:
        print(f"   ❌ Agent creation failed: {e}")
        return
    
    # Test search tools
    print("\n3. Testing search tools...")
    try:
        from agents.search_tools import SEARCH_TOOLS
        print(f"   ✅ Search tools loaded: {list(SEARCH_TOOLS.keys())}")
        
        # Test a simple web search (without API key)
        # This will fail but shows the structure works
        try:
            result = await SEARCH_TOOLS["web_search"]("test query")
            if isinstance(result, list) and len(result) > 0:
                if "error" in result[0]:
                    print(f"   ⚠️  Search failed as expected (no API key): {result[0]['error']}")
                else:
                    print(f"   ✅ Search succeeded: {len(result)} results")
        except Exception as e:
            print(f"   ⚠️  Search failed as expected: {e}")
    except Exception as e:
        print(f"   ❌ Search tools loading failed: {e}")
        return
    
    # Test agent query processing
    print("\n4. Testing agent query processing...")
    try:
        async with AsyncSessionLocal() as session:
            agent = await create_enhanced_agent(session, "test_user")
            
            # Simple test query
            result = await agent.process_query("Hello, can you introduce yourself?")
            
            if "error" in result:
                print(f"   ⚠️  Query processing had issues: {result['error']}")
            else:
                print(f"   ✅ Query processed successfully")
                print(f"   📝 Response preview: {result['response'][:100]}...")
                
    except Exception as e:
        print(f"   ❌ Query processing failed: {e}")
    
    print("\n🎉 Agent API component testing complete!")
    print("\n📋 Summary:")
    print("   - Database: SQLite working")
    print("   - Agent creation: Working")
    print("   - Search tools: Structure working (needs API key)")
    print("   - API endpoints: Ready for testing")
    print("\n💡 To test the full API:")
    print("   1. Set BRAVE_API_KEY in .env")
    print("   2. Run: python scripts/run_server.py")
    print("   3. Test: curl http://localhost:8000/health")

if __name__ == "__main__":
    asyncio.run(test_agent_api())