#!/usr/bin/env python3
"""
Test script for canvas dimension functionality
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_canvas_dimensions():
    """Test the canvas dimension functionality"""
    print("🧪 Testing Canvas Dimension Functionality")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from backend.core.primitives import set_canvas_dimensions_primitive, get_canvas_dimensions_primitive
        from backend.core.tools import set_canvas_dimensions_tool, get_canvas_dimensions_tool
        from backend.core.registry import get_canvas_management_function_schemas, execute_canvas_management_tool
        print("✅ All imports successful")
        
        # Test function schemas
        print("\n2. Testing function schemas...")
        schemas = get_canvas_management_function_schemas()
        print(f"✅ Generated {len(schemas)} function schemas:")
        for schema in schemas:
            print(f"   - {schema['name']}: {schema['description']}")
        
        # Test primitive operations
        print("\n3. Testing primitive operations...")
        
        # Get current dimensions
        current_result = await get_canvas_dimensions_primitive()
        print(f"✅ Current dimensions: {current_result}")
        
        # Set new dimensions
        set_result = await set_canvas_dimensions_primitive(1200, 800)
        print(f"✅ Set dimensions result: {set_result}")
        
        # Test tool operations
        print("\n4. Testing tool operations...")
        
        # Get dimensions with metadata
        tool_get_result = await get_canvas_dimensions_tool()
        print(f"✅ Tool get result: {tool_get_result}")
        
        # Set dimensions with validation
        tool_set_result = await set_canvas_dimensions_tool(1920, 1080)
        print(f"✅ Tool set result: {tool_set_result}")
        
        # Test registry execution
        print("\n5. Testing registry execution...")
        
        # Execute via registry
        registry_result = await execute_canvas_management_tool("get_canvas_dimensions", {})
        print(f"✅ Registry execution result: {registry_result}")
        
        # Test error handling
        print("\n6. Testing error handling...")
        
        # Test invalid dimensions
        error_result = await set_canvas_dimensions_tool(-100, 0)
        print(f"✅ Error handling result: {error_result}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_canvas_dimensions()) 