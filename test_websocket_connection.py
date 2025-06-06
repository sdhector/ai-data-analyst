#!/usr/bin/env python3
"""
Test WebSocket Connection - Check if WebSocket endpoint is working
"""

import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    """Test WebSocket connection to the backend"""
    print("🧪 Testing WebSocket Connection")
    print("=" * 40)
    
    try:
        # Connect to WebSocket
        uri = "ws://localhost:8000/ws"
        print(f"📡 Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send handshake
            handshake = {
                "type": "handshake",
                "data": {
                    "clientType": "test_client",
                    "version": "0.1.0"
                }
            }
            
            await websocket.send(json.dumps(handshake))
            print("📤 Handshake sent")
            
            # Wait for initial messages
            for i in range(2):  # Expect initial_state and handshake_response
                response = await websocket.recv()
                message = json.loads(response)
                print(f"📥 Received: {message['type']}")
            
            # Send a chat message
            chat_message = {
                "type": "chat_message",
                "message": "set canvas to 900x600",  # Different size to trigger actual resize
                "conversation_id": "test_session"
            }
            
            await websocket.send(json.dumps(chat_message))
            print("📤 Chat message sent")
            
            # Wait for chat response
            response = await websocket.recv()
            message = json.loads(response)
            print(f"📥 Chat response: {message['type']}")
            print(f"📋 Response data: {message.get('data', {})}")
            
            if message.get('type') == 'chat_response' and message.get('data', {}).get('success'):
                print("✅ Canvas resize command executed successfully!")
                
                # Check if there's a canvas command message
                try:
                    canvas_response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    canvas_message = json.loads(canvas_response)
                    print(f"📥 Canvas command: {canvas_message['type']} - {canvas_message.get('command', 'N/A')}")
                except asyncio.TimeoutError:
                    print("⏰ No canvas command received within timeout")
            
            print("✅ WebSocket test completed successfully!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_websocket_connection())
    sys.exit(0 if success else 1) 