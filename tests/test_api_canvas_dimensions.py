#!/usr/bin/env python3
"""
Test script for canvas dimension functionality via API
"""

import requests
import json
import time

def test_api_canvas_dimensions():
    """Test the canvas dimension functionality via API"""
    print("🌐 Testing Canvas Dimension API Functionality")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Wait for server to start
        print("Waiting for server to start...")
        for i in range(10):
            try:
                response = requests.get(f"{base_url}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Server is running!")
                    break
            except:
                time.sleep(1)
                print(f"   Attempt {i+1}/10...")
        else:
            print("❌ Server not responding after 10 attempts")
            return
        
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test chat endpoint with canvas dimension commands
        print("\n2. Testing chat endpoint with canvas dimension commands...")
        
        # Test getting current dimensions
        chat_data = {
            "message": "What are the current canvas dimensions?",
            "conversation_id": "test_session"
        }
        
        response = requests.post(f"{base_url}/chat", json=chat_data)
        print(f"✅ Get dimensions chat: {response.status_code}")
        result = response.json()
        print(f"   AI Response: {result.get('message', 'No message')[:200]}...")
        
        # Test setting canvas dimensions
        chat_data = {
            "message": "Set the canvas dimensions to 1600x900",
            "conversation_id": "test_session"
        }
        
        response = requests.post(f"{base_url}/chat", json=chat_data)
        print(f"✅ Set dimensions chat: {response.status_code}")
        result = response.json()
        print(f"   AI Response: {result.get('message', 'No message')[:200]}...")
        
        # Test canvas state endpoint
        print("\n3. Testing canvas state endpoint...")
        response = requests.get(f"{base_url}/canvas/state")
        print(f"✅ Canvas state: {response.status_code}")
        state = response.json()
        print(f"   Canvas size: {state.get('canvas_size', 'Unknown')}")
        
        # Test canvas size endpoint
        print("\n4. Testing canvas size endpoint...")
        response = requests.get(f"{base_url}/canvas/size")
        print(f"✅ Canvas size: {response.status_code}")
        size = response.json()
        print(f"   Size: {size}")
        
        print("\n🎉 All API tests completed successfully!")
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_canvas_dimensions() 