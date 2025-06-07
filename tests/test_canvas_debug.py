#!/usr/bin/env python3
"""
Test Canvas Debug - Check WebSocket connections and canvas operations
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.append('backend')

# Set debug mode
os.environ["DEBUG_MODE"] = "true"

from core.chatbot import core_chatbot as chatbot
from core.canvas_bridge import canvas_bridge

async def test_canvas_operations():
    """Test canvas operations and WebSocket connectivity"""
    print("🧪 Testing Canvas Operations and WebSocket Connectivity")
    print("=" * 60)
    
    # Test 1: Check initial canvas state
    print("\n1️⃣ Checking initial canvas state...")
    canvas_state = canvas_bridge.get_canvas_state()
    print(f"   Canvas size: {canvas_state['canvas_size']}")
    print(f"   WebSocket connections: {len(canvas_bridge.websocket_connections)}")
    
    # Test 2: Test direct primitive call
    print("\n2️⃣ Testing direct primitive call...")
    from core.primitives import set_canvas_dimensions_primitive
    
    result = await set_canvas_dimensions_primitive(500, 400)
    print(f"   Primitive result: {result['status']}")
    if result['status'] == 'success':
        print(f"   Changed from {result['old_dimensions']} to {result['new_dimensions']}")
    
    # Test 3: Check canvas state after change
    print("\n3️⃣ Checking canvas state after change...")
    canvas_state = canvas_bridge.get_canvas_state()
    print(f"   Canvas size: {canvas_state['canvas_size']}")
    
    # Test 4: Test through chatbot
    print("\n4️⃣ Testing through chatbot...")
    response = await chatbot.process_user_message("set canvas to 600x500")
    print(f"   Chatbot response success: {response['success']}")
    print(f"   Function calls made: {response.get('function_calls_made', 0)}")
    if 'request_id' in response:
        print(f"   Request ID: {response['request_id']}")
    
    # Test 5: Final canvas state
    print("\n5️⃣ Final canvas state...")
    canvas_state = canvas_bridge.get_canvas_state()
    print(f"   Canvas size: {canvas_state['canvas_size']}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_canvas_operations()) 