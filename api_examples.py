#!/usr/bin/env python3
"""
API Usage Examples for AGNO Multi-Agent System

This script demonstrates how to interact with the AGNO Multi-Agent API,
including streaming chat responses, document management, and system monitoring.
"""

import asyncio
import json
import httpx
import time
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:8000"
USER_ID = "example_user"

async def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False

async def test_system_info():
    """Test system information endpoint"""
    print("🔍 Testing system info...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/v1/system/info")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System info retrieved: {data.get('system_info', {}).get('name')}")
            return True
        else:
            print(f"❌ System info failed: {response.status_code}")
            return False

async def test_create_session():
    """Test creating a new chat session"""
    print("🔍 Testing session creation...")
    
    async with httpx.AsyncClient() as client:
        payload = {
            "user_id": USER_ID,
            "title": "Test Session",
            "metadata": {"source": "api_examples"}
        }
        
        response = await client.post(
            f"{API_BASE_URL}/api/v1/chat/sessions",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data["session"]["session_id"]
            print(f"✅ Session created: {session_id}")
            return session_id
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            return None

async def test_chat_message(session_id: str = None):
    """Test sending a chat message with streaming"""
    print("🔍 Testing chat message with streaming...")
    
    payload = {
        "message": "Hello! Can you tell me about artificial intelligence and machine learning?",
        "user_id": USER_ID,
        "session_id": session_id,
        "stream": True,
        "show_reasoning": False,
        "stream_intermediate_steps": True
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            async with client.stream(
                "POST",
                f"{API_BASE_URL}/api/v1/chat/message",
                json=payload
            ) as response:
                
                if response.status_code == 200:
                    print("✅ Streaming chat response:")
                    print("-" * 40)
                    
                    # Process Server-Sent Events
                    content_buffer = ""
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])  # Remove "data: " prefix
                                
                                if data.get("event") == "content":
                                    content = data.get("data", {}).get("content", "")
                                    content_buffer += content
                                    print(content, end="", flush=True)
                                
                                elif data.get("event") == "status":
                                    status = data.get("data", {}).get("status")
                                    print(f"\n[{status}]", flush=True)
                                
                                elif data.get("event") == "complete":
                                    print(f"\n[Complete]")
                                    break
                                
                                elif data.get("event") == "error":
                                    error = data.get("data", {}).get("error")
                                    print(f"\n❌ Error: {error}")
                                    break
                                    
                            except json.JSONDecodeError:
                                continue  # Skip malformed JSON
                    
                    print("-" * 40)
                    print(f"✅ Chat response completed ({len(content_buffer)} chars)")
                    return True
                
                else:
                    print(f"❌ Chat message failed: {response.status_code}")
                    return False
                    
        except httpx.TimeoutException:
            print("❌ Chat request timed out")
            return False

async def test_list_sessions():
    """Test listing user sessions"""
    print("🔍 Testing session listing...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/v1/chat/sessions/{USER_ID}?limit=5"
        )
        
        if response.status_code == 200:
            data = response.json()
            session_count = len(data.get("sessions", []))
            print(f"✅ Sessions listed: {session_count} sessions found")
            return True
        else:
            print(f"❌ Session listing failed: {response.status_code}")
            return False

async def test_agent_status():
    """Test getting agent status"""
    print("🔍 Testing agent status...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/v1/system/agents/status")
        
        if response.status_code == 200:
            data = response.json()
            agent_count = len(data.get("agents", []))
            print(f"✅ Agent status retrieved: {agent_count} agents")
            
            # Print agent details
            for agent in data.get("agents", []):
                name = agent.get("agent_name")
                status = agent.get("status")
                capabilities = agent.get("capabilities", [])
                print(f"  • {name}: {status} ({len(capabilities)} capabilities)")
            
            return True
        else:
            print(f"❌ Agent status failed: {response.status_code}")
            return False

async def test_memory_status():
    """Test getting memory status"""
    print("🔍 Testing memory status...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/v1/system/memory-status")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get("memory_stats", {})
            total_memories = stats.get("total_memories", 0)
            db_size = stats.get("database_size_mb", 0)
            print(f"✅ Memory status: {total_memories} memories, {db_size:.2f}MB")
            return True
        else:
            print(f"❌ Memory status failed: {response.status_code}")
            return False

async def test_document_upload():
    """Test document upload (requires a sample file)"""
    print("🔍 Testing document upload...")
    
    # Create a sample document
    sample_doc = Path("sample_doc.txt")
    sample_doc.write_text("""
# Sample Document for API Testing

This is a sample document created for testing the AGNO Multi-Agent API
document upload and processing functionality.

## Key Points

- Document processing with streaming progress updates
- Knowledge base integration
- Real-time status notifications

## Conclusion

This document demonstrates the document processing capabilities of the system.
""")
    
    async with httpx.AsyncClient() as client:
        try:
            with open(sample_doc, "rb") as f:
                files = {"file": ("sample_doc.txt", f, "text/plain")}
                data = {
                    "description": "Sample document for API testing",
                    "tags": "test,sample,api",
                    "auto_process": "true"
                }
                
                response = await client.post(
                    f"{API_BASE_URL}/api/v1/documents/upload",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    doc_id = result["document"]["document_id"]
                    print(f"✅ Document uploaded: {doc_id}")
                    return doc_id
                else:
                    print(f"❌ Document upload failed: {response.status_code}")
                    return None
                    
        finally:
            # Clean up sample file
            if sample_doc.exists():
                sample_doc.unlink()

async def test_document_list():
    """Test listing documents"""
    print("🔍 Testing document listing...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/v1/documents/?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            doc_count = len(data.get("documents", []))
            print(f"✅ Documents listed: {doc_count} documents")
            return True
        else:
            print(f"❌ Document listing failed: {response.status_code}")
            return False

async def run_comprehensive_test():
    """Run a comprehensive test of the API"""
    print("🚀 Starting comprehensive API test\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("System Info", test_system_info),
        ("Agent Status", test_agent_status),
        ("Memory Status", test_memory_status),
        ("Document List", test_document_list),
        ("Create Session", test_create_session),
        ("List Sessions", test_list_sessions),
    ]
    
    results = []
    session_id = None
    
    for test_name, test_func in tests:
        try:
            if test_name == "Create Session":
                result = await test_func()
                session_id = result
                results.append(result is not None)
            else:
                result = await test_func()
                results.append(result)
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append(False)
        
        print()  # Add spacing between tests
    
    # Test chat with session if we have one
    if session_id:
        print("🔍 Testing chat with session...")
        chat_result = await test_chat_message(session_id)
        results.append(chat_result)
        print()
    
    # Test document upload
    try:
        doc_id = await test_document_upload()
        results.append(doc_id is not None)
        print()
    except Exception as e:
        print(f"❌ Document upload crashed: {e}")
        results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    print(f"📊 API Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API tests passed! The implementation is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the server logs for details.")
    
    print("=" * 60)

async def main():
    """Main function"""
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health", timeout=5.0)
            if response.status_code != 200:
                print(f"❌ Server not responding correctly at {API_BASE_URL}")
                print("💡 Start the server with: python start_api.py")
                return 1
    except httpx.ConnectError:
        print(f"❌ Cannot connect to server at {API_BASE_URL}")
        print("💡 Start the server with: python start_api.py")
        return 1
    except httpx.TimeoutException:
        print(f"❌ Server timeout at {API_BASE_URL}")
        return 1
    
    # Run comprehensive test
    await run_comprehensive_test()
    return 0

if __name__ == "__main__":
    asyncio.run(main())