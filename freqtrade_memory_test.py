#!/usr/bin/env python3
"""
FreqTrade + Engram Memory Usage Test
====================================

This script measures memory usage when running FreqTrade with Engram integration 
in a dry-run environment. It simulates some trades or calls strategy indicators 
to load the model and see how much RAM is used.

Usage:
    python freqtrade_memory_test.py

Pre-requisites:
- freqtrade installed (pip install freqtrade)
- Engram model files accessible
- config/engram_freqtrade_config.json properly set up with "enabled": true
- psutil installed (pip install psutil)

Steps:
1. Load FreqTrade config for dry-run.
2. Initialize the FreqTradeBot with EngramStrategy.
3. Run a short simulation or forced indicator calls.
4. Measure memory usage before/after using psutil.
"""

import sys
import os
import time
import logging
import psutil

# Attempt to import freqtrade, Engram, etc.
try:
    from freqtrade.configuration.configuration import Configuration
    from freqtrade.freqtradebot import FreqtradeBot
    from freqtrade.rpc.rpc_manager import RPCManager
    from freqtrade.persistence import Trade
    from freqtrade.data.dataprovider import DataProvider
except ImportError as e:
    print(f"❌ Freqtrade import error: {e}")
    print("Please ensure freqtrade is installed (pip install freqtrade)")
    sys.exit(1)

# For Engram
try:
    # Make sure 'src' directory is accessible if needed
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    sys.path.insert(0, parent_dir)
    
    from src.trading.engram_trading_strategy import EngramStrategy
    # If other Engram imports needed, do them here
except ImportError as e:
    print(f"❌ Engram import error: {e}")
    print("Please ensure Engram code is placed in 'src/trading' or Python path is correct.")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_freqtrade_dry_run(config_path: str):
    """
    Initialize Freqtrade in dry-run mode to load the Engram strategy,
    measure memory usage before & after initialization,
    and optionally place a few test trades if possible.
    """
    process = psutil.Process()
    mem_before = process.memory_info().rss / 1024 / 1024  # MB
    
    logger.info(f"Memory usage before Freqtrade init: {mem_before:.2f} MB")
    
    # 1. Load config
    try:
        logger.info(f"Loading configuration from: {config_path}")
        freqtrade_config = Configuration.from_files([config_path])
        
        # Force dry-run
        freqtrade_config['dry_run'] = True
        
        # 2. Create freqtrade bot
        freqtrade_bot = FreqtradeBot(freqtrade_config)
        
        # 3. Initialize RPC manager
        rpc_manager = RPCManager(freqtrade_bot, freqtrade_config)
        
        # 4. Startup the bot (won't really trade, just init)
        freqtrade_bot.startup()
        
        mem_after_init = process.memory_info().rss / 1024 / 1024  # MB
        logger.info(f"Memory usage after Freqtrade init: {mem_after_init:.2f} MB")

        # 5. Simulate a short wait
        logger.info("Simulating short runtime for 5 seconds...")
        time.sleep(5)
        
        mem_during = process.memory_info().rss / 1024 / 1024
        logger.info(f"Memory usage after 5s: {mem_during:.2f} MB")

        # Attempt to shutdown gracefully
        rpc_manager.shutdown()
        freqtrade_bot.cleanup()
        
        mem_after_shutdown = process.memory_info().rss / 1024 / 1024  # MB
        logger.info(f"Memory usage after shutdown: {mem_after_shutdown:.2f} MB")
        
        logger.info("✅ Freqtrade + Engram memory test completed.")
    except Exception as e:
        logger.error(f"❌ Error during freqtrade memory test: {e}")

def main():
    """Main test entry."""
    logger.info("=== FreqTrade + Engram Memory Usage Test ===")
    config_path = "config/engram_freqtrade_config.json"
    
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)
    
    run_freqtrade_dry_run(config_path)

if __name__ == "__main__":
    main()
