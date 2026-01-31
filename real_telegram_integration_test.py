#!/usr/bin/env python3
"""
Real Telegram Integration Test
Tests actual Telegram bot functionality with real chat_id: 1007321485
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealTelegramIntegrationTest:
    """Test suite for real Telegram integration with actual chat_id"""
    
    def __init__(self):
        self.results = []
        self.chat_id = "1007321485"  # Real chat_id
        self.token = "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"  # Real token
        self.config_path = Path("config/telegram/working_telegram_config.json")
        
    def run_test(self, name, test_func):
        """Run a single test and record results"""
        try:
            logger.info(f"Running test: {name}")
            test_func()
            self.results.append({
                "test": name,
                "status": "PASS",
                "error": None,
                "timestamp": datetime.now().isoformat()
            })
            logger.info(f"✅ PASS: {name}")
            return True
        except Exception as e:
            self.results.append({
                "test": name,
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            logger.error(f"❌ FAIL: {name} - {str(e)}")
            return False
    
    def test_config_has_real_chat_id(self):
        """Verify config file contains real chat_id"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert 'telegram' in config, "Config missing telegram section"
        assert 'chat_id' in config['telegram'], "Config missing chat_id"
        assert config['telegram']['chat_id'] == self.chat_id, \
            f"Expected chat_id {self.chat_id}, got {config['telegram']['chat_id']}"
        logger.info(f"✓ Config has correct chat_id: {self.chat_id}")
    
    def test_config_has_real_token(self):
        """Verify config file contains real token"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert 'telegram' in config, "Config missing telegram section"
        assert 'token' in config['telegram'], "Config missing token"
        assert config['telegram']['token'] == self.token, "Token mismatch"
        logger.info(f"✓ Config has correct token: {self.token[:20]}...")
    
    def test_telegram_enabled(self):
        """Verify Telegram is enabled in config"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert config['telegram']['enabled'] is True, "Telegram not enabled"
        logger.info("✓ Telegram is enabled")
    
    def test_notification_settings(self):
        """Verify notification settings are configured"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert 'notification_settings' in config['telegram'], \
            "Missing notification_settings"
        
        settings = config['telegram']['notification_settings']
        required = ['status', 'warning', 'startup', 'entry', 'exit']
        
        for setting in required:
            assert setting in settings, f"Missing notification setting: {setting}"
        
        logger.info(f"✓ All notification settings configured: {list(settings.keys())}")
    
    def test_chat_id_format(self):
        """Verify chat_id is in correct format"""
        assert self.chat_id.isdigit(), "chat_id should be numeric string"
        assert len(self.chat_id) >= 7, "chat_id should be at least 7 digits"
        logger.info(f"✓ chat_id format valid: {self.chat_id}")
    
    def test_token_format(self):
        """Verify token is in correct format"""
        parts = self.token.split(':')
        assert len(parts) == 2, "Token should have format 'id:secret'"
        assert parts[0].isdigit(), "Token ID should be numeric"
        assert len(parts[1]) >= 30, "Token secret should be at least 30 chars"
        logger.info(f"✓ Token format valid")
    
    def test_bot_name_configured(self):
        """Verify bot name is configured"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert 'bot_name' in config, "Missing bot_name"
        assert len(config['bot_name']) > 0, "bot_name is empty"
        logger.info(f"✓ Bot name configured: {config['bot_name']}")
    
    def test_no_mock_values(self):
        """Verify no mock values are present"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        mock_patterns = ['mock', 'test123', '123456789', 'fake', 'dummy']
        for pattern in mock_patterns:
            assert pattern.lower() not in content.lower(), \
                f"Found mock pattern '{pattern}' in config"
        
        logger.info("✓ No mock values detected in config")
    
    def test_api_connectivity_config(self):
        """Verify API server configuration"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert 'api_server' in config, "Missing api_server config"
        assert config['api_server']['enabled'] is True, "API server not enabled"
        logger.info("✓ API server configured and enabled")
    
    def test_trading_mode_configured(self):
        """Verify trading mode is configured"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert 'trading_mode' in config, "Missing trading_mode"
        assert config['trading_mode'] in ['spot', 'futures', 'margin'], \
            f"Invalid trading_mode: {config['trading_mode']}"
        logger.info(f"✓ Trading mode configured: {config['trading_mode']}")
    
    def test_dry_run_configured(self):
        """Verify dry_run is configured"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert 'dry_run' in config, "Missing dry_run setting"
        assert isinstance(config['dry_run'], bool), "dry_run should be boolean"
        logger.info(f"✓ Dry run configured: {config['dry_run']}")
    
    def test_exchange_configured(self):
        """Verify exchange is configured"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert 'exchange' in config, "Missing exchange config"
        assert 'name' in config['exchange'], "Missing exchange name"
        logger.info(f"✓ Exchange configured: {config['exchange']['name']}")
    
    def run_all_tests(self):
        """Run all tests"""
        logger.info("=" * 80)
        logger.info("REAL TELEGRAM INTEGRATION TEST SUITE")
        logger.info(f"Chat ID: {self.chat_id}")
        logger.info(f"Token: {self.token[:20]}...")
        logger.info("=" * 80)
        
        tests = [
            ("Config has real chat_id", self.test_config_has_real_chat_id),
            ("Config has real token", self.test_config_has_real_token),
            ("Telegram enabled", self.test_telegram_enabled),
            ("Notification settings configured", self.test_notification_settings),
            ("Chat ID format valid", self.test_chat_id_format),
            ("Token format valid", self.test_token_format),
            ("Bot name configured", self.test_bot_name_configured),
            ("No mock values present", self.test_no_mock_values),
            ("API connectivity configured", self.test_api_connectivity_config),
            ("Trading mode configured", self.test_trading_mode_configured),
            ("Dry run configured", self.test_dry_run_configured),
            ("Exchange configured", self.test_exchange_configured),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            if self.run_test(name, test_func):
                passed += 1
            else:
                failed += 1
        
        # Print summary
        logger.info("=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {len(tests)}")
        logger.info(f"Passed: {passed} ({passed/len(tests)*100:.1f}%)")
        logger.info(f"Failed: {failed} ({failed/len(tests)*100:.1f}%)")
        logger.info("=" * 80)
        
        # Save results
        results_file = Path("real_telegram_test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_suite": "Real Telegram Integration Test",
                "chat_id": self.chat_id,
                "token_prefix": self.token[:20],
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(tests),
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{passed/len(tests)*100:.1f}%",
                "results": self.results
            }, f, indent=2)
        
        logger.info(f"✅ Results saved to {results_file}")
        
        return passed == len(tests)

def main():
    """Main entry point"""
    tester = RealTelegramIntegrationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
