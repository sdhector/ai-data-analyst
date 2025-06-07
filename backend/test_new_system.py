"""
Test New Container Creation System
Tests the create_containers_from_request function that handles natural language requests
"""

import asyncio
from core.function_executor import coreFunctionExecutor

async def test_new_system():
    print('🧪 Testing New Container Creation System')
    
    executor = coreFunctionExecutor()
    
    # Test the new function with "create two containers"
    print('\n🚀 Testing create_containers_from_request with "create two containers":')
    result = await executor.execute_function_call('create_containers_from_request', {
        'user_request': 'create two containers'
    })
    
    print(f'Status: {result.get("status")}')
    print(f'Message: {result.get("message", "No message")}')
    print(f'Containers requested: {result.get("containers_requested", 0)}')
    print(f'Containers created: {result.get("containers_created", 0)}')
    print(f'Generated IDs: {result.get("generated_ids", [])}')
    
    if result.get("created_containers"):
        print('\n📋 Created containers:')
        for container_data in result["created_containers"]:
            container = container_data["container"]
            print(f'  • {container_data["id"]}: ({container.get("x")}, {container.get("y")}) - {container.get("width")}x{container.get("height")}')
    
    # Test with different request
    print('\n🎯 Testing with "add three chart panels":')
    result2 = await executor.execute_function_call('create_containers_from_request', {
        'user_request': 'add three chart panels'
    })
    
    print(f'Status: {result2.get("status")}')
    print(f'Generated IDs: {result2.get("generated_ids", [])}')
    
    print('\n✨ This is how the LLM should now handle container creation!')

if __name__ == "__main__":
    asyncio.run(test_new_system()) 