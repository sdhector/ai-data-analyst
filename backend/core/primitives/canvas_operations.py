"""
Canvas Operations Primitives

Core atomic operations for canvas management.
These functions directly manipulate canvas state with minimal validation.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Tuple
from datetime import datetime

# Import canvas bridge for direct state manipulation
from ..canvas_bridge import canvas_bridge
from ..utilities import (
    log_component_entry,
    log_component_exit
)


async def set_canvas_dimensions_primitive(width: int, height: int) -> Dict[str, Any]:
    """
    Set canvas dimensions directly.
    
    Args:
        width: New canvas width in pixels
        height: New canvas height in pixels
        
    Returns:
        Dict with operation result and details
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[PRIMITIVE] ⚙️ set_canvas_dimensions_primitive STARTED with width={width}, height={height}")
    
    log_component_entry("PRIMITIVE", "set_canvas_dimensions_primitive", f"width={width}, height={height}")
    
    try:
        # Get current canvas state
        current_size = canvas_bridge.get_canvas_size()
        old_width = current_size.get('width', 800)
        old_height = current_size.get('height', 600)
        
        # Update canvas state directly
        canvas_bridge.canvas_state["canvas_size"] = {
            "width": width,
            "height": height
        }
        canvas_bridge.canvas_state["last_updated"] = datetime.now().isoformat()
        
        # Generate unique command ID for tracking
        import uuid
        command_id = f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Broadcast canvas resize command to frontend
        resize_message = {
            "type": "canvas_command",
            "command": "edit_canvas_size",  # Fixed: frontend expects "edit_canvas_size"
            "command_id": command_id,
            "data": {
                "width": width,
                "height": height,
                "old_width": old_width,
                "old_height": old_height
            }
        }
        
        # Check if there are any WebSocket connections
        connection_count = len(canvas_bridge.websocket_connections)
        print(f"[PRIMITIVE] Broadcasting resize to {connection_count} WebSocket connection(s)")
        
        if connection_count == 0:
            print("[WARNING] No WebSocket connections found - frontend may not be connected!")
        
        # Track the pending command
        canvas_bridge.track_pending_command(command_id, "edit_canvas_size", {
            "width": width,
            "height": height,
            "old_width": old_width,
            "old_height": old_height
        })
        
        await canvas_bridge.broadcast_to_frontend(resize_message)
        
        print(f"[PRIMITIVE] Canvas dimensions set to {width}x{height} (was {old_width}x{old_height})")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] ✅ set_canvas_dimensions_primitive COMPLETED successfully")
        
        result = {
            "status": "success",
            "operation": "set_canvas_dimensions",
            "old_dimensions": {"width": old_width, "height": old_height},
            "new_dimensions": {"width": width, "height": height},
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "set_canvas_dimensions_primitive", "SUCCESS", f"Set to {width}x{height}")
        return result
        
    except Exception as e:
        print(f"[PRIMITIVE ERROR] Failed to set canvas dimensions: {e}")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] ❌ set_canvas_dimensions_primitive FAILED: {e}")
        
        error_result = {
            "status": "error",
            "operation": "set_canvas_dimensions",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "set_canvas_dimensions_primitive", "ERROR", str(e))
        return error_result


async def get_canvas_dimensions_primitive() -> Dict[str, Any]:
    """
    Get current canvas dimensions.
    
    Returns:
        Dict with current canvas dimensions
    """
    log_component_entry("PRIMITIVE", "get_canvas_dimensions_primitive", "")
    
    try:
        current_size = canvas_bridge.get_canvas_size()
        
        result = {
            "status": "success",
            "operation": "get_canvas_dimensions",
            "dimensions": current_size,
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "get_canvas_dimensions_primitive", "SUCCESS", f"Retrieved {current_size}")
        return result
        
    except Exception as e:
        print(f"[PRIMITIVE ERROR] Failed to get canvas dimensions: {e}")
        error_result = {
            "status": "error",
            "operation": "get_canvas_dimensions",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "get_canvas_dimensions_primitive", "ERROR", str(e))
        return error_result 