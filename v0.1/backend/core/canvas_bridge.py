"""
Canvas Bridge for v0.1 Frontend Communication

Provides an interface to the v0.1 frontend canvas through WebSocket communication.
Replaces the Selenium-based approach with direct frontend integration.
"""

import json
import math
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime


class CanvasBridge:
    """
    Bridge between backend and v0.1 frontend canvas
    """
    
    def __init__(self):
        """Initialize the canvas bridge"""
        self.websocket_connections: Set = set()
        self.canvas_state = {
            "containers": {},
            "canvas_size": {"width": 800, "height": 600},
            "settings": {
                "auto_adjust": True,
                "overlap_prevention": False
            },
            "last_updated": datetime.now().isoformat()
        }
        
    def add_websocket_connection(self, websocket):
        """Add a WebSocket connection"""
        self.websocket_connections.add(websocket)
        
    def remove_websocket_connection(self, websocket):
        """Remove a WebSocket connection"""
        self.websocket_connections.discard(websocket)
        
    async def broadcast_to_frontend(self, message: Dict[str, Any]):
        """Broadcast a message to all connected frontends"""
        if not self.websocket_connections:
            return
            
        message_json = json.dumps(message)
        disconnected = set()
        
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(message_json)
            except Exception:
                disconnected.add(websocket)
        
        # Remove disconnected websockets
        for ws in disconnected:
            self.websocket_connections.discard(ws)
    
    def get_canvas_size(self) -> Dict[str, int]:
        """Get current canvas size"""
        return self.canvas_state["canvas_size"].copy()
    
    def get_canvas_state(self) -> Dict[str, Any]:
        """Get the current state of the canvas"""
        containers_list = []
        for container_id, container_data in self.canvas_state["containers"].items():
            containers_list.append({
                "id": container_id,
                "x": container_data["x"],
                "y": container_data["y"],
                "width": container_data["width"],
                "height": container_data["height"]
            })
        
        return {
            "hasContainers": len(self.canvas_state["containers"]) > 0,
            "containerCount": len(self.canvas_state["containers"]),
            "containers": containers_list,
            "canvas_size": self.canvas_state["canvas_size"],
            "settings": self.canvas_state["settings"]
        }
    
    def get_existing_containers(self) -> List[Dict[str, Any]]:
        """Get positions and sizes of all existing containers"""
        containers = []
        for container_id, container_data in self.canvas_state["containers"].items():
            containers.append({
                "id": container_id,
                "x": container_data["x"],
                "y": container_data["y"],
                "width": container_data["width"],
                "height": container_data["height"]
            })
        return containers
    
    def check_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
        """Check if two rectangles overlap"""
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)
    
    def find_non_overlapping_position(self, width, height, canvas_width, canvas_height, 
                                    existing_containers, preferred_x=None, preferred_y=None):
        """Find a position where the container won't overlap with existing ones"""
        # If preferred position is given and doesn't overlap, use it
        if preferred_x is not None and preferred_y is not None:
            overlaps = False
            for container in existing_containers:
                if self.check_overlap(preferred_x, preferred_y, width, height,
                                    container['x'], container['y'], container['width'], container['height']):
                    overlaps = True
                    break
            
            if not overlaps and preferred_x + width <= canvas_width and preferred_y + height <= canvas_height:
                return preferred_x, preferred_y
        
        # Try to find a non-overlapping position
        # Start from top-left and scan in a grid pattern
        step_size = 20  # Grid step size for positioning
        
        for y in range(0, canvas_height - height + 1, step_size):
            for x in range(0, canvas_width - width + 1, step_size):
                # Check if this position overlaps with any existing container
                overlaps = False
                for container in existing_containers:
                    if self.check_overlap(x, y, width, height,
                                        container['x'], container['y'], container['width'], container['height']):
                        overlaps = True
                        break
                
                if not overlaps:
                    return x, y
        
        # If no non-overlapping position found, try smaller step size
        step_size = 5
        for y in range(0, canvas_height - height + 1, step_size):
            for x in range(0, canvas_width - width + 1, step_size):
                overlaps = False
                for container in existing_containers:
                    if self.check_overlap(x, y, width, height,
                                        container['x'], container['y'], container['width'], container['height']):
                        overlaps = True
                        break
                
                if not overlaps:
                    return x, y
        
        # If still no position found, return None to indicate no space available
        return None, None
    
    def calculate_optimal_layout(self, containers, canvas_width, canvas_height):
        """
        Calculate optimal sizes and positions for containers to minimize empty space and size differences
        """
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
                
                optimized_containers.append(optimized_container)
                container_index += 1
        
        # Calculate space utilization
        total_container_area = num_containers * container_width * container_height
        canvas_area = canvas_width * canvas_height
        space_utilization = (total_container_area / canvas_area) * 100
        
        # Generate layout summary
        layout_summary = {
            "summary": f"Optimized layout for {num_containers} containers in {cols}x{rows} grid",
            "layout_type": f"{cols}x{rows}_grid",
            "containers": optimized_containers,
            "metrics": {
                "space_utilization_percent": round(space_utilization, 1),
                "size_uniformity_percent": 100.0,  # Perfect uniformity since all containers are same size
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
    
    async def create_container(self, container_id: str, x: int, y: int, width: int, height: int, 
                             auto_adjust: bool = True, avoid_overlap: bool = True) -> bool:
        """Create a new container on the canvas"""
        try:
            # Validate inputs
            if not isinstance(container_id, str) or not container_id.strip():
                raise ValueError("Container ID must be a non-empty string")
            
            if container_id in self.canvas_state["containers"]:
                print(f"❌ Container '{container_id}' already exists")
                return False
            
            if not all(isinstance(val, (int, float)) and val >= 0 for val in [x, y, width, height]):
                raise ValueError("Position and size values must be non-negative numbers")
            
            # Get current canvas size and existing containers
            canvas_size = self.get_canvas_size()
            canvas_width = canvas_size.get('width', 800)
            canvas_height = canvas_size.get('height', 600)
            existing_containers = self.get_existing_containers()
            
            # Store original values for reporting
            original_x, original_y, original_width, original_height = x, y, width, height
            
            if auto_adjust:
                # Auto-adjust to ensure container fits within canvas
                adjusted = False
                
                # Adjust width if too large
                if width > canvas_width:
                    width = canvas_width
                    adjusted = True
                    print(f"📏 Adjusted width from {original_width} to {width} to fit canvas")
                
                # Adjust height if too large
                if height > canvas_height:
                    height = canvas_height
                    adjusted = True
                    print(f"📏 Adjusted height from {original_height} to {height} to fit canvas")
                
                # Adjust X position if container extends beyond right edge
                if x + width > canvas_width:
                    x = canvas_width - width
                    adjusted = True
                    print(f"📍 Adjusted X position from {original_x} to {x} to fit canvas")
                
                # Adjust Y position if container extends beyond bottom edge
                if y + height > canvas_height:
                    y = canvas_height - height
                    adjusted = True
                    print(f"📍 Adjusted Y position from {original_y} to {y} to fit canvas")
                
                # Ensure position is not negative
                if x < 0:
                    x = 0
                    adjusted = True
                if y < 0:
                    y = 0
                    adjusted = True
                
                if adjusted:
                    print(f"🔧 Container auto-adjusted to fit within canvas bounds ({canvas_width}x{canvas_height})")
            
            # Check for overlaps and find non-overlapping position if needed
            if avoid_overlap and existing_containers:
                # Check if current position overlaps with existing containers
                overlaps = False
                overlapping_containers = []
                
                for container in existing_containers:
                    if self.check_overlap(x, y, width, height,
                                        container['x'], container['y'], container['width'], container['height']):
                        overlaps = True
                        overlapping_containers.append(container['id'])
                
                if overlaps:
                    print(f"🚫 Position ({x}, {y}) overlaps with: {', '.join(overlapping_containers)}")
                    
                    # Find a non-overlapping position
                    new_x, new_y = self.find_non_overlapping_position(
                        width, height, canvas_width, canvas_height, existing_containers, x, y
                    )
                    
                    if new_x is not None and new_y is not None:
                        if new_x != x or new_y != y:
                            print(f"🔄 Found non-overlapping position: ({x}, {y}) → ({new_x}, {new_y})")
                            x, y = new_x, new_y
                    else:
                        print(f"❌ No space available for container of size {width}x{height}")
                        print(f"❌ Cannot create container without overlapping - rejecting creation")
                        return False
            
            # Create container in state
            self.canvas_state["containers"][container_id] = {
                "id": container_id,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "created_at": datetime.now().isoformat()
            }
            
            self.canvas_state["last_updated"] = datetime.now().isoformat()
            
            # Send command to frontend
            await self.broadcast_to_frontend({
                "type": "canvas_command",
                "command": "create_container",
                "data": {
                    "container_id": container_id,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                }
            })
            
            print(f"✅ Container '{container_id}' created at ({x}, {y}) with size {width}x{height}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating container: {e}")
            return False
    
    async def delete_container(self, container_id: str) -> bool:
        """Delete a container from the canvas"""
        try:
            if container_id not in self.canvas_state["containers"]:
                print(f"❌ Container '{container_id}' not found")
                return False
            
            # Remove from state
            del self.canvas_state["containers"][container_id]
            self.canvas_state["last_updated"] = datetime.now().isoformat()
            
            # Send command to frontend
            await self.broadcast_to_frontend({
                "type": "canvas_command",
                "command": "delete_container",
                "data": {
                    "container_id": container_id
                }
            })
            
            print(f"✅ Container '{container_id}' deleted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting container: {e}")
            return False
    
    async def modify_container(self, container_id: str, x: int, y: int, width: int, height: int,
                             auto_adjust: bool = True, avoid_overlap: bool = True) -> bool:
        """Modify an existing container's position and size"""
        try:
            if container_id not in self.canvas_state["containers"]:
                print(f"❌ Container '{container_id}' not found")
                return False
            
            # Similar logic to create_container but for modification
            canvas_size = self.get_canvas_size()
            canvas_width = canvas_size.get('width', 800)
            canvas_height = canvas_size.get('height', 600)
            existing_containers = [c for c in self.get_existing_containers() if c['id'] != container_id]
            
            # Auto-adjust if enabled
            if auto_adjust:
                # Ensure container fits within canvas bounds
                if width > canvas_width:
                    width = canvas_width
                if height > canvas_height:
                    height = canvas_height
                if x + width > canvas_width:
                    x = canvas_width - width
                if y + height > canvas_height:
                    y = canvas_height - height
                if x < 0:
                    x = 0
                if y < 0:
                    y = 0
            
            # Check for overlaps if enabled
            if avoid_overlap and existing_containers:
                overlaps = False
                for container in existing_containers:
                    if self.check_overlap(x, y, width, height,
                                        container['x'], container['y'], container['width'], container['height']):
                        overlaps = True
                        break
                
                if overlaps:
                    new_x, new_y = self.find_non_overlapping_position(
                        width, height, canvas_width, canvas_height, existing_containers, x, y
                    )
                    
                    if new_x is not None and new_y is not None:
                        x, y = new_x, new_y
                    else:
                        print(f"❌ No space available for container modification")
                        return False
            
            # Update container in state
            self.canvas_state["containers"][container_id].update({
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "modified_at": datetime.now().isoformat()
            })
            
            self.canvas_state["last_updated"] = datetime.now().isoformat()
            
            # Send command to frontend
            await self.broadcast_to_frontend({
                "type": "canvas_command",
                "command": "modify_container",
                "data": {
                    "container_id": container_id,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                }
            })
            
            print(f"✅ Container '{container_id}' modified to pos({x}, {y}) size({width}x{height})")
            return True
            
        except Exception as e:
            print(f"❌ Error modifying container: {e}")
            return False
    
    async def clear_canvas(self) -> bool:
        """Remove all containers from the canvas"""
        try:
            if not self.canvas_state["containers"]:
                print("📭 Canvas is already empty")
                return True
            
            container_count = len(self.canvas_state["containers"])
            
            # Clear state
            self.canvas_state["containers"] = {}
            self.canvas_state["last_updated"] = datetime.now().isoformat()
            
            # Send command to frontend
            await self.broadcast_to_frontend({
                "type": "canvas_command",
                "command": "clear_canvas",
                "data": {}
            })
            
            print(f"🧹 Cleared {container_count} containers from canvas")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing canvas: {e}")
            return False
    
    async def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot of the current canvas state"""
        try:
            if filename is None:
                from datetime import datetime
                timestamp = int(datetime.now().timestamp())
                filename = f"canvas_screenshot_{timestamp}.png"
            
            # Send command to frontend
            await self.broadcast_to_frontend({
                "type": "canvas_command",
                "command": "take_screenshot",
                "data": {
                    "filename": filename
                }
            })
            
            print(f"📸 Screenshot requested: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error taking screenshot: {e}")
            return None


# Global instance
canvas_bridge = CanvasBridge() 