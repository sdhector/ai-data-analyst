"""
Test script using the new check_container_content function to verify pie chart creation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_canvas_chatbot import CanvasChatbot
import time

def test_pie_chart_with_verification():
    """Test pie chart creation with the new verification function"""
    print("🧪 TESTING PIE CHART WITH CONTENT VERIFICATION")
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
        
        # Test sequence with verification
        print("\n📋 Creating 2x2 grid and verifying each step...")
        
        # Step 1: Clear and create containers
        commands = [
            "Clear the canvas",
            "Create a container at 0,0 with size 401x301 called 'top_left'",
            "Create a container at 402,0 with size 401x301 called 'top_right'",
            "Create a container at 0,302 with size 401x301 called 'bottom_left'",
            "Create a container at 402,302 with size 401x301 called 'bottom_right'"
        ]
        
        for cmd in commands:
            print(f"\n   🔧 {cmd}")
            response = chatbot.process_user_message(cmd)
            success = "error" not in response.lower() and "failed" not in response.lower()
            print(f"   {'✅' if success else '❌'} {response[:100]}...")
        
        # Step 2: Verify containers are empty initially
        print(f"\n📋 Verifying containers are initially empty...")
        container_ids = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
        
        for container_id in container_ids:
            cmd = f"Check what's in container '{container_id}'"
            print(f"\n   🔍 {cmd}")
            response = chatbot.process_user_message(cmd)
            print(f"   📄 {response}")
        
        # Step 3: Add pie charts one by one with immediate verification
        print(f"\n🥧 Adding pie charts with immediate verification...")
        
        pie_chart_data = [
            ('top_left', 'Sales Data'),
            ('top_right', 'Marketing Data'),
            ('bottom_left', 'Development Data'),
            ('bottom_right', 'Support Data')
        ]
        
        all_successful = True
        
        for container_id, title in pie_chart_data:
            print(f"\n   📊 Creating pie chart in '{container_id}'...")
            
            # Create pie chart
            create_cmd = f"Create a pie chart in container '{container_id}' with title '{title}'"
            print(f"      🔧 {create_cmd}")
            create_response = chatbot.process_user_message(create_cmd)
            create_success = "successfully" in create_response.lower()
            print(f"      {'✅' if create_success else '❌'} {create_response[:100]}...")
            
            # Immediately verify the chart was created
            verify_cmd = f"Check what's in container '{container_id}'"
            print(f"      🔍 {verify_cmd}")
            verify_response = chatbot.process_user_message(verify_cmd)
            has_pie_chart = "PIE CHART" in verify_response
            print(f"      {'✅' if has_pie_chart else '❌'} Verification: {verify_response}")
            
            if not (create_success and has_pie_chart):
                all_successful = False
                print(f"      ❌ FAILED: Chart creation or verification failed for '{container_id}'")
            else:
                print(f"      ✅ SUCCESS: Chart verified in '{container_id}'")
            
            time.sleep(1)
        
        # Step 4: Final verification of all containers
        print(f"\n📊 Final verification of all containers...")
        for container_id in container_ids:
            cmd = f"Verify the pie chart in container '{container_id}'"
            print(f"\n   🔍 {cmd}")
            response = chatbot.process_user_message(cmd)
            has_chart = "PIE CHART" in response
            print(f"   {'✅' if has_chart else '❌'} Final check: {response}")
            
            if not has_chart:
                all_successful = False
        
        # Step 5: Take screenshot
        print(f"\n📸 Taking final screenshot...")
        screenshot_cmd = "Take a screenshot and save it as 'pie_chart_verification_test.png'"
        screenshot_response = chatbot.process_user_message(screenshot_cmd)
        print(f"   📷 {screenshot_response}")
        
        # Summary
        print(f"\n🎯 TEST RESULTS")
        print("=" * 60)
        
        if all_successful:
            print("🎉 SUCCESS: All pie charts created and verified successfully!")
            print("✅ All 4 containers have pie charts")
            print("✅ Content verification function works correctly")
            print("✅ No empty containers detected")
            print("📸 Screenshot saved for visual confirmation")
        else:
            print("❌ FAILURE: Some pie charts failed creation or verification")
            print("🔍 Check the detailed output above for specific issues")
        
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
    success = test_pie_chart_with_verification()
    print(f"\n{'🎉 VERIFICATION SUCCESSFUL' if success else '❌ VERIFICATION FAILED'}")
    sys.exit(0 if success else 1) 