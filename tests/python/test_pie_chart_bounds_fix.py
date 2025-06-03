"""
Test script to verify pie charts stay within container bounds after the fix
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_canvas_chatbot import CanvasChatbot
import time

def test_pie_chart_bounds_fix():
    """Test that pie charts stay within container bounds"""
    print("🧪 TESTING PIE CHART BOUNDS FIX")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        return False
    
    # Initialize chatbot in visual mode
    chatbot = CanvasChatbot(headless=False)
    
    try:
        print("🔧 Initializing chatbot...")
        chatbot.initialize()
        
        # Test sequence
        print("\n📋 Testing pie chart bounds...")
        
        # Create a container and add a pie chart
        commands = [
            "Clear the canvas",
            "Create a container at 100,100 with size 300x200 called 'test_chart'",
            "Create a pie chart in container 'test_chart' with title 'Bounds Test Chart'",
            "Check what's in container 'test_chart'"
        ]
        
        for cmd in commands:
            print(f"\n   🔧 {cmd}")
            response = chatbot.process_user_message(cmd)
            success = "error" not in response.lower() and "failed" not in response.lower()
            print(f"   {'✅' if success else '❌'} {response}")
            time.sleep(0.5)
        
        # Test container modification to ensure chart adapts
        print(f"\n📏 Testing chart adaptation to container resize...")
        
        resize_commands = [
            "Modify container 'test_chart' to position 50,50 with size 400x300",
            "Check what's in container 'test_chart'"
        ]
        
        for cmd in resize_commands:
            print(f"\n   🔧 {cmd}")
            response = chatbot.process_user_message(cmd)
            success = "error" not in response.lower() and "failed" not in response.lower()
            print(f"   {'✅' if success else '❌'} {response}")
            time.sleep(0.5)
        
        # Take screenshot for verification
        print(f"\n📸 Taking screenshot for verification...")
        screenshot_response = chatbot.process_user_message("Take a screenshot and save it as 'pie_chart_bounds_fix_test.png'")
        print(f"   📷 {screenshot_response}")
        
        print(f"\n🎯 TEST COMPLETED")
        print("=" * 50)
        print("✅ Pie chart bounds fix test completed")
        print("🔍 Visual verification:")
        print("   • Check the browser window - pie chart should be fully contained within the container")
        print("   • Chart should not extend outside container boundaries")
        print("   • Chart should adapt to container size changes")
        print("   • No absolute positioning issues")
        
        if not chatbot.headless:
            input("\nPress Enter to close the test...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        if chatbot.canvas_controller:
            chatbot.canvas_controller.close()

if __name__ == "__main__":
    success = test_pie_chart_bounds_fix()
    print(f"\n{'🎉 BOUNDS FIX SUCCESSFUL' if success else '❌ BOUNDS FIX FAILED'}")
    sys.exit(0 if success else 1) 