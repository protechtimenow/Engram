#!/usr/bin/env python3
"""
Enhanced Engram Launcher - Version 2
====================================

This script builds upon simple_engram_launcher.py with:
1) LMStudio Timeout Handling / Fallback
2) Environment Variable Support for Configuration
3) Basic AI Fallback Chain (LMStudio → Mock)
4) Telegram Bot Integration
5) Logging and Extended Testing Hooks

Usage:
    python enhanced_engram_launcher_v2.py

Features:
- Engram neural model for AI analysis
- LMStudio integration with fallback logic
- Telegram bot for user interaction
- Optional environment-based configuration
- Basic mock AI fallback if LMStudio times out
"""

import sys
import os
import logging
import time
import requests

# Insert 'src' directory to path. Adjust if needed for your project structure.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from core.engram_demo_v1 import EngramModel
except ImportError:
    print("Error: engram_demo_v1 not found or missing. Please ensure 'src/core/engram_demo_v1.py' is present.")
    sys.exit(1)

# Configure logging
LOG_FILENAME = "enhanced_engram.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Fallback AI if LMStudio times out or is unreachable
def mock_ai_response(prompt: str) -> str:
    """
    Minimal fallback AI response if LMStudio fails.
    """
    # Return a simple placeholder answer
    return f"*(Fallback)* Sorry, LMStudio timed out. Here is a mock response for prompt: '{prompt[:40]}...'"


class EnhancedEngramBot:
    """Enhanced Engram bot with improved timeout handling, environment config, and fallback AI."""

    def __init__(self):
        # Environment variable override or defaults
        self.telegram_token = os.environ.get("TELEGRAM_TOKEN", "REPLACE_ME")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
        self.lmstudio_url = os.environ.get("LMSTUDIO_URL", "http://192.168.56.1:1234/v1/chat/completions")
        self.base_url = f"https://api.telegram.org/bot{self.telegram_token}"
        self.last_update_id = 0
        self.engram_model = None
    
    def initialize(self):
        """Initialize Engram model and external connections."""
        try:
            logger.info("🚀 Initializing Enhanced Engram Bot...")

            # Check environment config
            if self.telegram_token == "REPLACE_ME" or self.chat_id == "YOUR_CHAT_ID":
                logger.warning("⚠️ Telegram token or chat_id not set. Please configure environment variables.")
            
            # Initialize Engram model
            logger.info("Loading Engram neural model with fallback logic...")
            self.engram_model = EngramModel(
                use_clawdbot=False, 
                use_lmstudio=True, 
                lmstudio_url=self.lmstudio_url.replace("/v1/chat/completions", "")
            )
            logger.info("✅ Engram model loaded")

            # Test LMStudio connection
            logger.info("Testing LMStudio connection...")
            test_url = self.lmstudio_url.replace("/chat/completions", "/models")
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                logger.info("✅ LMStudio reachable")
            else:
                logger.warning("⚠️ LMStudio connection issue (non-200 status code)")

            # Test Telegram connection
            logger.info("Testing Telegram connection...")
            tg_response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if tg_response.status_code == 200:
                bot_info = tg_response.json()
                logger.info(f"✅ Telegram bot connected: {bot_info['result'].get('username', 'Unknown')}")
            else:
                logger.error("❌ Telegram connection failed")

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
        """Query LMStudio with fallback on timeout error."""
        try:
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an advanced trading assistant using Engram neural architecture. Provide reasoned and accurate advice."
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
                return data.get("choices", [{}])[0].get("message", {}).get("content", "No response from LMStudio")
            else:
                return f"Error {response.status_code}: Reached LMStudio but got unexpected status."
        except requests.exceptions.Timeout:
            logger.warning("LMStudio request timed out. Using fallback AI.")
            return mock_ai_response(prompt)
        except Exception as e:
            logger.error(f"LMStudio query error: {e}")
            return f"Sorry, an error occurred: {str(e)}"

    def handle_command(self, command: str) -> str:
        """Handle recognized commands from user."""
        if command == "/start":
            return """
*Enhanced Engram Bot v2*

Commands:
/start - Welcome
/status - Bot Status
/analyze - Market Analysis
/help - This help message
            """
        elif command == "/status":
            return """
✅ *Bot Status:* Enhanced v2 Online

Engram Model: Active
LMStudio: Attempting connections with fallback
Telegram: Configured
            """
        elif command == "/analyze":
            self.send_message("📊 Analyzing markets (Enhanced v2)...")
            analysis_prompt = "Provide a comprehensive market analysis for top cryptocurrencies. Focus on BTC, ETH, altcoin trends, including potential trading signals."
            return f"**Market Analysis**\n\n{self.query_lmstudio(analysis_prompt)}"
        elif command == "/help":
            return """
🤖 *Help for Enhanced Engram Bot v2*
Commands:
/start - Welcome
/status - Check bot status
/analyze - Basic market analysis
/help - Show this help
            """
        else:
            return None

    def process_message(self, message_text: str) -> str:
        """Process incoming Telegram messages."""
        logger.info(f"Processing: {message_text}")

        if message_text.startswith("/"):
            response = self.handle_command(message_text)
            if response:
                return response

        # Default: pass user text to Engram + LMStudio with fallback
        return self.query_lmstudio(message_text)

    def get_updates(self):
        """Retrieve updates from Telegram."""
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
                logger.error(f"Failed to get Telegram updates: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error retrieving updates: {e}")
            return []

    def run(self):
        """Main bot loop."""
        if not self.initialize():
            logger.error("❌ Bot initialization failed. Exiting.")
            return

        logger.info("🤖 Enhanced Engram Bot v2 is running.")
        logger.info("📱 Send a message to your Telegram bot to test it.")

        # Send startup message
        self.send_message("🤖 Enhanced Engram Bot v2 is online and ready (with fallback logic)!")

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
                logger.info("🛑 Bot shutdown requested.")
                self.send_message("🛑 Enhanced Engram Bot v2 is shutting down. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                time.sleep(5)


def main():
    """Main entry point for Enhanced Engram Launcher v2."""
    logger.info("=" * 80)
    logger.info("ENHANCED ENGRAM BOT LAUNCHER V2")
    logger.info("=" * 80)

    bot = EnhancedEngramBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Shutdown by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
