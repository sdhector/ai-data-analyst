"""
Canvas Chatbot for Core New Architecture

Main chatbot class that orchestrates LLM and canvas operations using the new modular architecture.
Currently supports only canvas size operations as the first implementation.
"""

import json
import asyncio
import logging
import os
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.llm_client import coreLLMClient
from core.function_executor import coreFunctionExecutor
from core.canvas_bridge import canvas_bridge
from core.utilities import (
    RequestTracker,
    log_request_start,
    log_request_end,
    log_component_entry,
    log_component_exit,
    log_handover
)


class CoreChatbot:
    """
    Main chatbot class that orchestrates LLM and canvas operations using core_new architecture
    """
    
    def __init__(self):
        """Initialize the chatbot"""
        self.llm_client = None
        self.function_executor = None
        self.conversation_history = []
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.logger = logging.getLogger(__name__)
        
        if self.debug_mode:
            self.logger.info("[CHATBOT] Debug mode enabled for chatbot")
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all components"""
        try:
            # Initialize LLM client
            self.llm_client = coreLLMClient()
            
            # Initialize function executor
            self.function_executor = coreFunctionExecutor(self)
            
            print("[SUCCESS] Core New Chatbot components initialized successfully!")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize core_new chatbot components: {e}")
            raise
    
    async def process_user_message(self, user_message: str, conversation_id: str = None, allow_extended_iterations: bool = False) -> Dict[str, Any]:
        """
        Process a user message with LLM function calling using core_new architecture
        
        Args:
            user_message: User's message
            conversation_id: Optional conversation ID for context
            allow_extended_iterations: Allow more iterations for complex operations
            
        Returns:
            Dict with response and metadata
        """
        # Generate and set request ID
        request_id = RequestTracker.generate_request_id()
        RequestTracker.set_request_id(request_id)
        start_time = time.time()
        
        if self.debug_mode:
            self.logger.debug(f"[CHATBOT] 🚀 Processing user message: '{user_message}' (conversation_id: {conversation_id})")
        
        # Log request start
        log_request_start(request_id, user_message, conversation_id)
        log_component_entry("CHATBOT", "process_user_message", f"Message: '{user_message}'")
        
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
            max_iterations = 10 if allow_extended_iterations else 5
            iteration_count = 0
            
            # Check if user is requesting to continue from max iterations
            continue_keywords = ['continue', 'yes', 'keep going', 'more iterations', 'proceed']
            if any(keyword in user_message.lower() for keyword in continue_keywords):
                allow_extended_iterations = True
                max_iterations = 10
            
            while iteration_count < max_iterations:
                iteration_count += 1
                
                # Get LLM response
                if self.debug_mode:
                    self.logger.debug(f"[CHATBOT] 🤖 Calling LLM (iteration {iteration_count}/{max_iterations})")
                
                response = self.llm_client.chat_completion(
                    messages=messages,
                    functions=self.llm_client.get_function_schemas()
                )
                
                if self.debug_mode:
                    self.logger.debug(f"[CHATBOT] 🤖 LLM response status: {response['status']}")
                
                if response["status"] != "success":
                    return {
                        "success": False,
                        "message": f"[ERROR] Error: {response.get('error', 'Unknown error')}",
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat()
                    }
                
                message = response["message"]
                
                # Check if LLM wants to call a function (handle tools format)
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
                
                if function_calls_to_process:
                    if self.debug_mode:
                        self.logger.debug(f"[CHATBOT] 🔧 Processing {len(function_calls_to_process)} function call(s)")
                    
                    # Process each function call
                    for func_call in function_calls_to_process:
                        function_name = func_call['name']
                        
                        if self.debug_mode:
                            self.logger.debug(f"[CHATBOT] 📞 Function call: {function_name}({func_call['arguments']})")
                        
                        try:
                            function_args = json.loads(func_call['arguments'])
                        except json.JSONDecodeError as e:
                            return {
                                "success": False,
                                "message": f"[ERROR] Error: Invalid function arguments: {str(e)}",
                                "conversation_id": conversation_id,
                                "timestamp": datetime.now().isoformat()
                            }
                        
                        # Execute the function using core_new architecture
                        if self.debug_mode:
                            self.logger.debug(f"[CHATBOT] ⚡ Handing over to function executor: {function_name}")
                        
                        log_handover("CHATBOT", "FUNCTION_EXECUTOR", function_name, str(function_args))
                        
                        function_result = await self.function_executor.execute_function_call(
                            function_name, function_args
                        )
                        
                        if self.debug_mode:
                            self.logger.debug(f"[CHATBOT] ✅ Function executor returned: {function_result.get('status', 'unknown')}")
                        
                        log_component_exit("FUNCTION_EXECUTOR", function_name, function_result.get('status', 'unknown'))
                        
                        # Add assistant message with function call
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
                    
                    function_calls_made += 1
                    
                    # Enhanced error handling - let LLM handle errors gracefully
                    if function_result["status"] == "error":
                        error_context = f"Function {function_name} failed: {function_result.get('error', 'Unknown error')}"
                        if 'available_functions' in function_result:
                            error_context += f" Available functions: {', '.join(function_result['available_functions'])}"
                        print(f"[ERROR] {error_context}")
                        
                        # Continue to let LLM respond to the error
                
                else:
                    # No function calls, LLM provided a direct response
                    final_response = message.content if hasattr(message, 'content') else str(message)
                    
                    # Update conversation history
                    self.conversation_history.extend(messages[len(self.conversation_history):])
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": final_response
                    })
                    
                    # Log successful completion
                    duration_ms = (time.time() - start_time) * 1000
                    log_component_exit("CHATBOT", "process_user_message", "SUCCESS", f"Response generated")
                    log_request_end(request_id, True, duration_ms)
                    
                    return {
                        "success": True,
                        "message": final_response,
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat(),
                        "function_calls_made": function_calls_made,
                        "iterations": iteration_count,
                        "architecture": "core_new",
                        "request_id": request_id
                    }
            
            # Max iterations reached
            final_message = "I've reached the maximum number of iterations for this request. "
            if not allow_extended_iterations:
                final_message += "Would you like me to continue with more iterations? Just say 'continue' or 'yes'."
            else:
                final_message += "The operation may be too complex or there might be an issue. Please try rephrasing your request or ask for help."
            
            # Log max iterations reached
            duration_ms = (time.time() - start_time) * 1000
            log_component_exit("CHATBOT", "process_user_message", "MAX_ITERATIONS", f"Reached {max_iterations} iterations")
            log_request_end(request_id, True, duration_ms)
            
            return {
                "success": True,
                "message": final_message,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
                "function_calls_made": function_calls_made,
                "iterations": iteration_count,
                "max_iterations_reached": True,
                "architecture": "core_new",
                "request_id": request_id
            }
            
        except Exception as e:
            # Log error completion
            duration_ms = (time.time() - start_time) * 1000
            log_component_exit("CHATBOT", "process_user_message", "ERROR", str(e))
            log_request_end(request_id, False, duration_ms)
            
            return {
                "success": False,
                "message": f"[ERROR] Unexpected error: {str(e)}",
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
                "architecture": "core_new",
                "request_id": request_id
            }
    
    def get_help_text(self) -> str:
        """Get help text for available operations"""
        available_functions = self.function_executor.get_available_functions()
        
        help_text = """🎨 **AI Data Analyst - Core New Architecture (Phase 1)**

**Currently Available Operations:**
• **Canvas Dimension Management** - Set and get canvas dimensions with validation and feedback

**Canvas Dimension Examples:**
• "Set the canvas to 1200x800"
• "Make the canvas 1920 by 1080"  
• "Change canvas size to 800 width and 600 height"
• "What are the current canvas dimensions?"

**Features:**
✨ Direct dimension setting with positive integer validation
🛡️ Comprehensive error handling and user feedback
📊 Rich metadata including area, aspect ratio, and size categorization
🎯 Change tracking with before/after comparisons
📏 Detailed dimension analysis and recommendations

**Architecture Benefits:**
• Modular design for better maintainability
• Enhanced security with multiple validation layers
• Rich metadata and comprehensive error handling
• Optimized for AI integration and user experience

**Note:** This is Phase 1 of the new architecture. More operations will be added incrementally.

Type your request in natural language and I'll help you manage your canvas dimensions!"""
        
        return help_text
    
    def get_canvas_state(self) -> Dict[str, Any]:
        """Get current canvas state"""
        return canvas_bridge.get_canvas_state()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("[INFO] Core New conversation history cleared")
    
    def get_available_functions(self) -> List[str]:
        """Get list of available functions"""
        return self.function_executor.get_available_functions()


# Create global instance
core_chatbot = CoreChatbot() 