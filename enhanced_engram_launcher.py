#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Engram Bot Launcher
Production-ready launcher with timeout handling, environment variables, and AI fallback
"""

import sys
import os
import json
import logging
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AIBackend:
    """AI Backend with fallback chain: LMStudio → Mock → Rule-based"""
    
    def __init__(self, lmstudio_url: str = None, timeout: int = 10):
        self.lmstudio_url = lmstudio_url or os.getenv('LMSTUDIO_URL', 'http://100.118.172.23:1234')
        self.timeout = timeout
        self.lmstudio_available = False
        self.test_connection()
        
    def test_connection(self):
        """Test LMStudio connection with short timeout"""
        try:
            # Use tuple timeout: (connect_timeout, read_timeout)
            response = requests.get(
                f"{self.lmstudio_url}/v1/models",
                timeout=(5, 10)  # 5s connect, 10s read
            )
            self.lmstudio_available = response.status_code == 200
            if self.lmstudio_available:
                logger.info("✅ LMStudio connected")
            else:
                logger.warning(f"⚠️ LMStudio returned status {response.status_code}")
        except requests.exceptions.Timeout:
            logger.warning("⚠️ LMStudio connection timeout - using fallback AI")
            self.lmstudio_available = False
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️ LMStudio not reachable - using fallback AI")
            self.lmstudio_available = False
        except Exception as e:
            logger.warning(f"⚠️ LMStudio error: {e} - using fallback AI")
            self.lmstudio_available = False
            
    def query_lmstudio(self, prompt: str) -> Optional[str]:
        """Query LMStudio with timeout protection"""
        if not self.lmstudio_available:
            return None
            
        try:
            # Use tuple timeout: (connect_timeout, read_timeout)
            # Connect fast (5s), but allow long generation time (self.timeout)
            response = requests.post(
                f"{self.lmstudio_url}/v1/chat/completions",
                json={
                    "model": "local-model",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=(5, self.timeout)  # 5s connect, self.timeout for read
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats (especially glm-4.7-flash)
                choice = (result.get("choices") or [{}])[0]
                msg = choice.get("message") or {}
                
                # Try content first, then reasoning_content (for glm-4.7-flash)
                text = (msg.get("content") or "").strip()
                if not text:
                    text = (msg.get("reasoning_content") or "").strip()
                
                if text:
                    logger.info(f"✅ LMStudio response received ({len(text)} chars)")
                    return text
                else:
                    logger.warning("⚠️ LMStudio returned empty response")
                    return None
            else:
                logger.warning(f"LMStudio returned status {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.warning(f"⚠️ LMStudio query timeout after {self.timeout}s - using fallback for this request")
            # DO NOT permanently disable - just fall back for this request
            # self.lmstudio_available = False
            return None
        except Exception as e:
            logger.warning(f"LMStudio query error: {e}")
            return None
            
    def mock_ai_response(self, prompt: str) -> str:
        """Mock AI response for testing"""
        prompt_lower = prompt.lower()
        
        if 'analyze' in prompt_lower or 'btc' in prompt_lower or 'market' in prompt_lower:
            return (
                "📊 Market Analysis (Mock AI):\n\n"
                "Based on current market conditions:\n"
                "• Trend: Neutral to Bullish\n"
                "• Signal: HOLD with cautious optimism\n"
                "• Key Levels: Support at $40k, Resistance at $45k\n\n"
                "⚠️ Note: This is a mock response. LMStudio is not available."
            )
        elif 'status' in prompt_lower:
            return (
                "🤖 Bot Status (Mock AI):\n\n"
                "All systems operational. Using fallback AI mode.\n"
                "LMStudio: Offline\n"
                "Telegram: Connected\n"
                "Engram Model: Ready"
            )
        else:
            return (
                f"🤖 Mock AI Response:\n\n"
                f"I received your message: '{prompt[:100]}...'\n\n"
                f"I'm currently running in fallback mode because LMStudio is not available.\n"
                f"For production use, please ensure LMStudio is running and accessible."
            )
            
    def rule_based_analysis(self, symbol: str = "BTC/USDT") -> str:
        """Rule-based market analysis"""
        return (
            f"📈 Rule-Based Analysis for {symbol}:\n\n"
            f"• Recommendation: HOLD\n"
            f"• Confidence: Medium\n"
            f"• Reasoning: Using rule-based analysis due to AI unavailability\n\n"
            f"Key Indicators:\n"
            f"• RSI: Neutral zone (45-55)\n"
            f"• MACD: Consolidation pattern\n"
            f"• Volume: Average\n\n"
            f"⚠️ Note: This is a rule-based fallback. For AI-powered analysis, ensure LMStudio is running."
        )
        
    def query(self, prompt: str) -> str:
        """Query with fallback chain: LMStudio → Mock → Rule-based"""
        # Try LMStudio first
        if self.lmstudio_available:
            result = self.query_lmstudio(prompt)
            if result:
                return result
                
        # Fallback to mock AI
        logger.info("Using fallback AI (mock mode)")
        return self.mock_ai_response(prompt)


class EnhancedEngramBot:
    """Enhanced Engram bot with robust error handling and fallback mechanisms"""
    
    def __init__(self):
        self.config = None
        self.token = None
        self.chat_id = None
        self.base_url = None
        self.engram_model = None
        self.ai_backend = None
        self.running = False
        self.last_update_id = 0
        
    def load_config(self) -> bool:
        """Load configuration from file or environment variables"""
        # Try environment variables first
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if self.token and self.chat_id:
            logger.info("✅ Loaded credentials from environment variables")
            return True
            
        # Fallback to config file
        config_path = Path(__file__).parent / "config" / "telegram" / "working_telegram_config.json"
        if not config_path.exists():
            logger.error(f"❌ Config file not found: {config_path}")
            logger.info("💡 Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
            return False
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
            telegram_config = self.config.get('telegram', {})
            self.token = telegram_config.get('bot_token')
            self.chat_id = str(telegram_config.get('chat_id'))
            
            if not self.token or not self.chat_id:
                logger.error("❌ Missing Telegram credentials in config")
                return False
                
            logger.info("✅ Loaded credentials from config file")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return False
            
    def initialize(self) -> bool:
        """Initialize all components"""
        logger.info("="*80)
        logger.info("🚀 ENHANCED ENGRAM BOT LAUNCHER")
        logger.info("="*80)
        logger.info("Initializing Enhanced Engram Bot...")
        
        # Load configuration
        if not self.load_config():
            return False
            
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        # Initialize AI backend with timeout protection
        lmstudio_url = os.getenv('LMSTUDIO_URL', 'http://100.118.172.23:1234')
        lmstudio_timeout = int(os.getenv('LMSTUDIO_TIMEOUT', '180'))  # 3 minutes default (was 10s)
        self.ai_backend = AIBackend(lmstudio_url, lmstudio_timeout)
        
        # Load Engram model (optional)
        logger.info("Loading Engram neural model...")
        try:
            # Add src directory to Python path if not already there
            import sys
            from pathlib import Path
            
            # Try multiple path resolution strategies
            script_dir = Path(__file__).parent.resolve()
            possible_src_paths = [
                script_dir / "src",  # src relative to script
                Path.cwd() / "src",  # src relative to current working directory
                Path("src").resolve()  # src as absolute path from cwd
            ]
            
            src_path = None
            for path in possible_src_paths:
                if path.exists() and (path / "core" / "engram_demo_v1.py").exists():
                    src_path = path
                    break
            
            if src_path is None:
                raise ImportError("Could not locate src/core/engram_demo_v1.py")
            
            # Add to sys.path if not already there
            src_path_str = str(src_path)
            if src_path_str not in sys.path:
                sys.path.insert(0, src_path_str)
                logger.debug(f"Added to sys.path: {src_path_str}")
            
            from core.engram_demo_v1 import EngramModel
            logger.debug("EngramModel class imported successfully")
            self.engram_model = EngramModel()
            logger.info("✅ Engram model loaded")
        except Exception as e:
            logger.warning(f"⚠️ Engram model not available: {e}")
            if logger.isEnabledFor(logging.DEBUG):
                import traceback
                logger.debug(f"Import error details: {type(e).__name__}: {str(e)}")
                logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            self.engram_model = None
            
        # Test Telegram connection
        logger.info("Testing Telegram connection...")
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"✅ Telegram bot connected: {bot_info['result']['username']}")
            else:
                logger.error(f"❌ Telegram API error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to Telegram: {e}")
            return False
            
        logger.info("✅ All systems initialized successfully")
        return True
        
    def send_message(self, text: str) -> Optional[Dict[str, Any]]:
        """Send message via Telegram"""
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={'chat_id': self.chat_id, 'text': text},
                timeout=10
            )
            logger.info(f"📤 Sent: {text[:50]}...")
            return response.json()
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            return None
            
    def get_updates(self, offset: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get updates from Telegram"""
        try:
            params = {'timeout': 30}
            if offset:
                params['offset'] = offset
            response = requests.get(
                f"{self.base_url}/getUpdates",
                params=params,
                timeout=35
            )
            return response.json()
        except Exception as e:
            logger.error(f"❌ Failed to get updates: {e}")
            return None
            
    def process_message(self, message: Dict[str, Any]):
        """Process incoming message"""
        try:
            text = message.get('text', '')
            chat_id = message['chat']['id']
            
            logger.info(f"📨 Processing: {text[:50]}...")
            
            # Handle commands
            if text.startswith('/start'):
                response = (
                    "🤖 Welcome to Enhanced Engram Trading Bot!\n\n"
                    "Available commands:\n"
                    "/start - Show this message\n"
                    "/status - Check bot status\n"
                    "/analyze <symbol> - Analyze market\n"
                    "/help - Show help\n\n"
                    "💡 Tip: Just send me a message and I'll respond using AI!"
                )
            elif text.startswith('/status'):
                lmstudio_status = "✅ Connected" if self.ai_backend.lmstudio_available else "⚠️ Offline (using fallback)"
                engram_status = "✅ Loaded" if self.engram_model else "⚠️ Not Available"
                
                response = (
                    f"🤖 Bot Status:\n\n"
                    f"• Status: Running\n"
                    f"• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"• Engram Model: {engram_status}\n"
                    f"• LMStudio: {lmstudio_status}\n"
                    f"• Telegram: ✅ Connected\n"
                    f"• AI Mode: {'LMStudio' if self.ai_backend.lmstudio_available else 'Fallback (Mock)'}"
                )
            elif text.startswith('/analyze'):
                parts = text.split()
                symbol = parts[1] if len(parts) > 1 else "BTC/USDT"
                
                if self.ai_backend.lmstudio_available:
                    prompt = f"Analyze the market for {symbol}. Provide a brief trading signal (BUY/SELL/HOLD) with reasoning."
                    analysis = self.ai_backend.query(prompt)
                else:
                    analysis = self.ai_backend.rule_based_analysis(symbol)
                    
                response = f"📊 Analysis for {symbol}:\n\n{analysis}"
            elif text.startswith('/help'):
                response = (
                    "📚 Engram Trading Bot Help\n\n"
                    "This bot combines neural network analysis with AI-powered market insights.\n\n"
                    "Commands:\n"
                    "/start - Welcome message\n"
                    "/status - Bot status\n"
                    "/analyze <symbol> - Market analysis\n"
                    "/help - This help message\n\n"
                    "Configuration:\n"
                    "• Set TELEGRAM_BOT_TOKEN env var for bot token\n"
                    "• Set TELEGRAM_CHAT_ID env var for chat ID\n"
                    "• Set LMSTUDIO_URL env var for LMStudio URL\n"
                    "• Set LMSTUDIO_TIMEOUT env var for timeout (default: 180s)"
                )
            else:
                # Use AI backend for general queries
                response = self.ai_backend.query(text)
                
            # Send response
            self.send_message(response)
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            self.send_message(f"❌ Sorry, I encountered an error: {str(e)}")
            
    def run(self):
        """Main bot loop"""
        if not self.initialize():
            logger.error("❌ Initialization failed")
            return
            
        self.running = True
        logger.info("🤖 Bot is running and listening for messages...")
        logger.info("📱 Send a message to your Telegram bot to test it!")
        
        # Send startup notification
        startup_msg = (
            "🤖 Enhanced Engram Bot is now online!\n\n"
            f"• LMStudio: {'✅ Connected' if self.ai_backend.lmstudio_available else '⚠️ Offline (using fallback)'}\n"
            f"• Engram Model: {'✅ Loaded' if self.engram_model else '⚠️ Not Available'}\n"
            f"• AI Mode: {'LMStudio' if self.ai_backend.lmstudio_available else 'Fallback (Mock)'}\n\n"
            "Send /help for available commands!"
        )
        self.send_message(startup_msg)
        
        # Main loop
        while self.running:
            try:
                updates = self.get_updates(offset=self.last_update_id + 1)
                
                if updates and updates.get('ok'):
                    for update in updates.get('result', []):
                        self.last_update_id = update['update_id']
                        
                        if 'message' in update:
                            self.process_message(update['message'])
                            
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down...")
                self.running = False
                self.send_message("👋 Enhanced Engram Bot is shutting down. Goodbye!")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(5)


def main():
    """Main entry point"""
    bot = EnhancedEngramBot()
    bot.run()


if __name__ == "__main__":
    main()
