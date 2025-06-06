# Primitives - Core Atomic Operations

This directory contains the lowest-level functions that directly manipulate canvas state. These are the building blocks that all higher-level operations are built upon.

## Design Philosophy

Primitive functions follow strict design principles:

### 1. **Single Responsibility**
- Each function performs exactly one atomic operation
- No complex workflows or multi-step processes
- Clear, focused purpose with minimal side effects

### 2. **No Validation**
- Accept parameters as-is without validation
- No input sanitization or bounds checking
- Trust that higher layers have validated inputs

### 3. **No Optimization**
- Perform operations exactly as requested
- No automatic layout optimization or intelligent positioning
- No overlap prevention or auto-adjustment

### 4. **Minimal Dependencies**
- Direct interaction with canvas_bridge only
- No dependencies on utilities, guardrails, or tools
- Self-contained with basic error handling

### 5. **Not AI-Accessible**
- Never exposed directly to AI/LLM
- Only called by tools layer functions
- Internal implementation details

## Module Organization

### `container_operations.py`
Core container manipulation functions:
- `create_container_primitive()` - Create container with exact parameters
- `delete_container_primitive()` - Delete container by ID
- `modify_container_primitive()` - Modify container position/size
- `get_container_primitive()` - Retrieve specific container
- `list_containers_primitive()` - Get all containers as raw data
- `container_exists_primitive()` - Check container existence

### `canvas_operations.py`
Core canvas manipulation functions:
- `clear_canvas_primitive()` - Remove all containers
- `resize_canvas_primitive()` - Change canvas dimensions
- `take_screenshot_primitive()` - Capture canvas state
- `broadcast_canvas_command_primitive()` - Send raw frontend commands

### `state_operations.py`
Core state retrieval functions:
- `get_canvas_state_primitive()` - Get raw canvas state
- `get_canvas_size_primitive()` - Get canvas dimensions
- `get_canvas_settings_primitive()` - Get canvas settings
- `get_container_count_primitive()` - Count containers
- `get_all_container_ids_primitive()` - Get all container IDs
- `canvas_has_containers_primitive()` - Check if canvas has containers
- `get_websocket_connection_count_primitive()` - Count active connections

## Error Handling

Primitive functions use minimal error handling:
- Log errors with `[PRIMITIVE ERROR]` prefix
- Return sensible defaults (False, None, empty collections)
- Never raise exceptions to calling code
- Fail gracefully without breaking workflows

## Usage Guidelines

### ✅ **DO:**
- Use primitives as building blocks in tools layer
- Trust that inputs have been validated by guardrails
- Handle primitive failures gracefully in tools
- Keep primitive functions simple and focused

### ❌ **DON'T:**
- Call primitives directly from AI/LLM interfaces
- Add validation logic to primitive functions
- Implement complex workflows in primitives
- Expose primitives in function schemas

## Testing

Primitive functions should be tested with:
- Valid inputs to verify correct operation
- Invalid inputs to verify graceful failure
- Edge cases and boundary conditions
- Integration with canvas_bridge

## Future Extensions

When adding new primitives:
1. Follow the established patterns and principles
2. Keep functions atomic and focused
3. Add comprehensive docstrings
4. Update the `__init__.py` exports
5. Add corresponding tests

## Examples

```python
# ✅ Correct usage (from tools layer)
async def create_optimized_container(container_id: str):
    # Guardrails validate inputs
    # Utilities calculate optimal position
    x, y, width, height = calculate_optimal_layout(...)
    
    # Primitive performs the actual operation
    success = await create_container_primitive(
        container_id, x, y, width, height
    )
    return success

# ❌ Incorrect usage (direct AI access)
# Never expose primitives directly to AI
```

This layer provides the foundation for all canvas operations while maintaining strict separation of concerns and security boundaries. 