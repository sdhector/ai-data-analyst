"""
Debug script to investigate pie chart rendering issues
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_canvas_chatbot import CanvasChatbot
import time

def debug_pie_chart_rendering():
    """Debug pie chart rendering in multiple containers"""
    print("🔍 DEBUGGING PIE CHART RENDERING")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        return
    
    # Initialize chatbot in visual mode
    chatbot = CanvasChatbot(headless=False)
    
    try:
        chatbot.initialize()
        
        # Test sequence
        commands = [
            "Clear the canvas",
            "Create a container at 0,0 with size 400x300 called 'test1'",
            "Create a container at 410,0 with size 400x300 called 'test2'",
            "Create a container at 0,310 with size 400x300 called 'test3'",
            "Create a container at 410,310 with size 400x300 called 'test4'"
        ]
        
        print("\n📋 Creating containers...")
        for cmd in commands:
            print(f"   {cmd}")
            response = chatbot.process_user_message(cmd)
            print(f"   → {response[:80]}...")
            time.sleep(0.5)
        
        # Check container state
        print("\n📊 Checking container state...")
        state_response = chatbot.process_user_message("Show me the current canvas state")
        print(f"   → {state_response}")
        
        # Add pie charts one by one with debugging
        pie_commands = [
            ("test1", "Chart 1"),
            ("test2", "Chart 2"), 
            ("test3", "Chart 3"),
            ("test4", "Chart 4")
        ]
        
        print("\n🥧 Adding pie charts...")
        for container_id, title in pie_commands:
            cmd = f"Create a pie chart in container '{container_id}' with title '{title}'"
            print(f"   {cmd}")
            
            # Execute and check for detailed response
            response = chatbot.process_user_message(cmd)
            print(f"   → {response}")
            
            # Check if container has content using JavaScript
            try:
                has_content = chatbot.canvas_controller.driver.execute_script(f"""
                    const container = document.getElementById('{container_id}');
                    if (!container) return 'Container not found';
                    
                    return {{
                        hasContent: container.innerHTML.length > 0,
                        contentType: container.getAttribute('data-content-type'),
                        innerHTML: container.innerHTML.substring(0, 100)
                    }};
                """)
                print(f"   📋 Container '{container_id}' content check: {has_content}")
            except Exception as e:
                print(f"   ❌ Error checking container content: {e}")
            
            time.sleep(1)
            
            if not chatbot.headless:
                input("   Press Enter to continue...")
        
        print("\n📸 Taking final screenshot...")
        screenshot_response = chatbot.process_user_message("Take a screenshot and save it as 'debug_pie_charts.png'")
        print(f"   → {screenshot_response}")
        
        if not chatbot.headless:
            input("\nPress Enter to close...")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
    
    finally:
        if chatbot.canvas_controller:
            chatbot.canvas_controller.close()

if __name__ == "__main__":
    debug_pie_chart_rendering() 