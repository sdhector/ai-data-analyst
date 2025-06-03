"""
Interactive Canvas Controller Test Menu
Provides a user-friendly interface to test different canvas operations
"""

from canvas_controller import CanvasController
import time
import sys

class InteractiveCanvasTester:
    def __init__(self):
        self.controller = None
        self.running = True
        self.auto_adjust = True  # Default: auto-adjust containers to fit canvas
        self.avoid_overlap = True  # Default: avoid overlapping containers
    
    def display_menu(self):
        """Display the main menu options"""
        print("\n" + "="*60)
        print("🎯 INTERACTIVE CANVAS CONTROLLER TEST MENU")
        print("="*60)
        print("1. 🚀 Quick Setup Test (verify everything works)")
        print("2. 🎨 Manual Container Creation")
        print("3. 📊 View Current Canvas State")
        print("4. ✏️  Modify Existing Container")
        print("5. 🗑️  Delete Container")
        print("6. 🧹 Clear All Containers")
        print("7. 📸 Take Screenshot")
        print("8. 📐 Edit Canvas Size")
        print(f"9. 🔧 Toggle Auto-Adjust ({'ON' if self.auto_adjust else 'OFF'})")
        print(f"10. 🚫 Toggle Overlap Prevention ({'ON' if self.avoid_overlap else 'OFF'})")
        print("11. 🎪 Run Full Demo")
        print("12. 🔄 Restart Browser")
        print("13. ❓ Help & Instructions")
        print("0. 🚪 Exit")
        print("="*60)
    
    def get_user_choice(self):
        """Get and validate user menu choice"""
        try:
            choice = input("Enter your choice (0-13): ").strip()
            return int(choice) if choice.isdigit() else -1
        except (ValueError, KeyboardInterrupt):
            return -1
    
    def initialize_browser(self):
        """Initialize the browser if not already done"""
        if self.controller is None:
            print("\n🔧 Initializing browser...")
            try:
                headless = input("Run in headless mode? (y/N): ").strip().lower() == 'y'
                self.controller = CanvasController(headless=headless)
                print("✅ Browser initialized successfully!")
                return True
            except Exception as e:
                print(f"❌ Failed to initialize browser: {e}")
                return False
        return True
    
    def quick_setup_test(self):
        """Run a quick test to verify everything works"""
        print("\n🧪 Running Quick Setup Test...")
        
        if not self.initialize_browser():
            return
        
        try:
            # Get initial state
            print("1. Getting initial state...")
            state = self.controller.get_current_state()
            
            # Create test container
            print("2. Creating test container...")
            success = self.controller.create_container("quick_test", 150, 150, 180, 120)
            
            if success:
                print("3. Verifying container...")
                state = self.controller.get_current_state()
                if state and state['containerCount'] > 0:
                    print("✅ Quick test passed! Everything is working correctly.")
                    
                    # Clean up
                    cleanup = input("Remove test container? (Y/n): ").strip().lower()
                    if cleanup != 'n':
                        self.controller.delete_container("quick_test")
                        print("🧹 Test container removed.")
                else:
                    print("❌ Container verification failed.")
            else:
                print("❌ Quick test failed.")
                
        except Exception as e:
            print(f"❌ Quick test error: {e}")
    
    def manual_container_creation(self):
        """Interactive container creation"""
        print("\n🎨 Manual Container Creation")
        
        if not self.initialize_browser():
            return
        
        try:
            # Get container details from user
            container_id = input("Enter container ID: ").strip()
            if not container_id:
                print("❌ Container ID cannot be empty.")
                return
            
            # Get current canvas size
            canvas_size = self.get_canvas_size()
            print(f"Enter position and size (canvas is {canvas_size['width']}x{canvas_size['height']}):")
            x = int(input(f"X position (0-{canvas_size['width']}): "))
            y = int(input(f"Y position (0-{canvas_size['height']}): "))
            width = int(input("Width (pixels): "))
            height = int(input("Height (pixels): "))
            
            # Validate inputs
            if x < 0 or y < 0 or width <= 0 or height <= 0:
                print("❌ Invalid values. All values must be positive.")
                return
            
            # Create container
            success = self.controller.create_container(container_id, x, y, width, height, self.auto_adjust, self.avoid_overlap)
            
            if success:
                print(f"✅ Container '{container_id}' created successfully!")
            else:
                print(f"❌ Failed to create container '{container_id}'.")
                
        except ValueError:
            print("❌ Invalid input. Please enter numeric values for position and size.")
        except Exception as e:
            print(f"❌ Error creating container: {e}")
    
    def view_canvas_state(self):
        """Display current canvas state"""
        print("\n📊 Current Canvas State")
        
        if not self.initialize_browser():
            return
        
        try:
            state = self.controller.get_current_state()
            if state:
                print(f"Canvas has {state['containerCount']} containers")
                if state['containers']:
                    print("\nContainer Details:")
                    for i, container in enumerate(state['containers'], 1):
                        print(f"  {i}. ID: {container['id']}")
                        print(f"     Position: ({container['x']}, {container['y']})")
                        print(f"     Size: {container['width']}x{container['height']}px")
                        print()
                else:
                    print("📭 Canvas is empty.")
            else:
                print("❌ Could not retrieve canvas state.")
                
        except Exception as e:
            print(f"❌ Error getting canvas state: {e}")
    
    def modify_container(self):
        """Interactive container modification"""
        print("\n✏️  Modify Existing Container")
        
        if not self.initialize_browser():
            return
        
        try:
            # Show current containers
            state = self.controller.get_current_state()
            if not state or not state['containers']:
                print("📭 No containers to modify.")
                return
            
            print("Available containers:")
            for i, container in enumerate(state['containers'], 1):
                print(f"  {i}. {container['id']} - pos({container['x']}, {container['y']}) size({container['width']}x{container['height']})")
            
            # Get container to modify
            container_id = input("\nEnter container ID to modify: ").strip()
            
            # Check if container exists
            container_exists = any(c['id'] == container_id for c in state['containers'])
            if not container_exists:
                print(f"❌ Container '{container_id}' not found.")
                return
            
            # Get new values
            print("Enter new position and size:")
            x = int(input("New X position: "))
            y = int(input("New Y position: "))
            width = int(input("New width: "))
            height = int(input("New height: "))
            
            # Modify container
            success = self.controller.modify_container(container_id, x, y, width, height, self.auto_adjust, self.avoid_overlap)
            
            if success:
                print(f"✅ Container '{container_id}' modified successfully!")
            else:
                print(f"❌ Failed to modify container '{container_id}'.")
                
        except ValueError:
            print("❌ Invalid input. Please enter numeric values.")
        except Exception as e:
            print(f"❌ Error modifying container: {e}")
    
    def delete_container(self):
        """Interactive container deletion"""
        print("\n🗑️  Delete Container")
        
        if not self.initialize_browser():
            return
        
        try:
            # Show current containers
            state = self.controller.get_current_state()
            if not state or not state['containers']:
                print("📭 No containers to delete.")
                return
            
            print("Available containers:")
            for i, container in enumerate(state['containers'], 1):
                print(f"  {i}. {container['id']}")
            
            # Get container to delete
            container_id = input("\nEnter container ID to delete: ").strip()
            
            # Confirm deletion
            confirm = input(f"Are you sure you want to delete '{container_id}'? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Deletion cancelled.")
                return
            
            # Delete container
            success = self.controller.delete_container(container_id)
            
            if success:
                print(f"✅ Container '{container_id}' deleted successfully!")
            else:
                print(f"❌ Container '{container_id}' not found or could not be deleted.")
                
        except Exception as e:
            print(f"❌ Error deleting container: {e}")
    
    def clear_all_containers(self):
        """Clear all containers from canvas"""
        print("\n🧹 Clear All Containers")
        
        if not self.initialize_browser():
            return
        
        try:
            state = self.controller.get_current_state()
            if not state or not state['containers']:
                print("📭 Canvas is already empty.")
                return
            
            print(f"Found {state['containerCount']} containers.")
            confirm = input("Are you sure you want to delete ALL containers? (y/N): ").strip().lower()
            
            if confirm != 'y':
                print("❌ Clear operation cancelled.")
                return
            
            success = self.controller.clear_canvas()
            if success:
                print("✅ All containers cleared successfully!")
            else:
                print("❌ Failed to clear all containers.")
                
        except Exception as e:
            print(f"❌ Error clearing canvas: {e}")
    
    def take_screenshot(self):
        """Take a screenshot of current canvas"""
        print("\n📸 Take Screenshot")
        
        if not self.initialize_browser():
            return
        
        try:
            filename = input("Enter filename (or press Enter for auto-generated): ").strip()
            if not filename:
                filename = None
            
            screenshot_path = self.controller.take_screenshot(filename)
            if screenshot_path:
                print(f"✅ Screenshot saved: {screenshot_path}")
            else:
                print("❌ Failed to take screenshot.")
                
        except Exception as e:
            print(f"❌ Error taking screenshot: {e}")
    
    def get_canvas_size(self):
        """Get current canvas size from frontend"""
        if not self.controller:
            return {"width": 800, "height": 600}  # Default size
        
        try:
            size = self.controller.driver.execute_script("""
                const canvas = document.getElementById('canvas');
                return {
                    width: canvas.offsetWidth,
                    height: canvas.offsetHeight
                };
            """)
            return size
        except:
            return {"width": 800, "height": 600}  # Fallback
    
    def edit_canvas_size(self):
        """Interactive canvas size editing"""
        print("\n📐 Edit Canvas Size")
        
        if not self.initialize_browser():
            return
        
        try:
            # Show current size
            current_size = self.get_canvas_size()
            print(f"Current canvas size: {current_size['width']}x{current_size['height']} pixels")
            
            # Get new size from user
            print("\nEnter new canvas dimensions:")
            new_width = int(input(f"New width (current: {current_size['width']}): "))
            new_height = int(input(f"New height (current: {current_size['height']}): "))
            
            # Validate inputs
            if new_width <= 0 or new_height <= 0:
                print("❌ Canvas dimensions must be positive numbers.")
                return
            
            if new_width < 200 or new_height < 200:
                print("❌ Canvas dimensions should be at least 200x200 pixels for usability.")
                return
            
            if new_width > 2000 or new_height > 2000:
                print("❌ Canvas dimensions should not exceed 2000x2000 pixels.")
                return
            
            # Confirm change
            print(f"\nChanging canvas size from {current_size['width']}x{current_size['height']} to {new_width}x{new_height}")
            confirm = input("Continue? (y/N): ").strip().lower()
            
            if confirm != 'y':
                print("❌ Canvas size change cancelled.")
                return
            
            # Apply new size
            success = self.controller.driver.execute_script(f"""
                const canvas = document.getElementById('canvas');
                canvas.style.width = '{new_width}px';
                canvas.style.height = '{new_height}px';
                
                // Update any containers that might be outside new bounds
                const containers = document.querySelectorAll('.container');
                let adjustedCount = 0;
                
                containers.forEach(container => {{
                    const rect = container.getBoundingClientRect();
                    const canvasRect = canvas.getBoundingClientRect();
                    
                    let left = parseInt(container.style.left) || 0;
                    let top = parseInt(container.style.top) || 0;
                    let width = parseInt(container.style.width) || 100;
                    let height = parseInt(container.style.height) || 100;
                    
                    let adjusted = false;
                    
                    // Adjust if container extends beyond new canvas bounds
                    if (left + width > {new_width}) {{
                        if (width <= {new_width}) {{
                            left = {new_width} - width;
                        }} else {{
                            left = 0;
                            width = {new_width};
                        }}
                        adjusted = true;
                    }}
                    
                    if (top + height > {new_height}) {{
                        if (height <= {new_height}) {{
                            top = {new_height} - height;
                        }} else {{
                            top = 0;
                            height = {new_height};
                        }}
                        adjusted = true;
                    }}
                    
                    if (adjusted) {{
                        container.style.left = left + 'px';
                        container.style.top = top + 'px';
                        container.style.width = width + 'px';
                        container.style.height = height + 'px';
                        
                        // Update stored data
                        const containerId = container.id;
                        if (window.canvasState.containers.has(containerId)) {{
                            const containerData = window.canvasState.containers.get(containerId);
                            containerData.x = left;
                            containerData.y = top;
                            containerData.width = width;
                            containerData.height = height;
                        }}
                        
                        adjustedCount++;
                    }}
                }});
                
                // Update state display
                if (typeof updateStateDisplay === 'function') {{
                    updateStateDisplay();
                }}
                
                return adjustedCount;
            """)
            
            print(f"✅ Canvas size changed to {new_width}x{new_height} pixels!")
            
            if success > 0:
                print(f"📦 Adjusted {success} container(s) to fit within new canvas bounds.")
            
            # Show updated state
            print("\nUpdated canvas state:")
            self.view_canvas_state()
            
        except ValueError:
            print("❌ Invalid input. Please enter numeric values for dimensions.")
        except Exception as e:
            print(f"❌ Error changing canvas size: {e}")
    
    def toggle_auto_adjust(self):
        """Toggle auto-adjustment of containers to fit canvas bounds"""
        print("\n🔧 Toggle Auto-Adjust")
        
        current_status = "ON" if self.auto_adjust else "OFF"
        print(f"Current auto-adjust status: {current_status}")
        print()
        print("Auto-adjust ensures containers always fit within canvas bounds by:")
        print("  📏 Resizing containers that are too large")
        print("  📍 Repositioning containers that extend beyond edges")
        print("  🔒 Preventing negative positions")
        print()
        
        self.auto_adjust = not self.auto_adjust
        new_status = "ON" if self.auto_adjust else "OFF"
        
        print(f"✅ Auto-adjust toggled: {current_status} → {new_status}")
        
        if self.auto_adjust:
            print("🔧 Containers will now be automatically adjusted to fit canvas bounds")
        else:
            print("⚠️  Containers may now be placed outside canvas bounds (warnings only)")
    
    def toggle_overlap_prevention(self):
        """Toggle overlap prevention for containers"""
        print("\n🚫 Toggle Overlap Prevention")
        
        current_status = "ON" if self.avoid_overlap else "OFF"
        print(f"Current overlap prevention status: {current_status}")
        print()
        print("Overlap prevention automatically finds non-overlapping positions by:")
        print("  🔍 Detecting overlaps with existing containers")
        print("  📍 Finding alternative positions using grid search")
        print("  🎯 Prioritizing positions close to the requested location")
        print()
        
        self.avoid_overlap = not self.avoid_overlap
        new_status = "ON" if self.avoid_overlap else "OFF"
        
        print(f"✅ Overlap prevention toggled: {current_status} → {new_status}")
        
        if self.avoid_overlap:
            print("🚫 Containers will now automatically avoid overlapping with existing ones")
        else:
            print("⚠️  Containers may now overlap with existing ones (warnings only)")
    
    def run_full_demo(self):
        """Run the full demo"""
        print("\n🎪 Running Full Demo")
        
        if not self.initialize_browser():
            return
        
        try:
            print("This will create multiple containers, modify them, and take screenshots.")
            confirm = input("Continue? (Y/n): ").strip().lower()
            
            if confirm == 'n':
                print("❌ Demo cancelled.")
                return
            
            # Clear canvas first
            self.controller.clear_canvas()
            
            # Create containers
            print("Creating containers...")
            self.controller.create_container("demo_1", 50, 50, 200, 150)
            time.sleep(1)
            self.controller.create_container("demo_2", 300, 100, 150, 100)
            time.sleep(1)
            self.controller.create_container("demo_3", 100, 250, 250, 120)
            time.sleep(1)
            
            # Take screenshot
            self.controller.take_screenshot("demo_initial.png")
            
            # Modify a container
            print("Modifying container...")
            self.controller.modify_container("demo_2", 400, 200, 180, 120)
            time.sleep(1)
            
            # Delete a container
            print("Deleting container...")
            self.controller.delete_container("demo_1")
            time.sleep(1)
            
            # Final screenshot
            self.controller.take_screenshot("demo_final.png")
            
            print("✅ Full demo completed!")
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
    
    def restart_browser(self):
        """Restart the browser"""
        print("\n🔄 Restarting Browser")
        
        if self.controller:
            print("Closing current browser...")
            self.controller.close()
            self.controller = None
        
        print("Initializing new browser...")
        self.initialize_browser()
    
    def show_help(self):
        """Show help and instructions"""
        print("\n❓ Help & Instructions")
        print("="*50)
        print("🎯 Canvas Specifications:")
        print("   - Default size: 800x600 pixels (customizable)")
        print("   - Size range: 200x200 to 2000x2000 pixels")
        print("   - Coordinate system: Top-left origin (0,0)")
        print("   - Containers can be positioned anywhere within bounds")
        print()
        print("🎨 Container Operations:")
        print("   - Create: Specify ID, position (x,y), and size (width,height)")
        print("   - Modify: Change position and size of existing containers")
        print("   - Delete: Remove containers by ID")
        print("   - State: View all containers and their properties")
        print()
        print("📐 Canvas Operations:")
        print("   - Resize: Change canvas dimensions dynamically")
        print("   - Auto-adjust: Containers are repositioned if they exceed new bounds")
        print("   - Validation: Size limits prevent unusable dimensions")
        print()
        print("🔧 Auto-Adjust Feature:")
        print("   - ON: Containers automatically fit within canvas bounds")
        print("   - OFF: Containers can be placed outside bounds (warnings only)")
        print("   - Adjusts position, size, and prevents negative coordinates")
        print()
        print("🚫 Overlap Prevention:")
        print("   - ON: Containers automatically avoid overlapping with existing ones")
        print("   - OFF: Containers can overlap (warnings only)")
        print("   - Uses grid search to find optimal non-overlapping positions")
        print()
        print("📸 Screenshots:")
        print("   - Saved in 'screenshots/' directory")
        print("   - Auto-generated filenames include timestamp")
        print()
        print("🔧 Browser:")
        print("   - Choose headless mode for background operation")
        print("   - Visual mode shows the canvas in real-time")
        print("   - Restart browser if issues occur")
        print("="*50)
    
    def cleanup(self):
        """Clean up resources"""
        if self.controller:
            print("\n🔒 Closing browser...")
            self.controller.close()
    
    def run(self):
        """Main interactive loop"""
        print("🎯 Welcome to Interactive Canvas Controller!")
        print("This tool helps you test container placement functionality.")
        
        try:
            while self.running:
                self.display_menu()
                choice = self.get_user_choice()
                
                if choice == 0:
                    print("\n👋 Goodbye!")
                    self.running = False
                elif choice == 1:
                    self.quick_setup_test()
                elif choice == 2:
                    self.manual_container_creation()
                elif choice == 3:
                    self.view_canvas_state()
                elif choice == 4:
                    self.modify_container()
                elif choice == 5:
                    self.delete_container()
                elif choice == 6:
                    self.clear_all_containers()
                elif choice == 7:
                    self.take_screenshot()
                elif choice == 8:
                    self.edit_canvas_size()
                elif choice == 9:
                    self.toggle_auto_adjust()
                elif choice == 10:
                    self.toggle_overlap_prevention()
                elif choice == 11:
                    self.run_full_demo()
                elif choice == 12:
                    self.restart_browser()
                elif choice == 13:
                    self.show_help()
                else:
                    print("❌ Invalid choice. Please enter a number between 0-13.")
                
                if self.running and choice != 0:
                    input("\nPress Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user.")
        
        finally:
            self.cleanup()


if __name__ == "__main__":
    tester = InteractiveCanvasTester()
    tester.run() 