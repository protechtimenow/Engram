#!/usr/bin/env python3
"""
Test ClawdBot WebSocket connection.
"""

import asyncio
import json
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_clawdbot():
    """Test ClawdBot WebSocket connection."""
    try:
        uri = "ws://127.0.0.1:18789?token=fadd41211ea8f13507bfb3630aa9335d3fe2f1d86c8b3102"
        logger.info(f"Connecting to {uri}...")

        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connected to ClawdBot!")

            # Wait for initial message
            response = await websocket.recv()
            result = json.loads(response)
            logger.info(f"Initial message: {result}")

            if result.get("type") == "event" and result.get("event") == "connect.challenge":
                # Send auth response with nonce
                auth_message = {
                    "type": "auth",
                    "token": "fadd41211ea8f13507bfb3630aa9335d3fe2f1d86c8b3102",
                    "nonce": result["payload"]["nonce"]
                }
                logger.info(f"Sending auth: {auth_message}")
                await websocket.send(json.dumps(auth_message))

                # Wait for auth response
                response = await websocket.recv()
                result = json.loads(response)
                logger.info(f"Auth response: {result}")

            # Send a test message
            test_message = {
                "type": "chat",
                "message": "Hello, this is a test from the Telegram bot integration. Can you respond?",
                "model": "openai/glm-4.7b-chat"
            }

            logger.info(f"Sending: {test_message}")
            await websocket.send(json.dumps(test_message))

            # Wait for response
            logger.info("Waiting for response...")
            response = await websocket.recv()
            result = json.loads(response)

            logger.info(f"Received: {result}")

            if "response" in result:
                logger.info("✅ Success! ClawdBot responded:")
                logger.info(result["response"][:500])
            else:
                logger.warning(f"Unexpected response: {result}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_clawdbot())
