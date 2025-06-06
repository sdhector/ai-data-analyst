# Tools - High-Level LLM-Accessible Operations

This directory contains high-level operations that are exposed to the AI/LLM. Tools orchestrate primitives, utilities, and guardrails to provide intelligent, safe, and user-friendly interfaces for complex operations.

## Purpose

Tools serve as the AI interface layer:
- **AI-Friendly Interfaces**: Natural language compatible operations
- **Workflow Orchestration**: Combine multiple primitives into complex workflows
- **Intelligent Automation**: Automatic optimization and decision-making
- **Rich Response Formatting**: Detailed, informative responses for AI consumption
- **Error Recovery**: Graceful handling of failures with alternative approaches

## Design Philosophy

### 1. **AI-First Design**
- Natural language parameter interpretation
- Intelligent defaults and assumptions
- Rich, descriptive response formatting
- Context-aware operation behavior

### 2. **Comprehensive Orchestration**
- Coordinate guardrails, utilities, and primitives
- Handle complex multi-step workflows
- Provide transaction-like operation guarantees
- Implement rollback mechanisms for failures

### 3. **User Experience Focus**
- Minimize required parameters through intelligent defaults
- Provide helpful error messages and suggestions
- Offer alternative approaches when operations fail
- Include progress feedback for long-running operations

### 4. **Extensibility**
- Easy to add new tools without modifying existing code
- Consistent patterns across all tool implementations
- Plugin-like architecture for custom operations
- Version compatibility and migration support

## Planned Modules

### `container_tools.py` (To Be Implemented)
High-level container operations:
- `create_optimized_container()` - Intelligent container creation with layout optimization
- `delete_container_safely()` - Safe deletion with confirmation and cleanup
- `modify_container_intelligently()` - Smart modification with conflict resolution
- `batch_create_containers()` - Create multiple containers with optimal layout
- `reorganize_containers()` - Intelligent container reorganization

### `canvas_tools.py` (To Be Implemented)
High-level canvas operations:
- `optimize_canvas_layout()` - Comprehensive layout optimization
- `resize_canvas_intelligently()` - Smart resizing with container adjustment
- `clear_canvas_safely()` - Safe clearing with confirmation and backup
- `take_annotated_screenshot()` - Screenshot with metadata and annotations
- `analyze_canvas_efficiency()` - Canvas utilization analysis and recommendations

### `state_tools.py` (To Be Implemented)
High-level state and analysis operations:
- `get_canvas_summary()` - Comprehensive canvas state summary
- `analyze_container_distribution()` - Container layout analysis
- `generate_optimization_report()` - Layout optimization recommendations
- `check_canvas_health()` - System health and performance analysis
- `export_canvas_configuration()` - Configuration export for backup/restore

### `workflow_tools.py` (To Be Implemented)
Complex workflow operations:
- `create_dashboard_layout()` - Create predefined dashboard layouts
- `implement_design_pattern()` - Apply common design patterns
- `migrate_canvas_version()` - Version migration and compatibility
- `batch_operation_manager()` - Manage complex batch operations
- `undo_last_operation()` - Operation history and undo functionality

### `ai_assistance_tools.py` (To Be Implemented)
AI-specific helper operations:
- `suggest_next_actions()` - Intelligent action suggestions
- `explain_current_state()` - Natural language state explanation
- `recommend_optimizations()` - AI-driven optimization recommendations
- `interpret_user_intent()` - Natural language intent parsing
- `provide_contextual_help()` - Context-aware help and guidance

## Tool Implementation Pattern

All tools follow a consistent implementation pattern:

```python
from typing import Dict, Any
from core_new.guardrails import validate_inputs, check_security
from core_new.utilities import calculate_layout, format_response
from core_new.primitives import create_container_primitive

async def create_optimized_container_tool(
    container_id: str,
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a container with intelligent optimization.
    
    Args:
        container_id: Unique identifier for the container
        preferences: Optional user preferences for positioning/sizing
        
    Returns:
        Dict containing operation result and detailed information
    """
    try:
        # Step 1: Guardrails - Validation and Security
        validation_result = await validate_container_creation(container_id, preferences)
        if not validation_result.is_valid:
            return format_error_response(
                "Validation Failed",
                validation_result.error,
                suggestions=validation_result.suggestions
            )
        
        security_result = await check_operation_security("create_container", context)
        if not security_result.allowed:
            return format_error_response(
                "Security Check Failed", 
                security_result.error
            )
        
        # Step 2: Utilities - Calculations and Optimization
        current_state = get_canvas_state_primitive()
        layout_result = calculate_optimal_layout(
            containers=current_state.containers,
            new_container_id=container_id,
            preferences=preferences
        )
        
        # Step 3: Primitives - Execute Operation
        success = await create_container_primitive(
            container_id=container_id,
            x=layout_result.x,
            y=layout_result.y,
            width=layout_result.width,
            height=layout_result.height
        )
        
        if not success:
            return format_error_response(
                "Creation Failed",
                "Unable to create container with calculated parameters",
                retry_suggestions=["Try different container ID", "Check canvas space"]
            )
        
        # Step 4: Format Response
        return format_success_response(
            "Container Created Successfully",
            {
                "container_id": container_id,
                "position": (layout_result.x, layout_result.y),
                "size": (layout_result.width, layout_result.height),
                "optimization_applied": True,
                "space_utilization": layout_result.space_utilization,
                "recommendations": layout_result.recommendations
            }
        )
        
    except Exception as e:
        return format_error_response(
            "Unexpected Error",
            str(e),
            internal_error=True
        )
```

## Response Formatting

Tools provide rich, structured responses for AI consumption:

```python
# Success Response Format
{
    "status": "success",
    "message": "Human-readable success message",
    "data": {
        "operation_details": "...",
        "optimization_info": "...",
        "recommendations": ["..."]
    },
    "metadata": {
        "execution_time": "...",
        "resources_used": "...",
        "next_suggested_actions": ["..."]
    }
}

# Error Response Format
{
    "status": "error", 
    "message": "Human-readable error message",
    "error_code": "VALIDATION_FAILED",
    "details": {
        "validation_errors": ["..."],
        "suggestions": ["..."],
        "alternative_approaches": ["..."]
    },
    "recovery_options": ["..."]
}
```

## Integration with Registry

Tools are automatically discovered and registered:

```python
# Tool registration metadata
TOOL_METADATA = {
    "name": "create_optimized_container",
    "description": "Create a container with intelligent layout optimization",
    "category": "container_operations",
    "ai_accessible": True,
    "parameters": {
        "container_id": {
            "type": "string",
            "required": True,
            "description": "Unique identifier for the container"
        },
        "preferences": {
            "type": "object", 
            "required": False,
            "description": "Optional positioning and sizing preferences"
        }
    },
    "returns": {
        "type": "object",
        "description": "Operation result with optimization details"
    }
}
```

## Error Handling and Recovery

Tools implement comprehensive error handling:

```python
class ToolError(Exception):
    def __init__(self, message: str, error_code: str, suggestions: List[str] = None):
        self.message = message
        self.error_code = error_code
        self.suggestions = suggestions or []

async def handle_tool_error(error: Exception, operation_context: Dict) -> Dict[str, Any]:
    """Centralized error handling for all tools"""
    if isinstance(error, ToolError):
        return format_error_response(error.message, error.error_code, error.suggestions)
    
    # Log unexpected errors for debugging
    log_unexpected_error(error, operation_context)
    
    return format_error_response(
        "An unexpected error occurred",
        "INTERNAL_ERROR",
        suggestions=["Try the operation again", "Contact support if issue persists"]
    )
```

## Testing Strategy

Tools require comprehensive testing:
- **Unit Testing**: Test individual tool functions
- **Integration Testing**: Test tool orchestration of other layers
- **AI Interaction Testing**: Test with actual AI/LLM requests
- **Error Scenario Testing**: Test error handling and recovery
- **Performance Testing**: Measure tool execution times

## Implementation Guidelines

### ✅ **DO:**
- Always validate inputs through guardrails
- Use utilities for calculations and algorithms
- Provide rich, informative responses
- Handle errors gracefully with suggestions
- Include optimization and intelligence features

### ❌ **DON'T:**
- Call primitives directly without validation
- Implement validation logic in tools
- Return raw primitive responses
- Ignore error conditions
- Expose internal implementation details

## Status

🚧 **Currently**: Placeholder directory with basic structure
🤖 **Next Phase**: Implement core container and canvas tools
🎯 **Goal**: Provide intelligent, AI-friendly interfaces for all operations

This layer is the primary interface for AI interactions and should prioritize user experience, intelligence, and comprehensive functionality. 