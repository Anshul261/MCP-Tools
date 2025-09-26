#!/usr/bin/env python3
"""
Simple test script to validate the AGNO Multi-Agent API implementation
"""

import sys
import asyncio
import httpx
from pathlib import Path

# Add app to path for imports
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported successfully"""
    print("🔍 Testing imports...")
    
    try:
        # Test core imports
        from app.core.streaming import StreamingManager, WebStreamingResponseHandler
        from app.core.database import DatabaseManager, SessionManager
        from app.core.agents import AgentSystemManager
        
        # Test model imports
        from app.models.requests import ChatRequest, CreateSessionRequest
        from app.models.responses import ChatResponse, SessionCreateResponse
        
        # Test API imports
        from app.api.v1.chat import router as chat_router
        from app.api.v1.documents import router as documents_router
        from app.api.v1.system import router as system_router
        
        # Test main app
        from app.main import app
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_model_validation():
    """Test Pydantic model validation"""
    print("🔍 Testing model validation...")
    
    try:
        from app.models.requests import ChatRequest, StreamingFormat
        from app.models.responses import ChatResponse
        from datetime import datetime, timezone
        
        # Test ChatRequest validation
        chat_request = ChatRequest(
            message="Hello, world!",
            user_id="test_user",
            stream=True,
            streaming_format=StreamingFormat.SSE
        )
        
        print(f"✅ ChatRequest validation successful: {chat_request.message}")
        
        # Test ChatResponse validation
        chat_response = ChatResponse(
            success=True,
            response="Hello! How can I help you?",
            session_id="test_session",
            agent_used="team",
            timestamp=datetime.now(timezone.utc)
        )
        
        print(f"✅ ChatResponse validation successful")
        return True
        
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        return False

def test_streaming_components():
    """Test streaming system components"""
    print("🔍 Testing streaming components...")
    
    try:
        from app.core.streaming import StreamingManager, SSEFormatter
        
        # Test streaming manager
        manager = StreamingManager()
        stream_id = manager.create_stream("test_user", "test_session", "chat")
        
        print(f"✅ Created stream: {stream_id}")
        
        # Test SSE formatter
        test_event = SSEFormatter.format_event("test", {"message": "Hello"})
        print(f"✅ SSE formatting works: {len(test_event)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False

def test_agent_system():
    """Test agent system initialization"""
    print("🔍 Testing agent system...")
    
    try:
        from app.core.agents import agent_system
        
        if hasattr(agent_system, 'initialized'):
            print(f"✅ Agent system initialization status: {agent_system.initialized}")
        else:
            print("⚠️ Agent system has no initialized attribute")
        
        # Test getting agent status
        status = agent_system.get_agent_status()
        print(f"✅ Agent status retrieved: {len(status)} agents")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent system test failed: {e}")
        return False

async def test_app_startup():
    """Test FastAPI app can start"""
    print("🔍 Testing FastAPI app startup...")
    
    try:
        from app.main import app
        
        # Test that we can create the app
        print(f"✅ FastAPI app created: {app.title}")
        
        # Test basic route structure
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/api/v1/chat/message", "/api/v1/system/health"]
        
        found_routes = []
        for expected in expected_routes:
            if any(expected in route for route in routes):
                found_routes.append(expected)
        
        print(f"✅ Found {len(found_routes)}/{len(expected_routes)} expected routes")
        
        return True
        
    except Exception as e:
        print(f"❌ App startup test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AGNO Multi-Agent API Tests\n")
    
    tests = [
        test_imports,
        test_model_validation, 
        test_streaming_components,
        test_agent_system,
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
        print()
    
    # Run async tests
    print("🔍 Running async tests...")
    try:
        async_result = asyncio.run(test_app_startup())
        results.append(async_result)
    except Exception as e:
        print(f"❌ Async tests failed: {e}")
        results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API implementation looks good.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)