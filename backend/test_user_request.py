"""
Test User Request: "Create Two Containers"
Simulates what should happen when user asks to create two containers
"""

import asyncio
from core.function_executor import coreFunctionExecutor

async def test_create_two_containers():
    print('🧪 Testing User Request: "Create Two Containers"')
    print('This simulates what the LLM should do when user says "create two containers"')
    
    executor = coreFunctionExecutor()
    
    # Check current layout state
    print('\n📋 Current layout state:')
    result = await executor.execute_function_call('get_layout_mode', {})
    print(f'Layout mode: {result.get("current_mode", "unknown")}')
    print(f'Auto-layout enabled: {result.get("auto_layout_enabled", "unknown")}')
    
    # What the LLM SHOULD do: Just call create_container with auto-generated IDs
    print('\n🚀 Creating first container (what LLM should do):')
    result1 = await executor.execute_function_call('create_container', {
        'container_id': 'container_1'  # Auto-generated ID
    })
    print(f'Status: {result1.get("status")}')
    if result1.get('status') == 'success':
        container = result1.get('container', {})
        print(f'✅ Container 1 created at ({container.get("x")}, {container.get("y")}) with size {container.get("width")}x{container.get("height")}')
    
    print('\n🚀 Creating second container:')
    result2 = await executor.execute_function_call('create_container', {
        'container_id': 'container_2'  # Auto-generated ID
    })
    print(f'Status: {result2.get("status")}')
    if result2.get('status') == 'success':
        container = result2.get('container', {})
        print(f'✅ Container 2 created at ({container.get("x")}, {container.get("y")}) with size {container.get("width")}x{container.get("height")}')
    
    print('\n🎯 This is what the LLM should do automatically!')
    print('If it\'s asking for manual details, there\'s a problem with:')
    print('1. Function description clarity')  
    print('2. LLM understanding of the auto-layout capabilities')
    print('3. ID generation strategy')

if __name__ == "__main__":
    asyncio.run(test_create_two_containers()) 