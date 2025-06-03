"""
Debug script to investigate positioning issues with pie charts
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_canvas_chatbot import CanvasChatbot
import time

def debug_positioning_issue():
    """Debug the positioning issue where charts appear in diagonal"""
    print("🔍 DEBUGGING POSITIONING ISSUE")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        return False
    
    # Initialize chatbot in visual mode
    chatbot = CanvasChatbot(headless=False)
    
    try:
        print("🔧 Initializing chatbot...")
        chatbot.initialize()
        
        # Test specific positioning requests
        print("\n📋 Testing specific positioning requests...")
        
        # Clear and get canvas info
        commands = [
            "Clear the canvas",
            "What's the current canvas size?",
            "Show me the current canvas state"
        ]
        
        for cmd in commands:
            print(f"\n   🔧 {cmd}")
            response = chatbot.process_user_message(cmd)
            print(f"   📄 {response}")
            time.sleep(0.5)
        
        # Test top-left positioning specifically
        print(f"\n📍 Testing TOP-LEFT positioning...")
        
        top_left_commands = [
            "Create a container at 0,0 with size 200x150 called 'top_left'",
            "Show me the current canvas state",
            "Create a pie chart in container 'top_left' with title 'Top Left Chart'",
            "Check what's in container 'top_left'"
        ]
        
        for cmd in top_left_commands:
            print(f"\n   🔧 {cmd}")
            response = chatbot.process_user_message(cmd)
            print(f"   📄 {response}")
            time.sleep(0.5)
        
        # Test another position to see the pattern
        print(f"\n📍 Testing TOP-RIGHT positioning...")
        
        top_right_commands = [
            "Create a container at 400,0 with size 200x150 called 'top_right'",
            "Show me the current canvas state", 
            "Create a pie chart in container 'top_right' with title 'Top Right Chart'",
            "Check what's in container 'top_right'"
        ]
        
        for cmd in top_right_commands:
            print(f"\n   🔧 {cmd}")
            response = chatbot.process_user_message(cmd)
            print(f"   📄 {response}")
            time.sleep(0.5)
        
        # Test bottom positions
        print(f"\n📍 Testing BOTTOM positioning...")
        
        bottom_commands = [
            "Create a container at 0,300 with size 200x150 called 'bottom_left'",
            "Create a container at 400,300 with size 200x150 called 'bottom_right'",
            "Show me the current canvas state",
            "Create a pie chart in container 'bottom_left' with title 'Bottom Left Chart'",
            "Create a pie chart in container 'bottom_right' with title 'Bottom Right Chart'"
        ]
        
        for cmd in bottom_commands:
            print(f"\n   🔧 {cmd}")
            response = chatbot.process_user_message(cmd)
            print(f"   📄 {response}")
            time.sleep(0.5)
        
        # Final verification
        print(f"\n🔍 Final verification of all containers...")
        verify_commands = [
            "Show me the current canvas state",
            "Check what's in container 'top_left'",
            "Check what's in container 'top_right'", 
            "Check what's in container 'bottom_left'",
            "Check what's in container 'bottom_right'"
        ]
        
        for cmd in verify_commands:
            print(f"\n   🔍 {cmd}")
            response = chatbot.process_user_message(cmd)
            print(f"   📄 {response}")
            time.sleep(0.3)
        
        # Take screenshot
        print(f"\n📸 Taking screenshot for analysis...")
        screenshot_response = chatbot.process_user_message("Take a screenshot and save it as 'positioning_debug.png'")
        print(f"   📷 {screenshot_response}")
        
        print(f"\n🎯 DEBUGGING RESULTS")
        print("=" * 60)
        print("🔍 Visual Analysis Required:")
        print("   • Check if containers are where they should be")
        print("   • Check if pie charts are inside their containers")
        print("   • Look for any diagonal pattern in chart placement")
        print("   • Verify canvas coordinate system is working correctly")
        print("   • Check if there's any offset or transformation applied")
        
        if not chatbot.headless:
            input("\nPress Enter to close the debug session...")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False
    
    finally:
        if chatbot.canvas_controller:
            chatbot.canvas_controller.close()

if __name__ == "__main__":
    success = debug_positioning_issue()
    print(f"\n{'🔍 DEBUG COMPLETED' if success else '❌ DEBUG FAILED'}")
    sys.exit(0 if success else 1) 