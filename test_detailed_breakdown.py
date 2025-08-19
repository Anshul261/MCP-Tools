#!/usr/bin/env python3
"""
Test script to see detailed breakdown logs from the agent API.
"""

import asyncio
import httpx
import time
import sys
import json


async def test_agent_detailed_response(agent_id: str, message: str, detailed: bool = True):
    """Test agent with detailed breakdown and print the formatted response"""
    
    print(f"\n🧪 Testing {agent_id} with message: '{message}'")
    print(f"📋 Detailed breakdown: {detailed}")
    print("=" * 100)
    
    url = f"http://localhost:8000/v1/agents/{agent_id}/chat"
    payload = {
        "message": message,
        "user_id": "test_user",
        "session_id": f"test_{int(time.time())}",
        "stream": True,
        "detailed_breakdown": detailed,
        "debug_mode": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream('POST', url, json=payload) as response:
                if response.status_code == 200:
                    print("✅ Streaming response:\n")
                    
                    # Collect and display all chunks
                    full_response = ""
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            if data == "[DONE]":
                                print("\n✅ Stream completed")
                                break
                            elif data.startswith("Error:"):
                                print(f"\n❌ Error: {data}")
                                break
                            else:
                                # Print the chunk directly to see the formatting
                                print(data, end='', flush=True)
                                full_response += data
                                
                else:
                    error_content = await response.aread()
                    try:
                        error_json = json.loads(error_content)
                        print(f"❌ API Error {response.status_code}: {error_json.get('detail', 'Unknown error')}")
                    except:
                        print(f"❌ HTTP Error {response.status_code}: {error_content.decode()}")
                        
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        print("Make sure the agent-api server is running on http://localhost:8000")


async def test_comparison():
    """Compare detailed vs simple response"""
    agent_id = "reasoning_team"
    message = "What is artificial intelligence?"
    
    print("\n" + "="*100)
    print("🔄 COMPARISON TEST: Detailed vs Simple Response")
    print("="*100)
    
    # Test detailed response
    print("\n📋 DETAILED RESPONSE FORMAT:")
    await test_agent_detailed_response(agent_id, message, detailed=True)
    
    print("\n" + "-"*100)
    
    # Test simple response
    print("\n📝 SIMPLE RESPONSE FORMAT:")
    await test_agent_detailed_response(agent_id, message, detailed=False)


async def test_all_agents():
    """Test all available agents with detailed breakdown"""
    
    test_cases = [
        ("doc_agent", "What is the internal hajj policy?"),
        ("web_agent", "What's the latest news about artificial intelligence?"),
        ("reasoning_team", "Tell me about the model context protocol"),
    ]
    
    print("🚀 TESTING ALL 3 AGENTS WITH DETAILED BREAKDOWN (UI-STYLE LOGS)")
    print("="*100)
    
    # Check API health first
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            health_response = await client.get("http://localhost:8000/v1/health")
            if health_response.status_code == 200:
                print("✅ API server is running and healthy")
                
                # Also check available agents
                agents_response = await client.get("http://localhost:8000/v1/agents")
                if agents_response.status_code == 200:
                    available_agents = agents_response.json()
                    print(f"✅ Available agents: {available_agents}")
                else:
                    print(f"⚠️ Could not fetch agents list: {agents_response.status_code}")
            else:
                print(f"⚠️ API health check returned: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("Please start the server with: cd agent-api-main && PYTHONPATH=. python -m uvicorn api.main:app --reload --port 8000")
        return
    
    # Test each agent
    for i, (agent_id, message) in enumerate(test_cases, 1):
        print(f"\n{'='*50} AGENT {i}/3: {agent_id.upper()} {'='*50}")
        await test_agent_detailed_response(agent_id, message, detailed=True)
        
        if i < len(test_cases):
            print(f"\n⏳ Waiting 2 seconds before next agent test...")
            await asyncio.sleep(2)
    
    print(f"\n{'='*100}")
    print("🎉 All 3 agents tested successfully!")
    print("💡 This is how the logs would appear in your perplexity-chat-ui!")


async def quick_test():
    """Quick test with just one agent"""
    print("⚡ QUICK TEST - Reasoning Team with Detailed Breakdown")
    print("="*100)
    
    await test_agent_detailed_response(
        "reasoning_team", 
        "What is the model context protocol?", 
        detailed=True
    )


async def check_available_agents():
    """Check what agents are available"""
    print("📋 Checking available agents...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8000/v1/agents/info")
            if response.status_code == 200:
                agents = response.json()
                print(f"✅ Found {len(agents)} agents:")
                for agent in agents:
                    print(f"  • {agent['id']}: {agent['name']} ({agent['type']})")
                    print(f"    Description: {agent['description']}")
                return True
            else:
                print(f"❌ Failed to get agents: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error checking agents: {e}")
        return False


def print_usage():
    """Print usage information"""
    print("""
🧪 Agent API Detailed Breakdown Test Script - UI-Style Logs

Usage:
    python test_detailed_breakdown.py [command]

Commands:
    all        - Test ALL 3 agents with UI-style detailed breakdown (default)
    quick      - Quick test with reasoning team
    compare    - Compare detailed vs simple response
    agents     - List available agents
    help       - Show this help

Examples:
    python test_detailed_breakdown.py              # Test all 3 agents
    python test_detailed_breakdown.py quick        # Quick single test
    python test_detailed_breakdown.py compare      # Compare formats
    python test_detailed_breakdown.py agents       # List agents

Make sure the agent-api server is running:
    cd agent-api-main && PYTHONPATH=. python -m uvicorn api.main:app --reload --port 8000
    
This will show you the SAME detailed logs as your multi-agent-system.py but through the API!
    """)


async def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "help":
            print_usage()
        elif command == "quick":
            await quick_test()
        elif command == "compare":
            await test_comparison()
        elif command == "agents":
            await check_available_agents()
        elif command == "all":
            await test_all_agents()
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
    else:
        # Default action
        if await check_available_agents():
            print("\n")
            await test_all_agents()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")