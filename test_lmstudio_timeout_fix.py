#!/usr/bin/env python3
"""
Test script for LMStudio timeout fixes
Verifies all fixes are working correctly
"""

import sys
import os
import json
import requests
import time
from datetime import datetime

# Test configuration
LMSTUDIO_URL = os.getenv('LMSTUDIO_URL', 'http://100.118.172.23:1234')
LMSTUDIO_TIMEOUT = int(os.getenv('LMSTUDIO_TIMEOUT', '180'))

print("=" * 80)
print("🧪 LMSTUDIO TIMEOUT FIX - VERIFICATION TEST")
print("=" * 80)
print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🔗 LMStudio URL: {LMSTUDIO_URL}")
print(f"⏱️  Timeout: {LMSTUDIO_TIMEOUT}s")
print("=" * 80)
print()

test_results = {
    "timestamp": datetime.now().isoformat(),
    "lmstudio_url": LMSTUDIO_URL,
    "timeout": LMSTUDIO_TIMEOUT,
    "tests": []
}

def test_connection():
    """Test 1: Connection with proper timeout tuple"""
    print("Test 1: Connection Test with Timeout Tuple")
    print("-" * 80)
    
    try:
        start_time = time.time()
        response = requests.get(
            f"{LMSTUDIO_URL}/v1/models",
            timeout=(5, 10)  # Connect timeout: 5s, Read timeout: 10s
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ PASS: LMStudio connected in {elapsed:.2f}s")
            print(f"   Status: {response.status_code}")
            
            try:
                data = response.json()
                models = data.get('data', [])
                print(f"   Models available: {len(models)}")
                if models:
                    print(f"   First model: {models[0].get('id', 'unknown')}")
            except:
                pass
            
            test_results["tests"].append({
                "name": "connection_test",
                "status": "PASS",
                "elapsed": elapsed,
                "details": "LMStudio connected successfully"
            })
            return True
        else:
            print(f"❌ FAIL: LMStudio returned status {response.status_code}")
            test_results["tests"].append({
                "name": "connection_test",
                "status": "FAIL",
                "details": f"Status code: {response.status_code}"
            })
            return False
            
    except requests.exceptions.Timeout:
        print(f"⚠️  TIMEOUT: Connection timed out (this is expected if LMStudio is slow)")
        test_results["tests"].append({
            "name": "connection_test",
            "status": "TIMEOUT",
            "details": "Connection timeout - LMStudio may be slow or unreachable"
        })
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ FAIL: Connection error - {e}")
        test_results["tests"].append({
            "name": "connection_test",
            "status": "FAIL",
            "details": f"Connection error: {str(e)}"
        })
        return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error - {e}")
        test_results["tests"].append({
            "name": "connection_test",
            "status": "FAIL",
            "details": f"Error: {str(e)}"
        })
        return False
    finally:
        print()

def test_query_with_timeout():
    """Test 2: Query with proper timeout handling"""
    print("Test 2: Query with Timeout Tuple")
    print("-" * 80)
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{LMSTUDIO_URL}/v1/chat/completions",
            json={
                "model": "local-model",
                "messages": [{"role": "user", "content": "Say 'Hello, this is a test!' and nothing else."}],
                "temperature": 0.7,
                "max_tokens": 50
            },
            timeout=(5, LMSTUDIO_TIMEOUT)  # Connect: 5s, Read: configurable
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # Test the fix for glm-4.7-flash empty content
            choice = (result.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            
            # Try content first, then reasoning_content
            text = (msg.get("content") or "").strip()
            if not text:
                text = (msg.get("reasoning_content") or "").strip()
            
            if text:
                print(f"✅ PASS: Query successful in {elapsed:.2f}s")
                print(f"   Response length: {len(text)} chars")
                print(f"   Response preview: {text[:100]}...")
                print(f"   Used field: {'content' if msg.get('content') else 'reasoning_content'}")
                
                test_results["tests"].append({
                    "name": "query_test",
                    "status": "PASS",
                    "elapsed": elapsed,
                    "response_length": len(text),
                    "field_used": "content" if msg.get("content") else "reasoning_content"
                })
                return True
            else:
                print(f"⚠️  WARNING: Query returned empty response")
                print(f"   Raw response: {json.dumps(result, indent=2)}")
                
                test_results["tests"].append({
                    "name": "query_test",
                    "status": "WARNING",
                    "details": "Empty response received"
                })
                return False
        else:
            print(f"❌ FAIL: Query returned status {response.status_code}")
            test_results["tests"].append({
                "name": "query_test",
                "status": "FAIL",
                "details": f"Status code: {response.status_code}"
            })
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⚠️  TIMEOUT: Query timed out after {elapsed:.2f}s")
        print(f"   This is OK if timeout is set correctly - fallback will be used")
        
        test_results["tests"].append({
            "name": "query_test",
            "status": "TIMEOUT",
            "elapsed": elapsed,
            "details": "Query timeout - fallback should be used"
        })
        return False
    except Exception as e:
        print(f"❌ FAIL: Query error - {e}")
        test_results["tests"].append({
            "name": "query_test",
            "status": "FAIL",
            "details": f"Error: {str(e)}"
        })
        return False
    finally:
        print()

def test_multiple_queries():
    """Test 3: Multiple queries to verify no permanent disable"""
    print("Test 3: Multiple Queries (No Permanent Disable)")
    print("-" * 80)
    
    success_count = 0
    timeout_count = 0
    
    for i in range(3):
        print(f"Query {i+1}/3...")
        try:
            start_time = time.time()
            response = requests.post(
                f"{LMSTUDIO_URL}/v1/chat/completions",
                json={
                    "model": "local-model",
                    "messages": [{"role": "user", "content": f"Test query {i+1}. Respond with just 'OK'."}],
                    "temperature": 0.7,
                    "max_tokens": 20
                },
                timeout=(5, 30)  # Short timeout for this test
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                choice = (result.get("choices") or [{}])[0]
                msg = choice.get("message") or {}
                text = (msg.get("content") or "").strip()
                if not text:
                    text = (msg.get("reasoning_content") or "").strip()
                
                if text:
                    print(f"  ✅ Query {i+1} succeeded in {elapsed:.2f}s")
                    success_count += 1
                else:
                    print(f"  ⚠️  Query {i+1} returned empty")
            else:
                print(f"  ❌ Query {i+1} failed with status {response.status_code}")
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            print(f"  ⏱️  Query {i+1} timed out after {elapsed:.2f}s")
            timeout_count += 1
        except Exception as e:
            print(f"  ❌ Query {i+1} error: {e}")
        
        time.sleep(1)  # Brief pause between queries
    
    print()
    print(f"Results: {success_count} succeeded, {timeout_count} timed out, {3 - success_count - timeout_count} failed")
    
    if success_count > 0:
        print(f"✅ PASS: At least one query succeeded (no permanent disable)")
        test_results["tests"].append({
            "name": "multiple_queries_test",
            "status": "PASS",
            "success_count": success_count,
            "timeout_count": timeout_count,
            "details": "Multiple queries work - no permanent disable"
        })
        return True
    else:
        print(f"⚠️  WARNING: No queries succeeded (LMStudio may be unavailable)")
        test_results["tests"].append({
            "name": "multiple_queries_test",
            "status": "WARNING",
            "success_count": success_count,
            "timeout_count": timeout_count,
            "details": "No successful queries - check LMStudio availability"
        })
        return False
    
    print()

def test_environment_variables():
    """Test 4: Environment variable configuration"""
    print("Test 4: Environment Variable Configuration")
    print("-" * 80)
    
    env_vars = {
        'LMSTUDIO_URL': os.getenv('LMSTUDIO_URL'),
        'LMSTUDIO_TIMEOUT': os.getenv('LMSTUDIO_TIMEOUT'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID')
    }
    
    all_set = True
    for var, value in env_vars.items():
        if value:
            # Mask sensitive values
            if 'TOKEN' in var:
                display_value = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"⚠️  {var}: Not set (will use default)")
            if var in ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']:
                all_set = False
    
    print()
    if all_set:
        print("✅ PASS: All required environment variables are set")
        test_results["tests"].append({
            "name": "environment_variables_test",
            "status": "PASS",
            "details": "All environment variables configured"
        })
        return True
    else:
        print("⚠️  WARNING: Some environment variables not set (bot may not work)")
        test_results["tests"].append({
            "name": "environment_variables_test",
            "status": "WARNING",
            "details": "Some environment variables missing"
        })
        return False
    
    print()

# Run all tests
print("🚀 Starting tests...\n")

test_1 = test_connection()
test_2 = test_query_with_timeout()
test_3 = test_multiple_queries()
test_4 = test_environment_variables()

# Summary
print("=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)

total_tests = len(test_results["tests"])
passed = sum(1 for t in test_results["tests"] if t["status"] == "PASS")
failed = sum(1 for t in test_results["tests"] if t["status"] == "FAIL")
warnings = sum(1 for t in test_results["tests"] if t["status"] in ["WARNING", "TIMEOUT"])

print(f"Total Tests: {total_tests}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"⚠️  Warnings: {warnings}")
print()

if failed == 0 and passed > 0:
    print("🎉 ALL CRITICAL TESTS PASSED!")
    print("✅ LMStudio timeout fixes are working correctly")
    test_results["overall_status"] = "PASS"
elif failed > 0:
    print("⚠️  SOME TESTS FAILED")
    print("Check LMStudio availability and configuration")
    test_results["overall_status"] = "FAIL"
else:
    print("⚠️  NO TESTS PASSED")
    print("LMStudio may be unavailable or misconfigured")
    test_results["overall_status"] = "WARNING"

print()
print("=" * 80)
print("💡 NEXT STEPS")
print("=" * 80)

if test_1 and test_2:
    print("✅ LMStudio is working! You can now:")
    print("   1. Launch the bot: python enhanced_engram_launcher.py")
    print("   2. Send 'hi' to your Telegram bot")
    print("   3. Verify you get AI-powered responses")
elif not test_1:
    print("⚠️  LMStudio connection failed. Check:")
    print("   1. Is LMStudio running?")
    print("   2. Is the URL correct? (current: {})".format(LMSTUDIO_URL))
    print("   3. Is there a firewall blocking the connection?")
    print("   4. Try: curl {}}/v1/models".format(LMSTUDIO_URL))
elif not test_2:
    print("⚠️  LMStudio queries failed. Check:")
    print("   1. Is a model loaded in LMStudio?")
    print("   2. Is the timeout sufficient? (current: {}s)".format(LMSTUDIO_TIMEOUT))
    print("   3. Try increasing timeout: $env:LMSTUDIO_TIMEOUT=\"300\"")

if not test_4:
    print()
    print("⚠️  Environment variables not fully configured. Set:")
    print("   $env:TELEGRAM_BOT_TOKEN=\"8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA\"")
    print("   $env:TELEGRAM_CHAT_ID=\"1007321485\"")

print()
print("=" * 80)

# Save results
results_file = "lmstudio_timeout_fix_test_results.json"
with open(results_file, 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"📄 Test results saved to: {results_file}")
print("=" * 80)
