# Core Services - Detailed Documentation

## Overview

The core services module (`backend/core/`) contains the business logic, AI integration, and canvas management systems that power the intelligent functionality of the AI Data Analyst application. This module implements the sophisticated algorithms and integrations that enable natural language processing, intelligent canvas operations, and real-time state management.

---

## LLM Client Module (`llm_client.py`)

### Purpose and Architecture

The LLM Client module provides OpenAI API integration with canvas-specific function schemas, serving as the AI intelligence layer for natural language processing and function calling.

### Environment Integration

```python
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")
```

**Path Resolution**: `backend/core/llm_client.py` → `../../../.env` → **ROOT/.env**

### CanvasLLMClient Class

#### Initialization
```python
def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
    self.api_key = api_key or os.getenv("OPENAI_API_KEY")
    self.model = model
    self.client = OpenAI(api_key=self.api_key)
```

#### System Message Design
The system message defines AI behavior with specific rules:
- Never deviate from user requests without clarification
- Always check canvas state before operations
- Maximize canvas space usage through optimization
- Provide detailed feedback on operations

#### Function Schema Management
```python
def get_function_schemas(self) -> List[Dict]:
    return [
        {
            "name": "create_container",
            "description": "Create container with automatic optimal layout",
            "parameters": {
                "type": "object",
                "properties": {
                    "container_id": {"type": "string", "description": "Unique identifier"}
                },
                "required": ["container_id"]
            }
        }
        # ... additional schemas
    ]
```

#### Chat Completion System
```python
def chat_completion(self, messages: List[Dict], functions: List[Dict] = None) -> Dict[str, Any]:
    request_params = {
        "model": self.model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    if functions:
        tools = [{"type": "function", "function": func} for func in functions]
        request_params["tools"] = tools
        request_params["tool_choice"] = "auto"
```

---

## Chatbot Orchestrator (`chatbot.py`)

### Purpose and Design

Main orchestrator that manages conversation flow, function execution, and state consistency across the entire AI interaction system.

### CanvasChatbot Class

#### Component Initialization
```python
def __init__(self):
    self.llm_client = None
    self.function_executor = None
    self.conversation_history = []
    self.auto_adjust_enabled = True
    self.overlap_prevention_enabled = False
    self._initialize_components()
```

#### Message Processing System
```python
async def process_user_message(self, user_message: str, conversation_id: str = None, 
                              allow_extended_iterations: bool = False) -> Dict[str, Any]:
```

**Processing Flow:**
1. **Message Preparation**: Add system message and conversation history
2. **Iterative Processing**: Handle multiple function calls (5-10 iterations)
3. **Function Execution**: Execute AI-requested functions
4. **Response Generation**: Provide user-facing responses
5. **History Management**: Update conversation context

#### Extended Iteration Support
```python
max_iterations = 10 if allow_extended_iterations else 5
continue_keywords = ['continue', 'yes', 'keep going', 'more iterations', 'proceed']
if any(keyword in user_message.lower() for keyword in continue_keywords):
    allow_extended_iterations = True
    max_iterations = 10
```

#### Function Call Handling
```python
# Handle both old and new OpenAI API formats
if hasattr(message, 'tool_calls') and message.tool_calls:
    for tool_call in message.tool_calls:
        if tool_call.type == 'function':
            function_calls_to_process.append({
                'id': tool_call.id,
                'name': tool_call.function.name,
                'arguments': tool_call.function.arguments
            })
```

---

## Function Executor (`function_executor.py`)

### Purpose and Architecture

Bridges LLM function calls to actual canvas operations, providing intelligent layout optimization, identifier validation, and comprehensive error handling.

### CanvasFunctionExecutor Class

#### Identifier Management System
```python
def _validate_identifier_uniqueness(self, proposed_id, element_type="element"):
    clean_id = proposed_id.strip().replace(' ', '_').lower()
    used_identifiers = self._get_all_used_identifiers()
    
    if clean_id in used_identifiers["all_identifiers"]:
        return {
            "is_valid": False,
            "error": f"{element_type.capitalize()} identifier '{clean_id}' is already in use",
            "suggestions": self._generate_alternative_identifiers(clean_id, used_identifiers["all_identifiers"])
        }
```

#### Layout Optimization System
```python
def _get_all_containers_for_optimization(self, new_container_id=None, exclude_container_id=None):
    containers_for_optimization = []
    
    for container in existing_containers:
        if exclude_container_id and container['id'] == exclude_container_id:
            continue
            
        containers_for_optimization.append({
            "id": container['id'],
            "status": "existing",
            "current_x": container['x'],
            "current_y": container['y'],
            "current_width": container['width'],
            "current_height": container['height']
        })
    
    if new_container_id:
        containers_for_optimization.append({
            "id": new_container_id,
            "status": "new"
        })
```

#### Function Execution Implementation
```python
async def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if function_name == "create_container":
        # Validate identifier uniqueness
        validation_result = self._validate_identifier_uniqueness(container_id, "container")
        
        # Calculate optimal layout
        optimization_result = self.canvas_bridge.calculate_optimal_layout(
            containers_for_optimization, canvas_width, canvas_height
        )
        
        # Apply optimized layout
        layout_application = await self._apply_optimized_layout(optimization_result, container_id)
```

---

## Canvas Bridge (`canvas_bridge.py`)

### Purpose and Design

Provides interface between backend logic and frontend canvas, managing state, WebSocket communication, and container operations with intelligent optimization.

### CanvasBridge Class

#### State Management
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

#### WebSocket Communication
```python
async def broadcast_to_frontend(self, message: Dict[str, Any]):
    if not self.websocket_connections:
        return
        
    message_json = json.dumps(message)
    disconnected = set()
    
    for websocket in self.websocket_connections:
        try:
            await websocket.send_text(message_json)
        except Exception:
            disconnected.add(websocket)
    
    for ws in disconnected:
        self.websocket_connections.discard(ws)
```

#### Container Operations
```python
async def create_container(self, container_id: str, x: int, y: int, width: int, height: int, 
                          auto_adjust: bool = True, avoid_overlap: bool = True) -> bool:
    # Input validation
    if container_id in self.canvas_state["containers"]:
        return False
    
    # Auto-adjust for canvas bounds
    if auto_adjust:
        if width > canvas_width:
            width = canvas_width
        if x + width > canvas_width:
            x = canvas_width - width
    
    # Overlap detection and resolution
    if avoid_overlap and existing_containers:
        new_x, new_y = self.find_non_overlapping_position(
            width, height, canvas_width, canvas_height, existing_containers, x, y
        )
        if new_x is not None:
            x, y = new_x, new_y
    
    # Create and broadcast
    self.canvas_state["containers"][container_id] = {
        "id": container_id, "x": x, "y": y, "width": width, "height": height,
        "created_at": datetime.now().isoformat()
    }
    
    await self.broadcast_to_frontend({
        "type": "canvas_command",
        "command": "create_container",
        "data": {"container_id": container_id, "x": x, "y": y, "width": width, "height": height}
    })
```

#### Intelligent Layout System
```python
def calculate_optimal_layout(self, containers, canvas_width, canvas_height):
    num_containers = len(containers)
    cols = math.ceil(math.sqrt(num_containers))
    rows = math.ceil(num_containers / cols)
    
    padding_x = max(10, int(canvas_width * 0.02))
    padding_y = max(10, int(canvas_height * 0.02))
    
    available_width = canvas_width - (padding_x * (cols + 1))
    available_height = canvas_height - (padding_y * (rows + 1))
    
    container_width = max(50, int(available_width / cols))
    container_height = max(50, int(available_height / rows))
    
    # Generate optimized positions
    optimized_containers = []
    for row in range(rows):
        for col in range(cols):
            if container_index >= num_containers:
                break
            x = padding_x + col * (container_width + padding_x)
            y = padding_y + row * (container_height + padding_y)
            # ... container creation logic
```

---

## Integration Patterns

### Service Communication Flow

1. **User Input** → WebSocket → **Chatbot**
2. **Chatbot** → **LLM Client** → OpenAI API
3. **LLM Response** → **Function Executor** → **Canvas Bridge**
4. **Canvas Bridge** → WebSocket → **Frontend Update**

### Error Handling Strategy

```python
try:
    result = await operation()
    return {"status": "success", "result": result}
except SpecificException as e:
    return {"status": "error", "result": f"Specific error: {str(e)}"}
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    return {"status": "error", "result": f"Internal error: {str(e)}"}
```

### State Consistency

- **Centralized State**: Canvas bridge maintains authoritative state
- **Real-time Sync**: WebSocket broadcasts ensure client consistency
- **Validation**: Multiple validation layers prevent invalid states
- **Recovery**: Automatic cleanup and error recovery mechanisms

This documentation provides comprehensive coverage of the core services' implementation, enabling developers to understand and extend the intelligent canvas management system. 