"""
Auto-Layout Engine

Core layout calculation algorithms for intelligent container positioning.
This utility provides pure calculation functions that determine optimal
container positions and sizes based on canvas dimensions and layout patterns.

Architecture: Utilities layer - no direct canvas manipulation, only calculations.
"""

import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass


@dataclass
class ContainerLayout:
    """Container layout specification"""
    x: int
    y: int
    width: int
    height: int
    container_id: str
    layout_index: int = 0  # Position in layout order


@dataclass
class LayoutConfiguration:
    """Layout configuration parameters"""
    canvas_width: int
    canvas_height: int
    container_gap: int = 10
    canvas_padding: int = 20
    aspect_ratio: float = 1.0  # 1.0 = square containers
    min_container_size: int = 50
    max_container_size: int = 400


class AutoLayoutEngine:
    """
    Core auto-layout calculation engine.
    
    Provides pure calculation functions for determining optimal container
    layouts based on various patterns and configurations.
    """
    
    def __init__(self):
        """Initialize the layout engine"""
        self.supported_patterns = [
            "single_centered",
            "dual_column", 
            "triple_pyramid",
            "quad_grid",
            "penta_pyramid",
            "multi_grid"
        ]
    
    def calculate_layout(
        self,
        container_count: int,
        config: LayoutConfiguration,
        container_ids: Optional[List[str]] = None
    ) -> List[ContainerLayout]:
        """
        Calculate optimal layout for given number of containers.
        
        Args:
            container_count: Number of containers to layout
            config: Layout configuration parameters
            container_ids: Optional list of container IDs (generates defaults if None)
            
        Returns:
            List of ContainerLayout specifications
        """
        if container_count <= 0:
            return []
        
        # Generate container IDs if not provided
        if container_ids is None:
            container_ids = [f"container_{i+1}" for i in range(container_count)]
        elif len(container_ids) != container_count:
            raise ValueError(f"Container ID count ({len(container_ids)}) doesn't match container_count ({container_count})")
        
        # Select appropriate layout pattern
        if container_count == 1:
            return self._layout_single_centered(config, container_ids)
        elif container_count == 2:
            return self._layout_dual_column(config, container_ids)
        elif container_count == 3:
            return self._layout_triple_pyramid(config, container_ids)
        elif container_count == 4:
            return self._layout_quad_grid(config, container_ids)
        elif container_count == 5:
            return self._layout_penta_pyramid(config, container_ids)
        else:
            return self._layout_multi_grid(container_count, config, container_ids)
    
    def _layout_single_centered(
        self,
        config: LayoutConfiguration,
        container_ids: List[str]
    ) -> List[ContainerLayout]:
        """Layout for single container - centered, 5-10% smaller than canvas"""
        
        # Calculate container size (80-90% of canvas, maintaining aspect ratio)
        available_width = config.canvas_width - (2 * config.canvas_padding)
        available_height = config.canvas_height - (2 * config.canvas_padding)
        
        # Use 85% of available space
        target_width = int(available_width * 0.85)
        target_height = int(available_height * 0.85)
        
        # Apply aspect ratio constraint
        if config.aspect_ratio == 1.0:
            # Square containers - use smaller dimension
            size = min(target_width, target_height)
            width = height = size
        else:
            # Maintain aspect ratio
            if target_width / target_height > config.aspect_ratio:
                height = target_height
                width = int(height * config.aspect_ratio)
            else:
                width = target_width
                height = int(width / config.aspect_ratio)
        
        # Apply size constraints
        width = max(config.min_container_size, min(config.max_container_size, width))
        height = max(config.min_container_size, min(config.max_container_size, height))
        
        # Center on canvas
        x = (config.canvas_width - width) // 2
        y = (config.canvas_height - height) // 2
        
        return [ContainerLayout(
            x=x, y=y, width=width, height=height,
            container_id=container_ids[0], layout_index=0
        )]
    
    def _layout_dual_column(
        self,
        config: LayoutConfiguration,
        container_ids: List[str]
    ) -> List[ContainerLayout]:
        """Layout for two containers - side by side columns"""
        
        available_width = config.canvas_width - (2 * config.canvas_padding)
        available_height = config.canvas_height - (2 * config.canvas_padding)
        
        # Calculate container dimensions
        container_width = (available_width - config.container_gap) // 2
        container_height = available_height
        
        # Apply aspect ratio for square containers
        if config.aspect_ratio == 1.0:
            size = min(container_width, container_height)
            container_width = container_height = size
            
            # Recalculate total width needed
            total_width = (2 * container_width) + config.container_gap
            start_x = (config.canvas_width - total_width) // 2
            start_y = (config.canvas_height - container_height) // 2
        else:
            start_x = config.canvas_padding
            start_y = config.canvas_padding
        
        # Apply size constraints
        container_width = max(config.min_container_size, min(config.max_container_size, container_width))
        container_height = max(config.min_container_size, min(config.max_container_size, container_height))
        
        layouts = []
        for i, container_id in enumerate(container_ids):
            x = start_x + (i * (container_width + config.container_gap))
            y = start_y
            
            layouts.append(ContainerLayout(
                x=x, y=y, width=container_width, height=container_height,
                container_id=container_id, layout_index=i
            ))
        
        return layouts
    
    def _layout_triple_pyramid(
        self,
        config: LayoutConfiguration,
        container_ids: List[str]
    ) -> List[ContainerLayout]:
        """Layout for three containers - 2 on top row, 1 centered below"""
        
        available_width = config.canvas_width - (2 * config.canvas_padding)
        available_height = config.canvas_height - (2 * config.canvas_padding)
        
        # Calculate grid dimensions: 2 rows, with top row having 2 containers
        row_height = (available_height - config.container_gap) // 2
        container_width = (available_width - config.container_gap) // 2
        
        # Apply aspect ratio for square containers
        if config.aspect_ratio == 1.0:
            size = min(container_width, row_height)
            container_width = container_height = size
        else:
            container_height = row_height
        
        # Apply size constraints  
        container_width = max(config.min_container_size, min(config.max_container_size, container_width))
        container_height = max(config.min_container_size, min(config.max_container_size, container_height))
        
        layouts = []
        
        # Top row: 2 containers
        top_row_width = (2 * container_width) + config.container_gap
        top_start_x = (config.canvas_width - top_row_width) // 2
        top_y = config.canvas_padding
        
        for i in range(2):
            x = top_start_x + (i * (container_width + config.container_gap))
            layouts.append(ContainerLayout(
                x=x, y=top_y, width=container_width, height=container_height,
                container_id=container_ids[i], layout_index=i
            ))
        
        # Bottom row: 1 centered container
        bottom_x = (config.canvas_width - container_width) // 2
        bottom_y = top_y + container_height + config.container_gap
        
        layouts.append(ContainerLayout(
            x=bottom_x, y=bottom_y, width=container_width, height=container_height,
            container_id=container_ids[2], layout_index=2
        ))
        
        return layouts
    
    def _layout_quad_grid(
        self,
        config: LayoutConfiguration,
        container_ids: List[str]
    ) -> List[ContainerLayout]:
        """Layout for four containers - 2x2 grid"""
        
        available_width = config.canvas_width - (2 * config.canvas_padding)
        available_height = config.canvas_height - (2 * config.canvas_padding)
        
        # Calculate 2x2 grid dimensions
        container_width = (available_width - config.container_gap) // 2
        container_height = (available_height - config.container_gap) // 2
        
        # Apply aspect ratio for square containers
        if config.aspect_ratio == 1.0:
            size = min(container_width, container_height)
            container_width = container_height = size
            
            # Center the grid
            grid_width = (2 * container_width) + config.container_gap
            grid_height = (2 * container_height) + config.container_gap
            start_x = (config.canvas_width - grid_width) // 2
            start_y = (config.canvas_height - grid_height) // 2
        else:
            start_x = config.canvas_padding
            start_y = config.canvas_padding
        
        # Apply size constraints
        container_width = max(config.min_container_size, min(config.max_container_size, container_width))
        container_height = max(config.min_container_size, min(config.max_container_size, container_height))
        
        layouts = []
        for i, container_id in enumerate(container_ids):
            row = i // 2
            col = i % 2
            
            x = start_x + (col * (container_width + config.container_gap))
            y = start_y + (row * (container_height + config.container_gap))
            
            layouts.append(ContainerLayout(
                x=x, y=y, width=container_width, height=container_height,
                container_id=container_id, layout_index=i
            ))
        
        return layouts
    
    def _layout_penta_pyramid(
        self,
        config: LayoutConfiguration,
        container_ids: List[str]
    ) -> List[ContainerLayout]:
        """Layout for five containers - 2x2 grid on top, 1 centered below"""
        
        available_width = config.canvas_width - (2 * config.canvas_padding)
        available_height = config.canvas_height - (2 * config.canvas_padding)
        
        # Calculate dimensions: 3 rows with middle row having 2x2 containers
        row_height = (available_height - (2 * config.container_gap)) // 3
        container_width = (available_width - config.container_gap) // 2
        
        # Apply aspect ratio for square containers
        if config.aspect_ratio == 1.0:
            size = min(container_width, row_height)
            container_width = container_height = size
        else:
            container_height = row_height
        
        # Apply size constraints
        container_width = max(config.min_container_size, min(config.max_container_size, container_width))
        container_height = max(config.min_container_size, min(config.max_container_size, container_height))
        
        layouts = []
        
        # Top 2x2 grid: 4 containers
        grid_width = (2 * container_width) + config.container_gap
        grid_start_x = (config.canvas_width - grid_width) // 2
        top_y = config.canvas_padding
        
        for i in range(4):
            row = i // 2
            col = i % 2
            
            x = grid_start_x + (col * (container_width + config.container_gap))
            y = top_y + (row * (container_height + config.container_gap))
            
            layouts.append(ContainerLayout(
                x=x, y=y, width=container_width, height=container_height,
                container_id=container_ids[i], layout_index=i
            ))
        
        # Bottom centered container
        bottom_x = (config.canvas_width - container_width) // 2
        bottom_y = top_y + (2 * container_height) + (2 * config.container_gap)
        
        layouts.append(ContainerLayout(
            x=bottom_x, y=bottom_y, width=container_width, height=container_height,
            container_id=container_ids[4], layout_index=4
        ))
        
        return layouts
    
    def _layout_multi_grid(
        self,
        container_count: int,
        config: LayoutConfiguration,
        container_ids: List[str]
    ) -> List[ContainerLayout]:
        """Layout for 6+ containers - dynamic grid with optimal aspect ratio"""
        
        # Calculate optimal grid dimensions
        grid_cols, grid_rows = self._calculate_optimal_grid(container_count)
        
        available_width = config.canvas_width - (2 * config.canvas_padding)
        available_height = config.canvas_height - (2 * config.canvas_padding)
        
        # Calculate container dimensions
        container_width = (available_width - ((grid_cols - 1) * config.container_gap)) // grid_cols
        container_height = (available_height - ((grid_rows - 1) * config.container_gap)) // grid_rows
        
        # Apply aspect ratio for square containers
        if config.aspect_ratio == 1.0:
            size = min(container_width, container_height)
            container_width = container_height = size
            
            # Center the grid
            grid_width = (grid_cols * container_width) + ((grid_cols - 1) * config.container_gap)
            grid_height = (grid_rows * container_height) + ((grid_rows - 1) * config.container_gap)
            start_x = (config.canvas_width - grid_width) // 2
            start_y = (config.canvas_height - grid_height) // 2
        else:
            start_x = config.canvas_padding
            start_y = config.canvas_padding
        
        # Apply size constraints
        container_width = max(config.min_container_size, min(config.max_container_size, container_width))
        container_height = max(config.min_container_size, min(config.max_container_size, container_height))
        
        layouts = []
        for i, container_id in enumerate(container_ids):
            if i >= container_count:
                break
                
            row = i // grid_cols
            col = i % grid_cols
            
            x = start_x + (col * (container_width + config.container_gap))
            y = start_y + (row * (container_height + config.container_gap))
            
            layouts.append(ContainerLayout(
                x=x, y=y, width=container_width, height=container_height,
                container_id=container_id, layout_index=i
            ))
        
        return layouts
    
    def _calculate_optimal_grid(self, container_count: int) -> Tuple[int, int]:
        """Calculate optimal grid dimensions for given container count"""
        
        if container_count <= 0:
            return (0, 0)
        
        # Find the grid dimensions that are closest to square
        best_ratio = float('inf')
        best_cols = best_rows = 1
        
        for cols in range(1, container_count + 1):
            rows = math.ceil(container_count / cols)
            ratio = max(cols, rows) / min(cols, rows)
            
            if ratio < best_ratio:
                best_ratio = ratio
                best_cols = cols
                best_rows = rows
        
        return (best_cols, best_rows)
    
    def calculate_canvas_utilization(
        self,
        layouts: List[ContainerLayout],
        config: LayoutConfiguration
    ) -> Dict[str, float]:
        """Calculate canvas space utilization metrics"""
        
        if not layouts:
            return {
                "container_area": 0,
                "canvas_area": config.canvas_width * config.canvas_height,
                "utilization_percentage": 0.0,
                "empty_space": config.canvas_width * config.canvas_height
            }
        
        # Calculate total container area
        total_container_area = sum(layout.width * layout.height for layout in layouts)
        
        # Calculate canvas area
        canvas_area = config.canvas_width * config.canvas_height
        
        # Calculate utilization percentage
        utilization = (total_container_area / canvas_area) * 100 if canvas_area > 0 else 0
        
        return {
            "container_area": total_container_area,
            "canvas_area": canvas_area,
            "utilization_percentage": round(utilization, 2),
            "empty_space": canvas_area - total_container_area,
            "container_count": len(layouts)
        }
    
    def validate_layout(
        self,
        layouts: List[ContainerLayout],
        config: LayoutConfiguration
    ) -> Dict[str, Any]:
        """Validate that layout doesn't have overlaps or out-of-bounds containers"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check each container
        for i, layout in enumerate(layouts):
            # Check bounds
            if (layout.x < 0 or layout.y < 0 or 
                layout.x + layout.width > config.canvas_width or
                layout.y + layout.height > config.canvas_height):
                validation_result["valid"] = False
                validation_result["errors"].append(
                    f"Container {layout.container_id} is out of canvas bounds"
                )
            
            # Check minimum size
            if layout.width < config.min_container_size or layout.height < config.min_container_size:
                validation_result["warnings"].append(
                    f"Container {layout.container_id} is smaller than minimum size"
                )
            
            # Check for overlaps with other containers
            for j, other_layout in enumerate(layouts[i+1:], i+1):
                if self._containers_overlap(layout, other_layout):
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Containers {layout.container_id} and {other_layout.container_id} overlap"
                    )
        
        return validation_result
    
    def _containers_overlap(self, layout1: ContainerLayout, layout2: ContainerLayout) -> bool:
        """Check if two container layouts overlap"""
        return not (
            layout1.x + layout1.width <= layout2.x or
            layout2.x + layout2.width <= layout1.x or
            layout1.y + layout1.height <= layout2.y or
            layout2.y + layout2.height <= layout1.y
        )
    
    def find_available_position(
        self,
        existing_containers: List[Dict[str, Any]], 
        config: LayoutConfiguration,
        container_id: str,
        preferred_width: int = None,
        preferred_height: int = None
    ) -> Optional[ContainerLayout]:
        """Find an available position for a single container given existing containers"""
        
        # Use default size if not specified
        if preferred_width is None:
            preferred_width = min(200, (config.canvas_width - 2 * config.canvas_padding) // 3)
        if preferred_height is None:
            preferred_height = min(150, (config.canvas_height - 2 * config.canvas_padding) // 3)
        
        # Apply size constraints
        width = max(config.min_container_size, min(config.max_container_size, preferred_width))
        height = max(config.min_container_size, min(config.max_container_size, preferred_height))
        
        # Try different positions in a grid pattern
        step_x = width + config.container_gap
        step_y = height + config.container_gap
        
        for y in range(config.canvas_padding, config.canvas_height - height, step_y):
            for x in range(config.canvas_padding, config.canvas_width - width, step_x):
                # Check if this position conflicts with existing containers
                conflicts = False
                for existing in existing_containers:
                    if self._positions_overlap(
                        x, y, width, height,
                        existing.get('x', 0), existing.get('y', 0),
                        existing.get('width', 0), existing.get('height', 0)
                    ):
                        conflicts = True
                        break
                
                if not conflicts:
                    return ContainerLayout(
                        x=x, y=y, width=width, height=height,
                        container_id=container_id, layout_index=0
                    )
        
        return None  # No available position found
    
    def _positions_overlap(self, x1: int, y1: int, w1: int, h1: int, x2: int, y2: int, w2: int, h2: int) -> bool:
        """Check if two rectangular positions overlap"""
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

    def get_layout_recommendations(
        self,
        container_count: int,
        config: LayoutConfiguration
    ) -> Dict[str, Any]:
        """Get recommendations for optimal layout configuration"""
        
        recommendations = {
            "container_count": container_count,
            "recommended_pattern": "",
            "canvas_efficiency": "",
            "suggestions": []
        }
        
        # Pattern recommendations
        if container_count == 1:
            recommendations["recommended_pattern"] = "single_centered"
            recommendations["canvas_efficiency"] = "excellent"
        elif container_count <= 4:
            recommendations["recommended_pattern"] = f"{['', 'single', 'dual', 'triple', 'quad'][container_count]}_pattern"
            recommendations["canvas_efficiency"] = "very_good"
        elif container_count <= 9:
            recommendations["recommended_pattern"] = "grid_layout"
            recommendations["canvas_efficiency"] = "good"
        else:
            recommendations["recommended_pattern"] = "multi_grid"
            recommendations["canvas_efficiency"] = "moderate"
            recommendations["suggestions"].append(
                f"Consider using multiple canvases for {container_count} containers"
            )
        
        # Canvas size recommendations
        canvas_area = config.canvas_width * config.canvas_height
        estimated_container_area = container_count * (config.min_container_size ** 2)
        
        if estimated_container_area > canvas_area * 0.8:
            recommendations["suggestions"].append(
                "Consider increasing canvas size for better spacing"
            )
        
        if config.container_gap < 5:
            recommendations["suggestions"].append(
                "Consider increasing container gap for better visual separation"
            )
        
        return recommendations


# Utility function for easy access
def create_layout_engine() -> AutoLayoutEngine:
    """Create and return a new AutoLayoutEngine instance"""
    return AutoLayoutEngine() 