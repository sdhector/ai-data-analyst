# Canvas Operations Brainstorming

## Overview

This document brainstorms the canvas operations that users should be able to perform, breaking down each action into detailed steps and identifying the required primitives, utilities, and guardrails.

## User Actions Analysis

### 1. Modify Canvas Size

**User Intent**: Change the dimensions of the canvas (width and/or height)

#### Detailed Steps Required:

1. **Input Validation & Processing**
   - Parse user input (could be "make it bigger", "resize to 1920x1080", "double the width", etc.)
   - Convert natural language to specific dimensions
   - Validate dimensions are within acceptable limits
   - Handle relative vs absolute sizing requests

2. **Current State Assessment**
   - Get current canvas dimensions
   - Get current container positions and sizes
   - Identify containers that would be affected by resize
   - Calculate impact on existing layout

3. **Conflict Detection & Resolution**
   - Identify containers that would be outside new canvas bounds
   - Determine if containers need to be moved, resized, or removed
   - Check for overlapping containers after resize
   - Plan container repositioning strategy

4. **Pre-resize Preparation**
   - Create backup of current canvas state
   - Lock canvas from other modifications
   - Notify frontend of impending resize operation

5. **Canvas Resize Execution**
   - Apply new canvas dimensions
   - Broadcast resize command to frontend
   - Update internal canvas state

6. **Container Adjustment**
   - Move containers that are now outside bounds
   - Resize containers if necessary to fit new canvas
   - Maintain relative positioning where possible
   - Update container positions in state

7. **Verification & Cleanup**
   - Verify canvas was resized successfully
   - Verify all containers are within bounds
   - Update layout optimization if needed
   - Release canvas lock
   - Clear backup state

#### Edge Cases to Handle:
- Canvas becomes smaller than existing containers
- Canvas becomes extremely large (performance impact)
- Multiple containers need repositioning
- User cancels operation mid-resize

---

### 2. Clear All Elements in Canvas

**User Intent**: Remove all containers/elements from the canvas

#### Detailed Steps Required:

1. **Intent Confirmation**
   - Confirm user really wants to clear everything
   - Check if this is a destructive operation that needs confirmation
   - Provide option to save current state before clearing

2. **Current State Capture**
   - Get list of all containers on canvas
   - Create backup of current canvas state for potential undo
   - Count total containers for progress reporting

3. **Dependency Analysis**
   - Check if any containers have dependencies on others
   - Identify containers that might be referenced by external systems
   - Plan deletion order to avoid reference errors

4. **Progressive Deletion**
   - Delete containers in safe order (dependencies first)
   - Report progress to user ("Removing 5 of 12 containers...")
   - Handle deletion failures gracefully
   - Update canvas state after each deletion

5. **Canvas State Reset**
   - Reset canvas to default/empty state
   - Clear any cached layout information
   - Reset canvas settings if needed
   - Update container count to zero

6. **Frontend Synchronization**
   - Broadcast clear command to frontend
   - Verify frontend has cleared all visual elements
   - Ensure frontend canvas is in clean state

7. **Cleanup & Finalization**
   - Clear any temporary files or resources
   - Update system state to reflect empty canvas
   - Provide confirmation to user
   - Store backup for potential undo operation

#### Edge Cases to Handle:
- Some containers fail to delete
- Frontend doesn't sync properly
- User wants to undo the clear operation
- System has containers that can't be deleted

---

### 3. Optimize Distribution of Elements in Canvas

**User Intent**: Automatically arrange containers for better layout, spacing, and visual organization

#### Detailed Steps Required:

1. **Layout Analysis**
   - Get all container positions, sizes, and types
   - Analyze current layout patterns and problems
   - Identify overlapping containers
   - Calculate current space utilization
   - Detect clustering and spacing issues

2. **Optimization Strategy Selection**
   - Determine optimization goals (minimize overlap, maximize space usage, create grid, etc.)
   - Consider container relationships and groupings
   - Choose appropriate layout algorithm (grid, force-directed, hierarchical, etc.)
   - Account for user preferences or layout constraints

3. **Layout Calculation**
   - Calculate optimal positions for all containers
   - Ensure no overlaps in new layout
   - Maintain reasonable spacing between elements
   - Preserve important container relationships
   - Optimize for visual appeal and usability

4. **Impact Assessment**
   - Compare new layout with current layout
   - Calculate how much each container will move
   - Identify containers that won't need to move
   - Estimate time required for repositioning

5. **User Preview & Confirmation**
   - Generate preview of optimized layout
   - Show user the proposed changes
   - Allow user to approve or modify the optimization
   - Provide option to adjust optimization parameters

6. **Gradual Repositioning**
   - Move containers to new positions progressively
   - Animate movements for better user experience
   - Handle collisions during movement
   - Update positions in real-time
   - Report progress to user

7. **Layout Validation**
   - Verify all containers are in correct positions
   - Check that no overlaps exist
   - Validate that all containers are within canvas bounds
   - Ensure layout meets optimization goals

8. **Finalization**
   - Save new layout as current state
   - Update any layout metadata
   - Provide optimization summary to user
   - Store previous layout for potential undo

#### Edge Cases to Handle:
- Too many containers to optimize efficiently
- Containers with fixed positions that can't move
- Optimization creates worse layout than original
- User cancels optimization mid-process
- Some containers fail to move to new positions

---

## Required Primitives

Based on the analysis above, we need these primitive functions:

### Canvas State Primitives
```python
# Canvas dimension management
async def get_canvas_dimensions_primitive() -> dict
async def set_canvas_dimensions_primitive(width: int, height: int) -> bool
async def validate_canvas_dimensions_primitive(width: int, height: int) -> bool

# Canvas state management
async def get_canvas_state_snapshot_primitive() -> dict
async def restore_canvas_state_primitive(state_snapshot: dict) -> bool
async def lock_canvas_primitive(operation_id: str) -> bool
async def unlock_canvas_primitive(operation_id: str) -> bool
```

### Container Management Primitives
```python
# Container queries
async def get_all_container_positions_primitive() -> list
async def get_containers_outside_bounds_primitive(width: int, height: int) -> list
async def get_overlapping_containers_primitive() -> list

# Container modifications
async def move_container_primitive(container_id: str, x: int, y: int) -> bool
async def resize_container_primitive(container_id: str, width: int, height: int) -> bool
async def delete_all_containers_primitive() -> dict
async def delete_container_batch_primitive(container_ids: list) -> dict
```

### Frontend Communication Primitives
```python
# Canvas commands
async def broadcast_canvas_resize_primitive(width: int, height: int) -> bool
async def broadcast_canvas_clear_primitive() -> bool
async def broadcast_container_move_primitive(container_id: str, x: int, y: int) -> bool

# State synchronization
async def request_frontend_state_primitive() -> dict
async def verify_frontend_canvas_size_primitive(width: int, height: int) -> bool
async def verify_frontend_container_positions_primitive(expected_positions: dict) -> bool
```

---

## Required Utilities

### Layout Calculation Utilities
```python
# Optimization algorithms
async def calculate_grid_layout_utility(containers: list, canvas_size: dict) -> dict
async def calculate_force_directed_layout_utility(containers: list, canvas_size: dict) -> dict
async def calculate_hierarchical_layout_utility(containers: list, canvas_size: dict) -> dict

# Layout analysis
async def analyze_layout_efficiency_utility(containers: list, canvas_size: dict) -> dict
async def detect_layout_problems_utility(containers: list) -> list
async def calculate_space_utilization_utility(containers: list, canvas_size: dict) -> float

# Positioning utilities
async def find_optimal_position_utility(container_size: dict, existing_containers: list, canvas_size: dict) -> dict
async def calculate_movement_path_utility(from_pos: dict, to_pos: dict, obstacles: list) -> list
async def minimize_container_movements_utility(current_layout: dict, target_layout: dict) -> dict
```

### Input Processing Utilities
```python
# Natural language processing
async def parse_canvas_size_request_utility(user_input: str, current_size: dict) -> dict
async def parse_layout_optimization_request_utility(user_input: str) -> dict

# Dimension calculations
async def calculate_relative_dimensions_utility(base_size: dict, modifier: str) -> dict
async def validate_dimension_constraints_utility(width: int, height: int) -> dict
```

### State Management Utilities
```python
# Backup and restore
async def create_canvas_backup_utility(backup_id: str) -> bool
async def restore_canvas_backup_utility(backup_id: str) -> bool
async def cleanup_old_backups_utility(max_age_hours: int) -> int

# Progress tracking
async def create_progress_tracker_utility(operation_name: str, total_steps: int) -> str
async def update_progress_utility(tracker_id: str, current_step: int, message: str) -> bool
async def complete_progress_utility(tracker_id: str, final_message: str) -> bool
```

---

## Required Guardrails

### Canvas Dimension Guardrails
```python
# Size validation
async def validate_canvas_size_guardrail(width: int, height: int) -> dict
async def check_canvas_size_limits_guardrail(width: int, height: int) -> dict
async def validate_canvas_resize_impact_guardrail(new_size: dict, containers: list) -> dict

# Performance protection
async def check_canvas_performance_impact_guardrail(width: int, height: int, container_count: int) -> dict
async def validate_operation_complexity_guardrail(operation_type: str, affected_containers: int) -> dict
```

### Container Safety Guardrails
```python
# Deletion protection
async def confirm_destructive_operation_guardrail(operation_type: str, affected_count: int) -> dict
async def check_container_dependencies_guardrail(container_ids: list) -> dict
async def validate_batch_operation_size_guardrail(operation_type: str, batch_size: int) -> dict

# Position validation
async def validate_container_positions_guardrail(positions: dict, canvas_size: dict) -> dict
async def check_container_overlap_guardrail(containers: list) -> dict
async def validate_container_movement_guardrail(movements: dict) -> dict
```

### System Resource Guardrails
```python
# Resource protection
async def check_memory_usage_guardrail(operation_type: str) -> dict
async def validate_operation_timeout_guardrail(operation_type: str, complexity: int) -> dict
async def check_concurrent_operations_guardrail(operation_type: str) -> dict

# State consistency
async def validate_canvas_state_consistency_guardrail() -> dict
async def check_frontend_sync_status_guardrail() -> dict
async def validate_backup_integrity_guardrail(backup_id: str) -> dict
```

---

## Implementation Notes

### Priority Order
1. **High Priority**: Basic canvas resize and clear operations
2. **Medium Priority**: Layout optimization with simple algorithms
3. **Low Priority**: Advanced optimization algorithms and complex layout analysis

### Dependencies
- Canvas resize depends on container repositioning utilities
- Layout optimization requires multiple algorithm utilities
- All operations need comprehensive guardrails for safety

### Performance Considerations
- Large canvas sizes may impact frontend performance
- Layout optimization with many containers may be computationally expensive
- Batch operations should be chunked for better responsiveness

### User Experience
- All operations should provide progress feedback
- Destructive operations need confirmation
- Users should be able to undo major layout changes
- Preview functionality for layout optimization is highly desirable 