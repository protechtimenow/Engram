#!/usr/bin/env python3
"""
Test script to verify ClawdBot is connected to local LMStudio model
"""

import asyncio
import websockets
import json
import sys

async def test_clawdbot_model():
    """Test ClawdBot WebSocket connection and query local model"""
    uri = "ws://127.0.0.1:18789"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to ClawdBot WebSocket")

            # Send a simple test query
            test_query = {
                "method": "agents.query",
                "params": {
                    "query": "Hello, can you tell me what model you're using?",
                    "agent": "main"
                },
                "id": "test-1"
            }

            await websocket.send(json.dumps(test_query))
            print("📤 Sent test query to ClawdBot")

            # Wait for response
            response = await websocket.recv()
            response_data = json.loads(response)

            print("📥 Received response:")
            print(json.dumps(response_data, indent=2))

            # Check if response indicates local model usage
            if "result" in response_data:
                result = response_data["result"]
                if "response" in result:
                    response_text = result["response"]
                    print(f"\n🤖 Model Response: {response_text}")

                    # Check for indicators of local model
                    if "glm-4.7b" in response_text.lower() or "local" in response_text.lower():
                        print("✅ SUCCESS: ClawdBot is using local LMStudio model!")
                    elif "claude" in response_text.lower() or "anthropic" in response_text.lower():
                        print("❌ FAIL: ClawdBot is still using Anthropic Claude (cloud model)")
                    else:
                        print("⚠️  UNCLEAR: Cannot determine which model is being used")
                else:
                    print("❌ No response content in result")
            else:
                print("❌ No result in response")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🧪 Testing ClawdBot connection to local LMStudio model...")
    success = asyncio.run(test_clawdbot_model())
    if success:
        print("\n🎉 Test completed!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)
