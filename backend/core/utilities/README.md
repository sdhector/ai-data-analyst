# Utilities - Shared Functionality and Algorithms

This directory contains reusable functionality and algorithms used by multiple tools and operations. Utilities provide common functionality without direct canvas manipulation.

## Purpose

Utilities serve as the "library" layer of the architecture:
- **Reusable Components**: Common functionality used across multiple tools
- **Algorithm Implementation**: Complex calculations and optimizations
- **Data Transformation**: Format conversion and data processing
- **Helper Functions**: Supporting functionality for tools and guardrails

## Design Principles

### 1. **Pure Functions**
- No side effects or state modification
- Deterministic outputs for given inputs
- Easy to test and reason about

### 2. **Reusability**
- Designed to be used by multiple tools
- Generic implementations that can be parameterized
- Well-defined interfaces and contracts

### 3. **No Canvas Interaction**
- Never directly manipulate canvas state
- Work with data structures and calculations only
- Leave actual operations to primitives

### 4. **Stateless**
- No internal state or memory
- Each function call is independent
- Thread-safe and concurrent-friendly

## Planned Modules

### `layout_optimization.py` (To Be Implemented)
Advanced layout algorithms:
- `calculate_optimal_grid_layout()` - Grid-based container positioning
- `calculate_space_utilization()` - Efficiency metrics
- `find_non_overlapping_positions()` - Collision avoidance
- `optimize_container_sizes()` - Size uniformity algorithms

### `validation_helpers.py` (To Be Implemented)
Common validation utilities:
- `validate_container_id()` - ID format and uniqueness checking
- `validate_coordinates()` - Position and size validation
- `validate_canvas_bounds()` - Boundary checking
- `sanitize_user_input()` - Input cleaning and normalization

### `data_transformers.py` (To Be Implemented)
Data format conversion utilities:
- `format_container_response()` - Response formatting for AI
- `parse_layout_parameters()` - Parameter extraction and parsing
- `convert_coordinates()` - Coordinate system conversions
- `serialize_canvas_state()` - State serialization utilities

### `mathematical_utils.py` (To Be Implemented)
Mathematical calculations:
- `calculate_distance()` - Distance calculations
- `check_rectangle_overlap()` - Geometric overlap detection
- `calculate_aspect_ratio()` - Ratio calculations
- `round_to_grid()` - Grid snapping utilities

### `identifier_management.py` (To Be Implemented)
ID generation and management:
- `generate_unique_id()` - Unique identifier generation
- `suggest_alternative_ids()` - Alternative ID suggestions
- `clean_identifier()` - ID sanitization
- `check_id_conflicts()` - Conflict detection

## Usage Patterns

### From Tools Layer
```python
# Tools use utilities for calculations
from core_new.utilities.layout_optimization import calculate_optimal_grid_layout
from core_new.utilities.validation_helpers import validate_container_id

async def create_optimized_container_tool(container_id: str):
    # Use utility for validation
    validation_result = validate_container_id(container_id)
    if not validation_result.is_valid:
        return error_response(validation_result.error)
    
    # Use utility for layout calculation
    layout = calculate_optimal_grid_layout(containers, canvas_size)
    
    # Use primitive for actual operation
    success = await create_container_primitive(...)
    return success
```

### From Guardrails
```python
# Guardrails use utilities for validation
from core_new.utilities.validation_helpers import validate_coordinates

def validate_container_creation(x, y, width, height):
    coord_validation = validate_coordinates(x, y, width, height)
    return coord_validation.is_valid
```

## Implementation Guidelines

### ✅ **DO:**
- Keep functions pure and stateless
- Provide comprehensive docstrings
- Include type hints for all parameters
- Design for reusability across tools
- Focus on single responsibility

### ❌ **DON'T:**
- Directly manipulate canvas state
- Maintain internal state between calls
- Depend on specific tool implementations
- Include AI-specific formatting logic

## Testing Strategy

Utilities should have comprehensive unit tests:
- **Pure Function Testing**: Verify outputs for various inputs
- **Edge Case Coverage**: Test boundary conditions
- **Performance Testing**: Ensure algorithms are efficient
- **Integration Testing**: Verify usage in tools layer

## Future Development

When implementing utilities:

1. **Identify Common Patterns**: Look for repeated code in tools
2. **Extract Pure Logic**: Separate calculations from operations
3. **Design Generic Interfaces**: Make functions reusable
4. **Add Comprehensive Tests**: Ensure reliability
5. **Document Usage Examples**: Show how to use utilities

## Dependencies

Utilities may depend on:
- Standard Python libraries (math, typing, etc.)
- Third-party libraries for algorithms (numpy, etc.)
- Other utility modules within this directory

Utilities should NOT depend on:
- Primitives layer
- Tools layer
- Guardrails layer
- Canvas bridge directly

## Status

🚧 **Currently**: Placeholder directory with basic structure
📋 **Next Phase**: Implement layout optimization utilities
🎯 **Goal**: Provide robust, reusable functionality for all tools

This layer will significantly reduce code duplication and provide a solid foundation for complex tool implementations. 