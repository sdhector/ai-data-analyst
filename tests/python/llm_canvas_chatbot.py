"""
LLM Canvas Chatbot

A terminal-based chatbot interface that uses LLM function calling to control
the canvas through natural language commands. Follows the core AI engine architecture.
"""

import json
import math
import os
import sys
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import openai
from openai import OpenAI

# Add the project root to the path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from canvas_controller import CanvasController

# Load environment variables
load_dotenv()

class CanvasLLMClient:
    """
    LLM client specifically configured for canvas control operations
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """
        Initialize the LLM client for canvas operations
        
        Args:
            api_key: OpenAI API key
            model: Model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # System message for canvas control
        self.system_message = """You are a Canvas Control Assistant. You help users manage containers on a visual canvas through function calls.

Available capabilities:
- Create containers at specific positions and sizes
- Delete containers by ID
- Modify existing containers (position and size)
- View current canvas state
- Clear all containers
- Take screenshots
- Edit canvas size
- Control canvas behavior settings (auto-adjustment and overlap prevention)

Canvas specifications:
- Default size: 800x600 pixels (customizable)
- Coordinate system: Top-left origin (0,0)
- Position values: x, y coordinates in pixels
- Size values: width, height in pixels

Canvas behavior controls:
- Auto-adjustment: Containers automatically fit within canvas bounds (always enabled for safety)
- Overlap prevention: Containers can overlap with existing ones (disabled by default, can be controlled)
- Use get_canvas_settings to check current behavior settings

CRITICAL EXECUTION RULES:
1. NEVER DEVIATE from the user's explicit request without asking for clarification first
2. If you encounter ANY reason to change the plan or approach, STOP and ask the user for clarification
3. Follow the user's instructions exactly as specified - do not make assumptions or modifications
4. NEVER CHANGE THE CANVAS SIZE without explicitly asking the user for permission first
5. MAXIMIZE CANVAS SPACE USAGE: Always calculate optimal container sizes to make the best use of available canvas space
6. When creating multiple containers, distribute them efficiently across the canvas to utilize the full area
7. Calculate container dimensions based on canvas size and number of containers to maximize space utilization

When users request canvas operations:
1. ALWAYS start by checking current canvas state with get_canvas_state() and get_canvas_size() to understand available space
2. Container operations (create, modify, delete) now AUTOMATICALLY use optimal layout - no manual calculation needed
3. Simply call the container functions with required parameters - optimization happens automatically
4. The system will automatically maximize space usage and minimize size differences for all containers
5. Always explain what the optimization accomplished and why specific dimensions were chosen
6. Provide feedback on the optimization results including space utilization and layout metrics
7. If a function fails, check the error message and try alternative approaches
8. If placement fails due to safety constraints, explain why and ask user for clarification on how to proceed
9. Always provide a final text response summarizing what was accomplished
10. If you need to deviate from the user's request for any reason, ask for permission first

Space Optimization Guidelines:
- Container functions now AUTOMATICALLY optimize layout - no manual optimization calls needed
- ALL container operations (create, modify, delete) automatically include optimization for the entire canvas
- The system automatically calculates optimal sizes based on available canvas dimensions
- Grid layouts and proportional sizing are automatically applied for maximum space efficiency
- Minimal gaps between containers are automatically calculated to maximize usage
- Aspect ratios are automatically optimized to work well with canvas dimensions
- All containers automatically get uniform sizing for visual consistency
- Single container operations automatically consider and optimize ALL containers on canvas

Important guidelines:
- Container IDs must match exactly what exists on canvas (check with get_canvas_state first)
- Containers may be automatically repositioned to prevent overlaps (safety feature)
- Containers may be resized to fit canvas bounds (safety feature)
- Always acknowledge when automatic adjustments occur
- If a container cannot be placed due to safety constraints, ask user how to proceed rather than making assumptions

Be helpful, clear, precise, and always confirm successful operations with a final summary. NEVER change the user's plan without explicit permission."""
    
    def get_function_schemas(self) -> List[Dict]:
        """Get function schemas for canvas operations"""
        return [
            {
                "name": "create_container",
                "description": "Create a new container on the canvas using automatic optimal layout. Position and size are automatically calculated to maximize space usage and minimize size differences.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "Unique identifier for the container. Must be unique - check existing containers with get_canvas_state() if needed."
                        }
                    },
                    "required": ["container_id"]
                }
            },
            {
                "name": "delete_container",
                "description": "Delete a container from the canvas. IMPORTANT: Always call get_canvas_state() first to check existing container IDs before using this function.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID of the container to delete. Must match exactly an existing container ID from get_canvas_state()."
                        }
                    },
                    "required": ["container_id"]
                }
            },
            {
                "name": "modify_container",
                "description": "Modify an existing container using automatic optimal layout. All containers on canvas are re-optimized for best space usage and size uniformity. IMPORTANT: Always call get_canvas_state() first to check existing container IDs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID of the container to modify. Must match exactly an existing container ID from get_canvas_state()."
                        }
                    },
                    "required": ["container_id"]
                }
            },
            {
                "name": "get_canvas_state",
                "description": "Get the current state of the canvas including all containers. ESSENTIAL: Call this function first before modifying or deleting containers to get accurate container IDs and positions.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "clear_canvas",
                "description": "Remove all containers from the canvas",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "take_screenshot",
                "description": "Take a screenshot of the current canvas state",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Optional filename for the screenshot"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_canvas_size",
                "description": "Get the current canvas dimensions",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "edit_canvas_size",
                "description": "Change the canvas dimensions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "width": {
                            "type": "integer",
                            "description": "New canvas width in pixels"
                        },
                        "height": {
                            "type": "integer",
                            "description": "New canvas height in pixels"
                        }
                    },
                    "required": ["width", "height"]
                }
            },
            {
                "name": "create_pie_chart",
                "description": "Create a pie chart visualization in a container with sample data or custom data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID of the container to place the pie chart in. Must be an existing container."
                        },
                        "title": {
                            "type": "string",
                            "description": "Title for the pie chart",
                            "default": "Pie Chart"
                        },
                        "use_sample_data": {
                            "type": "boolean",
                            "description": "Whether to use default sample data (Technology, Healthcare, Finance, Education, Retail)",
                            "default": True
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Custom labels for pie chart segments (only used if use_sample_data is false)"
                        },
                        "values": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Custom values for pie chart segments (only used if use_sample_data is false)"
                        }
                    },
                    "required": ["container_id"]
                }
            },
            {
                "name": "get_canvas_settings",
                "description": "Get current canvas behavior settings (auto-adjust and overlap prevention status)",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "check_container_content",
                "description": "Check what content is in a specific container (useful for verifying pie charts or other content)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID of the container to check"
                        }
                    },
                    "required": ["container_id"]
                }
            },
            {
                "name": "calculate_optimal_layout",
                "description": "Calculate optimal sizes and positions for containers to minimize empty space and size differences. Use this before creating or modifying multiple containers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "containers": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "Container identifier"
                                    },
                                    "status": {
                                        "type": "string",
                                        "enum": ["existing", "new"],
                                        "description": "Whether this container already exists on canvas or is new"
                                    },
                                    "current_width": {
                                        "type": "integer",
                                        "description": "Current width if existing container, can be omitted for new containers"
                                    },
                                    "current_height": {
                                        "type": "integer",
                                        "description": "Current height if existing container, can be omitted for new containers"
                                    },
                                    "current_x": {
                                        "type": "integer",
                                        "description": "Current x position if existing container, can be omitted for new containers"
                                    },
                                    "current_y": {
                                        "type": "integer",
                                        "description": "Current y position if existing container, can be omitted for new containers"
                                    }
                                },
                                "required": ["id", "status"]
                            },
                            "description": "List of containers to optimize (both existing and new)"
                        },
                        "canvas_width": {
                            "type": "integer",
                            "description": "Canvas width in pixels"
                        },
                        "canvas_height": {
                            "type": "integer",
                            "description": "Canvas height in pixels"
                        }
                    },
                    "required": ["containers", "canvas_width", "canvas_height"]
                }
            },
            {
                "name": "check_identifier_availability",
                "description": "Check if an identifier is available for use and get suggestions if it conflicts with existing elements. Use this before creating containers or charts to avoid conflicts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "proposed_identifier": {
                            "type": "string",
                            "description": "The identifier you want to check for availability"
                        },
                        "element_type": {
                            "type": "string",
                            "enum": ["container", "chart", "element"],
                            "description": "Type of element the identifier will be used for",
                            "default": "element"
                        }
                    },
                    "required": ["proposed_identifier"]
                }
            }
        ]
    
    def chat_completion(self, messages: List[Dict], functions: List[Dict] = None) -> Dict[str, Any]:
        """
        Create a chat completion with function calling
        
        Args:
            messages: Conversation messages
            functions: Available functions
            
        Returns:
            LLM response
        """
        try:
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,  # Lower temperature for more consistent function calling
                "max_tokens": 1000   # Ensure we don't hit token limits
            }
            
            if functions:
                # Convert functions to tools format for better compatibility
                tools = [{"type": "function", "function": func} for func in functions]
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            response = self.client.chat.completions.create(**request_params)
            choice = response.choices[0]
            
            return {
                "status": "success",
                "message": choice.message,
                "content": choice.message.content,
                "function_call": getattr(choice.message, 'function_call', None),
                "tool_calls": getattr(choice.message, 'tool_calls', None),
                "finish_reason": choice.finish_reason
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

class CanvasFunctionExecutor:
    """
    Function executor that bridges LLM function calls to canvas controller operations
    """
    
    def __init__(self, canvas_controller: CanvasController, chatbot_instance):
        """
        Initialize with a canvas controller instance
        
        Args:
            canvas_controller: CanvasController instance
            chatbot_instance: Reference to chatbot for accessing settings
        """
        self.controller = canvas_controller
        self.chatbot = chatbot_instance
    
    def _get_all_used_identifiers(self):
        """
        Get all currently used identifiers across all elements on the canvas
        
        Returns:
            Dict with categorized identifiers and summary
        """
        try:
            # Get container identifiers
            current_state = self.controller.get_current_state()
            container_ids = [c['id'] for c in current_state.get('containers', [])]
            
            # Get chart identifiers (from containers with chart content)
            chart_ids = []
            for container in current_state.get('containers', []):
                container_id = container['id']
                try:
                    # Check if container has chart content
                    chart_info = self.controller.driver.execute_script(f"""
                        const container = document.getElementById('{container_id}');
                        if (!container) return null;
                        
                        const contentType = container.getAttribute('data-content-type');
                        const chartTitle = container.getAttribute('data-chart-title');
                        
                        if (contentType === 'pie-chart' && chartTitle) {{
                            return {{
                                chartId: chartTitle.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase(),
                                chartTitle: chartTitle,
                                containerId: '{container_id}'
                            }};
                        }}
                        return null;
                    """)
                    
                    if chart_info and chart_info.get('chartId'):
                        chart_ids.append(chart_info['chartId'])
                        
                except Exception:
                    # Skip if there's an error checking this container
                    continue
            
            # Combine all identifiers
            all_ids = container_ids + chart_ids
            
            return {
                "container_ids": container_ids,
                "chart_ids": chart_ids,
                "all_identifiers": all_ids,
                "total_count": len(all_ids),
                "summary": f"Found {len(container_ids)} container(s) and {len(chart_ids)} chart(s) - Total: {len(all_ids)} identifier(s)"
            }
            
        except Exception as e:
            print(f"⚠️ Warning: Error getting used identifiers: {e}")
            return {
                "container_ids": [],
                "chart_ids": [],
                "all_identifiers": [],
                "total_count": 0,
                "summary": "Error retrieving identifiers"
            }
    
    def _validate_identifier_uniqueness(self, proposed_id, element_type="element"):
        """
        Validate that a proposed identifier is unique across all canvas elements
        
        Args:
            proposed_id: The identifier to validate
            element_type: Type of element (for error messages)
            
        Returns:
            Dict with validation result and suggestions
        """
        if not proposed_id or not isinstance(proposed_id, str):
            return {
                "is_valid": False,
                "error": f"Invalid {element_type} identifier: must be a non-empty string",
                "proposed_id": proposed_id,
                "suggestions": ["Use alphanumeric characters and underscores", "Example: 'chart_1', 'container_main', 'sales_data'"]
            }
        
        # Clean the identifier (remove special characters, convert to lowercase)
        clean_id = proposed_id.strip().replace(' ', '_').lower()
        
        # Get all used identifiers
        used_identifiers = self._get_all_used_identifiers()
        all_used_ids = used_identifiers["all_identifiers"]
        
        # Check for exact match
        if clean_id in all_used_ids:
            return {
                "is_valid": False,
                "error": f"{element_type.capitalize()} identifier '{clean_id}' is already in use",
                "proposed_id": proposed_id,
                "clean_id": clean_id,
                "conflicting_with": clean_id,
                "used_identifiers": used_identifiers,
                "suggestions": self._generate_alternative_identifiers(clean_id, all_used_ids)
            }
        
        # Check for similar identifiers (potential confusion)
        similar_ids = [uid for uid in all_used_ids if uid.startswith(clean_id) or clean_id.startswith(uid)]
        
        if similar_ids:
            return {
                "is_valid": True,  # Valid but with warning
                "warning": f"Identifier '{clean_id}' is similar to existing: {', '.join(similar_ids)}",
                "proposed_id": proposed_id,
                "clean_id": clean_id,
                "similar_identifiers": similar_ids,
                "used_identifiers": used_identifiers
            }
        
        # Identifier is unique
        return {
            "is_valid": True,
            "proposed_id": proposed_id,
            "clean_id": clean_id,
            "message": f"Identifier '{clean_id}' is available",
            "used_identifiers": used_identifiers
        }
    
    def _generate_alternative_identifiers(self, base_id, used_ids, max_suggestions=5):
        """
        Generate alternative identifier suggestions when there's a conflict
        
        Args:
            base_id: The conflicting base identifier
            used_ids: List of already used identifiers
            max_suggestions: Maximum number of suggestions to generate
            
        Returns:
            List of alternative identifier suggestions
        """
        suggestions = []
        
        # Try numbered variations
        for i in range(1, max_suggestions + 1):
            candidate = f"{base_id}_{i}"
            if candidate not in used_ids:
                suggestions.append(candidate)
        
        # Try common suffixes if we need more suggestions
        suffixes = ["new", "alt", "v2", "main", "primary"]
        for suffix in suffixes:
            if len(suggestions) >= max_suggestions:
                break
            candidate = f"{base_id}_{suffix}"
            if candidate not in used_ids:
                suggestions.append(candidate)
        
        # Try prefixes if still need more
        prefixes = ["new", "my", "temp", "draft"]
        for prefix in prefixes:
            if len(suggestions) >= max_suggestions:
                break
            candidate = f"{prefix}_{base_id}"
            if candidate not in used_ids:
                suggestions.append(candidate)
        
        return suggestions[:max_suggestions]
    
    def _create_pie_chart_html(self, title, labels, values):
        """
        Create HTML content for a pie chart using CSS and SVG that fits within container bounds
        
        Args:
            title: Chart title
            labels: List of labels for pie segments
            values: List of values for pie segments
            
        Returns:
            HTML string for the pie chart
        """
        # Calculate percentages and cumulative angles
        total = sum(values)
        percentages = [(value / total) * 100 for value in values]
        
        # Colors for pie segments
        colors = [
            "#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe",
            "#fa709a", "#fee140", "#30cfd0", "#a8edea", "#fed6e3"
        ]
        
        # Create SVG pie chart with responsive sizing that adapts to container
        svg_content = f'<svg viewBox="0 0 200 200" style="width: 100%; height: auto; max-width: 200px; max-height: 200px;">'
        
        # Calculate pie segments
        current_angle = 0
        for i, (label, value, percentage) in enumerate(zip(labels, values, percentages)):
            color = colors[i % len(colors)]
            
            # Calculate arc parameters
            angle = (percentage / 100) * 360
            end_angle = current_angle + angle
            
            # Convert to radians for calculation
            start_rad = (current_angle * 3.14159) / 180
            end_rad = (end_angle * 3.14159) / 180
            
            # Calculate arc coordinates
            x1 = 100 + 80 * math.cos(start_rad)
            y1 = 100 + 80 * math.sin(start_rad)
            x2 = 100 + 80 * math.cos(end_rad)
            y2 = 100 + 80 * math.sin(end_rad)
            
            # Large arc flag
            large_arc = 1 if angle > 180 else 0
            
            # Create path for pie segment
            path = f'M 100 100 L {x1} {y1} A 80 80 0 {large_arc} 1 {x2} {y2} Z'
            
            svg_content += f'<path d="{path}" fill="{color}" stroke="white" stroke-width="2" opacity="0.8">'
            svg_content += f'<title>{label}: {value} ({percentage:.1f}%)</title>'
            svg_content += '</path>'
            
            current_angle = end_angle
        
        svg_content += '</svg>'
        
        # Create responsive legend that adapts to container
        legend_html = f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 6px; margin-top: 10px; font-size: 12px; width: 100%; max-height: 80px; overflow-y: auto;">'
        for i, (label, value, percentage) in enumerate(zip(labels, values, percentages)):
            color = colors[i % len(colors)]
            # Truncate long labels to fit container
            display_label = label[:15] + "..." if len(label) > 15 else label
            legend_html += f'''
                <div style="display: flex; align-items: center; gap: 4px; min-width: 0;">
                    <div style="width: 12px; height: 12px; background-color: {color}; border-radius: 2px; flex-shrink: 0;"></div>
                    <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{label}: {percentage:.1f}%">{display_label}: {percentage:.1f}%</span>
                </div>
            '''
        legend_html += '</div>'
        
        # Create container-responsive chart layout that stays within bounds
        chart_html = f'''
            <div style="
                width: 100%;
                height: 100%;
                padding: 15px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                font-family: Arial, sans-serif;
            ">
                {f'<h3 style="margin: 0 0 10px 0; font-size: 16px; color: #333; text-align: center; width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{title}">{title}</h3>' if title else ''}
                <div style="flex: 1; display: flex; align-items: center; justify-content: center; width: 100%; min-height: 0;">
                    {svg_content}
                </div>
                {legend_html}
            </div>
        '''
        
        # Clean up the HTML for safe injection
        # Remove newlines and normalize whitespace, but don't escape quotes since we're using arguments
        clean_html = ' '.join(chart_html.split())
        return clean_html
    
    def _calculate_optimal_container_layout(self, containers, canvas_width, canvas_height):
        """
        Calculate optimal sizes and positions for containers to minimize empty space and size differences
        
        Args:
            containers: List of container specifications
            canvas_width: Canvas width in pixels
            canvas_height: Canvas height in pixels
            
        Returns:
            Dict with optimized layout recommendations
        """
        import math
        
        num_containers = len(containers)
        if num_containers == 0:
            return {
                "summary": "No containers to optimize",
                "containers": [],
                "space_utilization": 100.0,
                "layout_type": "empty"
            }
        
        # Calculate optimal grid dimensions
        # Try to create a layout that's as close to square as possible
        cols = math.ceil(math.sqrt(num_containers))
        rows = math.ceil(num_containers / cols)
        
        # Add small padding between containers (2% of canvas size)
        padding_x = max(10, int(canvas_width * 0.02))
        padding_y = max(10, int(canvas_height * 0.02))
        
        # Calculate available space for containers
        available_width = canvas_width - (padding_x * (cols + 1))
        available_height = canvas_height - (padding_y * (rows + 1))
        
        # Calculate optimal container size
        container_width = max(50, int(available_width / cols))
        container_height = max(50, int(available_height / rows))
        
        # Generate optimized layout
        optimized_containers = []
        container_index = 0
        
        for row in range(rows):
            for col in range(cols):
                if container_index >= num_containers:
                    break
                    
                container = containers[container_index]
                
                # Calculate position
                x = padding_x + col * (container_width + padding_x)
                y = padding_y + row * (container_height + padding_y)
                
                # Ensure containers fit within canvas bounds
                x = min(x, canvas_width - container_width - padding_x)
                y = min(y, canvas_height - container_height - padding_y)
                
                optimized_container = {
                    "id": container["id"],
                    "status": container["status"],
                    "recommended_x": x,
                    "recommended_y": y,
                    "recommended_width": container_width,
                    "recommended_height": container_height,
                    "grid_position": {"row": row, "col": col}
                }
                
                # Include current dimensions if existing container
                if container["status"] == "existing":
                    optimized_container["current_x"] = container.get("current_x")
                    optimized_container["current_y"] = container.get("current_y")
                    optimized_container["current_width"] = container.get("current_width")
                    optimized_container["current_height"] = container.get("current_height")
                    
                    # Calculate change metrics
                    if all(key in container for key in ["current_width", "current_height"]):
                        size_change = abs(container_width * container_height - 
                                        container["current_width"] * container["current_height"])
                        optimized_container["size_change_pixels"] = size_change
                
                optimized_containers.append(optimized_container)
                container_index += 1
        
        # Calculate space utilization
        total_container_area = num_containers * container_width * container_height
        canvas_area = canvas_width * canvas_height
        space_utilization = (total_container_area / canvas_area) * 100
        
        # Calculate size uniformity (all containers will have same size)
        size_uniformity = 100.0  # Perfect uniformity since all containers are same size
        
        # Generate layout summary
        layout_summary = {
            "summary": f"Optimized layout for {num_containers} containers in {cols}x{rows} grid",
            "layout_type": f"{cols}x{rows}_grid",
            "containers": optimized_containers,
            "metrics": {
                "space_utilization_percent": round(space_utilization, 1),
                "size_uniformity_percent": size_uniformity,
                "container_size": f"{container_width}x{container_height}",
                "grid_dimensions": f"{cols}x{rows}",
                "padding": f"{padding_x}x{padding_y}"
            },
            "canvas_info": {
                "canvas_size": f"{canvas_width}x{canvas_height}",
                "available_space": f"{available_width}x{available_height}",
                "total_containers": num_containers
            },
            "recommendations": [
                f"Use {container_width}x{container_height} size for all containers",
                f"Arrange in {cols}x{rows} grid pattern",
                f"Space utilization: {round(space_utilization, 1)}%",
                "All containers will have uniform size for visual consistency"
            ]
        }
        
        return layout_summary
    
    def _get_all_containers_for_optimization(self, new_container_id=None, exclude_container_id=None):
        """
        Get all containers (existing + new) for optimization calculation
        
        Args:
            new_container_id: ID of new container to include
            exclude_container_id: ID of container to exclude (for deletion)
            
        Returns:
            List of container specifications for optimization
        """
        # Get current canvas state
        current_state = self.controller.get_current_state()
        existing_containers = current_state.get('containers', [])
        
        containers_for_optimization = []
        
        # Add existing containers (except excluded ones)
        for container in existing_containers:
            if exclude_container_id and container['id'] == exclude_container_id:
                continue  # Skip container being deleted
                
            containers_for_optimization.append({
                "id": container['id'],
                "status": "existing",
                "current_x": container['x'],
                "current_y": container['y'],
                "current_width": container['width'],
                "current_height": container['height']
            })
        
        # Add new container if specified
        if new_container_id:
            containers_for_optimization.append({
                "id": new_container_id,
                "status": "new"
            })
        
        return containers_for_optimization
    
    def _apply_optimized_layout(self, optimization_result, target_container_id=None):
        """
        Apply the optimized layout to all containers
        
        Args:
            optimization_result: Result from _calculate_optimal_container_layout
            target_container_id: If specified, only return info for this container
            
        Returns:
            Dict with operation results and optimization info
        """
        if not optimization_result or 'containers' not in optimization_result:
            return {
                "success": False,
                "error": "Invalid optimization result",
                "optimization_used": False
            }
        
        optimized_containers = optimization_result['containers']
        results = []
        target_result = None
        
        for opt_container in optimized_containers:
            container_id = opt_container['id']
            
            # Apply the optimized dimensions
            if opt_container['status'] == 'existing':
                # Modify existing container
                success = self.controller.modify_container(
                    container_id=container_id,
                    x=opt_container['recommended_x'],
                    y=opt_container['recommended_y'],
                    width=opt_container['recommended_width'],
                    height=opt_container['recommended_height'],
                    auto_adjust=self.chatbot.auto_adjust_enabled,
                    avoid_overlap=self.chatbot.overlap_prevention_enabled
                )
            else:
                # Create new container
                success = self.controller.create_container(
                    container_id=container_id,
                    x=opt_container['recommended_x'],
                    y=opt_container['recommended_y'],
                    width=opt_container['recommended_width'],
                    height=opt_container['recommended_height'],
                    auto_adjust=self.chatbot.auto_adjust_enabled,
                    avoid_overlap=self.chatbot.overlap_prevention_enabled
                )
            
            container_result = {
                "container_id": container_id,
                "success": success,
                "status": opt_container['status'],
                "optimized_position": (opt_container['recommended_x'], opt_container['recommended_y']),
                "optimized_size": (opt_container['recommended_width'], opt_container['recommended_height']),
                "grid_position": opt_container.get('grid_position', {})
            }
            
            # Add change information for existing containers
            if opt_container['status'] == 'existing':
                container_result["previous_position"] = (opt_container.get('current_x'), opt_container.get('current_y'))
                container_result["previous_size"] = (opt_container.get('current_width'), opt_container.get('current_height'))
                container_result["size_change_pixels"] = opt_container.get('size_change_pixels', 0)
            
            results.append(container_result)
            
            # Track target container result
            if target_container_id and container_id == target_container_id:
                target_result = container_result
        
        return {
            "success": True,
            "optimization_used": True,
            "optimization_result": optimization_result,
            "container_results": results,
            "target_container": target_result,
            "metrics": optimization_result.get('metrics', {}),
            "layout_summary": optimization_result.get('summary', ''),
            "recommendations": optimization_result.get('recommendations', [])
        }
    
    def _refresh_pie_chart_in_container(self, container_id):
        """
        Refresh a pie chart in a container (chart will auto-adapt to container size)
        
        Args:
            container_id: ID of the container
            
        Returns:
            bool: Success status
        """
        try:
            # Check if container has a pie chart
            has_pie_chart = self.controller.driver.execute_script(f"""
                const container = document.getElementById('{container_id}');
                return container && container.getAttribute('data-content-type') === 'pie-chart';
            """)
            
            if not has_pie_chart:
                return True  # No pie chart to refresh
            
            # Get existing chart data
            chart_data = self.controller.driver.execute_script(f"""
                const container = document.getElementById('{container_id}');
                if (!container) return null;
                
                return {{
                    title: container.getAttribute('data-chart-title') || 'Pie Chart',
                    contentType: container.getAttribute('data-content-type')
                }};
            """)
            
            if not chart_data or chart_data['contentType'] != 'pie-chart':
                return True  # No pie chart data found
            
            # For now, we'll use sample data since we don't store the original data
            # In a production system, you'd want to store the chart data
            labels = ["Technology", "Healthcare", "Finance", "Education", "Retail"]
            values = [35, 25, 20, 12, 8]
            title = chart_data['title']
            
            # Recreate the chart (will auto-adapt to container dimensions)
            chart_html = self._create_pie_chart_html(title, labels, values)
            
            # Update the container content using bounds enforcement
            success = self.controller.driver.execute_script("""
                const container = document.getElementById(arguments[0]);
                if (!container) {
                    console.error('Container not found for refresh:', arguments[0]);
                    return false;
                }
                
                try {
                    // ROBUST BOUNDS ENFORCEMENT FOR REFRESH
                    
                    // Store original container properties to prevent movement
                    const originalLeft = container.style.left;
                    const originalTop = container.style.top;
                    const originalWidth = container.style.width;
                    const originalHeight = container.style.height;
                    
                    // Enforce strict container positioning
                    container.style.position = 'absolute';
                    container.style.overflow = 'hidden';
                    container.style.contain = 'layout style paint';
                    
                    // Clear existing content
                    container.innerHTML = '';
                    
                    // Create bounds-enforcing wrapper
                    const wrapper = document.createElement('div');
                    wrapper.style.cssText = `
                        position: relative;
                        width: 100%;
                        height: 100%;
                        overflow: hidden;
                        box-sizing: border-box;
                        margin: 0;
                        padding: 0;
                        contain: layout style paint;
                    `;
                    
                    // Parse and add content with bounds enforcement
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = arguments[1];
                    
                    while (tempDiv.firstChild) {
                        const child = tempDiv.firstChild;
                        
                        // Enforce bounds on child elements
                        if (child.nodeType === Node.ELEMENT_NODE) {
                            child.style.position = 'relative';
                            child.style.maxWidth = '100%';
                            child.style.maxHeight = '100%';
                            child.style.overflow = 'hidden';
                            child.style.contain = 'layout style paint';
                        }
                        
                        wrapper.appendChild(child);
                    }
                    
                    container.appendChild(wrapper);
                    
                    // Re-lock container position and size
                    container.style.left = originalLeft;
                    container.style.top = originalTop;
                    container.style.width = originalWidth;
                    container.style.height = originalHeight;
                    
                    console.log('Pie chart refreshed with bounds enforcement:', arguments[0]);
                    return true;
                    
                } catch (error) {
                    console.error('Error refreshing pie chart with bounds enforcement:', error);
                    return false;
                }
            """, container_id, chart_html)
            
            return success
            
        except Exception as e:
            print(f"⚠️ Warning: Failed to refresh pie chart in container '{container_id}': {e}")
            return False
    
    def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call on the canvas controller
        
        Args:
            function_name: Name of function to execute
            arguments: Function arguments
            
        Returns:
            Function execution result
        """
        print(f"🔧 EXECUTING: {function_name}({arguments})")
        
        try:
            if function_name == "create_container":
                try:
                    container_id = arguments["container_id"]
                    
                    # GUARDRAIL: Validate identifier uniqueness across all elements
                    validation_result = self._validate_identifier_uniqueness(container_id, "container")
                    
                    if not validation_result["is_valid"]:
                        used_info = validation_result["used_identifiers"]
                        error_msg = f"❌ {validation_result['error']}\n"
                        error_msg += f"📋 Currently used identifiers:\n"
                        error_msg += f"   🗂️ Containers: {', '.join(used_info['container_ids']) if used_info['container_ids'] else 'None'}\n"
                        error_msg += f"   📊 Charts: {', '.join(used_info['chart_ids']) if used_info['chart_ids'] else 'None'}\n"
                        error_msg += f"💡 Suggested alternatives: {', '.join(validation_result['suggestions'])}"
                        
                        return {
                            "status": "error",
                            "result": error_msg,
                            "validation_details": validation_result,
                            "function_name": function_name
                        }
                    
                    # Use the cleaned identifier
                    clean_container_id = validation_result["clean_id"]
                    
                    # Get canvas size for optimization
                    canvas_size = self.controller.get_canvas_size()
                    
                    # Get all containers for optimization (existing + new)
                    containers_for_optimization = self._get_all_containers_for_optimization(
                        new_container_id=clean_container_id
                    )
                    
                    # Calculate optimal layout
                    optimization_result = self._calculate_optimal_container_layout(
                        containers_for_optimization, 
                        canvas_size['width'], 
                        canvas_size['height']
                    )
                    
                    # Apply optimized layout
                    layout_application = self._apply_optimized_layout(
                        optimization_result, 
                        target_container_id=clean_container_id
                    )
                    
                    if layout_application["success"] and layout_application["target_container"]["success"]:
                        target_info = layout_application["target_container"]
                        metrics = layout_application["metrics"]
                        
                        # Add identifier validation info if ID was cleaned
                        id_info = f"'{clean_container_id}'"
                        if clean_container_id != container_id:
                            id_info += f" (cleaned from '{container_id}')"
                        
                        result_msg = f"✅ Container {id_info} created successfully using optimized layout:\n"
                        result_msg += f"   📍 Position: {target_info['optimized_position']}\n"
                        result_msg += f"   📏 Size: {target_info['optimized_size']}\n"
                        result_msg += f"   🎯 Grid position: Row {target_info['grid_position']['row']}, Col {target_info['grid_position']['col']}\n"
                        result_msg += f"   📊 Space utilization: {metrics['space_utilization_percent']}%\n"
                        result_msg += f"   🔧 Layout: {metrics['grid_dimensions']} grid with {metrics['container_size']} containers\n"
                        result_msg += f"   💡 Optimization: {layout_application['layout_summary']}"
                        
                        # Add information about other containers that were repositioned
                        repositioned_containers = [r for r in layout_application["container_results"] 
                                                 if r["container_id"] != clean_container_id and r["status"] == "existing"]
                        if repositioned_containers:
                            result_msg += f"\n   🔄 Repositioned {len(repositioned_containers)} existing container(s) for optimal layout"
                        
                        # Add identifier validation warning if applicable
                        if validation_result.get("warning"):
                            result_msg += f"\n   ⚠️ {validation_result['warning']}"
                        
                        return {
                            "status": "success",
                            "result": result_msg,
                            "optimization_used": True,
                            "optimization_details": layout_application,
                            "function_name": function_name
                        }
                    else:
                        error_msg = layout_application.get("error", "Unknown optimization error")
                        return {
                            "status": "error",
                            "result": f"Failed to create container '{clean_container_id}' with optimization: {error_msg}",
                            "function_name": function_name
                        }
                        
                except Exception as e:
                    return {
                        "status": "error",
                        "result": f"Error creating container '{arguments.get('container_id', 'unknown')}': {str(e)}",
                        "function_name": function_name
                    }
            
            elif function_name == "delete_container":
                try:
                    container_id = arguments["container_id"]
                    
                    # Check if container exists
                    current_state = self.controller.get_current_state()
                    existing_ids = [c['id'] for c in current_state.get('containers', [])]
                    if container_id not in existing_ids:
                        if existing_ids:
                            return {
                                "status": "error",
                                "result": f"Failed to delete container '{container_id}'. Container not found. Available containers: {', '.join(existing_ids)}.",
                                "function_name": function_name
                            }
                        else:
                            return {
                                "status": "error",
                                "result": f"Failed to delete container '{container_id}'. No containers exist on canvas.",
                                "function_name": function_name
                            }
                    
                    # First delete the container
                    delete_result = self.controller.delete_container(container_id)
                    
                    if not delete_result:
                        return {
                            "status": "error",
                            "result": f"Failed to delete container '{container_id}' from canvas.",
                            "function_name": function_name
                        }
                    
                    # Get remaining containers after deletion
                    remaining_state = self.controller.get_current_state()
                    remaining_containers = remaining_state.get('containers', [])
                    
                    if len(remaining_containers) == 0:
                        # No containers left, just report deletion
                        return {
                            "status": "success",
                            "result": f"✅ Container '{container_id}' deleted successfully. Canvas is now empty.",
                            "optimization_used": False,
                            "function_name": function_name
                        }
                    
                    # Re-optimize remaining containers
                    canvas_size = self.controller.get_canvas_size()
                    containers_for_optimization = self._get_all_containers_for_optimization()
                    
                    # Calculate optimal layout for remaining containers
                    optimization_result = self._calculate_optimal_container_layout(
                        containers_for_optimization, 
                        canvas_size['width'], 
                        canvas_size['height']
                    )
                    
                    # Apply optimized layout to remaining containers
                    layout_application = self._apply_optimized_layout(optimization_result)
                    
                    if layout_application["success"]:
                        metrics = layout_application["metrics"]
                        
                        result_msg = f"✅ Container '{container_id}' deleted successfully and remaining containers optimized:\n"
                        result_msg += f"   🗑️ Deleted: '{container_id}'\n"
                        result_msg += f"   📊 Remaining containers: {len(remaining_containers)}\n"
                        result_msg += f"   📊 Space utilization: {metrics['space_utilization_percent']}%\n"
                        result_msg += f"   🔧 New layout: {metrics['grid_dimensions']} grid with {metrics['container_size']} containers\n"
                        result_msg += f"   💡 Optimization: {layout_application['layout_summary']}"
                        
                        # Add information about repositioned containers
                        repositioned_containers = layout_application["container_results"]
                        if repositioned_containers:
                            result_msg += f"\n   🔄 Repositioned {len(repositioned_containers)} remaining container(s) for optimal layout"
                        
                        return {
                            "status": "success",
                            "result": result_msg,
                            "optimization_used": True,
                            "optimization_details": layout_application,
                            "function_name": function_name
                        }
                    else:
                        # Deletion succeeded but optimization failed
                        return {
                            "status": "success",
                            "result": f"✅ Container '{container_id}' deleted successfully, but failed to optimize remaining containers.",
                            "optimization_used": False,
                            "function_name": function_name
                        }
                        
                except Exception as e:
                    return {
                        "status": "error",
                        "result": f"Error deleting container '{arguments.get('container_id', 'unknown')}': {str(e)}",
                        "function_name": function_name
                    }
            
            elif function_name == "modify_container":
                try:
                    container_id = arguments["container_id"]
                    
                    # Check if container exists
                    current_state = self.controller.get_current_state()
                    existing_ids = [c['id'] for c in current_state.get('containers', [])]
                    if container_id not in existing_ids:
                        if existing_ids:
                            return {
                                "status": "error",
                                "result": f"Failed to modify container '{container_id}'. Container not found. Available containers: {', '.join(existing_ids)}.",
                                "function_name": function_name
                            }
                        else:
                            return {
                                "status": "error",
                                "result": f"Failed to modify container '{container_id}'. No containers exist on canvas.",
                                "function_name": function_name
                            }
                    
                    # Get canvas size for optimization
                    canvas_size = self.controller.get_canvas_size()
                    
                    # Get all containers for optimization (all existing, including the one being modified)
                    containers_for_optimization = self._get_all_containers_for_optimization()
                    
                    # Calculate optimal layout
                    optimization_result = self._calculate_optimal_container_layout(
                        containers_for_optimization, 
                        canvas_size['width'], 
                        canvas_size['height']
                    )
                    
                    # Apply optimized layout
                    layout_application = self._apply_optimized_layout(
                        optimization_result, 
                        target_container_id=container_id
                    )
                    
                    if layout_application["success"] and layout_application["target_container"]["success"]:
                        target_info = layout_application["target_container"]
                        metrics = layout_application["metrics"]
                        
                        result_msg = f"✅ Container '{container_id}' modified successfully using optimized layout:\n"
                        result_msg += f"   📍 New position: {target_info['optimized_position']}\n"
                        result_msg += f"   📏 New size: {target_info['optimized_size']}\n"
                        result_msg += f"   🎯 Grid position: Row {target_info['grid_position']['row']}, Col {target_info['grid_position']['col']}\n"
                        result_msg += f"   📊 Space utilization: {metrics['space_utilization_percent']}%\n"
                        result_msg += f"   🔧 Layout: {metrics['grid_dimensions']} grid with {metrics['container_size']} containers\n"
                        result_msg += f"   💡 Optimization: {layout_application['layout_summary']}"
                        
                        # Show previous vs new dimensions
                        if target_info.get("previous_position") and target_info.get("previous_size"):
                            result_msg += f"\n   📋 Previous: {target_info['previous_position']} size {target_info['previous_size']}"
                            if target_info.get("size_change_pixels", 0) > 0:
                                result_msg += f"\n   📏 Size change: {target_info['size_change_pixels']} pixels"
                        
                        # Add information about other containers that were repositioned
                        repositioned_containers = [r for r in layout_application["container_results"] 
                                                 if r["container_id"] != container_id and r["status"] == "existing"]
                        if repositioned_containers:
                            result_msg += f"\n   🔄 Repositioned {len(repositioned_containers)} other container(s) for optimal layout"
                        
                        # Refresh any pie charts in the modified container
                        pie_chart_refreshed = self._refresh_pie_chart_in_container(container_id)
                        if pie_chart_refreshed:
                            result_msg += "\n   🥧 Pie chart automatically adapted to new container dimensions"
                        
                        return {
                            "status": "success",
                            "result": result_msg,
                            "optimization_used": True,
                            "optimization_details": layout_application,
                            "function_name": function_name
                        }
                    else:
                        error_msg = layout_application.get("error", "Unknown optimization error")
                        return {
                            "status": "error",
                            "result": f"Failed to modify container '{container_id}' with optimization: {error_msg}",
                            "function_name": function_name
                        }
                        
                except Exception as e:
                    return {
                        "status": "error",
                        "result": f"Error modifying container '{arguments.get('container_id', 'unknown')}': {str(e)}",
                        "function_name": function_name
                    }
            
            elif function_name == "get_canvas_state":
                state = self.controller.get_current_state()
                
                # Format the state information for better LLM understanding
                containers = state.get('containers', [])
                if containers:
                    container_summary = []
                    for container in containers:
                        summary = f"'{container['id']}': position ({container['x']}, {container['y']}), size {container['width']}x{container['height']}"
                        container_summary.append(summary)
                    
                    formatted_result = {
                        "canvas_size": state.get('canvas_size', 'Unknown'),
                        "container_count": len(containers),
                        "containers": containers,
                        "summary": f"Canvas has {len(containers)} container(s): " + "; ".join(container_summary)
                    }
                else:
                    formatted_result = {
                        "canvas_size": state.get('canvas_size', 'Unknown'),
                        "container_count": 0,
                        "containers": [],
                        "summary": "Canvas is empty (no containers)"
                    }
                
                return {
                    "status": "success",
                    "result": formatted_result,
                    "function_name": function_name
                }
            
            elif function_name == "clear_canvas":
                result = self.controller.clear_canvas()
                return {
                    "status": "success" if result else "error",
                    "result": "Canvas cleared successfully" if result else "Failed to clear canvas",
                    "function_name": function_name
                }
            
            elif function_name == "take_screenshot":
                filename = arguments.get("filename")
                screenshot_path = self.controller.take_screenshot(filename)
                return {
                    "status": "success" if screenshot_path else "error",
                    "result": f"Screenshot saved: {screenshot_path}" if screenshot_path else "Failed to take screenshot",
                    "function_name": function_name
                }
            
            elif function_name == "get_canvas_size":
                size = self.controller.get_canvas_size()
                return {
                    "status": "success",
                    "result": f"Canvas size: {size['width']}x{size['height']} pixels",
                    "canvas_size": size,
                    "function_name": function_name
                }
            
            elif function_name == "edit_canvas_size":
                try:
                    # Use JavaScript to change canvas size
                    success = self.controller.driver.execute_script(f"""
                        const canvas = document.getElementById('canvas');
                        canvas.style.width = '{arguments['width']}px';
                        canvas.style.height = '{arguments['height']}px';
                        return true;
                    """)
                    return {
                        "status": "success" if success else "error",
                        "result": f"Canvas resized to {arguments['width']}x{arguments['height']} pixels" if success else "Failed to resize canvas",
                        "function_name": function_name
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "result": f"Error resizing canvas: {str(e)}",
                        "function_name": function_name
                    }
            
            
            elif function_name == "create_pie_chart":
                try:
                    container_id = arguments["container_id"]
                    title = arguments.get("title", "Pie Chart")
                    use_sample_data = arguments.get("use_sample_data", True)
                    
                    # GUARDRAIL: Validate chart title as identifier (if it will be used as ID)
                    import re
                    chart_id = re.sub(r'[^a-zA-Z0-9]', '_', title).lower() if title else "pie_chart"
                    chart_validation = self._validate_identifier_uniqueness(chart_id, "chart")
                    
                    # Note: We don't block chart creation for ID conflicts since charts are content within containers
                    # But we warn the LLM about potential confusion
                    chart_id_warning = None
                    if not chart_validation["is_valid"]:
                        chart_id_warning = f"⚠️ Chart identifier '{chart_id}' conflicts with existing elements. Consider using a different title."
                    elif chart_validation.get("warning"):
                        chart_id_warning = f"⚠️ {chart_validation['warning']}"
                    
                    # Check if container exists and get its dimensions
                    state = self.controller.get_current_state()
                    if not state or not state.get('containers'):
                        return {
                            "status": "error",
                            "result": f"No containers exist on canvas. Create a container first before adding a pie chart.",
                            "function_name": function_name
                        }
                    
                    target_container = None
                    for container in state['containers']:
                        if container['id'] == container_id:
                            target_container = container
                            break
                    
                    if not target_container:
                        existing_ids = [c['id'] for c in state['containers']]
                        return {
                            "status": "error",
                            "result": f"Container '{container_id}' not found. Available containers: {', '.join(existing_ids)}. Use get_canvas_state() to check current containers.",
                            "function_name": function_name
                        }
                    
                    # Container dimensions are no longer needed - chart will be responsive
                    
                    # Prepare chart data
                    if use_sample_data:
                        labels = ["Technology", "Healthcare", "Finance", "Education", "Retail"]
                        values = [35, 25, 20, 12, 8]
                        data_source = "sample data"
                    else:
                        labels = arguments.get("labels", [])
                        values = arguments.get("values", [])
                        
                        if not labels or not values:
                            return {
                                "status": "error",
                                "result": "When use_sample_data is false, both 'labels' and 'values' must be provided.",
                                "function_name": function_name
                            }
                        
                        if len(labels) != len(values):
                            return {
                                "status": "error",
                                "result": f"Labels and values must have the same length. Got {len(labels)} labels and {len(values)} values.",
                                "function_name": function_name
                            }
                        
                        data_source = "custom data"
                    
                    # Create pie chart HTML content that adapts to container
                    chart_html = self._create_pie_chart_html(title, labels, values)
                    
                    # Inject the chart into the container using safer DOM manipulation
                    # First, pass the HTML content as an argument to avoid escaping issues
                    import time
                    
                    # Add a small delay to ensure container is fully ready
                    time.sleep(0.1)
                    
                    success = self.controller.driver.execute_script("""
                        const container = document.getElementById(arguments[0]);
                        if (!container) {
                            console.error('Container not found:', arguments[0]);
                            return false;
                        }
                        
                        try {
                            // ROBUST CONTAINER BOUNDS ENFORCEMENT
                            // Ensure container stays fixed and content is strictly contained
                            
                            // 1. Lock container positioning to prevent movement
                            const containerRect = container.getBoundingClientRect();
                            const canvas = container.parentElement;
                            const canvasRect = canvas.getBoundingClientRect();
                            
                            // Store original container properties
                            const originalLeft = container.style.left;
                            const originalTop = container.style.top;
                            const originalWidth = container.style.width;
                            const originalHeight = container.style.height;
                            
                            // 2. Enforce strict container positioning and containment
                            container.style.position = 'absolute';  // Ensure absolute positioning
                            container.style.overflow = 'hidden';   // Prevent any overflow
                            container.style.left = originalLeft;   // Lock original position
                            container.style.top = originalTop;     // Lock original position
                            container.style.width = originalWidth; // Lock original size
                            container.style.height = originalHeight; // Lock original size
                            container.style.zIndex = '1';          // Ensure proper stacking
                            container.style.contain = 'layout style paint'; // CSS containment
                            
                            // 3. Clear existing content
                            container.innerHTML = '';
                            
                            // 4. Create a wrapper div that enforces strict bounds
                            const wrapper = document.createElement('div');
                            wrapper.style.cssText = `
                                position: relative;
                                width: 100%;
                                height: 100%;
                                overflow: hidden;
                                box-sizing: border-box;
                                margin: 0;
                                padding: 0;
                                top: 0;
                                left: 0;
                                contain: layout style paint;
                            `;
                            
                            // 5. Parse chart HTML safely
                            const tempDiv = document.createElement('div');
                            tempDiv.innerHTML = arguments[1];
                            
                            // Verify the HTML was parsed correctly
                            if (tempDiv.children.length === 0) {
                                console.error('No child elements found in parsed HTML for container:', arguments[0]);
                                return false;
                            }
                            
                            // 6. Move chart content into wrapper with strict positioning
                            while (tempDiv.firstChild) {
                                const child = tempDiv.firstChild;
                                
                                // Ensure child elements cannot escape container bounds
                                if (child.nodeType === Node.ELEMENT_NODE) {
                                    child.style.position = 'relative';
                                    child.style.maxWidth = '100%';
                                    child.style.maxHeight = '100%';
                                    child.style.overflow = 'hidden';
                                    child.style.contain = 'layout style paint';
                                    
                                    // Remove any absolute positioning that might break containment
                                    if (child.style.position === 'absolute' || child.style.position === 'fixed') {
                                        child.style.position = 'relative';
                                    }
                                }
                                
                                wrapper.appendChild(child);
                            }
                            
                            // 7. Add wrapper to container
                            container.appendChild(wrapper);
                            
                            // 8. Final verification and enforcement
                            if (container.children.length === 0) {
                                console.error('No children added to container after HTML injection:', arguments[0]);
                                return false;
                            }
                            
                            // 9. Re-enforce container bounds after content addition
                            container.style.left = originalLeft;   // Re-lock position
                            container.style.top = originalTop;     // Re-lock position
                            container.style.width = originalWidth; // Re-lock size
                            container.style.height = originalHeight; // Re-lock size
                            
                            // 10. Mark container as having chart content
                            container.setAttribute('data-content-type', 'pie-chart');
                            container.setAttribute('data-chart-title', arguments[2]);
                            container.setAttribute('data-bounds-locked', 'true');
                            
                            console.log('Pie chart successfully injected with bounds enforcement:', arguments[0]);
                            return true;
                            
                        } catch (error) {
                            console.error('Error injecting pie chart with bounds enforcement:', error);
                            return false;
                        }
                    """, container_id, chart_html, title)
                    
                    if success:
                        result_msg = f"Pie chart '{title}' created successfully in container '{container_id}' using {data_source}"
                        if not use_sample_data:
                            result_msg += f" with {len(labels)} segments"
                        
                        # Add chart identifier warning if applicable
                        if chart_id_warning:
                            result_msg += f"\n{chart_id_warning}"
                    else:
                        # Get more detailed error information
                        error_info = self.controller.driver.execute_script("""
                            const container = document.getElementById(arguments[0]);
                            if (!container) return 'Container not found';
                            return {
                                hasContent: container.innerHTML.length > 0,
                                contentType: container.getAttribute('data-content-type'),
                                error: 'JavaScript execution failed'
                            };
                        """, container_id)
                        result_msg = f"Failed to create pie chart in container '{container_id}'. Debug info: {error_info}"
                    
                    return {
                        "status": "success" if success else "error",
                        "result": result_msg,
                        "chart_data": {
                            "title": title,
                            "labels": labels,
                            "values": values,
                            "segments": len(labels)
                        },
                        "function_name": function_name
                    }
                    
                except Exception as e:
                    return {
                        "status": "error",
                        "result": f"Error creating pie chart: {str(e)}",
                        "function_name": function_name
                    }
            
            elif function_name == "get_canvas_settings":
                return {
                    "status": "success",
                    "result": {
                        "auto_adjust": self.chatbot.auto_adjust_enabled,
                        "overlap_prevention": self.chatbot.overlap_prevention_enabled,
                        "summary": f"Auto-adjust: {'ON' if self.chatbot.auto_adjust_enabled else 'OFF'}, Overlap prevention: {'ON' if self.chatbot.overlap_prevention_enabled else 'OFF'}"
                    },
                    "function_name": function_name
                }
            
            elif function_name == "check_container_content":
                try:
                    container_id = arguments["container_id"]
                    
                    # Check if container exists first
                    state = self.controller.get_current_state()
                    if not state or not state.get('containers'):
                        return {
                            "status": "error",
                            "result": f"No containers exist on canvas. Cannot check container '{container_id}'.",
                            "function_name": function_name
                        }
                    
                    container_exists = any(c['id'] == container_id for c in state['containers'])
                    if not container_exists:
                        existing_ids = [c['id'] for c in state['containers']]
                        return {
                            "status": "error",
                            "result": f"Container '{container_id}' not found. Available containers: {', '.join(existing_ids)}",
                            "function_name": function_name
                        }
                    
                    # Get detailed container content information
                    content_info = self.controller.driver.execute_script("""
                        const container = document.getElementById(arguments[0]);
                        if (!container) return {error: 'Container not found in DOM'};
                        
                        // Get all relevant information about the container content
                        const result = {
                            exists: true,
                            hasContent: container.innerHTML.length > 0,
                            contentType: container.getAttribute('data-content-type'),
                            chartTitle: container.getAttribute('data-chart-title'),

                            childCount: container.children.length,
                            innerHTML: container.innerHTML.length > 0 ? container.innerHTML.substring(0, 200) + '...' : 'Empty',
                            containerStyle: {
                                position: container.style.position,
                                overflow: container.style.overflow,
                                width: container.offsetWidth + 'px',
                                height: container.offsetHeight + 'px'
                            }
                        };
                        
                        // Check for specific content types
                        if (result.contentType === 'pie-chart') {
                            result.hasPieChart = true;
                            result.pieChartElements = {
                                hasSVG: container.querySelector('svg') !== null,
                                hasLegend: container.querySelector('div[style*="grid"]') !== null,
                                hasTitle: container.querySelector('h3') !== null
                            };
                        } else {
                            result.hasPieChart = false;
                        }
                        
                        return result;
                    """, container_id)
                    
                    # Format the result for better readability
                    if content_info.get('error'):
                        result_msg = f"Error checking container '{container_id}': {content_info['error']}"
                        status = "error"
                    else:
                        # Create a comprehensive summary
                        summary_parts = []
                        
                        if content_info.get('hasPieChart'):
                            summary_parts.append(f"✅ Contains PIE CHART: '{content_info.get('chartTitle', 'Unknown Title')}'")
                            pie_elements = content_info.get('pieChartElements', {})
                            element_status = []
                            if pie_elements.get('hasSVG'): element_status.append("SVG")
                            if pie_elements.get('hasLegend'): element_status.append("Legend") 
                            if pie_elements.get('hasTitle'): element_status.append("Title")
                            if element_status:
                                summary_parts.append(f"   Chart elements: {', '.join(element_status)}")
                        elif content_info.get('contentType'):
                            summary_parts.append(f"📄 Contains: {content_info['contentType'].upper()}")
                        elif content_info.get('hasContent'):
                            summary_parts.append("📝 Has content but no specific type identified")
                        else:
                            summary_parts.append("📭 Container is EMPTY")
                        
                        summary_parts.append(f"   Child elements: {content_info.get('childCount', 0)}")
                        summary_parts.append(f"   Content length: {len(content_info.get('innerHTML', '')) - 3} characters")  # -3 for '...'
                        
                        result_msg = f"Container '{container_id}' content check:\n" + "\n".join(summary_parts)
                        status = "success"
                    
                    return {
                        "status": status,
                        "result": result_msg,
                        "detailed_info": content_info,
                        "function_name": function_name
                    }
                    
                except Exception as e:
                    return {
                        "status": "error",
                        "result": f"Error checking container '{arguments.get('container_id', 'unknown')}': {str(e)}",
                        "function_name": function_name
                    }
            
            elif function_name == "calculate_optimal_layout":
                try:
                    containers = arguments["containers"]
                    canvas_width = arguments["canvas_width"]
                    canvas_height = arguments["canvas_height"]
                    
                    # Calculate optimal layout using space optimization algorithm
                    layout_result = self._calculate_optimal_container_layout(
                        containers, canvas_width, canvas_height
                    )
                    
                    return {
                        "status": "success",
                        "result": layout_result,
                        "function_name": function_name
                    }
                    
                except Exception as e:
                    return {
                        "status": "error",
                        "result": f"Error calculating optimal layout: {str(e)}",
                        "function_name": function_name
                    }
            
            elif function_name == "check_identifier_availability":
                try:
                    proposed_id = arguments["proposed_identifier"]
                    element_type = arguments.get("element_type", "element")
                    
                    # Validate the identifier
                    validation_result = self._validate_identifier_uniqueness(proposed_id, element_type)
                    used_info = validation_result["used_identifiers"]
                    
                    if validation_result["is_valid"]:
                        if validation_result.get("warning"):
                            # Valid but with warning
                            result_msg = f"✅ Identifier '{validation_result['clean_id']}' is available but has a warning:\n"
                            result_msg += f"   ⚠️ {validation_result['warning']}\n"
                        else:
                            # Completely valid
                            result_msg = f"✅ Identifier '{validation_result['clean_id']}' is available and unique!\n"
                        
                        if validation_result['clean_id'] != proposed_id:
                            result_msg += f"   🔧 Cleaned from '{proposed_id}' to '{validation_result['clean_id']}'\n"
                        
                        result_msg += f"📋 Current usage: {used_info['summary']}"
                        
                        return {
                            "status": "success",
                            "result": result_msg,
                            "validation_details": validation_result,
                            "function_name": function_name
                        }
                    else:
                        # Invalid - conflicts found
                        result_msg = f"❌ Identifier '{proposed_id}' is NOT available:\n"
                        result_msg += f"   🚫 {validation_result['error']}\n"
                        result_msg += f"📋 Currently used identifiers:\n"
                        result_msg += f"   🗂️ Containers: {', '.join(used_info['container_ids']) if used_info['container_ids'] else 'None'}\n"
                        result_msg += f"   📊 Charts: {', '.join(used_info['chart_ids']) if used_info['chart_ids'] else 'None'}\n"
                        result_msg += f"💡 Suggested alternatives: {', '.join(validation_result['suggestions'])}"
                        
                        return {
                            "status": "error",
                            "result": result_msg,
                            "validation_details": validation_result,
                            "function_name": function_name
                        }
                        
                except Exception as e:
                    return {
                        "status": "error",
                        "result": f"Error checking identifier availability: {str(e)}",
                        "function_name": function_name
                    }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown function: {function_name}",
                    "available_functions": ["create_container", "delete_container", "modify_container", 
                                          "get_canvas_state", "clear_canvas", "take_screenshot", 
                                          "get_canvas_size", "edit_canvas_size", "create_pie_chart", 
                                          "get_canvas_settings", "check_container_content", "calculate_optimal_layout",
                                          "check_identifier_availability"]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error executing {function_name}: {str(e)}",
                "function_name": function_name
            }

class CanvasChatbot:
    """
    Main chatbot class that orchestrates LLM and canvas operations
    """
    
    def __init__(self, headless: bool = False):
        """
        Initialize the chatbot
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.canvas_controller = None
        self.llm_client = None
        self.function_executor = None
        self.conversation_history = []
        
        # Canvas behavior settings that LLM can control
        self.auto_adjust_enabled = True
        self.overlap_prevention_enabled = False
        
    def initialize(self):
        """Initialize all components"""
        print("🤖 Initializing Canvas Chatbot...")
        
        # Initialize canvas controller
        print("🔧 Starting browser and canvas...")
        self.canvas_controller = CanvasController(headless=self.headless)
        
        # Initialize LLM client
        print("🧠 Connecting to OpenAI...")
        self.llm_client = CanvasLLMClient()
        
        # Initialize function executor
        self.function_executor = CanvasFunctionExecutor(self.canvas_controller, self)
        
        print("✅ Chatbot initialized successfully!")
        print("💡 You can now give me commands to control the canvas.")
        print("💡 Try: 'Create a container at position 100,100 with size 200x150'")
        print("💡 Type 'help' for more examples or 'quit' to exit.")
    
    def process_user_message(self, user_message: str) -> str:
        """
        Process a user message with LLM function calling
        
        Args:
            user_message: User's message
            
        Returns:
            Assistant's response
        """
        # Add system message if this is the first message
        messages = []
        if not self.conversation_history:
            messages.append({
                "role": "system",
                "content": self.llm_client.system_message
            })
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        function_calls_made = 0
        max_iterations = 5  # Prevent infinite loops
        iteration_count = 0
        
        while iteration_count < max_iterations:
            iteration_count += 1
            
            # Get LLM response
            response = self.llm_client.chat_completion(
                messages=messages,
                functions=self.llm_client.get_function_schemas()
            )
            
            if response["status"] != "success":
                return f"❌ Error: {response.get('error', 'Unknown error')}"
            
            message = response["message"]
            
            # Check if LLM wants to call a function (handle both old and new API formats)
            function_calls_to_process = []
            
            # Handle new tools format
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.type == 'function':
                        function_calls_to_process.append({
                            'id': tool_call.id,
                            'name': tool_call.function.name,
                            'arguments': tool_call.function.arguments
                        })
            
            # Handle old function_call format (fallback)
            elif hasattr(message, 'function_call') and message.function_call:
                function_calls_to_process.append({
                    'id': None,
                    'name': message.function_call.name,
                    'arguments': message.function_call.arguments
                })
            
            if function_calls_to_process:
                # Process each function call
                for func_call in function_calls_to_process:
                    function_name = func_call['name']
                    
                    try:
                        function_args = json.loads(func_call['arguments'])
                    except json.JSONDecodeError as e:
                        return f"❌ Error: Invalid function arguments: {str(e)}"
                    
                    # Execute the function
                    function_result = self.function_executor.execute_function_call(
                        function_name, function_args
                    )
                    
                    # Add assistant message with function call
                    if func_call['id']:  # New tools format
                        messages.append({
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [{
                                "id": func_call['id'],
                                "type": "function",
                                "function": {
                                    "name": function_name,
                                    "arguments": func_call['arguments']
                                }
                            }]
                        })
                        
                        # Add tool result
                        messages.append({
                            "role": "tool",
                            "tool_call_id": func_call['id'],
                            "content": json.dumps(function_result)
                        })
                    else:  # Old function_call format
                        messages.append({
                            "role": "assistant",
                            "content": "",
                            "function_call": {
                                "name": function_name,
                                "arguments": func_call['arguments']
                            }
                        })
                        
                        # Add function result
                        messages.append({
                            "role": "function",
                            "name": function_name,
                            "content": json.dumps(function_result)
                        })
                
                function_calls_made += 1
                
                # Check if we should prompt user to continue after 5 calls
                if function_calls_made >= 5:
                    print(f"\n⚠️ Made {function_calls_made} function calls.")
                    continue_choice = input("🤔 Continue with more function calls? (y/N): ").strip().lower()
                    if continue_choice != 'y':
                        return f"⏹️ Stopped after {function_calls_made} function calls at user request."
                
                # Enhanced error handling - don't break immediately, let LLM handle errors
                if function_result["status"] == "error":
                    # Add error context to help LLM understand what went wrong
                    error_context = f"Function {function_name} failed: {function_result.get('error', 'Unknown error')}"
                    if 'available_functions' in function_result:
                        error_context += f" Available functions: {', '.join(function_result['available_functions'])}"
                    print(f"❌ {error_context}")
                    
                    # Continue to let LLM respond to the error rather than breaking
            
            else:
                # No function call, LLM provided final response
                final_response = message.content or "Operation completed."
                
                # Update conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": user_message
                })
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": final_response
                })
                
                # Keep conversation history manageable
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                return final_response
        
        # If we exit the loop without a proper response, determine why
        if iteration_count >= max_iterations:
            print(f"⚠️ Reached maximum iterations ({max_iterations}). Requesting final response...")
            summary_prompt = "You have reached the maximum number of iterations. Please provide a summary of the operations performed and their results. Do not make any more function calls."
        else:
            print("⚠️ Function calling loop ended unexpectedly. Requesting final response...")
            summary_prompt = "Please provide a summary of the operations performed and their results. Do not make any more function calls."
        
        # Add a message asking for summary
        messages.append({
            "role": "system",
            "content": summary_prompt
        })
        
        # Get final response without function calling
        final_response = self.llm_client.chat_completion(messages=messages, functions=None)
        
        if final_response["status"] == "success" and final_response["content"]:
            return final_response["content"]
        else:
            return f"⚠️ Operations completed but encountered issues. Made {function_calls_made} function calls in {iteration_count} iterations."
    
    def show_help(self):
        """Show help information"""
        help_text = f"""
🎯 CANVAS CHATBOT HELP

Available Commands:
• Create containers: "Create a container called 'chart1' at 100,100 with size 300x200"
• Delete containers: "Delete the container named 'chart1'"
• Modify containers: "Move container 'chart1' to position 200,150 and resize to 400x250"
• Create pie charts: "Create a pie chart in container 'chart1'" or "Add a pie chart with custom data"
• View canvas: "Show me the current canvas state"
• Clear canvas: "Clear all containers"
• Take screenshot: "Take a screenshot and save it as 'my_canvas.png'"
• Canvas size: "What's the current canvas size?" or "Resize canvas to 1000x800"
• Behavior control: "Turn off overlap prevention" or "Enable auto-adjustment"
• Check settings: "What are the current canvas settings?"
• Check container content: "Check what's in container 'chart1'" or "Verify the pie chart in container 'sales_chart'"

Natural Language Examples:
• "Put a small container in the top left corner"
• "Create three containers side by side"
• "Make a large container in the center"
• "Add a pie chart to the container I just created"
• "Create a pie chart showing sales data with custom values"
• "Remove all containers and start fresh"
• "Show me what's on the canvas right now"
• "Allow containers to overlap"
• "Turn off auto-adjustment so I can place containers exactly where I want"

Tips:
• Be specific about positions (x,y coordinates) and sizes (width x height)
• Container IDs should be unique strings
• Canvas coordinates start at (0,0) in the top-left corner
• Pie charts require an existing container - create a container first
• Pie charts use sample data by default (Technology, Healthcare, Finance, Education, Retail)
• You can provide custom labels and values for pie charts
• Auto-adjustment and overlap prevention are enabled by default
• You can control these behaviors through natural language commands
• For precise positioning, consider disabling auto-adjustment
• For overlapping layouts, disable overlap prevention

Type 'quit' to exit the chatbot.
        """
        print(help_text)
    
    def run(self):
        """Main chatbot loop"""
        try:
            self.initialize()
            
            print("\n" + "="*60)
            print("🎨 CANVAS CONTROL CHATBOT")
            print("="*60)
            
            while True:
                try:
                    user_input = input("\n💬 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        print("👋 Goodbye!")
                        break
                    
                    if user_input.lower() in ['help', '?']:
                        self.show_help()
                        continue
                    

                    
                    print("🤖 Assistant: ", end="", flush=True)
                    response = self.process_user_message(user_input)
                    print(response)
                    
                except KeyboardInterrupt:
                    print("\n\n⚠️ Interrupted by user.")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {str(e)}")
                    print("Please try again or type 'help' for assistance.")
        
        finally:
            if self.canvas_controller:
                print("\n🔒 Closing browser...")
                self.canvas_controller.close()

def main():
    """Main entry point"""
    print("🚀 Starting Canvas Control Chatbot...")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key in a .env file or environment variable.")
        return
    
    # Ask about headless mode
    # headless_input = input("Run browser in headless mode? (y/N): ").strip().lower()
    # headless = headless_input == 'y'
    headless = False
    # Create and run chatbot
    chatbot = CanvasChatbot(headless=headless)
    chatbot.run()

if __name__ == "__main__":
    main()
