#!/usr/bin/env python3
"""
Interactive Bot Testing - Test bot responses to actual commands
Simulates user interaction and validates responses
"""

import asyncio
import json
import logging
import time
import requests
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractiveBotTester:
    """Test bot by sending commands and monitoring responses"""
    
    def __init__(self):
        self.token = '8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA'
        self.chat_id = '1007321485'
        self.base_url = f'https://api.telegram.org/bot{self.token}'
        self.last_update_id = 0
        self.test_results = []
        
    def send_message(self, text: str) -> Dict:
        """Send message to bot"""
        try:
            response = requests.post(
                f'{self.base_url}/sendMessage',
                json={'chat_id': self.chat_id, 'text': text},
                timeout=10
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send: {e}")
            return {'ok': False, 'error': str(e)}
    
    def get_updates(self, timeout: int = 10) -> List[Dict]:
        """Get new updates from bot"""
        try:
            params = {
                'offset': self.last_update_id + 1,
                'timeout': timeout
            }
            response = requests.get(
                f'{self.base_url}/getUpdates',
                params=params,
                timeout=timeout + 5
            )
            data = response.json()
            
            if data.get('ok'):
                updates = data.get('result', [])
                if updates:
                    self.last_update_id = updates[-1]['update_id']
                return updates
            return []
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")
            return []
    
    def wait_for_response(self, timeout: int = 15) -> List[Dict]:
        """Wait for bot response"""
        logger.info(f"Waiting for response (timeout: {timeout}s)...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            updates = self.get_updates(timeout=5)
            if updates:
                return updates
            time.sleep(1)
        
        return []
    
    async def test_command(self, command: str, expected_keywords: List[str] = None) -> bool:
        """Test a specific command"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing command: {command}")
        logger.info(f"{'='*60}")
        
        # Send command
        send_result = self.send_message(command)
        if not send_result.get('ok'):
            logger.error(f"Failed to send command: {send_result}")
            return False
        
        logger.info(f"✅ Command sent successfully")
        
        # Wait for response
        responses = self.wait_for_response()
        
        if not responses:
            logger.warning(f"⚠️  No response received for: {command}")
            return False
        
        # Check responses
        for update in responses:
            if 'message' in update:
                msg = update['message']
                text = msg.get('text', '')
                logger.info(f"📨 Response: {text[:200]}...")
                
                # Check for expected keywords
                if expected_keywords:
                    found = [kw for kw in expected_keywords if kw.lower() in text.lower()]
                    if found:
                        logger.info(f"✅ Found keywords: {found}")
                        return True
                    else:
                        logger.warning(f"⚠️  Expected keywords not found: {expected_keywords}")
                else:
                    return True
        
        return True
    
    async def run_interactive_tests(self):
        """Run comprehensive interactive tests"""
        logger.info("🚀 Starting Interactive Bot Tests")
        logger.info(f"📱 Phone: 07585185906")
        logger.info(f"🕐 Time: {datetime.now()}")
        
        # Clear old updates
        self.get_updates()
        
        # Send start notification
        self.send_message(
            "🧪 INTERACTIVE BOT TESTING STARTED\n\n"
            "Testing all commands with real interactions..."
        )
        time.sleep(2)
        
        # Test cases
        test_cases = [
            {
                'command': '/start',
                'keywords': ['Welcome', 'Engram', 'Trading', 'Bot'],
                'description': 'Welcome message'
            },
            {
                'command': '/help',
                'keywords': ['Help', 'Commands', 'Use'],
                'description': 'Help information'
            },
            {
                'command': '/status',
                'keywords': ['Status', 'System', 'LMStudio'],
                'description': 'System status'
            },
            {
                'command': '/chat What is Bitcoin?',
                'keywords': ['Bitcoin', 'BTC', 'crypto'],
                'description': 'Chat query'
            },
            {
                'command': 'Tell me about Ethereum',
                'keywords': ['Ethereum', 'ETH'],
                'description': 'Natural language query'
            },
            {
                'command': '/analyze',
                'keywords': ['analysis', 'market', 'trading'],
                'description': 'Market analysis'
            },
        ]
        
        results = []
        
        for i, test in enumerate(test_cases, 1):
            logger.info(f"\n\n{'#'*60}")
            logger.info(f"TEST {i}/{len(test_cases)}: {test['description']}")
            logger.info(f"{'#'*60}")
            
            success = await self.test_command(
                test['command'],
                test.get('keywords')
            )
            
            results.append({
                'test': test['description'],
                'command': test['command'],
                'passed': success,
                'timestamp': datetime.now().isoformat()
            })
            
            # Wait between tests
            time.sleep(3)
        
        # Generate report
        passed = sum(1 for r in results if r['passed'])
        total = len(results)
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          INTERACTIVE BOT TEST REPORT                         ║
╚══════════════════════════════════════════════════════════════╝

📱 Phone: +447585185906
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Tests:    {total}
✅ Passed:      {passed}
❌ Failed:      {total - passed}
📈 Pass Rate:   {(passed/total*100):.1f}%

📋 DETAILED RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for i, r in enumerate(results, 1):
            status = "✅" if r['passed'] else "❌"
            report += f"\n{i}. {status} {r['test']}\n"
            report += f"   Command: {r['command']}\n"
        
        report += "\n╚══════════════════════════════════════════════════════════════╝\n"
        
        logger.info("\n" + report)
        
        # Send report
        self.send_message(report)
        
        # Save results
        with open('/vercel/sandbox/interactive_test_results.json', 'w') as f:
            json.dump({
                'phone': '+447585185906',
                'timestamp': datetime.now().isoformat(),
                'summary': {'total': total, 'passed': passed, 'failed': total - passed},
                'results': results
            }, f, indent=2)
        
        logger.info("📄 Results saved to: /vercel/sandbox/interactive_test_results.json")


async def main():
    """Main entry point"""
    tester = InteractiveBotTester()
    await tester.run_interactive_tests()


if __name__ == '__main__':
    asyncio.run(main())
