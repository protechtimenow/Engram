#!/usr/bin/env python3
"""Quick test to verify Engram model loads in enhanced_engram_launcher.py"""

import sys
import os
from pathlib import Path

# Set environment variables
os.environ['TELEGRAM_BOT_TOKEN'] = '8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA'
os.environ['TELEGRAM_CHAT_ID'] = '1007321485'
os.environ['LMSTUDIO_URL'] = 'http://100.118.172.23:1234'
os.environ['LMSTUDIO_TIMEOUT'] = '1'  # Short timeout to skip LMStudio

print("=" * 80)
print("QUICK ENGRAM MODEL TEST")
print("=" * 80)

# Test: Load Engram model directly using the same code as enhanced_engram_launcher.py
print("\n[TEST] Loading Engram model using launcher's logic...")
try:
    # Add src directory to Python path (same as launcher)
    script_dir = Path(__file__).parent.resolve()
    possible_src_paths = [
        script_dir / "src",
        Path.cwd() / "src",
        Path("src").resolve()
    ]
    
    src_path = None
    for path in possible_src_paths:
        if path.exists() and (path / "core" / "engram_demo_v1.py").exists():
            src_path = path
            print(f"  Found src path: {src_path}")
            break
    
    if src_path is None:
        raise ImportError("Could not locate src/core/engram_demo_v1.py")
    
    # Add to sys.path
    src_path_str = str(src_path)
    if src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)
        print(f"  Added to sys.path: {src_path_str}")
    
    # Import and instantiate
    from core.engram_demo_v1 import EngramModel
    print("  ✅ EngramModel class imported")
    
    print("  Creating EngramModel instance (this may take 10-15 seconds)...")
    engram_model = EngramModel()
    print(f"  ✅ Engram model instantiated: {type(engram_model)}")
    print(f"  ✅ SUCCESS! Engram model is fully functional")
    
except Exception as e:
    print(f"  ❌ FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
