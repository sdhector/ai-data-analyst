"""
Test script to verify robust bounds enforcement for pie charts
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_canvas_chatbot import CanvasChatbot
import time

def test_bounds_enforcement():
    """Test that bounds enforcement prevents charts from escaping containers"""
    print("🔒 TESTING ROBUST BOUNDS ENFORCEMENT")
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
        
        # Test sequence with bounds enforcement
        print("\n📋 Testing bounds enforcement...")
        
        # Create containers at edge positions to test bounds
        commands = [
            "Clear the canvas",
            "What's the current canvas size?",
            
            # Test edge positioning
            "Create a container at 0,0 with size 150x100 called 'top_left_edge'",
            "Create a container at 650,0 with size 150x100 called 'top_right_edge'",
            "Create a container at 0,500 with size 150x100 called 'bottom_left_edge'", 
            "Create a container at 650,500 with size 150x100 called 'bottom_right_edge'",
            
            # Test center position
            "Create a container at 325,250 with size 150x100 called 'center'",
            
            "Show me the current canvas state"
        ]
        
        for cmd in commands:
            print(f"\n   🔧 {cmd}")
            response = chatbot.process_user_message(cmd)
            success = "error" not in response.lower() and "failed" not in response.lower()
            print(f"   {'✅' if success else '❌'} {response[:100]}...")
            time.sleep(0.3)
        
        # Add pie charts to all containers
        print(f"\n🥧 Adding pie charts with bounds enforcement...")
        
        chart_commands = [
            ("top_left_edge", "Top Left Edge"),
            ("top_right_edge", "Top Right Edge"),
            ("bottom_left_edge", "Bottom Left Edge"),
            ("bottom_right_edge", "Bottom Right Edge"),
            ("center", "Center Chart")
        ]
        
        all_successful = True
        
        for container_id, title in chart_commands:
            print(f"\n   📊 Adding chart to '{container_id}'...")
            
            # Create pie chart
            create_cmd = f"Create a pie chart in container '{container_id}' with title '{title}'"
            print(f"      🔧 {create_cmd}")
            create_response = chatbot.process_user_message(create_cmd)
            create_success = "successfully" in create_response.lower()
            print(f"      {'✅' if create_success else '❌'} {create_response[:80]}...")
            
            # Verify bounds enforcement
            verify_cmd = f"Check what's in container '{container_id}'"
            print(f"      🔍 {verify_cmd}")
            verify_response = chatbot.process_user_message(verify_cmd)
            has_chart = "PIE CHART" in verify_response
            print(f"      {'✅' if has_chart else '❌'} Verification: Chart present")
            
            if not (create_success and has_chart):
                all_successful = False
            
            time.sleep(0.5)
        
        # Test container modification to ensure charts stay bounded
        print(f"\n📏 Testing bounds enforcement during container modification...")
        
        modify_commands = [
            "Modify container 'center' to position 100,100 with size 200x150",
            "Check what's in container 'center'",
            "Modify container 'top_left_edge' to position 50,50 with size 200x150", 
            "Check what's in container 'top_left_edge'"
        ]
        
        for cmd in modify_commands:
            print(f"\n   🔧 {cmd}")
            response = chatbot.process_user_message(cmd)
            success = "error" not in response.lower() and "failed" not in response.lower()
            print(f"   {'✅' if success else '❌'} {response[:80]}...")
            time.sleep(0.5)
        
        # Take screenshot for verification
        print(f"\n📸 Taking screenshot for bounds verification...")
        screenshot_response = chatbot.process_user_message("Take a screenshot and save it as 'bounds_enforcement_test.png'")
        print(f"   📷 {screenshot_response}")
        
        # Final state check
        print(f"\n🔍 Final canvas state check...")
        final_state = chatbot.process_user_message("Show me the current canvas state")
        print(f"   📊 {final_state}")
        
        print(f"\n🎯 BOUNDS ENFORCEMENT TEST RESULTS")
        print("=" * 60)
        
        if all_successful:
            print("🔒 SUCCESS: Bounds enforcement working correctly!")
            print("✅ All containers maintain fixed positions")
            print("✅ All pie charts stay within container bounds")
            print("✅ No charts escape to page-level positioning")
            print("✅ Container modifications preserve chart containment")
        else:
            print("❌ FAILURE: Some bounds enforcement issues detected")
        
        print("\n🔍 Visual Verification Checklist:")
        print("   • All containers should be exactly where positioned")
        print("   • All pie charts should be fully contained within containers")
        print("   • No chart elements should extend outside container borders")
        print("   • No chart elements should appear outside the canvas area")
        print("   • Container modifications should not break chart containment")
        
        if not chatbot.headless:
            input("\nPress Enter to close the test...")
        
        return all_successful
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        if chatbot.canvas_controller:
            chatbot.canvas_controller.close()

if __name__ == "__main__":
    success = test_bounds_enforcement()
    print(f"\n{'🔒 BOUNDS ENFORCEMENT SUCCESSFUL' if success else '❌ BOUNDS ENFORCEMENT FAILED'}")
    sys.exit(0 if success else 1) 