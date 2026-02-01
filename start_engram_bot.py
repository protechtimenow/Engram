"""
Engram Standalone Bot
Direct Telegram + LMStudio integration (no ClawdBot WebSocket dependency)
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

from bot.telegram_bot import EngramTelegramBot


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "engram_bot.log")
        ]
    )


async def main():
    """Main entry point"""
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Engram Standalone Bot Starting")
    logger.info("=" * 60)
    
    # Configuration
    config = {
        # LMStudio settings
        "lmstudio_host": os.getenv("LMSTUDIO_HOST", "100.118.172.23"),
        "lmstudio_port": int(os.getenv("LMSTUDIO_PORT", "1234")),
        "model": os.getenv("ENGRAM_MODEL", "glm-4.7-flash"),
        
        # Telegram settings
        "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
        
        # Agent settings
        "response_format": os.getenv("ENGRAM_RESPONSE_FORMAT", "clean")
    }
    
    logger.info("Configuration:")
    logger.info(f"  LMStudio: {config['lmstudio_host']}:{config['lmstudio_port']}")
    logger.info(f"  Model: {config['model']}")
    logger.info(f"  Telegram: {'Configured' if config['telegram_token'] else 'Not configured'}")
    logger.info(f"  Response Format: {config['response_format']}")
    
    # Create and run bot
    bot = EngramTelegramBot(config)
    
    try:
        logger.info("Starting Engram Telegram bot...")
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        logger.info("Shutting down...")
        await bot.shutdown()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
