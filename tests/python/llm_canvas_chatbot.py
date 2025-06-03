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
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
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
- Control canvas behavior settings (auto-adjustment and overlap prevention)

Canvas specifications:
- Default size: 800x600 pixels (customizable)
- Coordinate system: Top-left origin (0,0)
- Position values: x, y coordinates in pixels
- Size values: width, height in pixels

Canvas behavior controls:
- Auto-adjustment: When enabled, containers automatically fit within canvas bounds
- Overlap prevention: When enabled, containers avoid overlapping with existing ones
- You can toggle these settings using toggle_auto_adjust and toggle_overlap_prevention functions
- Use get_canvas_settings to check current behavior settings

When users request canvas operations:
1. ALWAYS start by checking current canvas state with get_canvas_state() if you need to know existing containers
2. Use the appropriate function to perform the action
3. Always explain what you're doing
4. Provide feedback on the results
5. If a function fails, check the error message and try alternative approaches
6. Consider adjusting behavior settings if users want specific placement behavior
7. Always provide a final text response summarizing what was accomplished
8. Suggest next steps if helpful

Important guidelines:
- Container IDs must match exactly what exists on canvas (check with get_canvas_state first)
- When overlap prevention is enabled, containers may be automatically repositioned
- When auto-adjustment is enabled, containers may be resized to fit canvas bounds
- Always acknowledge when automatic adjustments occur

Be helpful, clear, and always confirm successful operations with a final summary."""
    
    def get_function_schemas(self) -> List[Dict]:
        """Get function schemas for canvas operations"""
        return [
            {
                "name": "create_container",
                "description": "Create a new container on the canvas at specified position and size. TIP: Consider calling get_canvas_state() first to check existing containers and avoid ID conflicts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "Unique identifier for the container. Must be unique - check existing containers with get_canvas_state() if needed."
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
                "description": "Delete a container from the canvas. IMPORTANT: Always call get_canvas_state() first to check existing container IDs before using this function.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID of the container to delete. Must match exactly an existing container ID from get_canvas_state()."
                        }
                    },
                    "required": ["container_id"]
                }
            },
            {
                "name": "modify_container",
                "description": "Modify an existing container's position and size. IMPORTANT: Always call get_canvas_state() first to check existing container IDs before using this function.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID of the container to modify. Must match exactly an existing container ID from get_canvas_state()."
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
                "description": "Get the current state of the canvas including all containers. ESSENTIAL: Call this function first before modifying or deleting containers to get accurate container IDs and positions.",
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
            },
            {
                "name": "toggle_auto_adjust",
                "description": "Enable or disable automatic container adjustment to fit within canvas bounds",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "True to enable auto-adjustment, False to disable"
                        }
                    },
                    "required": ["enabled"]
                }
            },
            {
                "name": "toggle_overlap_prevention",
                "description": "Enable or disable automatic overlap prevention for containers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "True to enable overlap prevention, False to allow overlapping"
                        }
                    },
                    "required": ["enabled"]
                }
            },
            {
                "name": "get_canvas_settings",
                "description": "Get current canvas behavior settings (auto-adjust and overlap prevention status)",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
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
                "temperature": 0.3,  # Lower temperature for more consistent function calling
                "max_tokens": 1000   # Ensure we don't hit token limits
            }
            
            if functions:
                # Convert functions to tools format for better compatibility
                tools = [{"type": "function", "function": func} for func in functions]
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            response = self.client.chat.completions.create(**request_params)
            choice = response.choices[0]
            
            return {
                "status": "success",
                "message": choice.message,
                "content": choice.message.content,
                "function_call": getattr(choice.message, 'function_call', None),
                "tool_calls": getattr(choice.message, 'tool_calls', None),
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
    
    def __init__(self, canvas_controller: CanvasController, chatbot_instance):
        """
        Initialize with a canvas controller instance
        
        Args:
            canvas_controller: CanvasController instance
            chatbot_instance: Reference to chatbot for accessing settings
        """
        self.controller = canvas_controller
        self.chatbot = chatbot_instance
    
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
                    height=arguments["height"],
                    auto_adjust=self.chatbot.auto_adjust_enabled,
                    avoid_overlap=self.chatbot.overlap_prevention_enabled
                )
                
                if result:
                    # Get the actual final state to report any adjustments
                    state = self.controller.get_current_state()
                    created_container = None
                    for container in state.get('containers', []):
                        if container['id'] == arguments["container_id"]:
                            created_container = container
                            break
                    
                    result_msg = f"Container '{arguments['container_id']}' created successfully"
                    if created_container:
                        actual_pos = f"at ({created_container['x']}, {created_container['y']})"
                        actual_size = f"with size {created_container['width']}x{created_container['height']}"
                        requested_pos = f"({arguments['x']}, {arguments['y']})"
                        requested_size = f"{arguments['width']}x{arguments['height']}"
                        
                        if (created_container['x'] != arguments['x'] or 
                            created_container['y'] != arguments['y']):
                            result_msg += f" (repositioned from {requested_pos} to {actual_pos} due to overlap prevention)"
                        else:
                            result_msg += f" {actual_pos}"
                            
                        if (created_container['width'] != arguments['width'] or 
                            created_container['height'] != arguments['height']):
                            result_msg += f" (resized from {requested_size} to {actual_size} due to auto-adjustment)"
                        else:
                            result_msg += f" {actual_size}"
                
                if not result:
                    # Check if it's an ID conflict
                    state = self.controller.get_current_state()
                    existing_ids = [c['id'] for c in state.get('containers', [])]
                    if arguments["container_id"] in existing_ids:
                        result_msg = f"Failed to create container '{arguments['container_id']}'. Container ID already exists. Existing containers: {', '.join(existing_ids)}. Use get_canvas_state() to check current containers and choose a unique ID."
                    else:
                        result_msg = "Failed to create container due to unknown error."
                
                return {
                    "status": "success" if result else "error",
                    "result": result_msg if result else "Failed to create container",
                    "function_name": function_name
                }
            
            elif function_name == "delete_container":
                result = self.controller.delete_container(arguments["container_id"])
                
                if result:
                    result_msg = f"Container '{arguments['container_id']}' deleted successfully"
                else:
                    # Check if container exists to provide better error message
                    state = self.controller.get_current_state()
                    existing_ids = [c['id'] for c in state.get('containers', [])]
                    if existing_ids:
                        result_msg = f"Failed to delete container '{arguments['container_id']}'. Container not found. Available containers: {', '.join(existing_ids)}. Use get_canvas_state() to check current containers."
                    else:
                        result_msg = f"Failed to delete container '{arguments['container_id']}'. No containers exist on canvas. Use get_canvas_state() to verify canvas state."
                
                return {
                    "status": "success" if result else "error",
                    "result": result_msg,
                    "function_name": function_name
                }
            
            elif function_name == "modify_container":
                result = self.controller.modify_container(
                    container_id=arguments["container_id"],
                    x=arguments["x"],
                    y=arguments["y"],
                    width=arguments["width"],
                    height=arguments["height"],
                    auto_adjust=self.chatbot.auto_adjust_enabled,
                    avoid_overlap=self.chatbot.overlap_prevention_enabled
                )
                
                if result:
                    # Get the actual final state to report any adjustments
                    state = self.controller.get_current_state()
                    modified_container = None
                    for container in state.get('containers', []):
                        if container['id'] == arguments["container_id"]:
                            modified_container = container
                            break
                    
                    result_msg = f"Container '{arguments['container_id']}' modified successfully"
                    if modified_container:
                        actual_pos = f"to ({modified_container['x']}, {modified_container['y']})"
                        actual_size = f"with size {modified_container['width']}x{modified_container['height']}"
                        requested_pos = f"({arguments['x']}, {arguments['y']})"
                        requested_size = f"{arguments['width']}x{arguments['height']}"
                        
                        if (modified_container['x'] != arguments['x'] or 
                            modified_container['y'] != arguments['y']):
                            result_msg += f" (repositioned from requested {requested_pos} to {actual_pos} due to overlap prevention)"
                        else:
                            result_msg += f" {actual_pos}"
                            
                        if (modified_container['width'] != arguments['width'] or 
                            modified_container['height'] != arguments['height']):
                            result_msg += f" (resized from requested {requested_size} to {actual_size} due to auto-adjustment)"
                        else:
                            result_msg += f" {actual_size}"
                else:
                    # Check if container exists to provide better error message
                    state = self.controller.get_current_state()
                    existing_ids = [c['id'] for c in state.get('containers', [])]
                    if existing_ids:
                        result_msg = f"Failed to modify container '{arguments['container_id']}'. Container not found. Available containers: {', '.join(existing_ids)}. Use get_canvas_state() to check current containers."
                    else:
                        result_msg = f"Failed to modify container '{arguments['container_id']}'. No containers exist on canvas. Use get_canvas_state() to verify canvas state."
                
                return {
                    "status": "success" if result else "error",
                    "result": result_msg if result else f"Failed to modify container '{arguments['container_id']}'",
                    "function_name": function_name
                }
            
            elif function_name == "get_canvas_state":
                state = self.controller.get_current_state()
                
                # Format the state information for better LLM understanding
                containers = state.get('containers', [])
                if containers:
                    container_summary = []
                    for container in containers:
                        summary = f"'{container['id']}': position ({container['x']}, {container['y']}), size {container['width']}x{container['height']}"
                        container_summary.append(summary)
                    
                    formatted_result = {
                        "canvas_size": state.get('canvas_size', 'Unknown'),
                        "container_count": len(containers),
                        "containers": containers,
                        "summary": f"Canvas has {len(containers)} container(s): " + "; ".join(container_summary)
                    }
                else:
                    formatted_result = {
                        "canvas_size": state.get('canvas_size', 'Unknown'),
                        "container_count": 0,
                        "containers": [],
                        "summary": "Canvas is empty (no containers)"
                    }
                
                return {
                    "status": "success",
                    "result": formatted_result,
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
            
            elif function_name == "toggle_auto_adjust":
                self.chatbot.auto_adjust_enabled = arguments["enabled"]
                status = "enabled" if arguments["enabled"] else "disabled"
                return {
                    "status": "success",
                    "result": f"Auto-adjustment {status}. Containers will {'automatically fit within canvas bounds' if arguments['enabled'] else 'be placed at exact positions (may extend beyond canvas)'}.",
                    "function_name": function_name
                }
            
            elif function_name == "toggle_overlap_prevention":
                self.chatbot.overlap_prevention_enabled = arguments["enabled"]
                status = "enabled" if arguments["enabled"] else "disabled"
                return {
                    "status": "success",
                    "result": f"Overlap prevention {status}. Containers will {'automatically avoid overlapping' if arguments['enabled'] else 'be allowed to overlap'}.",
                    "function_name": function_name
                }
            
            elif function_name == "get_canvas_settings":
                return {
                    "status": "success",
                    "result": {
                        "auto_adjust": self.chatbot.auto_adjust_enabled,
                        "overlap_prevention": self.chatbot.overlap_prevention_enabled,
                        "summary": f"Auto-adjust: {'ON' if self.chatbot.auto_adjust_enabled else 'OFF'}, Overlap prevention: {'ON' if self.chatbot.overlap_prevention_enabled else 'OFF'}"
                    },
                    "function_name": function_name
                }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown function: {function_name}",
                    "available_functions": ["create_container", "delete_container", "modify_container", 
                                          "get_canvas_state", "clear_canvas", "take_screenshot", 
                                          "get_canvas_size", "edit_canvas_size", "toggle_auto_adjust",
                                          "toggle_overlap_prevention", "get_canvas_settings"]
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
    
    def __init__(self, headless: bool = False):
        """
        Initialize the chatbot
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.canvas_controller = None
        self.llm_client = None
        self.function_executor = None
        self.conversation_history = []
        
        # Canvas behavior settings that LLM can control
        self.auto_adjust_enabled = True
        self.overlap_prevention_enabled = True
        
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
        self.function_executor = CanvasFunctionExecutor(self.canvas_controller, self)
        
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
        max_iterations = 50  # Prevent infinite loops
        iteration_count = 0
        
        while iteration_count < max_iterations:
            iteration_count += 1
            
            # Get LLM response
            response = self.llm_client.chat_completion(
                messages=messages,
                functions=self.llm_client.get_function_schemas()
            )
            
            if response["status"] != "success":
                return f"❌ Error: {response.get('error', 'Unknown error')}"
            
            message = response["message"]
            
            # Check if LLM wants to call a function (handle both old and new API formats)
            function_calls_to_process = []
            
            # Handle new tools format
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.type == 'function':
                        function_calls_to_process.append({
                            'id': tool_call.id,
                            'name': tool_call.function.name,
                            'arguments': tool_call.function.arguments
                        })
            
            # Handle old function_call format (fallback)
            elif hasattr(message, 'function_call') and message.function_call:
                function_calls_to_process.append({
                    'id': None,
                    'name': message.function_call.name,
                    'arguments': message.function_call.arguments
                })
            
            if function_calls_to_process:
                # Process each function call
                for func_call in function_calls_to_process:
                    function_name = func_call['name']
                    
                    try:
                        function_args = json.loads(func_call['arguments'])
                    except json.JSONDecodeError as e:
                        return f"❌ Error: Invalid function arguments: {str(e)}"
                    
                    # Execute the function
                    function_result = self.function_executor.execute_function_call(
                        function_name, function_args
                    )
                    
                    # Add assistant message with function call
                    if func_call['id']:  # New tools format
                        messages.append({
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [{
                                "id": func_call['id'],
                                "type": "function",
                                "function": {
                                    "name": function_name,
                                    "arguments": func_call['arguments']
                                }
                            }]
                        })
                        
                        # Add tool result
                        messages.append({
                            "role": "tool",
                            "tool_call_id": func_call['id'],
                            "content": json.dumps(function_result)
                        })
                    else:  # Old function_call format
                        messages.append({
                            "role": "assistant",
                            "content": "",
                            "function_call": {
                                "name": function_name,
                                "arguments": func_call['arguments']
                            }
                        })
                        
                        # Add function result
                        messages.append({
                            "role": "function",
                            "name": function_name,
                            "content": json.dumps(function_result)
                        })
                
                function_calls_made += 1
                
                # Check if we should prompt user to continue after 25 calls
                if function_calls_made >= 25:
                    print(f"\n⚠️ Made {function_calls_made} function calls.")
                    continue_choice = input("🤔 Continue with more function calls? (y/N): ").strip().lower()
                    if continue_choice != 'y':
                        return f"⏹️ Stopped after {function_calls_made} function calls at user request."
                
                # Enhanced error handling - don't break immediately, let LLM handle errors
                if function_result["status"] == "error":
                    # Add error context to help LLM understand what went wrong
                    error_context = f"Function {function_name} failed: {function_result.get('error', 'Unknown error')}"
                    if 'available_functions' in function_result:
                        error_context += f" Available functions: {', '.join(function_result['available_functions'])}"
                    print(f"❌ {error_context}")
                    
                    # Continue to let LLM respond to the error rather than breaking
            
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
        
        # If we exit the loop without a proper response, determine why
        if iteration_count >= max_iterations:
            print(f"⚠️ Reached maximum iterations ({max_iterations}). Requesting final response...")
            summary_prompt = "You have reached the maximum number of iterations. Please provide a summary of the operations performed and their results. Do not make any more function calls."
        else:
            print("⚠️ Function calling loop ended unexpectedly. Requesting final response...")
            summary_prompt = "Please provide a summary of the operations performed and their results. Do not make any more function calls."
        
        # Add a message asking for summary
        messages.append({
            "role": "system",
            "content": summary_prompt
        })
        
        # Get final response without function calling
        final_response = self.llm_client.chat_completion(messages=messages, functions=None)
        
        if final_response["status"] == "success" and final_response["content"]:
            return final_response["content"]
        else:
            return f"⚠️ Operations completed but encountered issues. Made {function_calls_made} function calls in {iteration_count} iterations."
    
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
• Behavior control: "Turn off overlap prevention" or "Enable auto-adjustment"
• Check settings: "What are the current canvas settings?"

Natural Language Examples:
• "Put a small container in the top left corner"
• "Create three containers side by side"
• "Make a large container in the center"
• "Remove all containers and start fresh"
• "Show me what's on the canvas right now"
• "Allow containers to overlap"
• "Turn off auto-adjustment so I can place containers exactly where I want"

Tips:
• Be specific about positions (x,y coordinates) and sizes (width x height)
• Container IDs should be unique strings
• Canvas coordinates start at (0,0) in the top-left corner
• Auto-adjustment and overlap prevention are enabled by default
• You can control these behaviors through natural language commands
• For precise positioning, consider disabling auto-adjustment
• For overlapping layouts, disable overlap prevention

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