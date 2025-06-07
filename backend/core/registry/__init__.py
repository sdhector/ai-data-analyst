"""
Registry Module

Contains tool registration and schema management functionality.
Provides dynamic tool discovery and OpenAI function schema generation.
"""

# Import canvas management registry functions
from .canvas_management_registry import (
    get_canvas_management_function_schemas,
    execute_canvas_management_tool,
    get_tool_by_name,
    get_tool_metadata,
    list_available_tools
)

__all__ = [
    "get_canvas_management_function_schemas",
    "execute_canvas_management_tool", 
    "get_tool_by_name",
    "get_tool_metadata",
    "list_available_tools"
] 