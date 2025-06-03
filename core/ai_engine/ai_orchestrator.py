"""
AI Orchestrator

This is the main orchestration component that coordinates all AI engine modules
and provides the primary interface for the AI Data Analyst application.
"""

import json
from typing import Dict, Any, List, Optional
import logging
from .llm_client import LLMClient
from .conversation_manager import ConversationManager
from .function_caller import FunctionCaller

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Main AI orchestration component that coordinates LLM, conversation management,
    and function calling for the AI Data Analyst.
    """
    
    def __init__(self, 
                 api_key: str = None,
                 model: str = None,
                 max_tokens: int = None,
                 temperature: float = 0.7,
                 max_context_length: int = 4000):
        """
        Initialize the AI orchestrator
        
        Args:
            api_key: OpenAI API key
            model: LLM model to use
            max_tokens: Maximum tokens per response
            temperature: Response creativity (0.0-1.0)
            max_context_length: Maximum context window length
        """
        # Initialize components
        self.llm_client = LLMClient(
            api_key=api_key,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        self.conversation_manager = ConversationManager(
            max_context_length=max_context_length
        )
        
        self.function_caller = FunctionCaller()
        
        # Configuration
        self.enable_function_calling = True
        self.auto_execute_functions = True
        self.max_function_calls_per_turn = 5
        
    def process_request(self, 
                       user_message: str, 
                       conversation_id: str = None,
                       enable_functions: bool = True) -> Dict[str, Any]:
        """
        Process a user request with full AI capabilities
        
        Args:
            user_message: User's message/request
            conversation_id: Conversation ID (creates new if None)
            enable_functions: Whether to enable function calling
            
        Returns:
            Dictionary with AI response and metadata
        """
        try:
            # Ensure conversation exists
            if conversation_id is None:
                conversation_id = self.conversation_manager.create_conversation()
            elif conversation_id not in self.conversation_manager.conversations:
                self.conversation_manager.create_conversation(conversation_id)
            
            # Add user message to conversation
            self.conversation_manager.add_message(
                conversation_id=conversation_id,
                role="user",
                content=user_message
            )
            
            # Get conversation messages for LLM
            messages = self.conversation_manager.get_conversation_messages(conversation_id)
            
            # Prepare function schemas if enabled
            functions = None
            if enable_functions and self.enable_function_calling:
                functions = self.function_caller.get_function_schemas()
            
            # Process with function calling workflow
            if functions:
                response = self._process_with_function_calling(
                    messages=messages,
                    functions=functions,
                    conversation_id=conversation_id
                )
            else:
                # Simple chat without function calling
                response = self._process_simple_chat(
                    messages=messages,
                    conversation_id=conversation_id
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request for conversation_id '{conversation_id}': {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error processing request: {str(e)}", # Keep user-facing error simple
                "conversation_id": conversation_id,
                "user_message": user_message
            }
    
    def _process_with_function_calling(self, 
                                     messages: List[Dict[str, str]], 
                                     functions: List[Dict],
                                     conversation_id: str) -> Dict[str, Any]:
        """
        Process request with function calling capability
        
        Args:
            messages: Conversation messages
            functions: Available functions
            conversation_id: Conversation ID
            
        Returns:
            AI response with function execution results
        """
        function_calls_made = 0
        function_results = []
        
        while function_calls_made < self.max_function_calls_per_turn:
            # Get LLM response
            llm_response = self.llm_client.chat_completion(
                messages=messages,
                functions=functions,
                function_call="auto"
            )
            
            if llm_response["status"] != "success":
                return {
                    "status": "error",
                    "error": f"LLM error: {llm_response.get('error', 'Unknown error')}",
                    "conversation_id": conversation_id
                }
            
            message = llm_response["message"]
            
            # Check if LLM wants to call a function
            if hasattr(message, 'function_call') and message.function_call:
                function_call = message.function_call
                function_name = function_call.name
                
                try:
                    # Parse function arguments
                    function_args = json.loads(function_call.arguments)
                except json.JSONDecodeError as e:
                    logger.error(
                        f"Invalid function arguments JSON for function '{function_name}' in conversation '{conversation_id}'. Arguments: {function_call.arguments}. Error: {e}",
                        exc_info=True
                    )
                    return {
                        "status": "error",
                        "error": f"Invalid function arguments JSON: {str(e)}", # User-facing
                        "function_name": function_name,
                        "conversation_id": conversation_id
                    }
                
                # Execute the function
                function_result = self.function_caller.execute_function_call(
                    function_name=function_name,
                    arguments=function_args
                )
                
                function_results.append({
                    "function_name": function_name,
                    "arguments": function_args,
                    "result": function_result
                })
                
                # Add assistant message with function call
                self.conversation_manager.add_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content="",
                    function_call={
                        "name": function_name,
                        "arguments": function_call.arguments
                    }
                )
                
                # Add function result message
                from .conversation_manager import _safe_json_serialize
                safe_function_result = _safe_json_serialize(function_result)
                self.conversation_manager.add_message(
                    conversation_id=conversation_id,
                    role="function",
                    content=json.dumps(safe_function_result),
                    function_result=function_result,
                    function_name=function_name
                )
                
                # Update messages for next iteration
                messages = self.conversation_manager.get_conversation_messages(conversation_id)
                function_calls_made += 1
                
                # If function failed critically, break the loop
                if function_result["status"] == "error" and not self._is_recoverable_error(function_result):
                    break
                    
            else:
                # No function call, LLM provided final response
                final_content = message.content or "I've completed the requested operations."
                
                # Add assistant's final message
                self.conversation_manager.add_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=final_content
                )
                
                return {
                    "status": "success",
                    "message": final_content,
                    "conversation_id": conversation_id,
                    "function_calls": function_results,
                    "function_calls_count": function_calls_made,
                    "llm_usage": llm_response.get("usage"),
                    "finish_reason": llm_response.get("finish_reason")
                }
        
        # If we exit the loop due to max function calls
        return {
            "status": "partial_success",
            "message": f"Completed {function_calls_made} function calls. Some operations may be incomplete.",
            "conversation_id": conversation_id,
            "function_calls": function_results,
            "function_calls_count": function_calls_made,
            "warning": f"Reached maximum function calls limit ({self.max_function_calls_per_turn})"
        }
    
    def _process_simple_chat(self, 
                           messages: List[Dict[str, str]], 
                           conversation_id: str) -> Dict[str, Any]:
        """
        Process request without function calling
        
        Args:
            messages: Conversation messages
            conversation_id: Conversation ID
            
        Returns:
            Simple chat response
        """
        llm_response = self.llm_client.chat_completion(messages=messages)
        
        if llm_response["status"] != "success":
            return {
                "status": "error",
                "error": f"LLM error: {llm_response.get('error', 'Unknown error')}",
                "conversation_id": conversation_id
            }
        
        response_content = llm_response["content"] or "I'm here to help with data analysis."
        
        # Add assistant message to conversation
        self.conversation_manager.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_content
        )
        
        return {
            "status": "success",
            "message": response_content,
            "conversation_id": conversation_id,
            "function_calls": [],
            "function_calls_count": 0,
            "llm_usage": llm_response.get("usage"),
            "finish_reason": llm_response.get("finish_reason")
        }
    
    def _is_recoverable_error(self, function_result: Dict[str, Any]) -> bool:
        """
        Check if a function error is recoverable
        
        Args:
            function_result: Function execution result
            
        Returns:
            True if error is recoverable
        """
        error_message = function_result.get("error", "").lower()
        
        recoverable_patterns = [
            "column not found",
            "dataset not loaded",
            "container not found",
            "grid full",
            "invalid operator"
        ]
        
        return any(pattern in error_message for pattern in recoverable_patterns)
    
    def get_conversation_history(self, conversation_id: str, 
                               include_function_calls: bool = True) -> Dict[str, Any]:
        """
        Get conversation history
        
        Args:
            conversation_id: Conversation ID
            include_function_calls: Whether to include function call details
            
        Returns:
            Conversation history
        """
        try:
            # Get basic conversation info
            conv_info = self.conversation_manager.get_conversation_info(conversation_id)
            
            if conv_info["status"] != "success":
                return conv_info
            
            # Get messages
            messages = self.conversation_manager.get_recent_messages(conversation_id, count=50)
            
            # Get function call history if requested
            function_calls = []
            if include_function_calls:
                function_calls = self.conversation_manager.get_function_call_history(conversation_id)
            
            return {
                "status": "success",
                "conversation_info": conv_info,
                "messages": messages,
                "function_calls": function_calls,
                "total_messages": len(messages)
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation history for conversation_id '{conversation_id}': {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error getting conversation history: {str(e)}", # User-facing
                "conversation_id": conversation_id
            }
    
    def clear_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Clear conversation history
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Clear operation result
        """
        return self.conversation_manager.clear_conversation(conversation_id)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status
        
        Returns:
            System status information
        """
        try:
            # Test LLM connection
            llm_test = self.llm_client.test_connection()
            
            # Get LLM usage stats
            llm_stats = self.llm_client.get_usage_stats()
            
            # Get conversation stats
            conversations = self.conversation_manager.list_conversations()
            
            # Get available functions
            available_functions = self.function_caller.get_available_functions()
            
            return {
                "status": "success",
                "llm_connection": llm_test,
                "llm_usage": llm_stats,
                "conversations": {
                    "total": len(conversations),
                    "recent": conversations[:5]  # Last 5 conversations
                },
                "functions": {
                    "total_available": len(available_functions),
                    "function_calling_enabled": self.enable_function_calling
                },
                "configuration": {
                    "model": self.llm_client.model,
                    "max_tokens": self.llm_client.max_tokens,
                    "temperature": self.llm_client.temperature,
                    "max_function_calls_per_turn": self.max_function_calls_per_turn
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error getting system status: {str(e)}" # User-facing
            }
    
    def get_available_functions(self) -> Dict[str, Any]:
        """
        Get information about available functions
        
        Returns:
            Available functions information
        """
        return self.function_caller.get_function_help()
    
    def validate_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a function call
        
        Args:
            function_name: Function name
            arguments: Function arguments
            
        Returns:
            Validation result
        """
        return self.function_caller.validate_function_call(function_name, arguments)
    
    def execute_function_directly(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function directly (bypass LLM)
        
        Args:
            function_name: Function name
            arguments: Function arguments
            
        Returns:
            Function execution result
        """
        return self.function_caller.execute_function_call(function_name, arguments) 