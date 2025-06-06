"""
Canvas Chatbot Orchestrator

Main chatbot class that orchestrates LLM and canvas operations for the v0.1 backend.
Based on the proven implementation from tests/python/llm_canvas_chatbot.py.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.llm_client import CanvasLLMClient
from core.function_executor import CanvasFunctionExecutor
from core.canvas_bridge import canvas_bridge


class CanvasChatbot:
    """
    Main chatbot class that orchestrates LLM and canvas operations
    """
    
    def __init__(self):
        """Initialize the chatbot"""
        self.llm_client = None
        self.function_executor = None
        self.conversation_history = []
        
        # Canvas behavior settings that LLM can control
        self.auto_adjust_enabled = True
        self.overlap_prevention_enabled = False
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all components"""
        try:
            # Initialize LLM client
            self.llm_client = CanvasLLMClient()
            
            # Initialize function executor
            self.function_executor = CanvasFunctionExecutor(self)
            
            print("[SUCCESS] Chatbot components initialized successfully!")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize chatbot components: {e}")
            raise
    
    async def process_user_message(self, user_message: str, conversation_id: str = None, allow_extended_iterations: bool = False) -> Dict[str, Any]:
        """
        Process a user message with LLM function calling
        
        Args:
            user_message: User's message
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dict with response and metadata
        """
        try:
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
            max_iterations = 10 if allow_extended_iterations else 5  # Allow more iterations if requested
            iteration_count = 0
            
            # Check if user is requesting to continue from max iterations
            continue_keywords = ['continue', 'yes', 'keep going', 'more iterations', 'proceed']
            if any(keyword in user_message.lower() for keyword in continue_keywords):
                allow_extended_iterations = True
                max_iterations = 10
            
            while iteration_count < max_iterations:
                iteration_count += 1
                
                # Get LLM response
                response = self.llm_client.chat_completion(
                    messages=messages,
                    functions=self.llm_client.get_function_schemas()
                )
                
                if response["status"] != "success":
                    return {
                        "success": False,
                        "message": f"[ERROR] Error: {response.get('error', 'Unknown error')}",
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat()
                    }
                
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
                            return {
                                "success": False,
                                "message": f"[ERROR] Error: Invalid function arguments: {str(e)}",
                                "conversation_id": conversation_id,
                                "timestamp": datetime.now().isoformat()
                            }
                        
                        # Execute the function
                        function_result = await self.function_executor.execute_function_call(
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
                    
                    # Enhanced error handling - don't break immediately, let LLM handle errors
                    if function_result["status"] == "error":
                        # Add error context to help LLM understand what went wrong
                        error_context = f"Function {function_name} failed: {function_result.get('error', 'Unknown error')}"
                        if 'available_functions' in function_result:
                            error_context += f" Available functions: {', '.join(function_result['available_functions'])}"
                        print(f"[ERROR] {error_context}")
                        
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
                    
                    return {
                        "success": True,
                        "message": final_response,
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat(),
                        "function_calls_made": function_calls_made,
                        "iterations": iteration_count
                    }
            
            # If we exit the loop without a proper response, determine why
            if iteration_count >= max_iterations:
                print(f"[WARNING] Reached maximum iterations ({max_iterations}). Requesting final response...")
                
                # Return a response that prompts the user to continue or stop
                return {
                    "success": True,
                    "message": f"[WARNING] **Maximum iterations reached ({max_iterations})**\n\n" +
                              f"I've made {function_calls_made} function calls while processing your request. " +
                              f"Some operations may still be in progress.\n\n" +
                              f"**Would you like me to:**\n" +
                              f"• Continue with more iterations? (say 'continue' or 'yes')\n" +
                              f"• Stop here and provide a summary? (say 'stop' or 'summary')\n" +
                              f"• Try a different approach? (describe what you'd like)\n\n" +
                              f"*Note: You can also ask me to check the current canvas state to see what was accomplished.*",
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat(),
                    "function_calls_made": function_calls_made,
                    "iterations": iteration_count,
                    "status": "max_iterations_reached",
                    "requires_user_input": True
                }
            else:
                print("[WARNING] Function calling loop ended unexpectedly. Requesting final response...")
                summary_prompt = "Please provide a summary of the operations performed and their results. Do not make any more function calls."
                
                # Add a message asking for summary
                messages.append({
                    "role": "system",
                    "content": summary_prompt
                })
                
                # Get final response without function calling
                final_response = self.llm_client.chat_completion(messages=messages, functions=None)
                
                if final_response["status"] == "success" and final_response["content"]:
                    return {
                        "success": True,
                        "message": final_response["content"],
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat(),
                        "function_calls_made": function_calls_made,
                        "iterations": iteration_count,
                        "warning": "Function calling loop ended unexpectedly"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"[WARNING] Operations completed but encountered issues. Made {function_calls_made} function calls in {iteration_count} iterations.",
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat()
                    }
                
        except Exception as e:
            print(f"[ERROR] Error processing user message: {e}")
            return {
                "success": False,
                "message": f"[ERROR] Error processing message: {str(e)}",
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_help_text(self) -> str:
        """Get help information"""
        return """
[TARGET] CANVAS CHATBOT HELP

Available Commands:
• Create containers: "Create a container called 'chart1' at 100,100 with size 300x200"
• Delete containers: "Delete the container named 'chart1'"
• Modify containers: "Move container 'chart1' to position 200,150 and resize to 400x250"
• View canvas: "Show me the current canvas state"
• Clear canvas: "Clear all containers"
• Take screenshot: "Take a screenshot and save it as 'my_canvas.png'"
• Canvas size: "What's the current canvas size?" or "Resize canvas to 1000x800"
• Check settings: "What are the current canvas settings?"
• Check container content: "Check what's in container 'chart1'"

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
• Auto-adjustment and overlap prevention are enabled by default
• You can control these behaviors through natural language commands
• For precise positioning, consider disabling auto-adjustment
• For overlapping layouts, disable overlap prevention

Canvas specifications:
• Default size: 800x600 pixels (customizable)
• Coordinate system: Top-left origin (0,0)
• Position values: x, y coordinates in pixels
• Size values: width, height in pixels
        """
    
    def get_canvas_state(self) -> Dict[str, Any]:
        """Get current canvas state"""
        return canvas_bridge.get_canvas_state()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🧹 Conversation history cleared")


# Global instance
chatbot = CanvasChatbot() 