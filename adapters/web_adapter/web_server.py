"""
Web Server Adapter for AI Data Analyst

This module provides a FastAPI-based web server that:
- Serves the static web frontend files
- Handles WebSocket connections for real-time communication
- Provides REST API endpoints for the AI chatbot
- Bridges between the web frontend and existing Python backend
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Import core modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.ai_engine import AIOrchestrator
from core.function_registry.grid_management_functions import (
    add_container, remove_container, clear_grid, get_grid_status,
    move_container, resize_container, update_container_content
)


# Request/Response Models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    status: str
    message: str
    function_calls: Optional[List[Dict[str, Any]]] = []
    conversation_id: Optional[str] = None
    error: Optional[str] = None

class ContainerRequest(BaseModel):
    position: Optional[str] = None
    start_row: Optional[int] = None
    start_col: Optional[int] = None
    end_row: Optional[int] = None
    end_col: Optional[int] = None
    title: Optional[str] = None

class ChartRequest(BaseModel):
    container_id: str
    chart_type: str
    data: Dict[str, Any]


# Create FastAPI app
app = FastAPI(title="AI Data Analyst API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
ai_orchestrator: Optional[AIOrchestrator] = None
active_websockets: List[WebSocket] = []

# Setup logger
logger = logging.getLogger(__name__)


# Initialize AI Orchestrator
async def init_ai_orchestrator():
    """Initialize the AI Orchestrator"""
    global ai_orchestrator
    
    if ai_orchestrator is None:
        try:
            ai_orchestrator = AIOrchestrator()
            logger.info("AI Orchestrator initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AI Orchestrator: {e}", exc_info=True)
            return False
    return True


# Static file serving
static_path = Path(__file__).parent.parent.parent / "ui" / "web_frontend"
if static_path.exists():
    app.mount("/js", StaticFiles(directory=static_path / "js"), name="js")


# Serve styles.css directly
@app.get("/styles.css")
async def serve_styles():
    """Serve the CSS file"""
    css_path = static_path / "styles.css"
    if css_path.exists():
        return FileResponse(css_path, media_type="text/css")
    else:
        raise HTTPException(status_code=404, detail="styles.css not found")


# Root endpoint - serve index.html
@app.get("/")
async def read_root():
    """Serve the main HTML file"""
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return {"error": "Frontend files not found"}


# API Endpoints
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_initialized": ai_orchestrator is not None
    }


@app.get("/api/system/status")
async def get_system_status():
    """Get system status"""
    if not ai_orchestrator:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "error": "AI Orchestrator not initialized"}
        )
    
    status = ai_orchestrator.get_system_status()
    return status


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatMessage):
    """Handle chat messages"""
    if not ai_orchestrator:
        await init_ai_orchestrator()
    
    if not ai_orchestrator:
        return ChatResponse(
            status="error",
            message="",
            error="AI system not available"
        )
    
    try:
        logger.info(f"Processing WebSocket chat message for conversation_id: {conversation_id}")
        # Process the message
        response = ai_orchestrator.process_request(
            user_message=request.message,
            conversation_id=request.conversation_id,
            enable_functions=True
        )
        
        # Process function results for frontend
        processed_functions = []
        if response.get("function_calls"):
            for call in response["function_calls"]:
                # Handle container-related functions
                if call["function_name"] == "add_container" and call["result"]["status"] == "success":
                    # Ensure the frontend gets the position information
                    result = call["result"]["result"]
                    if "position" in result:
                        call["result"]["result"]["start_row"] = result["position"]["start_row"]
                        call["result"]["result"]["start_col"] = result["position"]["start_col"]
                        call["result"]["result"]["end_row"] = result["position"]["end_row"]
                        call["result"]["result"]["end_col"] = result["position"]["end_col"]
                
                processed_functions.append(call)
        
        return ChatResponse(
            status=response["status"],
            message=response["message"],
            function_calls=processed_functions,
            conversation_id=response.get("conversation_id")
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint for conversation_id '{request.conversation_id}': {e}", exc_info=True)
        return ChatResponse(
            status="error",
            message="",
            error=str(e)
        )


@app.get("/api/grid/status")
async def get_grid_status_endpoint():
    """Get current grid status"""
    return get_grid_status()


@app.post("/api/grid/container")
async def add_container_endpoint(request: ContainerRequest):
    """Add a new container to the grid"""
    result = add_container(
        position=request.position,
        start_row=request.start_row,
        start_col=request.start_col,
        end_row=request.end_row,
        end_col=request.end_col,
        title=request.title
    )
    
    # Broadcast to all connected clients
    await broadcast_message({
        "type": "grid_update",
        "data": result
    })
    
    return result


@app.delete("/api/grid/container/{container_id}")
async def remove_container_endpoint(container_id: str):
    """Remove a container from the grid"""
    result = remove_container(container_id)
    
    # Broadcast to all connected clients
    await broadcast_message({
        "type": "grid_update",
        "data": result
    })
    
    return result


@app.post("/api/grid/clear")
async def clear_grid_endpoint():
    """Clear all containers from the grid"""
    result = clear_grid()
    
    # Broadcast to all connected clients
    await broadcast_message({
        "type": "grid_update",
        "data": result
    })
    
    return result


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections"""
    await websocket.accept()
    active_websockets.append(websocket)
    logger.info(f"WebSocket client connected: {websocket.client}")
    
    # Initialize AI if needed
    if not ai_orchestrator:
        await init_ai_orchestrator()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError as jde:
                logger.warning(f"Failed to decode WebSocket JSON message from {websocket.client}. Data: '{data}'. Error: {jde}", exc_info=True)
                continue # Skip processing this message
            
            # Handle different message types
            if message["type"] == "handshake":
                # Send handshake response
                await websocket.send_json({
                    "type": "system",
                    "data": {
                        "message": "Handshake successful",
                        "server_version": "1.0.0"
                    }
                })
            
            elif message["type"] == "chat_message":
                # Process chat message
                response = await process_chat_message(
                    message.get("message", ""),
                    message.get("conversation_id")
                )
                
                # Send response
                await websocket.send_json({
                    "type": "chat_response",
                    "data": response
                })
            
            elif message["type"] == "container_removed":
                # Broadcast container removal
                await broadcast_message(
                    {
                        "type": "grid_update",
                        "data": {
                            "action": "container_removed",
                            "container_id": message.get("containerId")
                        }
                    },
                    exclude=websocket
                )
            
            elif message["type"] == "grid_cleared":
                # Broadcast grid clear
                await broadcast_message(
                    {
                        "type": "grid_update",
                        "data": {"action": "grid_cleared"}
                    },
                    exclude=websocket
                )
                
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
        logger.info(f"WebSocket client disconnected: {websocket.client}")
    except Exception as e:
        logger.error(f"WebSocket error for client {websocket.client}: {e}", exc_info=True)
        if websocket in active_websockets:
            active_websockets.remove(websocket)


async def process_chat_message(message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """Process chat message and return response"""
    if not ai_orchestrator:
        return {
            "status": "error",
            "error": "AI system not available"
        }
    
    try:
        # Process the message
        response = ai_orchestrator.process_request(
            user_message=message,
            conversation_id=conversation_id,
            enable_functions=True
        )
        
        # Process function results for frontend
        processed_functions = []
        if response.get("function_calls"):
            for call in response["function_calls"]:
                # Handle container-related functions
                if call["function_name"] == "add_container" and call["result"]["status"] == "success":
                    # Ensure the frontend gets the position information
                    result = call["result"]["result"]
                    if "position" in result:
                        call["result"]["result"]["start_row"] = result["position"]["start_row"]
                        call["result"]["result"]["start_col"] = result["position"]["start_col"]
                        call["result"]["result"]["end_row"] = result["position"]["end_row"]
                        call["result"]["result"]["end_col"] = result["position"]["end_col"]
                
                processed_functions.append(call)
        
        return {
            "status": response["status"],
            "message": response["message"],
            "function_calls": processed_functions,
            "conversation_id": response.get("conversation_id")
        }
        
    except Exception as e:
        logger.error(f"Error processing WebSocket chat message for conversation_id '{conversation_id}': {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }


async def broadcast_message(message: Dict[str, Any], exclude: Optional[WebSocket] = None):
    """Broadcast message to all connected WebSocket clients"""
    disconnected = []
    
    for ws in active_websockets:
        if ws != exclude:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
    
    # Remove disconnected clients
    for ws in disconnected:
        if ws in active_websockets:
            active_websockets.remove(ws)
            logger.warning(f"Removed disconnected client {ws.client} during broadcast attempt.")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("Starting AI Data Analyst Web Server...")
    await init_ai_orchestrator()
    logger.info("Web server ready!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("Shutting down web server...")
    # Close all WebSocket connections
    for ws in active_websockets:
        try:
            await ws.close()
        except Exception:
            pass
    active_websockets.clear()


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the web server"""
    uvicorn.run(
        "adapters.web_adapter.web_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    run_server() 