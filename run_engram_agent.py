#!/usr/bin/env python3
"""
Engram Agent Launcher
Connects to OpenClaw Gateway on port 17500
"""

import asyncio
import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.engram_agent import EngramAgent

async def main():
    """Main entry point"""
    
    # Configure for OpenClaw gateway on port 17500
    config = {
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY", ""),
        "stepfun_api_key": os.getenv("STEPFUN_API_KEY", ""),
        "model": os.getenv("ENGRAM_MODEL", "stepfun/step-3.5-flash:free"),
        "provider": "stepfun",
        "clawdbot_host": "localhost",
        "clawdbot_port": 17500,  # OpenClaw gateway port
        "clawdbot_token": os.getenv("OPENCLAW_GATEWAY_TOKEN", "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"),
        "response_format": "clean"
    }
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s - %(message)s'
    )
    
    print("=" * 50)
    print("  Engram Agent - StepFun Model")
    print("=" * 50)
    print(f"  Gateway: ws://localhost:17500")
    print(f"  Model: {config['model']}")
    print(f"  Provider: {config['provider']}")
    print("=" * 50)
    print()
    
    # Create and run agent
    agent = EngramAgent(config)
    
    try:
        await agent.run()
    except KeyboardInterrupt:
        print("\n[Engram] Shutting down...")
    finally:
        await agent.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
