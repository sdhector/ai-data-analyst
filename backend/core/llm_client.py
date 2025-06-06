"""
LLM Client for Core Architecture

Handles OpenAI API communication with function schemas from the registry system.
Currently supports only canvas size operations as the first implementation.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

from .registry import get_canvas_management_function_schemas

# Load environment variables from .env file in root directory
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")


class coreLLMClient:
    """
    LLM client specifically configured for core architecture operations
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """
        Initialize the LLM client for core operations
        
        Args:
            api_key: OpenAI API key
            model: Model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # System message for canvas control with core architecture
        self.system_message = """You are a Canvas Control Assistant using the modular architecture. You help users manage canvas operations through function calls.

Currently available capabilities (Phase 1 Implementation):
- Set canvas dimensions with validation and intelligent feedback
- Get canvas dimensions with metadata and analysis

Canvas specifications:
- Default size: 800x600 pixels (customizable)
- Coordinate system: Top-left origin (0,0)
- Position values: x, y coordinates in pixels
- Size values: width, height in pixels
- Minimum size: 1x1 pixels
- Maximum size: No hard limit (reasonable values recommended)

Canvas dimension management features:
- Direct dimension setting with positive integer validation
- Comprehensive error handling and user feedback
- Rich metadata including area, aspect ratio, and size categorization
- Change tracking with before/after comparisons

Input format for canvas dimensions:
- Width and height as positive integers
- Example: set_canvas_dimensions(1200, 800)
- Common sizes: 800x600, 1200x800, 1920x1080

CRITICAL EXECUTION RULES:
1. ALWAYS follow the user's explicit request without deviation
2. If you encounter ANY reason to change the plan, STOP and ask for clarification
3. Use the modular architecture functions exclusively
4. Provide detailed feedback on operations including metrics and timing
5. Explain any automatic optimizations or container repositioning that occurs

When users request canvas operations:
1. Use the set_canvas_dimensions function to change canvas size
2. Use the get_canvas_dimensions function to check current canvas state
3. Provide comprehensive feedback on what was accomplished
4. Explain the dimension changes and their impact

Important guidelines:
- The architecture provides enhanced security and validation
- All operations include comprehensive error handling and user feedback
- Container repositioning strategies are automatically selected for optimal results
- Always acknowledge successful operations with detailed summaries

Be helpful, clear, precise, and always provide rich feedback on operations. The architecture is designed for better user experience and system reliability."""
    
    def get_function_schemas(self) -> List[Dict]:
        """Get function schemas from the core registry system"""
        try:
            # Get schemas from the canvas management registry
            schemas = get_canvas_management_function_schemas()
            return schemas
        except Exception as e:
            print(f"[ERROR] Failed to get function schemas from core registry: {e}")
            return []
    
    def chat_completion(self, messages: List[Dict], functions: List[Dict] = None) -> Dict[str, Any]:
        """
        Get chat completion from OpenAI with function calling support
        
        Args:
            messages: List of message dictionaries
            functions: Optional function schemas (will use registry if not provided)
            
        Returns:
            Dict with status and message/error
        """
        try:
            # Use provided functions or get from registry
            if functions is None:
                functions = self.get_function_schemas()
            
            # Prepare the API call
            api_kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            # Add functions if available
            if functions:
                # Convert to tools format for newer OpenAI API
                tools = []
                for func in functions:
                    tools.append({
                        "type": "function",
                        "function": func
                    })
                api_kwargs["tools"] = tools
                api_kwargs["tool_choice"] = "auto"
            
            # Make the API call
            response = self.client.chat.completions.create(**api_kwargs)
            
            return {
                "status": "success",
                "message": response.choices[0].message,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 