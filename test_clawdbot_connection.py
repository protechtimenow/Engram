#!/usr/bin/env python3
"""
Test script to verify ClawdBot WebSocket connection to local LMStudio model
"""
import asyncio
import websockets
import json

async def test_clawdbot_connection():
    try:
        uri = "ws://127.0.0.1:18789"
        print(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to ClawdBot Gateway")
            
            # Send hello message
            hello_msg = {
                "type": "hello",
                "version": "1",
                "userAgent": "TestClient/1.0"
            }
            await websocket.send(json.dumps(hello_msg))
            print("📤 Sent hello message")
            
            # Wait for response
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {data}")
            
            if data.get("type") == "hello":
                session_id = data.get("sessionId")
                print(f"✅ Session established: {session_id}")
                
                # Send a test message
                test_msg = {
                    "type": "message",
                    "sessionId": session_id,
                    "message": "Hello, can you analyze BTC/USD market data?",
                    "thinking": "high"
                }
                await websocket.send(json.dumps(test_msg))
                print("📤 Sent test message")
                
                # Wait for response
                response_text = ""
                async for message in websocket:
                    data = json.loads(message)
                    if data.get("type") == "chunk":
                        if data.get("text"):
                            response_text += data["text"]
                        if data.get("done"):
                            break
                    elif data.get("type") == "message":
                        if data.get("text"):
                            response_text = data["text"]
                        break
                
                print(f"📥 Response: {response_text[:200]}...")
                return True
            else:
                print(f"❌ Unexpected response: {data}")
                return False
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_clawdbot_connection())
    if result:
        print("✅ ClawdBot connection test successful!")
    else:
        print("❌ ClawdBot connection test failed!")