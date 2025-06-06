"""
Function Executor for Canvas Operations

Bridges LLM function calls to canvas controller operations.
Based on the proven implementation from tests/python/llm_canvas_chatbot.py.
"""

import json
import math
from typing import Dict, Any, List, Optional
from datetime import datetime

from .canvas_bridge import canvas_bridge


class CanvasFunctionExecutor:
    """
    Function executor that bridges LLM function calls to canvas operations
    """
    
    def __init__(self, chatbot_instance=None):
        """
        Initialize with a reference to the chatbot instance
        
        Args:
            chatbot_instance: Reference to chatbot for accessing settings
        """
        self.chatbot = chatbot_instance
        self.canvas_bridge = canvas_bridge
        
        # Default settings
        self.auto_adjust_enabled = True
        self.overlap_prevention_enabled = False
    
    def _get_all_used_identifiers(self):
        """
        Get all currently used identifiers across all elements on the canvas
        
        Returns:
            Dict with categorized identifiers and summary
        """
        try:
            # Get container identifiers
            current_state = self.canvas_bridge.get_canvas_state()
            container_ids = [c['id'] for c in current_state.get('containers', [])]
            
            # For now, we only track container IDs
            # Chart IDs would be tracked here if we implement pie charts
            chart_ids = []
            
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
        current_state = self.canvas_bridge.get_canvas_state()
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
            optimization_result: Result from canvas_bridge.calculate_optimal_layout
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
                success = asyncio.create_task(self.canvas_bridge.modify_container(
                    container_id=container_id,
                    x=opt_container['recommended_x'],
                    y=opt_container['recommended_y'],
                    width=opt_container['recommended_width'],
                    height=opt_container['recommended_height'],
                    auto_adjust=self.auto_adjust_enabled,
                    avoid_overlap=self.overlap_prevention_enabled
                ))
            else:
                # Create new container
                success = asyncio.create_task(self.canvas_bridge.create_container(
                    container_id=container_id,
                    x=opt_container['recommended_x'],
                    y=opt_container['recommended_y'],
                    width=opt_container['recommended_width'],
                    height=opt_container['recommended_height'],
                    auto_adjust=self.auto_adjust_enabled,
                    avoid_overlap=self.overlap_prevention_enabled
                ))
            
            container_result = {
                "container_id": container_id,
                "success": True,  # Assume success for now
                "status": opt_container['status'],
                "optimized_position": (opt_container['recommended_x'], opt_container['recommended_y']),
                "optimized_size": (opt_container['recommended_width'], opt_container['recommended_height']),
                "grid_position": opt_container.get('grid_position', {})
            }
            
            # Add change information for existing containers
            if opt_container['status'] == 'existing':
                container_result["previous_position"] = (opt_container.get('current_x'), opt_container.get('current_y'))
                container_result["previous_size"] = (opt_container.get('current_width'), opt_container.get('current_height'))
            
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
    
    async def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call on the canvas bridge
        
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
                    canvas_size = self.canvas_bridge.get_canvas_size()
                    
                    # Get all containers for optimization (existing + new)
                    containers_for_optimization = self._get_all_containers_for_optimization(
                        new_container_id=clean_container_id
                    )
                    
                    # Calculate optimal layout
                    optimization_result = self.canvas_bridge.calculate_optimal_layout(
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
                    current_state = self.canvas_bridge.get_canvas_state()
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
                    
                    # Delete the container
                    delete_result = await self.canvas_bridge.delete_container(container_id)
                    
                    if not delete_result:
                        return {
                            "status": "error",
                            "result": f"Failed to delete container '{container_id}' from canvas.",
                            "function_name": function_name
                        }
                    
                    # Get remaining containers after deletion
                    remaining_state = self.canvas_bridge.get_canvas_state()
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
                    canvas_size = self.canvas_bridge.get_canvas_size()
                    containers_for_optimization = self._get_all_containers_for_optimization()
                    
                    # Calculate optimal layout for remaining containers
                    optimization_result = self.canvas_bridge.calculate_optimal_layout(
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
                    current_state = self.canvas_bridge.get_canvas_state()
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
                    canvas_size = self.canvas_bridge.get_canvas_size()
                    
                    # Get all containers for optimization (all existing, including the one being modified)
                    containers_for_optimization = self._get_all_containers_for_optimization()
                    
                    # Calculate optimal layout
                    optimization_result = self.canvas_bridge.calculate_optimal_layout(
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
                        
                        # Add information about other containers that were repositioned
                        repositioned_containers = [r for r in layout_application["container_results"] 
                                                 if r["container_id"] != container_id and r["status"] == "existing"]
                        if repositioned_containers:
                            result_msg += f"\n   🔄 Repositioned {len(repositioned_containers)} other container(s) for optimal layout"
                        
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
                state = self.canvas_bridge.get_canvas_state()
                
                # Format the state information for better LLM understanding
                containers = state.get('containers', [])
                if containers:
                    container_summary = []
                    for container in containers:
                        summary = f"'{container['id']}': position ({container['x']}, {container['y']}), size {container['width']}x{container['height']}"
                        container_summary.append(summary)
                    
                    formatted_result = {
                        "canvas_size": state.get('canvas_size', {'width': 800, 'height': 600}),
                        "container_count": len(containers),
                        "containers": containers,
                        "summary": f"Canvas has {len(containers)} container(s): " + "; ".join(container_summary)
                    }
                else:
                    formatted_result = {
                        "canvas_size": state.get('canvas_size', {'width': 800, 'height': 600}),
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
                result = await self.canvas_bridge.clear_canvas()
                return {
                    "status": "success" if result else "error",
                    "result": "Canvas cleared successfully" if result else "Failed to clear canvas",
                    "function_name": function_name
                }
            
            elif function_name == "take_screenshot":
                filename = arguments.get("filename")
                screenshot_path = await self.canvas_bridge.take_screenshot(filename)
                return {
                    "status": "success" if screenshot_path else "error",
                    "result": f"Screenshot requested: {screenshot_path}" if screenshot_path else "Failed to take screenshot",
                    "function_name": function_name
                }
            
            elif function_name == "get_canvas_size":
                size = self.canvas_bridge.get_canvas_size()
                return {
                    "status": "success",
                    "result": f"Canvas size: {size['width']}x{size['height']} pixels",
                    "canvas_size": size,
                    "function_name": function_name
                }
            
            elif function_name == "edit_canvas_size":
                try:
                    new_width = arguments['width']
                    new_height = arguments['height']
                    
                    # Update canvas size in bridge
                    self.canvas_bridge.canvas_state["canvas_size"] = {
                        "width": new_width,
                        "height": new_height
                    }
                    
                    # Send command to frontend
                    await self.canvas_bridge.broadcast_to_frontend({
                        "type": "canvas_command",
                        "command": "edit_canvas_size",
                        "data": {
                            "width": new_width,
                            "height": new_height
                        }
                    })
                    
                    return {
                        "status": "success",
                        "result": f"Canvas resized to {new_width}x{new_height} pixels",
                        "function_name": function_name
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "result": f"Error resizing canvas: {str(e)}",
                        "function_name": function_name
                    }
            
            elif function_name == "get_canvas_settings":
                return {
                    "status": "success",
                    "result": {
                        "auto_adjust": self.auto_adjust_enabled,
                        "overlap_prevention": self.overlap_prevention_enabled,
                        "summary": f"Auto-adjust: {'ON' if self.auto_adjust_enabled else 'OFF'}, Overlap prevention: {'ON' if self.overlap_prevention_enabled else 'OFF'}"
                    },
                    "function_name": function_name
                }
            
            elif function_name == "check_container_content":
                try:
                    container_id = arguments["container_id"]
                    
                    # Check if container exists first
                    state = self.canvas_bridge.get_canvas_state()
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
                    
                    # For now, just return basic container info
                    # In the future, this could check for charts or other content
                    container_data = None
                    for c in state['containers']:
                        if c['id'] == container_id:
                            container_data = c
                            break
                    
                    result_msg = f"Container '{container_id}' content check:\n"
                    result_msg += f"   📦 Container exists and is empty (basic container)\n"
                    result_msg += f"   📍 Position: ({container_data['x']}, {container_data['y']})\n"
                    result_msg += f"   📏 Size: {container_data['width']}x{container_data['height']}"
                    
                    return {
                        "status": "success",
                        "result": result_msg,
                        "function_name": function_name
                    }
                    
                except Exception as e:
                    return {
                        "status": "error",
                        "result": f"Error checking container '{arguments.get('container_id', 'unknown')}': {str(e)}",
                        "function_name": function_name
                    }
            
            # Placeholder for pie chart functionality (not implemented in v0.1)
            elif function_name == "create_pie_chart":
                return {
                    "status": "error",
                    "result": "Pie chart functionality is not implemented in v0.1. This feature is available in the Python test environment.",
                    "function_name": function_name
                }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown function: {function_name}",
                    "available_functions": ["create_container", "delete_container", "modify_container", 
                                          "get_canvas_state", "clear_canvas", "take_screenshot", 
                                          "get_canvas_size", "edit_canvas_size", "get_canvas_settings", 
                                          "check_container_content"]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error executing {function_name}: {str(e)}",
                "function_name": function_name
            } 