#!/usr/bin/env python3
"""
Simple Engram Launcher - Standalone Version
============================================

This is a simplified launcher that runs Engram + LMStudio + Telegram bot
without FreqTrade dependencies.

Usage:
    python simple_engram_launcher.py

Features:
- Engram neural model for AI analysis
- LMStudio integration for market insights
- Telegram bot for user interaction
- No FreqTrade required
"""

import sys
import os
import logging
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.engram_demo_v1 import EngramModel
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_engram.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class SimpleEngramBot:
    """Simple Engram bot with Telegram integration."""
    
    def __init__(self):
        self.telegram_token = "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
        self.chat_id = "1007321485"
        self.lmstudio_url = "http://192.168.56.1:1234/v1/chat/completions"
        self.base_url = f"https://api.telegram.org/bot{self.telegram_token}"
        self.last_update_id = 0
        self.engram_model = None
        
    def initialize(self):
        """Initialize Engram model and connections."""
        try:
            logger.info("🚀 Initializing Simple Engram Bot...")
            
            # Initialize Engram model with LMStudio
            logger.info("Loading Engram neural model...")
            self.engram_model = EngramModel(
                use_clawdbot=False,
                use_lmstudio=True,
                lmstudio_url="http://192.168.56.1:1234"
            )
            logger.info("✅ Engram model loaded")
            
            # Test LMStudio connection
            logger.info("Testing LMStudio connection...")
            response = requests.get("http://192.168.56.1:1234/v1/models", timeout=5)
            if response.status_code == 200:
                logger.info("✅ LMStudio connected")
            else:
                logger.warning("⚠️ LMStudio connection issue")
            
            # Test Telegram connection
            logger.info("Testing Telegram connection...")
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"✅ Telegram bot connected: {bot_info['result']['username']}")
            else:
                logger.error("❌ Telegram connection failed")
                return False
            
            logger.info("✅ All systems initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def send_message(self, text: str):
        """Send message to Telegram."""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"Sent: {text[:50]}...")
            else:
                logger.error(f"Failed to send message: {response.text}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def query_lmstudio(self, prompt: str) -> str:
        """Query LMStudio for AI response."""
        try:
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert cryptocurrency trading assistant powered by Engram neural architecture. Provide helpful, accurate trading advice and market analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500,
                "stream": False
            }
            
            response = requests.post(
                self.lmstudio_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"LMStudio query error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def handle_command(self, command: str) -> str:
        """Handle bot commands."""
        if command == "/start":
            return """
🤖 *Welcome to Simple Engram Bot!*

I'm powered by Engram neural architecture and LMStudio AI.

Commands:
/start - Show this message
/status - Bot status
/analyze - Market analysis
/help - Help

Or just ask me anything about trading!
            """
        elif command == "/status":
            return """
✅ *Bot Status: Online*

🧠 Engram Model: Active
🤖 LMStudio: Connected
📱 Telegram: Connected

Ready to help with trading!
            """
        elif command == "/analyze":
            self.send_message("📊 Analyzing markets...")
            prompt = "Provide a brief market analysis for BTC, ETH, and major altcoins. Include current trends and trading opportunities."
            response = self.query_lmstudio(prompt)
            return f"📊 *Market Analysis:*\n\n{response}"
        elif command == "/help":
            return """
🤖 *Engram Bot Help*

Commands:
/start - Welcome message
/status - Check bot status
/analyze - Get market analysis
/help - This help message

You can also ask me questions directly:
• "Should I buy BTC now?"
• "What's the market sentiment?"
• "Analyze ETH price action"
            """
        else:
            return None
    
    def process_message(self, message_text: str) -> str:
        """Process incoming message."""
        logger.info(f"Processing: {message_text}")
        
        # Check for commands
        if message_text.startswith("/"):
            response = self.handle_command(message_text)
            if response:
                return response
        
        # Regular message - use Engram + LMStudio
        return self.query_lmstudio(message_text)
    
    def get_updates(self):
        """Get updates from Telegram."""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "timeout": 30
            }
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json().get("result", [])
            else:
                logger.error(f"Failed to get updates: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []
    
    def run(self):
        """Run the bot."""
        if not self.initialize():
            logger.error("❌ Failed to initialize bot")
            return
        
        logger.info("🤖 Bot is running and listening for messages...")
        logger.info("📱 Send a message to your Telegram bot to test it!")
        
        # Send startup message
        self.send_message("🤖 Engram Bot is now online and ready!")
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    if "message" in update and "text" in update["message"]:
                        self.last_update_id = update["update_id"]
                        
                        message_text = update["message"]["text"]
                        response = self.process_message(message_text)
                        
                        self.send_message(response)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")
                self.send_message("🛑 Bot is shutting down. Goodbye!")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(5)


def main():
    """Main entry point."""
    logger.info("="*80)
    logger.info("SIMPLE ENGRAM BOT LAUNCHER")
    logger.info("="*80)
    
    bot = SimpleEngramBot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
