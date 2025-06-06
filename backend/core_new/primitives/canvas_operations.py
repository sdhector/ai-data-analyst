"""
Canvas Operations Primitives

Core atomic operations for canvas manipulation.
These functions directly interact with the canvas bridge with no validation or optimization.
"""

from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add the backend directory to Python path to import canvas_bridge
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from core.canvas_bridge import canvas_bridge


async def clear_canvas_primitive() -> bool:
    """
    Remove all containers from the canvas - no confirmation.
    
    Returns:
        bool: True if clearing succeeded, False otherwise
        
    Note:
        This is a primitive function - no confirmation or backup.
        Use tools layer for safe canvas clearing with confirmation.
    """
    try:
        return await canvas_bridge.clear_canvas()
    except Exception as e:
        print(f"[PRIMITIVE ERROR] clear_canvas_primitive failed: {e}")
        return False


async def resize_canvas_primitive(width: int, height: int) -> bool:
    """
    Resize the canvas to new dimensions - no validation or container adjustment.
    
    Args:
        width: New canvas width in pixels
        height: New canvas height in pixels
        
    Returns:
        bool: True if resize succeeded, False otherwise
        
    Note:
        This is a primitive function - no size validation or container repositioning.
        Use tools layer for safe canvas resizing with container optimization.
    """
    try:
        # Update canvas size in bridge state
        canvas_bridge.canvas_state["canvas_size"] = {
            "width": width,
            "height": height
        }
        
        # Send resize command to frontend
        await canvas_bridge.broadcast_to_frontend({
            "type": "canvas_command",
            "command": "edit_canvas_size",
            "data": {
                "width": width,
                "height": height
            }
        })
        
        return True
    except Exception as e:
        print(f"[PRIMITIVE ERROR] resize_canvas_primitive failed: {e}")
        return False


async def take_screenshot_primitive(filename: Optional[str] = None) -> Optional[str]:
    """
    Take a screenshot of the current canvas state - no filename validation.
    
    Args:
        filename: Optional filename for the screenshot
        
    Returns:
        Optional[str]: Screenshot filename if successful, None otherwise
        
    Note:
        This is a primitive function - no filename validation or path checking.
        Use tools layer for safe screenshot taking with validation.
    """
    try:
        return await canvas_bridge.take_screenshot(filename)
    except Exception as e:
        print(f"[PRIMITIVE ERROR] take_screenshot_primitive failed: {e}")
        return None


async def broadcast_canvas_command_primitive(command: str, data: Dict[str, Any]) -> bool:
    """
    Send a raw command to the frontend - no validation.
    
    Args:
        command: Command name to send
        data: Command data payload
        
    Returns:
        bool: True if broadcast succeeded, False otherwise
        
    Note:
        This is a primitive function - no command validation.
        Use with caution as invalid commands may break frontend.
    """
    try:
        await canvas_bridge.broadcast_to_frontend({
            "type": "canvas_command",
            "command": command,
            "data": data
        })
        return True
    except Exception as e:
        print(f"[PRIMITIVE ERROR] broadcast_canvas_command_primitive failed: {e}")
        return False 