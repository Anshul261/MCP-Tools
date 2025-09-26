#!/usr/bin/env python3
"""
Quick test script to verify the API endpoints are working
"""
import requests
import json

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:7777/api/health")
        if response.status_code == 200:
            print("✅ Health endpoint working:", response.json())
            return True
        else:
            print("❌ Health endpoint failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ Health endpoint error:", e)
        return False

def test_visualizations():
    """Test the visualizations endpoint"""
    try:
        response = requests.get("http://localhost:7777/api/visualizations")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Visualizations endpoint working: found {len(data['visualizations'])} files")
            for viz in data['visualizations'][:3]:  # Show first 3
                print(f"   - {viz['filename']} ({viz['type']})")
            return True
        else:
            print("❌ Visualizations endpoint failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ Visualizations endpoint error:", e)
        return False

def test_chat():
    """Test the chat endpoint with a simple message"""
    try:
        response = requests.post("http://localhost:7777/api/chat", 
                               json={"message": "Hello, what data do you have access to?"})
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint working")
            print(f"   Response length: {len(data['response'])} characters")
            print(f"   Visualizations: {len(data['visualizations'])}")
            return True
        else:
            print("❌ Chat endpoint failed:", response.status_code, response.text)
            return False
    except Exception as e:
        print("❌ Chat endpoint error:", e)
        return False

if __name__ == "__main__":
    print("🧪 Testing Data Agent API Endpoints")
    print("=" * 50)
    
    print("\n1. Testing health endpoint...")
    health_ok = test_health()
    
    print("\n2. Testing visualizations endpoint...")
    viz_ok = test_visualizations()
    
    print("\n3. Testing chat endpoint (simple message)...")
    chat_ok = test_chat()
    
    print("\n" + "=" * 50)
    if all([health_ok, viz_ok, chat_ok]):
        print("🎉 All endpoints working!")
        print("\nNow you can:")
        print("1. Start the frontend: cd ui && npm run dev")
        print("2. Open http://localhost:3000")
        print("3. Ask for visualizations in the chat")
    else:
        print("❌ Some endpoints failed. Check if the backend is running:")
        print("   python agent.py")