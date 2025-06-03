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
        print("8. 🎪 Run Full Demo")
        print("9. 🔄 Restart Browser")
        print("10. ❓ Help & Instructions")
        print("0. 🚪 Exit")
        print("="*60)
    
    def get_user_choice(self):
        """Get and validate user menu choice"""
        try:
            choice = input("Enter your choice (0-10): ").strip()
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
            
            print("Enter position and size (canvas is 800x600):")
            x = int(input("X position (0-800): "))
            y = int(input("Y position (0-600): "))
            width = int(input("Width (pixels): "))
            height = int(input("Height (pixels): "))
            
            # Validate inputs
            if x < 0 or y < 0 or width <= 0 or height <= 0:
                print("❌ Invalid values. All values must be positive.")
                return
            
            # Create container
            success = self.controller.create_container(container_id, x, y, width, height)
            
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
            success = self.controller.modify_container(container_id, x, y, width, height)
            
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
        print("   - Size: 800x600 pixels")
        print("   - Coordinate system: Top-left origin (0,0)")
        print("   - Containers can be positioned anywhere within bounds")
        print()
        print("🎨 Container Operations:")
        print("   - Create: Specify ID, position (x,y), and size (width,height)")
        print("   - Modify: Change position and size of existing containers")
        print("   - Delete: Remove containers by ID")
        print("   - State: View all containers and their properties")
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
                    self.run_full_demo()
                elif choice == 9:
                    self.restart_browser()
                elif choice == 10:
                    self.show_help()
                else:
                    print("❌ Invalid choice. Please enter a number between 0-10.")
                
                if self.running and choice != 0:
                    input("\nPress Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user.")
        
        finally:
            self.cleanup()


if __name__ == "__main__":
    tester = InteractiveCanvasTester()
    tester.run() 