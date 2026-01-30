#!/usr/bin/env python3
"""
Engram-FreqTrade Integration Launcher
=====================================

This script launches an integrated trading system that combines:
- FreqTrade's robust trading framework
- Engram's neural architecture for AI analysis
- Enhanced Telegram bot with natural language processing

Usage:
    python launch_engram_trader.py [--config config.json] [--dry-run]

Features:
- AI-powered trading signals
- Natural language Telegram interface
- Real-time market analysis
- Risk management through neural networks
- Portfolio optimization suggestions
"""

import sys
import os
import json
import logging
import argparse
from pathlib import Path

# Add current directory and src/ to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

print("DEBUG sys.path:", sys.path)
print("DEBUG current dir:", os.getcwd())

try:
    import sys
    import os
    sys.path.insert(0, '/home/offstar0/.local/lib/python3.13/site-packages')
    # Add freqtrade directory for development install
    freqtrade_path = os.path.join(os.path.dirname(__file__), '..', 'freqtrade')
    sys.path.insert(0, freqtrade_path)

    from freqtrade.configuration.configuration import Configuration
    from freqtrade.freqtradebot import FreqtradeBot
    from freqtrade.rpc.rpc_manager import RPCManager
    from freqtrade.persistence import Trade
    from freqtrade.data.dataprovider import DataProvider

    # Import our custom components
    from src.trading.engram_trading_strategy import EngramStrategy
    from src.telegram.engram_telegram_bot import EngramTelegramBot
    from src.core.engram_demo_v1 import EngramModel, engram_cfg
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure FreqTrade is installed: pip install freqtrade")
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('engram_trader.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class EngramFreqTrader:
    """
    Main integration class that combines FreqTrade with Engram capabilities.
    """
    
    def __init__(self, config_path: str = None):
        self.config = None
        self.freqtrade_bot = None
        self.rpc_manager = None
        self.engram_bot = None
        self.engram_model = None
        
        # Load configuration
        self._load_configuration(config_path)
        
        # Initialize components
        self._initialize_engram()
        self._initialize_freqtrade()
        
        logger.info("Engram-FreqTrader initialized successfully")

    def _load_configuration(self, config_path: str):
        """Load configuration from file."""
        default_config = Path(__file__).parent.parent / "config" / "engram_freqtrade_config.json"
        
        if config_path is None:
            config_path = default_config
        
        try:
            with open(config_path, 'r') as f:
                full_config = json.load(f)
            
            # Extract FreqTrade configuration
            freqtrade_config = full_config.get('freqtrade', {})
            
            # Add Engram configuration to FreqTrade config
            freqtrade_config['engram'] = full_config.get('engram', {})
            freqtrade_config['telegram'] = full_config.get('telegram', {})
            freqtrade_config['api_server'] = full_config.get('api_server', {})
            
            # Set strategy path to project root directory
            freqtrade_config['strategy_path'] = str(Path(__file__).parent.parent)
            
            # Initialize FreqTrade configuration
            self.config = Configuration.from_files([config_path], freqtrade_config)
            
            logger.info(f"Configuration loaded from: {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)

    def _initialize_engram(self):
        """Initialize Engram model and components."""
        try:
            engram_config = self.config.get('engram', {})
            
            if engram_config.get('enabled', True):
                logger.info("Initializing Engram model...")
                
                # Update Engram configuration from file
                if 'max_ngram_size' in engram_config:
                    engram_cfg.max_ngram_size = engram_config['max_ngram_size']
                if 'n_embed_per_ngram' in engram_config:
                    engram_cfg.n_embed_per_ngram = engram_config['n_embed_per_ngram']
                if 'n_head_per_ngram' in engram_config:
                    engram_cfg.n_head_per_ngram = engram_config['n_head_per_ngram']
                if 'layer_ids' in engram_config:
                    engram_cfg.layer_ids = engram_config['layer_ids']
                
                # Initialize the model
                self.engram_model = EngramModel()
                
                logger.info("✅ Engram model initialized successfully")
                logger.info(f"🧠 Neural Architecture: {engram_cfg.max_ngram_size}-gram network")
                logger.info(f"📊 Embedding Dimensions: {engram_cfg.n_embed_per_ngram}")
                logger.info(f"🎯 Attention Heads: {engram_cfg.n_head_per_ngram}")
                
            else:
                logger.info("Engram disabled in configuration")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Engram: {e}")
            # Continue without Engram if initialization fails
            self.engram_model = None

    def _initialize_freqtrade(self):
        """Initialize FreqTrade bot and RPC components."""
        try:
            logger.info("Initializing FreqTrade bot...")
            
            # Create FreqTrade bot
            self.freqtrade_bot = FreqtradeBot(self.config)
            
            # Initialize RPC manager
            self.rpc_manager = RPCManager(self.freqtrade_bot, self.config)
            
            # Initialize Engram Telegram bot if enabled
            telegram_config = self.config.get('telegram', {})
            if telegram_config.get('enabled', False):
                logger.info("Initializing Engram-enhanced Telegram bot...")
                self.engram_bot = EngramTelegramBot(self.rpc_manager.rpc, self.config)
                
                # Setup handlers with the Telegram application
                if hasattr(self.rpc_manager, 'telegram') and self.rpc_manager.telegram:
                    self.engram_bot.setup_handlers(self.rpc_manager.telegram._app)
                    logger.info("✅ Engram Telegram bot handlers registered")
            
            logger.info("✅ FreqTrade bot initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize FreqTrade: {e}")
            sys.exit(1)

    def start(self):
        """Start the integrated trading system."""
        try:
            logger.info("🚀 Starting Engram-FreqTrader...")
            
            # Start FreqTrade bot
            self.freqtrade_bot.startup()
            
            # Start RPC manager (includes Telegram bot)
            self.rpc_manager.start()
            
            logger.info("✅ Trading system started successfully")
            logger.info("🤖 Engram AI integration active")
            logger.info("📱 Telegram bot ready for commands")
            logger.info("📊 Monitoring markets...")
            
            # Keep the main thread alive
            try:
                while True:
                    import time
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                logger.info("🛑 Shutdown signal received")
                self._shutdown()
                
        except Exception as e:
            logger.error(f"❌ Error during startup: {e}")
            self._shutdown()
            sys.exit(1)

    def _shutdown(self):
        """Gracefully shutdown the trading system."""
        try:
            logger.info("🔄 Shutting down trading system...")
            
            if self.rpc_manager:
                self.rpc_manager.shutdown()
            
            if self.freqtrade_bot:
                self.freqtrade_bot.cleanup()
            
            logger.info("✅ Shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def get_status(self):
        """Get current system status."""
        status = {
            'freqtrade_bot': self.freqtrade_bot is not None,
            'engram_model': self.engram_model is not None,
            'telegram_bot': self.engram_bot is not None,
            'rpc_manager': self.rpc_manager is not None,
        }
        
        # Add trading statistics if available
        if self.freqtrade_bot:
            try:
                open_trades = Trade.get_open_trades()
                status.update({
                    'open_trades': len(open_trades),
                    'bot_state': str(self.freqtrade_bot.state),
                })
            except Exception:
                pass
        
        return status


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Engram-FreqTrade Integration Launcher"
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (default: engram_freqtrade_config.json)',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (simulation)',
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status and exit',
    )
    
    args = parser.parse_args()
    
    # Create and initialize the trader
    try:
        trader = EngramFreqTrader(args.config)
        
        # Override dry-run setting if specified
        if args.dry_run:
            trader.config['dry_run'] = True
            logger.info("🔬 Running in dry-run mode")
        
        if args.status:
            # Show status and exit
            status = trader.get_status()
            print("📊 System Status:")
            for key, value in status.items():
                print(f"  {key}: {'✅' if value else '❌'} {value}")
        else:
            # Start the trading system
            trader.start()
            
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()