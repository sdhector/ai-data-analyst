"""
State Operations Primitives

Core atomic operations for canvas state retrieval.
These functions directly access canvas state with no formatting or validation.
"""

from typing import Dict, Any, Set
import sys
from pathlib import Path

# Add the backend directory to Python path to import canvas_bridge
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from core.canvas_bridge import canvas_bridge


def get_canvas_state_primitive() -> Dict[str, Any]:
    """
    Get the raw canvas state - no formatting.
    
    Returns:
        Dict[str, Any]: Raw canvas state data
        
    Note:
        This is a primitive function - returns raw state without formatting.
        Use tools layer for formatted state information.
    """
    try:
        return canvas_bridge.get_canvas_state()
    except Exception as e:
        print(f"[PRIMITIVE ERROR] get_canvas_state_primitive failed: {e}")
        return {
            "hasContainers": False,
            "containerCount": 0,
            "containers": [],
            "canvas_size": {"width": 800, "height": 600},
            "settings": {}
        }


def get_canvas_size_primitive() -> Dict[str, int]:
    """
    Get the current canvas dimensions - no validation.
    
    Returns:
        Dict[str, int]: Canvas size with width and height
        
    Note:
        This is a primitive function - returns raw size data.
        Use tools layer for formatted size information.
    """
    try:
        return canvas_bridge.get_canvas_size()
    except Exception as e:
        print(f"[PRIMITIVE ERROR] get_canvas_size_primitive failed: {e}")
        return {"width": 800, "height": 600}


def get_canvas_settings_primitive() -> Dict[str, Any]:
    """
    Get the current canvas settings - no validation.
    
    Returns:
        Dict[str, Any]: Raw canvas settings
        
    Note:
        This is a primitive function - returns raw settings data.
        Use tools layer for formatted settings information.
    """
    try:
        canvas_state = canvas_bridge.get_canvas_state()
        return canvas_state.get("settings", {})
    except Exception as e:
        print(f"[PRIMITIVE ERROR] get_canvas_settings_primitive failed: {e}")
        return {}


def get_container_count_primitive() -> int:
    """
    Get the number of containers on canvas - simple count.
    
    Returns:
        int: Number of containers
        
    Note:
        This is a primitive function - simple count only.
        Use tools layer for detailed container statistics.
    """
    try:
        canvas_state = canvas_bridge.get_canvas_state()
        return canvas_state.get("containerCount", 0)
    except Exception as e:
        print(f"[PRIMITIVE ERROR] get_container_count_primitive failed: {e}")
        return 0


def get_all_container_ids_primitive() -> Set[str]:
    """
    Get all container IDs currently on canvas - no validation.
    
    Returns:
        Set[str]: Set of all container IDs
        
    Note:
        This is a primitive function - returns raw ID set.
        Use tools layer for formatted ID listings.
    """
    try:
        canvas_state = canvas_bridge.get_canvas_state()
        containers = canvas_state.get("containers", [])
        return {container.get("id", "") for container in containers if container.get("id")}
    except Exception as e:
        print(f"[PRIMITIVE ERROR] get_all_container_ids_primitive failed: {e}")
        return set()


def canvas_has_containers_primitive() -> bool:
    """
    Check if canvas has any containers - simple boolean check.
    
    Returns:
        bool: True if canvas has containers, False otherwise
        
    Note:
        This is a primitive function - simple existence check only.
        Use tools layer for detailed canvas analysis.
    """
    try:
        canvas_state = canvas_bridge.get_canvas_state()
        return canvas_state.get("hasContainers", False)
    except Exception as e:
        print(f"[PRIMITIVE ERROR] canvas_has_containers_primitive failed: {e}")
        return False


def get_websocket_connection_count_primitive() -> int:
    """
    Get the number of active WebSocket connections - no validation.
    
    Returns:
        int: Number of active connections
        
    Note:
        This is a primitive function - simple count only.
        Use tools layer for detailed connection information.
    """
    try:
        return len(canvas_bridge.websocket_connections)
    except Exception as e:
        print(f"[PRIMITIVE ERROR] get_websocket_connection_count_primitive failed: {e}")
        return 0 