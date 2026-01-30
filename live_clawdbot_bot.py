#!/usr/bin/env python3
"""
Live Engram Telegram bot with ClawdBot + LMStudio integration.
"""

import sys
import os
import asyncio
import logging
import json
import websockets

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiveClawdBotTelegramBot:
    """
    Telegram bot integrated with ClawdBot gateway for LMStudio GLM-4.7B Chat responses.
    """

    def __init__(self, token: str, chat_id: str, clawdbot_ws_url: str = "ws://127.0.0.1:18789"):
        self.token = token
        self.chat_id = chat_id
        self.clawdbot_ws_url = clawdbot_ws_url
        self.websocket = None

    async def _connect_clawdbot(self):
        """Connect to ClawdBot WebSocket."""
        try:
            self.websocket = await websockets.connect(self.clawdbot_ws_url)
            logger.info("✅ Connected to ClawdBot WebSocket")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to ClawdBot: {e}")
            return False

    async def _query_clawdbot(self, message: str) -> str:
        """Send message to ClawdBot and get response."""
        if not self.websocket:
            connected = await self._connect_clawdbot()
            if not connected:
                return "❌ Cannot connect to ClawdBot gateway"

        try:
            # Send message
            await self.websocket.send(json.dumps({
                "type": "chat",
                "message": message,
                "model": "openai/glm-4.7b-chat"
            }))

            # Receive response
            response = await self.websocket.recv()
            result = json.loads(response)

            if "error" in result:
                return f"ClawdBot Error: {result['error']}"

            return result.get("response", "No response from ClawdBot")

        except Exception as e:
            logger.error(f"ClawdBot query failed: {e}")
            # Try to reconnect
            self.websocket = None
            return f"Error: {str(e)}"

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_text = """
🤖 *Engram AI Trading Bot - LIVE*

Connected to ClawdBot Gateway + LMStudio GLM-4.7B Chat

🔹 *Commands:*
💬 `/chat <message>` - Ask trading questions
🧠 `/status` - System status
📊 `/analyze` - Market analysis
🔮 `/predict` - AI predictions
📈 `/help` - Help

*Just type your trading questions naturally!*
        """

        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        ws_status = "✅ Connected" if self.websocket else "❌ Disconnected"

        status_text = f"""
🔬 *System Status*
━━━━━━━━━━━━━━━━━━━━━━━

🦞 *ClawdBot Gateway:* {ws_status}
🌐 *WebSocket URL:* {self.clawdbot_ws_url}
🧠 *AI Model:* GLM-4.7B Chat (via LMStudio)
💬 *Telegram Bot:* ✅ Active
📡 *Gateway Port:* 18789

*Mode:* Live AI responses through ClawdBot
        """

        await update.message.reply_text(
            status_text,
            parse_mode=ParseMode.MARKDOWN
        )

    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chat command."""
        if not context.args:
            await update.message.reply_text(
                "💬 *Usage:* `/chat What should I do with BTC?`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        user_query = " ".join(context.args)
        await self._process_trading_query(update, user_query)

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command."""
        query = "Provide a comprehensive cryptocurrency market analysis including current trends, key indicators, and trading recommendations."
        await self._process_trading_query(update, query)

    async def predict_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /predict command."""
        query = "Predict the next 24-hour price movements for BTC, ETH, and major altcoins. Include confidence levels and risk assessments."
        await self._process_trading_query(update, query)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """
📚 *Engram AI Trading Bot Help*

🔹 *How to Use:*
• Type natural language trading questions
• Use commands for specific analysis
• Get AI-powered trading insights

🔹 *Commands:*
/start - Welcome message
/status - System status
/chat <question> - Ask specific questions
/analyze - Market analysis
/predict - AI predictions
/help - This help

🔹 *Examples:*
• "Should I buy BTC now?"
• "What's the market doing?"
• "Analyze ETH price action"
• "Risk assessment for altcoins"

💡 *AI Model:* GLM-4.7B Chat via ClawdBot + LMStudio
        """

        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages with AI."""
        user_text = update.message.text
        await self._process_trading_query(update, user_text)

    async def _process_trading_query(self, update: Update, query: str):
        """Process trading query through ClawdBot."""
        # Show typing indicator
        await update.message.chat.send_action("typing")

        try:
            # Format query for trading context
            trading_prompt = f"""
You are an expert cryptocurrency trading AI assistant with deep market knowledge.

User Question: {query}

Please provide a comprehensive, helpful response that includes:
- Clear analysis and insights
- Relevant trading information
- Risk considerations when applicable
- Actionable recommendations

Be conversational, informative, and focus on trading/crypto markets.
            """

            # Get AI response from ClawdBot
            ai_response = await self._query_clawdbot(trading_prompt)

            # Format for Telegram
            formatted_response = f"""
💬 *AI Trading Assistant*

🤔 *Your Question:* {query[:100]}{'...' if len(query) > 100 else ''}

🧠 *AI Response:*
{ai_response[:3500]}{'...' if len(ai_response) > 3500 else ''}

💡 *Powered by ClawdBot + LMStudio GLM-4.7B*
            """

            await update.message.reply_text(
                formatted_response,
                parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            await update.message.reply_text(
                f"❌ Error: {str(e)[:100]}",
                parse_mode=ParseMode.MARKDOWN
            )

    async def start_bot(self):
        """Start the Telegram bot."""
        # Connect to ClawdBot first
        logger.info("🔌 Connecting to ClawdBot gateway...")
        connected = await self._connect_clawdbot()
        if not connected:
            logger.error("Failed to connect to ClawdBot. Please ensure gateway is running.")
            return

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

        logger.info("🤖 Bot is starting with ClawdBot integration...")
        await application.run_polling()


async def main():
    """Run the live ClawdBot-integrated system."""
    try:
        logger.info("🚀 Starting Engram Telegram bot with ClawdBot + LMStudio...")

        # Load config
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
        bot = LiveClawdBotTelegramBot(token, chat_id)
        logger.info("✅ Bot initialized with ClawdBot WebSocket")

        # Start the bot
        await bot.start_bot()

    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        if 'bot' in locals() and bot.websocket:
            await bot.websocket.close()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
