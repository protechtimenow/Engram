#!/usr/bin/env python3
"""
Engram-FreqTrade Quick Status Check
==================================
Simple status check that avoids dependency conflicts.
"""

import sys
import os
import json
import subprocess

def run_cmd(cmd):
    """Run command and return result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_config():
    """Check configuration file."""
    try:
        with open('engram_freqtrade_config.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration loaded successfully!")
        print(f"📊 Trading pairs: {config['freqtrade']['exchange']['pair_whitelist']}")
        print(f"🧠 Engram enabled: {config['engram']['enabled']}")
        print(f"📱 Telegram enabled: {config['telegram']['enabled']}")
        print(f"💰 Initial wallet: {config['freqtrade']['dry_run_wallet']} USDT")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def check_files():
    """Check if required files exist."""
    required_files = [
        'engram_demo_v1.py',
        'engram_trading_strategy.py', 
        'engram_telegram_bot.py',
        'launch_engram_trader.py'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✅ All required files present!")
        return True

def check_python_packages():
    """Check Python package availability."""
    packages = ['freqtrade', 'numpy', 'pandas', 'ccxt']
    
    print("🐍 Checking Python packages:")
    for package in packages:
        success, _, _ = run_cmd(f"python -c 'import {package}; print(\"OK\")'")
        status = "✅" if success else "❌"
        print(f"  {status} {package}")
    
    return True

def check_freqtrade_install():
    """Check FreqTrade installation."""
    success, output, _ = run_cmd("freqtrade --version")
    if success:
        print(f"✅ FreqTrade installed: {output}")
        return True
    else:
        print("❌ FreqTrade not found in PATH")
        return False

def main():
    """Run status check."""
    print("🚀 Engram-FreqTrade Status Check")
    print("=" * 40)
    
    checks = [
        ("Files", check_files),
        ("Configuration", check_config), 
        ("Python Packages", check_python_packages),
        ("FreqTrade Binary", check_freqtrade_install),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 40)
    print("📊 Status Summary:")
    
    passed = 0
    for name, result in results:
        status = "✅ OK" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("🎉 System is ready!")
        print("\n📝 Next steps:")
        print("  1. Update Telegram token in config")
        print("  2. Run: python launch_engram_trader.py --status")
        print("  3. Start trading: python launch_engram_trader.py")
    else:
        print("⚠️ Some checks failed. Please fix the issues above.")

if __name__ == "__main__":
    main()