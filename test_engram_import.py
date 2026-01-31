#!/usr/bin/env python3
"""Test script to diagnose Engram model import issues"""

import sys
import os
import logging
from pathlib import Path

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set environment variables
os.environ['TELEGRAM_BOT_TOKEN'] = '8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA'
os.environ['TELEGRAM_CHAT_ID'] = '1007321485'
os.environ['LMSTUDIO_URL'] = 'http://100.118.172.23:1234'

print("=" * 80)
print("ENGRAM MODEL IMPORT DIAGNOSTIC TEST")
print("=" * 80)

# Test 1: Check if src/core/engram_demo_v1.py exists
print("\n[TEST 1] Checking file existence...")
engram_file = Path("src/core/engram_demo_v1.py")
print(f"  File exists: {engram_file.exists()}")
print(f"  Absolute path: {engram_file.resolve()}")

# Test 2: Try direct import with path manipulation
print("\n[TEST 2] Testing direct import...")
try:
    src_path = Path("src").resolve()
    sys.path.insert(0, str(src_path))
    print(f"  Added to sys.path: {src_path}")
    
    from core.engram_demo_v1 import EngramModel
    print("  ✅ Direct import successful!")
    
    # Try to instantiate
    model = EngramModel()
    print(f"  ✅ Model instantiated: {type(model)}")
except Exception as e:
    print(f"  ❌ Direct import failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Import the launcher and check
print("\n[TEST 3] Testing EnhancedEngramBot...")
try:
    from enhanced_engram_launcher import EnhancedEngramBot
    bot = EnhancedEngramBot()
    
    print(f"  Bot object created: {bot is not None}")
    
    # Call initialize() to load the Engram model
    print("  Calling bot.initialize()...")
    init_success = bot.initialize()
    
    has_engram = hasattr(bot, 'engram_model')
    engram_loaded = has_engram and bot.engram_model is not None
    
    print(f"  Initialization successful: {init_success}")
    print(f"  Has engram_model attribute: {has_engram}")
    print(f"  Engram model loaded: {engram_loaded}")
    
    if engram_loaded:
        print(f"  ✅ Engram model type: {type(bot.engram_model)}")
    else:
        print(f"  ⚠️ Engram model: {bot.engram_model if has_engram else 'attribute missing'}")
        
except Exception as e:
    print(f"  ❌ Bot initialization failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 80)
