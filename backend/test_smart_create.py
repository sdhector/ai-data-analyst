"""
Test Smart Container Creation System
Tests the enhanced create_container function that automatically adapts based on layout mode.
"""

import asyncio
from core.function_executor import coreFunctionExecutor

async def test_smart_container():
    print('🧪 Testing Smart Container Creation System')
    
    # Initialize executor
    executor = coreFunctionExecutor()
    
    # Test 1: Check current layout mode
    print('\n📋 Current layout state:')
    result = await executor.execute_function_call('get_layout_mode', {})
    print(f'Layout mode: {result.get("current_mode", "unknown")}')
    print(f'Auto-layout enabled: {result.get("auto_layout_enabled", "unknown")}')
    
    # Test 2: Try creating container with just ID (should use auto-layout)
    print('\n🚀 Testing auto-layout (container_id only):')
    result = await executor.execute_function_call('create_container', {'container_id': 'test_smart_container'})
    print(f'Status: {result.get("status")}')
    print(f'Message: {result.get("message", "No message")}')
    if result.get('status') == 'success':
        container = result.get('container', {})
        print(f'✅ Container created at ({container.get("x")}, {container.get("y")}) with size {container.get("width")}x{container.get("height")}')
        layout_info = result.get('layout_info', {})
        print(f'Mode used: {layout_info.get("mode_used", "unknown")}')
    else:
        print('❌ Container creation failed')
        print(f'Error: {result.get("error", "unknown")}')
        
    # Test 3: Switch to manual mode and test
    print('\n🔧 Switching to manual mode:')
    result = await executor.execute_function_call('set_layout_mode', {'mode': 'manual'})
    print(f'Status: {result.get("status")}')
    
    # Test 4: Try creating container with just ID in manual mode (should fail)
    print('\n⚠️ Testing manual mode requirement (should fail with just container_id):')
    result = await executor.execute_function_call('create_container', {'container_id': 'test_manual_fail'})
    print(f'Status: {result.get("status")}')
    print(f'Message: {result.get("message", "No message")}')
    if result.get('status') == 'error':
        print('✅ Correctly rejected incomplete parameters in manual mode')
        missing = result.get('missing_parameters', [])
        print(f'Missing parameters: {missing}')
    
    # Test 5: Create container with all parameters in manual mode
    print('\n📍 Testing manual mode with all parameters:')
    result = await executor.execute_function_call('create_container', {
        'container_id': 'test_manual_complete',
        'x': 400,
        'y': 300,
        'width': 200,
        'height': 150
    })
    print(f'Status: {result.get("status")}')
    if result.get('status') == 'success':
        container = result.get('container', {})
        print(f'✅ Manual container created at ({container.get("x")}, {container.get("y")}) with size {container.get("width")}x{container.get("height")}')
        layout_info = result.get('layout_info', {})
        print(f'Mode used: {layout_info.get("mode_used", "unknown")}')
    
    print('\n🎯 Smart Container System Test Complete!')

if __name__ == "__main__":
    asyncio.run(test_smart_container()) 