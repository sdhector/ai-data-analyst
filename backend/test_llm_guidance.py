"""
Test LLM Guidance for Automatic Container ID Generation
Shows expected behavior after updating function descriptions
"""

from core.registry.canvas_management_registry import get_canvas_management_function_schemas

def test_function_descriptions():
    """Test that function descriptions properly guide LLM behavior"""
    
    print("🔍 Testing Updated Function Descriptions")
    print("=" * 50)
    
    # Get the function schemas
    schemas = get_canvas_management_function_schemas()
    
    # Find create_container function
    create_container_schema = None
    for schema in schemas:
        if schema['name'] == 'create_container':
            create_container_schema = schema
            break
    
    if not create_container_schema:
        print("❌ create_container function not found!")
        return
    
    print("📋 create_container Function Description:")
    print("-" * 40)
    print(create_container_schema['description'])
    print()
    
    print("🎯 container_id Parameter Description:")
    print("-" * 40)
    container_id_desc = create_container_schema['parameters']['properties']['container_id']['description']
    print(container_id_desc)
    print()
    
    print("✅ Expected LLM Behavior Examples:")
    print("-" * 40)
    print("User: 'create three containers'")
    print("LLM should call:")
    print("  create_container('container_1')")
    print("  create_container('container_2')")  
    print("  create_container('container_3')")
    print()
    
    print("User: 'add a sales dashboard and customer analytics'")
    print("LLM should call:")
    print("  create_container('sales_dashboard')")
    print("  create_container('customer_analytics')")
    print()
    
    print("User: 'create some widgets for the report'")
    print("LLM should call:")
    print("  create_container('widget_1')")
    print("  create_container('widget_2')")
    print("  create_container('widget_3')")
    print()
    
    # Check for key phrases that should guide LLM
    description = create_container_schema['description']
    container_desc = container_id_desc
    
    has_never_ask = "NEVER ask" in description or "NEVER ask" in container_desc
    has_generate = "generate" in description.lower() or "generate" in container_desc.lower()
    has_examples = "→" in description or "Examples:" in container_desc
    
    print("🔍 Description Analysis:")
    print("-" * 40)
    print(f"Contains 'NEVER ask user': {has_never_ask}")
    print(f"Contains 'generate' guidance: {has_generate}")
    print(f"Contains clear examples: {has_examples}")
    
    if has_never_ask and has_generate and has_examples:
        print("✅ Function description should properly guide LLM!")
    else:
        print("⚠️ Function description may need improvement")

if __name__ == "__main__":
    test_function_descriptions() 