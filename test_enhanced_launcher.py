#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Enhanced Engram Launcher
Tests timeout handling, fallback mechanisms, and environment variable support
"""

import sys
import os
import json
import unittest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_engram_launcher import AIBackend, EnhancedEngramBot


class TestAIBackend(unittest.TestCase):
    """Test AI Backend with fallback mechanisms"""
    
    def test_initialization(self):
        """Test AI backend initialization"""
        backend = AIBackend(lmstudio_url="http://localhost:1234", timeout=5)
        self.assertIsNotNone(backend)
        self.assertEqual(backend.timeout, 5)
        self.assertEqual(backend.lmstudio_url, "http://localhost:1234")
        
    def test_mock_ai_response_analyze(self):
        """Test mock AI response for analysis queries"""
        backend = AIBackend()
        response = backend.mock_ai_response("analyze BTC market")
        self.assertIn("Market Analysis", response)
        self.assertIn("Mock AI", response)
        
    def test_mock_ai_response_status(self):
        """Test mock AI response for status queries"""
        backend = AIBackend()
        response = backend.mock_ai_response("what is the status")
        self.assertIn("Bot Status", response)
        self.assertIn("Mock AI", response)
        
    def test_mock_ai_response_general(self):
        """Test mock AI response for general queries"""
        backend = AIBackend()
        response = backend.mock_ai_response("hello world")
        self.assertIn("Mock AI Response", response)
        self.assertIn("fallback mode", response)
        
    def test_rule_based_analysis(self):
        """Test rule-based market analysis"""
        backend = AIBackend()
        response = backend.rule_based_analysis("ETH/USDT")
        self.assertIn("Rule-Based Analysis", response)
        self.assertIn("ETH/USDT", response)
        self.assertIn("HOLD", response)
        
    @patch('requests.get')
    def test_connection_timeout(self, mock_get):
        """Test LMStudio connection timeout handling"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        backend = AIBackend(timeout=3)
        self.assertFalse(backend.lmstudio_available)
        
    @patch('requests.get')
    def test_connection_error(self, mock_get):
        """Test LMStudio connection error handling"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        backend = AIBackend(timeout=3)
        self.assertFalse(backend.lmstudio_available)
        
    @patch('requests.post')
    def test_query_timeout(self, mock_post):
        """Test LMStudio query timeout handling"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        backend = AIBackend()
        backend.lmstudio_available = True  # Force enable
        
        result = backend.query_lmstudio("test query")
        self.assertIsNone(result)
        self.assertFalse(backend.lmstudio_available)  # Should be disabled after timeout
        
    def test_query_fallback_chain(self):
        """Test query fallback chain"""
        backend = AIBackend()
        backend.lmstudio_available = False  # Force fallback
        
        result = backend.query("analyze BTC")
        self.assertIsNotNone(result)
        self.assertIn("Mock AI", result)


class TestEnhancedEngramBot(unittest.TestCase):
    """Test Enhanced Engram Bot"""
    
    def setUp(self):
        """Set up test environment"""
        # Set test environment variables
        os.environ['TELEGRAM_BOT_TOKEN'] = '8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA'
        os.environ['TELEGRAM_CHAT_ID'] = '1007321485'
        os.environ['LMSTUDIO_URL'] = 'http://localhost:1234'
        os.environ['LMSTUDIO_TIMEOUT'] = '5'
        
    def tearDown(self):
        """Clean up test environment"""
        for key in ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'LMSTUDIO_URL', 'LMSTUDIO_TIMEOUT']:
            if key in os.environ:
                del os.environ[key]
                
    def test_load_config_from_env(self):
        """Test loading configuration from environment variables"""
        bot = EnhancedEngramBot()
        result = bot.load_config()
        
        self.assertTrue(result)
        self.assertEqual(bot.token, '8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA')
        self.assertEqual(bot.chat_id, '1007321485')
        
    def test_load_config_from_file(self):
        """Test loading configuration from file"""
        # Clear environment variables
        for key in ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']:
            if key in os.environ:
                del os.environ[key]
                
        bot = EnhancedEngramBot()
        result = bot.load_config()
        
        # Should load from file if it exists
        if result:
            self.assertIsNotNone(bot.token)
            self.assertIsNotNone(bot.chat_id)
            
    @patch('requests.get')
    def test_telegram_connection(self, mock_get):
        """Test Telegram connection"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ok': True,
            'result': {'username': 'Freqtrad3_bot'}
        }
        mock_get.return_value = mock_response
        
        bot = EnhancedEngramBot()
        bot.token = 'test_token'
        bot.chat_id = '1007321485'
        bot.base_url = 'https://api.telegram.org/bottest_token'
        
        # Mock AI backend
        bot.ai_backend = AIBackend()
        
        # Test connection (will call mocked requests.get)
        # Note: We can't fully test initialize() without mocking more, but we can test components
        
    def test_process_start_command(self):
        """Test /start command processing"""
        bot = EnhancedEngramBot()
        bot.ai_backend = AIBackend()
        bot.send_message = Mock()
        
        message = {
            'text': '/start',
            'chat': {'id': 1007321485}
        }
        
        bot.process_message(message)
        
        # Verify send_message was called
        self.assertTrue(bot.send_message.called)
        call_args = bot.send_message.call_args[0][0]
        self.assertIn('Welcome', call_args)
        
    def test_process_status_command(self):
        """Test /status command processing"""
        bot = EnhancedEngramBot()
        bot.ai_backend = AIBackend()
        bot.engram_model = None
        bot.send_message = Mock()
        
        message = {
            'text': '/status',
            'chat': {'id': 1007321485}
        }
        
        bot.process_message(message)
        
        # Verify send_message was called
        self.assertTrue(bot.send_message.called)
        call_args = bot.send_message.call_args[0][0]
        self.assertIn('Bot Status', call_args)
        
    def test_process_analyze_command(self):
        """Test /analyze command processing"""
        bot = EnhancedEngramBot()
        bot.ai_backend = AIBackend()
        bot.ai_backend.lmstudio_available = False  # Force fallback
        bot.send_message = Mock()
        
        message = {
            'text': '/analyze BTC/USDT',
            'chat': {'id': 1007321485}
        }
        
        bot.process_message(message)
        
        # Verify send_message was called
        self.assertTrue(bot.send_message.called)
        call_args = bot.send_message.call_args[0][0]
        self.assertIn('Analysis', call_args)
        self.assertIn('BTC/USDT', call_args)
        
    def test_process_help_command(self):
        """Test /help command processing"""
        bot = EnhancedEngramBot()
        bot.ai_backend = AIBackend()
        bot.send_message = Mock()
        
        message = {
            'text': '/help',
            'chat': {'id': 1007321485}
        }
        
        bot.process_message(message)
        
        # Verify send_message was called
        self.assertTrue(bot.send_message.called)
        call_args = bot.send_message.call_args[0][0]
        self.assertIn('Help', call_args)
        self.assertIn('TELEGRAM_BOT_TOKEN', call_args)
        
    def test_process_general_message(self):
        """Test general message processing"""
        bot = EnhancedEngramBot()
        bot.ai_backend = AIBackend()
        bot.ai_backend.lmstudio_available = False  # Force fallback
        bot.send_message = Mock()
        
        message = {
            'text': 'hello bot',
            'chat': {'id': 1007321485}
        }
        
        bot.process_message(message)
        
        # Verify send_message was called
        self.assertTrue(bot.send_message.called)
        call_args = bot.send_message.call_args[0][0]
        self.assertIsNotNone(call_args)


class TestTimeoutHandling(unittest.TestCase):
    """Test timeout handling and error recovery"""
    
    @patch('requests.post')
    def test_lmstudio_timeout_recovery(self, mock_post):
        """Test recovery from LMStudio timeout"""
        import requests
        
        # First call times out
        mock_post.side_effect = requests.exceptions.Timeout()
        
        backend = AIBackend()
        backend.lmstudio_available = True
        
        # Query should handle timeout and return fallback
        result = backend.query("test query")
        
        self.assertIsNotNone(result)
        self.assertIn("Mock AI", result)
        self.assertFalse(backend.lmstudio_available)
        
    @patch('requests.post')
    def test_multiple_timeout_handling(self, mock_post):
        """Test handling multiple consecutive timeouts"""
        import requests
        
        backend = AIBackend()
        backend.lmstudio_available = True
        
        # Simulate multiple timeouts
        for i in range(3):
            mock_post.side_effect = requests.exceptions.Timeout()
            result = backend.query(f"query {i}")
            
            self.assertIsNotNone(result)
            self.assertIn("Mock AI", result)


def run_tests():
    """Run all tests and generate report"""
    print("="*80)
    print("ENHANCED ENGRAM LAUNCHER - TEST SUITE")
    print("="*80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAIBackend))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedEngramBot))
    suite.addTests(loader.loadTestsFromTestCase(TestTimeoutHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print()
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*80)
    
    # Save results
    results_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failed": len(result.failures),
        "errors": len(result.errors),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    }
    
    with open('enhanced_launcher_test_results.json', 'w') as f:
        json.dump(results_data, f, indent=2)
        
    print(f"\n✅ Test results saved to: enhanced_launcher_test_results.json")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
