"""
HTTP API Routes for Canvas Control

Provides HTTP endpoints for canvas control operations as a fallback when WebSocket is not available.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.chatbot import chatbot
from core.canvas_bridge import canvas_bridge


# Request/Response Models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool
    message: str
    conversation_id: Optional[str] = None
    timestamp: str
    function_calls_made: Optional[int] = None
    iterations: Optional[int] = None


class CanvasState(BaseModel):
    hasContainers: bool
    containerCount: int
    containers: List[Dict[str, Any]]
    canvas_size: Dict[str, int]
    settings: Dict[str, Any]


class ErrorResponse(BaseModel):
    error: str
    timestamp: str


# Create router
router = APIRouter(prefix="/api", tags=["canvas"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """
    Process a chat message and return the response
    """
    try:
        if not chat_message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Process message with chatbot
        response = await chatbot.process_user_message(
            chat_message.message, 
            chat_message.conversation_id
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        print(f"[ERROR] Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/canvas/state", response_model=CanvasState)
async def get_canvas_state():
    """
    Get the current state of the canvas
    """
    try:
        state = canvas_bridge.get_canvas_state()
        return CanvasState(**state)
        
    except Exception as e:
        print(f"[ERROR] Error getting canvas state: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting canvas state: {str(e)}")


@router.get("/canvas/size")
async def get_canvas_size():
    """
    Get the current canvas dimensions
    """
    try:
        size = canvas_bridge.get_canvas_size()
        return {
            "width": size["width"],
            "height": size["height"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[ERROR] Error getting canvas size: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting canvas size: {str(e)}")


@router.post("/canvas/clear")
async def clear_canvas():
    """
    Clear all containers from the canvas
    """
    try:
        result = await canvas_bridge.clear_canvas()
        
        if result:
            return {
                "success": True,
                "message": "Canvas cleared successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear canvas")
            
    except Exception as e:
        print(f"[ERROR] Error clearing canvas: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing canvas: {str(e)}")


@router.get("/help")
async def get_help():
    """
    Get help information for using the chatbot
    """
    try:
        help_text = chatbot.get_help_text()
        return {
            "help_text": help_text,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[ERROR] Error getting help: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting help: {str(e)}")


@router.get("/conversation/history")
async def get_conversation_history():
    """
    Get the current conversation history
    """
    try:
        history = chatbot.get_conversation_history()
        return {
            "history": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[ERROR] Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting conversation history: {str(e)}")


@router.post("/conversation/clear")
async def clear_conversation():
    """
    Clear the conversation history
    """
    try:
        chatbot.clear_conversation_history()
        return {
            "success": True,
            "message": "Conversation history cleared",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[ERROR] Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing conversation: {str(e)}")


@router.get("/status")
async def get_status():
    """
    Get the current status of the backend services
    """
    try:
        canvas_state = canvas_bridge.get_canvas_state()
        
        return {
            "status": "healthy",
            "version": "v0.1.0",
            "services": {
                "llm_client": "connected" if chatbot.llm_client else "disconnected",
                "canvas_bridge": "active",
                "function_executor": "active" if chatbot.function_executor else "inactive"
            },
            "canvas": {
                "container_count": canvas_state["containerCount"],
                "canvas_size": canvas_state["canvas_size"]
            },
            "conversation": {
                "history_length": len(chatbot.get_conversation_history())
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[ERROR] Error getting status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


# Container management endpoints (direct API access)
class ContainerCreate(BaseModel):
    container_id: str
    x: int
    y: int
    width: int
    height: int
    auto_adjust: bool = True
    avoid_overlap: bool = True


class ContainerModify(BaseModel):
    x: int
    y: int
    width: int
    height: int
    auto_adjust: bool = True
    avoid_overlap: bool = True


@router.post("/container/create")
async def create_container_direct(container_data: ContainerCreate):
    """
    Create a container directly via API (bypasses LLM)
    """
    try:
        result = await canvas_bridge.create_container(
            container_data.container_id,
            container_data.x,
            container_data.y,
            container_data.width,
            container_data.height,
            container_data.auto_adjust,
            container_data.avoid_overlap
        )
        
        if result:
            return {
                "success": True,
                "message": f"Container '{container_data.container_id}' created successfully",
                "container_id": container_data.container_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create container")
            
    except Exception as e:
        print(f"[ERROR] Error creating container: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating container: {str(e)}")


@router.delete("/container/{container_id}")
async def delete_container_direct(container_id: str):
    """
    Delete a container directly via API (bypasses LLM)
    """
    try:
        result = await canvas_bridge.delete_container(container_id)
        
        if result:
            return {
                "success": True,
                "message": f"Container '{container_id}' deleted successfully",
                "container_id": container_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Container '{container_id}' not found")
            
    except Exception as e:
        print(f"[ERROR] Error deleting container: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting container: {str(e)}")


@router.put("/container/{container_id}")
async def modify_container_direct(container_id: str, container_data: ContainerModify):
    """
    Modify a container directly via API (bypasses LLM)
    """
    try:
        result = await canvas_bridge.modify_container(
            container_id,
            container_data.x,
            container_data.y,
            container_data.width,
            container_data.height,
            container_data.auto_adjust,
            container_data.avoid_overlap
        )
        
        if result:
            return {
                "success": True,
                "message": f"Container '{container_id}' modified successfully",
                "container_id": container_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Container '{container_id}' not found")
            
    except Exception as e:
        print(f"[ERROR] Error modifying container: {e}")
        raise HTTPException(status_code=500, detail=f"Error modifying container: {str(e)}")


@router.get("/container/{container_id}")
async def get_container_info(container_id: str):
    """
    Get information about a specific container
    """
    try:
        canvas_state = canvas_bridge.get_canvas_state()
        
        for container in canvas_state["containers"]:
            if container["id"] == container_id:
                return {
                    "container": container,
                    "timestamp": datetime.now().isoformat()
                }
        
        raise HTTPException(status_code=404, detail=f"Container '{container_id}' not found")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Error getting container info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting container info: {str(e)}") 