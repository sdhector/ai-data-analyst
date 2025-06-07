#!/usr/bin/env python3
"""
Test Acknowledgment System - Verify frontend acknowledgments are received
"""

import asyncio
import websockets
import json
import sys
import time

async def test_acknowledgment_system():
    """Test the acknowledgment system"""
    print("🧪 Testing Canvas Command Acknowledgment System")
    print("=" * 50)
    
    try:
        # Connect to WebSocket
        uri = "ws://localhost:8000/ws"
        print(f"📡 Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send handshake and wait for responses
            handshake = {
                "type": "handshake",
                "data": {
                    "clientType": "test_acknowledgment_client",
                    "version": "0.1.0"
                }
            }
            
            await websocket.send(json.dumps(handshake))
            print("📤 Handshake sent")
            
            # Wait for initial messages
            for i in range(2):  # initial_state and handshake_response
                response = await websocket.recv()
                message = json.loads(response)
                print(f"📥 Received: {message['type']}")
            
            # Test 1: Send canvas resize command
            print("\n🎯 Test 1: Canvas resize with acknowledgment tracking")
            chat_message = {
                "type": "chat_message",
                "message": "resize canvas to 500x500",  # Check current size first
                "conversation_id": "ack_test_session"
            }
            
            await websocket.send(json.dumps(chat_message))
            print("📤 Canvas resize request sent")
            
            # Wait for messages and track acknowledgments
            messages_received = 0
            canvas_command_received = False
            acknowledgment_received = False
            
            while messages_received < 10:  # Expect: chat_response, canvas_command, and possibly ack
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    message = json.loads(response)
                    messages_received += 1
                    
                    print(f"📥 Message {messages_received}: {message['type']}")
                    
                    if message['type'] == 'canvas_command':
                        canvas_command_received = True
                        command_id = message.get('command_id', 'N/A')
                        print(f"   🎨 Canvas command: {message['command']} (ID: {command_id})")
                        print(f"   📋 Data: {message['data']}")
                        
                        # Simulate frontend acknowledgment
                        if command_id != 'N/A':
                            ack_message = {
                                "type": "canvas_command_ack",
                                "command": message['command'],
                                "status": "success",
                                "data": {
                                    "requested_width": message['data']['width'],
                                    "requested_height": message['data']['height'],
                                    "actual_width": message['data']['width'],
                                    "actual_height": message['data']['height'],
                                    "command_id": command_id,
                                    "timestamp": "2025-06-06T18:30:00.000Z"
                                },
                                "message": f"Canvas successfully resized to {message['data']['width']}x{message['data']['height']}"
                            }
                            
                            await websocket.send(json.dumps(ack_message))
                            print(f"   📤 Sent acknowledgment for command {command_id}")
                        
                    elif message['type'] == 'canvas_command_ack':
                        acknowledgment_received = True
                        ack_data = message.get('data', {})
                        print(f"   ✅ Acknowledgment: {ack_data.get('status', 'unknown')}")
                        print(f"   📋 Message: {ack_data.get('message', 'No message')}")
                        
                    elif message['type'] == 'chat_response':
                        success = message.get('data', {}).get('success', False)
                        print(f"   💬 Chat response: {'Success' if success else 'Failed'}")
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for more messages")
                    break
            
            # Test 2: Check backend state
            print("\n🎯 Test 2: Checking backend pending commands")
            # We can't directly access the backend from here, but we can infer from the messages
            
            # Summary
            print("\n" + "=" * 50)
            print("📊 Test Results:")
            print(f"   Canvas command sent: {'✅' if canvas_command_received else '❌'}")
            print(f"   Acknowledgment received: {'✅' if acknowledgment_received else '❌'}")
            
            if canvas_command_received and acknowledgment_received:
                print("🎉 Acknowledgment system working correctly!")
                return True
            else:
                print("❌ Acknowledgment system has issues")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_acknowledgment_system())
    sys.exit(0 if success else 1) 