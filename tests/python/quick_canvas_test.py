"""
Quick test for canvas-sized container overlap prevention fix
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from canvas_controller import CanvasController

def quick_test():
    """Quick test for the canvas-sized container fix"""
    print("🧪 Quick Canvas-Sized Container Test")
    print("=" * 40)
    
    controller = CanvasController(headless=True)  # Headless for quick test
    
    try:
        # Get canvas size
        canvas_size = controller.get_canvas_size()
        width = canvas_size.get('width', 800)
        height = canvas_size.get('height', 600)
        
        print(f"Canvas size: {width}x{height}")
        
        # Test 1: Create first canvas-sized container
        print("\n1. Creating first canvas-sized container...")
        result1 = controller.create_container("full1", 0, 0, width, height, avoid_overlap=True)
        print(f"Result 1: {result1}")
        
        # Test 2: Try to create second canvas-sized container (should FAIL)
        print("\n2. Creating second canvas-sized container (should FAIL)...")
        result2 = controller.create_container("full2", 0, 0, width, height, avoid_overlap=True)
        print(f"Result 2: {result2}")
        
        # Check final state
        state = controller.get_current_state()
        container_count = len(state['containers']) if state else 0
        
        print(f"\nFinal container count: {container_count}")
        
        if container_count == 1 and not result2:
            print("✅ SUCCESS: Second container was properly rejected!")
        elif container_count > 1:
            print("❌ FAILURE: Multiple canvas-sized containers were created!")
        else:
            print("❓ UNEXPECTED: No containers were created")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    finally:
        controller.close()

if __name__ == "__main__":
    quick_test() 