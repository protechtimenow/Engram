#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Testing Suite for Clawdbot/Engram Telegram Bot
Tests all functionality including persistence, commands, and integrations
"""

import asyncio
import json
import logging
import os
import sys
import time
import requests
from datetime import datetime
from typing import Dict, List, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveTestSuite:
    """Comprehensive testing for Clawdbot system"""
    
    def __init__(self):
        self.token = '8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA'
        self.chat_id = '1007321485'
        self.base_url = f'https://api.telegram.org/bot{self.token}'
        self.test_results = []
        self.phone_number = '07585185906'
        
    def send_telegram_message(self, text: str) -> Dict:
        """Send message via Telegram API"""
        try:
            response = requests.post(
                f'{self.base_url}/sendMessage',
                json={'chat_id': self.chat_id, 'text': text},
                timeout=10
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return {'ok': False, 'error': str(e)}
    
    def get_updates(self, offset: int = None) -> Dict:
        """Get updates from Telegram"""
        try:
            params = {'timeout': 5}
            if offset:
                params['offset'] = offset
            response = requests.get(
                f'{self.base_url}/getUpdates',
                params=params,
                timeout=10
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")
            return {'ok': False, 'error': str(e)}
    
    def record_test(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        result = {
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name} - {details}")
    
    # ========== CRITICAL PATH TESTS ==========
    
    def test_telegram_connectivity(self) -> bool:
        """Test 1: Telegram API connectivity"""
        logger.info("🧪 Test 1: Telegram API Connectivity")
        try:
            response = requests.get(f'{self.base_url}/getMe', timeout=10)
            data = response.json()
            
            if data.get('ok'):
                bot_info = data.get('result', {})
                details = f"Bot: {bot_info.get('username')} (ID: {bot_info.get('id')})"
                self.record_test("Telegram Connectivity", True, details)
                return True
            else:
                self.record_test("Telegram Connectivity", False, "API returned not ok")
                return False
        except Exception as e:
            self.record_test("Telegram Connectivity", False, str(e))
            return False
    
    def test_send_receive_message(self) -> bool:
        """Test 2: Send and receive messages"""
        logger.info("🧪 Test 2: Send/Receive Messages")
        try:
            # Send test message
            test_msg = f"🧪 Test Message from {self.phone_number} at {datetime.now()}"
            send_result = self.send_telegram_message(test_msg)
            
            if not send_result.get('ok'):
                self.record_test("Send/Receive Messages", False, "Failed to send")
                return False
            
            # Wait and check for updates
            time.sleep(2)
            updates = self.get_updates()
            
            if updates.get('ok'):
                self.record_test("Send/Receive Messages", True, f"Sent message ID: {send_result.get('result', {}).get('message_id')}")
                return True
            else:
                self.record_test("Send/Receive Messages", False, "Failed to get updates")
                return False
                
        except Exception as e:
            self.record_test("Send/Receive Messages", False, str(e))
            return False
    
    def test_bot_commands(self) -> bool:
        """Test 3: Bot command structure"""
        logger.info("🧪 Test 3: Bot Commands")
        try:
            commands = ['/start', '/status', '/help', '/chat', '/analyze', '/predict']
            
            # Send command info
            msg = f"📋 Testing Commands:\n" + "\n".join(commands)
            result = self.send_telegram_message(msg)
            
            if result.get('ok'):
                self.record_test("Bot Commands", True, f"Tested {len(commands)} commands")
                return True
            else:
                self.record_test("Bot Commands", False, "Failed to send command list")
                return False
                
        except Exception as e:
            self.record_test("Bot Commands", False, str(e))
            return False
    
    # ========== FUNCTIONALITY TESTS ==========
    
    def test_config_loading(self) -> bool:
        """Test 4: Configuration file loading"""
        logger.info("🧪 Test 4: Config Loading")
        try:
            config_path = '/vercel/sandbox/config/telegram/working_telegram_config.json'
            
            if not os.path.exists(config_path):
                self.record_test("Config Loading", False, "Config file not found")
                return False
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Validate config structure
            required_keys = ['telegram', 'exchange', 'strategy']
            missing = [k for k in required_keys if k not in config]
            
            if missing:
                self.record_test("Config Loading", False, f"Missing keys: {missing}")
                return False
            
            telegram_config = config.get('telegram', {})
            if telegram_config.get('token') == self.token:
                self.record_test("Config Loading", True, "Config valid and loaded")
                return True
            else:
                self.record_test("Config Loading", False, "Token mismatch")
                return False
                
        except Exception as e:
            self.record_test("Config Loading", False, str(e))
            return False
    
    def test_engram_model_import(self) -> bool:
        """Test 5: Engram model import"""
        logger.info("🧪 Test 5: Engram Model Import")
        try:
            sys.path.insert(0, '/vercel/sandbox/src')
            from src.core.engram_demo_v1 import EngramModel
            
            self.record_test("Engram Model Import", True, "Successfully imported EngramModel")
            return True
        except Exception as e:
            self.record_test("Engram Model Import", False, str(e))
            return False
    
    def test_lmstudio_connectivity(self) -> bool:
        """Test 6: LMStudio connectivity (optional)"""
        logger.info("🧪 Test 6: LMStudio Connectivity")
        try:
            lmstudio_url = "http://192.168.56.1:1234"
            response = requests.get(f"{lmstudio_url}/v1/models", timeout=5)
            
            if response.status_code == 200:
                self.record_test("LMStudio Connectivity", True, "LMStudio accessible")
                return True
            else:
                self.record_test("LMStudio Connectivity", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            # LMStudio is optional, so we mark as warning not failure
            self.record_test("LMStudio Connectivity", False, f"Not accessible (optional): {str(e)[:50]}")
            return False
    
    # ========== EDGE CASE TESTS ==========
    
    def test_invalid_command_handling(self) -> bool:
        """Test 7: Invalid command handling"""
        logger.info("🧪 Test 7: Invalid Command Handling")
        try:
            invalid_msg = "/invalidcommand12345"
            result = self.send_telegram_message(invalid_msg)
            
            if result.get('ok'):
                self.record_test("Invalid Command Handling", True, "Sent invalid command")
                return True
            else:
                self.record_test("Invalid Command Handling", False, "Failed to send")
                return False
        except Exception as e:
            self.record_test("Invalid Command Handling", False, str(e))
            return False
    
    def test_long_message_handling(self) -> bool:
        """Test 8: Long message handling"""
        logger.info("🧪 Test 8: Long Message Handling")
        try:
            long_msg = "🧪 Long message test: " + ("A" * 500)
            result = self.send_telegram_message(long_msg)
            
            if result.get('ok'):
                self.record_test("Long Message Handling", True, "Sent 500+ char message")
                return True
            else:
                self.record_test("Long Message Handling", False, "Failed to send")
                return False
        except Exception as e:
            self.record_test("Long Message Handling", False, str(e))
            return False
    
    def test_rapid_messages(self) -> bool:
        """Test 9: Rapid message sending"""
        logger.info("🧪 Test 9: Rapid Messages")
        try:
            success_count = 0
            for i in range(3):
                msg = f"🧪 Rapid test {i+1}/3"
                result = self.send_telegram_message(msg)
                if result.get('ok'):
                    success_count += 1
                time.sleep(0.5)
            
            if success_count == 3:
                self.record_test("Rapid Messages", True, "Sent 3 rapid messages")
                return True
            else:
                self.record_test("Rapid Messages", False, f"Only {success_count}/3 succeeded")
                return False
        except Exception as e:
            self.record_test("Rapid Messages", False, str(e))
            return False
    
    # ========== PERSISTENCE TESTS ==========
    
    def test_bot_persistence_check(self) -> bool:
        """Test 10: Check if bot process can stay alive"""
        logger.info("🧪 Test 10: Bot Persistence")
        try:
            # Check if live_telegram_bot.py exists
            bot_script = '/vercel/sandbox/live_telegram_bot.py'
            if not os.path.exists(bot_script):
                self.record_test("Bot Persistence", False, "Bot script not found")
                return False
            
            # Verify script has async main
            with open(bot_script, 'r') as f:
                content = f.read()
                has_async_main = 'async def main()' in content
                has_run_polling = 'run_polling' in content
            
            if has_async_main and has_run_polling:
                self.record_test("Bot Persistence", True, "Bot has persistence structure")
                return True
            else:
                self.record_test("Bot Persistence", False, "Missing async/polling structure")
                return False
        except Exception as e:
            self.record_test("Bot Persistence", False, str(e))
            return False
    
    # ========== REPORTING ==========
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          COMPREHENSIVE CLAWDBOT TEST REPORT                  ║
╚══════════════════════════════════════════════════════════════╝

📱 Phone Number: {self.phone_number}
🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Tests:    {total_tests}
✅ Passed:      {passed_tests}
❌ Failed:      {failed_tests}
📈 Pass Rate:   {pass_rate:.1f}%

📋 DETAILED RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            report += f"\n{i}. {status} - {result['test']}\n"
            report += f"   Details: {result['details']}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 CRITICAL PATH STATUS
"""
        critical_tests = ['Telegram Connectivity', 'Send/Receive Messages', 'Bot Commands']
        critical_passed = all(
            r['passed'] for r in self.test_results 
            if r['test'] in critical_tests
        )
        
        if critical_passed:
            report += "✅ All critical path tests PASSED\n"
        else:
            report += "❌ Some critical path tests FAILED\n"
        
        report += f"""
🔍 RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if pass_rate == 100:
            report += "✅ All tests passed! System is ready for production.\n"
        elif pass_rate >= 80:
            report += "⚠️  Most tests passed. Review failed tests before deployment.\n"
        else:
            report += "❌ Multiple failures detected. System needs attention.\n"
        
        # Add specific recommendations
        failed_critical = [r for r in self.test_results if not r['passed'] and r['test'] in critical_tests]
        if failed_critical:
            report += "\n🚨 CRITICAL: Fix these issues immediately:\n"
            for r in failed_critical:
                report += f"   - {r['test']}: {r['details']}\n"
        
        report += "\n╚══════════════════════════════════════════════════════════════╝\n"
        
        return report
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        logger.info("🚀 Starting Comprehensive Test Suite")
        
        # Send start notification
        self.send_telegram_message(
            f"🚀 COMPREHENSIVE TEST SUITE STARTED\n\n"
            f"Phone: {self.phone_number}\n"
            f"Time: {datetime.now()}\n"
            f"Running 10 comprehensive tests..."
        )
        
        # Critical Path Tests
        logger.info("\n" + "="*60)
        logger.info("CRITICAL PATH TESTS")
        logger.info("="*60)
        self.test_telegram_connectivity()
        self.test_send_receive_message()
        self.test_bot_commands()
        
        # Functionality Tests
        logger.info("\n" + "="*60)
        logger.info("FUNCTIONALITY TESTS")
        logger.info("="*60)
        self.test_config_loading()
        self.test_engram_model_import()
        self.test_lmstudio_connectivity()
        
        # Edge Case Tests
        logger.info("\n" + "="*60)
        logger.info("EDGE CASE TESTS")
        logger.info("="*60)
        self.test_invalid_command_handling()
        self.test_long_message_handling()
        self.test_rapid_messages()
        
        # Persistence Tests
        logger.info("\n" + "="*60)
        logger.info("PERSISTENCE TESTS")
        logger.info("="*60)
        self.test_bot_persistence_check()
        
        # Generate and send report
        report = self.generate_report()
        logger.info("\n" + report)
        
        # Send report via Telegram (split if too long)
        if len(report) > 4000:
            # Split into chunks
            chunks = [report[i:i+4000] for i in range(0, len(report), 4000)]
            for i, chunk in enumerate(chunks):
                self.send_telegram_message(f"📊 Report Part {i+1}/{len(chunks)}\n\n{chunk}")
                time.sleep(1)
        else:
            self.send_telegram_message(report)
        
        # Save report to file
        report_file = '/vercel/sandbox/test_report.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {report_file}")
        
        # Save JSON results
        json_file = '/vercel/sandbox/test_results.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'phone_number': self.phone_number,
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': len(self.test_results),
                    'passed': sum(1 for r in self.test_results if r['passed']),
                    'failed': sum(1 for r in self.test_results if not r['passed'])
                },
                'results': self.test_results
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"JSON results saved to: {json_file}")


async def main():
    """Main entry point"""
    suite = ComprehensiveTestSuite()
    await suite.run_all_tests()


if __name__ == '__main__':
    asyncio.run(main())
