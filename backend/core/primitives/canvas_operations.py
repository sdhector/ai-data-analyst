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


async def create_container_primitive(container_id: str, x: int, y: int, width: int, height: int) -> Dict[str, Any]:
    """
    Create a new container directly.
    
    Args:
        container_id: Unique identifier for the container
        x: X coordinate position on canvas
        y: Y coordinate position on canvas
        width: Container width in pixels
        height: Container height in pixels
        
    Returns:
        Dict with operation result and details
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[PRIMITIVE] create_container_primitive STARTED with container_id={container_id}, x={x}, y={y}, width={width}, height={height}")
    
    log_component_entry("PRIMITIVE", "create_container_primitive", f"container_id={container_id}, x={x}, y={y}, width={width}, height={height}")
    
    try:
        # Validate container_id uniqueness
        existing_containers = canvas_bridge.canvas_state.get("containers", {})
        if container_id in existing_containers:
            error_result = {
                "status": "error",
                "operation": "create_container",
                "error": f"Container ID '{container_id}' already exists",
                "error_code": "DUPLICATE_ID",
                "existing_container_ids": list(existing_containers.keys()),
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "create_container_primitive", "ERROR", f"Duplicate ID: {container_id}")
            return error_result
        
        # Validate coordinates and dimensions
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            error_result = {
                "status": "error",
                "operation": "create_container",
                "error": "X and Y coordinates must be numeric",
                "error_code": "INVALID_COORDINATES",
                "provided_x": x,
                "provided_y": y,
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "create_container_primitive", "ERROR", "Invalid coordinates")
            return error_result
        
        if not isinstance(width, (int, float)) or not isinstance(height, (int, float)) or width <= 0 or height <= 0:
            error_result = {
                "status": "error",
                "operation": "create_container",
                "error": "Width and height must be positive numeric values",
                "error_code": "INVALID_DIMENSIONS",
                "provided_width": width,
                "provided_height": height,
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "create_container_primitive", "ERROR", "Invalid dimensions")
            return error_result
        
        # Convert to integers for consistency
        x, y, width, height = int(x), int(y), int(width), int(height)
        
        # Validate placement within canvas bounds
        canvas_size = canvas_bridge.get_canvas_size()
        canvas_width = canvas_size.get('width', 800)
        canvas_height = canvas_size.get('height', 600)
        
        if x < 0 or y < 0 or x + width > canvas_width or y + height > canvas_height:
            error_result = {
                "status": "error",
                "operation": "create_container",
                "error": "Container bounding box extends outside canvas boundaries",
                "error_code": "OUT_OF_BOUNDS",
                "canvas_size": {"width": canvas_width, "height": canvas_height},
                "container_bounds": {"x": x, "y": y, "width": width, "height": height},
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "create_container_primitive", "ERROR", "Out of bounds")
            return error_result
        
        # Validate no overlap with existing containers
        existing_container_list = canvas_bridge.get_existing_containers()
        overlapping_containers = []
        
        for existing in existing_container_list:
            if canvas_bridge.check_overlap(x, y, width, height, 
                                         existing['x'], existing['y'], 
                                         existing['width'], existing['height']):
                overlapping_containers.append(existing['id'])
        
        if overlapping_containers:
            error_result = {
                "status": "error",
                "operation": "create_container",
                "error": "Container overlaps with existing containers",
                "error_code": "OVERLAP_DETECTED",
                "overlapping_containers": overlapping_containers,
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "create_container_primitive", "ERROR", f"Overlaps with: {overlapping_containers}")
            return error_result
        
        # Generate unique command ID for tracking
        import uuid
        command_id = f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Create container in canvas state
        canvas_bridge.canvas_state["containers"][container_id] = {
            "id": container_id,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "created_at": datetime.now().isoformat()
        }
        canvas_bridge.canvas_state["last_updated"] = datetime.now().isoformat()
        
        # Broadcast container creation command to frontend
        create_message = {
            "type": "canvas_command",
            "command": "create_container",
            "command_id": command_id,
            "data": {
                "container_id": container_id,
                "x": x,
                "y": y,
                "width": width,
                "height": height
            }
        }
        
        # Check if there are any WebSocket connections
        connection_count = len(canvas_bridge.websocket_connections)
        print(f"[PRIMITIVE] Broadcasting container creation to {connection_count} WebSocket connection(s)")
        
        if connection_count == 0:
            print("[WARNING] No WebSocket connections found - frontend may not be connected!")
        
        # Track the pending command
        canvas_bridge.track_pending_command(command_id, "create_container", {
            "container_id": container_id,
            "x": x,
            "y": y,
            "width": width,
            "height": height
        })
        
        await canvas_bridge.broadcast_to_frontend(create_message)
        
        print(f"[PRIMITIVE] Container '{container_id}' created at ({x}, {y}) with size {width}x{height}")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] create_container_primitive COMPLETED successfully")
        
        result = {
            "status": "success",
            "operation": "create_container",
            "container": {
                "id": container_id,
                "x": x,
                "y": y,
                "width": width,
                "height": height
            },
            "canvas_size": {"width": canvas_width, "height": canvas_height},
            "total_containers": len(canvas_bridge.canvas_state["containers"]),
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "create_container_primitive", "SUCCESS", f"Created {container_id} at ({x},{y})")
        return result
        
    except Exception as e:
        print(f"[PRIMITIVE ERROR] Failed to create container: {e}")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] create_container_primitive FAILED: {e}")
        
        error_result = {
            "status": "error",
            "operation": "create_container",
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR",
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "create_container_primitive", "ERROR", str(e))
        return error_result


async def resize_container_primitive(container_id: str, width: int, height: int) -> Dict[str, Any]:
    """
    Resize an existing container directly.
    
    Args:
        container_id: Identifier of the container to resize
        width: New container width in pixels
        height: New container height in pixels
        
    Returns:
        Dict with operation result and details
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[PRIMITIVE] resize_container_primitive STARTED with container_id={container_id}, width={width}, height={height}")
    
    log_component_entry("PRIMITIVE", "resize_container_primitive", f"container_id={container_id}, width={width}, height={height}")
    
    try:
        # Validate container exists
        existing_containers = canvas_bridge.canvas_state.get("containers", {})
        if container_id not in existing_containers:
            error_result = {
                "status": "error",
                "operation": "resize_container",
                "error": f"Container ID '{container_id}' does not exist",
                "error_code": "CONTAINER_NOT_FOUND",
                "existing_container_ids": list(existing_containers.keys()),
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "resize_container_primitive", "ERROR", f"Container not found: {container_id}")
            return error_result
        
        # Validate dimensions
        if not isinstance(width, (int, float)) or not isinstance(height, (int, float)) or width <= 0 or height <= 0:
            error_result = {
                "status": "error",
                "operation": "resize_container",
                "error": "Width and height must be positive numeric values",
                "error_code": "INVALID_DIMENSIONS",
                "provided_width": width,
                "provided_height": height,
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "resize_container_primitive", "ERROR", "Invalid dimensions")
            return error_result
        
        # Convert to integers for consistency
        width, height = int(width), int(height)
        
        # Get current container data
        current_container = existing_containers[container_id]
        current_x = current_container["x"]
        current_y = current_container["y"]
        old_width = current_container["width"]
        old_height = current_container["height"]
        
        # Validate placement within canvas bounds
        canvas_size = canvas_bridge.get_canvas_size()
        canvas_width = canvas_size.get('width', 800)
        canvas_height = canvas_size.get('height', 600)
        
        if current_x < 0 or current_y < 0 or current_x + width > canvas_width or current_y + height > canvas_height:
            error_result = {
                "status": "error",
                "operation": "resize_container",
                "error": "Resized container bounding box extends outside canvas boundaries",
                "error_code": "OUT_OF_BOUNDS",
                "canvas_size": {"width": canvas_width, "height": canvas_height},
                "container_position": {"x": current_x, "y": current_y},
                "new_dimensions": {"width": width, "height": height},
                "new_bounds": {"x": current_x, "y": current_y, "width": width, "height": height},
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "resize_container_primitive", "ERROR", "Out of bounds")
            return error_result
        
        # Validate no overlap with other existing containers
        existing_container_list = canvas_bridge.get_existing_containers()
        overlapping_containers = []
        
        for existing in existing_container_list:
            # Skip the container we're resizing
            if existing['id'] == container_id:
                continue
                
            if canvas_bridge.check_overlap(current_x, current_y, width, height, 
                                         existing['x'], existing['y'], 
                                         existing['width'], existing['height']):
                overlapping_containers.append(existing['id'])
        
        if overlapping_containers:
            error_result = {
                "status": "error",
                "operation": "resize_container",
                "error": "Resized container would overlap with existing containers",
                "error_code": "OVERLAP_DETECTED",
                "overlapping_containers": overlapping_containers,
                "container_position": {"x": current_x, "y": current_y},
                "new_dimensions": {"width": width, "height": height},
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "resize_container_primitive", "ERROR", f"Overlaps with: {overlapping_containers}")
            return error_result
        
        # Generate unique command ID for tracking
        import uuid
        command_id = f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Update container in canvas state
        canvas_bridge.canvas_state["containers"][container_id].update({
            "width": width,
            "height": height,
            "modified_at": datetime.now().isoformat()
        })
        canvas_bridge.canvas_state["last_updated"] = datetime.now().isoformat()
        
        # Broadcast container resize command to frontend
        resize_message = {
            "type": "canvas_command",
            "command": "resize_container",
            "command_id": command_id,
            "data": {
                "container_id": container_id,
                "x": current_x,
                "y": current_y,
                "width": width,
                "height": height,
                "old_width": old_width,
                "old_height": old_height
            }
        }
        
        # Check if there are any WebSocket connections
        connection_count = len(canvas_bridge.websocket_connections)
        print(f"[PRIMITIVE] Broadcasting container resize to {connection_count} WebSocket connection(s)")
        
        if connection_count == 0:
            print("[WARNING] No WebSocket connections found - frontend may not be connected!")
        
        # Track the pending command
        canvas_bridge.track_pending_command(command_id, "resize_container", {
            "container_id": container_id,
            "x": current_x,
            "y": current_y,
            "width": width,
            "height": height,
            "old_width": old_width,
            "old_height": old_height
        })
        
        await canvas_bridge.broadcast_to_frontend(resize_message)
        
        print(f"[PRIMITIVE] Container '{container_id}' resized from {old_width}x{old_height} to {width}x{height}")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] resize_container_primitive COMPLETED successfully")
        
        result = {
            "status": "success",
            "operation": "resize_container",
            "container": {
                "id": container_id,
                "x": current_x,
                "y": current_y,
                "width": width,
                "height": height
            },
            "old_dimensions": {"width": old_width, "height": old_height},
            "new_dimensions": {"width": width, "height": height},
            "canvas_size": {"width": canvas_width, "height": canvas_height},
            "total_containers": len(canvas_bridge.canvas_state["containers"]),
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "resize_container_primitive", "SUCCESS", f"Resized {container_id} to {width}x{height}")
        return result
        
    except Exception as e:
        print(f"[PRIMITIVE ERROR] Failed to resize container: {e}")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] resize_container_primitive FAILED: {e}")
        
        error_result = {
            "status": "error",
            "operation": "resize_container",
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR",
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "resize_container_primitive", "ERROR", str(e))
        return error_result 