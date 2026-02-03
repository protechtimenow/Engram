#!/usr/bin/env python3
"""
Engram Market Analysis Script
Analyzes market conditions for a trading pair using LMStudio
"""

import argparse
import json
import sys
import os

# Add the Engram skills path
sys.path.insert(0, r'C:\Users\OFFRSTAR0\Engram')

from skills.engram.engram_skill import EngramSkill
import asyncio


async def analyze_market(pair: str, timeframe: str = "1h"):
    """Analyze market for a trading pair"""
    
    config = {
        "lmstudio_host": "localhost",
        "lmstudio_port": 1234,
        "model": "glm-4.7-flash",
        "response_format": "clean"
    }
    
    skill = EngramSkill(config)
    
    message = f"Analyze the market for {pair} on the {timeframe} timeframe. Provide technical analysis, support/resistance levels, and trend direction."
    
    try:
        response = await skill.process_message(message)
        print(response)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await skill.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Engram Market Analysis")
    parser.add_argument("--pair", required=True, help="Trading pair (e.g., BTC/USD, EUR/USD)")
    parser.add_argument("--timeframe", default="1h", choices=["1m", "5m", "15m", "1h", "4h", "1d"],
                        help="Analysis timeframe")
    
    args = parser.parse_args()
    
    asyncio.run(analyze_market(args.pair, args.timeframe))


if __name__ == "__main__":
    main()
