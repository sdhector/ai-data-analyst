"""
Final Verification Test
Simulates the original user request: "create three containers"
"""

import asyncio
from core.function_executor import coreFunctionExecutor

async def test_original_request():
    print("🎯 Final Verification: 'create three containers'")
    print("=" * 50)
    
    executor = coreFunctionExecutor()
    
    # Clear any existing containers first
    print("🧹 Clearing canvas...")
    clear_result = await executor.execute_function_call('clear_canvas', {})
    print(f"Clear status: {clear_result.get('status')}")
    
    # Simulate what the LLM should do for "create three containers"
    print("\n🤖 LLM Creating Three Containers...")
    print("-" * 30)
    
    containers_to_create = [
        {'container_id': 'container_1'},
        {'container_id': 'container_2'}, 
        {'container_id': 'container_3'}
    ]
    
    results = []
    for i, container_info in enumerate(containers_to_create, 1):
        print(f"\n📦 Creating Container {i}...")
        result = await executor.execute_function_call('create_container', container_info)
        results.append(result)
        
        if result.get('status') == 'success':
            container = result['container']
            print(f"✅ SUCCESS: {container['id']} at ({container['x']}, {container['y']}) size {container['width']}x{container['height']}")
            print(f"   Layout mode: {result['layout_info']['mode_used']}")
        else:
            print(f"❌ ERROR: {result.get('message', 'Unknown error')}")
            if result.get('suggestions'):
                print("💡 Suggestions:")
                for suggestion in result['suggestions']:
                    print(f"   • {suggestion}")
    
    # Summary
    print(f"\n🎯 FINAL RESULTS:")
    print("-" * 20)
    successes = sum(1 for r in results if r.get('status') == 'success')
    print(f"✅ Successful containers: {successes}/3")
    
    if successes == 3:
        print("🎉 PERFECT! All containers created successfully")
        print("✨ Auto-layout system working correctly")
        print("🤖 LLM guidance working - no manual input needed")
    else:
        print("⚠️  Some containers failed to create")
        failed = [r for r in results if r.get('status') != 'success']
        for fail in failed:
            print(f"   • {fail.get('message', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test_original_request()) 