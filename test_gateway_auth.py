#!/usr/bin/env python3
"""Test script to verify gateway authentication"""

import asyncio
import json
import os
import sys
import websockets

# Get token from environment or ClawdBot config
TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN")
if not TOKEN:
    import subprocess
    result = subprocess.run(
        ['powershell', '-Command', 
         'Get-Content "$env:USERPROFILE\\.clawdbot\\clawdbot.json" | ConvertFrom-Json | Select-Object -ExpandProperty gateway | Select-Object -ExpandProperty auth | Select-Object -ExpandProperty token'],
        capture_output=True, text=True
    )
    TOKEN = result.stdout.strip()
    if TOKEN:
        os.environ["OPENCLAW_GATEWAY_TOKEN"] = TOKEN

GATEWAY_HOST = "localhost"
GATEWAY_PORT = 17500

async def test_connection():
    """Test WebSocket connection and authentication to gateway"""
    uri = f"ws://{GATEWAY_HOST}:{GATEWAY_PORT}?token={TOKEN}"
    
    print(f"Testing connection to {GATEWAY_HOST}:{GATEWAY_PORT}")
    print(f"Token: {TOKEN[:10]}...{TOKEN[-10:]}")
    print()
    
    try:
        async with websockets.connect(uri) as ws:
            print("[OK] WebSocket connected")
            
            # Wait for challenge
            message = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(message)
            print(f"[RECV] {data}")
            
            if data.get("type") == "event" and data.get("event") == "connect.challenge":
                print("[OK] Received authentication challenge")
                
                # Send connect request
                import uuid
                connect_msg = {
                    "type": "req",
                    "id": str(uuid.uuid4()),
                    "method": "connect",
                    "params": {
                        "minProtocol": 3,
                        "maxProtocol": 3,
                        "client": {
                            "id": "test-client",
                            "displayName": "Test Client",
                            "version": "1.0.0",
                            "platform": "python",
                            "mode": "backend"
                        },
                        "caps": ["chat"],
                        "auth": {"token": TOKEN},
                        "role": "operator",
                        "scopes": ["operator.admin"]
                    }
                }
                
                await ws.send(json.dumps(connect_msg))
                print("[OK] Sent connect request")
                
                # Wait for response
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                response_data = json.loads(response)
                print(f"[RECV] {response_data}")
                
                if response_data.get("type") == "res" and response_data.get("ok") == True:
                    print("\n" + "="*50)
                    print("AUTHENTICATION SUCCESSFUL!")
                    print("="*50)
                    return True
                else:
                    print("\n[ERROR] Authentication failed:", response_data)
                    return False
            else:
                print(f"\n[WARN] Unexpected message: {data}")
                return False
                
    except websockets.exceptions.ConnectionRefused:
        print(f"\n[ERROR] Connection refused - is the gateway running on port {GATEWAY_PORT}?")
        return False
    except asyncio.TimeoutError:
        print("\n[ERROR] Timeout waiting for response")
        return False
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
