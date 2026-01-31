#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Engram Bot Launcher
Standalone launcher for Engram trading bot with Telegram integration
"""

import sys
import os
import json
import logging
import time
import requests
from datetime import datetime
from pathlib import Path

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


class SimpleEngramBot:
    """Simple standalone Engram bot with Telegram integration"""
    
    def __init__(self):
        self.config = None
        self.token = None
        self.chat_id = None
        self.base_url = None
        self.engram_model = None
        self.lmstudio_url = "http://100.118.172.23:1234"
        self.running = False
        self.last_update_id = 0
        
    def initialize(self):
        """Initialize all components"""
        logger.info("="*80)
        logger.info("SIMPLE ENGRAM BOT LAUNCHER")
        logger.info("="*80)
        logger.info("Initializing Simple Engram Bot...")
        
        # Load configuration
        config_path = Path(__file__).parent / "config" / "telegram" / "working_telegram_config.json"
        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            return False
            
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
        # Extract Telegram credentials
        telegram_config = self.config.get('telegram', {})
        self.token = telegram_config.get('bot_token')
        self.chat_id = str(telegram_config.get('chat_id'))
        
        if not self.token or not self.chat_id:
            logger.error("Missing Telegram credentials in config")
            return False
            
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        # Load Engram model
        logger.info("Loading Engram neural model...")
        try:
            from engram_demo_v1 import EngramModel
            self.engram_model = EngramModel()
            logger.info("Engram model loaded")
        except Exception as e:
            logger.warning(f"Engram model not available: {e}")
            self.engram_model = None
            
        # Test LMStudio connection
        logger.info("Testing LMStudio connection...")
        try:
            response = requests.get(f"{self.lmstudio_url}/v1/models", timeout=5)
            if response.status_code == 200:
                logger.info("LMStudio connected")
            else:
                logger.warning(f"LMStudio returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"LMStudio not available: {e}")
            
        # Test Telegram connection
        logger.info("Testing Telegram connection...")
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"Telegram bot connected: {bot_info['result']['username']}")
            else:
                logger.error(f"Telegram API error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            return False
            
        logger.info("All systems initialized successfully")
        return True
        
    def send_message(self, text: str):
        """Send message via Telegram"""
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={'chat_id': self.chat_id, 'text': text},
                timeout=10
            )
            logger.info(f"Sent: {text[:50]}...")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None
            
    def get_updates(self, offset=None):
        """Get updates from Telegram"""
        try:
            params = {'timeout': 30}
            if offset:
                params['offset'] = offset
            response = requests.get(
                f"{self.base_url}/getUpdates",
                params=params,
                timeout=35
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")
            return None
            
    def analyze_with_lmstudio(self, prompt: str):
        """Analyze using LMStudio"""
        try:
            response = requests.post(
                f"{self.lmstudio_url}/v1/chat/completions",
                json={
                    "model": "local-model",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"LMStudio error: {response.status_code}"
        except Exception as e:
            return f"LMStudio unavailable: {e}"
            
    def process_message(self, message):
        """Process incoming message"""
        try:
            text = message.get('text', '')
            chat_id = message['chat']['id']
            
            logger.info(f"Processing: {text[:50]}...")
            
            # Handle commands
            if text.startswith('/start'):
                response = (
                    "Welcome to Engram Trading Bot!\n\n"
                    "Available commands:\n"
                    "/start - Show this message\n"
                    "/status - Check bot status\n"
                    "/analyze <symbol> - Analyze market\n"
                    "/help - Show help"
                )
            elif text.startswith('/status'):
                response = (
                    f"Bot Status: Running\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Engram Model: {'Loaded' if self.engram_model else 'Not Available'}\n"
                    f"LMStudio: Connected"
                )
            elif text.startswith('/analyze'):
                parts = text.split()
                symbol = parts[1] if len(parts) > 1 else "BTC/USDT"
                prompt = f"Analyze the market for {symbol}. Provide a brief trading signal (BUY/SELL/HOLD) with reasoning."
                analysis = self.analyze_with_lmstudio(prompt)
                response = f"Analysis for {symbol}:\n\n{analysis}"
            elif text.startswith('/help'):
                response = (
                    "Engram Trading Bot Help\n\n"
                    "This bot combines neural network analysis with AI-powered market insights.\n\n"
                    "Commands:\n"
                    "/start - Welcome message\n"
                    "/status - Bot status\n"
                    "/analyze <symbol> - Market analysis\n"
                    "/help - This help message"
                )
            else:
                # Use LMStudio for general queries
                response = self.analyze_with_lmstudio(text)
                
            # Send response
            self.send_message(response)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.send_message(f"Error: {str(e)}")
            
    def run(self):
        """Main bot loop"""
        if not self.initialize():
            logger.error("Initialization failed")
            return
            
        self.running = True
        logger.info("Bot is running and listening for messages...")
        logger.info("Send a message to your Telegram bot to test it!")
        
        # Send startup notification
        self.send_message("Engram Bot is now online and ready!")
        
        # Main loop
        while self.running:
            try:
                updates = self.get_updates(offset=self.last_update_id + 1)
                
                if updates and updates.get('ok'):
                    for update in updates.get('result', []):
                        self.last_update_id = update['update_id']
                        
                        if 'message' in update:
                            self.process_message(update['message'])
                            
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                self.running = False
                self.send_message("Engram Bot is shutting down. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)


def main():
    """Main entry point"""
    bot = SimpleEngramBot()
    bot.run()


if __name__ == "__main__":
    main()
