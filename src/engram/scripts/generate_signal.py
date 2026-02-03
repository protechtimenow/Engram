#!/usr/bin/env python3
"""
Engram Signal Generation Script
Generates trading signals for a trading pair
"""

import argparse
import json
import sys

# Add the Engram skills path
sys.path.insert(0, r'C:\Users\OFFRSTAR0\Engram')

from skills.engram.engram_skill import EngramSkill
import asyncio


async def generate_signal(pair: str, context: str = ""):
    """Generate trading signal for a pair"""
    
    config = {
        "lmstudio_host": "localhost",
        "lmstudio_port": 1234,
        "model": "glm-4.7-flash",
        "response_format": "clean"
    }
    
    skill = EngramSkill(config)
    
    message = f"Generate a trading signal for {pair}."
    if context:
        message += f" Context: {context}"
    message += " Provide signal (BUY/SELL/HOLD), confidence score, and reasoning."
    
    try:
        response = await skill.process_message(message)
        print(response)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await skill.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Engram Signal Generation")
    parser.add_argument("--pair", required=True, help="Trading pair (e.g., BTC/USD, EUR/USD)")
    parser.add_argument("--context", default="", help="Additional market context")
    
    args = parser.parse_args()
    
    asyncio.run(generate_signal(args.pair, args.context))


if __name__ == "__main__":
    main()
