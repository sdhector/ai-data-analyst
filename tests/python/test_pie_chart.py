"""
Test script for pie chart functionality in the LLM Canvas Chatbot
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_canvas_chatbot import CanvasChatbot

def test_pie_chart_functionality():
    """Test the pie chart creation functionality"""
    print("🧪 Testing Pie Chart Functionality")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = CanvasChatbot(headless=False)  # Visual mode to see the results
    
    try:
        chatbot.initialize()
        
        print("\n1. Testing pie chart with sample data...")
        response1 = chatbot.process_user_message("Create a container at 100,100 with size 400x300 called 'chart_container'")
        print(f"Container creation: {response1}")
        
        print("\n2. Adding pie chart with sample data...")
        response2 = chatbot.process_user_message("Create a pie chart in container 'chart_container' with the title 'Market Share'")
        print(f"Pie chart creation: {response2}")
        
        print("\n3. Testing custom pie chart data...")
        response3 = chatbot.process_user_message("Create another container at 550,100 with size 400x300 called 'custom_chart'")
        print(f"Second container: {response3}")
        
        print("\n4. Adding custom pie chart...")
        response4 = chatbot.process_user_message("""Create a pie chart in container 'custom_chart' with custom data:
        - Labels: Sales, Marketing, Development, Support
        - Values: 40, 25, 30, 5
        - Title: Department Budget""")
        print(f"Custom pie chart: {response4}")
        
        print("\n5. Taking screenshot...")
        response5 = chatbot.process_user_message("Take a screenshot and save it as 'pie_charts_test.png'")
        print(f"Screenshot: {response5}")
        
        print("\n6. Checking final canvas state...")
        response6 = chatbot.process_user_message("Show me the current canvas state")
        print(f"Final state: {response6}")
        
        print("\n✅ Pie chart test completed!")
        print("🔍 Check the browser window to see the pie charts")
        print("📸 Screenshot saved for verification")
        
        # Keep browser open for inspection
        input("\nPress Enter to close the test...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        if chatbot.canvas_controller:
            chatbot.canvas_controller.close()

def test_pie_chart_error_handling():
    """Test error handling for pie chart functionality"""
    print("\n🧪 Testing Pie Chart Error Handling")
    print("=" * 50)
    
    chatbot = CanvasChatbot(headless=True)  # Headless for quick error testing
    
    try:
        chatbot.initialize()
        
        print("\n1. Testing pie chart without container...")
        response1 = chatbot.process_user_message("Create a pie chart in container 'nonexistent'")
        print(f"No container test: {response1}")
        
        print("\n2. Creating container for further tests...")
        response2 = chatbot.process_user_message("Create a container at 100,100 with size 300x200 called 'test_container'")
        print(f"Container creation: {response2}")
        
        print("\n3. Testing custom data with mismatched arrays...")
        response3 = chatbot.process_user_message("""Create a pie chart with custom data:
        - Labels: A, B, C
        - Values: 10, 20
        - Container: test_container""")
        print(f"Mismatched arrays test: {response3}")
        
        print("\n✅ Error handling test completed!")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    finally:
        if chatbot.canvas_controller:
            chatbot.canvas_controller.close()

if __name__ == "__main__":
    print("🚀 Starting Pie Chart Tests...")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key to run this test.")
        sys.exit(1)
    
    # Run main functionality test
    test_pie_chart_functionality()
    
    # Run error handling test
    test_pie_chart_error_handling()
    
    print("🎉 All pie chart tests completed!") 