"""
Demo script for pie chart functionality
Shows how to use the new pie chart feature in the LLM Canvas Chatbot
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_canvas_chatbot import CanvasChatbot

def demo_pie_chart():
    """Demonstrate pie chart functionality"""
    print("🎯 PIE CHART FUNCTIONALITY DEMO")
    print("=" * 50)
    print("This demo shows how to create pie charts using the LLM Canvas Chatbot.")
    print("You can interact with the chatbot using natural language!")
    print()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key to run this demo.")
        return
    
    # Ask user about headless mode
    headless_input = input("Run browser in headless mode? (y/N): ").strip().lower()
    headless = headless_input == 'y'
    
    # Initialize chatbot
    chatbot = CanvasChatbot(headless=headless)
    
    try:
        chatbot.initialize()
        
        print("\n🎨 DEMO SEQUENCE")
        print("=" * 30)
        
        # Demo sequence
        demo_commands = [
            "Clear the canvas to start fresh",
            "Create a container at position 100,100 with size 400x300 called 'sales_chart'",
            "Create a pie chart in container 'sales_chart' with the title 'Q4 Sales by Region'",
            "Create another container at position 550,100 with size 400x300 called 'budget_chart'",
            "Create a pie chart in container 'budget_chart' with custom data: Labels are Marketing, Development, Sales, Support and values are 30, 40, 20, 10 with title 'Department Budget'",
            "Take a screenshot and save it as 'pie_chart_demo.png'",
            "Show me the current canvas state"
        ]
        
        for i, command in enumerate(demo_commands, 1):
            print(f"\n{i}. Command: {command}")
            print("   Processing...")
            
            response = chatbot.process_user_message(command)
            print(f"   ✅ Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            
            if not headless:
                input("   Press Enter to continue...")
        
        print("\n🎉 Demo completed successfully!")
        print("\nYou can now interact with the chatbot directly.")
        print("Try commands like:")
        print("• 'Create a pie chart showing market share data'")
        print("• 'Add a pie chart with custom values to a new container'")
        print("• 'Show me what's on the canvas'")
        print()
        
        # Interactive mode
        while True:
            try:
                user_input = input("\n💬 Your command (or 'quit' to exit): ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() in ['help', '?']:
                    chatbot.show_help()
                    continue
                
                print("🤖 Processing...")
                response = chatbot.process_user_message(user_input)
                print(f"🤖 Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user.")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again or type 'help' for assistance.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    
    finally:
        if chatbot.canvas_controller:
            print("\n🔒 Closing browser...")
            chatbot.canvas_controller.close()

if __name__ == "__main__":
    demo_pie_chart() 