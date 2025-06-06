"""
WebSocket Server for Real-time Canvas Communication

Handles WebSocket connections for real-time communication between the v0.1 frontend and backend.
"""

import json
import asyncio
from typing import Dict, Any, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

from core.chatbot import chatbot
from core.canvas_bridge import canvas_bridge


class WebSocketManager:
    """Manages WebSocket connections and message routing"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        canvas_bridge.add_websocket_connection(websocket)
        print(f"[SUCCESS] WebSocket client connected. Total connections: {len(self.active_connections)}")
        
        # Send initial canvas state
        try:
            initial_state = canvas_bridge.get_canvas_state()
            await websocket.send_text(json.dumps({
                "type": "initial_state",
                "data": initial_state,
                "timestamp": datetime.now().isoformat()
            }))
        except Exception as e:
            print(f"[ERROR] Error sending initial state: {e}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        canvas_bridge.remove_websocket_connection(websocket)
        print(f"🔌 WebSocket client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"[ERROR] Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any], exclude: WebSocket = None):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
            
        message_json = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections:
            if connection != exclude:
                try:
                    await connection.send_text(message_json)
                except Exception:
                    disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Global WebSocket manager
websocket_manager = WebSocketManager()


async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint handler"""
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            message_type = message.get("type")
            
            if message_type == "ping":
                # Handle ping/pong for keepalive
                await websocket_manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
            elif message_type == "handshake":
                # Handle initial handshake
                await websocket_manager.send_personal_message({
                    "type": "handshake_response",
                    "data": {
                        "message": "Handshake successful",
                        "server_version": "v0.1.0",
                        "features": ["canvas_control", "chat", "real_time_updates"]
                    },
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
            elif message_type == "chat_message":
                # Handle chat message
                user_message = message.get("message", "")
                conversation_id = message.get("conversation_id")
                allow_extended_iterations = message.get("allow_extended_iterations", False)
                
                if not user_message.strip():
                    await websocket_manager.send_personal_message({
                        "type": "error",
                        "data": {"message": "Empty message received"},
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                    continue
                
                # Process message with chatbot
                try:
                    response = await chatbot.process_user_message(
                        user_message, 
                        conversation_id, 
                        allow_extended_iterations=allow_extended_iterations
                    )
                    
                    # Send response back to client
                    await websocket_manager.send_personal_message({
                        "type": "chat_response",
                        "data": response,
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                    
                    # If the response indicates canvas changes, broadcast to other clients
                    if response.get("success") and response.get("function_calls_made", 0) > 0:
                        canvas_state = canvas_bridge.get_canvas_state()
                        await websocket_manager.broadcast({
                            "type": "canvas_update",
                            "data": canvas_state,
                            "timestamp": datetime.now().isoformat()
                        }, exclude=websocket)
                        
                except Exception as e:
                    print(f"[ERROR] Error processing chat message: {e}")
                    await websocket_manager.send_personal_message({
                        "type": "error",
                        "data": {"message": f"Error processing message: {str(e)}"},
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                
            elif message_type == "get_canvas_state":
                # Handle canvas state request
                try:
                    canvas_state = canvas_bridge.get_canvas_state()
                    await websocket_manager.send_personal_message({
                        "type": "canvas_state",
                        "data": canvas_state,
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                except Exception as e:
                    print(f"[ERROR] Error getting canvas state: {e}")
                    await websocket_manager.send_personal_message({
                        "type": "error",
                        "data": {"message": f"Error getting canvas state: {str(e)}"},
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                
            elif message_type == "get_help":
                # Handle help request
                help_text = chatbot.get_help_text()
                await websocket_manager.send_personal_message({
                    "type": "help_response",
                    "data": {"help_text": help_text},
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
            elif message_type == "clear_conversation":
                # Handle conversation history clear
                chatbot.clear_conversation_history()
                await websocket_manager.send_personal_message({
                    "type": "conversation_cleared",
                    "data": {"message": "Conversation history cleared"},
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
            elif message_type == "canvas_update_notification":
                # Handle canvas update notifications from frontend
                # This could be used for manual canvas changes made directly in the frontend
                canvas_data = message.get("data", {})
                
                # Broadcast the update to other clients
                await websocket_manager.broadcast({
                    "type": "canvas_update",
                    "data": canvas_data,
                    "timestamp": datetime.now().isoformat()
                }, exclude=websocket)
                
            else:
                # Unknown message type
                print(f"[WARNING] Unknown message type: {message_type}")
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "data": {"message": f"Unknown message type: {message_type}"},
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"[ERROR] WebSocket error: {e}")
        websocket_manager.disconnect(websocket) 