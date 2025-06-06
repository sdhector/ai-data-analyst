# API Layer - Detailed Documentation

## Overview

The API layer (`backend/api/`) serves as the primary communication interface between the AI Data Analyst frontend and the backend core services. This layer implements both traditional HTTP REST APIs and modern WebSocket connections to support different interaction patterns and use cases.

### Architecture Philosophy

The API layer follows a dual-protocol approach:
- **HTTP REST APIs**: For stateless operations, external integrations, and traditional request-response patterns
- **WebSocket Connections**: For real-time bidirectional communication, live updates, and interactive chat sessions

This design ensures maximum compatibility while providing optimal user experience through real-time features.

---

## HTTP Routes Module (`routes.py`)

### Module Overview

The `routes.py` module implements a comprehensive RESTful API using FastAPI's router system. It provides HTTP endpoints that serve as alternatives to WebSocket communication and enable external system integrations.

### Import Structure and Dependencies

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.chatbot import chatbot
from core.canvas_bridge import canvas_bridge
```

**Key Dependencies:**
- **FastAPI**: Modern async web framework for high-performance APIs
- **Pydantic**: Data validation and serialization for type-safe APIs
- **Core Services**: Direct integration with chatbot and canvas bridge

### Data Models and Schemas

#### Request Models

**ChatMessage Model**
```python
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
```

**Purpose**: Structures incoming chat messages for AI processing
**Fields**:
- `message`: The user's natural language input (required)
- `conversation_id`: Optional identifier for conversation context

**ContainerCreate Model**
```python
class ContainerCreate(BaseModel):
    container_id: str
    x: int
    y: int
    width: int
    height: int
    auto_adjust: bool = True
    avoid_overlap: bool = True
```

**Purpose**: Defines parameters for direct container creation
**Fields**:
- `container_id`: Unique identifier for the container
- `x`, `y`: Position coordinates in pixels
- `width`, `height`: Container dimensions in pixels
- `auto_adjust`: Enable automatic bounds adjustment
- `avoid_overlap`: Enable overlap prevention

**ContainerModify Model**
```python
class ContainerModify(BaseModel):
    x: int
    y: int
    width: int
    height: int
    auto_adjust: bool = True
    avoid_overlap: bool = True
```

**Purpose**: Specifies container modification parameters
**Note**: Similar to ContainerCreate but without container_id (provided in URL path)

#### Response Models

**ChatResponse Model**
```python
class ChatResponse(BaseModel):
    success: bool
    message: str
    conversation_id: Optional[str] = None
    timestamp: str
    function_calls_made: Optional[int] = None
    iterations: Optional[int] = None
```

**Purpose**: Standardized response format for chat interactions
**Fields**:
- `success`: Boolean indicating operation success
- `message`: Human-readable response message
- `conversation_id`: Echo of conversation context
- `timestamp`: ISO format timestamp of response
- `function_calls_made`: Number of AI function calls executed
- `iterations`: Number of processing iterations

**CanvasState Model**
```python
class CanvasState(BaseModel):
    hasContainers: bool
    containerCount: int
    containers: List[Dict[str, Any]]
    canvas_size: Dict[str, int]
    settings: Dict[str, Any]
```

**Purpose**: Complete canvas state representation
**Fields**:
- `hasContainers`: Quick boolean check for container existence
- `containerCount`: Total number of containers
- `containers`: Detailed list of all container objects
- `canvas_size`: Current canvas dimensions
- `settings`: Canvas behavior configuration

### Router Configuration

```python
router = APIRouter(prefix="/api", tags=["canvas"])
```

**Configuration Details:**
- **Prefix**: All endpoints prefixed with `/api`
- **Tags**: Grouped under "canvas" for OpenAPI documentation
- **Integration**: Included in main FastAPI application

### Core Endpoints

#### Chat Processing Endpoint

```python
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
```

**Purpose**: Processes natural language messages through the AI chatbot system

**Implementation Details:**
```python
async def chat_endpoint(chat_message: ChatMessage):
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
```

**Features:**
- Input validation for empty messages
- Asynchronous processing for non-blocking operations
- Comprehensive error handling with detailed messages
- Structured response format for consistent client handling

**Usage Example:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Create a container called test1", "conversation_id": "session_1"}'
```

#### Canvas State Management

**Get Canvas State**
```python
@router.get("/canvas/state", response_model=CanvasState)
async def get_canvas_state():
```

**Implementation:**
```python
async def get_canvas_state():
    try:
        state = canvas_bridge.get_canvas_state()
        return CanvasState(**state)
        
    except Exception as e:
        print(f"[ERROR] Error getting canvas state: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting canvas state: {str(e)}")
```

**Features:**
- Real-time state retrieval from canvas bridge
- Structured response with type validation
- Error handling for state access failures

**Get Canvas Size**
```python
@router.get("/canvas/size")
async def get_canvas_size():
```

**Response Format:**
```json
{
    "width": 800,
    "height": 600,
    "timestamp": "2024-01-01T00:00:00Z"
}
```

**Clear Canvas**
```python
@router.post("/canvas/clear")
async def clear_canvas():
```

**Features:**
- Removes all containers from canvas
- Returns success confirmation with timestamp
- Handles clearing failures gracefully

#### Direct Container Operations

**Create Container**
```python
@router.post("/container/create")
async def create_container_direct(container_data: ContainerCreate):
```

**Implementation Details:**
```python
async def create_container_direct(container_data: ContainerCreate):
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
```

**Features:**
- Direct canvas manipulation bypassing AI layer
- Full parameter control for programmatic access
- Validation and error handling
- Success confirmation with metadata

**Delete Container**
```python
@router.delete("/container/{container_id}")
async def delete_container_direct(container_id: str):
```

**URL Parameter**: `container_id` - The ID of container to delete

**Features:**
- RESTful URL parameter for container identification
- Existence validation before deletion
- Clear success/failure responses

**Modify Container**
```python
@router.put("/container/{container_id}")
async def modify_container_direct(container_id: str, container_data: ContainerModify):
```

**Features:**
- RESTful PUT method for container updates
- Combines URL parameter and request body
- Full modification control with validation

**Get Container Info**
```python
@router.get("/container/{container_id}")
async def get_container_info(container_id: str):
```

**Implementation:**
```python
async def get_container_info(container_id: str):
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
```

#### System Information Endpoints

**Help Endpoint**
```python
@router.get("/help")
async def get_help():
```

**Purpose**: Returns comprehensive help documentation for API usage

**Response Format:**
```json
{
    "help_text": "Detailed help content...",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

**Status Endpoint**
```python
@router.get("/status")
async def get_status():
```

**Implementation:**
```python
async def get_status():
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
```

**Features:**
- Comprehensive system health check
- Service status monitoring
- Canvas state summary
- Conversation context information

**Conversation Management**
```python
@router.get("/conversation/history")
async def get_conversation_history():

@router.post("/conversation/clear")
async def clear_conversation():
```

**Features:**
- Access to conversation history for debugging
- Manual conversation clearing
- Metadata about conversation state

### Error Handling Strategy

#### HTTP Status Codes

**Success Responses:**
- `200 OK`: Successful GET requests
- `201 Created`: Successful POST requests (implied)

**Client Error Responses:**
- `400 Bad Request`: Invalid input data or parameters
- `404 Not Found`: Requested resource doesn't exist

**Server Error Responses:**
- `500 Internal Server Error`: Unexpected server errors

#### Error Response Format

```python
class ErrorResponse(BaseModel):
    error: str
    timestamp: str
```

**Consistent Error Structure:**
```json
{
    "detail": "Error description",
    "status_code": 400
}
```

#### Exception Handling Pattern

```python
try:
    # Operation logic
    result = await some_operation()
    return success_response
except SpecificException as e:
    # Handle specific cases
    raise HTTPException(status_code=400, detail=f"Specific error: {str(e)}")
except Exception as e:
    # Handle unexpected errors
    print(f"[ERROR] Unexpected error: {e}")
    raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
```

### Integration Patterns

#### Core Service Integration

**Chatbot Integration:**
```python
response = await chatbot.process_user_message(message, conversation_id)
```

**Canvas Bridge Integration:**
```python
result = await canvas_bridge.create_container(...)
state = canvas_bridge.get_canvas_state()
```

#### Async/Await Usage

All endpoints use async/await for:
- Non-blocking I/O operations
- Concurrent request handling
- Integration with async core services

### Testing and Development

#### API Documentation

FastAPI automatically generates:
- OpenAPI/Swagger documentation at `/docs`
- ReDoc documentation at `/redoc`
- JSON schema at `/openapi.json`

#### Example Usage Patterns

**Programmatic Container Creation:**
```python
import requests

response = requests.post("http://localhost:8000/api/container/create", json={
    "container_id": "chart1",
    "x": 100,
    "y": 100,
    "width": 300,
    "height": 200,
    "auto_adjust": True,
    "avoid_overlap": True
})
```

**Chat Integration:**
```python
response = requests.post("http://localhost:8000/api/chat", json={
    "message": "Create three containers in a row",
    "conversation_id": "session_1"
})
```

---

## WebSocket Server Module (`websocket.py`)

### Module Overview

The `websocket.py` module implements a sophisticated real-time communication system using WebSocket connections. It enables bidirectional communication between the frontend and backend, supporting live chat interactions, real-time canvas updates, and multi-client synchronization.

### Import Structure and Dependencies

```python
import json
import asyncio
from typing import Dict, Any, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

from core.chatbot import chatbot
from core.canvas_bridge import canvas_bridge
```

**Key Dependencies:**
- **FastAPI WebSocket**: Native WebSocket support with async handling
- **JSON**: Message serialization and deserialization
- **AsyncIO**: Asynchronous operation support
- **Core Services**: Direct integration with chatbot and canvas systems

### WebSocket Manager Class

#### Class Definition and State Management

```python
class WebSocketManager:
    """Manages WebSocket connections and message routing"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
```

**State Management:**
- **Connection Registry**: Set-based storage for active WebSocket connections
- **Thread Safety**: Set operations are atomic for concurrent access
- **Memory Efficiency**: Automatic cleanup of disconnected clients

#### Connection Lifecycle Management

**Connection Establishment**
```python
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
```

**Features:**
- **Automatic Acceptance**: WebSocket handshake completion
- **Registry Management**: Addition to active connections
- **Canvas Integration**: Registration with canvas bridge for updates
- **Initial State Sync**: Immediate state synchronization for new clients
- **Error Handling**: Graceful handling of initial state failures

**Connection Termination**
```python
def disconnect(self, websocket: WebSocket):
    """Remove a WebSocket connection"""
    self.active_connections.discard(websocket)
    canvas_bridge.remove_websocket_connection(websocket)
    print(f"🔌 WebSocket client disconnected. Total connections: {len(self.active_connections)}")
```

**Features:**
- **Safe Removal**: Set.discard() doesn't raise errors for missing items
- **Canvas Cleanup**: Removal from canvas bridge notifications
- **Connection Tracking**: Real-time connection count monitoring

#### Message Communication

**Personal Messaging**
```python
async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
    """Send a message to a specific WebSocket connection"""
    try:
        await websocket.send_text(json.dumps(message))
    except Exception as e:
        print(f"[ERROR] Error sending personal message: {e}")
        self.disconnect(websocket)
```

**Features:**
- **JSON Serialization**: Automatic message formatting
- **Error Recovery**: Automatic disconnection on send failures
- **Type Safety**: Dictionary-based message structure

**Broadcasting System**
```python
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
```

**Features:**
- **Efficient Broadcasting**: Single JSON serialization for all clients
- **Exclusion Support**: Prevent echo effects by excluding sender
- **Automatic Cleanup**: Detection and removal of failed connections
- **Batch Operations**: Efficient handling of multiple disconnections

### Message Protocol and Handling

#### Message Structure

**Standard Message Format:**
```json
{
    "type": "message_type",
    "data": { /* message-specific data */ },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

**Required Fields:**
- `type`: Message type identifier for routing
- `data`: Message payload (optional for some types)
- `timestamp`: ISO format timestamp for ordering

#### Supported Message Types

**1. Handshake Messages**

**Client Request:**
```json
{
    "type": "handshake",
    "data": {
        "clientType": "v0.1_frontend",
        "version": "0.1.0"
    }
}
```

**Server Response:**
```json
{
    "type": "handshake_response",
    "data": {
        "message": "Handshake successful",
        "server_version": "v0.1.0",
        "features": ["canvas_control", "chat", "real_time_updates"]
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

**Purpose**: Initial connection establishment and capability negotiation

**2. Chat Messages**

**Client Request:**
```json
{
    "type": "chat_message",
    "message": "Create a container called test1",
    "conversation_id": "session_1",
    "allow_extended_iterations": false
}
```

**Server Response:**
```json
{
    "type": "chat_response",
    "data": {
        "success": true,
        "message": "Container 'test1' created successfully",
        "function_calls_made": 2,
        "iterations": 1
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

**Features:**
- **Natural Language Processing**: Integration with AI chatbot
- **Conversation Context**: Persistent conversation tracking
- **Extended Iterations**: Support for complex multi-step operations
- **Function Call Reporting**: Transparency in AI operations

**3. Canvas State Requests**

**Client Request:**
```json
{
    "type": "get_canvas_state"
}
```

**Server Response:**
```json
{
    "type": "canvas_state",
    "data": {
        "hasContainers": true,
        "containerCount": 2,
        "containers": [
            {
                "id": "test1",
                "x": 100,
                "y": 100,
                "width": 200,
                "height": 150
            }
        ],
        "canvas_size": {"width": 800, "height": 600}
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

**4. System Commands**

**Help Request:**
```json
{
    "type": "get_help"
}
```

**Clear Conversation:**
```json
{
    "type": "clear_conversation"
}
```

**5. Ping/Pong for Keepalive**

**Client Ping:**
```json
{
    "type": "ping"
}
```

**Server Pong:**
```json
{
    "type": "pong",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### Main WebSocket Endpoint

#### Endpoint Handler

```python
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
            
            # Message routing logic...
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"[ERROR] WebSocket error: {e}")
        websocket_manager.disconnect(websocket)
```

#### Message Routing Implementation

**Chat Message Processing:**
```python
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
```

**Features:**
- **Input Validation**: Empty message detection and handling
- **Asynchronous Processing**: Non-blocking chat processing
- **Automatic Broadcasting**: Canvas changes propagated to all clients
- **Error Isolation**: Individual message errors don't break connection

### Real-time Synchronization

#### Automatic State Broadcasting

**Canvas Update Propagation:**
```python
# If the response indicates canvas changes, broadcast to other clients
if response.get("success") and response.get("function_calls_made", 0) > 0:
    canvas_state = canvas_bridge.get_canvas_state()
    await websocket_manager.broadcast({
        "type": "canvas_update",
        "data": canvas_state,
        "timestamp": datetime.now().isoformat()
    }, exclude=websocket)
```

**Features:**
- **Change Detection**: Automatic detection of canvas modifications
- **Selective Broadcasting**: Exclude originating client to prevent echo
- **State Consistency**: All clients receive identical state updates
- **Timestamp Ordering**: Chronological message ordering

#### Multi-Client Coordination

**Connection State Management:**
- **Global Connection Registry**: Centralized tracking of all active connections
- **Canvas Bridge Integration**: Automatic registration for canvas updates
- **Cleanup Automation**: Automatic removal of disconnected clients

**State Synchronization:**
- **Initial State Sync**: New clients receive current state immediately
- **Live Updates**: Real-time propagation of all changes
- **Consistency Guarantees**: All clients maintain identical state

### Error Handling and Resilience

#### Connection Error Handling

**WebSocket Disconnection:**
```python
except WebSocketDisconnect:
    websocket_manager.disconnect(websocket)
```

**Unexpected Errors:**
```python
except Exception as e:
    print(f"[ERROR] WebSocket error: {e}")
    websocket_manager.disconnect(websocket)
```

**Features:**
- **Graceful Disconnection**: Proper cleanup on client disconnect
- **Error Logging**: Comprehensive error tracking for debugging
- **Connection Recovery**: Automatic cleanup prevents resource leaks

#### Message Error Handling

**JSON Parsing Errors:**
```python
try:
    message = json.loads(data)
except json.JSONDecodeError as e:
    await websocket_manager.send_personal_message({
        "type": "error",
        "data": {"message": f"Invalid JSON: {str(e)}"},
        "timestamp": datetime.now().isoformat()
    }, websocket)
    continue
```

**Unknown Message Types:**
```python
else:
    # Unknown message type
    print(f"[WARNING] Unknown message type: {message_type}")
    await websocket_manager.send_personal_message({
        "type": "error",
        "data": {"message": f"Unknown message type: {message_type}"},
        "timestamp": datetime.now().isoformat()
    }, websocket)
```

#### Resilience Features

**Connection Health Monitoring:**
- **Ping/Pong Implementation**: Regular connectivity verification
- **Automatic Cleanup**: Detection and removal of dead connections
- **Resource Management**: Prevention of connection leaks

**Message Delivery Guarantees:**
- **Error Detection**: Failed send operations trigger disconnection
- **Retry Logic**: Automatic connection cleanup on failures
- **State Recovery**: New connections receive full state sync

### Performance Considerations

#### Efficient Message Handling

**JSON Optimization:**
- **Single Serialization**: Broadcast messages serialized once
- **Minimal Payloads**: Efficient message structure design
- **Streaming Processing**: Continuous message processing loop

**Connection Management:**
- **Set-based Storage**: O(1) connection operations
- **Batch Cleanup**: Efficient handling of multiple disconnections
- **Memory Efficiency**: Automatic garbage collection of connections

#### Scalability Features

**Async Architecture:**
- **Non-blocking Operations**: All I/O operations use async/await
- **Concurrent Handling**: Multiple connections handled simultaneously
- **Resource Efficiency**: Minimal memory footprint per connection

**Broadcasting Optimization:**
- **Selective Broadcasting**: Exclude sender to prevent echo
- **Batch Operations**: Efficient multi-client message delivery
- **Error Isolation**: Individual connection failures don't affect others

### Integration with Core Services

#### Chatbot Integration

**Message Processing:**
```python
response = await chatbot.process_user_message(
    user_message, 
    conversation_id, 
    allow_extended_iterations=allow_extended_iterations
)
```

**Features:**
- **Async Processing**: Non-blocking AI operations
- **Context Preservation**: Conversation state management
- **Extended Operations**: Support for complex multi-step tasks

#### Canvas Bridge Integration

**State Synchronization:**
```python
canvas_bridge.add_websocket_connection(websocket)
canvas_state = canvas_bridge.get_canvas_state()
```

**Features:**
- **Automatic Registration**: WebSocket connections registered for updates
- **Real-time Updates**: Immediate state change notifications
- **Consistent State**: All clients maintain synchronized canvas state

This detailed documentation provides comprehensive coverage of the API layer's implementation, features, and integration patterns, enabling developers to understand and extend the system effectively. 