"""
Test Error Response Structure
Debug what the actual error response looks like from create_container
"""

import asyncio
from core.function_executor import coreFunctionExecutor

async def test_error_response():
    print("🔍 Testing create_container Error Response")
    print("=" * 50)
    
    executor = coreFunctionExecutor()
    result = await executor.execute_function_call('create_container', {
        'container_id': 'test_container'
    })
    
    print("📋 Full Result:")
    print("-" * 20)
    print(result)
    print()
    
    print("🔍 Error Analysis:")
    print("-" * 20)
    print(f"Status: {result.get('status', 'No status')}")
    print(f"Error field: {result.get('error', 'No error field')}")
    print(f"Message field: {result.get('message', 'No message field')}")
    print(f"Error code: {result.get('error_code', 'No error_code field')}")
    print()
    
    if 'suggestions' in result:
        print("💡 Suggestions:")
        for suggestion in result['suggestions']:
            print(f"  • {suggestion}")
    
    print("\n🎯 What LLM Should See:")
    print("-" * 20)
    if result.get('status') == 'error':
        if 'message' in result:
            print(f"Primary: {result['message']}")
        if 'suggestions' in result:
            print("Helpful suggestions provided ✅")
        else:
            print("No suggestions provided ❌")

if __name__ == "__main__":
    asyncio.run(test_error_response()) 