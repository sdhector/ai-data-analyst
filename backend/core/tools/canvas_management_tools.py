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
    get_canvas_dimensions_primitive
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