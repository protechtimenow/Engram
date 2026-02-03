#!/usr/bin/env python3
"""
Engram Risk Assessment Script
Assesses risk level for a trading position
"""

import argparse
import json
import sys

# Add the Engram skills path
sys.path.insert(0, r'C:\Users\OFFRSTAR0\Engram')

from skills.engram.engram_skill import EngramSkill
import asyncio


async def assess_risk(pair: str, position_size: float = 1000):
    """Assess risk for a position"""
    
    config = {
        "lmstudio_host": "localhost",
        "lmstudio_port": 1234,
        "model": "glm-4.7-flash",
        "response_format": "clean"
    }
    
    skill = EngramSkill(config)
    
    message = f"Assess the risk level for a {position_size} USD position in {pair}. Provide risk level (LOW/MEDIUM/HIGH) and recommendations."
    
    try:
        response = await skill.process_message(message)
        print(response)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await skill.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Engram Risk Assessment")
    parser.add_argument("--pair", required=True, help="Trading pair (e.g., BTC/USD, EUR/USD)")
    parser.add_argument("--position-size", type=float, default=1000, help="Position size in USD")
    
    args = parser.parse_args()
    
    asyncio.run(assess_risk(args.pair, args.position_size))


if __name__ == "__main__":
    main()
