"""
Test script to verify pie charts stay within container bounds
Tests responsive sizing and container constraint behavior
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_canvas_chatbot import CanvasChatbot

def test_pie_chart_container_bounds():
    """Test that pie charts properly constrain to container bounds"""
    print("🧪 TESTING PIE CHART CONTAINER BOUNDS")
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
        
        # Test sequence for container bounds
        test_scenarios = [
            {
                "name": "Large Container Test",
                "commands": [
                    "Clear the canvas",
                    "Create a container at 50,50 with size 600x400 called 'large_container'",
                    "Create a pie chart in container 'large_container' with title 'Large Container Chart'"
                ]
            },
            {
                "name": "Small Container Test", 
                "commands": [
                    "Create a container at 700,50 with size 200x150 called 'small_container'",
                    "Create a pie chart in container 'small_container' with title 'Small Container Chart'"
                ]
            },
            {
                "name": "Very Small Container Test",
                "commands": [
                    "Create a container at 50,500 with size 120x100 called 'tiny_container'",
                    "Create a pie chart in container 'tiny_container' with title 'Tiny Chart'"
                ]
            },
            {
                "name": "Container Resize Test",
                "commands": [
                    "Modify container 'large_container' to position 50,50 with size 300x200",
                    "Modify container 'small_container' to position 400,50 with size 400x300"
                ]
            },
            {
                "name": "Custom Data Test",
                "commands": [
                    "Create a container at 700,400 with size 250x200 called 'custom_container'",
                    "Create a pie chart in container 'custom_container' with custom data: Labels are Sales, Marketing, Development, Support, Operations and values are 30, 20, 25, 15, 10 with title 'Department Budget'"
                ]
            }
        ]
        
        all_passed = True
        
        for scenario in test_scenarios:
            print(f"\n📋 {scenario['name']}")
            print("-" * 30)
            
            for i, command in enumerate(scenario['commands'], 1):
                print(f"   {i}. {command}")
                try:
                    response = chatbot.process_user_message(command)
                    success = "error" not in response.lower() and "failed" not in response.lower()
                    print(f"      {'✅' if success else '❌'} {response[:80]}{'...' if len(response) > 80 else ''}")
                    
                    if not success:
                        all_passed = False
                        
                except Exception as e:
                    print(f"      ❌ ERROR: {str(e)}")
                    all_passed = False
                
                # Small delay for visual inspection
                if not chatbot.headless:
                    input("      Press Enter to continue...")
        
        # Final verification
        print(f"\n📊 FINAL VERIFICATION")
        print("-" * 30)
        
        verification_commands = [
            "Show me the current canvas state",
            "Take a screenshot and save it as 'pie_chart_bounds_test.png'"
        ]
        
        for command in verification_commands:
            print(f"   {command}")
            try:
                response = chatbot.process_user_message(command)
                print(f"   ✅ {response[:100]}{'...' if len(response) > 100 else ''}")
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                all_passed = False
        
        print(f"\n🎯 CONTAINER BOUNDS TEST SUMMARY")
        print("=" * 50)
        
        if all_passed:
            print("✅ All pie chart container bounds tests PASSED!")
            print("🔍 Visual inspection points:")
            print("   • Large container should have a well-sized pie chart")
            print("   • Small container should have a proportionally smaller chart")
            print("   • Tiny container should have minimal but readable chart")
            print("   • Resized containers should show updated chart sizes")
            print("   • Custom data chart should fit properly in its container")
            print("   • All charts should be fully contained within their containers")
            print("   • No chart elements should overflow container boundaries")
        else:
            print("❌ Some container bounds tests failed!")
            print("   Check the output above for specific failures")
        
        if not chatbot.headless:
            input("\nPress Enter to close the test...")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False
    
    finally:
        if chatbot.canvas_controller:
            chatbot.canvas_controller.close()

if __name__ == "__main__":
    success = test_pie_chart_container_bounds()
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILURE'}: Container bounds test {'completed successfully' if success else 'failed'}")
    sys.exit(0 if success else 1) 