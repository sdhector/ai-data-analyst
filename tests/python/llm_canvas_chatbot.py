"""
LLM Canvas Chatbot

A terminal-based chatbot interface that uses LLM function calling to control
the canvas through natural language commands. Follows the core AI engine architecture.
"""

import json
import os
import sys
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import openai
from openai import OpenAI

# Add the project root to the path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from canvas_controller import CanvasController

# Load environment variables
load_dotenv()

class CanvasLLMClient:
    """
    LLM client specifically configured for canvas control operations
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM client for canvas operations
        
        Args:
            api_key: OpenAI API key
            model: Model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # System message for canvas control
        self.system_message = """You are a Canvas Control Assistant. You help users manage containers on a visual canvas through function calls.

Available capabilities:
- Create containers at specific positions and sizes
- Delete containers by ID
- Modify existing containers (position and size)
- View current canvas state
- Clear all containers
- Take screenshots
- Edit canvas size

Canvas specifications:
- Default size: 800x600 pixels (customizable)
- Coordinate system: Top-left origin (0,0)
- Position values: x, y coordinates in pixels
- Size values: width, height in pixels
- Auto-adjustment: Containers automatically fit within canvas bounds
- Overlap prevention: Containers avoid overlapping with existing ones

When users request canvas operations:
1. Use the appropriate function to perform the action
2. Always explain what you're doing
3. Provide feedback on the results
4. Suggest next steps if helpful

Be helpful, clear, and always confirm successful operations."""
    
    def get_function_schemas(self) -> List[Dict]:
        """Get function schemas for canvas operations"""
        return [
            {
                "name": "create_container",
                "description": "Create a new container on the canvas at specified position and size",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "Unique identifier for the container"
                        },
                        "x": {
                            "type": "integer",
                            "description": "X position in pixels (0 = left edge)"
                        },
                        "y": {
                            "type": "integer", 
                            "description": "Y position in pixels (0 = top edge)"
                        },
                        "width": {
                            "type": "integer",
                            "description": "Width in pixels"
                        },
                        "height": {
                            "type": "integer",
                            "description": "Height in pixels"
                        }
                    },
                    "required": ["container_id", "x", "y", "width", "height"]
                }
            },
            {
                "name": "delete_container",
                "description": "Delete a container from the canvas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID of the container to delete"
                        }
                    },
                    "required": ["container_id"]
                }
            },
            {
                "name": "modify_container",
                "description": "Modify an existing container's position and size",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID of the container to modify"
                        },
                        "x": {
                            "type": "integer",
                            "description": "New X position in pixels"
                        },
                        "y": {
                            "type": "integer",
                            "description": "New Y position in pixels"
                        },
                        "width": {
                            "type": "integer",
                            "description": "New width in pixels"
                        },
                        "height": {
                            "type": "integer",
                            "description": "New height in pixels"
                        }
                    },
                    "required": ["container_id", "x", "y", "width", "height"]
                }
            },
            {
                "name": "get_canvas_state",
                "description": "Get the current state of the canvas including all containers",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "clear_canvas",
                "description": "Remove all containers from the canvas",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "take_screenshot",
                "description": "Take a screenshot of the current canvas state",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Optional filename for the screenshot"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_canvas_size",
                "description": "Get the current canvas dimensions",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "edit_canvas_size",
                "description": "Change the canvas dimensions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "width": {
                            "type": "integer",
                            "description": "New canvas width in pixels"
                        },
                        "height": {
                            "type": "integer",
                            "description": "New canvas height in pixels"
                        }
                    },
                    "required": ["width", "height"]
                }
            }
        ]
    
    def chat_completion(self, messages: List[Dict], functions: List[Dict] = None) -> Dict[str, Any]:
        """
        Create a chat completion with function calling
        
        Args:
            messages: Conversation messages
            functions: Available functions
            
        Returns:
            LLM response
        """
        try:
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7
            }
            
            if functions:
                request_params["functions"] = functions
                request_params["function_call"] = "auto"
            
            response = self.client.chat.completions.create(**request_params)
            choice = response.choices[0]
            
            return {
                "status": "success",
                "message": choice.message,
                "content": choice.message.content,
                "function_call": getattr(choice.message, 'function_call', None),
                "finish_reason": choice.finish_reason
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

class CanvasFunctionExecutor:
    """
    Function executor that bridges LLM function calls to canvas controller operations
    """
    
    def __init__(self, canvas_controller: CanvasController):
        """
        Initialize with a canvas controller instance
        
        Args:
            canvas_controller: CanvasController instance
        """
        self.controller = canvas_controller
    
    def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call on the canvas controller
        
        Args:
            function_name: Name of function to execute
            arguments: Function arguments
            
        Returns:
            Function execution result
        """
        print(f"🔧 EXECUTING: {function_name}({arguments})")
        
        try:
            if function_name == "create_container":
                result = self.controller.create_container(
                    container_id=arguments["container_id"],
                    x=arguments["x"],
                    y=arguments["y"],
                    width=arguments["width"],
                    height=arguments["height"]
                )
                return {
                    "status": "success" if result else "error",
                    "result": f"Container '{arguments['container_id']}' created successfully" if result else "Failed to create container",
                    "function_name": function_name
                }
            
            elif function_name == "delete_container":
                result = self.controller.delete_container(arguments["container_id"])
                return {
                    "status": "success" if result else "error",
                    "result": f"Container '{arguments['container_id']}' deleted successfully" if result else "Failed to delete container",
                    "function_name": function_name
                }
            
            elif function_name == "modify_container":
                result = self.controller.modify_container(
                    container_id=arguments["container_id"],
                    x=arguments["x"],
                    y=arguments["y"],
                    width=arguments["width"],
                    height=arguments["height"]
                )
                return {
                    "status": "success" if result else "error",
                    "result": f"Container '{arguments['container_id']}' modified successfully" if result else "Failed to modify container",
                    "function_name": function_name
                }
            
            elif function_name == "get_canvas_state":
                state = self.controller.get_current_state()
                return {
                    "status": "success",
                    "result": state,
                    "function_name": function_name
                }
            
            elif function_name == "clear_canvas":
                result = self.controller.clear_canvas()
                return {
                    "status": "success" if result else "error",
                    "result": "Canvas cleared successfully" if result else "Failed to clear canvas",
                    "function_name": function_name
                }
            
            elif function_name == "take_screenshot":
                filename = arguments.get("filename")
                screenshot_path = self.controller.take_screenshot(filename)
                return {
                    "status": "success" if screenshot_path else "error",
                    "result": f"Screenshot saved: {screenshot_path}" if screenshot_path else "Failed to take screenshot",
                    "function_name": function_name
                }
            
            elif function_name == "get_canvas_size":
                size = self.controller.get_canvas_size()
                return {
                    "status": "success",
                    "result": f"Canvas size: {size['width']}x{size['height']} pixels",
                    "canvas_size": size,
                    "function_name": function_name
                }
            
            elif function_name == "edit_canvas_size":
                try:
                    # Use JavaScript to change canvas size
                    success = self.controller.driver.execute_script(f"""
                        const canvas = document.getElementById('canvas');
                        canvas.style.width = '{arguments['width']}px';
                        canvas.style.height = '{arguments['height']}px';
                        return true;
                    """)
                    return {
                        "status": "success" if success else "error",
                        "result": f"Canvas resized to {arguments['width']}x{arguments['height']} pixels" if success else "Failed to resize canvas",
                        "function_name": function_name
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "result": f"Error resizing canvas: {str(e)}",
                        "function_name": function_name
                    }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown function: {function_name}",
                    "available_functions": ["create_container", "delete_container", "modify_container", 
                                          "get_canvas_state", "clear_canvas", "take_screenshot", 
                                          "get_canvas_size", "edit_canvas_size"]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error executing {function_name}: {str(e)}",
                "function_name": function_name
            }

class CanvasChatbot:
    """
    Main chatbot class that orchestrates LLM and canvas operations
    """
    
    def __init__(self, headless: bool = False, max_function_calls: int = 10):
        """
        Initialize the chatbot
        
        Args:
            headless: Whether to run browser in headless mode
            max_function_calls: Maximum function calls per user message
        """
        self.headless = headless
        self.canvas_controller = None
        self.llm_client = None
        self.function_executor = None
        self.conversation_history = []
        self.max_function_calls_per_turn = max_function_calls
        
    def initialize(self):
        """Initialize all components"""
        print("🤖 Initializing Canvas Chatbot...")
        
        # Initialize canvas controller
        print("🔧 Starting browser and canvas...")
        self.canvas_controller = CanvasController(headless=self.headless)
        
        # Initialize LLM client
        print("🧠 Connecting to OpenAI...")
        self.llm_client = CanvasLLMClient()
        
        # Initialize function executor
        self.function_executor = CanvasFunctionExecutor(self.canvas_controller)
        
        print("✅ Chatbot initialized successfully!")
        print("💡 You can now give me commands to control the canvas.")
        print("💡 Try: 'Create a container at position 100,100 with size 200x150'")
        print("💡 Type 'help' for more examples or 'quit' to exit.")
    
    def process_user_message(self, user_message: str) -> str:
        """
        Process a user message with LLM function calling
        
        Args:
            user_message: User's message
            
        Returns:
            Assistant's response
        """
        # Add system message if this is the first message
        messages = []
        if not self.conversation_history:
            messages.append({
                "role": "system",
                "content": self.llm_client.system_message
            })
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        function_calls_made = 0
        
        while function_calls_made < self.max_function_calls_per_turn:
            # Get LLM response
            response = self.llm_client.chat_completion(
                messages=messages,
                functions=self.llm_client.get_function_schemas()
            )
            
            if response["status"] != "success":
                return f"❌ Error: {response.get('error', 'Unknown error')}"
            
            message = response["message"]
            
            # Check if LLM wants to call a function
            if hasattr(message, 'function_call') and message.function_call:
                function_call = message.function_call
                function_name = function_call.name
                
                try:
                    function_args = json.loads(function_call.arguments)
                except json.JSONDecodeError as e:
                    return f"❌ Error: Invalid function arguments: {str(e)}"
                
                # Execute the function
                function_result = self.function_executor.execute_function_call(
                    function_name, function_args
                )
                
                # Add assistant message with function call
                messages.append({
                    "role": "assistant",
                    "content": "",
                    "function_call": {
                        "name": function_name,
                        "arguments": function_call.arguments
                    }
                })
                
                # Add function result
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_result)
                })
                
                function_calls_made += 1
                
                # If function failed critically, break
                if function_result["status"] == "error":
                    break
            
            else:
                # No function call, LLM provided final response
                final_response = message.content or "Operation completed."
                
                # Update conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": user_message
                })
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": final_response
                })
                
                # Keep conversation history manageable
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                return final_response
        
        return f"⚠️ Reached maximum function calls limit ({self.max_function_calls_per_turn}). Some operations may be incomplete. Try breaking your request into smaller steps or increase the limit."
    
    def show_help(self):
        """Show help information"""
        help_text = f"""
🎯 CANVAS CHATBOT HELP

Available Commands:
• Create containers: "Create a container called 'chart1' at 100,100 with size 300x200"
• Delete containers: "Delete the container named 'chart1'"
• Modify containers: "Move container 'chart1' to position 200,150 and resize to 400x250"
• View canvas: "Show me the current canvas state"
• Clear canvas: "Clear all containers"
• Take screenshot: "Take a screenshot and save it as 'my_canvas.png'"
• Canvas size: "What's the current canvas size?" or "Resize canvas to 1000x800"

Natural Language Examples:
• "Put a small container in the top left corner"
• "Create three containers side by side"
• "Make a large container in the center"
• "Remove all containers and start fresh"
• "Show me what's on the canvas right now"

Tips:
• Be specific about positions (x,y coordinates) and sizes (width x height)
• Container IDs should be unique strings
• Canvas coordinates start at (0,0) in the top-left corner
• The system will auto-adjust containers to fit within canvas bounds
• Containers automatically avoid overlapping with existing ones
• For complex operations, break requests into smaller steps
• Use 'set limit X' to adjust function call limit (current: {self.max_function_calls_per_turn})

Type 'quit' to exit the chatbot.
        """
        print(help_text)
    
    def run(self):
        """Main chatbot loop"""
        try:
            self.initialize()
            
            print("\n" + "="*60)
            print("🎨 CANVAS CONTROL CHATBOT")
            print("="*60)
            
            while True:
                try:
                    user_input = input("\n💬 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        print("👋 Goodbye!")
                        break
                    
                    if user_input.lower() in ['help', '?']:
                        self.show_help()
                        continue
                    
                    # Handle limit adjustment command
                    if user_input.lower().startswith('set limit '):
                        try:
                            new_limit = int(user_input.split()[-1])
                            if 1 <= new_limit <= 50:
                                self.max_function_calls_per_turn = new_limit
                                print(f"✅ Function call limit set to {new_limit}")
                            else:
                                print("❌ Limit must be between 1 and 50")
                        except ValueError:
                            print("❌ Invalid limit. Use: 'set limit 15'")
                        continue
                    
                    print("🤖 Assistant: ", end="", flush=True)
                    response = self.process_user_message(user_input)
                    print(response)
                    
                except KeyboardInterrupt:
                    print("\n\n⚠️ Interrupted by user.")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {str(e)}")
                    print("Please try again or type 'help' for assistance.")
        
        finally:
            if self.canvas_controller:
                print("\n🔒 Closing browser...")
                self.canvas_controller.close()

def main():
    """Main entry point"""
    print("🚀 Starting Canvas Control Chatbot...")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key in a .env file or environment variable.")
        return
    
    # Ask about headless mode
    headless_input = input("Run browser in headless mode? (y/N): ").strip().lower()
    headless = headless_input == 'y'
    
    # Create and run chatbot
    chatbot = CanvasChatbot(headless=headless)
    chatbot.run()

if __name__ == "__main__":
    main() 