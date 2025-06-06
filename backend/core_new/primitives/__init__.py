"""
Primitive Functions Module

Contains core, atomic operations that directly manipulate canvas state.
These functions have single responsibility, no validation logic, and minimal dependencies.
"""

from .container_operations import *
from .canvas_operations import *
from .state_operations import *

__all__ = [
    # Container operations
    "create_container_primitive",
    "delete_container_primitive", 
    "modify_container_primitive",
    "get_container_primitive",
    "list_containers_primitive",
    
    # Canvas operations
    "clear_canvas_primitive",
    "resize_canvas_primitive", 
    "take_screenshot_primitive",
    
    # State operations
    "get_canvas_state_primitive",
    "get_canvas_size_primitive",
] 