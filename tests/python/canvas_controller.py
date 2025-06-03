"""
Canvas Controller - Python interface for managing frontend containers
"""

import json
import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CanvasController:
    def __init__(self, headless=False):
        """
        Initialize the canvas controller with a browser instance
        
        Args:
            headless (bool): Whether to run browser in headless mode
        """
        self.driver = None
        self.headless = headless
        self.frontend_path = None
        self._setup_browser()
        self._load_frontend()
    
    def _setup_browser(self):
        """Setup Chrome browser with appropriate options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1200,800")
        
        # Reduce TensorFlow and other Chrome logging
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Browser initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize browser: {e}")
            print("Make sure ChromeDriver is installed and in PATH")
            raise
    
    def _load_frontend(self):
        """Load the frontend HTML file"""
        # Get the path to the frontend HTML file
        current_dir = Path(__file__).parent
        frontend_dir = current_dir.parent / "frontend"
        html_file = frontend_dir / "index.html"
        
        if not html_file.exists():
            raise FileNotFoundError(f"Frontend HTML file not found: {html_file}")
        
        # Convert to file:// URL
        self.frontend_path = f"file://{html_file.resolve()}"
        
        # Load the page
        self.driver.get(self.frontend_path)
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "canvas"))
        )
        
        print(f"✅ Frontend loaded: {self.frontend_path}")
    
    def get_canvas_size(self):
        """Get current canvas size from frontend"""
        try:
            size = self.driver.execute_script("""
                const canvas = document.getElementById('canvas');
                return {
                    width: canvas.offsetWidth,
                    height: canvas.offsetHeight
                };
            """)
            return size
        except:
            return {"width": 800, "height": 600}  # Fallback to default
    
    def get_existing_containers(self):
        """Get positions and sizes of all existing containers"""
        try:
            containers = self.driver.execute_script("""
                const containers = [];
                for (const [id, container] of window.canvasState.containers) {
                    containers.push({
                        id: id,
                        x: container.x,
                        y: container.y,
                        width: container.width,
                        height: container.height
                    });
                }
                return containers;
            """)
            return containers
        except:
            return []
    
    def check_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2):
        """Check if two rectangles overlap"""
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)
    
    def find_non_overlapping_position(self, width, height, canvas_width, canvas_height, existing_containers, preferred_x=None, preferred_y=None):
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
        
        # If still no position found, return top-left corner (last resort)
        return 0, 0
    
    def get_current_state(self):
        """
        Get the current state of the canvas
        
        Returns:
            dict: Canvas state with container information
        """
        try:
            # Execute JavaScript to get state
            state = self.driver.execute_script("return window.canvasAPI.getState();")
            
            print(f"📊 Canvas State:")
            print(f"   - Has containers: {state['hasContainers']}")
            print(f"   - Container count: {state['containerCount']}")
            
            if state['containers']:
                print("   - Containers:")
                for container in state['containers']:
                    print(f"     * {container['id']}: pos({container['x']}, {container['y']}) size({container['width']}x{container['height']})")
            
            return state
            
        except Exception as e:
            print(f"❌ Error getting canvas state: {e}")
            return None
    
    def create_container(self, container_id, x, y, width, height, auto_adjust=True, avoid_overlap=True):
        """
        Create a new container on the canvas
        
        Args:
            container_id (str): Unique identifier for the container
            x (int): X position in pixels
            y (int): Y position in pixels  
            width (int): Width in pixels
            height (int): Height in pixels
            auto_adjust (bool): Whether to automatically adjust position/size to fit canvas
            avoid_overlap (bool): Whether to automatically avoid overlapping with existing containers
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate inputs
            if not isinstance(container_id, str) or not container_id.strip():
                raise ValueError("Container ID must be a non-empty string")
            
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
            else:
                # Just warn if container extends beyond bounds
                if x + width > canvas_width or y + height > canvas_height:
                    print(f"⚠️  Warning: Container extends beyond canvas bounds ({canvas_width}x{canvas_height})")
                    print(f"   Container: ({x}, {y}) to ({x + width}, {y + height})")
                    print(f"   Canvas: (0, 0) to ({canvas_width}, {canvas_height})")
            
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
                    
                    if new_x != x or new_y != y:
                        print(f"🔄 Found non-overlapping position: ({x}, {y}) → ({new_x}, {new_y})")
                        x, y = new_x, new_y
                    else:
                        print(f"⚠️  Could not find completely non-overlapping position")
            elif not avoid_overlap and existing_containers:
                # Just warn about overlaps
                overlapping_containers = []
                for container in existing_containers:
                    if self.check_overlap(x, y, width, height,
                                        container['x'], container['y'], container['width'], container['height']):
                        overlapping_containers.append(container['id'])
                
                if overlapping_containers:
                    print(f"⚠️  Warning: Container will overlap with: {', '.join(overlapping_containers)}")
            
            # Execute JavaScript to create container
            result = self.driver.execute_script(
                "return window.canvasAPI.createContainer(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4]);",
                container_id, x, y, width, height
            )
            
            if result:
                adjustments = []
                if auto_adjust and (width != original_width or height != original_height):
                    adjustments.append("size-adjusted")
                if auto_adjust and (x != original_x or y != original_y):
                    adjustments.append("position-adjusted")
                if avoid_overlap and existing_containers and (x != original_x or y != original_y):
                    adjustments.append("overlap-avoided")
                
                if adjustments:
                    adjustment_text = ", ".join(adjustments)
                    print(f"✅ Container '{container_id}' created at ({x}, {y}) with size {width}x{height} ({adjustment_text})")
                else:
                    print(f"✅ Container '{container_id}' created at ({x}, {y}) with size {width}x{height}")
            else:
                print(f"❌ Failed to create container '{container_id}'")
            
            return result
            
        except Exception as e:
            print(f"❌ Error creating container: {e}")
            return False
    
    def delete_container(self, container_id):
        """
        Delete a container from the canvas
        
        Args:
            container_id (str): ID of the container to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not isinstance(container_id, str) or not container_id.strip():
                raise ValueError("Container ID must be a non-empty string")
            
            # Execute JavaScript to delete container
            result = self.driver.execute_script(
                "return window.canvasAPI.deleteContainer(arguments[0]);",
                container_id
            )
            
            if result:
                print(f"✅ Container '{container_id}' deleted successfully")
            else:
                print(f"❌ Container '{container_id}' not found or could not be deleted")
            
            return result
            
        except Exception as e:
            print(f"❌ Error deleting container: {e}")
            return False
    
    def modify_container(self, container_id, x, y, width, height, auto_adjust=True, avoid_overlap=True):
        """
        Modify an existing container's position and size
        
        Args:
            container_id (str): ID of the container to modify
            x (int): New X position in pixels
            y (int): New Y position in pixels
            width (int): New width in pixels
            height (int): New height in pixels
            auto_adjust (bool): Whether to automatically adjust position/size to fit canvas
            avoid_overlap (bool): Whether to automatically avoid overlapping with existing containers
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate inputs
            if not isinstance(container_id, str) or not container_id.strip():
                raise ValueError("Container ID must be a non-empty string")
            
            if not all(isinstance(val, (int, float)) and val >= 0 for val in [x, y, width, height]):
                raise ValueError("Position and size values must be non-negative numbers")
            
            # Get current canvas size and existing containers
            canvas_size = self.get_canvas_size()
            canvas_width = canvas_size.get('width', 800)
            canvas_height = canvas_size.get('height', 600)
            existing_containers = self.get_existing_containers()
            
            # Filter out the container being modified from overlap checking
            existing_containers = [c for c in existing_containers if c['id'] != container_id]
            
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
            else:
                # Just warn if container extends beyond bounds
                if x + width > canvas_width or y + height > canvas_height:
                    print(f"⚠️  Warning: Modified container extends beyond canvas bounds ({canvas_width}x{canvas_height})")
                    print(f"   Container: ({x}, {y}) to ({x + width}, {y + height})")
                    print(f"   Canvas: (0, 0) to ({canvas_width}, {canvas_height})")
            
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
                    print(f"🚫 Position ({x}, {y}) would overlap with: {', '.join(overlapping_containers)}")
                    
                    # Find a non-overlapping position
                    new_x, new_y = self.find_non_overlapping_position(
                        width, height, canvas_width, canvas_height, existing_containers, x, y
                    )
                    
                    if new_x != x or new_y != y:
                        print(f"🔄 Found non-overlapping position: ({x}, {y}) → ({new_x}, {new_y})")
                        x, y = new_x, new_y
                    else:
                        print(f"⚠️  Could not find completely non-overlapping position")
            elif not avoid_overlap and existing_containers:
                # Just warn about overlaps
                overlapping_containers = []
                for container in existing_containers:
                    if self.check_overlap(x, y, width, height,
                                        container['x'], container['y'], container['width'], container['height']):
                        overlapping_containers.append(container['id'])
                
                if overlapping_containers:
                    print(f"⚠️  Warning: Container will overlap with: {', '.join(overlapping_containers)}")
            
            # Execute JavaScript to modify container
            result = self.driver.execute_script(
                "return window.canvasAPI.modifyContainer(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4]);",
                container_id, x, y, width, height
            )
            
            if result:
                adjustments = []
                if auto_adjust and (width != original_width or height != original_height):
                    adjustments.append("size-adjusted")
                if auto_adjust and (x != original_x or y != original_y):
                    adjustments.append("position-adjusted")
                if avoid_overlap and existing_containers and (x != original_x or y != original_y):
                    adjustments.append("overlap-avoided")
                
                if adjustments:
                    adjustment_text = ", ".join(adjustments)
                    print(f"✅ Container '{container_id}' modified to pos({x}, {y}) size({width}x{height}) ({adjustment_text})")
                else:
                    print(f"✅ Container '{container_id}' modified to pos({x}, {y}) size({width}x{height})")
            else:
                print(f"❌ Container '{container_id}' not found or could not be modified")
            
            return result
            
        except Exception as e:
            print(f"❌ Error modifying container: {e}")
            return False
    
    def clear_canvas(self):
        """
        Remove all containers from the canvas
        
        Returns:
            bool: True if successful
        """
        try:
            state = self.get_current_state()
            if not state or not state['hasContainers']:
                print("📭 Canvas is already empty")
                return True
            
            # Delete all containers
            success_count = 0
            for container in state['containers']:
                if self.delete_container(container['id']):
                    success_count += 1
            
            print(f"🧹 Cleared {success_count} containers from canvas")
            return success_count == len(state['containers'])
            
        except Exception as e:
            print(f"❌ Error clearing canvas: {e}")
            return False
    
    def take_screenshot(self, filename=None):
        """
        Take a screenshot of the current canvas state
        
        Args:
            filename (str): Optional filename for the screenshot
            
        Returns:
            str: Path to the saved screenshot
        """
        try:
            if filename is None:
                timestamp = int(time.time())
                filename = f"canvas_screenshot_{timestamp}.png"
            
            # Ensure screenshots directory exists
            screenshots_dir = Path(__file__).parent / "screenshots"
            screenshots_dir.mkdir(exist_ok=True)
            
            screenshot_path = screenshots_dir / filename
            
            # Take screenshot
            self.driver.save_screenshot(str(screenshot_path))
            
            print(f"📸 Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            print(f"❌ Error taking screenshot: {e}")
            return None
    
    def close(self):
        """Close the browser and cleanup resources"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")


def demo_usage():
    """Demonstrate the canvas controller functionality"""
    print("🚀 Starting Canvas Controller Demo")
    
    # Initialize controller
    controller = CanvasController(headless=False)  # Set to True for headless mode
    
    try:
        # Get initial state
        print("\n1. Getting initial state:")
        controller.get_current_state()
        
        # Create some containers
        print("\n2. Creating containers:")
        controller.create_container("container_1", 50, 50, 200, 150)
        controller.create_container("container_2", 300, 100, 150, 100)
        controller.create_container("container_3", 100, 250, 250, 120)
        
        # Get state after creation
        print("\n3. State after creation:")
        controller.get_current_state()
        
        # Take a screenshot
        print("\n4. Taking screenshot:")
        controller.take_screenshot("demo_with_containers.png")
        
        # Modify a container
        print("\n5. Modifying container_2:")
        controller.modify_container("container_2", 400, 200, 180, 120)
        
        # Delete a container
        print("\n6. Deleting container_1:")
        controller.delete_container("container_1")
        
        # Final state
        print("\n7. Final state:")
        controller.get_current_state()
        
        # Keep browser open for a moment to see results
        print("\n8. Keeping browser open for 5 seconds...")
        time.sleep(5)
        
    finally:
        # Cleanup
        controller.close()
    
    print("✅ Demo completed!")


if __name__ == "__main__":
    demo_usage() 