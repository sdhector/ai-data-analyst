"""
Primitive Functions Module

Contains core, atomic operations that directly manipulate canvas state.
These functions have single responsibility, no validation logic, and minimal dependencies.
"""

from .canvas_operations import (
    set_canvas_dimensions_primitive,
    get_canvas_dimensions_primitive,
    create_container_primitive,
    resize_container_primitive,
    move_container_primitive,
    delete_container_primitive,
    clear_canvas_primitive
)

__all__ = [
    # Canvas operations
    "set_canvas_dimensions_primitive",
    "get_canvas_dimensions_primitive",
    "create_container_primitive",
    "resize_container_primitive",
    "move_container_primitive",
    "delete_container_primitive",
    "clear_canvas_primitive"
] 