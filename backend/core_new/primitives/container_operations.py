"""
Container Operations Primitives

Core atomic operations for container manipulation.
These functions directly interact with the canvas bridge with no validation or optimization.
"""

from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Add the backend directory to Python path to import canvas_bridge
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from core.canvas_bridge import canvas_bridge


async def create_container_primitive(
    container_id: str, 
    x: int, 
    y: int, 
    width: int, 
    height: int
) -> bool:
    """
    Create a container with exact parameters - no validation or optimization.
    
    Args:
        container_id: Unique identifier for the container
        x: X coordinate position
        y: Y coordinate position  
        width: Container width in pixels
        height: Container height in pixels
        
    Returns:
        bool: True if creation succeeded, False otherwise
        
    Note:
        This is a primitive function - no validation, auto-adjustment, or overlap prevention.
        Use tools layer for intelligent container creation with optimization.
    """
    try:
        return await canvas_bridge.create_container(
            container_id=container_id,
            x=x,
            y=y, 
            width=width,
            height=height,
            auto_adjust=False,  # No automatic adjustments
            avoid_overlap=False  # No overlap prevention
        )
    except Exception as e:
        print(f"[PRIMITIVE ERROR] create_container_primitive failed: {e}")
        return False


async def delete_container_primitive(container_id: str) -> bool:
    """
    Delete a container by ID - no existence checking.
    
    Args:
        container_id: ID of the container to delete
        
    Returns:
        bool: True if deletion succeeded, False otherwise
        
    Note:
        This is a primitive function - no existence validation.
        Use tools layer for safe container deletion with validation.
    """
    try:
        return await canvas_bridge.delete_container(container_id)
    except Exception as e:
        print(f"[PRIMITIVE ERROR] delete_container_primitive failed: {e}")
        return False


async def modify_container_primitive(
    container_id: str,
    x: int,
    y: int, 
    width: int,
    height: int
) -> bool:
    """
    Modify an existing container's position and size - no validation.
    
    Args:
        container_id: ID of the container to modify
        x: New X coordinate position
        y: New Y coordinate position
        width: New container width in pixels
        height: New container height in pixels
        
    Returns:
        bool: True if modification succeeded, False otherwise
        
    Note:
        This is a primitive function - no existence checking or optimization.
        Use tools layer for safe container modification with validation.
    """
    try:
        return await canvas_bridge.modify_container(
            container_id=container_id,
            x=x,
            y=y,
            width=width, 
            height=height,
            auto_adjust=False,  # No automatic adjustments
            avoid_overlap=False  # No overlap prevention
        )
    except Exception as e:
        print(f"[PRIMITIVE ERROR] modify_container_primitive failed: {e}")
        return False


async def get_container_primitive(container_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific container by ID - no validation.
    
    Args:
        container_id: ID of the container to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: Container data if found, None otherwise
        
    Note:
        This is a primitive function - no existence validation.
        Returns None if container doesn't exist instead of raising errors.
    """
    try:
        canvas_state = canvas_bridge.get_canvas_state()
        containers = canvas_state.get('containers', [])
        
        for container in containers:
            if container.get('id') == container_id:
                return container
                
        return None
    except Exception as e:
        print(f"[PRIMITIVE ERROR] get_container_primitive failed: {e}")
        return None


async def list_containers_primitive() -> List[Dict[str, Any]]:
    """
    Get all containers from canvas - no formatting.
    
    Returns:
        List[Dict[str, Any]]: Raw list of container data
        
    Note:
        This is a primitive function - returns raw container data.
        Use tools layer for formatted container listings.
    """
    try:
        canvas_state = canvas_bridge.get_canvas_state()
        return canvas_state.get('containers', [])
    except Exception as e:
        print(f"[PRIMITIVE ERROR] list_containers_primitive failed: {e}")
        return []


async def container_exists_primitive(container_id: str) -> bool:
    """
    Check if a container exists by ID - simple boolean check.
    
    Args:
        container_id: ID of the container to check
        
    Returns:
        bool: True if container exists, False otherwise
        
    Note:
        This is a primitive function - simple existence check only.
    """
    try:
        container = await get_container_primitive(container_id)
        return container is not None
    except Exception as e:
        print(f"[PRIMITIVE ERROR] container_exists_primitive failed: {e}")
        return False 