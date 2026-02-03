"""
Engram-ClawdBot Integration
Main entry point for running Engram as a ClawdBot agent
"""

import asyncio
import logging
import os
import sys
import json
from pathlib import Path

# Fix Windows console encoding for Unicode support
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
    except Exception:
        # Fallback if encoding fix fails
        pass

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.engram_agent import EngramAgent


def load_config() -> dict:
    """
    Load configuration from file and environment variables
    
    Returns:
        Configuration dictionary
    """
    # Try to load from config file
    config_path = Path(__file__).parent / "config" / "engram_config.json"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            file_config = json.load(f)
    else:
        file_config = {}
    
    # Override with environment variables
    config = {
        # LMStudio settings
        "lmstudio_host": os.getenv("LMSTUDIO_HOST", file_config.get("lmstudio", {}).get("host", "100.118.172.23")),
        "lmstudio_port": int(os.getenv("LMSTUDIO_PORT", file_config.get("lmstudio", {}).get("port", 1234))),
        "model": os.getenv("ENGRAM_MODEL", file_config.get("lmstudio", {}).get("model", "glm-4.7-flash")),
        
        # ClawdBot gateway settings
        "clawdbot_host": os.getenv("CLAWDBOT_HOST", file_config.get("clawdbot", {}).get("host", "localhost")),
        "clawdbot_port": int(os.getenv("CLAWDBOT_PORT", file_config.get("clawdbot", {}).get("port", 18789))),
        "clawdbot_token": os.getenv("CLAWDBOT_TOKEN", file_config.get("clawdbot", {}).get("token", "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc")),
        
        # Agent settings
        "response_format": os.getenv("ENGRAM_RESPONSE_FORMAT", file_config.get("agent", {}).get("response_format", "clean"))
    }
    
    return config


def setup_logging(level: str = "INFO"):
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "engram.log")
        ]
    )


async def main():
    """
    Main entry point
    """
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Engram-ClawdBot Integration Starting")
    logger.info("=" * 60)
    
    # Load configuration
    config = load_config()
    
    logger.info("Configuration:")
    logger.info(f"  LMStudio: {config['lmstudio_host']}:{config['lmstudio_port']}")
    logger.info(f"  Model: {config['model']}")
    logger.info(f"  ClawdBot Gateway: {config['clawdbot_host']}:{config['clawdbot_port']}")
    logger.info(f"  Response Format: {config['response_format']}")
    
    # Create and run agent
    agent = EngramAgent(config)
    
    try:
        logger.info("Starting Engram agent...")
        await agent.run()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        logger.info("Shutting down...")
        await agent.shutdown()
        logger.info("Shutdown complete")


def print_usage():
    """Print usage information"""
    print("""
Engram-ClawdBot Integration
===========================

Usage:
    python engram_clawdbot_integration.py

Environment Variables:
    LMSTUDIO_HOST          LMStudio server host (default: localhost)
    LMSTUDIO_PORT          LMStudio server port (default: 1234)
    ENGRAM_MODEL           Model to use (default: glm-4.7-flash)
    CLAWDBOT_HOST          ClawdBot gateway host (default: localhost)
    CLAWDBOT_PORT          ClawdBot gateway port (default: 18789)
    CLAWDBOT_TOKEN         Authentication token for ClawdBot
    ENGRAM_RESPONSE_FORMAT Response format: clean/detailed/raw (default: clean)
    LOG_LEVEL              Logging level: DEBUG/INFO/WARNING/ERROR (default: INFO)

Example:
    export LMSTUDIO_HOST=localhost
    export LMSTUDIO_PORT=1234
    export CLAWDBOT_HOST=localhost
    export CLAWDBOT_PORT=18789
    export ENGRAM_RESPONSE_FORMAT=clean
    
    python engram_clawdbot_integration.py

Features:
    [OK] WebSocket connection to ClawdBot gateway (fixes 1008 error)
    [OK] Event message handler (prevents 1008 disconnects)
    [OK] Proper clawdbot-v1 subprotocol support
    [OK] Automatic reconnection with exponential backoff
    [OK] Trading analysis tools (market analysis, signals, risk assessment)
    [OK] LMStudio integration with function calling
    [OK] Clean response formatting (filters reasoning content)
    [OK] Health monitoring and status reporting
    [OK] Bot commands (/help, /status, /analyze, /alert, /alerts, /portfolio)
    [OK] Price alert tracking
    [OK] Portfolio management

For more information, see docs/SETUP_GUIDE.md
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print_usage()
        sys.exit(0)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
