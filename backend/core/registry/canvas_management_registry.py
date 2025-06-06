"""
Canvas Management Registry

Provides function schemas and execution for canvas management operations.
This registry exposes canvas dimension tools to the AI system.
"""

import logging
import os
from typing import Dict, Any, List
from ..tools import (
    set_canvas_dimensions_tool,
    get_canvas_dimensions_tool
)
from ..utilities import (
    log_component_entry,
    log_component_exit,
    log_handover
)


def get_canvas_management_function_schemas() -> List[Dict[str, Any]]:
    """
    Get OpenAI function schemas for canvas management operations.
    
    Returns:
        List of function schema dictionaries
    """
    return [
        {
            "name": "set_canvas_dimensions",
            "description": "Set the canvas dimensions (width and height) to resize the scrollable content area",
            "parameters": {
                "type": "object",
                "properties": {
                    "width": {
                        "type": "integer",
                        "description": "Canvas width in pixels (must be positive integer)",
                        "minimum": 1
                    },
                    "height": {
                        "type": "integer", 
                        "description": "Canvas height in pixels (must be positive integer)",
                        "minimum": 1
                    }
                },
                "required": ["width", "height"]
            }
        },
        {
            "name": "get_canvas_dimensions",
            "description": "Get the current canvas dimensions and metadata",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    ]


async def execute_canvas_management_tool(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a canvas management tool by name.
    
    Args:
        function_name: Name of the function to execute
        arguments: Function arguments
        
    Returns:
        Function execution result
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[REGISTRY] 🎪 Received tool execution request: {function_name}")
        logger.debug(f"[REGISTRY] 📋 Arguments: {arguments}")
    
    log_component_entry("REGISTRY", "execute_canvas_management_tool", f"{function_name}({arguments})")
    
    try:
        if function_name == "set_canvas_dimensions":
            if debug_mode:
                logger.debug(f"[REGISTRY] 🎯 Executing set_canvas_dimensions tool")
            
            width = arguments.get("width")
            height = arguments.get("height")
            
            if width is None or height is None:
                if debug_mode:
                    logger.debug(f"[REGISTRY] ❌ Missing parameters for set_canvas_dimensions")
                return {
                    "status": "error",
                    "message": "Missing required parameters: width and height",
                    "error_code": "MISSING_PARAMETERS",
                    "required_parameters": ["width", "height"],
                    "provided_arguments": arguments
                }
            
            if debug_mode:
                logger.debug(f"[REGISTRY] 🔄 Calling set_canvas_dimensions_tool({width}, {height})")
            
            log_handover("REGISTRY", "TOOL", "set_canvas_dimensions", f"width={width}, height={height}")
            
            result = await set_canvas_dimensions_tool(width, height)
            
            if debug_mode:
                logger.debug(f"[REGISTRY] 🏁 Tool returned: {result.get('status', 'unknown')}")
            
            log_component_exit("REGISTRY", "execute_canvas_management_tool", result.get('status', 'unknown'))
            return result
            
        elif function_name == "get_canvas_dimensions":
            if debug_mode:
                logger.debug(f"[REGISTRY] 🎯 Executing get_canvas_dimensions tool")
                logger.debug(f"[REGISTRY] 🔄 Calling get_canvas_dimensions_tool()")
            
            log_handover("REGISTRY", "TOOL", "get_canvas_dimensions", "")
            
            result = await get_canvas_dimensions_tool()
            
            if debug_mode:
                logger.debug(f"[REGISTRY] 🏁 Tool returned: {result.get('status', 'unknown')}")
            
            log_component_exit("REGISTRY", "execute_canvas_management_tool", result.get('status', 'unknown'))
            return result
            
        else:
            return {
                "status": "error",
                "message": f"Unknown canvas management function: {function_name}",
                "error_code": "UNKNOWN_FUNCTION",
                "available_functions": ["set_canvas_dimensions", "get_canvas_dimensions"],
                "requested_function": function_name
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error executing canvas management function {function_name}: {str(e)}",
            "error_code": "EXECUTION_ERROR",
            "function_name": function_name,
            "arguments": arguments
        }


def get_tool_by_name(tool_name: str) -> callable:
    """
    Get a tool function by name.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool function or None if not found
    """
    tools = {
        "set_canvas_dimensions": set_canvas_dimensions_tool,
        "get_canvas_dimensions": get_canvas_dimensions_tool
    }
    return tools.get(tool_name)


def get_tool_metadata(tool_name: str) -> Dict[str, Any]:
    """
    Get metadata for a specific tool.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool metadata dictionary
    """
    metadata = {
        "set_canvas_dimensions": {
            "name": "set_canvas_dimensions",
            "description": "Set canvas dimensions with validation and intelligent feedback",
            "category": "canvas_management",
            "parameters": ["width", "height"],
            "returns": "Operation result with dimension changes and recommendations"
        },
        "get_canvas_dimensions": {
            "name": "get_canvas_dimensions", 
            "description": "Get current canvas dimensions with additional context",
            "category": "canvas_management",
            "parameters": [],
            "returns": "Current dimensions with metadata and analysis"
        }
    }
    return metadata.get(tool_name, {})


def list_available_tools() -> List[str]:
    """
    Get list of available canvas management tools.
    
    Returns:
        List of tool names
    """
    return ["set_canvas_dimensions", "get_canvas_dimensions"] 