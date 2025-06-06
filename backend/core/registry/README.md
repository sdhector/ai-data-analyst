# Registry - Tool Registration and Schema Management

This directory contains the tool registration system and schema management functionality. The registry provides dynamic tool discovery, OpenAI function schema generation, and metadata management for all AI-accessible operations.

## Purpose

The registry serves as the central management system for tools:
- **Dynamic Tool Discovery**: Automatically discover and register available tools
- **Schema Generation**: Generate OpenAI function schemas for AI integration
- **Metadata Management**: Store and manage tool metadata and documentation
- **Version Control**: Handle tool versioning and compatibility
- **Access Control**: Manage which tools are accessible in different contexts

## Design Philosophy

### 1. **Dynamic Discovery**
- Automatically scan and register tools at runtime
- No manual registration required for new tools
- Support for plugin-like tool additions
- Hot-reloading of tool definitions

### 2. **Schema-Driven**
- Generate OpenAI function schemas from tool metadata
- Validate tool implementations against schemas
- Ensure consistency across all tool interfaces
- Support for schema evolution and migration

### 3. **Metadata Rich**
- Comprehensive tool documentation and examples
- Usage statistics and performance metrics
- Dependency tracking and compatibility information
- Categorization and tagging for organization

### 4. **Flexible Configuration**
- Environment-specific tool availability
- Role-based access control for tools
- Configurable tool parameters and defaults
- Runtime tool enabling/disabling

## Planned Modules

### `tool_registry.py` (To Be Implemented)
Core tool registration functionality:
- `ToolRegistry` - Main registry class for tool management
- `register_tool()` - Register individual tools with metadata
- `discover_tools()` - Automatically discover tools in modules
- `get_available_tools()` - Get tools available for current context
- `get_tool_metadata()` - Retrieve detailed tool information

### `schema_generator.py` (To Be Implemented)
OpenAI function schema generation:
- `generate_function_schema()` - Create OpenAI function schema from tool
- `validate_tool_schema()` - Validate tool implementation against schema
- `update_schema_version()` - Handle schema versioning and migration
- `export_schemas()` - Export schemas for external use
- `import_schemas()` - Import external schema definitions

### `metadata_manager.py` (To Be Implemented)
Tool metadata and documentation management:
- `ToolMetadata` - Data class for tool metadata
- `store_metadata()` - Store tool metadata and documentation
- `get_tool_documentation()` - Retrieve tool documentation
- `update_usage_statistics()` - Track tool usage and performance
- `generate_tool_catalog()` - Create comprehensive tool catalog

### `access_control.py` (To Be Implemented)
Tool access control and permissions:
- `check_tool_access()` - Verify tool access permissions
- `get_user_tools()` - Get tools available to specific user/role
- `configure_tool_permissions()` - Set tool access permissions
- `audit_tool_usage()` - Log and audit tool access
- `manage_tool_quotas()` - Handle usage quotas and rate limiting

### `version_manager.py` (To Be Implemented)
Tool versioning and compatibility:
- `ToolVersion` - Version information data class
- `register_tool_version()` - Register new tool versions
- `check_compatibility()` - Check tool version compatibility
- `migrate_tool_usage()` - Handle tool version migrations
- `deprecate_tool_version()` - Manage tool deprecation lifecycle

## Tool Registration Process

### Automatic Discovery
```python
from core_new.registry.tool_registry import ToolRegistry

# Registry automatically discovers tools
registry = ToolRegistry()
registry.discover_tools("core_new.tools")

# Tools are automatically registered with metadata
available_tools = registry.get_available_tools()
```

### Manual Registration
```python
from core_new.registry.tool_registry import register_tool
from core_new.registry.metadata_manager import ToolMetadata

# Manual tool registration with metadata
metadata = ToolMetadata(
    name="create_optimized_container",
    description="Create a container with intelligent layout optimization",
    category="container_operations",
    version="1.0.0",
    parameters={
        "container_id": {
            "type": "string",
            "required": True,
            "description": "Unique identifier for the container"
        }
    },
    examples=[
        {
            "description": "Create a simple container",
            "parameters": {"container_id": "chart1"},
            "expected_result": "Container created successfully"
        }
    ]
)

register_tool(create_optimized_container_tool, metadata)
```

## Schema Generation

### OpenAI Function Schema
```python
from core_new.registry.schema_generator import generate_function_schema

# Generate OpenAI function schema
schema = generate_function_schema("create_optimized_container")

# Result:
{
    "name": "create_optimized_container",
    "description": "Create a container with intelligent layout optimization",
    "parameters": {
        "type": "object",
        "properties": {
            "container_id": {
                "type": "string",
                "description": "Unique identifier for the container"
            },
            "preferences": {
                "type": "object",
                "description": "Optional positioning and sizing preferences",
                "properties": {
                    "position": {"type": "string", "enum": ["auto", "top-left", "center"]},
                    "size": {"type": "string", "enum": ["auto", "small", "medium", "large"]}
                }
            }
        },
        "required": ["container_id"]
    }
}
```

### Schema Validation
```python
from core_new.registry.schema_generator import validate_tool_schema

# Validate tool implementation against schema
validation_result = validate_tool_schema("create_optimized_container")
if not validation_result.is_valid:
    print(f"Schema validation failed: {validation_result.errors}")
```

## Metadata Management

### Tool Metadata Structure
```python
@dataclass
class ToolMetadata:
    name: str
    description: str
    category: str
    version: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]
    examples: List[Dict[str, Any]]
    tags: List[str]
    dependencies: List[str]
    performance_metrics: Dict[str, Any]
    access_level: str
    deprecation_info: Optional[Dict[str, Any]]
    
    # Usage statistics
    usage_count: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 100.0
    last_used: Optional[datetime] = None
```

### Documentation Generation
```python
from core_new.registry.metadata_manager import generate_tool_catalog

# Generate comprehensive tool documentation
catalog = generate_tool_catalog()
# Creates markdown documentation with examples, parameters, etc.
```

## Access Control

### Role-Based Access
```python
from core_new.registry.access_control import check_tool_access

# Check if user can access tool
can_access = check_tool_access(
    tool_name="create_optimized_container",
    user_role="standard_user",
    context={"session_id": "...", "permissions": ["canvas_modify"]}
)
```

### Tool Filtering
```python
# Get tools available to specific user
user_tools = registry.get_user_tools(
    user_role="standard_user",
    context={"permissions": ["canvas_read", "canvas_modify"]}
)
```

## Integration with AI System

### LLM Client Integration
```python
from core_new.registry import get_ai_function_schemas

# Get all function schemas for AI
schemas = get_ai_function_schemas(
    user_context={"role": "standard_user"},
    categories=["container_operations", "canvas_operations"]
)

# Use with LLM client
llm_response = llm_client.chat_completion(
    messages=messages,
    functions=schemas
)
```

### Tool Execution
```python
from core_new.registry import execute_tool

# Execute tool by name
result = await execute_tool(
    tool_name="create_optimized_container",
    parameters={"container_id": "chart1"},
    context={"user_id": "...", "session_id": "..."}
)
```

## Configuration

### Registry Configuration
```python
REGISTRY_CONFIG = {
    "discovery": {
        "auto_discover": True,
        "scan_paths": ["core_new.tools"],
        "reload_interval": 300  # seconds
    },
    "schema": {
        "validate_on_registration": True,
        "generate_examples": True,
        "include_performance_hints": True
    },
    "access_control": {
        "enable_rbac": True,
        "default_access_level": "standard",
        "audit_tool_usage": True
    },
    "performance": {
        "track_usage_statistics": True,
        "cache_schemas": True,
        "enable_metrics": True
    }
}
```

## Testing Strategy

Registry components require thorough testing:
- **Discovery Testing**: Verify automatic tool discovery
- **Schema Testing**: Validate generated schemas
- **Access Control Testing**: Test permission enforcement
- **Performance Testing**: Measure registry overhead
- **Integration Testing**: Test with actual AI interactions

## Implementation Guidelines

### ✅ **DO:**
- Automatically discover tools when possible
- Generate comprehensive schemas with examples
- Track usage statistics and performance metrics
- Implement proper access control
- Provide rich metadata and documentation

### ❌ **DON'T:**
- Require manual registration for every tool
- Generate incomplete or invalid schemas
- Ignore access control requirements
- Skip performance monitoring
- Expose internal implementation details

## Status

🚧 **Currently**: Placeholder directory with basic structure
📋 **Next Phase**: Implement core registry and schema generation
🎯 **Goal**: Provide dynamic, intelligent tool management for AI integration

This layer is crucial for maintaining a clean, discoverable, and well-documented interface between the AI system and the available tools. 