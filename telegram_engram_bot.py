#!/usr/bin/env python3
"""
Simple Telegram Bot with Engram Integration
Direct Telegram → Engram integration without ClawdBot
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
    except Exception:
        pass

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    # Try older version import
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
    from telegram import Update
    USE_OLD_API = True
else:
    USE_OLD_API = False
from skills.engram.engram_skill import EngramSkill

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global skill instance
engram_skill = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🤖 *Engram Trading Bot*\n\n"
        "Available commands:\n"
        "/start - Show this message\n"
        "/help - Show help\n"
        "/status - Check bot status\n"
        "/analyze <symbol> - Analyze trading pair\n\n"
        "Send me any message to chat!",
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "📚 *Engram Bot Help*\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/status - Check system status\n"
        "/analyze <symbol> - Analyze a trading pair (e.g., /analyze BTC/USD)\n\n"
        "*Features:*\n"
        "• AI-powered trading analysis\n"
        "• Market sentiment analysis\n"
        "• Real-time price alerts\n"
        "• Portfolio tracking\n\n"
        "Just send me a message to start chatting!",
        parse_mode='Markdown'
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    health = await engram_skill.health_check()
    
    status_text = (
        "📊 *Bot Status*\n\n"
        f"Status: {'✅ Running' if health['status'] == 'healthy' else '❌ Error'}\n"
        f"LMStudio: {'✅ Connected' if health['lmstudio'] else '❌ Disconnected'}\n"
        f"Model: {health.get('model', 'Unknown')}\n"
        f"Tools: {health.get('tools_registered', 0)} registered\n\n"
        "Bot is ready to assist with trading analysis!"
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze command"""
    if not context.args:
        await update.message.reply_text(
            "❌ Please specify a trading pair.\n"
            "Example: `/analyze BTC/USD`",
            parse_mode='Markdown'
        )
        return
    
    symbol = ' '.join(context.args)
    await update.message.reply_text(f"🔍 Analyzing {symbol}...")
    
    try:
        analysis_request = f"Analyze {symbol} and provide trading signal"
        response = await engram_skill.process_message(analysis_request, {})
        await update.message.reply_text(f"📈 *Analysis for {symbol}*\n\n{response}", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        await update.message.reply_text(f"❌ Error analyzing {symbol}: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Processing message from user {user_id}: {user_message[:50]}...")
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        # Process through Engram skill
        context_data = {
            'user_id': user_id,
            'chat_id': update.effective_chat.id,
            'username': update.effective_user.username
        }
        
        response = await engram_skill.process_message(user_message, context_data)
        
        # Send response
        await update.message.reply_text(response)
        logger.info(f"Sent response ({len(response)} chars)")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            "❌ Sorry, I encountered an error processing your message.\n"
            "Please try again later."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error: {context.error}")


async def main():
    """Main entry point"""
    global engram_skill
    
    # Get configuration from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        print("Please set TELEGRAM_BOT_TOKEN environment variable")
        return
    
    # Initialize Engram skill
    logger.info("Initializing Engram skill...")
    config = {
        'lmstudio_host': os.getenv('LMSTUDIO_HOST', '100.118.172.23'),
        'lmstudio_port': int(os.getenv('LMSTUDIO_PORT', '1234')),
        'model': os.getenv('ENGRAM_MODEL', 'glm-4.7-flash'),
    }
    
    engram_skill = EngramSkill(config)
    
    # Test LMStudio connection
    health = await engram_skill.health_check()
    if health['lmstudio']:
        logger.info("[OK] LMStudio connected")
    else:
        logger.warning("[WARN] LMStudio not available")
    
    # Create application
    logger.info("Starting Telegram bot...")
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("=" * 60)
    logger.info("Telegram Engram Bot Started")
    logger.info("=" * 60)
    logger.info("Bot is running and listening for messages...")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        await engram_skill.shutdown()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
