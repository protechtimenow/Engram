#!/usr/bin/env python3
"""
Test script for LMStudio integration with Engram model.
"""

import sys
import os
sys.path.append('src')

from core.engram_demo_v1 import EngramModel

def test_lmstudio_integration():
    """Test LMStudio integration."""
    print("Testing LMStudio integration...")

    # Initialize model with LMStudio
    model = EngramModel(
        use_clawdbot=False,
        use_lmstudio=True,
        lmstudio_url="http://192.168.56.1:1234"
    )

    # Test market analysis
    test_data = """
    Market: BTC/USDT
    Timeframe: 5m
    Current Price: 45000.00
    Price Change: 2.5%
    RSI: 65.0
    Volume: 1500000.0
    High volume activity detected.
    """

    print("Analyzing market data...")
    analysis = model.analyze_market(test_data)

    print("Analysis result:")
    print(f"Signal: {analysis['signal']}")
    print(f"Confidence: {analysis['confidence']}")
    print(f"Reason: {analysis['reason']}")

    print("✅ LMStudio integration test completed!")

if __name__ == "__main__":
    test_lmstudio_integration()
