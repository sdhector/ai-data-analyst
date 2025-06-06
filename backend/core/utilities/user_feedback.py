"""
User Feedback Utility

Manages user-facing notifications for tool execution progress.
This is separate from debugging logs and provides real-time feedback to users.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class FeedbackType(Enum):
    """Types of feedback messages"""
    TOOL_START = "tool_start"
    TOOL_SUCCESS = "tool_success"
    TOOL_ERROR = "tool_error"
    TOOL_PROGRESS = "tool_progress"
    SYSTEM_INFO = "system_info"

class UserFeedbackManager:
    """Manages user feedback messages during tool execution"""
    
    def __init__(self):
        self.websocket_connections = set()
        self.pending_operations = {}  # Track ongoing operations for progress updates
    
    def add_websocket_connection(self, websocket):
        """Add a WebSocket connection for user feedback"""
        self.websocket_connections.add(websocket)
    
    def remove_websocket_connection(self, websocket):
        """Remove a WebSocket connection"""
        self.websocket_connections.discard(websocket)
    
    async def send_user_feedback(
        self, 
        feedback_type: FeedbackType, 
        operation: str, 
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        group_id: Optional[str] = None,
        start_group: bool = False,
        end_group: bool = False
    ):
        """Send feedback message to user(s)"""
        
        feedback_message = {
            "type": "user_feedback",
            "feedback_type": feedback_type.value,
            "operation": operation,
            "message": message,
            "details": details or {},
            "request_id": request_id,
            "group_id": group_id,
            "start_group": start_group,
            "end_group": end_group,
            "timestamp": datetime.now().isoformat()
        }
        
        if not self.websocket_connections:
            print(f"[USER_FEEDBACK] No connections available: {message}")
            return
        
        message_json = json.dumps(feedback_message)
        disconnected = set()
        
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                print(f"[USER_FEEDBACK] Failed to send feedback: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected websockets
        for ws in disconnected:
            self.websocket_connections.discard(ws)
    
    async def notify_tool_start(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any],
        request_id: Optional[str] = None
    ):
        """Notify user that a tool execution has started"""
        message = f"⚙️ Starting {tool_name}"
        details = {
            "tool_name": tool_name,
            "parameters": parameters,
            "stage": "start"
        }
        
        # Use request_id as group_id for related tool operations
        group_id = f"tool_{request_id}" if request_id else f"tool_{tool_name}"
        
        await self.send_user_feedback(
            FeedbackType.TOOL_START,
            tool_name,
            message,
            details,
            request_id,
            group_id=group_id,
            start_group=True
        )
    
    async def notify_tool_success(
        self, 
        tool_name: str, 
        result: Dict[str, Any],
        request_id: Optional[str] = None
    ):
        """Notify user that a tool execution completed successfully"""
        message = f"✅ {tool_name} completed successfully"
        details = {
            "tool_name": tool_name,
            "result": result,
            "stage": "success"
        }
        
        # Use same group_id as start
        group_id = f"tool_{request_id}" if request_id else f"tool_{tool_name}"
        
        await self.send_user_feedback(
            FeedbackType.TOOL_SUCCESS,
            tool_name,
            message,
            details,
            request_id,
            group_id=group_id,
            end_group=True
        )
    
    async def notify_tool_error(
        self, 
        tool_name: str, 
        error: str,
        request_id: Optional[str] = None
    ):
        """Notify user that a tool execution failed"""
        message = f"❌ {tool_name} failed: {error}"
        details = {
            "tool_name": tool_name,
            "error": error,
            "stage": "error"
        }
        
        # Use same group_id as start
        group_id = f"tool_{request_id}" if request_id else f"tool_{tool_name}"
        
        await self.send_user_feedback(
            FeedbackType.TOOL_ERROR,
            tool_name,
            message,
            details,
            request_id,
            group_id=group_id,
            end_group=True
        )
    
    async def notify_tool_progress(
        self, 
        tool_name: str, 
        progress_message: str,
        progress_percent: Optional[float] = None,
        request_id: Optional[str] = None
    ):
        """Notify user of tool execution progress"""
        message = f"🔄 {tool_name}: {progress_message}"
        details = {
            "tool_name": tool_name,
            "progress_message": progress_message,
            "progress_percent": progress_percent,
            "stage": "progress"
        }
        
        await self.send_user_feedback(
            FeedbackType.TOOL_PROGRESS,
            tool_name,
            message,
            details,
            request_id
        )

# Global feedback manager
user_feedback_manager = UserFeedbackManager() 