#!/usr/bin/env python3
"""
Live Bot Runner - Keeps Clawdbot running persistently
Handles graceful shutdown and automatic restarts
"""

import asyncio
import signal
import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/vercel/sandbox/logs/bot_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import the bot
from live_telegram_bot import main as bot_main

class BotRunner:
    """Manages bot lifecycle and persistence"""
    
    def __init__(self):
        self.running = True
        self.restart_count = 0
        self.max_restarts = 5
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    async def run_with_monitoring(self):
        """Run bot with monitoring and auto-restart"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🚀 Bot Runner Started")
        logger.info(f"📱 Phone: +447585185906")
        logger.info(f"🕐 Start Time: {datetime.now()}")
        
        while self.running and self.restart_count < self.max_restarts:
            try:
                logger.info(f"🤖 Starting bot (attempt {self.restart_count + 1}/{self.max_restarts})")
                
                # Run the bot
                await bot_main()
                
                # If we get here, bot stopped normally
                logger.info("Bot stopped normally")
                break
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
                
            except Exception as e:
                logger.error(f"Bot crashed: {e}")
                self.restart_count += 1
                
                if self.restart_count < self.max_restarts:
                    logger.info(f"Restarting in 5 seconds... ({self.restart_count}/{self.max_restarts})")
                    await asyncio.sleep(5)
                else:
                    logger.error("Max restart attempts reached, exiting")
                    break
        
        logger.info("🛑 Bot Runner Stopped")


async def main():
    """Main entry point"""
    runner = BotRunner()
    await runner.run_with_monitoring()


if __name__ == '__main__':
    # Ensure logs directory exists
    os.makedirs('/vercel/sandbox/logs', exist_ok=True)
    
    # Run the bot runner
    asyncio.run(main())
