#!/usr/bin/env python3
"""
Diagnostic Script: Test Engram Model Loading
Tests the Engram Model import and initialization to diagnose loading issues.
"""

import sys
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_engram_model_loading():
    """Test Engram Model loading with detailed diagnostics"""
    
    print("="*80)
    print("🔍 ENGRAM MODEL LOADING DIAGNOSTIC TEST")
    print("="*80)
    
    # Test 1: Check if src/core directory exists
    print("\n[Test 1] Checking directory structure...")
    src_path = Path(__file__).parent / "src"
    core_path = src_path / "core"
    engram_file = core_path / "engram_demo_v1.py"
    
    print(f"  📁 Project root: {Path(__file__).parent}")
    print(f"  📁 src path: {src_path} - {'✅ EXISTS' if src_path.exists() else '❌ NOT FOUND'}")
    print(f"  📁 core path: {core_path} - {'✅ EXISTS' if core_path.exists() else '❌ NOT FOUND'}")
    print(f"  📄 engram_demo_v1.py: {engram_file} - {'✅ EXISTS' if engram_file.exists() else '❌ NOT FOUND'}")
    
    if not engram_file.exists():
        print("\n❌ FAILED: engram_demo_v1.py not found!")
        return False
    
    # Test 2: Check Python path
    print("\n[Test 2] Checking Python path...")
    print(f"  Current sys.path entries:")
    for i, path in enumerate(sys.path[:5]):
        print(f"    {i+1}. {path}")
    
    # Test 3: Add src to path and try import
    print("\n[Test 3] Adding src to Python path...")
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        print(f"  ✅ Added {src_path} to sys.path")
    else:
        print(f"  ℹ️  {src_path} already in sys.path")
    
    # Test 4: Try importing the module
    print("\n[Test 4] Attempting to import EngramModel...")
    try:
        from core.engram_demo_v1 import EngramModel
        print("  ✅ Import successful!")
        
        # Test 5: Try instantiating the model
        print("\n[Test 5] Attempting to instantiate EngramModel...")
        try:
            model = EngramModel()
            print("  ✅ EngramModel instantiated successfully!")
            print(f"  📊 Model type: {type(model)}")
            print(f"  📊 Model attributes: {dir(model)[:10]}...")
            
            print("\n" + "="*80)
            print("✅ ALL TESTS PASSED - Engram Model is working!")
            print("="*80)
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to instantiate EngramModel: {type(e).__name__}")
            print(f"  Error details: {str(e)}")
            import traceback
            print("\n  Full traceback:")
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"  ❌ Import failed: {type(e).__name__}")
        print(f"  Error details: {str(e)}")
        import traceback
        print("\n  Full traceback:")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {type(e).__name__}")
        print(f"  Error details: {str(e)}")
        import traceback
        print("\n  Full traceback:")
        traceback.print_exc()
        return False

def test_dependencies():
    """Test if required dependencies are installed"""
    print("\n[Test 6] Checking required dependencies...")
    
    dependencies = {
        'torch': 'PyTorch',
        'numpy': 'NumPy',
        'transformers': 'Hugging Face Transformers',
        'sympy': 'SymPy',
        'tokenizers': 'Tokenizers'
    }
    
    all_installed = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {name} ({module}) - installed")
        except ImportError:
            print(f"  ❌ {name} ({module}) - NOT INSTALLED")
            all_installed = False
    
    return all_installed

def main():
    """Run all diagnostic tests"""
    
    # Test dependencies first
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n⚠️  WARNING: Some dependencies are missing!")
        print("   Install with: pip install torch numpy transformers sympy tokenizers")
        print("\n   Continuing with Engram Model loading test anyway...\n")
    
    # Test Engram Model loading
    success = test_engram_model_loading()
    
    # Summary
    print("\n" + "="*80)
    print("📋 DIAGNOSTIC SUMMARY")
    print("="*80)
    
    if success:
        print("✅ Status: ENGRAM MODEL LOADING SUCCESSFUL")
        print("\n📝 Recommendation:")
        print("   The Engram Model should now load correctly in enhanced_engram_launcher.py")
        print("   Restart your bot to see the change.")
    else:
        print("❌ Status: ENGRAM MODEL LOADING FAILED")
        print("\n📝 Recommendations:")
        print("   1. Check if all dependencies are installed")
        print("   2. Verify src/core/engram_demo_v1.py exists and is readable")
        print("   3. Check the error traceback above for specific issues")
        print("   4. Ensure Python version is compatible (3.8+)")
    
    print("="*80)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
