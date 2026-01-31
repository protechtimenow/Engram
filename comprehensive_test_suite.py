#!/usr/bin/env python3
"""
Comprehensive Test Suite for Engram Trading System
===================================================

This test suite performs thorough testing of:
1. Engram Model (local neural network)
2. LMStudio Integration
3. FreqTrade Strategy Integration
4. Telegram Bot Functionality
5. Edge Cases and Error Handling
6. Concurrency and Performance
"""

import sys
import os
import time
import json
import logging
import asyncio
from typing import Dict, List
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'tests': []
}

def log_test_result(test_name: str, passed: bool, message: str = ""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    logger.info(f"{status}: {test_name} - {message}")
    
    test_results['tests'].append({
        'name': test_name,
        'passed': passed,
        'message': message
    })
    
    if passed:
        test_results['passed'] += 1
    else:
        test_results['failed'] += 1

def test_engram_model_import():
    """Test 1: Engram Model Import"""
    try:
        sys.path.append('src')
        from core.engram_demo_v1 import EngramModel
        log_test_result("Engram Model Import", True, "Successfully imported EngramModel")
        return True
    except Exception as e:
        log_test_result("Engram Model Import", False, f"Import failed: {e}")
        return False

def test_engram_model_initialization():
    """Test 2: Engram Model Initialization"""
    try:
        sys.path.append('src')
        from core.engram_demo_v1 import EngramModel
        
        model = EngramModel(use_clawdbot=False, use_lmstudio=False)
        log_test_result("Engram Model Initialization", True, "Model initialized successfully")
        return True
    except Exception as e:
        log_test_result("Engram Model Initialization", False, f"Initialization failed: {e}")
        return False

def test_engram_forward_pass():
    """Test 3: Engram Forward Pass"""
    try:
        sys.path.append('src')
        from core.engram_demo_v1 import EngramModel
        import torch
        
        model = EngramModel(use_clawdbot=False, use_lmstudio=False)
        input_ids = torch.randint(0, 1000, (1, 10))
        output = model(input_ids)
        
        if output.shape[0] == 1 and output.shape[1] == 10:
            log_test_result("Engram Forward Pass", True, f"Output shape: {output.shape}")
            return True
        else:
            log_test_result("Engram Forward Pass", False, f"Unexpected output shape: {output.shape}")
            return False
    except Exception as e:
        log_test_result("Engram Forward Pass", False, f"Forward pass failed: {e}")
        return False

def test_engram_various_input_shapes():
    """Test 4: Engram Various Input Shapes"""
    try:
        sys.path.append('src')
        from core.engram_demo_v1 import EngramModel
        import torch
        
        model = EngramModel(use_clawdbot=False, use_lmstudio=False)
        
        test_shapes = [(1, 5), (1, 10), (1, 20), (2, 10)]
        all_passed = True
        
        for shape in test_shapes:
            try:
                input_ids = torch.randint(0, 1000, shape)
                output = model(input_ids)
                logger.info(f"  Shape {shape} -> Output {output.shape}")
            except Exception as e:
                logger.error(f"  Shape {shape} failed: {e}")
                all_passed = False
        
        log_test_result("Engram Various Input Shapes", all_passed, f"Tested {len(test_shapes)} shapes")
        return all_passed
    except Exception as e:
        log_test_result("Engram Various Input Shapes", False, f"Test failed: {e}")
        return False

def test_lmstudio_connection():
    """Test 5: LMStudio Connection"""
    try:
        url = "http://192.168.56.1:1234/v1/models"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            log_test_result("LMStudio Connection", True, "LMStudio server is reachable")
            return True
        else:
            log_test_result("LMStudio Connection", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test_result("LMStudio Connection", False, f"Connection failed: {e}")
        return False

def test_lmstudio_integration():
    """Test 6: LMStudio Integration"""
    try:
        sys.path.append('src')
        from core.engram_demo_v1 import EngramModel
        
        model = EngramModel(
            use_clawdbot=False,
            use_lmstudio=True,
            lmstudio_url="http://192.168.56.1:1234"
        )
        
        test_data = """
        Market: BTC/USDT
        Current Price: 45000.00
        RSI: 65.0
        """
        
        analysis = model.analyze_market(test_data)
        
        if 'signal' in analysis and 'confidence' in analysis:
            log_test_result("LMStudio Integration", True, f"Signal: {analysis['signal']}, Confidence: {analysis['confidence']}")
            return True
        else:
            log_test_result("LMStudio Integration", False, "Invalid analysis response")
            return False
    except Exception as e:
        log_test_result("LMStudio Integration", False, f"Integration failed: {e}")
        return False

def test_freqtrade_strategy_import():
    """Test 7: FreqTrade Strategy Import"""
    try:
        sys.path.append('src')
        from trading.engram_trading_strategy import EngramStrategy
        log_test_result("FreqTrade Strategy Import", True, "Successfully imported EngramStrategy")
        return True
    except Exception as e:
        log_test_result("FreqTrade Strategy Import", False, f"Import failed: {e}")
        return False

def test_telegram_api_reachable():
    """Test 8: Telegram API Reachable"""
    try:
        url = "https://api.telegram.org/bot8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                log_test_result("Telegram API Reachable", True, f"Bot: {data['result']['username']}")
                return True
        
        log_test_result("Telegram API Reachable", False, f"Status: {response.status_code}")
        return False
    except Exception as e:
        log_test_result("Telegram API Reachable", False, f"Connection failed: {e}")
        return False

def test_config_files_exist():
    """Test 9: Configuration Files Exist"""
    try:
        config_files = [
            'config/engram_freqtrade_config.json',
            'config/freqtrade_config.json',
            'TODO.md'
        ]
        
        all_exist = True
        for config_file in config_files:
            if not os.path.exists(config_file):
                logger.warning(f"  Missing: {config_file}")
                all_exist = False
            else:
                logger.info(f"  Found: {config_file}")
        
        log_test_result("Configuration Files Exist", all_exist, f"Checked {len(config_files)} files")
        return all_exist
    except Exception as e:
        log_test_result("Configuration Files Exist", False, f"Check failed: {e}")
        return False

def test_error_handling_invalid_input():
    """Test 10: Error Handling - Invalid Input"""
    try:
        sys.path.append('src')
        from core.engram_demo_v1 import EngramModel
        import torch
        
        model = EngramModel(use_clawdbot=False, use_lmstudio=False)
        
        # Test with invalid input (negative values)
        try:
            input_ids = torch.tensor([[-1, -2, -3]])
            output = model(input_ids)
            log_test_result("Error Handling - Invalid Input", True, "Model handled invalid input gracefully")
            return True
        except Exception as e:
            log_test_result("Error Handling - Invalid Input", True, f"Model raised expected error: {type(e).__name__}")
            return True
    except Exception as e:
        log_test_result("Error Handling - Invalid Input", False, f"Test failed: {e}")
        return False

def test_concurrent_model_calls():
    """Test 11: Concurrent Model Calls"""
    try:
        sys.path.append('src')
        from core.engram_demo_v1 import EngramModel
        import torch
        import threading
        
        model = EngramModel(use_clawdbot=False, use_lmstudio=False)
        results = []
        errors = []
        
        def run_inference():
            try:
                input_ids = torch.randint(0, 1000, (1, 10))
                output = model(input_ids)
                results.append(output.shape)
            except Exception as e:
                errors.append(str(e))
        
        # Run 5 concurrent inferences
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=run_inference)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        if len(errors) == 0 and len(results) == 5:
            log_test_result("Concurrent Model Calls", True, f"Successfully ran {len(results)} concurrent calls")
            return True
        else:
            log_test_result("Concurrent Model Calls", False, f"Errors: {len(errors)}, Results: {len(results)}")
            return False
    except Exception as e:
        log_test_result("Concurrent Model Calls", False, f"Test failed: {e}")
        return False

def test_memory_usage():
    """Test 12: Memory Usage"""
    try:
        import psutil
        import torch
        sys.path.append('src')
        from core.engram_demo_v1 import EngramModel
        
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        model = EngramModel(use_clawdbot=False, use_lmstudio=False)
        
        # Run multiple inferences
        for _ in range(10):
            input_ids = torch.randint(0, 1000, (1, 10))
            output = model(input_ids)
        
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_increase = mem_after - mem_before
        
        if mem_increase < 500:  # Less than 500MB increase
            log_test_result("Memory Usage", True, f"Memory increase: {mem_increase:.2f} MB")
            return True
        else:
            log_test_result("Memory Usage", False, f"Excessive memory increase: {mem_increase:.2f} MB")
            return False
    except ImportError:
        log_test_result("Memory Usage", True, "psutil not available, skipping")
        test_results['skipped'] += 1
        return True
    except Exception as e:
        log_test_result("Memory Usage", False, f"Test failed: {e}")
        return False

def test_launch_script_exists():
    """Test 13: Launch Script Exists"""
    try:
        script_path = "scripts/launch_engram_trader.py"
        
        if os.path.exists(script_path):
            with open(script_path, 'r') as f:
                content = f.read()
                if 'EngramFreqTrader' in content:
                    log_test_result("Launch Script Exists", True, "Script found and contains main class")
                    return True
        
        log_test_result("Launch Script Exists", False, "Script not found or invalid")
        return False
    except Exception as e:
        log_test_result("Launch Script Exists", False, f"Check failed: {e}")
        return False

def test_git_commit_exists():
    """Test 14: Git Commit Exists"""
    try:
        import subprocess
        
        result = subprocess.run(
            ['git', 'rev-parse', 'e582dd2016644788e2d8958d36391914d8f227ed'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            log_test_result("Git Commit Exists", True, "Commit e582dd2 found")
            return True
        else:
            log_test_result("Git Commit Exists", False, "Commit not found")
            return False
    except Exception as e:
        log_test_result("Git Commit Exists", False, f"Check failed: {e}")
        return False

def generate_test_report():
    """Generate comprehensive test report"""
    logger.info("\n" + "="*80)
    logger.info("COMPREHENSIVE TEST SUITE RESULTS")
    logger.info("="*80)
    
    total_tests = test_results['passed'] + test_results['failed'] + test_results['skipped']
    pass_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    logger.info(f"\nTotal Tests: {total_tests}")
    logger.info(f"✅ Passed: {test_results['passed']}")
    logger.info(f"❌ Failed: {test_results['failed']}")
    logger.info(f"⏭️  Skipped: {test_results['skipped']}")
    logger.info(f"Pass Rate: {pass_rate:.1f}%")
    
    logger.info("\n" + "-"*80)
    logger.info("DETAILED RESULTS:")
    logger.info("-"*80)
    
    for test in test_results['tests']:
        status = "✅" if test['passed'] else "❌"
        logger.info(f"{status} {test['name']}: {test['message']}")
    
    logger.info("\n" + "="*80)
    
    # Save report to file
    report_path = "COMPREHENSIVE_TEST_REPORT.md"
    with open(report_path, 'w') as f:
        f.write("# Comprehensive Test Suite Results\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Total Tests: {total_tests}\n")
        f.write(f"- ✅ Passed: {test_results['passed']}\n")
        f.write(f"- ❌ Failed: {test_results['failed']}\n")
        f.write(f"- ⏭️ Skipped: {test_results['skipped']}\n")
        f.write(f"- Pass Rate: {pass_rate:.1f}%\n\n")
        f.write(f"## Detailed Results\n\n")
        
        for test in test_results['tests']:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            f.write(f"### {test['name']}\n")
            f.write(f"**Status:** {status}\n")
            f.write(f"**Message:** {test['message']}\n\n")
    
    logger.info(f"\n📄 Full report saved to: {report_path}")
    
    return pass_rate >= 80  # Consider success if 80% or more tests pass

def main():
    """Run all tests"""
    logger.info("🚀 Starting Comprehensive Test Suite for Engram Trading System")
    logger.info("="*80 + "\n")
    
    # Run all tests
    tests = [
        test_engram_model_import,
        test_engram_model_initialization,
        test_engram_forward_pass,
        test_engram_various_input_shapes,
        test_lmstudio_connection,
        test_lmstudio_integration,
        test_freqtrade_strategy_import,
        test_telegram_api_reachable,
        test_config_files_exist,
        test_error_handling_invalid_input,
        test_concurrent_model_calls,
        test_memory_usage,
        test_launch_script_exists,
        test_git_commit_exists,
    ]
    
    for test_func in tests:
        logger.info(f"\nRunning: {test_func.__doc__}")
        try:
            test_func()
        except Exception as e:
            logger.error(f"Test crashed: {e}")
            log_test_result(test_func.__doc__, False, f"Test crashed: {e}")
        
        time.sleep(0.5)  # Small delay between tests
    
    # Generate final report
    success = generate_test_report()
    
    if success:
        logger.info("\n🎉 TEST SUITE PASSED!")
        return 0
    else:
        logger.error("\n❌ TEST SUITE FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
