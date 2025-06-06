# AI Data Analyst v0.1 - Backend

## 📁 Directory Structure

```
backend/
├── api/                    # API layer and communication
│   ├── routes/            # HTTP route handlers
│   └── websocket/         # WebSocket connection management
├── config/                # Configuration files and settings
├── core/                  # Core business logic
│   ├── ai_engine/         # AI/LLM integration and processing
│   └── function_registry/ # Function definitions and management
├── services/              # Business logic services
├── tests/                 # Backend unit and integration tests
└── utils/                 # Utility functions and helpers
```

## 🎯 Purpose

This backend provides the server-side functionality for the AI Data Analyst system, including:

- **AI Chat Interface**: Natural language processing and response generation
- **Canvas Control**: Function calling for canvas manipulation
- **Real-time Communication**: WebSocket support for live updates
- **Function Registry**: Organized function definitions and execution

## 📋 Key Components

### **Core (`/core/`)**
- **AI Engine**: LLM integration, conversation management, function calling
- **Function Registry**: Three-tier function classification (Tool, Helper, Guardrail)

### **API (`/api/`)**
- **Routes**: HTTP endpoints for REST API
- **WebSocket**: Real-time bidirectional communication

### **Services (`/services/`)**
- Business logic layer
- Data processing and validation
- External service integrations

### **Configuration (`/config/`)**
- Environment settings
- API keys and credentials
- System configuration

### **Utils (`/utils/`)**
- Helper functions
- Common utilities
- Shared constants

### **Tests (`/tests/`)**
- Unit tests
- Integration tests
- API endpoint tests

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   cd v0.1/backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp config/example.env config/.env
   # Edit config/.env with your settings
   ```

3. **Run Server**
   ```bash
   python main.py
   ```

## 🔧 Development

- **Main Entry Point**: `main.py`
- **Configuration**: `config/settings.py`
- **API Routes**: `api/routes/`
- **WebSocket Handler**: `api/websocket/`
- **AI Engine**: `core/ai_engine/`
- **Functions**: `core/function_registry/`

## 📡 API Endpoints

### **HTTP Routes**
- `GET /health` - Health check
- `POST /api/chat` - Send chat message
- `GET /api/canvas/state` - Get canvas state
- `POST /api/canvas/action` - Execute canvas action

### **WebSocket**
- `/ws` - Real-time communication
- Message types: `chat`, `canvas_update`, `function_call`

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/api/
python -m pytest tests/core/
```

## 📚 Related Documentation

- [Infrastructure Documentation](../INFRASTRUCTURE_DOCUMENTATION.md)
- [Reproduction Template](../REPRODUCTION_TEMPLATE.md)
- [Frontend Documentation](../frontend/README.md) 