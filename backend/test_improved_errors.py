"""
Test Improved Error Reporting
Shows how errors are now communicated more clearly to the LLM
"""

import asyncio
from core.function_executor import coreFunctionExecutor

async def test_improved_errors():
    print("🔍 Testing Improved Error Reporting")
    print("=" * 60)
    
    executor = coreFunctionExecutor()
    
    # Test 1: Duplicate container ID error
    print("\n📋 Test 1: Create First Container (should succeed)")
    print("-" * 40)
    result1 = await executor.execute_function_call('create_container', {
        'container_id': 'duplicate_test'
    })
    print(f"✅ Status: {result1.get('status')}")
    
    print("\n📋 Test 2: Duplicate Container ID (should show good error)")
    print("-" * 40)
    result2 = await executor.execute_function_call('create_container', {
        'container_id': 'duplicate_test'  # Same ID!
    })
    print(f"❌ Status: {result2.get('status')}")
    print(f"💬 Message: {result2.get('message', 'No message')}")
    print(f"🔧 Error Code: {result2.get('error_code', 'No error code')}")
    if result2.get('suggestions'):
        print("💡 Suggestions:")
        for suggestion in result2['suggestions']:
            print(f"   • {suggestion}")
    
    # Test 3: Out of bounds error 
    print("\n📋 Test 3: Out of Bounds Container (should show good error)")
    print("-" * 40)
    result3 = await executor.execute_function_call('create_container', {
        'container_id': 'huge_container',
        'x': 700,
        'y': 500, 
        'width': 500,  # Too big!
        'height': 400   # Too big!
    })
    print(f"❌ Status: {result3.get('status')}")
    print(f"💬 Message: {result3.get('message', 'No message')}")
    print(f"🔧 Error Code: {result3.get('error_code', 'No error code')}")
    if result3.get('suggestions'):
        print("💡 Suggestions:")
        for suggestion in result3['suggestions']:
            print(f"   • {suggestion}")
    
    # Test 4: Invalid parameters
    print("\n📋 Test 4: Invalid Parameters (should show good error)")
    print("-" * 40)
    result4 = await executor.execute_function_call('create_container', {
        'container_id': 'invalid_container',
        'x': 'not_a_number',  # Invalid!
        'y': 50,
        'width': 200,
        'height': 150
    })
    print(f"❌ Status: {result4.get('status')}")
    print(f"💬 Message: {result4.get('message', 'No message')}")
    print(f"🔧 Error Code: {result4.get('error_code', 'No error code')}")
    if result4.get('suggestions'):
        print("💡 Suggestions:")
        for suggestion in result4['suggestions']:
            print(f"   • {suggestion}")

    print("\n" + "=" * 60)
    print("🎯 Summary: LLM now gets detailed error information!")
    print("   • Specific error messages")
    print("   • Error codes for categorization") 
    print("   • Actionable suggestions")
    print("   • Context about what went wrong")

if __name__ == "__main__":
    asyncio.run(test_improved_errors()) 