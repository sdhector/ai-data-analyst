# Configuration Module - Detailed Documentation

## Overview

The configuration module (`backend/config/`) provides centralized, type-safe configuration management for the AI Data Analyst application. Built on Pydantic's BaseSettings, it offers automatic environment variable loading, type validation, and hierarchical configuration resolution.

### Design Philosophy

The configuration system follows these principles:
- **Type Safety**: All configuration values are type-checked at runtime
- **Environment Flexibility**: Support for multiple environment sources
- **Default Values**: Sensible defaults for development and production
- **Validation**: Automatic validation of configuration values
- **Documentation**: Self-documenting configuration through type hints

---

## Settings Module (`settings.py`)

### Module Overview

The `settings.py` module implements a comprehensive configuration system using Pydantic BaseSettings. It manages all application configuration including server settings, AI integration, canvas behavior, and system parameters.

### Import Structure and Dependencies

```python
import os
from typing import Optional
from pydantic import BaseSettings
```

**Key Dependencies:**
- **Pydantic BaseSettings**: Type-safe configuration management
- **OS Module**: Environment variable access
- **Typing**: Type hints for configuration validation

### Configuration Architecture

#### Settings Class Definition

```python
class Settings(BaseSettings):
    """Application settings"""
    
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
    
    # Chatbot settings
    max_conversation_history: int = 20
    max_function_calls_per_turn: int = 5
    function_call_timeout: int = 30
    
    # WebSocket settings
    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10
    
    # CORS settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    
    # Logging settings
    log_level: str = "info"
    
    class Config:
        env_file = ".env"
        env_prefix = "AI_DATA_ANALYST_"
```

### Configuration Categories

#### Server Configuration

**Host Settings**
```python
host: str = "127.0.0.1"
```
- **Purpose**: Server bind address for HTTP and WebSocket connections
- **Default**: `"127.0.0.1"` (localhost only)
- **Production**: Set to `"0.0.0.0"` for external access
- **Environment Variable**: `AI_DATA_ANALYST_HOST`

**Port Configuration**
```python
port: int = 8000
```
- **Purpose**: Server port for all HTTP/WebSocket traffic
- **Default**: `8000` (FastAPI standard)
- **Range**: 1024-65535 (avoid privileged ports)
- **Environment Variable**: `AI_DATA_ANALYST_PORT`

**Development Settings**
```python
reload: bool = False
```
- **Purpose**: Enable automatic code reloading during development
- **Default**: `False` (production-safe)
- **Development**: Set to `True` for auto-reload
- **Environment Variable**: `AI_DATA_ANALYST_RELOAD`

**Usage Example:**
```bash
# Development
export AI_DATA_ANALYST_HOST="0.0.0.0"
export AI_DATA_ANALYST_PORT="3000"
export AI_DATA_ANALYST_RELOAD="true"

# Production
export AI_DATA_ANALYST_HOST="0.0.0.0"
export AI_DATA_ANALYST_PORT="8000"
export AI_DATA_ANALYST_RELOAD="false"
```

#### AI Integration Settings

**OpenAI API Configuration**
```python
openai_api_key: Optional[str] = None
openai_model: str = "gpt-4o-mini"
```

**API Key Management:**
- **Type**: `Optional[str]` - Can be None during initialization
- **Sources**: Environment variable, `.env` file
- **Security**: Never hardcoded in source code
- **Validation**: Required for AI functionality
- **Environment Variable**: `AI_DATA_ANALYST_OPENAI_API_KEY` or `OPENAI_API_KEY`

**Model Selection:**
- **Default**: `"gpt-4o-mini"` - Cost-effective model for canvas operations
- **Alternatives**: `"gpt-4"`, `"gpt-3.5-turbo"`, `"gpt-4-turbo"`
- **Considerations**: Balance between capability and cost
- **Environment Variable**: `AI_DATA_ANALYST_OPENAI_MODEL`

**Configuration Examples:**
```bash
# Standard configuration
export OPENAI_API_KEY="sk-..."
export AI_DATA_ANALYST_OPENAI_MODEL="gpt-4o-mini"

# High-performance configuration
export OPENAI_API_KEY="sk-..."
export AI_DATA_ANALYST_OPENAI_MODEL="gpt-4"

# Development with different key
export AI_DATA_ANALYST_OPENAI_API_KEY="sk-dev-..."
export AI_DATA_ANALYST_OPENAI_MODEL="gpt-3.5-turbo"
```

#### Canvas Behavior Settings

**Default Canvas Dimensions**
```python
default_canvas_width: int = 800
default_canvas_height: int = 600
```

**Width Configuration:**
- **Purpose**: Initial canvas width in pixels
- **Default**: `800` pixels (standard web width)
- **Range**: 200-5000 pixels (enforced by application)
- **Environment Variable**: `AI_DATA_ANALYST_DEFAULT_CANVAS_WIDTH`

**Height Configuration:**
- **Purpose**: Initial canvas height in pixels
- **Default**: `600` pixels (4:3 aspect ratio)
- **Range**: 200-5000 pixels (enforced by application)
- **Environment Variable**: `AI_DATA_ANALYST_DEFAULT_CANVAS_HEIGHT`

**Usage Scenarios:**
```bash
# Standard web display
export AI_DATA_ANALYST_DEFAULT_CANVAS_WIDTH="800"
export AI_DATA_ANALYST_DEFAULT_CANVAS_HEIGHT="600"

# Widescreen display
export AI_DATA_ANALYST_DEFAULT_CANVAS_WIDTH="1200"
export AI_DATA_ANALYST_DEFAULT_CANVAS_HEIGHT="800"

# Mobile-optimized
export AI_DATA_ANALYST_DEFAULT_CANVAS_WIDTH="400"
export AI_DATA_ANALYST_DEFAULT_CANVAS_HEIGHT="600"
```

#### Chatbot Configuration

**Conversation Management**
```python
max_conversation_history: int = 20
max_function_calls_per_turn: int = 5
function_call_timeout: int = 30
```

**History Limits:**
- **Purpose**: Maximum conversation messages to retain in memory
- **Default**: `20` messages (10 user + 10 assistant)
- **Memory Impact**: Higher values increase memory usage
- **Performance**: Affects AI context processing time
- **Environment Variable**: `AI_DATA_ANALYST_MAX_CONVERSATION_HISTORY`

**Function Call Limits:**
- **Purpose**: Maximum AI function calls per user message
- **Default**: `5` calls (prevents infinite loops)
- **Safety**: Protects against runaway AI operations
- **Flexibility**: Can be increased for complex operations
- **Environment Variable**: `AI_DATA_ANALYST_MAX_FUNCTION_CALLS_PER_TURN`

**Timeout Configuration:**
- **Purpose**: Maximum time for function execution in seconds
- **Default**: `30` seconds (generous for canvas operations)
- **Network**: Accounts for API latency and processing time
- **User Experience**: Prevents hanging operations
- **Environment Variable**: `AI_DATA_ANALYST_FUNCTION_CALL_TIMEOUT`

**Performance Tuning Examples:**
```bash
# High-performance environment
export AI_DATA_ANALYST_MAX_CONVERSATION_HISTORY="50"
export AI_DATA_ANALYST_MAX_FUNCTION_CALLS_PER_TURN="10"
export AI_DATA_ANALYST_FUNCTION_CALL_TIMEOUT="60"

# Resource-constrained environment
export AI_DATA_ANALYST_MAX_CONVERSATION_HISTORY="10"
export AI_DATA_ANALYST_MAX_FUNCTION_CALLS_PER_TURN="3"
export AI_DATA_ANALYST_FUNCTION_CALL_TIMEOUT="15"

# Development environment
export AI_DATA_ANALYST_MAX_CONVERSATION_HISTORY="5"
export AI_DATA_ANALYST_MAX_FUNCTION_CALLS_PER_TURN="2"
export AI_DATA_ANALYST_FUNCTION_CALL_TIMEOUT="10"
```

#### WebSocket Configuration

**Connection Management**
```python
websocket_ping_interval: int = 30
websocket_ping_timeout: int = 10
```

**Ping Interval:**
- **Purpose**: Frequency of keepalive ping messages in seconds
- **Default**: `30` seconds (balance between responsiveness and overhead)
- **Network**: Shorter intervals for unstable connections
- **Performance**: Longer intervals reduce server load
- **Environment Variable**: `AI_DATA_ANALYST_WEBSOCKET_PING_INTERVAL`

**Ping Timeout:**
- **Purpose**: Maximum time to wait for pong response in seconds
- **Default**: `10` seconds (reasonable for web connections)
- **Detection**: Time to detect dead connections
- **Cleanup**: Affects connection cleanup speed
- **Environment Variable**: `AI_DATA_ANALYST_WEBSOCKET_PING_TIMEOUT`

**Network Optimization Examples:**
```bash
# Stable network (reduce overhead)
export AI_DATA_ANALYST_WEBSOCKET_PING_INTERVAL="60"
export AI_DATA_ANALYST_WEBSOCKET_PING_TIMEOUT="20"

# Unstable network (quick detection)
export AI_DATA_ANALYST_WEBSOCKET_PING_INTERVAL="15"
export AI_DATA_ANALYST_WEBSOCKET_PING_TIMEOUT="5"

# Mobile network (balanced)
export AI_DATA_ANALYST_WEBSOCKET_PING_INTERVAL="45"
export AI_DATA_ANALYST_WEBSOCKET_PING_TIMEOUT="15"
```

#### CORS Configuration

**Cross-Origin Resource Sharing**
```python
cors_origins: list = ["*"]
cors_allow_credentials: bool = True
```

**Origins Configuration:**
- **Purpose**: Allowed origins for cross-origin requests
- **Default**: `["*"]` (allow all origins - development only)
- **Security**: Restrict to specific domains in production
- **Format**: List of URLs or wildcard patterns
- **Environment Variable**: `AI_DATA_ANALYST_CORS_ORIGINS` (comma-separated)

**Credentials Configuration:**
- **Purpose**: Allow credentials in cross-origin requests
- **Default**: `True` (enable cookie/auth header sharing)
- **Security**: Required for authenticated requests
- **Compatibility**: Needed for some frontend frameworks
- **Environment Variable**: `AI_DATA_ANALYST_CORS_ALLOW_CREDENTIALS`

**Security Examples:**
```bash
# Development (permissive)
export AI_DATA_ANALYST_CORS_ORIGINS="*"
export AI_DATA_ANALYST_CORS_ALLOW_CREDENTIALS="true"

# Production (restrictive)
export AI_DATA_ANALYST_CORS_ORIGINS="https://myapp.com,https://www.myapp.com"
export AI_DATA_ANALYST_CORS_ALLOW_CREDENTIALS="true"

# API-only (no credentials)
export AI_DATA_ANALYST_CORS_ORIGINS="https://api.myapp.com"
export AI_DATA_ANALYST_CORS_ALLOW_CREDENTIALS="false"
```

#### Logging Configuration

**Log Level Management**
```python
log_level: str = "info"
```

**Log Levels:**
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages (default)
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors requiring immediate attention

**Environment Variable**: `AI_DATA_ANALYST_LOG_LEVEL`

**Logging Examples:**
```bash
# Development (verbose)
export AI_DATA_ANALYST_LOG_LEVEL="debug"

# Production (standard)
export AI_DATA_ANALYST_LOG_LEVEL="info"

# Production (minimal)
export AI_DATA_ANALYST_LOG_LEVEL="warning"

# Troubleshooting
export AI_DATA_ANALYST_LOG_LEVEL="debug"
```

### Environment Variable Integration

#### Configuration Class

```python
class Config:
    env_file = ".env"
    env_prefix = "AI_DATA_ANALYST_"
```

**Environment File:**
- **Purpose**: Load configuration from `.env` file
- **Location**: Root directory of the project
- **Format**: `KEY=value` pairs, one per line
- **Priority**: Lower than direct environment variables

**Environment Prefix:**
- **Purpose**: Namespace configuration variables
- **Prefix**: `AI_DATA_ANALYST_` for all application settings
- **Conflict Resolution**: Prevents conflicts with system variables
- **Organization**: Groups related configuration together

#### Variable Resolution Priority

**Resolution Order (highest to lowest priority):**
1. **Direct Environment Variables**: `export VARIABLE=value`
2. **Prefixed Environment Variables**: `export AI_DATA_ANALYST_VARIABLE=value`
3. **`.env` File Variables**: `VARIABLE=value` in `.env` file
4. **Default Values**: Values defined in Settings class

**Example Resolution:**
```bash
# Environment variables (highest priority)
export AI_DATA_ANALYST_PORT="3000"
export OPENAI_API_KEY="sk-env-key"

# .env file (lower priority)
# AI_DATA_ANALYST_PORT=8000
# OPENAI_API_KEY=sk-file-key

# Result: port=3000, api_key="sk-env-key"
```

#### Environment File Format

**`.env` File Example:**
```bash
# Server Configuration
AI_DATA_ANALYST_HOST=0.0.0.0
AI_DATA_ANALYST_PORT=8000
AI_DATA_ANALYST_RELOAD=false

# AI Configuration
OPENAI_API_KEY=sk-proj-your-api-key-here
AI_DATA_ANALYST_OPENAI_MODEL=gpt-4o-mini

# Canvas Configuration
AI_DATA_ANALYST_DEFAULT_CANVAS_WIDTH=1200
AI_DATA_ANALYST_DEFAULT_CANVAS_HEIGHT=800

# Performance Configuration
AI_DATA_ANALYST_MAX_CONVERSATION_HISTORY=30
AI_DATA_ANALYST_MAX_FUNCTION_CALLS_PER_TURN=8
AI_DATA_ANALYST_FUNCTION_CALL_TIMEOUT=45

# WebSocket Configuration
AI_DATA_ANALYST_WEBSOCKET_PING_INTERVAL=60
AI_DATA_ANALYST_WEBSOCKET_PING_TIMEOUT=20

# Security Configuration
AI_DATA_ANALYST_CORS_ORIGINS=https://myapp.com,https://www.myapp.com
AI_DATA_ANALYST_CORS_ALLOW_CREDENTIALS=true

# Logging Configuration
AI_DATA_ANALYST_LOG_LEVEL=info
```

### Type Safety and Validation

#### Pydantic Integration

**Automatic Type Conversion:**
```python
# String to integer conversion
port: int = 8000  # "8000" -> 8000

# String to boolean conversion
reload: bool = False  # "true" -> True, "false" -> False

# String to list conversion
cors_origins: list = ["*"]  # "a,b,c" -> ["a", "b", "c"]
```

**Validation Features:**
- **Type Checking**: Runtime validation of all configuration values
- **Range Validation**: Automatic validation of numeric ranges
- **Format Validation**: String format validation (URLs, etc.)
- **Required Fields**: Validation of required configuration

**Error Handling:**
```python
# Invalid configuration example
try:
    settings = Settings()
except ValidationError as e:
    print(f"Configuration error: {e}")
    # Handle configuration errors gracefully
```

#### Custom Validation

**Range Validation Example:**
```python
from pydantic import validator

class Settings(BaseSettings):
    port: int = 8000
    
    @validator('port')
    def validate_port(cls, v):
        if not 1024 <= v <= 65535:
            raise ValueError('Port must be between 1024 and 65535')
        return v
```

**URL Validation Example:**
```python
from pydantic import validator, HttpUrl

class Settings(BaseSettings):
    cors_origins: List[str] = ["*"]
    
    @validator('cors_origins', pre=True)
    def validate_origins(cls, v):
        if isinstance(v, str):
            return v.split(',')
        return v
```

### Global Settings Instance

#### Singleton Pattern

```python
# Global settings instance
settings = Settings()
```

**Usage Throughout Application:**
```python
from config.settings import settings

# Access configuration values
print(f"Server running on {settings.host}:{settings.port}")
print(f"Using OpenAI model: {settings.openai_model}")
print(f"Canvas size: {settings.default_canvas_width}x{settings.default_canvas_height}")
```

**Benefits:**
- **Centralized Access**: Single point of configuration access
- **Type Safety**: IDE autocompletion and type checking
- **Validation**: Automatic validation on application startup
- **Performance**: Configuration loaded once at startup

#### Configuration Access Patterns

**Direct Access:**
```python
from config.settings import settings

def create_server():
    return FastAPI(
        title="AI Data Analyst",
        host=settings.host,
        port=settings.port
    )
```

**Dependency Injection:**
```python
from fastapi import Depends
from config.settings import Settings, settings

def get_settings() -> Settings:
    return settings

@app.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    return {
        "canvas_size": {
            "width": settings.default_canvas_width,
            "height": settings.default_canvas_height
        }
    }
```

### Development vs Production Configuration

#### Development Configuration

**Characteristics:**
- **Permissive CORS**: Allow all origins for easy testing
- **Auto-reload**: Enable code reloading for development
- **Verbose Logging**: Debug-level logging for troubleshooting
- **Local Binding**: Bind to localhost for security

**Development `.env`:**
```bash
AI_DATA_ANALYST_HOST=127.0.0.1
AI_DATA_ANALYST_PORT=8000
AI_DATA_ANALYST_RELOAD=true
AI_DATA_ANALYST_CORS_ORIGINS=*
AI_DATA_ANALYST_LOG_LEVEL=debug
AI_DATA_ANALYST_MAX_CONVERSATION_HISTORY=5
```

#### Production Configuration

**Characteristics:**
- **Restrictive CORS**: Specific allowed origins only
- **No Auto-reload**: Stable production deployment
- **Minimal Logging**: Info-level logging for performance
- **External Binding**: Allow external connections

**Production Environment:**
```bash
AI_DATA_ANALYST_HOST=0.0.0.0
AI_DATA_ANALYST_PORT=8000
AI_DATA_ANALYST_RELOAD=false
AI_DATA_ANALYST_CORS_ORIGINS=https://myapp.com
AI_DATA_ANALYST_LOG_LEVEL=info
AI_DATA_ANALYST_MAX_CONVERSATION_HISTORY=20
```

#### Environment-Specific Overrides

**Docker Configuration:**
```dockerfile
ENV AI_DATA_ANALYST_HOST=0.0.0.0
ENV AI_DATA_ANALYST_PORT=8000
ENV AI_DATA_ANALYST_LOG_LEVEL=info
```

**Kubernetes Configuration:**
```yaml
env:
  - name: AI_DATA_ANALYST_HOST
    value: "0.0.0.0"
  - name: AI_DATA_ANALYST_PORT
    value: "8000"
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: openai-secret
        key: api-key
```

### Configuration Testing

#### Unit Testing Configuration

**Test Configuration:**
```python
import pytest
from config.settings import Settings

def test_default_configuration():
    settings = Settings()
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.openai_model == "gpt-4o-mini"

def test_environment_override():
    import os
    os.environ["AI_DATA_ANALYST_PORT"] = "3000"
    settings = Settings()
    assert settings.port == 3000
    del os.environ["AI_DATA_ANALYST_PORT"]
```

**Configuration Validation Testing:**
```python
def test_invalid_port():
    import os
    os.environ["AI_DATA_ANALYST_PORT"] = "99999"
    with pytest.raises(ValidationError):
        Settings()
    del os.environ["AI_DATA_ANALYST_PORT"]
```

#### Integration Testing

**Configuration Loading Test:**
```python
def test_env_file_loading():
    # Create temporary .env file
    with open(".env.test", "w") as f:
        f.write("AI_DATA_ANALYST_PORT=9000\n")
    
    # Test configuration loading
    settings = Settings(_env_file=".env.test")
    assert settings.port == 9000
    
    # Cleanup
    os.remove(".env.test")
```

### Performance Considerations

#### Configuration Loading

**Startup Performance:**
- **Single Load**: Configuration loaded once at application startup
- **Validation Cost**: Type validation performed once during initialization
- **Memory Usage**: Configuration stored in memory for fast access

**Runtime Performance:**
- **Direct Access**: O(1) attribute access for configuration values
- **No I/O**: No file system access after initial load
- **Type Safety**: No runtime type conversion overhead

#### Memory Optimization

**Configuration Size:**
- **Minimal Memory**: Simple data types with minimal memory footprint
- **No Caching**: Configuration values accessed directly
- **Garbage Collection**: Automatic cleanup of unused configuration

### Security Considerations

#### Sensitive Data Handling

**API Key Security:**
- **Environment Variables**: Never store API keys in source code
- **File Permissions**: Secure `.env` file permissions (600)
- **Version Control**: Add `.env` to `.gitignore`
- **Production Secrets**: Use secure secret management systems

**Configuration Validation:**
- **Input Sanitization**: Validate all configuration inputs
- **Range Checking**: Ensure numeric values are within safe ranges
- **Format Validation**: Validate URLs, file paths, and other formats

#### Best Practices

**Development Security:**
```bash
# Secure .env file permissions
chmod 600 .env

# Use different keys for development
OPENAI_API_KEY=sk-dev-your-development-key
```

**Production Security:**
```bash
# Use environment variables instead of files
export OPENAI_API_KEY="$(cat /run/secrets/openai_key)"

# Restrict CORS origins
export AI_DATA_ANALYST_CORS_ORIGINS="https://myapp.com"
```

This detailed documentation provides comprehensive coverage of the configuration system's implementation, usage patterns, and best practices for secure and efficient configuration management. 