#!/usr/bin/env python3
"""
Simple Engram-FreqTrade Integration Test
========================================

This script tests the basic functionality without the complex setup.
"""

import sys
import os
import json

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/offstar0/.local/lib/python3.12/site-packages')

def test_engram():
    """Test Engram model loading."""
    try:
        print("🧠 Testing Engram model...")
        from engram_demo_v1 import EngramModel, engram_cfg
        
        model = EngramModel()
        print(f"✅ Engram model loaded successfully!")
        print(f"📊 Model config: {engram_cfg.max_ngram_size}-gram, {engram_cfg.n_embed_per_ngram} embed dim")
        return True
    except Exception as e:
        print(f"❌ Engram test failed: {e}")
        return False

def test_freqtrade():
    """Test FreqTrade import."""
    try:
        print("🤖 Testing FreqTrade import...")
        from freqtrade.configuration.configuration import Configuration
        from freqtrade.persistence import Trade
        
        print("✅ FreqTrade imports successful!")
        return True
    except Exception as e:
        print(f"❌ FreqTrade test failed: {e}")
        return False

def test_strategy():
    """Test strategy import."""
    try:
        print("📈 Testing strategy import...")
        from engram_trading_strategy import EngramStrategy
        
        print("✅ Engram strategy loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        return False

def test_telegram():
    """Test Telegram bot import."""
    try:
        print("📱 Testing Telegram bot import...")
        from engram_telegram_bot import EngramTelegramBot
        
        print("✅ Engram Telegram bot loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Telegram bot test failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    try:
        print("⚙️ Testing configuration...")
        config_path = "/mnt/c/Users/OFFRSTAR0/Engram/engram_freqtrade_config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"✅ Configuration loaded successfully!")
        print(f"📊 Pairs: {config['freqtrade']['exchange']['pair_whitelist']}")
        print(f"🧠 Engram enabled: {config['engram']['enabled']}")
        print(f"📱 Telegram enabled: {config['telegram']['enabled']}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Engram-FreqTrade Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Engram Model", test_engram),
        ("FreqTrade Core", test_freqtrade),
        ("Strategy", test_strategy),
        ("Telegram Bot", test_telegram),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🧪 Testing {name}...")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Integration is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)