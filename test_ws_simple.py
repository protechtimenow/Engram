#!/usr/bin/env python3
"""
Simple WebSocket test for ClawdBot
"""

import asyncio
import json
import websockets
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_simple():
    """Test simple WebSocket connection"""
    # Use the correct token from clawdbot.json
    token = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
    uri = f"ws://127.0.0.1:18789?token={token}"
    
    logger.info(f"Connecting to {uri[:50]}...")
    
    try:
        async with websockets.connect(uri) as ws:
            logger.info("Connected! Waiting for challenge...")
            
            # Receive challenge
            msg = await ws.recv()
            data = json.loads(msg)
            logger.info(f"Received: {data}")
            
            if data.get("type") == "event" and data.get("event") == "connect.challenge":
                nonce = data["payload"]["nonce"]
                logger.info(f"Got nonce: {nonce}")
                
                # Send auth - try different formats
                auth_msg = {
                    "type": "auth",
                    "token": token,
                    "nonce": nonce
                }
                
                auth_json = json.dumps(auth_msg)
                logger.info(f"Sending auth: {auth_json}")
                await ws.send(auth_json)
                logger.info("Auth sent, waiting for response...")
                
                # Try to receive response
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    logger.info(f"Auth response: {response}")
                except asyncio.TimeoutError:
                    logger.error("Timeout waiting for auth response")
                    
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple())
