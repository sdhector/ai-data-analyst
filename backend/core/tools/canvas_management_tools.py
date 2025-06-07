"""
Canvas Management Tools

High-level canvas management operations exposed to the AI.
These tools orchestrate primitives with validation and provide rich responses.
"""

import logging
import os
from typing import Dict, Any, Optional
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
from ..canvas_bridge import canvas_bridge
from ..utilities import (
    log_component_entry,
    log_component_exit,
    log_handover,
    AutoLayoutEngine,
    LayoutConfiguration,
    ContainerLayout,
    create_layout_engine
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


async def create_container_tool(
    container_id: str, 
    x: Optional[int] = None, 
    y: Optional[int] = None, 
    width: Optional[int] = None, 
    height: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a new container with intelligent auto-layout support.
    
    This function automatically adapts based on the current layout mode:
    - Auto mode: Position and size parameters are optional (auto-calculated)
    - Manual mode: All position and size parameters are required
    
    Args:
        container_id: Unique identifier for the container (required)
        x: X coordinate position (optional in auto mode, required in manual mode)
        y: Y coordinate position (optional in auto mode, required in manual mode)
        width: Container width in pixels (optional in auto mode, required in manual mode)
        height: Container height in pixels (optional in auto mode, required in manual mode)
        
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
        
        # Get current layout state to determine behavior
        layout_state = canvas_bridge.get_layout_state()
        
        # Check if we should use auto-layout
        use_auto_layout = (
            layout_state["auto_layout_enabled"] and 
            layout_state["layout_mode"] == "auto" and
            (x is None or y is None or width is None or height is None)
        )
        
        if debug_mode:
            logger.debug(f"[TOOL] Layout mode: {layout_state['layout_mode']}, Auto-layout enabled: {layout_state['auto_layout_enabled']}, Use auto: {use_auto_layout}")
        
        # If we should use auto-layout, delegate to the auto-layout system
        if use_auto_layout:
            if debug_mode:
                logger.debug(f"[TOOL] Using auto-layout for container creation")
            
            # Get existing containers for layout calculation
            existing_containers = canvas_bridge.canvas_state.get("containers", {})
            container_count = len(existing_containers) + 1  # +1 for the new container
            
            # Create layout configuration
            config = LayoutConfiguration(
                canvas_width=canvas_width,
                canvas_height=canvas_height,
                container_gap=layout_state["preferences"]["container_gap"],
                canvas_padding=layout_state["preferences"]["canvas_padding"] or 20,
                aspect_ratio=1.0,  # Square containers by default
                min_container_size=50,
                max_container_size=min(canvas_width, canvas_height) // 2
            )
            
            # Find a good position for just this container without moving existing ones
            layout_engine = create_layout_engine()
            existing_container_list = list(existing_containers.values())
            new_container_layout = layout_engine.find_available_position(
                existing_container_list, config, container_id
            )
            
            if new_container_layout is None:
                return {
                    "status": "error",
                    "message": "Auto-layout failed: No available space for new container",
                    "error_code": "AUTO_LAYOUT_NO_SPACE",
                    "suggestions": [
                        "Try manual positioning with explicit coordinates",
                        "Consider increasing canvas size",
                        "Clear some existing containers to make space"
                    ]
                }
            
            # Use auto-calculated values, but allow manual overrides
            x = x if x is not None else new_container_layout.x
            y = y if y is not None else new_container_layout.y  
            width = width if width is not None else new_container_layout.width
            height = height if height is not None else new_container_layout.height
        
        # Manual mode - all parameters are required
        if x is None or y is None or width is None or height is None:
            return {
                "status": "error",
                "message": "Manual layout mode requires all position and size parameters",
                "error_code": "MISSING_MANUAL_PARAMETERS",
                "current_mode": layout_state["layout_mode"],
                "auto_layout_enabled": layout_state["auto_layout_enabled"],
                "missing_parameters": [
                    param for param, value in [("x", x), ("y", y), ("width", width), ("height", height)]
                    if value is None
                ],
                "suggestions": [
                    "Provide all parameters: x, y, width, height",
                    "Or switch to auto-layout mode with set_layout_mode('auto')",
                    "Example: create_container('my_container', 100, 50, 200, 150)",
                    "Auto mode example: Just use create_container('my_container') and position will be calculated automatically"
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
            "layout_info": {
                "mode_used": "manual",
                "layout_mode": layout_state["layout_mode"],
                "auto_layout_enabled": layout_state["auto_layout_enabled"]
            },
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
                f"Manual positioning used - container occupies {area_percentage:.1f}% of canvas area",
                f"Canvas now has {result['total_containers']} container(s)",
                "Container is ready for content or further modifications",
                "Tip: Switch to auto-layout mode for automatic positioning of future containers"
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


# ================================
# LAYOUT MANAGEMENT TOOLS
# ================================

async def set_layout_mode_tool(mode: str, apply_to_existing: bool = False, force: bool = False) -> Dict[str, Any]:
    """
    Set the canvas layout mode between auto-layout and manual positioning.
    
    Args:
        mode: Layout mode - "auto" or "manual"
        apply_to_existing: Whether to apply mode change to existing containers
        force: Skip confirmation prompts (use with caution)
        
    Returns:
        Dict with operation result and detailed information
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[TOOL] set_layout_mode_tool called with mode={mode}, apply_to_existing={apply_to_existing}, force={force}")
    
    log_component_entry("TOOL", "set_layout_mode_tool", f"mode={mode}, apply_to_existing={apply_to_existing}")
    
    try:
        # Validate mode parameter
        if mode not in ["auto", "manual"]:
            return {
                "status": "error",
                "message": f"Invalid layout mode: '{mode}'. Must be 'auto' or 'manual'.",
                "error_code": "INVALID_MODE",
                "valid_modes": ["auto", "manual"],
                "provided_mode": mode,
                "timestamp": datetime.now().isoformat()
            }
        
        # Get current layout state for context
        current_layout_state = canvas_bridge.get_layout_state()
        current_mode = current_layout_state["layout_mode"]
        container_count = current_layout_state["container_count"]
        
        # Call canvas bridge to set layout mode
        if debug_mode:
            logger.debug(f"[TOOL] Calling canvas_bridge.set_layout_mode()")
        
        log_handover("TOOL", "CANVAS_BRIDGE", "set_layout_mode", f"mode={mode}")
        
        result = await canvas_bridge.set_layout_mode(
            mode=mode,
            user_confirmed=force,
            apply_to_existing=apply_to_existing
        )
        
        if debug_mode:
            logger.debug(f"[TOOL] Canvas bridge returned: {result.get('status', 'unknown')}")
        
        # Handle confirmation required
        if result.get("status") == "requires_confirmation":
            confirmation_result = {
                "status": "requires_confirmation",
                "message": result["message"],
                "action_required": result["action_required"],
                "current_state": {
                    "current_mode": current_mode,
                    "requested_mode": mode,
                    "container_count": container_count,
                    "will_affect_existing": apply_to_existing
                },
                "pending_operation": result["pending_operation"],
                "next_steps": [
                    "Confirm the mode change to proceed",
                    "Or call with force=True to skip confirmation"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            log_component_exit("TOOL", "set_layout_mode_tool", "CONFIRMATION_REQUIRED", f"Mode change requires confirmation")
            return confirmation_result
        
        # Handle errors
        if result.get("status") == "error":
            return {
                "status": "error",
                "message": result.get("error", "Failed to set layout mode"),
                "error_code": "MODE_CHANGE_FAILED",
                "current_mode": current_mode,
                "requested_mode": mode,
                "suggestions": [
                    "Check that the mode parameter is valid",
                    "Ensure canvas is in a valid state",
                    "Try again with different parameters"
                ],
                "timestamp": datetime.now().isoformat()
            }
        
        # Handle successful mode change
        if result.get("status") == "success":
            new_mode = result["mode"]
            no_change = result.get("no_change", False)
            
            # Build response based on whether change occurred
            if no_change:
                final_result = {
                    "status": "success",
                    "message": f"Layout mode already set to '{new_mode}'",
                    "operation": "set_layout_mode",
                    "mode_info": {
                        "current_mode": new_mode,
                        "auto_layout_enabled": result.get("auto_layout_enabled", current_layout_state["auto_layout_enabled"]),
                        "no_change_made": True
                    },
                    "container_context": {
                        "total_containers": container_count,
                        "containers_affected": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Calculate impact and provide detailed feedback
                containers_affected = result.get("containers_to_reposition", 0) if apply_to_existing else 0
                manual_container_count = result.get("manual_container_count", 0)
                
                # Generate mode-specific recommendations
                if new_mode == "auto":
                    recommendations = [
                        "New containers will be automatically positioned",
                        "Container layouts will be optimized for space efficiency",
                        "Use create_container() without position parameters"
                    ]
                    if containers_affected > 0:
                        recommendations.insert(0, f"All {containers_affected} existing containers will be repositioned")
                else:  # manual mode
                    recommendations = [
                        "New containers will require explicit positioning (x, y, width, height)",
                        "No automatic layout optimization will be applied", 
                        "You have full control over container placement"
                    ]
                    if apply_to_existing:
                        recommendations.insert(0, f"All {container_count} existing containers marked as manually positioned")
                
                final_result = {
                    "status": "success",
                    "message": result["message"],
                    "operation": "set_layout_mode",
                    "mode_change": {
                        "from_mode": current_mode,
                        "to_mode": new_mode,
                        "auto_layout_enabled": result.get("auto_layout_enabled", False)
                    },
                    "container_impact": {
                        "total_containers": container_count,
                        "existing_containers_affected": result.get("existing_containers_affected", False),
                        "containers_to_reposition": containers_affected,
                        "manual_container_count": manual_container_count
                    },
                    "layout_context": {
                        "new_container_behavior": "auto-positioned" if new_mode == "auto" else "requires explicit positioning",
                        "existing_container_status": "repositioned" if apply_to_existing and containers_affected > 0 else "unchanged"
                    },
                    "recommendations": recommendations,
                    "timestamp": datetime.now().isoformat()
                }
            
            log_component_exit("TOOL", "set_layout_mode_tool", "SUCCESS", f"Mode set to {new_mode}")
            return final_result
        
        # Unexpected response
        return {
            "status": "error",
            "message": "Unexpected response from layout mode change",
            "error_code": "UNEXPECTED_RESPONSE",
            "bridge_result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Unexpected error setting layout mode: {str(e)}",
            "error_code": "UNEXPECTED_ERROR",
            "provided_parameters": {
                "mode": mode,
                "apply_to_existing": apply_to_existing,
                "force": force
            },
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "set_layout_mode_tool", "ERROR", str(e))
        return error_result


async def get_layout_mode_tool() -> Dict[str, Any]:
    """
    Get current layout mode and container positioning information.
    
    Returns:
        Dict with current layout state and detailed information
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[TOOL] get_layout_mode_tool called")
    
    log_component_entry("TOOL", "get_layout_mode_tool", "")
    
    try:
        # Get layout state from canvas bridge
        if debug_mode:
            logger.debug(f"[TOOL] Getting layout state from canvas_bridge")
        
        log_handover("TOOL", "CANVAS_BRIDGE", "get_layout_state", "")
        
        layout_state = canvas_bridge.get_layout_state()
        
        if debug_mode:
            logger.debug(f"[TOOL] Retrieved layout state successfully")
        
        # Get canvas dimensions for additional context
        canvas_result = await get_canvas_dimensions_primitive()
        if canvas_result["status"] == "success":
            canvas_dims = canvas_result["dimensions"]
            canvas_width = canvas_dims["width"]
            canvas_height = canvas_dims["height"]
            canvas_area = canvas_width * canvas_height
        else:
            canvas_width = canvas_height = canvas_area = 0
        
        # Analyze container distribution
        container_count = layout_state["container_count"]
        manual_count = len(layout_state["manual_containers"])
        auto_count = container_count - manual_count
        
        # Calculate layout efficiency if containers exist
        layout_analysis = {}
        if container_count > 0:
            manual_percentage = (manual_count / container_count) * 100
            auto_percentage = (auto_count / container_count) * 100
            
            layout_analysis = {
                "total_containers": container_count,
                "auto_positioned_containers": auto_count,
                "manually_positioned_containers": manual_count,
                "auto_percentage": round(auto_percentage, 1),
                "manual_percentage": round(manual_percentage, 1),
                "mixed_layout": manual_count > 0 and auto_count > 0
            }
        
        # Generate mode-specific insights
        current_mode = layout_state["layout_mode"]
        auto_enabled = layout_state["auto_layout_enabled"]
        
        if current_mode == "auto" and auto_enabled:
            mode_insights = [
                "Auto-layout is active - new containers will be automatically positioned",
                "Container layouts are optimized for space efficiency",
                "Position and size parameters are optional for new containers"
            ]
        elif current_mode == "manual":
            mode_insights = [
                "Manual positioning mode is active",
                "All position and size parameters are required for new containers",
                "No automatic layout optimization is applied"
            ]
        else:
            mode_insights = [
                "Layout mode state is inconsistent",
                "Consider resetting layout mode for proper operation"
            ]
        
        # Add container-specific insights
        if container_count == 0:
            mode_insights.append("Canvas is empty - ready for new content")
        elif layout_analysis.get("mixed_layout", False):
            mode_insights.append(f"Mixed layout detected: {auto_count} auto-positioned, {manual_count} manual")
        
        # Generate recommendations
        recommendations = []
        if current_mode == "auto" and container_count > 0:
            recommendations.extend([
                "Use create_container('id') for automatic positioning",
                "Consider set_layout_mode('manual') for precise control"
            ])
        elif current_mode == "manual":
            recommendations.extend([
                "Use create_container('id', x, y, width, height) for manual positioning",
                "Consider set_layout_mode('auto') for automatic optimization"
            ])
        
        if container_count == 0:
            recommendations.append("Start creating containers to build your layout")
        elif container_count > 10:
            recommendations.append("Consider using clear_canvas() if layout becomes too complex")
        
        final_result = {
            "status": "success",
            "message": f"Current layout mode: {current_mode}",
            "operation": "get_layout_mode",
            "layout_mode_info": {
                "current_mode": current_mode,
                "auto_layout_enabled": auto_enabled,
                "layout_engine_version": layout_state["layout_engine_version"],
                "last_auto_layout_time": layout_state["last_auto_layout_time"]
            },
            "container_analysis": layout_analysis if container_count > 0 else {
                "total_containers": 0,
                "message": "No containers on canvas"
            },
            "canvas_context": {
                "canvas_size": {"width": canvas_width, "height": canvas_height},
                "canvas_area": canvas_area,
                "container_creation_order": layout_state["container_creation_order"]
            },
            "user_preferences": layout_state["preferences"],
            "mode_insights": mode_insights,
            "recommendations": recommendations,
            "available_actions": [
                "set_layout_mode() - Change layout mode",
                "create_container() - Add new container",
                "clear_canvas() - Start fresh"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "get_layout_mode_tool", "SUCCESS", f"Retrieved layout mode: {current_mode}")
        return final_result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Unexpected error getting layout mode: {str(e)}",
            "error_code": "UNEXPECTED_ERROR",
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("TOOL", "get_layout_mode_tool", "ERROR", str(e))
        return error_result


