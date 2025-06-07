"""
Canvas Management Tools

High-level canvas management operations exposed to the AI.
These tools orchestrate primitives with validation and provide rich responses.
"""

import logging
import os
from typing import Dict, Any
from datetime import datetime

# Import primitives
from ..primitives import (
    set_canvas_dimensions_primitive,
    get_canvas_dimensions_primitive,
    create_container_primitive,
    resize_container_primitive,
    move_container_primitive,
    delete_container_primitive,
    clear_canvas_primitive
)
from ..utilities import (
    log_component_entry,
    log_component_exit,
    log_handover
)


async def set_canvas_dimensions_tool(width: int, height: int) -> Dict[str, Any]:
    """
    Set canvas dimensions with validation and intelligent feedback.
    
    Args:
        width: New canvas width in pixels (must be positive integer)
        height: New canvas height in pixels (must be positive integer)
        
    Returns:
        Dict with operation result and detailed information
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[TOOL] 🛠️ set_canvas_dimensions_tool called with width={width}, height={height}")
    
    log_component_entry("TOOL", "set_canvas_dimensions_tool", f"width={width}, height={height}")
    
    try:
        # Basic validation
        if not isinstance(width, int) or not isinstance(height, int):
            return {
                "status": "error",
                "message": "Width and height must be integers",
                "error_code": "INVALID_TYPE",
                "provided_width": width,
                "provided_height": height,
                "suggestions": [
                    "Provide width and height as positive integers",
                    "Example: set_canvas_dimensions(1200, 800)"
                ]
            }
        
        if width <= 0 or height <= 0:
            return {
                "status": "error",
                "message": "Width and height must be positive integers",
                "error_code": "INVALID_VALUE",
                "provided_width": width,
                "provided_height": height,
                "suggestions": [
                    "Use positive values greater than 0",
                    "Minimum recommended size: 200x200",
                    "Common sizes: 800x600, 1200x800, 1920x1080"
                ]
            }
        
        # Get current dimensions for comparison
        current_result = await get_canvas_dimensions_primitive()
        if current_result["status"] != "success":
            return {
                "status": "error",
                "message": "Failed to get current canvas dimensions",
                "error_code": "STATE_ERROR",
                "details": current_result
            }
        
        current_dims = current_result["dimensions"]
        old_width = current_dims["width"]
        old_height = current_dims["height"]
        
        # Check if dimensions are already the same
        if width == old_width and height == old_height:
            return {
                "status": "success",
                "message": f"Canvas dimensions are already {width}x{height}",
                "operation": "set_canvas_dimensions",
                "dimensions": {"width": width, "height": height},
                "change_applied": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Execute the primitive operation
        if debug_mode:
            logger.debug(f"[TOOL] 🔄 Calling primitive: set_canvas_dimensions_primitive({width}, {height})")
        
        log_handover("TOOL", "PRIMITIVE", "set_canvas_dimensions", f"width={width}, height={height}")
        
        result = await set_canvas_dimensions_primitive(width, height)
        
        if debug_mode:
            logger.debug(f"[TOOL] 🏁 Primitive returned: {result.get('status', 'unknown')}")
        
        if result["status"] != "success":
            return {
                "status": "error",
                "message": "Failed to set canvas dimensions",
                "error_code": "OPERATION_FAILED",
                "primitive_result": result,
                "suggestions": [
                    "Try again with different dimensions",
                    "Check if canvas is in a valid state"
                ]
            }
        
        # Calculate dimension changes
        width_change = width - old_width
        height_change = height - old_height
        area_old = old_width * old_height
        area_new = width * height
        area_change_percent = ((area_new - area_old) / area_old) * 100 if area_old > 0 else 0
        
        final_result = {
            "status": "success",
            "message": f"Canvas dimensions successfully changed from {old_width}x{old_height} to {width}x{height}",
            "operation": "set_canvas_dimensions",
            "old_dimensions": {"width": old_width, "height": old_height},
            "new_dimensions": {"width": width, "height": height},
            "changes": {
                "width_change": width_change,
                "height_change": height_change,
                "area_change_percent": round(area_change_percent, 1)
            },
            "change_applied": True,
            "recommendations": [
                f"Canvas area {'increased' if area_change_percent > 0 else 'decreased'} by {abs(area_change_percent):.1f}%",
                "Existing containers may need repositioning if they're outside the new bounds",
                "Consider optimizing container layout for the new canvas size"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "set_canvas_dimensions_tool", "SUCCESS", f"Changed to {width}x{height}")
        return final_result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Unexpected error setting canvas dimensions: {str(e)}",
            "error_code": "UNEXPECTED_ERROR",
            "provided_width": width,
            "provided_height": height,
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "set_canvas_dimensions_tool", "ERROR", str(e))
        return error_result


async def get_canvas_dimensions_tool() -> Dict[str, Any]:
    """
    Get current canvas dimensions with additional context.
    
    Returns:
        Dict with current canvas dimensions and metadata
    """
    log_component_entry("TOOL", "get_canvas_dimensions_tool", "")
    
    try:
        result = await get_canvas_dimensions_primitive()
        
        if result["status"] != "success":
            return {
                "status": "error",
                "message": "Failed to get canvas dimensions",
                "error_code": "OPERATION_FAILED",
                "primitive_result": result
            }
        
        dims = result["dimensions"]
        width = dims["width"]
        height = dims["height"]
        area = width * height
        aspect_ratio = width / height if height > 0 else 0
        
        # Determine canvas size category
        if area < 500000:  # Less than ~707x707
            size_category = "small"
        elif area < 1500000:  # Less than ~1225x1225
            size_category = "medium"
        else:
            size_category = "large"
        
        final_result = {
            "status": "success",
            "message": f"Current canvas dimensions: {width}x{height}",
            "operation": "get_canvas_dimensions",
            "dimensions": {"width": width, "height": height},
            "metadata": {
                "area_pixels": area,
                "aspect_ratio": round(aspect_ratio, 2),
                "size_category": size_category,
                "is_landscape": width > height,
                "is_portrait": height > width,
                "is_square": width == height
            },
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "get_canvas_dimensions_tool", "SUCCESS", f"Retrieved {width}x{height}")
        return final_result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Unexpected error getting canvas dimensions: {str(e)}",
            "error_code": "UNEXPECTED_ERROR",
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "get_canvas_dimensions_tool", "ERROR", str(e))
        return error_result


async def create_container_tool(container_id: str, x: int, y: int, width: int, height: int) -> Dict[str, Any]:
    """
    Create a new container with validation and intelligent feedback.
    
    Args:
        container_id: Unique identifier for the container (must be non-empty string)
        x: X coordinate position on canvas (must be non-negative integer)
        y: Y coordinate position on canvas (must be non-negative integer)
        width: Container width in pixels (must be positive integer)
        height: Container height in pixels (must be positive integer)
        
    Returns:
        Dict with operation result and detailed information
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[TOOL] create_container_tool called with container_id={container_id}, x={x}, y={y}, width={width}, height={height}")
    
    log_component_entry("TOOL", "create_container_tool", f"container_id={container_id}, x={x}, y={y}, width={width}, height={height}")
    
    try:
        # Basic validation
        if not isinstance(container_id, str) or not container_id.strip():
            return {
                "status": "error",
                "message": "Container ID must be a non-empty string",
                "error_code": "INVALID_CONTAINER_ID",
                "provided_container_id": container_id,
                "suggestions": [
                    "Provide a unique, non-empty string identifier",
                    "Example: 'container_1', 'data_viz', 'chart_panel'"
                ]
            }
        
        if not isinstance(x, int) or not isinstance(y, int):
            return {
                "status": "error",
                "message": "X and Y coordinates must be integers",
                "error_code": "INVALID_COORDINATES",
                "provided_x": x,
                "provided_y": y,
                "suggestions": [
                    "Provide X and Y as non-negative integers",
                    "Example: create_container('my_container', 100, 50, 200, 150)"
                ]
            }
        
        if not isinstance(width, int) or not isinstance(height, int):
            return {
                "status": "error",
                "message": "Width and height must be integers",
                "error_code": "INVALID_DIMENSIONS",
                "provided_width": width,
                "provided_height": height,
                "suggestions": [
                    "Provide width and height as positive integers",
                    "Minimum recommended size: 50x50",
                    "Common sizes: 200x150, 300x200, 400x300"
                ]
            }
        
        if x < 0 or y < 0:
            return {
                "status": "error",
                "message": "X and Y coordinates must be non-negative",
                "error_code": "NEGATIVE_COORDINATES",
                "provided_x": x,
                "provided_y": y,
                "suggestions": [
                    "Use coordinates >= 0",
                    "Top-left corner of canvas is (0, 0)"
                ]
            }
        
        if width <= 0 or height <= 0:
            return {
                "status": "error",
                "message": "Width and height must be positive integers",
                "error_code": "INVALID_SIZE",
                "provided_width": width,
                "provided_height": height,
                "suggestions": [
                    "Use positive values greater than 0",
                    "Minimum recommended size: 50x50",
                    "Consider the canvas size when choosing dimensions"
                ]
            }
        
        # Get current canvas dimensions for context
        canvas_result = await get_canvas_dimensions_primitive()
        if canvas_result["status"] != "success":
            return {
                "status": "error",
                "message": "Failed to get current canvas dimensions",
                "error_code": "CANVAS_STATE_ERROR",
                "details": canvas_result
            }
        
        canvas_dims = canvas_result["dimensions"]
        canvas_width = canvas_dims["width"]
        canvas_height = canvas_dims["height"]
        
        # Execute the primitive operation
        if debug_mode:
            logger.debug(f"[TOOL] Calling primitive: create_container_primitive({container_id}, {x}, {y}, {width}, {height})")
        
        log_handover("TOOL", "PRIMITIVE", "create_container", f"container_id={container_id}, x={x}, y={y}, width={width}, height={height}")
        
        result = await create_container_primitive(container_id, x, y, width, height)
        
        if debug_mode:
            logger.debug(f"[TOOL] Primitive returned: {result.get('status', 'unknown')}")
        
        if result["status"] != "success":
            # Enhance error messages with helpful suggestions
            error_code = result.get("error_code", "UNKNOWN_ERROR")
            enhanced_suggestions = []
            
            if error_code == "DUPLICATE_ID":
                enhanced_suggestions = [
                    f"Container ID '{container_id}' already exists",
                    "Try a different unique identifier",
                    f"Existing containers: {', '.join(result.get('existing_container_ids', []))}"
                ]
            elif error_code == "OUT_OF_BOUNDS":
                enhanced_suggestions = [
                    f"Container extends outside canvas bounds ({canvas_width}x{canvas_height})",
                    f"Reduce size or move position to fit within canvas",
                    f"Maximum position for {width}x{height} container: ({canvas_width-width}, {canvas_height-height})"
                ]
            elif error_code == "OVERLAP_DETECTED":
                overlapping = result.get("overlapping_containers", [])
                enhanced_suggestions = [
                    f"Container overlaps with existing containers: {', '.join(overlapping)}",
                    "Try a different position or size",
                    "Use get_canvas_state to see existing container positions"
                ]
            else:
                enhanced_suggestions = [
                    "Check container parameters and try again",
                    "Ensure canvas is in a valid state"
                ]
            
            return {
                "status": "error",
                "message": result.get("error", "Failed to create container"),
                "error_code": error_code,
                "primitive_result": result,
                "suggestions": enhanced_suggestions
            }
        
        # Calculate additional context for successful creation
        container_area = width * height
        canvas_area = canvas_width * canvas_height
        area_percentage = (container_area / canvas_area) * 100 if canvas_area > 0 else 0
        
        final_result = {
            "status": "success",
            "message": f"Container '{container_id}' successfully created at position ({x}, {y}) with size {width}x{height}",
            "operation": "create_container",
            "container": result["container"],
            "canvas_context": {
                "canvas_size": {"width": canvas_width, "height": canvas_height},
                "container_area_percentage": round(area_percentage, 1),
                "total_containers": result["total_containers"]
            },
            "positioning": {
                "distance_from_edges": {
                    "left": x,
                    "top": y,
                    "right": canvas_width - (x + width),
                    "bottom": canvas_height - (y + height)
                }
            },
            "recommendations": [
                f"Container occupies {area_percentage:.1f}% of canvas area",
                f"Canvas now has {result['total_containers']} container(s)",
                "Container is ready for content or further modifications"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "create_container_tool", "SUCCESS", f"Created {container_id} at ({x},{y})")
        return final_result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Unexpected error creating container: {str(e)}",
            "error_code": "UNEXPECTED_ERROR",
            "provided_parameters": {
                "container_id": container_id,
                "x": x,
                "y": y,
                "width": width,
                "height": height
            },
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "create_container_tool", "ERROR", str(e))
        return error_result


async def resize_container_tool(container_id: str, width: int, height: int) -> Dict[str, Any]:
    """
    Resize an existing container with validation and intelligent feedback.
    
    Args:
        container_id: Identifier of the container to resize (must exist)
        width: New container width in pixels (must be positive integer)
        height: New container height in pixels (must be positive integer)
        
    Returns:
        Dict with operation result and detailed information
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[TOOL] resize_container_tool called with container_id={container_id}, width={width}, height={height}")
    
    log_component_entry("TOOL", "resize_container_tool", f"container_id={container_id}, width={width}, height={height}")
    
    try:
        # Basic validation
        if not isinstance(container_id, str) or not container_id.strip():
            return {
                "status": "error",
                "message": "Container ID must be a non-empty string",
                "error_code": "INVALID_CONTAINER_ID",
                "provided_container_id": container_id,
                "suggestions": [
                    "Provide a valid container identifier",
                    "Use get_canvas_state to see existing containers"
                ]
            }
        
        if not isinstance(width, int) or not isinstance(height, int):
            return {
                "status": "error",
                "message": "Width and height must be integers",
                "error_code": "INVALID_DIMENSIONS",
                "provided_width": width,
                "provided_height": height,
                "suggestions": [
                    "Provide width and height as positive integers",
                    "Example: resize_container('my_container', 300, 200)"
                ]
            }
        
        if width <= 0 or height <= 0:
            return {
                "status": "error",
                "message": "Width and height must be positive integers",
                "error_code": "INVALID_SIZE",
                "provided_width": width,
                "provided_height": height,
                "suggestions": [
                    "Use positive values greater than 0",
                    "Minimum recommended size: 50x50",
                    "Consider the canvas size and other containers when choosing dimensions"
                ]
            }
        
        # Get current canvas dimensions for context
        canvas_result = await get_canvas_dimensions_primitive()
        if canvas_result["status"] != "success":
            return {
                "status": "error",
                "message": "Failed to get current canvas dimensions",
                "error_code": "CANVAS_STATE_ERROR",
                "details": canvas_result
            }
        
        canvas_dims = canvas_result["dimensions"]
        canvas_width = canvas_dims["width"]
        canvas_height = canvas_dims["height"]
        
        # Execute the primitive operation
        if debug_mode:
            logger.debug(f"[TOOL] Calling primitive: resize_container_primitive({container_id}, {width}, {height})")
        
        log_handover("TOOL", "PRIMITIVE", "resize_container", f"container_id={container_id}, width={width}, height={height}")
        
        result = await resize_container_primitive(container_id, width, height)
        
        if debug_mode:
            logger.debug(f"[TOOL] Primitive returned: {result.get('status', 'unknown')}")
        
        if result["status"] != "success":
            # Enhance error messages with helpful suggestions
            error_code = result.get("error_code", "UNKNOWN_ERROR")
            enhanced_suggestions = []
            
            if error_code == "CONTAINER_NOT_FOUND":
                existing_ids = result.get("existing_container_ids", [])
                enhanced_suggestions = [
                    f"Container '{container_id}' does not exist",
                    "Check the container ID spelling",
                    f"Available containers: {', '.join(existing_ids) if existing_ids else 'None'}"
                ]
            elif error_code == "OUT_OF_BOUNDS":
                container_pos = result.get("container_position", {})
                x, y = container_pos.get("x", 0), container_pos.get("y", 0)
                max_width = canvas_width - x
                max_height = canvas_height - y
                enhanced_suggestions = [
                    f"Resized container would extend outside canvas bounds ({canvas_width}x{canvas_height})",
                    f"Container is at position ({x}, {y})",
                    f"Maximum size at this position: {max_width}x{max_height}",
                    "Consider reducing size or moving the container first"
                ]
            elif error_code == "OVERLAP_DETECTED":
                overlapping = result.get("overlapping_containers", [])
                enhanced_suggestions = [
                    f"Resized container would overlap with: {', '.join(overlapping)}",
                    "Try a smaller size that doesn't overlap",
                    "Consider moving other containers first",
                    "Use get_canvas_state to see container positions"
                ]
            else:
                enhanced_suggestions = [
                    "Check container parameters and try again",
                    "Ensure canvas is in a valid state"
                ]
            
            return {
                "status": "error",
                "message": result.get("error", "Failed to resize container"),
                "error_code": error_code,
                "primitive_result": result,
                "suggestions": enhanced_suggestions
            }
        
        # Calculate additional context for successful resize
        old_dims = result["old_dimensions"]
        new_dims = result["new_dimensions"]
        old_area = old_dims["width"] * old_dims["height"]
        new_area = new_dims["width"] * new_dims["height"]
        area_change_percent = ((new_area - old_area) / old_area) * 100 if old_area > 0 else 0
        
        canvas_area = canvas_width * canvas_height
        new_area_percentage = (new_area / canvas_area) * 100 if canvas_area > 0 else 0
        
        container_info = result["container"]
        
        final_result = {
            "status": "success",
            "message": f"Container '{container_id}' successfully resized from {old_dims['width']}x{old_dims['height']} to {width}x{height}",
            "operation": "resize_container",
            "container": container_info,
            "size_changes": {
                "old_dimensions": old_dims,
                "new_dimensions": new_dims,
                "width_change": width - old_dims["width"],
                "height_change": height - old_dims["height"],
                "area_change_percent": round(area_change_percent, 1)
            },
            "canvas_context": {
                "canvas_size": {"width": canvas_width, "height": canvas_height},
                "container_area_percentage": round(new_area_percentage, 1),
                "total_containers": result["total_containers"]
            },
            "positioning": {
                "position": {"x": container_info["x"], "y": container_info["y"]},
                "distance_from_edges": {
                    "left": container_info["x"],
                    "top": container_info["y"],
                    "right": canvas_width - (container_info["x"] + width),
                    "bottom": canvas_height - (container_info["y"] + height)
                }
            },
            "recommendations": [
                f"Container area {'increased' if area_change_percent > 0 else 'decreased'} by {abs(area_change_percent):.1f}%",
                f"Container now occupies {new_area_percentage:.1f}% of canvas area",
                "Container is ready for content updates or further modifications"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "resize_container_tool", "SUCCESS", f"Resized {container_id} to {width}x{height}")
        return final_result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Unexpected error resizing container: {str(e)}",
            "error_code": "UNEXPECTED_ERROR",
            "provided_parameters": {
                "container_id": container_id,
                "width": width,
                "height": height
            },
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "resize_container_tool", "ERROR", str(e))
        return error_result


async def move_container_tool(container_id: str, x: int, y: int) -> Dict[str, Any]:
    """
    Move an existing container to a new position with validation and intelligent feedback.
    
    Args:
        container_id: Identifier of the container to move (must exist)
        x: New X coordinate position on canvas (must be non-negative integer)
        y: New Y coordinate position on canvas (must be non-negative integer)
        
    Returns:
        Dict with operation result and detailed information
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[TOOL] move_container_tool called with container_id={container_id}, x={x}, y={y}")
    
    log_component_entry("TOOL", "move_container_tool", f"container_id={container_id}, x={x}, y={y}")
    
    try:
        # Basic validation
        if not isinstance(container_id, str) or not container_id.strip():
            return {
                "status": "error",
                "message": "Container ID must be a non-empty string",
                "error_code": "INVALID_CONTAINER_ID",
                "provided_container_id": container_id,
                "suggestions": [
                    "Provide a valid container identifier",
                    "Use get_canvas_state to see existing containers"
                ]
            }
        
        if not isinstance(x, int) or not isinstance(y, int):
            return {
                "status": "error",
                "message": "X and Y coordinates must be integers",
                "error_code": "INVALID_COORDINATES",
                "provided_x": x,
                "provided_y": y,
                "suggestions": [
                    "Provide X and Y as non-negative integers",
                    "Example: move_container('my_container', 150, 100)"
                ]
            }
        
        if x < 0 or y < 0:
            return {
                "status": "error",
                "message": "X and Y coordinates must be non-negative",
                "error_code": "NEGATIVE_COORDINATES",
                "provided_x": x,
                "provided_y": y,
                "suggestions": [
                    "Use coordinates >= 0",
                    "Top-left corner of canvas is (0, 0)"
                ]
            }
        
        # Get current canvas dimensions for context
        canvas_result = await get_canvas_dimensions_primitive()
        if canvas_result["status"] != "success":
            return {
                "status": "error",
                "message": "Failed to get current canvas dimensions",
                "error_code": "CANVAS_STATE_ERROR",
                "details": canvas_result
            }
        
        canvas_dims = canvas_result["dimensions"]
        canvas_width = canvas_dims["width"]
        canvas_height = canvas_dims["height"]
        
        # Execute the primitive operation
        if debug_mode:
            logger.debug(f"[TOOL] Calling primitive: move_container_primitive({container_id}, {x}, {y})")
        
        log_handover("TOOL", "PRIMITIVE", "move_container", f"container_id={container_id}, x={x}, y={y}")
        
        result = await move_container_primitive(container_id, x, y)
        
        if debug_mode:
            logger.debug(f"[TOOL] Primitive returned: {result.get('status', 'unknown')}")
        
        if result["status"] != "success":
            # Enhance error messages with helpful suggestions
            error_code = result.get("error_code", "UNKNOWN_ERROR")
            enhanced_suggestions = []
            
            if error_code == "CONTAINER_NOT_FOUND":
                existing_ids = result.get("existing_container_ids", [])
                enhanced_suggestions = [
                    f"Container '{container_id}' does not exist",
                    "Check the container ID spelling",
                    f"Available containers: {', '.join(existing_ids) if existing_ids else 'None'}"
                ]
            elif error_code == "OUT_OF_BOUNDS":
                container_size = result.get("container_size", {})
                width, height = container_size.get("width", 0), container_size.get("height", 0)
                max_x = canvas_width - width
                max_y = canvas_height - height
                enhanced_suggestions = [
                    f"Container would extend outside canvas bounds ({canvas_width}x{canvas_height})",
                    f"Container size: {width}x{height}",
                    f"Maximum position for this container: ({max_x}, {max_y})",
                    "Consider resizing the container or choosing a different position"
                ]
            elif error_code == "OVERLAP_DETECTED":
                overlapping = result.get("overlapping_containers", [])
                enhanced_suggestions = [
                    f"Container would overlap with: {', '.join(overlapping)}",
                    "Try a different position that doesn't overlap",
                    "Consider moving other containers first",
                    "Use get_canvas_state to see container positions"
                ]
            else:
                enhanced_suggestions = [
                    "Check container parameters and try again",
                    "Ensure canvas is in a valid state"
                ]
            
            return {
                "status": "error",
                "message": result.get("error", "Failed to move container"),
                "error_code": error_code,
                "primitive_result": result,
                "suggestions": enhanced_suggestions
            }
        
        # Calculate additional context for successful move
        old_pos = result["old_position"]
        new_pos = result["new_position"]
        container_info = result["container"]
        
        distance_moved = ((new_pos["x"] - old_pos["x"])**2 + (new_pos["y"] - old_pos["y"])**2)**0.5
        
        final_result = {
            "status": "success",
            "message": f"Container '{container_id}' successfully moved from ({old_pos['x']}, {old_pos['y']}) to ({x}, {y})",
            "operation": "move_container",
            "container": container_info,
            "movement": {
                "old_position": old_pos,
                "new_position": new_pos,
                "distance_moved": round(distance_moved, 1),
                "x_change": x - old_pos["x"],
                "y_change": y - old_pos["y"]
            },
            "canvas_context": {
                "canvas_size": {"width": canvas_width, "height": canvas_height},
                "total_containers": result["total_containers"]
            },
            "positioning": {
                "distance_from_edges": {
                    "left": x,
                    "top": y,
                    "right": canvas_width - (x + container_info["width"]),
                    "bottom": canvas_height - (y + container_info["height"])
                }
            },
            "recommendations": [
                f"Container moved {distance_moved:.1f} pixels",
                f"Container is now at position ({x}, {y})",
                "Container is ready for content updates or further modifications"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "move_container_tool", "SUCCESS", f"Moved {container_id} to ({x},{y})")
        return final_result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Unexpected error moving container: {str(e)}",
            "error_code": "UNEXPECTED_ERROR",
            "provided_parameters": {
                "container_id": container_id,
                "x": x,
                "y": y
            },
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "move_container_tool", "ERROR", str(e))
        return error_result


async def delete_container_tool(container_id: str) -> Dict[str, Any]:
    """
    Delete an existing container with validation and intelligent feedback.
    
    Args:
        container_id: Identifier of the container to delete (must exist)
        
    Returns:
        Dict with operation result and detailed information
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[TOOL] delete_container_tool called with container_id={container_id}")
    
    log_component_entry("TOOL", "delete_container_tool", f"container_id={container_id}")
    
    try:
        # Basic validation
        if not isinstance(container_id, str) or not container_id.strip():
            return {
                "status": "error",
                "message": "Container ID must be a non-empty string",
                "error_code": "INVALID_CONTAINER_ID",
                "provided_container_id": container_id,
                "suggestions": [
                    "Provide a valid container identifier",
                    "Use get_canvas_state to see existing containers"
                ]
            }
        
        # Get current canvas dimensions for context
        canvas_result = await get_canvas_dimensions_primitive()
        if canvas_result["status"] != "success":
            return {
                "status": "error",
                "message": "Failed to get current canvas dimensions",
                "error_code": "CANVAS_STATE_ERROR",
                "details": canvas_result
            }
        
        canvas_dims = canvas_result["dimensions"]
        canvas_width = canvas_dims["width"]
        canvas_height = canvas_dims["height"]
        
        # Execute the primitive operation
        if debug_mode:
            logger.debug(f"[TOOL] Calling primitive: delete_container_primitive({container_id})")
        
        log_handover("TOOL", "PRIMITIVE", "delete_container", f"container_id={container_id}")
        
        result = await delete_container_primitive(container_id)
        
        if debug_mode:
            logger.debug(f"[TOOL] Primitive returned: {result.get('status', 'unknown')}")
        
        if result["status"] != "success":
            # Enhance error messages with helpful suggestions
            error_code = result.get("error_code", "UNKNOWN_ERROR")
            enhanced_suggestions = []
            
            if error_code == "CONTAINER_NOT_FOUND":
                existing_ids = result.get("existing_container_ids", [])
                enhanced_suggestions = [
                    f"Container '{container_id}' does not exist",
                    "Check the container ID spelling",
                    f"Available containers: {', '.join(existing_ids) if existing_ids else 'None'}"
                ]
            else:
                enhanced_suggestions = [
                    "Check container ID and try again",
                    "Ensure canvas is in a valid state"
                ]
            
            return {
                "status": "error",
                "message": result.get("error", "Failed to delete container"),
                "error_code": error_code,
                "primitive_result": result,
                "suggestions": enhanced_suggestions
            }
        
        # Calculate additional context for successful deletion
        deleted_container = result["deleted_container"]
        container_area = deleted_container["width"] * deleted_container["height"]
        canvas_area = canvas_width * canvas_height
        freed_area_percentage = (container_area / canvas_area) * 100 if canvas_area > 0 else 0
        
        final_result = {
            "status": "success",
            "message": f"Container '{container_id}' successfully deleted",
            "operation": "delete_container",
            "deleted_container": deleted_container,
            "canvas_context": {
                "canvas_size": {"width": canvas_width, "height": canvas_height},
                "remaining_containers": result["remaining_containers"],
                "freed_area_percentage": round(freed_area_percentage, 1)
            },
            "space_freed": {
                "position": {"x": deleted_container["x"], "y": deleted_container["y"]},
                "size": {"width": deleted_container["width"], "height": deleted_container["height"]},
                "area": container_area
            },
            "recommendations": [
                f"Freed {freed_area_percentage:.1f}% of canvas area",
                f"Canvas now has {result['remaining_containers']} container(s)",
                "Space is now available for new containers"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "delete_container_tool", "SUCCESS", f"Deleted {container_id}")
        return final_result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Unexpected error deleting container: {str(e)}",
            "error_code": "UNEXPECTED_ERROR",
            "provided_parameters": {
                "container_id": container_id
            },
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "delete_container_tool", "ERROR", str(e))
        return error_result


async def clear_canvas_tool() -> Dict[str, Any]:
    """
    Clear all elements from the canvas with validation and intelligent feedback.
    
    Returns:
        Dict with operation result and detailed information
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[TOOL] clear_canvas_tool called")
    
    log_component_entry("TOOL", "clear_canvas_tool", "")
    
    try:
        # Get current canvas dimensions for context
        canvas_result = await get_canvas_dimensions_primitive()
        if canvas_result["status"] != "success":
            return {
                "status": "error",
                "message": "Failed to get current canvas dimensions",
                "error_code": "CANVAS_STATE_ERROR",
                "details": canvas_result
            }
        
        canvas_dims = canvas_result["dimensions"]
        canvas_width = canvas_dims["width"]
        canvas_height = canvas_dims["height"]
        
        # Execute the primitive operation
        if debug_mode:
            logger.debug(f"[TOOL] Calling primitive: clear_canvas_primitive()")
        
        log_handover("TOOL", "PRIMITIVE", "clear_canvas", "")
        
        result = await clear_canvas_primitive()
        
        if debug_mode:
            logger.debug(f"[TOOL] Primitive returned: {result.get('status', 'unknown')}")
        
        if result["status"] != "success":
            # Enhance error messages with helpful suggestions
            error_code = result.get("error_code", "UNKNOWN_ERROR")
            enhanced_suggestions = [
                "Check canvas state and try again",
                "Ensure canvas system is properly initialized",
                "Verify WebSocket connections are active"
            ]
            
            return {
                "status": "error",
                "message": result.get("error", "Failed to clear canvas"),
                "error_code": error_code,
                "primitive_result": result,
                "suggestions": enhanced_suggestions
            }
        
        # Calculate additional context for successful clear
        cleared_elements = result["cleared_elements"]
        canvas_context = result["canvas_context"]
        final_state = result["final_state"]
        
        containers_cleared = cleared_elements["total_containers"]
        area_cleared = cleared_elements["total_area_cleared"]
        area_percentage = canvas_context["area_cleared_percentage"]
        
        # Generate recommendations based on what was cleared
        recommendations = []
        if containers_cleared == 0:
            recommendations = [
                "Canvas was already empty",
                "Ready for new content creation",
                "All canvas space is now available"
            ]
        elif containers_cleared == 1:
            recommendations = [
                f"Cleared 1 container, freed {area_percentage:.1f}% of canvas space",
                "Canvas is now ready for new content",
                "Consider the layout for your next elements"
            ]
        else:
            recommendations = [
                f"Cleared {containers_cleared} containers, freed {area_percentage:.1f}% of canvas space",
                "Canvas is now completely empty and ready for new content",
                "You have full canvas space available for new layouts"
            ]
        
        final_result = {
            "status": "success",
            "message": f"Canvas successfully cleared - removed {containers_cleared} container(s)",
            "operation": "clear_canvas",
            "cleared_summary": {
                "containers_removed": containers_cleared,
                "total_area_freed": area_cleared,
                "area_percentage_freed": round(area_percentage, 1),
                "container_details": cleared_elements["containers"]
            },
            "canvas_context": {
                "canvas_size": {"width": canvas_width, "height": canvas_height},
                "canvas_area": canvas_context["canvas_area"],
                "is_empty": final_state["is_empty"]
            },
            "space_analysis": {
                "available_area": canvas_context["canvas_area"],
                "utilization_before": f"{area_percentage:.1f}%",
                "utilization_after": "0%",
                "space_freed": area_cleared
            },
            "recommendations": recommendations,
            "next_actions": [
                "Canvas is ready for new container creation",
                "Consider your layout strategy for new elements",
                "Use create_container() to add new elements"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "clear_canvas_tool", "SUCCESS", f"Cleared {containers_cleared} containers")
        return final_result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Unexpected error clearing canvas: {str(e)}",
            "error_code": "UNEXPECTED_ERROR",
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "clear_canvas_tool", "ERROR", str(e))
        return error_result 