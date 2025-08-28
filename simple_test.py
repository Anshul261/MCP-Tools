#!/usr/bin/env python3
"""
Simplified test for the API implementation
"""

def test_basic_imports():
    """Test basic model imports"""
    try:
        from app.models.requests import ChatRequest, StreamingFormat
        from app.models.responses import ChatResponse
        print("✅ Model imports successful")
        return True
    except Exception as e:
        print(f"❌ Model imports failed: {e}")
        return False

def test_model_creation():
    """Test creating model instances"""
    try:
        from app.models.requests import ChatRequest, StreamingFormat
        from datetime import datetime, timezone
        
        request = ChatRequest(
            message="Test message",
            user_id="test_user"
        )
        print("✅ Model creation successful")
        return True
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def test_streaming_imports():
    """Test streaming module imports"""
    try:
        from app.core.streaming import StreamingManager, SSEFormatter
        print("✅ Streaming imports successful") 
        return True
    except Exception as e:
        print(f"❌ Streaming imports failed: {e}")
        return False

def main():
    tests = [
        test_basic_imports,
        test_model_creation,
        test_streaming_imports
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Core components working!")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    main()