#!/usr/bin/env python3
"""
Engram ACP (Agent Control Protocol) Bridge
Exposes Engram as an A2A agent for ClawdBot
"""

import asyncio
import json
import logging
import os
import websockets
from typing import Dict, Any, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EngramACPBridge:
    """
    ACP Bridge for Engram
    Allows ClawdBot to connect to Engram via A2A protocol
    """
    
    def __init__(self, host: str = "localhost", port: int = 17505):
        self.host = host
        self.port = port
        self.clients = set()
        
        # Import Engram skill
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from skills.engram.engram_skill import EngramSkill
        
        self.skill = EngramSkill({
            "model": os.getenv("ENGRAM_MODEL", "openai/gpt-4o-mini"),
            "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
            "response_format": "clean"
        })
        
        logger.info(f"Engram ACP Bridge initialized on {host}:{port}")
    
    async def handle_client(self, websocket, path):
        """Handle ACP client connection from ClawdBot"""
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        logger.info(f"[ACP] ClawdBot connected from {client_addr}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"[ACP] Received: {data.get('type', 'unknown')}")
                    
                    response = await self.process_acp_message(data)
                    
                    if response:
                        await websocket.send(json.dumps(response))
                        
                except json.JSONDecodeError:
                    logger.error("[ACP] Invalid JSON received")
                except Exception as e:
                    logger.error(f"[ACP] Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"[ACP] ClawdBot disconnected from {client_addr}")
        finally:
            self.clients.discard(websocket)
    
    async def process_acp_message(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process ACP message and return response"""
        msg_type = data.get("type", "")
        
        # Handle ACP protocol messages
        if msg_type == "ping":
            return {"type": "pong", "timestamp": datetime.now().isoformat()}
        
        if msg_type == "chat" or msg_type == "message":
            content = data.get("content", data.get("message", ""))
            
            # Process with Engram skill
            response_text = await self.skill.process_message(content, {})
            
            return {
                "type": "response",
                "content": response_text,
                "agent": "engram",
                "timestamp": datetime.now().isoformat()
            }
        
        if msg_type == "health":
            health = await self.skill.health_check()
            return {
                "type": "health_response",
                "status": health.get("status", "unknown"),
                "model": health.get("model", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
        
        # Unknown message type
        logger.warning(f"[ACP] Unknown message type: {msg_type}")
        return None
    
    async def start(self):
        """Start ACP bridge server"""
        logger.info(f"[ACP] Starting Engram ACP Bridge on ws://{self.host}:{self.port}")
        
        server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            subprotocols=["acp-v1"]
        )
        
        logger.info(f"[ACP] Bridge ready at ws://{self.host}:{self.port}")
        logger.info("[ACP] Waiting for ClawdBot to connect...")
        
        await server.wait_closed()
    
    async def shutdown(self):
        """Shutdown bridge"""
        logger.info("[ACP] Shutting down...")
        await self.skill.shutdown()


async def main():
    """Main entry point"""
    bridge = EngramACPBridge()
    
    try:
        await bridge.start()
    except KeyboardInterrupt:
        logger.info("\n[ACP] Interrupted by user")
    finally:
        await bridge.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
