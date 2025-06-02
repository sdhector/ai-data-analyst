"""
Test AI Engine

Simple test script to verify AI Engine functionality before implementing the UI.
This script tests the core AI capabilities without requiring a full UI.
"""

import os
from dotenv import load_dotenv
from core.ai_engine import AIOrchestrator

# Load environment variables
load_dotenv()

def test_ai_engine():
    """Test the AI Engine components"""
    print("🧪 Testing AI Data Analyst Engine")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    try:
        # Initialize AI Orchestrator
        print("🚀 Initializing AI Orchestrator...")
        ai = AIOrchestrator()
        
        # Test system status
        print("\n📊 Testing System Status...")
        status = ai.get_system_status()
        
        if status["status"] == "success":
            print("✅ System Status: OK")
            print(f"   Model: {status['configuration']['model']}")
            print(f"   Functions Available: {status['functions']['total_available']}")
            print(f"   LLM Connection: {status['llm_connection']['status']}")
        else:
            print(f"❌ System Status Error: {status.get('error', 'Unknown error')}")
            return False
        
        # Test function availability
        print("\n🔧 Testing Function Registry...")
        functions_info = ai.get_available_functions()
        
        if functions_info["status"] == "success":
            print(f"✅ Functions Available: {functions_info['total_functions']}")
            
            # Show function categories
            categories = {
                "data_analysis": ["load_", "filter_", "group_", "sort_", "calculate_", "get_"],
                "visualization": ["create_"],
                "grid_management": ["add_", "remove_", "clear_", "resize_", "update_"]
            }
            
            for category, prefixes in categories.items():
                category_functions = [name for name in functions_info["functions"].keys() 
                                    if any(name.startswith(prefix) for prefix in prefixes)]
                print(f"   {category}: {len(category_functions)} functions")
        else:
            print(f"❌ Functions Error: {functions_info.get('error', 'Unknown error')}")
            return False
        
        # Test simple function execution (without LLM)
        print("\n⚡ Testing Direct Function Execution...")
        
        # Test loading sample data
        result = ai.execute_function_directly("load_sample_data", {"dataset_name": "sales"})
        if result["status"] == "success":
            print("✅ Sample data loaded successfully")
            print(f"   Dataset: {result['result']['dataset_name']}")
            print(f"   Shape: {result['result']['shape']}")
        else:
            print(f"❌ Data loading failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test grid management
        grid_result = ai.execute_function_directly("add_container", {})
        if grid_result["status"] == "success":
            print("✅ Container created successfully")
            print(f"   Container ID: {grid_result['result']['container_id']}")
            print(f"   Position: {grid_result['result']['position']}")
        else:
            print(f"❌ Container creation failed: {grid_result.get('error', 'Unknown error')}")
            return False
        
        # Test AI conversation (simple)
        print("\n🤖 Testing AI Conversation...")
        
        # Simple test without function calling first
        response = ai.process_request(
            user_message="Hello! Can you tell me about your capabilities?",
            enable_functions=False
        )
        
        if response["status"] == "success":
            print("✅ Simple conversation test passed")
            print(f"   Response: {response['message'][:100]}...")
        else:
            print(f"❌ Conversation test failed: {response.get('error', 'Unknown error')}")
            return False
        
        print("\n🎉 All tests passed! AI Engine is ready.")
        print("\n📝 Next steps:")
        print("   1. Create .env file with OPENAI_API_KEY if not done")
        print("   2. Run Streamlit app: streamlit run ui/streamlit_app/app.py")
        print("   3. Test full AI capabilities with function calling")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False

def test_with_function_calling():
    """Test AI with function calling (requires valid API key)"""
    print("\n🧠 Testing AI with Function Calling...")
    print("=" * 50)
    
    try:
        ai = AIOrchestrator()
        
        # Test with function calling
        response = ai.process_request(
            user_message="Load the sales dataset and show me the first 5 rows",
            enable_functions=True
        )
        
        if response["status"] == "success":
            print("✅ Function calling test passed")
            print(f"   Functions called: {response['function_calls_count']}")
            print(f"   Response: {response['message'][:200]}...")
            
            # Show function calls made
            if response["function_calls"]:
                print("\n📋 Function calls made:")
                for i, call in enumerate(response["function_calls"], 1):
                    print(f"   {i}. {call['function_name']}")
                    if call['result']['status'] == 'success':
                        print(f"      ✅ Success")
                    else:
                        print(f"      ❌ Error: {call['result'].get('error', 'Unknown')}")
        else:
            print(f"❌ Function calling test failed: {response.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Function calling test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Run basic tests
    basic_success = test_ai_engine()
    
    if basic_success:
        # Ask user if they want to test function calling (uses API credits)
        print("\n" + "=" * 50)
        user_input = input("Test function calling with OpenAI API? (y/n): ").lower().strip()
        
        if user_input == 'y':
            test_with_function_calling()
        else:
            print("Skipping function calling test. Run again with 'y' to test full AI capabilities.")
    
    print("\n🏁 Testing complete!") 