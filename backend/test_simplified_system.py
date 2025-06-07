"""
Test Simplified Container Creation System
Tests the simplified approach where LLM generates meaningful IDs and makes multiple calls
"""

import asyncio
from core.function_executor import coreFunctionExecutor

async def test_simplified_system():
    print('🧪 Testing Simplified Container Creation System')
    print('This simulates how the LLM should handle user requests now.')
    
    executor = coreFunctionExecutor()
    
    # Simulate user request: "create a YoY sales chart and customer retention dashboard"
    print('\n🎯 Simulating: "create a YoY sales chart and customer retention dashboard"')
    print('LLM should make multiple create_container calls with meaningful IDs:')
    
    # First container - YoY sales chart
    print('\n📊 Creating YoY sales chart:')
    result1 = await executor.execute_function_call('create_container', {
        'container_id': 'yoy_sales_trend_chart'
    })
    print(f'Status: {result1.get("status")}')
    if result1.get('status') == 'success':
        container = result1.get('container', {})
        print(f'✅ Created at ({container.get("x")}, {container.get("y")}) - {container.get("width")}x{container.get("height")}')
    
    # Second container - Customer retention dashboard
    print('\n📈 Creating customer retention dashboard:')
    result2 = await executor.execute_function_call('create_container', {
        'container_id': 'customer_retention_dashboard'
    })
    print(f'Status: {result2.get("status")}')
    if result2.get('status') == 'success':
        container = result2.get('container', {})
        print(f'✅ Created at ({container.get("x")}, {container.get("y")}) - {container.get("width")}x{container.get("height")}')
    
    # Third container - More descriptive
    print('\n💰 Creating quarterly revenue comparison:')
    result3 = await executor.execute_function_call('create_container', {
        'container_id': 'quarterly_revenue_comparison_2024'
    })
    print(f'Status: {result3.get("status")}')
    if result3.get('status') == 'success':
        container = result3.get('container', {})
        print(f'✅ Created at ({container.get("x")}, {container.get("y")}) - {container.get("width")}x{container.get("height")}')
    
    print('\n🎉 This is much better!')
    print('- Meaningful, descriptive container IDs')
    print('- LLM has full control over naming based on context')
    print('- Automatic positioning without any manual input needed')
    print('- Simpler architecture with fewer moving parts')

if __name__ == "__main__":
    asyncio.run(test_simplified_system()) 