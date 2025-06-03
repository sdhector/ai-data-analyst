"""
Generic Function Executor for AI Data Analyst

This module provides a reusable function execution system adapted from lesson-06
for data analysis and visualization functions.
"""

import json
from typing import Dict, Any, Callable, List
from dotenv import load_dotenv
import os
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class FunctionExecutor:
    """
    Generic function executor that can work with any function registry.
    
    This is the reusable component adapted for data analysis functions.
    """
    
    def __init__(self, function_registry: Dict[str, Callable], function_schemas: List[Dict]):
        """
        Initialize with a function registry and schemas
        
        Args:
            function_registry: Dictionary mapping function names to function objects
            function_schemas: List of OpenAI function schemas
        """
        self.function_registry = function_registry
        self.function_schemas = function_schemas
    
    def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call - this is the core magic!
        
        Args:
            function_name: Name of function to execute (from LLM)
            arguments: Arguments to pass to function (from LLM)
        
        Returns:
            Result of function execution
        """
        logger.info(f"Executing function: {function_name} with arguments: {arguments}")
        
        # Check if function exists
        if function_name not in self.function_registry:
            return {
                "error": f"Function '{function_name}' not found",
                "available_functions": list(self.function_registry.keys()),
                "status": "error"
            }
        
        try:
            # Get the actual function object (the magic line!)
            function_to_call = self.function_registry[function_name]
            
            # Execute it with LLM-provided arguments (the other magic line!)
            result = function_to_call(**arguments)
            
            logger.info(f"Function {function_name} executed successfully. Result: {result}")
            return result
            
        except Exception as e:
            # Log the error with stack trace
            logger.error(
                f"Error executing function '{function_name}' with arguments '{arguments}'. Error: {e}",
                exc_info=True
            )
            # The error_result dictionary is for the caller, ensure it's constructed and returned
            error_result = {
                "error": f"Error executing {function_name}: {str(e)}", # User-facing error
                "function_name": function_name,
                "arguments": arguments, # Be cautious with sensitive/large args in returned payload
                "status": "error"
            }
            return error_result
    
    def get_available_functions(self) -> List[str]:
        """Get list of available function names"""
        return list(self.function_registry.keys())
    
    def get_function_schemas(self) -> List[Dict]:
        """Get function schemas for LLM"""
        return self.function_schemas
    
    def is_function_available(self, function_name: str) -> bool:
        """Check if a function is available"""
        return function_name in self.function_registry

class LLMFunctionCaller:
    """
    Complete LLM function calling system using the generic executor.
    
    This handles the full workflow: LLM -> Function Call -> Result -> LLM
    Adapted for data analysis and visualization use cases.
    """
    
    def __init__(self, function_executor: FunctionExecutor, openai_client=None):
        """
        Initialize with a function executor and optional OpenAI client
        
        Args:
            function_executor: FunctionExecutor instance
            openai_client: OpenAI client (will create one if not provided)
        """
        self.executor = function_executor
        
        if openai_client is None:
            from openai import OpenAI
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.client = openai_client
    
    def chat_with_functions(self, user_message: str, model: str = "gpt-3.5-turbo", 
                          conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Complete function calling workflow for data analysis
        
        Args:
            user_message: User's message
            model: OpenAI model to use
            conversation_history: Previous conversation messages
        
        Returns:
            Dictionary with response and any function results
        """
        logger.info(f"User message: {user_message}")
        
        # Build conversation with history
        messages = [
            {
                "role": "system",
                "content": """You are an AI Data Analyst assistant. You can help users analyze data and create visualizations.

Available capabilities:
- Load and analyze sample datasets
- Create various types of charts (line, bar, scatter, histogram)
- Create data tables and summaries
- Filter, group, and sort data
- Manage visualization containers in a grid layout

When users ask for data analysis or visualizations, use the provided functions to help them.
Always be helpful and explain what you're doing."""
            }
        ]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Send to LLM with available functions
        logger.info("Sending request to LLM...")
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            functions=self.executor.get_function_schemas(),
            function_call="auto"
        )
        
        assistant_message = response.choices[0].message
        function_results = []
        
        # Check if LLM wants to call a function
        if assistant_message.function_call:
            logger.info("LLM requested a function call.")
            
            # Extract function call details
            function_name = assistant_message.function_call.name
            function_args = json.loads(assistant_message.function_call.arguments)
            
            logger.info(f"Function to call: {function_name}")
            logger.info(f"Function arguments: {function_args}")
            
            # Execute the function using our generic executor!
            function_result = self.executor.execute_function_call(function_name, function_args)
            function_results.append({
                "function_name": function_name,
                "arguments": function_args,
                "result": function_result
            })
            
            # Continue conversation with function result
            messages.append(assistant_message)
            messages.append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(function_result)
            })
            
            # Get final response from LLM
            logger.info("Sending function result back to LLM...")
            final_response = self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            
            final_answer = final_response.choices[0].message.content
            logger.info(f"LLM final response: {final_answer}")
            
            return {
                "response": final_answer,
                "function_calls": function_results,
                "conversation": messages,
                "status": "success"
            }
        
        else:
            # No function call needed
            direct_answer = assistant_message.content
            logger.info(f"LLM direct response: {direct_answer}")
            
            return {
                "response": direct_answer,
                "function_calls": [],
                "conversation": messages,
                "status": "success"
            }

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_function_caller_from_registry(function_registry: Dict[str, Callable], 
                                       function_schemas: List[Dict]) -> LLMFunctionCaller:
    """
    Convenience function to create a complete function calling system
    from a registry and schemas.
    
    Args:
        function_registry: Dictionary of functions
        function_schemas: List of OpenAI schemas
    
    Returns:
        Ready-to-use LLMFunctionCaller
    """
    executor = FunctionExecutor(function_registry, function_schemas)
    return LLMFunctionCaller(executor)

def test_function_execution(function_registry: Dict[str, Callable], 
                          function_name: str, 
                          arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test function execution without LLM (for debugging)
    
    Args:
        function_registry: Dictionary of functions
        function_name: Function to test
        arguments: Arguments to pass
    
    Returns:
        Function result
    """
    executor = FunctionExecutor(function_registry, [])
    return executor.execute_function_call(function_name, arguments) 