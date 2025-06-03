"""
Grid Management Functions

This module contains functions for managing the visualization grid layout,
including adding, removing, and organizing containers in a flexible 6x6 grid.
"""

from typing import Dict, Any, List, Optional, Tuple
import uuid

# Global grid state (in production, this would be managed by a proper state manager)
_grid_containers = {}
_grid_layout = {
    "grid_size": 3,  # 3x3 grid
    "containers": {}
}

def add_container(position: str = None, 
                 start_row: int = None, start_col: int = None,
                 end_row: int = None, end_col: int = None,
                 title: str = None) -> Dict[str, Any]:
    """
    Add a new visualization container to the grid
    
    Args:
        position: Natural language position (e.g., "bottom right", "top left")
        start_row: Starting row (0-2)
        start_col: Starting column (0-2)
        end_row: Ending row (0-2)
        end_col: Ending column (0-2)
        title: Container title
        
    Returns:
        Dictionary with container information
    """
    global _grid_containers, _grid_layout
    
    try:
        # Parse position if provided
        if position and not all([start_row is not None, start_col is not None]):
            coords = _parse_position_description(position)
            start_row = coords["start_row"]
            start_col = coords["start_col"]
            end_row = coords["end_row"]
            end_col = coords["end_col"]
        
        # Default to single cell if end coordinates not provided
        if end_row is None:
            end_row = start_row if start_row is not None else 0
        if end_col is None:
            end_col = start_col if start_col is not None else 0
        if start_row is None:
            start_row = 0
        if start_col is None:
            start_col = 0
            
        # Validate coordinates
        if not _validate_coordinates(start_row, start_col, end_row, end_col):
            return {
                "status": "error",
                "error": f"Invalid coordinates: must be within 0-2 range"
            }
        
        # Check if cells are available
        if not _are_cells_available(start_row, start_col, end_row, end_col):
            return {
                "status": "error",
                "error": f"Selected cells are already occupied"
            }
        
        # Generate unique container ID
        container_id = f"container_{uuid.uuid4().hex[:8]}"
        
        # Create container
        container = {
            "id": container_id,
            "title": title or f"Container {len(_grid_containers) + 1}",
            "start_row": start_row,
            "start_col": start_col,
            "end_row": end_row,
            "end_col": end_col,
            "content": None,
            "content_type": None,
            "created_at": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
        }
        
        _grid_containers[container_id] = container
        _grid_layout["containers"][container_id] = {
            "start_row": start_row,
            "start_col": start_col,
            "end_row": end_row,
            "end_col": end_col
        }
        
        return {
            "status": "success",
            "result": {
                "container_id": container_id,
                "title": container["title"],
                "position": {
                    "start_row": start_row,
                    "start_col": start_col,
                    "end_row": end_row,
                    "end_col": end_col
                },
                "grid_status": _get_grid_status_summary()
            },
            "metadata": {
                "action": "container_added",
                "cells_occupied": (end_row - start_row + 1) * (end_col - start_col + 1)
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
        del _grid_layout["containers"][container_id]
        
        return {
            "status": "success",
            "result": {
                "removed_container_id": container_id,
                "removed_position": {
                    "start_row": removed_container["start_row"],
                    "start_col": removed_container["start_col"],
                    "end_row": removed_container["end_row"],
                    "end_col": removed_container["end_col"]
                },
                "grid_status": _get_grid_status_summary()
            },
            "metadata": {
                "action": "container_removed"
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
        _grid_layout["containers"].clear()
        
        return {
            "status": "success",
            "result": {
                "containers_removed": containers_removed,
                "removed_container_ids": removed_container_ids,
                "grid_status": _get_grid_status_summary()
            },
            "metadata": {
                "action": "grid_cleared"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error clearing grid: {str(e)}",
            "function_name": "clear_grid"
        }

def move_container(container_id: str, 
                  position: str = None,
                  start_row: int = None, start_col: int = None,
                  end_row: int = None, end_col: int = None) -> Dict[str, Any]:
    """
    Move a container to a new position
    
    Args:
        container_id: ID of the container to move
        position: Natural language position
        start_row, start_col, end_row, end_col: New coordinates
        
    Returns:
        Dictionary with move status
    """
    global _grid_containers, _grid_layout
    
    try:
        if container_id not in _grid_containers:
            return {
                "status": "error",
                "error": f"Container '{container_id}' not found"
            }
        
        container = _grid_containers[container_id]
        
        # Parse position if provided
        if position and not all([start_row is not None, start_col is not None]):
            coords = _parse_position_description(position)
            start_row = coords["start_row"]
            start_col = coords["start_col"]
            end_row = coords["end_row"]
            end_col = coords["end_col"]
        
        # Use current size if not specified
        if end_row is None:
            end_row = start_row + (container["end_row"] - container["start_row"])
        if end_col is None:
            end_col = start_col + (container["end_col"] - container["start_col"])
            
        # Validate new position
        if not _validate_coordinates(start_row, start_col, end_row, end_col):
            return {
                "status": "error",
                "error": "Invalid coordinates"
            }
        
        # Check if new position is available (excluding current container)
        if not _are_cells_available(start_row, start_col, end_row, end_col, exclude_container=container_id):
            return {
                "status": "error",
                "error": "Target position is occupied"
            }
        
        # Update position
        old_position = {
            "start_row": container["start_row"],
            "start_col": container["start_col"],
            "end_row": container["end_row"],
            "end_col": container["end_col"]
        }
        
        container["start_row"] = start_row
        container["start_col"] = start_col
        container["end_row"] = end_row
        container["end_col"] = end_col
        
        _grid_layout["containers"][container_id] = {
            "start_row": start_row,
            "start_col": start_col,
            "end_row": end_row,
            "end_col": end_col
        }
        
        return {
            "status": "success",
            "result": {
                "container_id": container_id,
                "old_position": old_position,
                "new_position": {
                    "start_row": start_row,
                    "start_col": start_col,
                    "end_row": end_row,
                    "end_col": end_col
                }
            },
            "metadata": {
                "action": "container_moved"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error moving container: {str(e)}",
            "function_name": "move_container"
        }

def resize_container(container_id: str,
                    width: int = None, height: int = None,
                    end_row: int = None, end_col: int = None) -> Dict[str, Any]:
    """
    Resize a container
    
    Args:
        container_id: ID of the container to resize
        width: New width in cells
        height: New height in cells
        end_row: New end row
        end_col: New end column
        
    Returns:
        Dictionary with resize status
    """
    global _grid_containers, _grid_layout
    
    try:
        if container_id not in _grid_containers:
            return {
                "status": "error",
                "error": f"Container '{container_id}' not found"
            }
        
        container = _grid_containers[container_id]
        
        # Calculate new dimensions
        if width is not None:
            end_col = container["start_col"] + width - 1
        elif end_col is None:
            end_col = container["end_col"]
            
        if height is not None:
            end_row = container["start_row"] + height - 1
        elif end_row is None:
            end_row = container["end_row"]
        
        # Validate new size
        if not _validate_coordinates(container["start_row"], container["start_col"], end_row, end_col):
            return {
                "status": "error",
                "error": "Invalid dimensions"
            }
        
        # Check if new size is available
        if not _are_cells_available(container["start_row"], container["start_col"], 
                                   end_row, end_col, exclude_container=container_id):
            return {
                "status": "error",
                "error": "Cannot resize: cells are occupied"
            }
        
        # Update size
        old_size = {
            "width": container["end_col"] - container["start_col"] + 1,
            "height": container["end_row"] - container["start_row"] + 1
        }
        
        container["end_row"] = end_row
        container["end_col"] = end_col
        
        _grid_layout["containers"][container_id]["end_row"] = end_row
        _grid_layout["containers"][container_id]["end_col"] = end_col
        
        new_size = {
            "width": end_col - container["start_col"] + 1,
            "height": end_row - container["start_row"] + 1
        }
        
        return {
            "status": "success",
            "result": {
                "container_id": container_id,
                "old_size": old_size,
                "new_size": new_size,
                "position": {
                    "start_row": container["start_row"],
                    "start_col": container["start_col"],
                    "end_row": end_row,
                    "end_col": end_col
                }
            },
            "metadata": {
                "action": "container_resized"
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
                "title": container["title"],
                "position": {
                    "start_row": container["start_row"],
                    "start_col": container["start_col"],
                    "end_row": container["end_row"],
                    "end_col": container["end_col"]
                },
                "size": {
                    "width": container["end_col"] - container["start_col"] + 1,
                    "height": container["end_row"] - container["start_row"] + 1
                },
                "content_type": container["content_type"]
            })
        
        # Create grid visualization
        grid_visual = _create_grid_visualization()
        
        return {
            "status": "success",
            "result": {
                "grid_size": _grid_layout["grid_size"],
                "containers": containers_info,
                "total_containers": len(_grid_containers),
                "occupied_cells": _count_occupied_cells(),
                "available_cells": 9 - _count_occupied_cells(),
                "grid_visualization": grid_visual
            },
            "metadata": {
                "grid_full": _count_occupied_cells() >= 9
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
                "position": {
                    "start_row": _grid_containers[container_id]["start_row"],
                    "start_col": _grid_containers[container_id]["start_col"],
                    "end_row": _grid_containers[container_id]["end_row"],
                    "end_col": _grid_containers[container_id]["end_col"]
                },
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
def _validate_coordinates(start_row: int, start_col: int, end_row: int, end_col: int) -> bool:
    """Validate grid coordinates"""
    return (0 <= start_row <= end_row < 3 and 
            0 <= start_col <= end_col < 3)

def _are_cells_available(start_row: int, start_col: int, end_row: int, end_col: int, 
                        exclude_container: str = None) -> bool:
    """Check if cells in the specified range are available"""
    for container_id, coords in _grid_layout["containers"].items():
        if exclude_container and container_id == exclude_container:
            continue
            
        # Check for overlap
        if not (end_row < coords["start_row"] or 
                start_row > coords["end_row"] or
                end_col < coords["start_col"] or
                start_col > coords["end_col"]):
            return False
    
    return True

def _count_occupied_cells() -> int:
    """Count total occupied cells"""
    occupied = set()
    for coords in _grid_layout["containers"].values():
        for row in range(coords["start_row"], coords["end_row"] + 1):
            for col in range(coords["start_col"], coords["end_col"] + 1):
                occupied.add((row, col))
    return len(occupied)

def _get_grid_status_summary() -> Dict[str, Any]:
    """Get summary of grid status"""
    occupied = _count_occupied_cells()
    return {
        "total_containers": len(_grid_containers),
        "occupied_cells": occupied,
        "available_cells": 9 - occupied,
        "utilization": f"{(occupied / 9) * 100:.1f}%"
    }

def _create_grid_visualization() -> List[List[str]]:
    """Create ASCII visualization of the grid"""
    grid = [["." for _ in range(3)] for _ in range(3)]
    
    for container_id, coords in _grid_layout["containers"].items():
        # Use first letter of container ID for visualization
        marker = container_id[10] if len(container_id) > 10 else "X"
        for row in range(coords["start_row"], coords["end_row"] + 1):
            for col in range(coords["start_col"], coords["end_col"] + 1):
                grid[row][col] = marker
    
    return grid

def _parse_position_description(position: str) -> Dict[str, int]:
    """Parse natural language position description"""
    position = position.lower().strip()
    
    # Position mappings for common descriptions (3x3 grid)
    positions = {
        # Corners
        "top left": {"start_row": 0, "start_col": 0, "end_row": 0, "end_col": 0},
        "top right": {"start_row": 0, "start_col": 2, "end_row": 0, "end_col": 2},
        "bottom left": {"start_row": 2, "start_col": 0, "end_row": 2, "end_col": 0},
        "bottom right": {"start_row": 2, "start_col": 2, "end_row": 2, "end_col": 2},
        
        # Edges
        "top": {"start_row": 0, "start_col": 0, "end_row": 0, "end_col": 2},
        "bottom": {"start_row": 2, "start_col": 0, "end_row": 2, "end_col": 2},
        "left": {"start_row": 0, "start_col": 0, "end_row": 2, "end_col": 0},
        "right": {"start_row": 0, "start_col": 2, "end_row": 2, "end_col": 2},
        
        # Center positions
        "center": {"start_row": 1, "start_col": 1, "end_row": 1, "end_col": 1},
        "middle": {"start_row": 1, "start_col": 1, "end_row": 1, "end_col": 1},
        
        # Full grid
        "full": {"start_row": 0, "start_col": 0, "end_row": 2, "end_col": 2},
        "entire": {"start_row": 0, "start_col": 0, "end_row": 2, "end_col": 2},
        
        # Specific sizes (all single cell in 3x3)
        "small": {"start_row": 0, "start_col": 0, "end_row": 0, "end_col": 0},
        "medium": {"start_row": 0, "start_col": 0, "end_row": 1, "end_col": 1},
        "large": {"start_row": 0, "start_col": 0, "end_row": 2, "end_col": 2}
    }
    
    # Look for matches
    for key, coords in positions.items():
        if key in position:
            # Check for size modifiers
            if "small" in position and key not in ["small", "medium", "large"]:
                # Make it smaller
                width = coords["end_col"] - coords["start_col"] + 1
                height = coords["end_row"] - coords["start_row"] + 1
                coords["end_col"] = coords["start_col"] + max(0, width // 2 - 1)
                coords["end_row"] = coords["start_row"] + max(0, height // 2 - 1)
            elif "large" in position and key not in ["small", "medium", "large"]:
                # Make it larger (but stay within bounds)
                coords["end_col"] = min(2, coords["end_col"] + 1)
                coords["end_row"] = min(2, coords["end_row"] + 1)
                
            return coords
    
    # Default to small container at top-left
    return {"start_row": 0, "start_col": 0, "end_row": 0, "end_col": 0} 