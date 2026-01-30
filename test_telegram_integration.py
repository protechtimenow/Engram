#!/usr/bin/env python3
"""
Test script for Telegram + ClawdBot + LMStudio integration
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from telegram.engram_telegram_bot import EngramTelegramBot
from freqtrade.rpc.rpc import RPC


def load_config():
    """Load test configuration."""
    config_path = Path(__file__).parent / "config" / "engram_freqtrade_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def create_mock_rpc():
    """Create a mock RPC for testing."""
    class MockRPC:
        def _rpc_daily_profit(self):
            return {"profit_closed_coin": 0.0, "profit_all_coin": 0.0}

        def _rpc_status(self):
            return "Mock status"

    return MockRPC()


async def test_telegram_bot():
    """Test the Telegram bot integration."""
    print("🧪 Testing Telegram + ClawdBot + LMStudio Integration")
    print("=" * 60)

    try:
        # Load configuration
        config = load_config()
        print("✅ Configuration loaded")

        # Create mock RPC
        rpc = create_mock_rpc()
        print("✅ Mock RPC created")

        # Initialize Telegram bot
        print("🤖 Initializing Engram Telegram Bot...")
        bot = EngramTelegramBot(rpc, config)

        if bot.engram_initialized:
            print("✅ Engram model initialized in Telegram bot")

            # Test natural language processing
            print("\n🧠 Testing natural language query processing...")

            test_queries = [
                "Should I buy BTC now?",
                "What's the market sentiment?",
                "Analyze my current positions"
            ]

            for query in test_queries:
                print(f"\n📝 Testing query: '{query}'")
                try:
                    response = await bot._process_natural_query(query, 12345)
                    print("✅ Response received:")
                    print(response[:200] + "..." if len(response) > 200 else response)
                except Exception as e:
                    print(f"❌ Error processing query: {e}")

        else:
            print("❌ Engram model not initialized")

        print("\n🎉 Integration test completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_telegram_bot())
