#!/usr/bin/env python3
"""
Simple script to run the live Engram Telegram bot with LMStudio integration.
"""

import sys
import os
import asyncio
import logging
import json
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Import Engram components
from src.core.engram_demo_v1 import EngramModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleEngramTelegramBot:
    """
    Simple Telegram bot with LMStudio integration for natural language trading conversations.
    """

    def __init__(self, token: str, chat_id: str, lmstudio_url: str = "http://100.118.172.23:1234"):
        self.token = token
        self.chat_id = chat_id
        self.lmstudio_url = lmstudio_url
        self.engram_model = None
        self.engram_initialized = False

        # Initialize Engram model
        self._initialize_engram()

    def _initialize_engram(self):
        """Initialize Engram model for LMStudio integration."""
        try:
            logger.info("Initializing Engram model with LMStudio...")
            self.engram_model = EngramModel(use_lmstudio=True, lmstudio_url=self.lmstudio_url)
            self.engram_initialized = True
            logger.info("✅ Engram model initialized with LMStudio")
        except Exception as e:
            logger.error(f"Failed to initialize Engram: {e}")
            self.engram_initialized = False

    def _query_lmstudio(self, prompt: str) -> str:
        """Query LMStudio API."""
        try:
            response = requests.post(
                f"{self.lmstudio_url}/v1/chat/completions",
                json={
                    "model": "glm-4.7b-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"LMStudio query failed: {e}")
            return f"Error querying LMStudio: {e}"

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_text = """
🤖 *Welcome to Engram AI Trading Bot!*

I'm your AI-powered trading assistant connected to LMStudio.

🔹 *Commands:*
💬 `/chat <message>` - Ask anything about trading
🧠 `/status` - Check system status
📊 `/analyze` - Market analysis
🔮 `/predict` - AI predictions
📈 `/help` - Show this help

Just type your trading questions naturally and I'll respond using AI!
        """

        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        status_text = f"""
🔬 *System Status*
━━━━━━━━━━━━━━━━━━━━━━━

🤖 *LMStudio Connection:* {'✅ Connected' if self.engram_initialized else '❌ Disconnected'}
🧠 *AI Model:* GLM-4.7B Chat
🌐 *LMStudio URL:* {self.lmstudio_url}
💬 *Telegram Bot:* ✅ Active

*Last Check:* {asyncio.get_event_loop().time()}
        """

        await update.message.reply_text(
            status_text,
            parse_mode=ParseMode.MARKDOWN
        )

    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chat command."""
        if not context.args:
            await update.message.reply_text(
                "💬 *Usage:* `/chat What should I do with my BTC position?`\n\n"
                "Or just type your question directly!",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        user_query = " ".join(context.args)
        await self._process_query(update, user_query)

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command."""
        query = "Provide a detailed market analysis for cryptocurrency trading. Include current trends, key indicators, and trading recommendations."
        await self._process_query(update, query)

    async def predict_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /predict command."""
        query = "Based on current market conditions, predict the next 24-hour price movements for BTC, ETH, and major altcoins. Include confidence levels and risk assessment."
        await self._process_query(update, query)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """
📚 *Help - Engram AI Trading Bot*

🔹 *How to Use:*
• Type natural language questions about trading
• Use commands for specific functions
• Ask about market analysis, predictions, or strategies

🔹 *Commands:*
/start - Welcome message
/status - Check system status
/chat <message> - Ask specific questions
/analyze - Market analysis
/predict - AI predictions
/help - This help message

🔹 *Examples:*
• "Should I buy BTC now?"
• "What's the market sentiment?"
• "Analyze ETH price action"
• "Risk assessment for altcoins"

💡 *Tip:* The more specific your question, the better the AI response!
        """

        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user_text = update.message.text
        await self._process_query(update, user_text)

    async def _process_query(self, update: Update, query: str):
        """Process a query using LMStudio."""
        if not self.engram_initialized:
            await update.message.reply_text(
                "❌ AI system is not available. Please check LMStudio connection.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Show typing indicator
        await update.message.chat.send_action("typing")

        try:
            # Format the query for better trading context
            trading_prompt = f"""
You are an expert cryptocurrency trading AI assistant. Provide helpful, accurate, and natural responses to trading questions.

User Question: {query}

Please provide a comprehensive response that includes:
- Clear analysis or answer
- Relevant trading insights
- Risk considerations when applicable
- Actionable recommendations

Keep responses conversational but informative.
            """

            # Get response from LMStudio
            response = self._query_lmstudio(trading_prompt)

            # Format for Telegram
            formatted_response = f"""
💬 *AI Trading Assistant*

🤔 *Your Question:* {query[:100]}{'...' if len(query) > 100 else ''}

🧠 *AI Response:*
{response[:3000]}{'...' if len(response) > 3000 else ''}

💡 *Need more details?* Try `/analyze` or `/predict` commands!
            """

            await update.message.reply_text(
                formatted_response,
                parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            await update.message.reply_text(
                f"❌ Error processing your request: {str(e)[:100]}",
                parse_mode=ParseMode.MARKDOWN
            )

    async def start_bot(self):
        """Start the Telegram bot."""
        application = Application.builder().token(self.token).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("chat", self.chat_command))
        application.add_handler(CommandHandler("analyze", self.analyze_command))
        application.add_handler(CommandHandler("predict", self.predict_command))
        application.add_handler(CommandHandler("help", self.help_command))

        # Add message handler for natural language
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
        )

        # Set bot commands
        await application.bot.set_my_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("status", "Check system status"),
            BotCommand("chat", "Ask trading questions"),
            BotCommand("analyze", "Market analysis"),
            BotCommand("predict", "AI predictions"),
            BotCommand("help", "Show help"),
        ])

        logger.info("🤖 Bot is starting...")
        await application.run_polling()


async def main():
    """Run the live system."""
    try:
        logger.info("🚀 Starting live Engram Telegram bot...")

        # Load config from working_telegram_config.json
        config_path = "config/telegram/working_telegram_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)

        telegram_config = config.get('telegram', {})
        token = telegram_config.get('token')
        chat_id = telegram_config.get('chat_id')

        if not token or not chat_id:
            logger.error("Telegram token or chat_id not found in config")
            sys.exit(1)

        # Initialize bot
        bot = SimpleEngramTelegramBot(token, chat_id)
        logger.info("✅ Telegram bot initialized")

        # Start the bot
        await bot.start_bot()

    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
