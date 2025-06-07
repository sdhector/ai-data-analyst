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
    get_canvas_dimensions_tool,
    create_container_tool,
    resize_container_tool,
    move_container_tool,
    delete_container_tool
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
        },
        {
            "name": "create_container",
            "description": "Create a new container at a specified position on the canvas with given dimensions",
            "parameters": {
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Unique identifier for the container (must be non-empty string)",
                        "minLength": 1
                    },
                    "x": {
                        "type": "integer",
                        "description": "X coordinate position on canvas (must be non-negative)",
                        "minimum": 0
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate position on canvas (must be non-negative)",
                        "minimum": 0
                    },
                    "width": {
                        "type": "integer",
                        "description": "Container width in pixels (must be positive)",
                        "minimum": 1
                    },
                    "height": {
                        "type": "integer",
                        "description": "Container height in pixels (must be positive)",
                        "minimum": 1
                    }
                },
                "required": ["container_id", "x", "y", "width", "height"]
            }
        },
        {
            "name": "resize_container",
            "description": "Resize an existing container by changing its width and height dimensions",
            "parameters": {
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Identifier of the container to resize (must exist)",
                        "minLength": 1
                    },
                    "width": {
                        "type": "integer",
                        "description": "New container width in pixels (must be positive)",
                        "minimum": 1
                    },
                    "height": {
                        "type": "integer",
                        "description": "New container height in pixels (must be positive)",
                        "minimum": 1
                    }
                },
                "required": ["container_id", "width", "height"]
            }
        },
        {
            "name": "move_container",
            "description": "Move an existing container to a new position on the canvas",
            "parameters": {
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Identifier of the container to move (must exist)",
                        "minLength": 1
                    },
                    "x": {
                        "type": "integer",
                        "description": "New X coordinate position on canvas (must be non-negative)",
                        "minimum": 0
                    },
                    "y": {
                        "type": "integer",
                        "description": "New Y coordinate position on canvas (must be non-negative)",
                        "minimum": 0
                    }
                },
                "required": ["container_id", "x", "y"]
            }
        },
        {
            "name": "delete_container",
            "description": "Delete an existing container and remove it from the canvas",
            "parameters": {
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Identifier of the container to delete (must exist)",
                        "minLength": 1
                    }
                },
                "required": ["container_id"]
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
            
        elif function_name == "create_container":
            if debug_mode:
                logger.debug(f"[REGISTRY] 🎯 Executing create_container tool")
            
            container_id = arguments.get("container_id")
            x = arguments.get("x")
            y = arguments.get("y")
            width = arguments.get("width")
            height = arguments.get("height")
            
            # Check for missing required parameters
            missing_params = []
            if container_id is None:
                missing_params.append("container_id")
            if x is None:
                missing_params.append("x")
            if y is None:
                missing_params.append("y")
            if width is None:
                missing_params.append("width")
            if height is None:
                missing_params.append("height")
            
            if missing_params:
                if debug_mode:
                    logger.debug(f"[REGISTRY] ❌ Missing parameters for create_container: {missing_params}")
                return {
                    "status": "error",
                    "message": f"Missing required parameters: {', '.join(missing_params)}",
                    "error_code": "MISSING_PARAMETERS",
                    "required_parameters": ["container_id", "x", "y", "width", "height"],
                    "missing_parameters": missing_params,
                    "provided_arguments": arguments
                }
            
            if debug_mode:
                logger.debug(f"[REGISTRY] 🔄 Calling create_container_tool({container_id}, {x}, {y}, {width}, {height})")
            
            log_handover("REGISTRY", "TOOL", "create_container", f"container_id={container_id}, x={x}, y={y}, width={width}, height={height}")
            
            result = await create_container_tool(container_id, x, y, width, height)
            
            if debug_mode:
                logger.debug(f"[REGISTRY] 🏁 Tool returned: {result.get('status', 'unknown')}")
            
            log_component_exit("REGISTRY", "execute_canvas_management_tool", result.get('status', 'unknown'))
            return result
            
        elif function_name == "resize_container":
            if debug_mode:
                logger.debug(f"[REGISTRY] 🎯 Executing resize_container tool")
            
            container_id = arguments.get("container_id")
            width = arguments.get("width")
            height = arguments.get("height")
            
            # Check for missing required parameters
            missing_params = []
            if container_id is None:
                missing_params.append("container_id")
            if width is None:
                missing_params.append("width")
            if height is None:
                missing_params.append("height")
            
            if missing_params:
                if debug_mode:
                    logger.debug(f"[REGISTRY] ❌ Missing parameters for resize_container: {missing_params}")
                return {
                    "status": "error",
                    "message": f"Missing required parameters: {', '.join(missing_params)}",
                    "error_code": "MISSING_PARAMETERS",
                    "required_parameters": ["container_id", "width", "height"],
                    "missing_parameters": missing_params,
                    "provided_arguments": arguments
                }
            
            if debug_mode:
                logger.debug(f"[REGISTRY] 🔄 Calling resize_container_tool({container_id}, {width}, {height})")
            
            log_handover("REGISTRY", "TOOL", "resize_container", f"container_id={container_id}, width={width}, height={height}")
            
            result = await resize_container_tool(container_id, width, height)
            
            if debug_mode:
                logger.debug(f"[REGISTRY] 🏁 Tool returned: {result.get('status', 'unknown')}")
            
            log_component_exit("REGISTRY", "execute_canvas_management_tool", result.get('status', 'unknown'))
            return result
            
        elif function_name == "move_container":
            if debug_mode:
                logger.debug(f"[REGISTRY] 🎯 Executing move_container tool")
            
            container_id = arguments.get("container_id")
            x = arguments.get("x")
            y = arguments.get("y")
            
            # Check for missing required parameters
            missing_params = []
            if container_id is None:
                missing_params.append("container_id")
            if x is None:
                missing_params.append("x")
            if y is None:
                missing_params.append("y")
            
            if missing_params:
                if debug_mode:
                    logger.debug(f"[REGISTRY] ❌ Missing parameters for move_container: {missing_params}")
                return {
                    "status": "error",
                    "message": f"Missing required parameters: {', '.join(missing_params)}",
                    "error_code": "MISSING_PARAMETERS",
                    "required_parameters": ["container_id", "x", "y"],
                    "missing_parameters": missing_params,
                    "provided_arguments": arguments
                }
            
            if debug_mode:
                logger.debug(f"[REGISTRY] 🔄 Calling move_container_tool({container_id}, {x}, {y})")
            
            log_handover("REGISTRY", "TOOL", "move_container", f"container_id={container_id}, x={x}, y={y}")
            
            result = await move_container_tool(container_id, x, y)
            
            if debug_mode:
                logger.debug(f"[REGISTRY] 🏁 Tool returned: {result.get('status', 'unknown')}")
            
            log_component_exit("REGISTRY", "execute_canvas_management_tool", result.get('status', 'unknown'))
            return result
            
        elif function_name == "delete_container":
            if debug_mode:
                logger.debug(f"[REGISTRY] 🎯 Executing delete_container tool")
            
            container_id = arguments.get("container_id")
            
            # Check for missing required parameters
            if container_id is None:
                if debug_mode:
                    logger.debug(f"[REGISTRY] ❌ Missing parameters for delete_container: container_id")
                return {
                    "status": "error",
                    "message": "Missing required parameter: container_id",
                    "error_code": "MISSING_PARAMETERS",
                    "required_parameters": ["container_id"],
                    "missing_parameters": ["container_id"],
                    "provided_arguments": arguments
                }
            
            if debug_mode:
                logger.debug(f"[REGISTRY] 🔄 Calling delete_container_tool({container_id})")
            
            log_handover("REGISTRY", "TOOL", "delete_container", f"container_id={container_id}")
            
            result = await delete_container_tool(container_id)
            
            if debug_mode:
                logger.debug(f"[REGISTRY] 🏁 Tool returned: {result.get('status', 'unknown')}")
            
            log_component_exit("REGISTRY", "execute_canvas_management_tool", result.get('status', 'unknown'))
            return result
            
        else:
            return {
                "status": "error",
                "message": f"Unknown canvas management function: {function_name}",
                "error_code": "UNKNOWN_FUNCTION",
                "available_functions": ["set_canvas_dimensions", "get_canvas_dimensions", "create_container", "resize_container", "move_container", "delete_container"],
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
        "get_canvas_dimensions": get_canvas_dimensions_tool,
        "create_container": create_container_tool,
        "resize_container": resize_container_tool,
        "move_container": move_container_tool,
        "delete_container": delete_container_tool
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
        },
        "create_container": {
            "name": "create_container",
            "description": "Create a new container with validation and intelligent feedback",
            "category": "canvas_management",
            "parameters": ["container_id", "x", "y", "width", "height"],
            "returns": "Container creation result with positioning context and recommendations"
        },
        "resize_container": {
            "name": "resize_container",
            "description": "Resize an existing container with validation and intelligent feedback",
            "category": "canvas_management",
            "parameters": ["container_id", "width", "height"],
            "returns": "Container resize result with size changes and positioning context"
        },
        "move_container": {
            "name": "move_container",
            "description": "Move an existing container with validation and intelligent feedback",
            "category": "canvas_management",
            "parameters": ["container_id", "x", "y"],
            "returns": "Container move result with movement details and positioning context"
        },
        "delete_container": {
            "name": "delete_container",
            "description": "Delete an existing container with validation and intelligent feedback",
            "category": "canvas_management",
            "parameters": ["container_id"],
            "returns": "Container deletion result with freed space information"
        }
    }
    return metadata.get(tool_name, {})


def list_available_tools() -> List[str]:
    """
    Get list of available canvas management tools.
    
    Returns:
        List of tool names
    """
    return ["set_canvas_dimensions", "get_canvas_dimensions", "create_container", "resize_container", "move_container", "delete_container"] 