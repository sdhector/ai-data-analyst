
"""
LLM Client for Canvas Control Operations

Handles OpenAI API communication with canvas-specific function schemas.
Based on the proven implementation from tests/python/llm_canvas_chatbot.py.
"""

import json
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
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

Canvas specifications:
- Default size: 800x600 pixels (customizable)
- Coordinate system: Top-left origin (0,0)
- Position values: x, y coordinates in pixels
- Size values: width, height in pixels

Canvas behavior controls:
- Auto-adjustment: Containers automatically fit within canvas bounds (always enabled for safety)
- Overlap prevention: Containers can overlap with existing ones (disabled by default)

CRITICAL EXECUTION RULES:
1. NEVER DEVIATE from the user's explicit request without asking for clarification first
2. If you encounter ANY reason to change the plan or approach, STOP and ask the user for clarification
3. Follow the user's instructions exactly as specified - do not make assumptions or modifications
4. NEVER CHANGE THE CANVAS SIZE without explicitly asking the user for permission first
5. MAXIMIZE CANVAS SPACE USAGE: Always calculate optimal container sizes to make the best use of available canvas space
6. When creating multiple containers, distribute them efficiently across the canvas to utilize the full area

When users request canvas operations:
1. ALWAYS start by checking current canvas state with get_canvas_state() and get_canvas_size() to understand available space
2. Container operations (create, modify, delete) now AUTOMATICALLY use optimal layout - no manual calculation needed
3. Simply call the container functions with required parameters - optimization happens automatically
4. The system will automatically maximize space usage and minimize size differences for all containers
5. Always explain what the optimization accomplished and why specific dimensions were chosen
6. Provide feedback on the optimization results including space utilization and layout metrics
7. If a function fails, check the error message and try alternative approaches
8. If placement fails due to safety constraints, explain why and ask user for clarification on how to proceed
9. Always provide a final text response summarizing what was accomplished
10. If you need to deviate from the user's request for any reason, ask for permission first

Important guidelines:
- Container IDs must match exactly what exists on canvas (check with get_canvas_state first)
- Containers may be automatically repositioned to prevent overlaps (safety feature)
- Containers may be resized to fit canvas bounds (safety feature)
- Always acknowledge when automatic adjustments occur
- If a container cannot be placed due to safety constraints, ask user how to proceed rather than making assumptions

Be helpful, clear, precise, and always confirm successful operations with a final summary. NEVER change the user's plan without explicit permission."""
    
    def get_function_schemas(self) -> List[Dict]:
        """Get function schemas for canvas operations"""
        return [
            {
                "name": "create_container",
                "description": "Create a new container on the canvas using automatic optimal layout. Position and size are automatically calculated to maximize space usage and minimize size differences.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "Unique identifier for the container. Must be unique - check existing containers with get_canvas_state() if needed."
                        }
                    },
                    "required": ["container_id"]
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
                "description": "Modify an existing container using automatic optimal layout. All containers on canvas are re-optimized for best space usage and size uniformity. IMPORTANT: Always call get_canvas_state() first to check existing container IDs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID of the container to modify. Must match exactly an existing container ID from get_canvas_state()."
                        }
                    },
                    "required": ["container_id"]
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
                "name": "create_pie_chart",
                "description": "Create a pie chart visualization in a container with sample data or custom data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID of the container to place the pie chart in. Must be an existing container."
                        },
                        "title": {
                            "type": "string",
                            "description": "Title for the pie chart",
                            "default": "Pie Chart"
                        },
                        "use_sample_data": {
                            "type": "boolean",
                            "description": "Whether to use default sample data (Technology, Healthcare, Finance, Education, Retail)",
                            "default": True
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Custom labels for pie chart segments (only used if use_sample_data is false)"
                        },
                        "values": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Custom values for pie chart segments (only used if use_sample_data is false)"
                        }
                    },
                    "required": ["container_id"]
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
            },
            {
                "name": "check_container_content",
                "description": "Check what content is in a specific container (useful for verifying pie charts or other content)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID of the container to check"
                        }
                    },
                    "required": ["container_id"]
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