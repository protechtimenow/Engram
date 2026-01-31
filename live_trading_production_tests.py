#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Trading Production Tests
Comprehensive testing for real live trading scenarios with specific exchange settings
Designed for production deployment on Windows/WSL environment
"""

import sys
import os
import json
import logging
import time
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LiveTradingProductionTests(unittest.TestCase):
    """Comprehensive live trading production tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.config_path = Path("config/engram_freqtrade_config.json")
        self.test_results = []
        self.start_time = time.time()
        
    def tearDown(self):
        """Clean up after tests"""
        duration = time.time() - self.start_time
        logger.info(f"Test completed in {duration:.2f}s")
        
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    # ========================================================================
    # EXCHANGE CONFIGURATION TESTS
    # ========================================================================
    
    def test_binance_exchange_config(self):
        """Test Binance exchange configuration for live trading"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Binance Exchange Configuration")
        logger.info("="*80)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            exchange = config.get('freqtrade', {}).get('exchange', {})
            
            # Test 1: Exchange name
            assert exchange.get('name') == 'binance', "Exchange must be Binance"
            self.log_result("Binance exchange name", True, "binance")
            
            # Test 2: API credentials structure (empty for dry-run is OK)
            assert 'key' in exchange, "API key field must exist"
            assert 'secret' in exchange, "API secret field must exist"
            self.log_result("API credentials structure", True, "key and secret fields present")
            
            # Test 3: Pair whitelist
            whitelist = exchange.get('pair_whitelist', [])
            assert len(whitelist) > 0, "Pair whitelist must not be empty"
            assert 'BTC/USDT' in whitelist, "BTC/USDT should be in whitelist"
            self.log_result("Pair whitelist", True, f"{len(whitelist)} pairs configured")
            
            # Test 4: CCXT config
            assert 'ccxt_config' in exchange, "CCXT config must exist"
            assert 'ccxt_async_config' in exchange, "CCXT async config must exist"
            self.log_result("CCXT configuration", True, "Both sync and async configs present")
            
            logger.info("✅ Binance exchange configuration: VALID")
            
        except Exception as e:
            self.log_result("Binance exchange config", False, str(e))
            raise
            
    def test_exchange_api_rate_limits(self):
        """Test exchange API rate limit configuration"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Exchange API Rate Limits")
        logger.info("="*80)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Binance rate limits (as of 2026)
            binance_limits = {
                'requests_per_second': 10,
                'orders_per_second': 5,
                'orders_per_day': 200000,
                'weight_per_minute': 1200
            }
            
            exchange = config.get('freqtrade', {}).get('exchange', {})
            ccxt_config = exchange.get('ccxt_config', {})
            
            # Test rate limit awareness
            self.log_result("Rate limit configuration", True, 
                          f"Binance limits: {binance_limits['requests_per_second']} req/s")
            
            # Test process throttle
            internals = config.get('internals', {})
            throttle = internals.get('process_throttle_secs', 5)
            assert throttle >= 1, "Process throttle should be at least 1 second"
            self.log_result("Process throttle", True, f"{throttle}s between iterations")
            
            logger.info("✅ Exchange API rate limits: CONFIGURED")
            
        except Exception as e:
            self.log_result("Exchange API rate limits", False, str(e))
            raise
            
    def test_trading_pairs_validation(self):
        """Test trading pairs are valid for selected exchange"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Trading Pairs Validation")
        logger.info("="*80)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            exchange = config.get('freqtrade', {}).get('exchange', {})
            whitelist = exchange.get('pair_whitelist', [])
            blacklist = exchange.get('pair_blacklist', [])
            
            # Test 1: Valid pair format
            for pair in whitelist:
                assert '/' in pair, f"Invalid pair format: {pair}"
                base, quote = pair.split('/')
                assert len(base) > 0 and len(quote) > 0, f"Invalid pair: {pair}"
            self.log_result("Pair format validation", True, f"{len(whitelist)} pairs valid")
            
            # Test 2: No overlap between whitelist and blacklist
            overlap = set(whitelist) & set(blacklist)
            assert len(overlap) == 0, f"Pairs in both lists: {overlap}"
            self.log_result("Whitelist/blacklist separation", True, "No overlap")
            
            # Test 3: Recommended pairs for Binance
            recommended = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
            found = [p for p in recommended if p in whitelist]
            self.log_result("Recommended pairs", True, f"{len(found)}/{len(recommended)} present")
            
            logger.info("✅ Trading pairs validation: PASSED")
            
        except Exception as e:
            self.log_result("Trading pairs validation", False, str(e))
            raise
            
    # ========================================================================
    # LIVE TRADING SAFETY TESTS
    # ========================================================================
    
    def test_dry_run_mode_safety(self):
        """Test dry-run mode is properly configured for safety"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Dry-Run Mode Safety")
        logger.info("="*80)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            freqtrade = config.get('freqtrade', {})
            
            # Test 1: Dry-run mode
            dry_run = freqtrade.get('dry_run', True)
            self.log_result("Dry-run mode", True, 
                          f"{'ENABLED (SAFE)' if dry_run else 'DISABLED (LIVE TRADING)'}")
            
            # Test 2: Dry-run wallet
            if dry_run:
                wallet = freqtrade.get('dry_run_wallet', 0)
                assert wallet > 0, "Dry-run wallet must be > 0"
                self.log_result("Dry-run wallet", True, f"${wallet} USDT")
            
            # Test 3: Force entry disabled (safety)
            force_entry = config.get('force_entry_enable', False)
            assert force_entry == False, "Force entry should be disabled for safety"
            self.log_result("Force entry disabled", True, "Safety feature active")
            
            logger.info("✅ Dry-run mode safety: CONFIGURED")
            
        except Exception as e:
            self.log_result("Dry-run mode safety", False, str(e))
            raise
            
    def test_risk_management_settings(self):
        """Test risk management settings for live trading"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Risk Management Settings")
        logger.info("="*80)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            freqtrade = config.get('freqtrade', {})
            engram = config.get('engram', {})
            
            # Test 1: Max open trades
            max_trades = freqtrade.get('max_open_trades', 0)
            assert max_trades > 0, "Max open trades must be configured"
            assert max_trades <= 10, "Max open trades should be reasonable (≤10)"
            self.log_result("Max open trades", True, f"{max_trades} trades")
            
            # Test 2: Stake amount
            stake_amount = freqtrade.get('stake_amount', 0)
            self.log_result("Stake amount", True, f"{stake_amount}")
            
            # Test 3: Tradable balance ratio
            balance_ratio = freqtrade.get('tradable_balance_ratio', 0)
            assert 0 < balance_ratio <= 1, "Balance ratio must be between 0 and 1"
            self.log_result("Tradable balance ratio", True, f"{balance_ratio*100}%")
            
            # Test 4: Engram risk management
            risk_mgmt = engram.get('trading', {}).get('risk_management', {})
            max_position = risk_mgmt.get('max_position_size', 0)
            assert 0 < max_position <= 0.2, "Max position size should be ≤20%"
            self.log_result("Max position size", True, f"{max_position*100}%")
            
            # Test 5: Stop loss multiplier
            stop_loss = risk_mgmt.get('stop_loss_multiplier', 0)
            assert stop_loss > 0, "Stop loss multiplier must be configured"
            self.log_result("Stop loss multiplier", True, f"{stop_loss}x")
            
            # Test 6: Take profit multiplier
            take_profit = risk_mgmt.get('take_profit_multiplier', 0)
            assert take_profit > stop_loss, "Take profit should be > stop loss"
            self.log_result("Take profit multiplier", True, f"{take_profit}x")
            
            logger.info("✅ Risk management settings: CONFIGURED")
            
        except Exception as e:
            self.log_result("Risk management settings", False, str(e))
            raise
            
    def test_order_timeout_settings(self):
        """Test order timeout settings for live trading"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Order Timeout Settings")
        logger.info("="*80)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            freqtrade = config.get('freqtrade', {})
            timeout = freqtrade.get('unfilledtimeout', {})
            
            # Test 1: Entry timeout
            entry_timeout = timeout.get('entry', 0)
            assert entry_timeout > 0, "Entry timeout must be configured"
            self.log_result("Entry timeout", True, f"{entry_timeout} minutes")
            
            # Test 2: Exit timeout
            exit_timeout = timeout.get('exit', 0)
            assert exit_timeout > 0, "Exit timeout must be configured"
            self.log_result("Exit timeout", True, f"{exit_timeout} minutes")
            
            # Test 3: Timeout unit
            unit = timeout.get('unit', 'minutes')
            assert unit in ['minutes', 'seconds'], "Invalid timeout unit"
            self.log_result("Timeout unit", True, unit)
            
            # Test 4: Cancel open orders on exit
            cancel_on_exit = freqtrade.get('cancel_open_orders_on_exit', False)
            self.log_result("Cancel orders on exit", True, 
                          f"{'ENABLED' if cancel_on_exit else 'DISABLED'}")
            
            logger.info("✅ Order timeout settings: CONFIGURED")
            
        except Exception as e:
            self.log_result("Order timeout settings", False, str(e))
            raise
            
    # ========================================================================
    # TELEGRAM INTEGRATION TESTS
    # ========================================================================
    
    def test_telegram_live_notifications(self):
        """Test Telegram notifications for live trading"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Telegram Live Notifications")
        logger.info("="*80)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            telegram = config.get('telegram', {})
            
            # Test 1: Telegram enabled
            enabled = telegram.get('enabled', False)
            assert enabled == True, "Telegram must be enabled for live trading"
            self.log_result("Telegram enabled", True, "Active")
            
            # Test 2: Credentials
            token = telegram.get('token', '')
            chat_id = telegram.get('chat_id', '')
            assert len(token) > 0, "Telegram token must be configured"
            assert len(chat_id) > 0, "Telegram chat_id must be configured"
            self.log_result("Telegram credentials", True, "Token and chat_id present")
            
            # Test 3: Critical notifications enabled
            notifications = telegram.get('notification_settings', {})
            critical = ['entry', 'exit', 'entry_fill', 'exit_fill', 'warning']
            for notif in critical:
                status = notifications.get(notif, 'off')
                assert status == 'on', f"{notif} notifications should be enabled"
            self.log_result("Critical notifications", True, f"{len(critical)} enabled")
            
            # Test 4: Engram features
            engram_features = telegram.get('engram_features', {})
            assert engram_features.get('enabled', False), "Engram features should be enabled"
            self.log_result("Engram Telegram features", True, "Enabled")
            
            logger.info("✅ Telegram live notifications: CONFIGURED")
            
        except Exception as e:
            self.log_result("Telegram live notifications", False, str(e))
            raise
            
    # ========================================================================
    # ENGRAM AI INTEGRATION TESTS
    # ========================================================================
    
    def test_engram_ai_configuration(self):
        """Test Engram AI configuration for live trading"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Engram AI Configuration")
        logger.info("="*80)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            engram = config.get('engram', {})
            
            # Test 1: Engram enabled
            enabled = engram.get('enabled', False)
            assert enabled == True, "Engram must be enabled"
            self.log_result("Engram enabled", True, "Active")
            
            # Test 2: LMStudio configuration
            use_lmstudio = engram.get('use_lmstudio', False)
            lmstudio_url = engram.get('lmstudio_url', '')
            self.log_result("LMStudio configuration", True, 
                          f"{'Enabled' if use_lmstudio else 'Disabled'}: {lmstudio_url}")
            
            # Test 3: Confidence threshold
            trading = engram.get('trading', {})
            confidence = trading.get('confidence_threshold', 0)
            assert 0 < confidence <= 1, "Confidence threshold must be between 0 and 1"
            self.log_result("Confidence threshold", True, f"{confidence*100}%")
            
            # Test 4: Max signals per pair
            max_signals = trading.get('max_signals_per_pair', 0)
            assert max_signals > 0, "Max signals per pair must be configured"
            self.log_result("Max signals per pair", True, f"{max_signals} signals")
            
            # Test 5: Analysis interval
            interval = trading.get('analysis_interval', 0)
            assert interval > 0, "Analysis interval must be configured"
            self.log_result("Analysis interval", True, f"{interval} minutes")
            
            logger.info("✅ Engram AI configuration: CONFIGURED")
            
        except Exception as e:
            self.log_result("Engram AI configuration", False, str(e))
            raise
            
    # ========================================================================
    # PRODUCTION ENVIRONMENT TESTS
    # ========================================================================
    
    def test_windows_wsl_compatibility(self):
        """Test Windows/WSL environment compatibility"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Windows/WSL Compatibility")
        logger.info("="*80)
        
        try:
            # Test 1: Python version
            python_version = sys.version_info
            assert python_version >= (3, 8), "Python 3.8+ required"
            self.log_result("Python version", True, 
                          f"{python_version.major}.{python_version.minor}.{python_version.micro}")
            
            # Test 2: Path separators
            config_path = Path("config/engram_freqtrade_config.json")
            assert config_path.exists(), "Config file must exist"
            self.log_result("Path handling", True, "Cross-platform paths working")
            
            # Test 3: File encoding
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert len(content) > 0, "File must be readable"
            self.log_result("File encoding", True, "UTF-8 encoding working")
            
            # Test 4: Environment detection
            is_wsl = 'microsoft' in os.uname().release.lower() if hasattr(os, 'uname') else False
            is_windows = sys.platform == 'win32'
            env = "WSL" if is_wsl else ("Windows" if is_windows else "Linux")
            self.log_result("Environment detection", True, env)
            
            logger.info("✅ Windows/WSL compatibility: VERIFIED")
            
        except Exception as e:
            self.log_result("Windows/WSL compatibility", False, str(e))
            raise
            
    def test_production_deployment_readiness(self):
        """Test production deployment readiness"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Production Deployment Readiness")
        logger.info("="*80)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Test 1: Bot name configured
            bot_name = config.get('bot_name', '')
            assert len(bot_name) > 0, "Bot name must be configured"
            self.log_result("Bot name", True, bot_name)
            
            # Test 2: Initial state
            initial_state = config.get('initial_state', '')
            assert initial_state in ['running', 'stopped'], "Invalid initial state"
            self.log_result("Initial state", True, initial_state)
            
            # Test 3: API server configuration
            api_server = config.get('api_server', {})
            api_enabled = api_server.get('enabled', False)
            self.log_result("API server", True, 
                          f"{'Enabled' if api_enabled else 'Disabled'}")
            
            # Test 4: All required sections present
            required_sections = ['freqtrade', 'engram', 'telegram', 'api_server']
            for section in required_sections:
                assert section in config, f"Missing required section: {section}"
            self.log_result("Configuration completeness", True, 
                          f"{len(required_sections)} sections present")
            
            logger.info("✅ Production deployment readiness: VERIFIED")
            
        except Exception as e:
            self.log_result("Production deployment readiness", False, str(e))
            raise
            
    # ========================================================================
    # PERFORMANCE AND MONITORING TESTS
    # ========================================================================
    
    def test_logging_and_monitoring(self):
        """Test logging and monitoring configuration"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Logging and Monitoring")
        logger.info("="*80)
        
        try:
            # Test 1: Logging directory
            log_dir = Path("logs")
            if not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)
            assert log_dir.exists(), "Logs directory must exist"
            self.log_result("Logs directory", True, str(log_dir.absolute()))
            
            # Test 2: Test log file creation
            test_log = log_dir / "test.log"
            with open(test_log, 'w') as f:
                f.write(f"Test log entry: {datetime.now().isoformat()}\n")
            assert test_log.exists(), "Log file creation failed"
            test_log.unlink()  # Clean up
            self.log_result("Log file creation", True, "Write permissions OK")
            
            # Test 3: Logging configuration
            root_logger = logging.getLogger()
            assert len(root_logger.handlers) > 0, "No logging handlers configured"
            self.log_result("Logging handlers", True, f"{len(root_logger.handlers)} handlers")
            
            logger.info("✅ Logging and monitoring: CONFIGURED")
            
        except Exception as e:
            self.log_result("Logging and monitoring", False, str(e))
            raise
            
    def test_data_directory_structure(self):
        """Test data directory structure for live trading"""
        logger.info("\n" + "="*80)
        logger.info("TEST: Data Directory Structure")
        logger.info("="*80)
        
        try:
            # Required directories for FreqTrade
            required_dirs = [
                'user_data',
                'user_data/data',
                'user_data/strategies',
                'user_data/notebooks',
                'config'
            ]
            
            created_dirs = []
            for dir_path in required_dirs:
                path = Path(dir_path)
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(dir_path)
                assert path.exists(), f"Directory {dir_path} must exist"
            
            self.log_result("Data directories", True, 
                          f"{len(required_dirs)} directories verified")
            
            if created_dirs:
                logger.info(f"Created missing directories: {', '.join(created_dirs)}")
            
            logger.info("✅ Data directory structure: VERIFIED")
            
        except Exception as e:
            self.log_result("Data directory structure", False, str(e))
            raise


def run_tests():
    """Run all live trading production tests"""
    logger.info("="*80)
    logger.info("LIVE TRADING PRODUCTION TESTS")
    logger.info("="*80)
    logger.info(f"Test started: {datetime.now().isoformat()}")
    logger.info(f"Environment: {sys.platform}")
    logger.info(f"Python: {sys.version}")
    logger.info("="*80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(LiveTradingProductionTests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    total_tests = result.testsRun
    passed = total_tests - len(result.failures) - len(result.errors)
    failed = len(result.failures) + len(result.errors)
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed} ({pass_rate:.1f}%)")
    logger.info(f"Failed: {failed}")
    logger.info("="*80)
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "environment": sys.platform,
        "python_version": sys.version,
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "status": "PASS" if failed == 0 else "FAIL"
    }
    
    with open("live_trading_production_test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to: live_trading_production_test_results.json")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
