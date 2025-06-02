# AI Engine Module

## 🎯 Purpose

The AI Engine module handles all LLM integration, conversation management, and the orchestration of function calling workflows. It provides a clean interface between the user's natural language requests and the function registry.

## 📁 Structure

```
ai_engine/
├── README.md                    # This file
├── __init__.py                  # Module initialization
├── llm_client.py                # OpenAI API integration
├── conversation_manager.py      # Chat history and context management
├── function_caller.py           # LLM function calling workflow
└── ai_orchestrator.py           # Main AI orchestration logic
```

## 🔧 Core Components

### LLM Client
- **Purpose**: Direct integration with OpenAI API
- **Features**: 
  - API key management
  - Model selection and configuration
  - Error handling and retries
  - Token usage tracking

### Conversation Manager
- **Purpose**: Manage chat history and context
- **Features**:
  - Message history storage
  - Context window management
  - Conversation state persistence
  - Memory optimization

### Function Caller
- **Purpose**: Orchestrate the function calling workflow
- **Features**:
  - Function call detection
  - Argument parsing and validation
  - Result processing
  - Multi-step function calling

### AI Orchestrator
- **Purpose**: Main coordination between all components
- **Features**:
  - Request routing
  - Response generation
  - Error handling
  - Performance monitoring

## 🚀 Usage

```python
from core.ai_engine import AIOrchestrator
from core.function_registry import AVAILABLE_FUNCTIONS, FUNCTION_SCHEMAS

# Create AI orchestrator
ai = AIOrchestrator(
    functions=AVAILABLE_FUNCTIONS,
    schemas=FUNCTION_SCHEMAS
)

# Process user request
response = ai.process_request(
    user_message="Load the sales dataset and create a line chart",
    conversation_id="user_123"
)

# Get response
print(response["message"])
```

## 🔗 Integration

The AI Engine integrates with:
- **Function Registry**: For available functions and schemas
- **Data Manager**: For data state management
- **UI Adapters**: For response formatting
- **Configuration**: For API keys and settings

## 📝 Development Guidelines

1. **Framework Independence**: No UI framework dependencies
2. **Error Handling**: Comprehensive error catching and user-friendly messages
3. **Performance**: Efficient token usage and response times
4. **Security**: Secure API key handling
5. **Logging**: Detailed logging for debugging and monitoring

## 🧪 Testing

```bash
python -m pytest core/ai_engine/tests/
```

## 🔧 Configuration

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: gpt-3.5-turbo)
- `MAX_TOKENS`: Maximum tokens per response (default: 1000) 