"""
Quick automated test for pie chart functionality
Runs without user interaction to verify everything works
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_canvas_chatbot import CanvasChatbot

def quick_pie_chart_test():
    """Quick automated test of pie chart functionality"""
    print("🚀 QUICK PIE CHART TEST")
    print("=" * 40)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        return False
    
    # Initialize chatbot in headless mode
    chatbot = CanvasChatbot(headless=True)
    
    try:
        print("🔧 Initializing chatbot...")
        chatbot.initialize()
        
        # Test sequence
        test_commands = [
            ("Clear canvas", "Clear the canvas"),
            ("Create container", "Create a container at 100,100 with size 400x300 called 'test_chart'"),
            ("Sample pie chart", "Create a pie chart in container 'test_chart' with title 'Sample Data Chart'"),
            ("Create second container", "Create a container at 550,100 with size 400x300 called 'custom_chart'"),
            ("Custom pie chart", "Create a pie chart in container 'custom_chart' with custom data: Labels are A, B, C, D and values are 30, 25, 25, 20 with title 'Custom Data Chart'"),
            ("Canvas state", "Show me the current canvas state"),
            ("Screenshot", "Take a screenshot and save it as 'quick_pie_test.png'")
        ]
        
        results = []
        for test_name, command in test_commands:
            print(f"\n📋 {test_name}...")
            try:
                response = chatbot.process_user_message(command)
                success = "error" not in response.lower() and "failed" not in response.lower()
                results.append((test_name, success, response[:100] + "..." if len(response) > 100 else response))
                print(f"   {'✅' if success else '❌'} {test_name}: {'PASS' if success else 'FAIL'}")
            except Exception as e:
                results.append((test_name, False, str(e)))
                print(f"   ❌ {test_name}: ERROR - {str(e)}")
        
        # Summary
        print(f"\n📊 TEST RESULTS")
        print("=" * 40)
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)
        
        for test_name, success, response in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
            if not success:
                print(f"      Error: {response}")
        
        print(f"\n🎯 SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All pie chart functionality tests PASSED!")
            return True
        else:
            print("⚠️ Some tests failed. Check the output above.")
            return False
            
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False
    
    finally:
        if chatbot.canvas_controller:
            chatbot.canvas_controller.close()

if __name__ == "__main__":
    success = quick_pie_chart_test()
    sys.exit(0 if success else 1) 