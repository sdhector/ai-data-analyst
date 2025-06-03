"""
Test script to verify overlap prevention functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from canvas_controller import CanvasController

def test_overlap_prevention():
    """Test overlap prevention functionality"""
    print("🧪 Testing Overlap Prevention Functionality")
    print("=" * 50)
    
    # Initialize controller
    controller = CanvasController(headless=False)
    
    try:
        # Clear canvas first
        print("\n1. Clearing canvas...")
        controller.clear_canvas()
        
        # Test 1: Create first container
        print("\n2. Creating first container...")
        result1 = controller.create_container("test1", 100, 100, 200, 150, avoid_overlap=True)
        print(f"   Result: {result1}")
        
        # Test 2: Try to create overlapping container (should be repositioned)
        print("\n3. Creating overlapping container (should be repositioned)...")
        result2 = controller.create_container("test2", 150, 120, 180, 130, avoid_overlap=True)
        print(f"   Result: {result2}")
        
        # Test 3: Try to create overlapping container with avoid_overlap=False
        print("\n4. Creating overlapping container with overlap allowed...")
        result3 = controller.create_container("test3", 120, 110, 160, 140, avoid_overlap=False)
        print(f"   Result: {result3}")
        
        # Test 4: Check final state
        print("\n5. Final canvas state:")
        state = controller.get_current_state()
        
        # Test 5: Test modify with overlap prevention
        print("\n6. Testing modify with overlap prevention...")
        if state and state['containers']:
            # Try to move test1 to overlap with test2
            result4 = controller.modify_container("test1", 50, 50, 200, 150, avoid_overlap=True)
            print(f"   Modify result: {result4}")
        
        # Test 6: Final state after modification
        print("\n7. Final state after modification:")
        controller.get_current_state()
        
        # Test overlap detection algorithm directly
        print("\n8. Testing overlap detection algorithm directly:")
        test_overlap_algorithm(controller)
        
        # Test 7: Critical edge case - canvas-sized containers
        print("\n9. Testing critical edge case - canvas-sized containers:")
        test_canvas_sized_containers(controller)
        
        print("\n✅ Overlap prevention test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        input("\nPress Enter to close browser...")
        controller.close()

def test_overlap_algorithm(controller):
    """Test the overlap detection algorithm directly"""
    print("   Testing overlap detection:")
    
    # Test cases: (x1, y1, w1, h1, x2, y2, w2, h2, expected_overlap)
    test_cases = [
        (0, 0, 100, 100, 50, 50, 100, 100, True),   # Overlapping
        (0, 0, 100, 100, 100, 100, 100, 100, False), # Touching corners (no overlap)
        (0, 0, 100, 100, 200, 200, 100, 100, False), # Completely separate
        (0, 0, 100, 100, 50, 0, 100, 100, True),    # Overlapping horizontally
        (0, 0, 100, 100, 0, 50, 100, 100, True),    # Overlapping vertically
        (10, 10, 80, 80, 0, 0, 100, 100, True),     # One inside another
    ]
    
    for i, (x1, y1, w1, h1, x2, y2, w2, h2, expected) in enumerate(test_cases):
        result = controller.check_overlap(x1, y1, w1, h1, x2, y2, w2, h2)
        status = "✅" if result == expected else "❌"
        print(f"   {status} Test {i+1}: Rect1({x1},{y1},{w1}x{h1}) vs Rect2({x2},{y2},{w2}x{h2}) = {result} (expected {expected})")

def test_position_finding(controller):
    """Test the position finding algorithm"""
    print("\n9. Testing position finding algorithm:")
    
    # Create some existing containers for testing
    existing = [
        {'id': 'existing1', 'x': 0, 'y': 0, 'width': 100, 'height': 100},
        {'id': 'existing2', 'x': 200, 'y': 0, 'width': 100, 'height': 100},
        {'id': 'existing3', 'x': 0, 'y': 200, 'width': 100, 'height': 100},
    ]
    
    # Test finding position for a 50x50 container
    new_x, new_y = controller.find_non_overlapping_position(
        50, 50, 800, 600, existing, preferred_x=50, preferred_y=50
    )
    
    print(f"   Found position for 50x50 container: ({new_x}, {new_y})")
    
    # Verify the found position doesn't overlap
    overlaps = False
    for container in existing:
        if controller.check_overlap(new_x, new_y, 50, 50,
                                  container['x'], container['y'], container['width'], container['height']):
            overlaps = True
            break
    
    print(f"   Position overlaps with existing: {overlaps}")

def test_canvas_sized_containers(controller):
    """Test the critical edge case with canvas-sized containers"""
    print("   🚨 CRITICAL TEST: Canvas-sized containers")
    
    # Clear canvas first
    controller.clear_canvas()
    
    # Get canvas size
    canvas_size = controller.get_canvas_size()
    canvas_width = canvas_size.get('width', 800)
    canvas_height = canvas_size.get('height', 600)
    
    print(f"   Canvas size: {canvas_width}x{canvas_height}")
    
    # Test 1: Create first canvas-sized container
    print(f"\n   Test 1: Creating first canvas-sized container ({canvas_width}x{canvas_height})...")
    result1 = controller.create_container("canvas_full_1", 0, 0, canvas_width, canvas_height, avoid_overlap=True)
    print(f"   Result: {result1}")
    
    # Test 2: Try to create second canvas-sized container (SHOULD FAIL or be rejected)
    print(f"\n   Test 2: Creating second canvas-sized container ({canvas_width}x{canvas_height})...")
    print("   ⚠️  This should either FAIL or be rejected due to no available space!")
    result2 = controller.create_container("canvas_full_2", 0, 0, canvas_width, canvas_height, avoid_overlap=True)
    print(f"   Result: {result2}")
    
    # Check final state
    print("\n   Final state after canvas-sized container test:")
    state = controller.get_current_state()
    
    if state and len(state['containers']) > 1:
        print("   ❌ PROBLEM: Multiple canvas-sized containers were created!")
        print("   ❌ This means overlap prevention failed for impossible scenarios!")
        
        # Check if they actually overlap
        containers = state['containers']
        if len(containers) >= 2:
            c1, c2 = containers[0], containers[1]
            overlaps = controller.check_overlap(
                c1['x'], c1['y'], c1['width'], c1['height'],
                c2['x'], c2['y'], c2['width'], c2['height']
            )
            print(f"   ❌ Containers overlap: {overlaps}")
            print(f"   Container 1: pos({c1['x']}, {c1['y']}) size({c1['width']}x{c1['height']})")
            print(f"   Container 2: pos({c2['x']}, {c2['y']}) size({c2['width']}x{c2['height']})")
    else:
        print("   ✅ Good: Only one container was created (as expected)")
    
    # Test 3: Try with smaller but still problematic sizes
    print(f"\n   Test 3: Creating large containers that can't both fit...")
    controller.clear_canvas()
    
    # Create a container that takes up most of the canvas
    large_width = int(canvas_width * 0.8)
    large_height = int(canvas_height * 0.8)
    
    result3 = controller.create_container("large_1", 0, 0, large_width, large_height, avoid_overlap=True)
    print(f"   Created large container 1 ({large_width}x{large_height}): {result3}")
    
    # Try to create another large container
    result4 = controller.create_container("large_2", 100, 100, large_width, large_height, avoid_overlap=True)
    print(f"   Created large container 2 ({large_width}x{large_height}): {result4}")
    
    # Check if they overlap
    final_state = controller.get_current_state()
    if final_state and len(final_state['containers']) >= 2:
        containers = final_state['containers']
        c1, c2 = containers[0], containers[1]
        overlaps = controller.check_overlap(
            c1['x'], c1['y'], c1['width'], c1['height'],
            c2['x'], c2['y'], c2['width'], c2['height']
        )
        print(f"   Large containers overlap: {overlaps}")
        if overlaps:
            print("   ❌ PROBLEM: Large containers overlap despite overlap prevention!")

if __name__ == "__main__":
    test_overlap_prevention() 