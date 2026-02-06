#!/usr/bin/env python3
"""
Engram Agent Launcher - FAST MODE
Optimized for speed: 15s timeout, streaming, no typing delays
"""

import asyncio
import os
import sys
import logging
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.engram_agent import EngramAgent

# Fast memory cache for mind modality
class FastMemory:
    """Quick context recall for mind modality"""
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.timestamps = {}
        self.ttl = ttl_seconds
    
    def get(self, key):
        """Get cached value if not expired"""
        if key in self.cache:
            if self.timestamps.get(key, 0) + self.ttl > asyncio.get_event_loop().time():
                return self.cache[key]
            else:
                del self.cache[key]
                del self.timestamps[key]
        return None
    
    def set(self, key, value):
        """Cache value with timestamp"""
        self.cache[key] = value
        self.timestamps[key] = asyncio.get_event_loop().time()
    
    def clear(self):
        """Clear all cached data"""
        self.cache.clear()
        self.timestamps.clear()

# Global fast memory instance
fast_memory = FastMemory(ttl_seconds=300)

async def main():
    """Main entry point - FAST MODE"""
    
    # Load fast config
    config_path = os.getenv("ENGRAM_CONFIG", "config/engram_fast.json")
    fast_config = {}
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                fast_config = json.load(f)
        except Exception as e:
            print(f"[WARN] Could not load fast config: {e}")
    
    # Configure for OpenClaw gateway on port 17500 - FAST SETTINGS
    config = {
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY", ""),
        "stepfun_api_key": os.getenv("STEPFUN_API_KEY", ""),
        "model": fast_config.get("models", {}).get("default", "z-ai/glm-4.7-flash"),
        "provider": "openrouter",
        "clawdbot_host": "localhost",
        "clawdbot_port": 17500,
        "clawdbot_token": fast_config.get("clawdbot", {}).get("token", "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"),
        "response_format": "stream",
        "fast_mode": True,
        "timeout": fast_config.get("openrouter", {}).get("timeout", 15),
        "stream": True,
        "ping_interval": fast_config.get("clawdbot", {}).get("ping_interval", 10),
        "reconnect_delay": fast_config.get("clawdbot", {}).get("reconnect_delay", 0.5),
        "mind_modality": fast_config.get("agent", {}).get("mind_modality", {}),
    }
    
    # Setup logging - minimal for speed
    logging.basicConfig(
        level=logging.WARNING,  # Only warnings/errors for speed
        format='%(asctime)s [%(name)s] %(levelname)s - %(message)s'
    )
    
    print("=" * 50, flush=True)
    print("  Engram Agent - FAST MODE", flush=True)
    print("=" * 50, flush=True)
    print(f"  Gateway: ws://localhost:17500", flush=True)
    print(f"  Model: {config['model']}", flush=True)
    print(f"  Timeout: {config['timeout']}s", flush=True)
    print(f"  Ping: {config['ping_interval']}s", flush=True)
    print(f"  Streaming: ON", flush=True)
    print(f"  Mind Modality: ACTIVE", flush=True)
    print(f"  Token: {config['clawdbot_token'][:10]}...{config['clawdbot_token'][-10:]}", flush=True)
    print("=" * 50, flush=True)
    print()
    
    # Create and run agent
    agent = EngramAgent(config)
    
    # Override with fast reconnect settings
    agent.reconnect_delay = config['reconnect_delay']
    agent.max_reconnect_delay = 10  # Cap at 10 seconds
    
    try:
        await agent.run()
    except KeyboardInterrupt:
        print("\n[Engram] Shutting down...")
    finally:
        await agent.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
