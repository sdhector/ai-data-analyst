"""
Function Executor for Core Architecture

Bridges LLM function calls to the modular architecture.
Currently supports only canvas size operations as the first implementation.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from .registry import execute_canvas_management_tool
from .utilities import (
    log_component_entry,
    log_component_exit,
    log_handover,
    user_feedback_manager
)


class coreFunctionExecutor:
    """
    Function executor that bridges LLM function calls to core  operations
    """
    
    def __init__(self, chatbot_instance=None):
        """
        Initialize with a reference to the chatbot instance
        
        Args:
            chatbot_instance: Reference to chatbot for accessing settings
        """
        self.chatbot = chatbot_instance
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.logger = logging.getLogger(__name__)
        
        # Available functions in core  (currently only canvas management operations)
        self.available_functions = [
            "set_canvas_dimensions",
            "get_canvas_dimensions",
            "create_container"
        ]
        
        if self.debug_mode:
            self.logger.info(f"[FUNCTION_EXECUTOR] Initialized with functions: {self.available_functions}")
    
    async def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call using the core  architecture
        
        Args:
            function_name: Name of function to execute
            arguments: Function arguments
            
        Returns:
            Function execution result
        """
        print(f"[CORE ] EXECUTING: {function_name}({arguments})")
        
        if self.debug_mode:
            self.logger.debug(f"[FUNCTION_EXECUTOR] 🎯 Received function call: {function_name}")
            self.logger.debug(f"[FUNCTION_EXECUTOR] 📋 Arguments: {arguments}")
        
        log_component_entry("FUNCTION_EXECUTOR", "execute_function_call", f"{function_name}({arguments})")
        
        # Send user feedback: tool execution started
        await user_feedback_manager.notify_tool_start(function_name, arguments)
        
        try:
            if function_name in self.available_functions:
                if self.debug_mode:
                    self.logger.debug(f"[FUNCTION_EXECUTOR] ✅ Function {function_name} is available")
                    self.logger.debug(f"[FUNCTION_EXECUTOR] 🔄 Handing over to registry: execute_canvas_management_tool")
                
                log_handover("FUNCTION_EXECUTOR", "REGISTRY", function_name, str(arguments))
                
                # Execute using the canvas management tool
                result = await execute_canvas_management_tool(function_name, arguments)
                
                if self.debug_mode:
                    self.logger.debug(f"[FUNCTION_EXECUTOR] 🏁 Registry returned: {result.get('status', 'unknown')}")
                
                # Send user feedback based on result
                if result.get('status') == 'success':
                    await user_feedback_manager.notify_tool_success(function_name, result)
                else:
                    error_msg = result.get('error', 'Unknown error occurred')
                    await user_feedback_manager.notify_tool_error(function_name, error_msg)
                
                log_component_exit("FUNCTION_EXECUTOR", "execute_function_call", result.get('status', 'unknown'))
                return result
            
            else:
                error_msg = f"Function '{function_name}' not available in core architecture"
                await user_feedback_manager.notify_tool_error(function_name, error_msg)
                
                log_component_exit("FUNCTION_EXECUTOR", "execute_function_call", "ERROR", f"Function not available: {function_name}")
                return {
                    "status": "error",
                    "error": error_msg,
                    "available_functions": self.available_functions,
                    "message": f"The function '{function_name}' is not yet implemented in the architecture. Currently available: {', '.join(self.available_functions)}"
                }
                
        except Exception as e:
            error_msg = f"Error executing {function_name}: {str(e)}"
            await user_feedback_manager.notify_tool_error(function_name, error_msg)
            
            log_component_exit("FUNCTION_EXECUTOR", "execute_function_call", "EXCEPTION", str(e))
            return {
                "status": "error",
                "error": error_msg,
                "function_name": function_name
            }
    
    def get_available_functions(self) -> List[str]:
        """Get list of available function names"""
        return self.available_functions.copy()
    
    def is_function_available(self, function_name: str) -> bool:
        """Check if a function is available in core """
        return function_name in self.available_functions 