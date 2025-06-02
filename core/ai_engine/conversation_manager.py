"""
Conversation Manager

This module manages conversation history, context, and state for the AI Data Analyst.
It handles message storage, context window management, and conversation persistence.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import numpy as np
import pandas as pd

def _safe_json_serialize(obj):
    """
    Safely serialize objects to JSON-compatible format
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON-serializable object
    """
    if isinstance(obj, dict):
        return {k: _safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_safe_json_serialize(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(_safe_json_serialize(item) for item in obj)
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj) if isinstance(obj, np.floating) else int(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (pd.Timestamp, pd.DatetimeIndex)):
        return str(obj)
    elif hasattr(obj, 'dtype'):  # Handle pandas/numpy dtypes
        return str(obj)
    elif isinstance(obj, type):  # Handle type objects
        return str(obj)
    else:
        return obj

class ConversationManager:
    """
    Manages conversation history and context for AI interactions
    """
    
    def __init__(self, max_context_length: int = 4000):
        """
        Initialize the conversation manager
        
        Args:
            max_context_length: Maximum number of tokens to keep in context
        """
        self.max_context_length = max_context_length
        self.conversations = {}  # conversation_id -> conversation data
        
        # System message for the AI Data Analyst
        self.system_message = """You are an AI Data Analyst assistant. You can help users analyze data and create visualizations.

Available capabilities:
- Load and analyze sample datasets (sales, employees, stocks)
- Create various types of charts (line, bar, scatter, histogram)
- Create data tables and summaries
- Filter, group, and sort data
- Manage visualization containers in a grid layout (1-6 containers)

When users ask for data analysis or visualizations:
1. First load a dataset if none is loaded
2. Use appropriate analysis functions to understand the data
3. Create visualizations in containers as requested
4. Always explain what you're doing and provide insights

Be helpful, clear, and always explain your analysis steps."""
    
    def create_conversation(self, conversation_id: str = None) -> str:
        """
        Create a new conversation
        
        Args:
            conversation_id: Optional conversation ID (generates one if not provided)
            
        Returns:
            Conversation ID
        """
        if conversation_id is None:
            conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        
        self.conversations[conversation_id] = {
            "id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "context_tokens": 0,
            "function_calls": [],
            "metadata": {
                "total_messages": 0,
                "total_function_calls": 0,
                "last_activity": datetime.now().isoformat()
            }
        }
        
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                   function_call: Dict = None, function_result: Dict = None, function_name: str = None) -> Dict[str, Any]:
        """
        Add a message to a conversation
        
        Args:
            conversation_id: ID of the conversation
            role: Message role (user, assistant, system)
            content: Message content
            function_call: Optional function call data
            function_result: Optional function result data
            function_name: Optional function name for function role messages
            
        Returns:
            Dictionary with operation status
        """
        try:
            # Ensure conversation exists
            if conversation_id not in self.conversations:
                self.create_conversation(conversation_id)
            
            conversation = self.conversations[conversation_id]
            
            # Create message
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "message_id": f"msg_{uuid.uuid4().hex[:8]}"
            }
            
            # Add function call data if provided
            if function_call:
                message["function_call"] = function_call
                conversation["function_calls"].append({
                    "function_call": function_call,
                    "timestamp": message["timestamp"],
                    "message_id": message["message_id"]
                })
                conversation["metadata"]["total_function_calls"] += 1
            
            # Add function result if provided
            if function_result:
                message["function_result"] = _safe_json_serialize(function_result)
            
            # Add function name if provided (required for function role messages)
            if function_name:
                message["function_name"] = function_name
            
            # Add message to conversation
            conversation["messages"].append(message)
            conversation["metadata"]["total_messages"] += 1
            conversation["metadata"]["last_activity"] = message["timestamp"]
            
            # Manage context window
            self._manage_context_window(conversation_id)
            
            return {
                "status": "success",
                "message_id": message["message_id"],
                "conversation_id": conversation_id,
                "total_messages": len(conversation["messages"])
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error adding message: {str(e)}",
                "conversation_id": conversation_id
            }
    
    def get_conversation_messages(self, conversation_id: str, 
                                include_system: bool = True) -> List[Dict[str, Any]]:
        """
        Get messages for a conversation in OpenAI format
        
        Args:
            conversation_id: ID of the conversation
            include_system: Whether to include system message
            
        Returns:
            List of messages in OpenAI format
        """
        if conversation_id not in self.conversations:
            return []
        
        messages = []
        
        # Add system message if requested
        if include_system:
            messages.append({
                "role": "system",
                "content": self.system_message
            })
        
        # Add conversation messages
        conversation = self.conversations[conversation_id]
        for msg in conversation["messages"]:
            # Convert to OpenAI format
            openai_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            
            # Add function call if present
            if "function_call" in msg:
                openai_msg["function_call"] = msg["function_call"]
            
            # Add function name if present (required for function role messages)
            if "function_name" in msg:
                openai_msg["name"] = msg["function_name"]
            
            messages.append(openai_msg)
        
        return messages
    
    def get_conversation_info(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get information about a conversation
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dictionary with conversation information
        """
        if conversation_id not in self.conversations:
            return {
                "status": "error",
                "error": f"Conversation '{conversation_id}' not found"
            }
        
        conversation = self.conversations[conversation_id]
        
        return {
            "status": "success",
            "conversation_id": conversation_id,
            "created_at": conversation["created_at"],
            "total_messages": len(conversation["messages"]),
            "total_function_calls": len(conversation["function_calls"]),
            "last_activity": conversation["metadata"]["last_activity"],
            "context_tokens": conversation["context_tokens"]
        }
    
    def get_recent_messages(self, conversation_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent messages from a conversation
        
        Args:
            conversation_id: ID of the conversation
            count: Number of recent messages to return
            
        Returns:
            List of recent messages
        """
        if conversation_id not in self.conversations:
            return []
        
        conversation = self.conversations[conversation_id]
        return conversation["messages"][-count:]
    
    def clear_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Clear all messages from a conversation
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dictionary with operation status
        """
        try:
            if conversation_id not in self.conversations:
                return {
                    "status": "error",
                    "error": f"Conversation '{conversation_id}' not found"
                }
            
            # Reset conversation data
            conversation = self.conversations[conversation_id]
            messages_cleared = len(conversation["messages"])
            
            conversation["messages"] = []
            conversation["function_calls"] = []
            conversation["context_tokens"] = 0
            conversation["metadata"]["total_messages"] = 0
            conversation["metadata"]["total_function_calls"] = 0
            conversation["metadata"]["last_activity"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "conversation_id": conversation_id,
                "messages_cleared": messages_cleared
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error clearing conversation: {str(e)}",
                "conversation_id": conversation_id
            }
    
    def delete_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Delete a conversation completely
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dictionary with operation status
        """
        try:
            if conversation_id not in self.conversations:
                return {
                    "status": "error",
                    "error": f"Conversation '{conversation_id}' not found"
                }
            
            del self.conversations[conversation_id]
            
            return {
                "status": "success",
                "conversation_id": conversation_id,
                "message": "Conversation deleted successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error deleting conversation: {str(e)}",
                "conversation_id": conversation_id
            }
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        List all conversations
        
        Returns:
            List of conversation summaries
        """
        conversations = []
        
        for conv_id, conv_data in self.conversations.items():
            conversations.append({
                "conversation_id": conv_id,
                "created_at": conv_data["created_at"],
                "total_messages": len(conv_data["messages"]),
                "total_function_calls": len(conv_data["function_calls"]),
                "last_activity": conv_data["metadata"]["last_activity"]
            })
        
        # Sort by last activity (most recent first)
        conversations.sort(key=lambda x: x["last_activity"], reverse=True)
        
        return conversations
    
    def _manage_context_window(self, conversation_id: str):
        """
        Manage context window to stay within token limits
        
        Args:
            conversation_id: ID of the conversation
        """
        conversation = self.conversations[conversation_id]
        messages = conversation["messages"]
        
        # Rough token estimation (4 characters ≈ 1 token)
        total_chars = sum(len(msg["content"]) for msg in messages)
        estimated_tokens = total_chars // 4
        
        # If we're over the limit, remove older messages (keep recent ones)
        while estimated_tokens > self.max_context_length and len(messages) > 1:
            # Remove the oldest message (but keep at least 1 message)
            removed_msg = messages.pop(0)
            total_chars -= len(removed_msg["content"])
            estimated_tokens = total_chars // 4
        
        conversation["context_tokens"] = estimated_tokens
    
    def export_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Export conversation data
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dictionary with conversation data
        """
        if conversation_id not in self.conversations:
            return {
                "status": "error",
                "error": f"Conversation '{conversation_id}' not found"
            }
        
        return {
            "status": "success",
            "conversation_data": self.conversations[conversation_id]
        }
    
    def get_function_call_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get history of function calls for a conversation
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of function calls
        """
        if conversation_id not in self.conversations:
            return []
        
        return self.conversations[conversation_id]["function_calls"] 