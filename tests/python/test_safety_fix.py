"""
Test script to verify that LLM chatbot cannot bypass safety systems
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_canvas_chatbot import CanvasChatbot

def test_safety_fix():
    """Test that LLM cannot bypass overlap prevention"""
    print("🧪 Testing Safety Fix - LLM Cannot Bypass Overlap Prevention")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = CanvasChatbot(headless=True)
    
    try:
        chatbot.initialize()
        
        # Test 1: Create a full-canvas container
        print("\n1. Creating full-canvas container...")
        response1 = chatbot.process_user_message("Create a container that fills the entire canvas")
        print(f"Response: {response1}")
        
        # Test 2: Try to create overlapping container (should fail and NOT bypass safety)
        print("\n2. Trying to create overlapping container...")
        response2 = chatbot.process_user_message("Create another container half the size of the canvas at position 0,0")
        print(f"Response: {response2}")
        
        # Test 3: Check if toggle functions are available
        print("\n3. Testing if toggle functions are still available...")
        response3 = chatbot.process_user_message("Disable overlap prevention")
        print(f"Response: {response3}")
        
        # Test 4: Check final state
        print("\n4. Checking final canvas state...")
        response4 = chatbot.process_user_message("Show me the current canvas state")
        print(f"Response: {response4}")
        
        print("\n✅ Safety fix test completed!")
        print("🔍 Check the responses above:")
        print("   - The LLM should NOT be able to disable overlap prevention")
        print("   - The second container should be rejected or repositioned")
        print("   - No overlapping containers should exist")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        if chatbot.canvas_controller:
            chatbot.canvas_controller.close()

if __name__ == "__main__":
    test_safety_fix() 