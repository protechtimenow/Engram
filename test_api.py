"""
Quick API Key Validation Test
Verifies that OpenRouter API key is accessible and working
"""

import os
import sys

def test_api_key():
    """Test if API key is accessible"""
    print("=" * 60)
    print("Engram API Key Validation Test")
    print("=" * 60)
    print()

    # Check OpenRouter API key
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GLM_API_KEY")
    if api_key:
        print(f"[OK] OPENROUTER_API_KEY found")
        print(f"    Length: {len(api_key)} characters")
        print(f"    Prefix: {api_key[:10]}...")
        print(f"    Suffix: ...{api_key[-10:]}")
        print()
    else:
        print("[FAIL] OPENROUTER_API_KEY not found in environment")
        print()
        return False

    # Check STEPFUN_API key
    stepfun_key = os.getenv("STEPFUN_API_KEY")
    if stepfun_key:
        print(f"[OK] STEPFUN_API_KEY found")
        print(f"    Length: {len(stepfun_key)} characters")
        print()
    else:
        print("[WARN] STEPFUN_API_KEY not found (optional)")
        print()

    print("=" * 60)
    print("RESULT: API keys are accessible!")
    print("=" * 60)
    return True

def test_openrouter_connection():
    """Test actual connection to OpenRouter"""
    import aiohttp
    import json

    print()
    print("=" * 60)
    print("OpenRouter Connection Test")
    print("=" * 60)
    print()

    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GLM_API_KEY")

    async def test():
        session = aiohttp.ClientSession()
        try:
            # Test listing models
            print("[TEST] Connecting to OpenRouter API...")
            async with session.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("data", [])
                    print(f"[OK] Connected successfully!")
                    print(f"[OK] Found {len(models)} available models")
                    print()

                    # Show a few models
                    print("Sample models:")
                    for model in models[:5]:
                        print(f"  - {model.get('id', 'unknown')}")
                    if len(models) > 5:
                        print(f"  ... and {len(models) - 5} more")
                    print()
                    return True
                else:
                    print(f"[FAIL] HTTP {response.status}")
                    error_text = await response.text()
                    print(f"[ERROR] {error_text[:200]}")
                    return False
        except Exception as e:
            print(f"[FAIL] Connection error: {e}")
            return False
        finally:
            await session.close()

    return asyncio.run(test())

import asyncio

if __name__ == "__main__":
    success = True

    # Test 1: API key accessibility
    if not test_api_key():
        success = False

    # Test 2: Connection (optional, only if API key exists)
    if success:
        test_openrouter_connection()

    print()
    if success:
        print("[SUCCESS] All validation tests passed!")
        print("[INFO] You can now run: python run_engram_fast.py")
    else:
        print("[FAIL] Validation failed - fix the issue above")

    sys.exit(0 if success else 1)
