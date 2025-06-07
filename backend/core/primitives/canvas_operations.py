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


async def move_container_primitive(container_id: str, x: int, y: int) -> Dict[str, Any]:
    """
    Move an existing container to a new position directly.
    
    Args:
        container_id: Identifier of the container to move
        x: New X coordinate position on canvas
        y: New Y coordinate position on canvas
        
    Returns:
        Dict with operation result and details
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[PRIMITIVE] move_container_primitive STARTED with container_id={container_id}, x={x}, y={y}")
    
    log_component_entry("PRIMITIVE", "move_container_primitive", f"container_id={container_id}, x={x}, y={y}")
    
    try:
        # Validate container exists
        existing_containers = canvas_bridge.canvas_state.get("containers", {})
        if container_id not in existing_containers:
            error_result = {
                "status": "error",
                "operation": "move_container",
                "error": f"Container ID '{container_id}' does not exist",
                "error_code": "CONTAINER_NOT_FOUND",
                "existing_container_ids": list(existing_containers.keys()),
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "move_container_primitive", "ERROR", f"Container not found: {container_id}")
            return error_result
        
        # Validate coordinates
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            error_result = {
                "status": "error",
                "operation": "move_container",
                "error": "X and Y coordinates must be numeric",
                "error_code": "INVALID_COORDINATES",
                "provided_x": x,
                "provided_y": y,
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "move_container_primitive", "ERROR", "Invalid coordinates")
            return error_result
        
        # Convert to integers for consistency
        x, y = int(x), int(y)
        
        # Get current container data
        current_container = existing_containers[container_id]
        old_x = current_container["x"]
        old_y = current_container["y"]
        width = current_container["width"]
        height = current_container["height"]
        
        # Validate placement within canvas bounds
        canvas_size = canvas_bridge.get_canvas_size()
        canvas_width = canvas_size.get('width', 800)
        canvas_height = canvas_size.get('height', 600)
        
        if x < 0 or y < 0 or x + width > canvas_width or y + height > canvas_height:
            error_result = {
                "status": "error",
                "operation": "move_container",
                "error": "Moved container bounding box extends outside canvas boundaries",
                "error_code": "OUT_OF_BOUNDS",
                "canvas_size": {"width": canvas_width, "height": canvas_height},
                "container_size": {"width": width, "height": height},
                "new_position": {"x": x, "y": y},
                "new_bounds": {"x": x, "y": y, "width": width, "height": height},
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "move_container_primitive", "ERROR", "Out of bounds")
            return error_result
        
        # Validate no overlap with other existing containers
        existing_container_list = canvas_bridge.get_existing_containers()
        overlapping_containers = []
        
        for existing in existing_container_list:
            # Skip the container we're moving
            if existing['id'] == container_id:
                continue
                
            if canvas_bridge.check_overlap(x, y, width, height, 
                                         existing['x'], existing['y'], 
                                         existing['width'], existing['height']):
                overlapping_containers.append(existing['id'])
        
        if overlapping_containers:
            error_result = {
                "status": "error",
                "operation": "move_container",
                "error": "Moved container would overlap with existing containers",
                "error_code": "OVERLAP_DETECTED",
                "overlapping_containers": overlapping_containers,
                "new_position": {"x": x, "y": y},
                "container_size": {"width": width, "height": height},
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "move_container_primitive", "ERROR", f"Overlaps with: {overlapping_containers}")
            return error_result
        
        # Generate unique command ID for tracking
        import uuid
        command_id = f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Update container position in canvas state
        canvas_bridge.canvas_state["containers"][container_id].update({
            "x": x,
            "y": y,
            "modified_at": datetime.now().isoformat()
        })
        canvas_bridge.canvas_state["last_updated"] = datetime.now().isoformat()
        
        # Broadcast container move command to frontend
        move_message = {
            "type": "canvas_command",
            "command": "move_container",
            "command_id": command_id,
            "data": {
                "container_id": container_id,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "old_x": old_x,
                "old_y": old_y
            }
        }
        
        # Check if there are any WebSocket connections
        connection_count = len(canvas_bridge.websocket_connections)
        print(f"[PRIMITIVE] Broadcasting container move to {connection_count} WebSocket connection(s)")
        
        if connection_count == 0:
            print("[WARNING] No WebSocket connections found - frontend may not be connected!")
        
        # Track the pending command
        canvas_bridge.track_pending_command(command_id, "move_container", {
            "container_id": container_id,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "old_x": old_x,
            "old_y": old_y
        })
        
        await canvas_bridge.broadcast_to_frontend(move_message)
        
        print(f"[PRIMITIVE] Container '{container_id}' moved from ({old_x}, {old_y}) to ({x}, {y})")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] move_container_primitive COMPLETED successfully")
        
        result = {
            "status": "success",
            "operation": "move_container",
            "container": {
                "id": container_id,
                "x": x,
                "y": y,
                "width": width,
                "height": height
            },
            "old_position": {"x": old_x, "y": old_y},
            "new_position": {"x": x, "y": y},
            "canvas_size": {"width": canvas_width, "height": canvas_height},
            "total_containers": len(canvas_bridge.canvas_state["containers"]),
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "move_container_primitive", "SUCCESS", f"Moved {container_id} to ({x},{y})")
        return result
        
    except Exception as e:
        print(f"[PRIMITIVE ERROR] Failed to move container: {e}")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] move_container_primitive FAILED: {e}")
        
        error_result = {
            "status": "error",
            "operation": "move_container",
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR",
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "move_container_primitive", "ERROR", str(e))
        return error_result


async def delete_container_primitive(container_id: str) -> Dict[str, Any]:
    """
    Delete an existing container directly.
    
    Args:
        container_id: Identifier of the container to delete
        
    Returns:
        Dict with operation result and details
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[PRIMITIVE] delete_container_primitive STARTED with container_id={container_id}")
    
    log_component_entry("PRIMITIVE", "delete_container_primitive", f"container_id={container_id}")
    
    try:
        # Validate container exists
        existing_containers = canvas_bridge.canvas_state.get("containers", {})
        if container_id not in existing_containers:
            error_result = {
                "status": "error",
                "operation": "delete_container",
                "error": f"Container ID '{container_id}' does not exist",
                "error_code": "CONTAINER_NOT_FOUND",
                "existing_container_ids": list(existing_containers.keys()),
                "timestamp": datetime.now().isoformat()
            }
            log_component_exit("PRIMITIVE", "delete_container_primitive", "ERROR", f"Container not found: {container_id}")
            return error_result
        
        # Get container data before deletion for response
        container_data = existing_containers[container_id].copy()
        
        # Generate unique command ID for tracking
        import uuid
        command_id = f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Remove container from canvas state
        del canvas_bridge.canvas_state["containers"][container_id]
        canvas_bridge.canvas_state["last_updated"] = datetime.now().isoformat()
        
        # Broadcast container deletion command to frontend
        delete_message = {
            "type": "canvas_command",
            "command": "delete_container",
            "command_id": command_id,
            "data": {
                "container_id": container_id
            }
        }
        
        # Check if there are any WebSocket connections
        connection_count = len(canvas_bridge.websocket_connections)
        print(f"[PRIMITIVE] Broadcasting container deletion to {connection_count} WebSocket connection(s)")
        
        if connection_count == 0:
            print("[WARNING] No WebSocket connections found - frontend may not be connected!")
        
        # Track the pending command
        canvas_bridge.track_pending_command(command_id, "delete_container", {
            "container_id": container_id,
            "deleted_container": container_data
        })
        
        await canvas_bridge.broadcast_to_frontend(delete_message)
        
        print(f"[PRIMITIVE] Container '{container_id}' deleted successfully")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] delete_container_primitive COMPLETED successfully")
        
        result = {
            "status": "success",
            "operation": "delete_container",
            "deleted_container": container_data,
            "remaining_containers": len(canvas_bridge.canvas_state["containers"]),
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "delete_container_primitive", "SUCCESS", f"Deleted {container_id}")
        return result
        
    except Exception as e:
        print(f"[PRIMITIVE ERROR] Failed to delete container: {e}")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] delete_container_primitive FAILED: {e}")
        
        error_result = {
            "status": "error",
            "operation": "delete_container",
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR",
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "delete_container_primitive", "ERROR", str(e))
        return error_result


async def clear_canvas_primitive() -> Dict[str, Any]:
    """
    Clear all elements from the canvas directly.
    
    Returns:
        Dict with operation result and details
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = logging.getLogger(__name__)
    
    if debug_mode:
        logger.debug(f"[PRIMITIVE] clear_canvas_primitive STARTED")
    
    log_component_entry("PRIMITIVE", "clear_canvas_primitive", "")
    
    try:
        # Get current canvas state for reporting
        current_containers = canvas_bridge.canvas_state.get("containers", {})
        container_count = len(current_containers)
        container_ids = list(current_containers.keys())
        
        # Calculate total area being cleared
        total_cleared_area = 0
        container_details = []
        
        for container_id, container_data in current_containers.items():
            area = container_data.get("width", 0) * container_data.get("height", 0)
            total_cleared_area += area
            container_details.append({
                "id": container_id,
                "x": container_data.get("x", 0),
                "y": container_data.get("y", 0),
                "width": container_data.get("width", 0),
                "height": container_data.get("height", 0),
                "area": area
            })
        
        # Get canvas dimensions for context
        canvas_size = canvas_bridge.get_canvas_size()
        canvas_width = canvas_size.get('width', 800)
        canvas_height = canvas_size.get('height', 600)
        canvas_area = canvas_width * canvas_height
        
        # Generate unique command ID for tracking
        import uuid
        command_id = f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Clear all containers from canvas state
        canvas_bridge.canvas_state["containers"] = {}
        canvas_bridge.canvas_state["last_updated"] = datetime.now().isoformat()
        canvas_bridge.canvas_state["last_cleared"] = datetime.now().isoformat()
        
        # Broadcast canvas clear command to frontend
        clear_message = {
            "type": "canvas_command",
            "command": "clear_canvas",
            "command_id": command_id,
            "data": {
                "cleared_containers": container_ids,
                "container_count": container_count
            }
        }
        
        # Check if there are any WebSocket connections
        connection_count = len(canvas_bridge.websocket_connections)
        print(f"[PRIMITIVE] Broadcasting canvas clear to {connection_count} WebSocket connection(s)")
        
        if connection_count == 0:
            print("[WARNING] No WebSocket connections found - frontend may not be connected!")
        
        # Track the pending command
        canvas_bridge.track_pending_command(command_id, "clear_canvas", {
            "cleared_containers": container_ids,
            "container_count": container_count,
            "cleared_area": total_cleared_area
        })
        
        await canvas_bridge.broadcast_to_frontend(clear_message)
        
        print(f"[PRIMITIVE] Canvas cleared successfully - removed {container_count} container(s)")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] clear_canvas_primitive COMPLETED successfully")
        
        result = {
            "status": "success",
            "operation": "clear_canvas",
            "cleared_elements": {
                "containers": container_details,
                "total_containers": container_count,
                "total_area_cleared": total_cleared_area
            },
            "canvas_context": {
                "canvas_size": {"width": canvas_width, "height": canvas_height},
                "canvas_area": canvas_area,
                "area_cleared_percentage": (total_cleared_area / canvas_area * 100) if canvas_area > 0 else 0
            },
            "final_state": {
                "containers": {},
                "container_count": 0,
                "is_empty": True
            },
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "clear_canvas_primitive", "SUCCESS", f"Cleared {container_count} containers")
        return result
        
    except Exception as e:
        print(f"[PRIMITIVE ERROR] Failed to clear canvas: {e}")
        
        if debug_mode:
            logger.debug(f"[PRIMITIVE] clear_canvas_primitive FAILED: {e}")
        
        error_result = {
            "status": "error",
            "operation": "clear_canvas",
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR",
            "timestamp": datetime.now().isoformat()
        }
        
        log_component_exit("PRIMITIVE", "clear_canvas_primitive", "ERROR", str(e))
        return error_result 