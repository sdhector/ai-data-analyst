# Auto-Layout System Specification & Implementation Plan

## Overview

This document defines a comprehensive auto-layout system that intelligently manages container placement, sizing, and organization on the canvas. The system provides smart defaults while maintaining user control and flexibility.

## Core Principles

1. **Auto-layout by default** - Containers are automatically positioned and sized optimally
2. **Progressive size reduction** - Container sizes adapt intelligently as count increases
3. **Square containers** - Maintain 1:1 aspect ratio for aesthetic consistency  
4. **Pyramid patterns** - Elegant handling of odd container counts (3, 5, 7, etc.)
5. **Context awareness** - Layout decisions based on current canvas state
6. **User override capability** - Manual positioning available with confirmation
7. **Background optimization** - Continuous monitoring and recommendations

## Layout Specifications

### Container Count Patterns

#### 1 Container
- **Layout**: Single container centered on canvas
- **Size**: 90% of available canvas space (respecting margins)
- **Position**: Perfectly centered both horizontally and vertically

```
┌─────────────────────┐
│                     │
│   ┌─────────────┐   │
│   │             │   │
│   │      1      │   │
│   │             │   │
│   └─────────────┘   │
│                     │
└─────────────────────┘
```

#### 2 Containers  
- **Layout**: One row, two columns
- **Size**: Equally sized squares fitting in available width
- **Position**: Horizontally centered with gap between containers

```
┌─────────────────────┐
│                     │
│   ┌─────┬─────┐     │
│   │  1  │  2  │     │
│   │     │     │     │
│   └─────┴─────┘     │
│                     │
└─────────────────────┘
```

#### 3 Containers
- **Layout**: Pyramid - 2 containers on top row, 1 spanning below
- **Size**: Top containers are squares, bottom container width = 2*square_size + gap
- **Position**: All centered, maintaining alignment

```
┌─────────────────────┐
│                     │
│   ┌─────┬─────┐     │
│   │  1  │  2  │     │
│   │     │     │     │
│   ├─────┴─────┤     │
│   │     3     │     │
│   └───────────┘     │
│                     │
└─────────────────────┘
```

#### 4 Containers
- **Layout**: 2x2 grid
- **Size**: Equal squares fitting in available space
- **Position**: Centered grid with gaps between all containers

```
┌─────────────────────┐
│                     │
│   ┌─────┬─────┐     │
│   │  1  │  2  │     │
│   ├─────┼─────┤     │
│   │  3  │  4  │     │
│   └─────┴─────┘     │
│                     │
└─────────────────────┘
```

#### 5 Containers
- **Layout**: Pyramid - 2x2 grid on top, 1 spanning bottom
- **Size**: Top 4 are squares, bottom spans width of 2 squares + gap
- **Position**: Centered pyramid structure

```
┌─────────────────────┐
│                     │
│   ┌─────┬─────┐     │
│   │  1  │  2  │     │
│   ├─────┼─────┤     │
│   │  3  │  4  │     │
│   ├─────┴─────┤     │
│   │     5     │     │
│   └───────────┘     │
│                     │
└─────────────────────┘
```

#### 6+ Containers
- **Layout**: Extends pyramid pattern or transitions to grid
- **6**: 2x3 grid
- **7**: 3x3 grid with bottom container spanning 3 columns
- **8**: 3x3 grid with bottom row having 2 containers
- **9**: 3x3 perfect grid
- **10+**: Dynamic grid calculation with pyramid handling for odd numbers

### Spacing and Margins

#### Canvas Margins
- **Outer padding**: 5% of smaller canvas dimension (min 20px, max 50px)
- **Ensures**: Containers never touch canvas edges
- **Responsive**: Scales with canvas size

#### Container Gaps
- **Between containers**: 10px minimum, scales up to 2% of canvas width for large canvases
- **Maintains**: Visual separation and clean appearance
- **Consistent**: Same gap size used throughout layout

#### Size Calculation Formula
```python
def calculate_container_size(container_count: int, canvas_size: dict) -> int:
    padding = min(canvas_size["width"], canvas_size["height"]) * 0.05
    gap = max(10, min(canvas_size["width"], canvas_size["height"]) * 0.02)
    
    usable_width = canvas_size["width"] - (2 * padding)
    usable_height = canvas_size["height"] - (2 * padding)
    
    if container_count == 1:
        return int(min(usable_width, usable_height) * 0.9)
    
    rows, cols = calculate_grid_dimensions(container_count)
    
    max_width_per_container = (usable_width - (cols - 1) * gap) // cols
    max_height_per_container = (usable_height - (rows - 1) * gap) // rows
    
    return min(max_width_per_container, max_height_per_container)
```

## User Control Mechanisms

### Auto vs Manual Mode Toggle

#### Default Behavior
- **Auto-layout enabled** by default for all new containers
- **Smart positioning** without user input required
- **Progressive resizing** of existing containers when new ones added

#### Manual Override Detection
- **LLM Recognition**: When user provides specific coordinates or dimensions
- **Confirmation Prompt**: "Manual positioning detected. Disable auto-layout mode?"
- **Mode Switch**: Auto-layout disabled until user confirms re-enabling

#### Manual Mode Triggers
- User specifies exact coordinates: "create container at (100, 200)"
- User specifies exact dimensions: "make container 150x150 pixels"
- User manually resizes existing container
- User manually moves existing container

#### Re-enabling Auto-layout
- **User Confirmation Required**: "Would you like to re-enable auto-layout mode?"
- **Layout Recalculation**: All containers repositioned according to auto-layout rules
- **Smooth Transition**: Animated movement to new positions

### Mixed Layout Constraints
- **Phase 1**: No mixed layouts - all containers either auto or manual
- **Future Enhancement**: Allow pinning specific containers while others auto-layout
- **State Tracking**: Track which containers were manually positioned

## Implementation Architecture

### 1. AutoLayoutEngine Class

```python
class AutoLayoutEngine:
    """Core engine for calculating optimal container layouts"""
    
    def __init__(self, canvas_size: dict):
        self.canvas_size = canvas_size
        self.padding = self._calculate_padding()
        self.gap = self._calculate_gap()
    
    async def calculate_layout(self, container_count: int) -> List[dict]:
        """Calculate positions and sizes for all containers"""
        
    async def calculate_container_size(self, count: int) -> int:
        """Calculate optimal square size for given container count"""
        
    async def calculate_positions(self, count: int, size: int) -> List[tuple]:
        """Calculate (x, y) positions for pyramid/grid layout"""
        
    async def calculate_grid_dimensions(self, count: int) -> tuple:
        """Determine (rows, cols) for container count"""
        
    # Layout pattern methods
    async def _layout_single(self, size: int) -> List[tuple]
    async def _layout_two_horizontal(self, size: int) -> List[tuple]
    async def _layout_three_pyramid(self, size: int) -> List[tuple]
    async def _layout_four_grid(self, size: int) -> List[tuple]
    async def _layout_five_pyramid(self, size: int) -> List[tuple]
    # ... continue for 6+ containers
```

### 2. Enhanced Tool Layer

```python
async def create_container_tool(
    container_id: str,
    x: Optional[int] = None,
    y: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    auto_layout: Optional[bool] = None,
    intent: Optional[str] = None  # "header", "sidebar", "card", etc.
):
    """Enhanced container creation with auto-layout intelligence"""
    
    # Detect manual parameters
    manual_params_provided = any(param is not None for param in [x, y, width, height])
    
    # Get current layout state  
    layout_state = canvas_bridge.get_layout_state()
    auto_layout_enabled = layout_state.get("auto_layout_enabled", True)
    
    # Handle mode conflicts
    if manual_params_provided and auto_layout_enabled:
        return await _handle_manual_override_detection(container_id, x, y, width, height)
    
    # Auto-layout calculation
    if auto_layout_enabled or auto_layout is True:
        return await _create_with_auto_layout(container_id, intent)
    
    # Manual positioning
    return await _create_with_manual_positioning(container_id, x, y, width, height)

async def _create_with_auto_layout(container_id: str, intent: Optional[str] = None):
    """Create container using auto-layout system"""
    
    existing_count = len(canvas_bridge.canvas_state.get("containers", {}))
    new_count = existing_count + 1
    
    layout_engine = AutoLayoutEngine(canvas_bridge.get_canvas_size())
    all_positions = await layout_engine.calculate_layout(new_count)
    
    # Reposition existing containers for optimal layout
    await _reposition_existing_containers(all_positions[:-1])
    
    # Create new container with calculated position
    new_position = all_positions[-1]
    return await create_container_primitive(
        container_id, 
        new_position["x"], 
        new_position["y"], 
        new_position["width"], 
        new_position["height"]
    )

async def _handle_manual_override_detection(container_id: str, x: int, y: int, width: int, height: int):
    """Handle detection of manual positioning intent"""
    
    return {
        "status": "requires_confirmation",
        "message": "Manual positioning detected. Would you like to disable auto-layout mode and place the container manually?",
        "action_required": "confirm_disable_auto_layout",
        "pending_operation": {
            "type": "create_container",
            "params": {"container_id": container_id, "x": x, "y": y, "width": width, "height": height}
        }
    }
```

### 3. Canvas Utilization Monitor

```python
class CanvasUtilizationMonitor:
    """Background service monitoring canvas efficiency and providing recommendations"""
    
    def __init__(self):
        self.monitoring_enabled = True
        self.check_interval = 30  # seconds
        self.last_recommendations = {}
    
    async def start_monitoring(self):
        """Start background monitoring loop"""
        while self.monitoring_enabled:
            await self._perform_analysis()
            await asyncio.sleep(self.check_interval)
    
    async def _perform_analysis(self) -> dict:
        """Analyze current canvas utilization"""
        
        canvas_size = canvas_bridge.get_canvas_size()
        containers = canvas_bridge.get_existing_containers()
        
        analysis = {
            "utilization_percent": self._calculate_space_utilization(containers, canvas_size),
            "container_count": len(containers),
            "recommendations": await self._generate_recommendations(containers, canvas_size)
        }
        
        return analysis
```

## Implementation Phases

### Phase 1: Core Auto-Layout Engine (Priority: Critical)
**Timeline: 3-4 days**

#### Components to Implement:
1. **AutoLayoutEngine Class**
   - Container size calculation algorithms
   - Position calculation for 1-5 container patterns
   - Grid dimension calculation 
   - Spacing and margin calculations

2. **Enhanced create_container_tool**
   - Auto-layout parameter resolution
   - Manual override detection
   - Layout mode integration

3. **Layout State Management**
   - Enhanced canvas_state structure
   - Layout mode tracking
   - Container creation order tracking

4. **Basic Repositioning System**
   - Reposition existing containers when new ones added
   - Smooth transitions between layouts
   - Validation of final positions

#### Success Criteria:
- ✅ 1-5 containers automatically position correctly
- ✅ Container sizes scale appropriately 
- ✅ Pyramid patterns work for odd numbers
- ✅ Manual override detection functional
- ✅ Layout state persisted correctly

### Phase 2: User Control & Intelligence (Priority: High)
**Timeline: 2-3 days**

#### Components to Implement:
1. **Manual Override System**
   - LLM detection of manual positioning intent
   - Confirmation prompts for mode switching
   - State transitions between auto/manual modes

2. **Layout Mode Management**
   - Toggle between auto and manual modes
   - User preference persistence
   - Mode-specific behavior enforcement

3. **Enhanced Container Operations**
   - Auto-layout disable on manual resize/move
   - Layout recalculation on container deletion
   - Batch operations with layout preservation

4. **Extended Layout Patterns**
   - 6-12 container arrangements
   - Dynamic grid calculation
   - Pyramid pattern extensions

#### Success Criteria:
- ✅ Users can override auto-layout when needed
- ✅ Mode switching works with confirmations
- ✅ Manual operations disable auto-layout appropriately
- ✅ Extended patterns work for 6+ containers

### Phase 3: Monitoring & Optimization (Priority: Medium)
**Timeline: 2-3 days**

#### Components to Implement:
1. **CanvasUtilizationMonitor**
   - Background monitoring service
   - Space utilization calculations
   - Layout efficiency analysis
   - Recommendation generation

2. **Intelligent Recommendations**
   - Canvas size optimization suggestions
   - Container count management
   - Layout improvement recommendations
   - Performance impact warnings

3. **Advanced Layout Features**
   - Layout optimization algorithms
   - Automatic layout improvements
   - Smart container grouping
   - Visual appeal metrics

#### Success Criteria:
- ✅ Background monitoring operational
- ✅ Intelligent recommendations generated
- ✅ Canvas utilization tracked accurately
- ✅ Performance recommendations provided

### Phase 4: Polish & Advanced Features (Priority: Low)
**Timeline: 1-2 days**

#### Components to Implement:
1. **Animation & Transitions**
   - Smooth container movements
   - Layout transition animations
   - Progressive repositioning

2. **Layout Templates**
   - Dashboard layout presets
   - Grid layout variations
   - Custom layout patterns

3. **Undo/Redo System**
   - Layout history tracking
   - State rollback capabilities
   - Operation reversal

#### Success Criteria:
- ✅ Smooth visual transitions
- ✅ Layout templates available
- ✅ Undo/redo functional
- ✅ Performance optimized for scale

## Additional Ideas & Future Enhancements

### Smart Container Intents
- **Semantic understanding**: "create a header" → auto-sized for header use
- **Component templates**: Pre-defined sizes for common UI elements
- **Relationship awareness**: Containers that work together (header + sidebar + main)

### Advanced Layout Algorithms
- **Magnetic alignment**: Containers snap to invisible grid lines
- **Golden ratio sizing**: Aesthetically pleasing proportions
- **Whitespace optimization**: Maximize visual breathing room
- **Balance scoring**: Quantify layout visual balance

### User Learning System
- **Preference detection**: Learn from user's manual adjustments
- **Pattern recognition**: Identify user's preferred layouts
- **Adaptive defaults**: Adjust auto-layout based on usage patterns
- **Style consistency**: Maintain visual consistency across sessions

### Multi-Canvas Management
- **Canvas relationships**: Link related canvases
- **Cross-canvas optimization**: Optimize layouts across multiple canvases
- **Canvas templates**: Pre-configured canvas layouts
- **Workspace management**: Organize multiple canvases

### Performance & Scalability
- **Lazy layout calculation**: Calculate only visible layouts
- **Layout caching**: Cache complex layout calculations
- **Progressive rendering**: Render large layouts progressively
- **Memory optimization**: Efficient data structures for large container counts

### Accessibility & Usability
- **Keyboard navigation**: Navigate between auto-positioned containers
- **Screen reader support**: Describe auto-layout decisions
- **High contrast mode**: Ensure layouts work with accessibility themes
- **Mobile responsiveness**: Adapt layouts for different screen sizes

### Analytics & Insights
- **Layout efficiency metrics**: Quantify layout quality
- **User behavior tracking**: Understand how users interact with auto-layout
- **Performance monitoring**: Track layout calculation performance
- **Usage analytics**: Identify most common layout patterns

## Testing Strategy

### Unit Tests
- **Layout calculation accuracy** for all container counts
- **Spacing algorithm correctness** with various canvas sizes
- **Grid dimension calculation** for different patterns
- **Edge case handling** (very small/large canvases)

### Integration Tests
- **Auto-layout with existing containers** repositioning correctly
- **Mode switching** with proper state transitions
- **Manual override detection** and confirmation flows
- **Background monitoring** integration with layout system

### User Experience Tests
- **Layout quality assessment** with real-world scenarios
- **Performance testing** with many containers
- **Accessibility testing** with screen readers
- **Cross-browser compatibility** testing

### Performance Benchmarks
- **Layout calculation speed** for 1-50 containers
- **Memory usage** with large container counts
- **Animation smoothness** during repositioning
- **Background monitoring overhead**

## Success Metrics

### User Experience
- **Reduced manual positioning**: 80% of containers created with auto-layout
- **User satisfaction**: Positive feedback on automatic layouts
- **Error reduction**: Fewer overlapping containers and bound violations
- **Efficiency gains**: Faster container creation workflow

### Technical Performance
- **Layout calculation speed**: <100ms for up to 20 containers
- **Memory usage**: Minimal impact on overall system memory
- **State management**: Reliable persistence across sessions
- **Background monitoring**: <5% CPU overhead

### System Adoption
- **Feature usage**: Auto-layout enabled for majority of users
- **Manual override frequency**: <20% of container operations
- **Recommendation acceptance**: Users follow 60%+ of recommendations
- **Mode switching**: Smooth transitions between auto/manual modes

---

This specification provides a comprehensive foundation for implementing an intelligent, user-friendly auto-layout system that balances automation with user control while maintaining high performance and usability. 