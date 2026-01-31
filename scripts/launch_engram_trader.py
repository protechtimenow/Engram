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

# Add parent directory to Python path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

print("DEBUG sys.path:", sys.path)
print("DEBUG current dir:", os.getcwd())
print("DEBUG script dir:", script_dir)
print("DEBUG parent dir:", parent_dir)

try:
    # Add freqtrade directory for development install
    freqtrade_path = os.path.join(parent_dir, 'freqtrade')
    if os.path.exists(freqtrade_path):
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
