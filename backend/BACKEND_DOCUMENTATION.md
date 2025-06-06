# AI Data Analyst Backend Documentation

## Introduction

The AI Data Analyst backend is a sophisticated Python-based server application that serves as the intelligent core of an AI-powered data analysis and visualization system. This backend is designed to process natural language queries, execute canvas operations, and maintain real-time communication with the frontend through WebSocket connections and HTTP APIs.

### Application Context

The AI Data Analyst is a comprehensive system that seamlessly integrates frontend and backend components:

- **Frontend Interface**: A compact, modern web interface (`frontend/`) that provides users with an interactive canvas for creating and manipulating visual containers while maintaining real-time communication with the backend
- **Backend Engine**: This sophisticated Python server that processes natural language queries, executes AI-driven canvas operations, and manages the application state
- **Real-time Communication**: WebSocket-based bidirectional communication enabling instant synchronization between user actions and AI responses
- **HTTP API Layer**: RESTful endpoints providing alternative access methods and integration capabilities

The backend specifically focuses on:
- **Natural Language Processing**: Using OpenAI's GPT models to interpret user commands and convert them into canvas operations
- **Intelligent Canvas Management**: Automatically optimizing container layouts, managing overlaps, and ensuring efficient space utilization
- **Function Execution**: Bridging AI decisions to actual canvas manipulations through a sophisticated function calling system
- **State Management**: Maintaining consistent application state across multiple client connections
- **Configuration Management**: Handling environment variables, API keys, and application settings

## Architecture Overview

The backend follows a modular, service-oriented architecture with three main organizational folders:

1. **API Layer** (`api/`) - Handles external communication through HTTP routes and WebSocket endpoints
2. **Configuration** (`config/`) - Manages application settings, environment variables, and configuration schemas
3. **Core Services** (`core/`) - Contains the business logic, AI integration, and canvas management systems

The application uses a real-time communication model where:
- User interactions from the frontend trigger WebSocket messages to the backend
- The AI engine processes natural language commands and converts them to function calls
- Canvas operations are executed and synchronized across all connected clients
- HTTP APIs provide alternative access for integration and testing purposes

### Technology Stack

- **Framework**: FastAPI for high-performance async web services
- **AI Integration**: OpenAI GPT models for natural language processing
- **Real-time Communication**: WebSocket for bidirectional client-server communication
- **Environment Management**: python-dotenv for configuration management
- **Validation**: Pydantic for data validation and serialization

---

## API Layer (`api/`)

### Purpose
The API layer serves as the communication interface between the frontend and the backend core services. It provides both HTTP REST endpoints and WebSocket connections for different interaction patterns and use cases.

### Components Overview

The API layer consists of two main modules:
- **`routes.py`**: HTTP REST API endpoints for stateless operations and integration
- **`websocket.py`**: WebSocket server for real-time bidirectional communication

### HTTP Routes (`routes.py`)

#### Purpose
Provides RESTful HTTP endpoints as a fallback communication method when WebSocket is not available, and for external integrations that prefer traditional HTTP APIs.

#### Key Features

**Chat Endpoint**
```python
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage)
```
- Processes natural language messages through the AI chatbot
- Returns structured responses with success status and metadata
- Supports conversation context through optional conversation IDs
- Handles error cases gracefully with detailed error messages

**Canvas State Management**
```python
@router.get("/canvas/state", response_model=CanvasState)
async def get_canvas_state()

@router.get("/canvas/size")
async def get_canvas_size()

@router.post("/canvas/clear")
async def clear_canvas()
```
- Provides read access to current canvas state and dimensions
- Allows clearing all containers from the canvas
- Returns structured data models for consistent API responses

**Direct Container Operations**
```python
@router.post("/container/create")
async def create_container_direct(container_data: ContainerCreate)

@router.delete("/container/{container_id}")
async def delete_container_direct(container_id: str)

@router.put("/container/{container_id}")
async def modify_container_direct(container_id: str, container_data: ContainerModify)
```
- Bypasses the AI layer for direct canvas manipulation
- Useful for programmatic access and testing
- Includes validation and error handling
- Supports auto-adjustment and overlap prevention settings

**System Information**
```python
@router.get("/help")
async def get_help()

@router.get("/status")
async def get_status()

@router.get("/conversation/history")
async def get_conversation_history()
```
- Provides system status and health information
- Returns help documentation for API usage
- Manages conversation history for debugging and analysis

#### Data Models

**Request Models**
- `ChatMessage`: Structures incoming chat messages with optional conversation context
- `ContainerCreate`: Defines parameters for direct container creation
- `ContainerModify`: Specifies container modification parameters

**Response Models**
- `ChatResponse`: Standardized chat response with success status and metadata
- `CanvasState`: Complete canvas state including containers and settings
- `ErrorResponse`: Consistent error reporting structure

#### Error Handling
- Comprehensive exception handling with detailed error messages
- HTTP status codes following REST conventions
- Structured error responses for programmatic handling
- Logging of errors for debugging and monitoring

### WebSocket Server (`websocket.py`)

#### Purpose
Provides real-time bidirectional communication between the frontend and backend, enabling instant synchronization of canvas operations and chat interactions.

#### Connection Management

**WebSocketManager Class**
```python
class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
```

**Key Features:**
- Maintains active connection registry
- Handles connection lifecycle (connect, disconnect, cleanup)
- Provides broadcasting capabilities to all connected clients
- Integrates with canvas bridge for automatic state synchronization

**Connection Lifecycle**
```python
async def connect(self, websocket: WebSocket)
async def disconnect(self, websocket: WebSocket)
async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket)
async def broadcast(self, message: Dict[str, Any], exclude: WebSocket = None)
```

#### Message Handling

**Supported Message Types:**

1. **Handshake Messages**
   ```python
   {"type": "handshake", "data": {"clientType": "v0.1_frontend", "version": "0.1.0"}}
   ```
   - Initial connection establishment
   - Client identification and capability negotiation
   - Server feature advertisement

2. **Chat Messages**
   ```python
   {"type": "chat_message", "message": "Create a container", "conversation_id": "session_1"}
   ```
   - Natural language command processing
   - Integration with AI chatbot for intelligent responses
   - Support for extended iteration modes for complex operations

3. **Canvas State Requests**
   ```python
   {"type": "get_canvas_state"}
   ```
   - Real-time canvas state retrieval
   - Automatic state synchronization across clients

4. **System Commands**
   ```python
   {"type": "get_help"}
   {"type": "clear_conversation"}
   ```
   - System information and help requests
   - Conversation management operations

5. **Ping/Pong**
   ```python
   {"type": "ping"}
   ```
   - Connection keepalive mechanism
   - Network connectivity verification

#### Real-time Synchronization

**Automatic Broadcasting**
- Canvas changes are automatically broadcast to all connected clients
- State updates ensure all frontends remain synchronized
- Excludes the originating client to prevent echo effects

**State Management Integration**
- Direct integration with canvas bridge for state updates
- Automatic client notification on canvas modifications
- Consistent state across multiple concurrent users

#### Error Handling and Resilience

**Connection Resilience**
- Automatic cleanup of disconnected clients
- Graceful handling of network interruptions
- Connection state monitoring and recovery

**Message Validation**
- JSON parsing with error handling
- Message type validation and routing
- Structured error responses for invalid requests

**Error Response Format**
```python
{
    "type": "error",
    "data": {"message": "Error description"},
    "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Integration Points

**Chatbot Integration**
- Direct integration with core chatbot for message processing
- Support for function calling and extended iterations
- Conversation context management

**Canvas Bridge Integration**
- Real-time canvas operation execution
- State synchronization across all connected clients
- Automatic optimization and layout management

---

## Configuration (`config/`)

### Purpose
The configuration module manages application settings, environment variables, and configuration schemas using Pydantic for type safety and validation.

### Settings Management (`settings.py`)

#### Purpose
Centralizes all application configuration using Pydantic BaseSettings for type-safe configuration management with automatic environment variable loading.

#### Configuration Architecture

**Settings Class Structure**
```python
class Settings(BaseSettings):
    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False
    
    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    # Canvas settings
    default_canvas_width: int = 800
    default_canvas_height: int = 600
```

#### Configuration Categories

**Server Configuration**
- `host`: Server bind address (default: "127.0.0.1")
- `port`: Server port (default: 8000)
- `reload`: Development auto-reload flag (default: False)

**AI Integration Settings**
- `openai_api_key`: OpenAI API key for GPT model access
- `openai_model`: Default model selection (default: "gpt-4o-mini")

**Canvas Behavior Settings**
- `default_canvas_width`: Initial canvas width in pixels (default: 800)
- `default_canvas_height`: Initial canvas height in pixels (default: 600)

**Chatbot Configuration**
- `max_conversation_history`: Maximum conversation messages to retain (default: 20)
- `max_function_calls_per_turn`: Limit on function calls per user message (default: 5)
- `function_call_timeout`: Timeout for function execution in seconds (default: 30)

**WebSocket Settings**
- `websocket_ping_interval`: Ping interval for connection keepalive (default: 30)
- `websocket_ping_timeout`: Ping timeout threshold (default: 10)

**CORS Configuration**
- `cors_origins`: Allowed origins for cross-origin requests (default: ["*"])
- `cors_allow_credentials`: Enable credential sharing (default: True)

**Logging Configuration**
- `log_level`: Application logging level (default: "info")

#### Environment Variable Integration

**Automatic Loading**
```python
class Config:
    env_file = ".env"
    env_prefix = "AI_DATA_ANALYST_"
```

**Environment Variable Sources:**
1. **Direct Environment Variables**: System environment variables
2. **`.env` File**: Root directory `.env` file for development
3. **Prefixed Variables**: Variables with `AI_DATA_ANALYST_` prefix for namespacing

**Variable Resolution Priority:**
1. Explicit environment variables (highest priority)
2. `.env` file variables
3. Default values defined in the Settings class (lowest priority)

#### Type Safety and Validation

**Pydantic Integration**
- Automatic type conversion and validation
- Runtime type checking for configuration values
- Clear error messages for invalid configurations

**Optional vs Required Settings**
- Required settings raise errors if not provided
- Optional settings use sensible defaults
- Type hints provide clear documentation of expected types

#### Global Settings Instance

**Singleton Pattern**
```python
# Global settings instance
settings = Settings()
```

**Usage Throughout Application**
- Centralized configuration access point
- Consistent settings across all modules
- Easy testing with configuration overrides

#### Development vs Production

**Development Features**
- Auto-reload support for code changes
- Permissive CORS settings for local development
- Debug-friendly logging levels

**Production Considerations**
- Secure API key management through environment variables
- Restrictive CORS settings for security
- Performance-optimized settings

---

## Core Services (`core/`)

### Purpose
The core services module contains the business logic, AI integration, and canvas management systems that power the intelligent functionality of the AI Data Analyst application.

### Components Overview

The core services consist of five main modules:
- **`llm_client.py`**: OpenAI API integration and function schema management
- **`chatbot.py`**: Main orchestrator for AI-driven conversations and operations
- **`function_executor.py`**: Bridges AI function calls to actual canvas operations
- **`canvas_bridge.py`**: Canvas state management and frontend communication
- **Additional modules**: Supporting utilities and specialized functionality

### LLM Client (`llm_client.py`)

#### Purpose
Handles OpenAI API communication with canvas-specific function schemas, providing the AI intelligence layer for natural language processing and function calling.

#### Environment Integration

**Automatic Environment Loading**
```python
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")
```

**Key Features:**
- Loads environment variables from root `.env` file
- Resolves path relative to the module location
- Ensures API key availability before client initialization

#### CanvasLLMClient Class

**Initialization and Configuration**
```python
def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
    self.api_key = api_key or os.getenv("OPENAI_API_KEY")
    self.model = model
    self.client = OpenAI(api_key=self.api_key)
```

**Features:**
- Automatic API key resolution from environment variables
- Configurable model selection with sensible defaults
- Validation of API key availability with clear error messages

#### System Message and Behavior

**Comprehensive System Prompt**
The system message defines the AI assistant's behavior and capabilities:

- **Role Definition**: Canvas Control Assistant with specific capabilities
- **Canvas Specifications**: Coordinate system, size constraints, and behavior rules
- **Execution Rules**: Critical guidelines for following user instructions precisely
- **Optimization Guidelines**: Automatic space utilization and layout optimization
- **Error Handling**: Instructions for graceful error recovery and user communication

**Key Behavioral Rules:**
1. Never deviate from user requests without explicit clarification
2. Always check canvas state before operations
3. Maximize canvas space usage through automatic optimization
4. Provide detailed feedback on optimization results
5. Handle errors gracefully with alternative approaches

#### Function Schema Management

**Available Functions:**
```python
def get_function_schemas(self) -> List[Dict]:
```

**Core Canvas Operations:**
- `create_container`: Create containers with automatic optimal layout
- `delete_container`: Remove containers with state validation
- `modify_container`: Update containers with re-optimization
- `get_canvas_state`: Retrieve current canvas state and container information
- `clear_canvas`: Remove all containers from the canvas

**Canvas Management:**
- `get_canvas_size`: Get current canvas dimensions
- `edit_canvas_size`: Resize canvas with automatic container optimization
- `take_screenshot`: Capture current canvas state

**System Operations:**
- `get_canvas_settings`: Retrieve current behavior settings
- `check_container_content`: Inspect container contents and properties

**Advanced Features:**
- `create_pie_chart`: Placeholder for future chart functionality

#### Chat Completion System

**Function Calling Integration**
```python
def chat_completion(self, messages: List[Dict], functions: List[Dict] = None) -> Dict[str, Any]:
```

**Features:**
- Modern tools API format for better compatibility
- Automatic function schema conversion
- Temperature optimization for consistent function calling
- Token limit management for reliable responses

**Response Handling:**
- Support for both old `function_call` and new `tool_calls` formats
- Comprehensive error handling and status reporting
- Structured response format for consistent processing

### Chatbot Orchestrator (`chatbot.py`)

#### Purpose
Main chatbot class that orchestrates LLM and canvas operations, managing conversation flow, function execution, and state consistency.

#### CanvasChatbot Class

**Initialization and Component Management**
```python
def __init__(self):
    self.llm_client = None
    self.function_executor = None
    self.conversation_history = []
    self.auto_adjust_enabled = True
    self.overlap_prevention_enabled = False
```

**Component Initialization:**
- Automatic LLM client setup with error handling
- Function executor initialization with chatbot reference
- Conversation history management
- Canvas behavior settings control

#### Message Processing System

**Core Processing Method**
```python
async def process_user_message(self, user_message: str, conversation_id: str = None, 
                              allow_extended_iterations: bool = False) -> Dict[str, Any]:
```

**Processing Flow:**
1. **Message Preparation**: Add system message and conversation history
2. **Iterative Processing**: Handle multiple function calls with configurable limits
3. **Function Execution**: Execute AI-requested functions through the function executor
4. **Response Generation**: Provide final user-facing responses
5. **History Management**: Update conversation context for future interactions

**Advanced Features:**

**Extended Iteration Support**
- Configurable iteration limits (5 standard, 10 extended)
- User-controlled continuation for complex operations
- Automatic detection of continuation keywords
- Graceful handling of iteration limits with user prompts

**Function Call Management**
- Support for both old and new OpenAI API formats
- Multiple function calls per iteration
- Comprehensive error handling and recovery
- Function result integration into conversation context

**Error Handling and Recovery**
- Graceful handling of function execution errors
- Continuation of processing despite individual function failures
- Detailed error reporting with context
- Alternative approach suggestions

#### Conversation Management

**History Tracking**
```python
def get_conversation_history(self) -> List[Dict[str, Any]]:
def clear_conversation_history(self):
```

**Features:**
- Automatic conversation history maintenance
- Configurable history length limits (default: 20 messages)
- Context preservation across function calls
- Manual history clearing for fresh starts

**Context Management:**
- User message and assistant response pairing
- Function call and result integration
- System message injection for new conversations
- Memory-efficient history truncation

#### Help and Documentation

**Comprehensive Help System**
```python
def get_help_text(self) -> str:
```

**Help Content:**
- Available command examples with natural language
- Canvas specifications and coordinate system explanation
- Behavior settings documentation
- Tips for effective interaction
- Common use case examples

### Function Executor (`function_executor.py`)

#### Purpose
Bridges LLM function calls to actual canvas operations, providing intelligent layout optimization, identifier validation, and comprehensive error handling.

#### CanvasFunctionExecutor Class

**Initialization and Configuration**
```python
def __init__(self, chatbot_instance=None):
    self.chatbot = chatbot_instance
    self.canvas_bridge = canvas_bridge
    self.auto_adjust_enabled = True
    self.overlap_prevention_enabled = False
```

#### Identifier Management System

**Unique Identifier Validation**
```python
def _validate_identifier_uniqueness(self, proposed_id, element_type="element"):
```

**Features:**
- Cross-element identifier uniqueness validation
- Automatic identifier cleaning and normalization
- Conflict detection with detailed error reporting
- Alternative identifier suggestions for conflicts
- Support for multiple element types (containers, charts, etc.)

**Identifier Conflict Resolution**
```python
def _generate_alternative_identifiers(self, base_id, used_ids, max_suggestions=5):
```

**Suggestion Strategies:**
- Numbered variations (`container_1`, `container_2`)
- Common suffixes (`container_new`, `container_alt`)
- Prefix variations (`new_container`, `my_container`)
- Intelligent conflict avoidance

#### Layout Optimization System

**Automatic Layout Calculation**
```python
def _get_all_containers_for_optimization(self, new_container_id=None, exclude_container_id=None):
```

**Optimization Features:**
- Grid-based layout calculation for optimal space usage
- Automatic size uniformity for visual consistency
- Padding calculation based on canvas size
- Space utilization metrics and reporting

**Layout Application**
```python
async def _apply_optimized_layout(self, optimization_result, target_container_id=None):
```

**Application Process:**
- Batch container operations for consistency
- Individual operation success tracking
- Rollback capabilities for failed operations
- Detailed result reporting with metrics

#### Function Execution System

**Core Execution Method**
```python
async def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
```

**Supported Functions:**

**Container Operations:**
- `create_container`: Create with automatic optimization and validation
- `delete_container`: Remove with re-optimization of remaining containers
- `modify_container`: Update with full layout re-optimization
- `clear_canvas`: Remove all containers with state cleanup

**Canvas Management:**
- `get_canvas_state`: Retrieve formatted state information
- `get_canvas_size`: Get current dimensions
- `edit_canvas_size`: Resize with automatic container re-optimization
- `take_screenshot`: Capture current state

**System Operations:**
- `get_canvas_settings`: Retrieve behavior configuration
- `check_container_content`: Inspect container properties

#### Advanced Error Handling

**Comprehensive Validation**
- Input parameter validation with type checking
- Existence validation for container operations
- Bounds checking for canvas constraints
- Identifier uniqueness enforcement

**Detailed Error Reporting**
- Structured error responses with context
- Available alternatives and suggestions
- Current state information for debugging
- Clear user-facing error messages

**Graceful Degradation**
- Partial success handling for batch operations
- Alternative approach suggestions
- State consistency maintenance during failures
- Recovery guidance for users

### Canvas Bridge (`canvas_bridge.py`)

#### Purpose
Provides the interface between backend logic and frontend canvas, managing canvas state, WebSocket communication, and container operations with intelligent optimization.

#### CanvasBridge Class

**State Management**
```python
def __init__(self):
    self.websocket_connections: Set = set()
    self.canvas_state = {
        "containers": {},
        "canvas_size": {"width": 800, "height": 600},
        "settings": {"auto_adjust": True, "overlap_prevention": False},
        "last_updated": datetime.now().isoformat()
    }
```

**Features:**
- Centralized canvas state storage
- WebSocket connection management
- Automatic timestamp tracking
- Configurable behavior settings

#### WebSocket Communication

**Connection Management**
```python
def add_websocket_connection(self, websocket):
def remove_websocket_connection(self, websocket):
async def broadcast_to_frontend(self, message: Dict[str, Any]):
```

**Broadcasting Features:**
- Automatic message distribution to all connected clients
- Connection health monitoring and cleanup
- JSON serialization and error handling
- Disconnection detection and recovery

#### Container Operations

**Container Creation**
```python
async def create_container(self, container_id: str, x: int, y: int, width: int, height: int, 
                          auto_adjust: bool = True, avoid_overlap: bool = True) -> bool:
```

**Creation Process:**
1. **Input Validation**: Parameter type and range checking
2. **Bounds Adjustment**: Automatic fitting within canvas constraints
3. **Overlap Detection**: Intelligent positioning to avoid conflicts
4. **State Update**: Internal state management with timestamps
5. **Frontend Notification**: WebSocket broadcast to all clients

**Container Modification**
```python
async def modify_container(self, container_id: str, x: int, y: int, width: int, height: int,
                          auto_adjust: bool = True, avoid_overlap: bool = True) -> bool:
```

**Modification Features:**
- Existence validation before modification
- Similar bounds and overlap checking as creation
- State consistency maintenance
- Automatic frontend synchronization

**Container Deletion**
```python
async def delete_container(self, container_id: str) -> bool:
```

**Deletion Process:**
- Existence validation with clear error messages
- State cleanup and timestamp updates
- Frontend notification for UI updates
- Comprehensive success/failure reporting

#### Intelligent Layout System

**Overlap Detection**
```python
def check_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
```

**Non-overlapping Positioning**
```python
def find_non_overlapping_position(self, width, height, canvas_width, canvas_height, 
                                existing_containers, preferred_x=None, preferred_y=None):
```

**Positioning Algorithm:**
- Grid-based scanning for optimal placement
- Preference for user-specified positions when possible
- Multi-resolution search (coarse to fine)
- Fallback strategies for constrained spaces

**Optimal Layout Calculation**
```python
def calculate_optimal_layout(self, containers, canvas_width, canvas_height):
```

**Layout Features:**
- Automatic grid dimension calculation
- Space utilization optimization
- Uniform container sizing for visual consistency
- Padding calculation based on canvas size
- Comprehensive metrics and reporting

#### Canvas Management

**State Retrieval**
```python
def get_canvas_state(self) -> Dict[str, Any]:
def get_canvas_size(self) -> Dict[str, int]:
```

**Canvas Operations**
```python
async def clear_canvas(self) -> bool:
async def take_screenshot(self, filename: str = None) -> str:
```

**Management Features:**
- Formatted state information for frontend consumption
- Automatic filename generation for screenshots
- Batch operations with transaction-like behavior
- Comprehensive success/failure reporting

#### Error Handling and Resilience

**Validation and Safety**
- Comprehensive input validation
- Bounds checking for all operations
- State consistency verification
- Graceful error recovery

**Communication Resilience**
- WebSocket connection health monitoring
- Automatic cleanup of dead connections
- Error handling in broadcast operations
- Fallback mechanisms for communication failures

---

## Integration and Communication Flow

### Backend-Frontend Integration
The backend maintains seamless integration with the frontend through multiple communication channels:

1. **WebSocket Communication**: Real-time bidirectional communication for instant canvas updates and chat interactions
2. **HTTP API Access**: RESTful endpoints for integration, testing, and alternative access patterns
3. **State Synchronization**: Automatic state management ensuring consistency across multiple client connections
4. **Error Handling**: Comprehensive error reporting and recovery mechanisms

### AI-Driven Operation Flow

#### Natural Language Processing
1. **User Input**: Natural language commands received via WebSocket or HTTP
2. **AI Interpretation**: OpenAI GPT models process commands and determine appropriate actions
3. **Function Calling**: AI generates structured function calls for canvas operations
4. **Execution**: Function executor validates and executes operations with optimization
5. **Response Generation**: AI provides user-friendly summaries of completed operations

#### Intelligent Canvas Management
1. **State Analysis**: Current canvas state evaluation before operations
2. **Optimization Calculation**: Automatic layout optimization for space efficiency
3. **Operation Execution**: Canvas operations with safety constraints and validation
4. **Synchronization**: Real-time updates broadcast to all connected clients
5. **Feedback Loop**: Operation results fed back to AI for response generation

### Environment Configuration Flow

#### Configuration Loading Priority
1. **Environment Variables**: Direct system environment variables (highest priority)
2. **`.env` File**: Root directory configuration file loaded by `llm_client.py`
3. **Settings Defaults**: Pydantic BaseSettings default values (lowest priority)

#### API Key Management
- **Primary Loading**: `llm_client.py` loads `.env` file from root directory
- **Validation**: Multiple validation points ensure API key availability
- **Error Handling**: Clear error messages for missing or invalid API keys
- **Security**: Environment-based configuration prevents key exposure in code

### Performance Considerations

#### Efficient State Management
- **In-memory State**: Fast access to canvas state and container information
- **WebSocket Pooling**: Efficient connection management for multiple clients
- **Batch Operations**: Optimized container operations with minimal frontend updates
- **Lazy Loading**: On-demand initialization of expensive components

#### AI Integration Optimization
- **Function Schema Caching**: Pre-computed function schemas for faster API calls
- **Conversation Context**: Efficient history management with configurable limits
- **Token Management**: Optimized prompts and responses to minimize API costs
- **Error Recovery**: Intelligent retry mechanisms for transient failures

#### Scalability Features
- **Async Architecture**: FastAPI async support for high concurrency
- **Connection Management**: Efficient WebSocket connection pooling
- **State Isolation**: Clean separation between different user sessions
- **Resource Management**: Automatic cleanup of inactive connections and resources

This backend provides a robust, intelligent foundation for AI-driven data analysis applications, combining modern Python web technologies with sophisticated AI integration and real-time communication capabilities. 