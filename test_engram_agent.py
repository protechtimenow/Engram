#!/usr/bin/env python3
"""
Test Engram Agent WebSocket connection to ClawdBot Gateway
"""

import asyncio
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
    except Exception:
        pass

from agents.engram_agent import EngramAgent


async def test_agent():
    """Test the Engram Agent connection"""
    config = {
        "lmstudio_host": "100.118.172.23",
        "lmstudio_port": 1234,
        "model": "glm-4.7-flash",
        "clawdbot_host": "localhost",
        "clawdbot_port": 18789,
        "clawdbot_token": "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc",
        "response_format": "clean"
    }
    
    agent = EngramAgent(config)
    
    try:
        logger.info("=" * 60)
        logger.info("Testing Engram Agent Connection")
        logger.info("=" * 60)
        
        # Try to connect
        connected = await agent.connect()
        
        if connected:
            logger.info("[OK] Successfully connected and authenticated!")
            
            # Listen for a few messages
            logger.info("Listening for messages (press Ctrl+C to stop)...")
            
            # Set a timeout for the test
            try:
                await asyncio.wait_for(agent.listen(), timeout=10.0)
            except asyncio.TimeoutError:
                logger.info("[OK] Test completed - no errors for 10 seconds")
        else:
            logger.error("[ERROR] Failed to connect")
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"[ERROR] Test failed: {e}", exc_info=True)
    finally:
        await agent.shutdown()
        logger.info("Test complete")


if __name__ == "__main__":
    asyncio.run(test_agent())
