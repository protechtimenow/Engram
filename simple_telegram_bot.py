#!/usr/bin/env python3
"""
Simple Telegram Bot with LMStudio - No asyncio conflicts
"""

import logging
import sys
import time
from telegram import Bot
from telegram.error import TelegramError
import httpx

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleEngramBot:
    def __init__(self, telegram_token: str, chat_id: str, lmstudio_url: str = "http://192.168.56.1:1234/v1/chat/completions"):
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self.lmstudio_url = lmstudio_url
        self.bot = Bot(token=telegram_token)
        self.client = httpx.Client(timeout=30.0)
        self.last_update_id = 0

    def query_lmstudio(self, prompt: str) -> str:
        """Query LMStudio for AI response"""
        try:
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert cryptocurrency trading assistant. Provide helpful, accurate trading advice and market analysis. Be concise but informative."
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

            response = self.client.post(
                self.lmstudio_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
            else:
                return f"Error: {response.status_code} - {response.text}"

        except Exception as e:
            logger.error(f"LMStudio query error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    def send_message(self, text: str):
        """Send message to Telegram"""
        try:
            self.bot.send_message(chat_id=self.chat_id, text=text)
            logger.info(f"Sent message: {text[:50]}...")
        except TelegramError as e:
            logger.error(f"Failed to send message: {e}")

    def handle_command(self, command: str, args: str = "") -> str:
        """Handle bot commands"""
        if command == "/start":
            return """
🤖 Welcome to Engram Trading Bot!

I'm your AI-powered cryptocurrency trading assistant. I can help you with:

📊 Market Analysis
💡 Trading Strategies
📈 Price Predictions
📰 Market News & Insights
💬 General Trading Questions

Just type your question or use these commands:
/analyze - Market analysis
/predict - Price predictions
/status - Bot status
/help - Show this help

How can I help you with trading today?
            """
        elif command == "/help":
            return """
🤖 Engram Trading Bot Commands:

📊 /analyze - Get market analysis
💡 /predict - Price predictions
📊 /status - Check bot status
🆘 /help - Show this help

💬 Or just ask me anything about trading!

Examples:
• "Should I buy BTC now?"
• "What's the market sentiment?"
• "Analyze ETH price action"
• "Best trading strategy for altcoins?"
            """
        elif command == "/status":
            return """
✅ Bot Status: Online

🧠 AI Model: LMStudio (glm-4.7b-chat)
📡 Connection: Active
💬 Telegram: Connected
📊 Trading: Ready

Send me a trading question to get started!
            """
        elif command == "/analyze":
            self.send_message("📊 Analyzing current market conditions...")
            prompt = "Provide a comprehensive market analysis for major cryptocurrencies (BTC, ETH, BNB, SOL, ADA). Include current trends, key levels, and trading opportunities."
            response = self.query_lmstudio(prompt)
            return f"📊 Market Analysis:\n\n{response}"
        elif command == "/predict":
            self.send_message("🔮 Generating price predictions...")
            prompt = "Based on current market conditions, provide short-term price predictions for BTC, ETH, and major altcoins. Include confidence levels and timeframes."
            response = self.query_lmstudio(prompt)
            return f"🔮 Price Predictions:\n\n{response}"
        else:
            return None

    def process_message(self, message_text: str) -> str:
        """Process incoming message"""
        logger.info(f"Processing message: {message_text}")

        # Check for commands
        if message_text.startswith("/"):
            parts = message_text.split(" ", 1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            response = self.handle_command(command, args)
            if response:
                return response

        # Regular message - query LMStudio
        return self.query_lmstudio(message_text)

    def run(self):
        """Run the bot"""
        logger.info("🚀 Starting simple Engram Telegram bot...")

        # Test LMStudio connection
        logger.info("Testing LMStudio connection...")
        test_response = self.query_lmstudio("Hello, are you working?")
        if "Error" in test_response:
            logger.error(f"❌ LMStudio connection failed: {test_response}")
            return
        else:
            logger.info("✅ Engram model initialized with LMStudio")

        # Test Telegram connection
        try:
            self.bot.get_me()
            logger.info("✅ Telegram bot initialized")
        except TelegramError as e:
            logger.error(f"❌ Telegram connection failed: {e}")
            return

        logger.info("🤖 Bot is running and listening for messages...")

        while True:
            try:
                # Get updates
                updates = self.bot.get_updates(offset=self.last_update_id + 1, timeout=30)

                for update in updates:
                    if update.message and update.message.text:
                        self.last_update_id = update.update_id

                        # Process the message
                        response = self.process_message(update.message.text)

                        # Send response
                        self.send_message(response)

                time.sleep(1)  # Small delay to prevent spam

            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying

def main():
    # Configuration
    TELEGRAM_TOKEN = "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
    CHAT_ID = "1007321485"
    LMSTUDIO_URL = "http://192.168.56.1:1234/v1/chat/completions"

    # Create and run bot
    bot = SimpleEngramBot(TELEGRAM_TOKEN, CHAT_ID, LMSTUDIO_URL)

    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
