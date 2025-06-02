"""
Grid Management Functions

This module contains functions for managing the visualization grid layout,
including adding, removing, and organizing containers.
"""

from typing import Dict, Any, List
import uuid

# Global grid state (in production, this would be managed by a proper state manager)
_grid_containers = {}
_grid_layout = {"max_containers": 6, "current_count": 0}

def add_container(position: int = None, size_ratio: float = 1.0) -> Dict[str, Any]:
    """
    Add a new visualization container to the grid
    
    Args:
        position: Position in the grid (1-6, None for next available)
        size_ratio: Relative size of the container (0.5-2.0)
        
    Returns:
        Dictionary with container information
    """
    global _grid_containers, _grid_layout
    
    try:
        # Check if we've reached the maximum number of containers
        if _grid_layout["current_count"] >= _grid_layout["max_containers"]:
            return {
                "status": "error",
                "error": f"Maximum number of containers ({_grid_layout['max_containers']}) reached",
                "current_containers": list(_grid_containers.keys())
            }
        
        # Determine position
        if position is None:
            # Find next available position
            used_positions = [container["position"] for container in _grid_containers.values()]
            for i in range(1, _grid_layout["max_containers"] + 1):
                if i not in used_positions:
                    position = i
                    break
        else:
            # Validate position
            if position < 1 or position > _grid_layout["max_containers"]:
                return {
                    "status": "error",
                    "error": f"Position must be between 1 and {_grid_layout['max_containers']}"
                }
            
            # Check if position is already occupied
            for container in _grid_containers.values():
                if container["position"] == position:
                    return {
                        "status": "error",
                        "error": f"Position {position} is already occupied",
                        "occupied_positions": [c["position"] for c in _grid_containers.values()]
                    }
        
        # Validate size ratio
        if size_ratio < 0.5 or size_ratio > 2.0:
            return {
                "status": "error",
                "error": "Size ratio must be between 0.5 and 2.0"
            }
        
        # Generate unique container ID
        container_id = f"container_{uuid.uuid4().hex[:8]}"
        
        # Create container
        container = {
            "id": container_id,
            "position": position,
            "size_ratio": size_ratio,
            "content": None,
            "content_type": None,
            "created_at": "2024-01-01T00:00:00Z",  # In production, use actual timestamp
            "title": f"Container {position}"
        }
        
        _grid_containers[container_id] = container
        _grid_layout["current_count"] += 1
        
        return {
            "status": "success",
            "result": {
                "container_id": container_id,
                "position": position,
                "size_ratio": size_ratio,
                "grid_status": {
                    "total_containers": _grid_layout["current_count"],
                    "max_containers": _grid_layout["max_containers"],
                    "available_positions": _get_available_positions()
                }
            },
            "metadata": {
                "action": "container_added",
                "grid_layout": _get_grid_layout()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error adding container: {str(e)}",
            "function_name": "add_container"
        }

def remove_container(container_id: str) -> Dict[str, Any]:
    """
    Remove a container from the grid
    
    Args:
        container_id: ID of the container to remove
        
    Returns:
        Dictionary with removal status
    """
    global _grid_containers, _grid_layout
    
    try:
        if container_id not in _grid_containers:
            return {
                "status": "error",
                "error": f"Container '{container_id}' not found",
                "available_containers": list(_grid_containers.keys())
            }
        
        # Get container info before removal
        removed_container = _grid_containers[container_id].copy()
        
        # Remove container
        del _grid_containers[container_id]
        _grid_layout["current_count"] -= 1
        
        return {
            "status": "success",
            "result": {
                "removed_container_id": container_id,
                "removed_position": removed_container["position"],
                "grid_status": {
                    "total_containers": _grid_layout["current_count"],
                    "max_containers": _grid_layout["max_containers"],
                    "available_positions": _get_available_positions()
                }
            },
            "metadata": {
                "action": "container_removed",
                "grid_layout": _get_grid_layout()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error removing container: {str(e)}",
            "function_name": "remove_container"
        }

def clear_grid() -> Dict[str, Any]:
    """
    Clear all containers from the grid
    
    Returns:
        Dictionary with clear status
    """
    global _grid_containers, _grid_layout
    
    try:
        containers_removed = len(_grid_containers)
        removed_container_ids = list(_grid_containers.keys())
        
        # Clear all containers
        _grid_containers.clear()
        _grid_layout["current_count"] = 0
        
        return {
            "status": "success",
            "result": {
                "containers_removed": containers_removed,
                "removed_container_ids": removed_container_ids,
                "grid_status": {
                    "total_containers": 0,
                    "max_containers": _grid_layout["max_containers"],
                    "available_positions": list(range(1, _grid_layout["max_containers"] + 1))
                }
            },
            "metadata": {
                "action": "grid_cleared",
                "grid_layout": _get_grid_layout()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error clearing grid: {str(e)}",
            "function_name": "clear_grid"
        }

def resize_container(container_id: str, size_ratio: float) -> Dict[str, Any]:
    """
    Resize a container in the grid
    
    Args:
        container_id: ID of the container to resize
        size_ratio: New size ratio (0.5-2.0)
        
    Returns:
        Dictionary with resize status
    """
    global _grid_containers
    
    try:
        if container_id not in _grid_containers:
            return {
                "status": "error",
                "error": f"Container '{container_id}' not found",
                "available_containers": list(_grid_containers.keys())
            }
        
        # Validate size ratio
        if size_ratio < 0.5 or size_ratio > 2.0:
            return {
                "status": "error",
                "error": "Size ratio must be between 0.5 and 2.0"
            }
        
        # Update container size
        old_size = _grid_containers[container_id]["size_ratio"]
        _grid_containers[container_id]["size_ratio"] = size_ratio
        
        return {
            "status": "success",
            "result": {
                "container_id": container_id,
                "old_size_ratio": old_size,
                "new_size_ratio": size_ratio,
                "position": _grid_containers[container_id]["position"]
            },
            "metadata": {
                "action": "container_resized",
                "grid_layout": _get_grid_layout()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error resizing container: {str(e)}",
            "function_name": "resize_container"
        }

def get_grid_status() -> Dict[str, Any]:
    """
    Get current grid status and layout information
    
    Returns:
        Dictionary with grid status
    """
    global _grid_containers, _grid_layout
    
    try:
        containers_info = []
        for container_id, container in _grid_containers.items():
            containers_info.append({
                "id": container_id,
                "position": container["position"],
                "size_ratio": container["size_ratio"],
                "content_type": container["content_type"],
                "title": container["title"]
            })
        
        # Sort by position
        containers_info.sort(key=lambda x: x["position"])
        
        return {
            "status": "success",
            "result": {
                "grid_layout": _grid_layout,
                "containers": containers_info,
                "available_positions": _get_available_positions(),
                "grid_utilization": f"{_grid_layout['current_count']}/{_grid_layout['max_containers']}"
            },
            "metadata": {
                "total_containers": len(_grid_containers),
                "grid_full": _grid_layout["current_count"] >= _grid_layout["max_containers"]
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error getting grid status: {str(e)}",
            "function_name": "get_grid_status"
        }

def update_container_content(container_id: str, content: Dict[str, Any], 
                           content_type: str, title: str = None) -> Dict[str, Any]:
    """
    Update the content of a container
    
    Args:
        container_id: ID of the container to update
        content: Content data (chart config, table data, etc.)
        content_type: Type of content ('chart', 'table', 'text')
        title: Optional title for the container
        
    Returns:
        Dictionary with update status
    """
    global _grid_containers
    
    try:
        if container_id not in _grid_containers:
            return {
                "status": "error",
                "error": f"Container '{container_id}' not found",
                "available_containers": list(_grid_containers.keys())
            }
        
        # Update container content
        _grid_containers[container_id]["content"] = content
        _grid_containers[container_id]["content_type"] = content_type
        
        if title:
            _grid_containers[container_id]["title"] = title
        
        return {
            "status": "success",
            "result": {
                "container_id": container_id,
                "content_type": content_type,
                "title": _grid_containers[container_id]["title"],
                "position": _grid_containers[container_id]["position"],
                "updated": True
            },
            "metadata": {
                "action": "container_content_updated",
                "content_size": len(str(content)) if content else 0
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error updating container content: {str(e)}",
            "function_name": "update_container_content"
        }

# Helper functions
def _get_available_positions() -> List[int]:
    """Get list of available positions in the grid"""
    used_positions = [container["position"] for container in _grid_containers.values()]
    return [i for i in range(1, _grid_layout["max_containers"] + 1) if i not in used_positions]

def _get_grid_layout() -> Dict[str, Any]:
    """Get current grid layout information"""
    return {
        "containers": {cid: {"position": c["position"], "size_ratio": c["size_ratio"]} 
                      for cid, c in _grid_containers.items()},
        "total_containers": _grid_layout["current_count"],
        "max_containers": _grid_layout["max_containers"]
    } 