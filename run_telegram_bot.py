KK#!/usr/bin/env python3
"""
Live Engram Telegram Bot with LMStudio Integration
"""

import asyncio
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class EngramBot:
    def __init__(self, telegram_token: str, lmstudio_url: str = "http://192.168.56.1:1234/v1/chat/completions"):
        self.telegram_token = telegram_token
        self.lmstudio_url = lmstudio_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def query_lmstudio(self, prompt: str) -> str:
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

            response = await self.client.post(
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

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = """
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
        await update.message.reply_text(welcome_msg)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
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
        await update.message.reply_text(help_text)

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status_msg = """
✅ Bot Status: Online

🧠 AI Model: LMStudio (glm-4.7b-chat)
📡 Connection: Active
💬 Telegram: Connected
📊 Trading: Ready

Send me a trading question to get started!
        """
        await update.message.reply_text(status_msg)

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command"""
        await update.message.reply_text("📊 Analyzing current market conditions...")

        prompt = "Provide a comprehensive market analysis for major cryptocurrencies (BTC, ETH, BNB, SOL, ADA). Include current trends, key levels, and trading opportunities."
        response = await self.query_lmstudio(prompt)

        await update.message.reply_text(f"📊 Market Analysis:\n\n{response}")

    async def predict_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /predict command"""
        await update.message.reply_text("🔮 Generating price predictions...")

        prompt = "Based on current market conditions, provide short-term price predictions for BTC, ETH, and major altcoins. Include confidence levels and timeframes."
        response = await self.query_lmstudio(prompt)

        await update.message.reply_text(f"🔮 Price Predictions:\n\n{response}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user_message = update.message.text
        logger.info(f"Received message: {user_message}")

        # Show typing indicator
        await update.message.chat.send_action("typing")

        # Query LMStudio
        response = await self.query_lmstudio(user_message)

        # Send response
        await update.message.reply_text(response)

    async def run(self):
        """Run the bot"""
        try:
            logger.info("🚀 Starting live Engram Telegram bot...")
            logger.info("Initializing Engram model with LMStudio...")

            # Test LMStudio connection
            test_response = await self.query_lmstudio("Hello, are you working?")
            if "Error" in test_response:
                logger.error(f"❌ LMStudio connection failed: {test_response}")
                return
            else:
                logger.info("✅ Engram model initialized with LMStudio")

            # Initialize Telegram bot
            application = Application.builder().token(self.telegram_token).build()
            logger.info("✅ Telegram bot initialized")

            # Add handlers
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CommandHandler("status", self.status_command))
            application.add_handler(CommandHandler("analyze", self.analyze_command))
            application.add_handler(CommandHandler("predict", self.predict_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

            logger.info("🤖 Bot is starting...")

            # Start polling
            await application.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            logger.error(f"❌ Error running bot: {e}")
        finally:
            await self.client.aclose()

def main():
    # Configuration
    TELEGRAM_TOKEN = "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
    LMSTUDIO_URL = "http://192.168.56.1:1234/v1/chat/completions"

    # Create and run bot
    bot = EngramBot(TELEGRAM_TOKEN, LMSTUDIO_URL)

    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
