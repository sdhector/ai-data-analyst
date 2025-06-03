"""
Test script to verify the pie chart rendering fix
Tests the 2x2 grid scenario that was failing before
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_canvas_chatbot import CanvasChatbot
import time

def test_pie_chart_fix():
    """Test that the pie chart rendering fix works for 2x2 grid"""
    print("🧪 TESTING PIE CHART RENDERING FIX")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        return False
    
    # Initialize chatbot in visual mode to see the results
    chatbot = CanvasChatbot(headless=False)
    
    try:
        print("🔧 Initializing chatbot...")
        chatbot.initialize()
        
        # Test the exact scenario that was failing: 2x2 grid of pie charts
        print("\n📋 Creating 2x2 grid of containers...")
        
        grid_commands = [
            "Clear the canvas",
            "Create a container at 0,0 with size 401x301 called 'top_left_chart'",
            "Create a container at 402,0 with size 401x301 called 'top_right_chart'", 
            "Create a container at 0,302 with size 401x301 called 'bottom_left_chart'",
            "Create a container at 402,302 with size 401x301 called 'bottom_right_chart'"
        ]
        
        for cmd in grid_commands:
            print(f"   {cmd}")
            response = chatbot.process_user_message(cmd)
            success = "error" not in response.lower() and "failed" not in response.lower()
            print(f"   {'✅' if success else '❌'} {response[:80]}...")
            time.sleep(0.5)
        
        # Check container state
        print("\n📊 Verifying all containers created...")
        state_response = chatbot.process_user_message("Show me the current canvas state")
        print(f"   {state_response}")
        
        # Add pie charts to all containers
        print("\n🥧 Adding pie charts to all containers...")
        
        pie_chart_commands = [
            ("top_left_chart", "Top Left Chart"),
            ("top_right_chart", "Top Right Chart"),
            ("bottom_left_chart", "Bottom Left Chart"), 
            ("bottom_right_chart", "Bottom Right Chart")
        ]
        
        all_charts_successful = True
        
        for container_id, title in pie_chart_commands:
            cmd = f"Create a pie chart in container '{container_id}' with title '{title}'"
            print(f"   {cmd}")
            
            response = chatbot.process_user_message(cmd)
            success = "successfully" in response.lower() and "error" not in response.lower()
            
            print(f"   {'✅' if success else '❌'} {response}")
            
            if not success:
                all_charts_successful = False
            
            # Verify the chart was actually rendered
            try:
                chart_check = chatbot.canvas_controller.driver.execute_script("""
                    const container = document.getElementById(arguments[0]);
                    if (!container) return {error: 'Container not found'};
                    
                    return {
                        hasContent: container.innerHTML.length > 0,
                        contentType: container.getAttribute('data-content-type'),
                        childCount: container.children.length,
                        innerHTML: container.innerHTML.substring(0, 50) + '...'
                    };
                """, container_id)
                
                has_chart = chart_check.get('contentType') == 'pie-chart' and chart_check.get('hasContent', False)
                print(f"   📋 Chart verification: {'✅ RENDERED' if has_chart else '❌ NOT RENDERED'} - {chart_check}")
                
                if not has_chart:
                    all_charts_successful = False
                    
            except Exception as e:
                print(f"   ❌ Error verifying chart: {e}")
                all_charts_successful = False
            
            time.sleep(1)
        
        # Final verification
        print(f"\n📸 Taking screenshot for visual verification...")
        screenshot_response = chatbot.process_user_message("Take a screenshot and save it as 'pie_chart_fix_test.png'")
        print(f"   {screenshot_response}")
        
        # Summary
        print(f"\n🎯 TEST RESULTS")
        print("=" * 50)
        
        if all_charts_successful:
            print("✅ SUCCESS: All 4 pie charts rendered successfully!")
            print("🔍 Visual verification:")
            print("   • Check the browser window - you should see 4 pie charts in a 2x2 grid")
            print("   • All containers should have pie charts (no empty containers)")
            print("   • Charts should be properly contained within their boundaries")
            print("   • Screenshot saved for documentation")
        else:
            print("❌ FAILURE: Some pie charts failed to render")
            print("   Check the detailed output above for specific failures")
        
        if not chatbot.headless:
            input("\nPress Enter to close the test...")
        
        return all_charts_successful
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        if chatbot.canvas_controller:
            chatbot.canvas_controller.close()

if __name__ == "__main__":
    success = test_pie_chart_fix()
    print(f"\n{'🎉 FIX SUCCESSFUL' if success else '❌ FIX FAILED'}: Pie chart rendering {'works correctly' if success else 'still has issues'}")
    sys.exit(0 if success else 1) 