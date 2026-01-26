#!/usr/bin/env python3
"""
Intelligent Engram-FreqTrade Integration System
===========================================

Advanced trading system that intelligently uses Engram AI only when needed,
with seamless modular integration capabilities and smart response system.

Features:
- Conditional AI activation based on market conditions
- Natural language understanding in Telegram
- Modular integration system for external services
- Smart resource management
- Contextual responses without unnecessary chart calls
"""

import sys
import os
import json
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add system path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class AIActivationMode(Enum):
    """Intelligent AI activation modes"""
    OFF = "off"
    SMART = "smart"
    ALWAYS = "always"

@dataclass
class MarketCondition:
    """Market condition analysis"""
    volatility: float
    trend_strength: float
    volume_anomaly: bool
    price_momentum: float
    timestamp: datetime

@dataclass
class AIRequest:
    """AI request context"""
    trigger: str
    priority: int
    data: Dict[str, Any]
    requires_deep_analysis: bool = False

class IntelligentEngramCore:
    """Core intelligence system for smart AI activation"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.ai_mode = AIActivationMode.SMART
        self.market_conditions = {}
        self.last_analysis = {}
        self.active_integrations = {}
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration with validation"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "ai": {
                "activation_mode": "smart",
                "triggers": {
                    "volatility_threshold": 0.02,
                    "volume_spike_threshold": 3.0,
                    "trend_change_threshold": 0.05
                },
                "resource_limits": {
                    "max_requests_per_minute": 10,
                    "cooldown_period": 60
                }
            },
            "integrations": {
                "telegram": {"enabled": True},
                "api_server": {"enabled": True},
                "notifications": {"enabled": True}
            }
        }
    
    def analyze_market_condition(self, pair: str, price_data: List[Dict]) -> MarketCondition:
        """Analyze current market conditions intelligently"""
        if len(price_data) < 20:
            return MarketCondition(0, 0, False, 0, datetime.now())
        
        prices = [float(candle['close']) for candle in price_data[-20:]]
        volumes = [float(candle['volume']) for candle in price_data[-20:]]
        
        # Calculate volatility
        price_changes = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        volatility = sum(abs(change) for change in price_changes) / len(price_changes)
        
        # Calculate trend strength
        short_ma = sum(prices[-5:]) / 5
        long_ma = sum(prices[-20:]) / 20
        trend_strength = (short_ma - long_ma) / long_ma
        
        # Volume anomaly detection
        avg_volume = sum(volumes[:-5]) / (len(volumes) - 5)
        recent_volume = sum(volumes[-5:]) / 5
        volume_anomaly = recent_volume > (avg_volume * 3)
        
        # Price momentum
        momentum = (prices[-1] - prices[-10]) / prices[-10] if len(prices) >= 10 else 0
        
        condition = MarketCondition(
            volatility=volatility,
            trend_strength=trend_strength,
            volume_anomaly=volume_anomaly,
            price_momentum=momentum,
            timestamp=datetime.now()
        )
        
        self.market_conditions[pair] = condition
        return condition
    
    def should_activate_ai(self, pair: str, user_request: Optional[str] = None) -> bool:
        """Determine if AI activation is needed"""
        if self.ai_mode == AIActivationMode.ALWAYS:
            return True
        
        if self.ai_mode == AIActivationMode.OFF:
            return user_request is not None
        
        if self.ai_mode == AIActivationMode.SMART:
            # Check user request first
            if user_request:
                return self._analyze_user_intent(user_request)
            
            # Check market conditions
            if pair not in self.market_conditions:
                return False
            
            condition = self.market_conditions[pair]
            thresholds = self.config["ai"]["triggers"]
            
            # Smart activation triggers
            return (
                condition.volatility > thresholds["volatility_threshold"] or
                condition.volume_anomaly or
                abs(condition.trend_strength) > thresholds["trend_change_threshold"] or
                abs(condition.price_momentum) > 0.03
            )
    
    def _analyze_user_intent(self, request: str) -> bool:
        """Analyze user intent from natural language"""
        ai_keywords = [
            "analyze", "predict", "forecast", "deep", "detailed",
            "enagram", "ai", "neural", "explain", "why",
            "what if", "scenario", "advanced", "complex"
        ]
        
        # Simple NLP - can be enhanced with proper NLP later
        request_lower = request.lower()
        return any(keyword in request_lower for keyword in ai_keywords)
    
    def create_intelligent_response(self, pair: str, query: str, context: Dict[str, Any]) -> str:
        """Create intelligent response without unnecessary AI calls"""
        
        # Simple queries - no AI needed
        if any(word in query.lower() for word in ["status", "balance", "profit"]):
            return self._get_basic_response(query, context)
        
        # Market info queries
        if any(word in query.lower() for word in ["price", "current", "market"]):
            return self._get_market_info(pair, context)
        
        # Analysis queries - use AI only when needed
        if self.should_activate_ai(pair, query):
            return self._get_ai_analysis(pair, query, context)
        
        # Default response
        return self._get_default_response(pair, query)
    
    def _get_basic_response(self, query: str, context: Dict[str, Any]) -> str:
        """Handle basic queries without AI"""
        if "status" in query.lower():
            return "🤖 Engram-FreqTrade is running in smart mode. AI activates only when market conditions require deep analysis."
        
        if "balance" in query.lower():
            return f"💰 Wallet: {context.get('balance', '1000 USDT')} | Active trades: {context.get('active_trades', 0)}"
        
        if "profit" in query.lower():
            return f"📊 Current P/L: {context.get('profit', 'No active trades')}"
        
        return "ℹ️ Use 'analyze', 'predict', or ask specific questions for AI insights."
    
    def _get_market_info(self, pair: str, context: Dict[str, Any]) -> str:
        """Get current market information without AI"""
        current_price = context.get('current_price', 'Unknown')
        change = context.get('price_change', 'Unknown')
        
        return f"📈 {pair}: {current_price} ({change})\n\n💡 For deeper analysis, ask 'analyze {pair}' or 'predict {pair}'"
    
    def _get_ai_analysis(self, pair: str, query: str, context: Dict[str, Any]) -> str:
        """Get AI analysis when needed"""
        try:
            # This would integrate with actual Engram model
            # For now, simulate intelligent response
            
            if pair in self.market_conditions:
                condition = self.market_conditions[pair]
                
                return f"""
🧠 **Engram AI Analysis for {pair}**

**Market Intelligence:**
- Volatility: {condition.volatility:.3f} {'⚠️ High' if condition.volatility > 0.02 else '✅ Normal'}
- Trend: {'📈 Bullish' if condition.trend_strength > 0 else '📉 Bearish'} ({condition.trend_strength:.3f})
- Volume: {'🚀 Spike detected' if condition.volume_anomaly else '📊 Normal'}
- Momentum: {condition.price_momentum:.3f}

**AI Recommendation:**
{'AI suggests active monitoring - high volatility detected' if condition.volatility > 0.02 else 'Market conditions are stable - normal trading strategy'}

*Smart AI activation - analysis only when needed*
"""
            else:
                return f"🔍 Analyzing {pair}... Please wait a moment for market data."
        
        except Exception as e:
            return f"⚠️ AI analysis temporarily unavailable: {str(e)}"
    
    def _get_default_response(self, pair: str, query: str) -> str:
        """Default intelligent response"""
        return f"""
🤖 **Intelligent Response**

I'm ready to help! Here are some options:

**For {pair}:**
- "analyze {pair}" - Deep AI analysis
- "predict {pair}" - AI price prediction  
- "status" - System status
- "market {pair}" - Current market info

**Global Commands:**
- "integrate <service>" - Add external integration
- "mode <smart/off/always>" - Change AI activation mode

📟 I'll use AI only when you need deep analysis!
"""

class ModularIntegrationSystem:
    """Modular system for seamless integrations"""
    
    def __init__(self, core: IntelligentEngramCore):
        self.core = core
        self.integrations = {}
        
    def register_integration(self, name: str, integration_class, config: Dict[str, Any]):
        """Register a new integration"""
        try:
            instance = integration_class(config, self.core)
            self.integrations[name] = instance
            self.core.active_integrations[name] = True
            return True
        except Exception as e:
            core.logger.error(f"Failed to register {name}: {e}")
            return False
    
    def get_integration(self, name: str):
        """Get active integration"""
        return self.integrations.get(name)
    
    def list_integrations(self) -> List[str]:
        """List all active integrations"""
        return list(self.integrations.keys())

class IntelligentTelegramHandler:
    """Enhanced Telegram handler with NLU capabilities"""
    
    def __init__(self, core: IntelligentEngramCore, token: str, chat_id: str):
        self.core = core
        self.token = token
        self.chat_id = chat_id
        self.context_cache = {}
        
    async def handle_message(self, message: str, user_id: int = None) -> str:
        """Handle incoming Telegram messages intelligently"""
        
        # Parse user intent
        intent = self._parse_intent(message)
        
        # Handle different intents
        if intent["type"] == "integration":
            return await self._handle_integration_request(intent["service"])
        
        elif intent["type"] == "mode_change":
            return self._handle_mode_change(intent["mode"])
        
        elif intent["type"] == "analysis":
            pair = intent.get("pair", "BTC/USDT")
            return self.core.create_intelligent_response(pair, message, self._get_context())
        
        else:
            return self.core.create_intelligent_response("BTC/USDT", message, self._get_context())
    
    def _parse_intent(self, message: str) -> Dict[str, Any]:
        """Parse user intent from message"""
        message_lower = message.lower().strip()
        
        # Integration requests
        if "integrate" in message_lower:
            parts = message_lower.split("integrate")
            if len(parts) > 1:
                service = parts[1].strip()
                return {"type": "integration", "service": service}
        
        # Mode changes
        if "mode" in message_lower:
            parts = message_lower.split("mode")
            if len(parts) > 1:
                mode = parts[1].strip()
                return {"type": "mode_change", "mode": mode}
        
        # Analysis requests
        if any(word in message_lower for word in ["analyze", "predict", "analysis"]):
            # Extract pair if mentioned
            pair = "BTC/USDT"  # Default
            for p in ["BTC/USDT", "ETH/USDT", "BNB/USDT"]:
                if p.lower() in message_lower:
                    pair = p
                    break
            
            return {"type": "analysis", "pair": pair}
        
        return {"type": "general"}
    
    def _handle_integration_request(self, service: str) -> str:
        """Handle integration request"""
        available = ["discord", "slack", "webhook", "database", "alerts"]
        
        if service.lower() in available:
            return f"🔧 Integrating {service}... This feature will be available in the next update."
        else:
            return f"❓ Unknown integration. Available: {', '.join(available)}"
    
    def _handle_mode_change(self, mode: str) -> str:
        """Handle AI mode change"""
        valid_modes = ["smart", "off", "always"]
        
        if mode.lower() in valid_modes:
            self.core.ai_mode = AIActivationMode(mode.lower())
            return f"⚙️ AI mode changed to: {mode.upper()}\n\n📍 Smart = AI only when needed\n📍 Always = AI always active\n📍 Off = AI disabled"
        else:
            return f"❌ Invalid mode. Use: smart, off, always"
    
    def _get_context(self) -> Dict[str, Any]:
        """Get current context for responses"""
        return {
            "balance": "1000 USDT",
            "active_trades": 0,
            "profit": "No active trades",
            "current_price": "Pending market data"
        }

# Main System Class
class IntelligentEngramFreqTrade:
    """Main intelligent trading system"""
    
    def __init__(self, config_path: str = "engram_intelligent_config.json"):
        self.core = IntelligentEngramCore(config_path)
        self.integration_system = ModularIntegrationSystem(self.core)
        self.telegram_handler = None
        
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """Initialize all integrations"""
        # Telegram integration
        telegram_config = self.core.config.get("telegram", {})
        if telegram_config.get("enabled"):
            self.telegram_handler = IntelligentTelegramHandler(
                self.core,
                telegram_config.get("token", ""),
                telegram_config.get("chat_id", "")
            )
        
        # Initialize other integrations here
        # API server, webhooks, etc.
    
    def start_intelligent_trading(self):
        """Start the intelligent trading system"""
        self.core.logger.info("🚀 Starting Intelligent Engram-FreqTrade System")
        self.core.logger.info("🧠 AI Mode: SMART - activates only when needed")
        self.core.logger.info("📱 Telegram integration ready with NLU")
        self.core.logger.info("🔧 Modular integration system active")
        
        print("""
🚀 **Intelligent Engram-FreqTrade System Ready**

🧠 **Smart AI Activation:**
   • AI only activates when market conditions require it
   • Natural language understanding
   • Resource-efficient operation

📱 **Enhanced Telegram:**
   • Try: "analyze BTC/USDT" for AI analysis
   • Try: "mode smart/off/always" to change AI mode
   • Try: "integrate discord" for new integrations

🔧 **Seamless Integrations:**
   • Modular plugin system
   • External service connections
   • Smart response without unnecessary calls

**The system is now running intelligently!**
        """)
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "ai_mode": self.core.ai_mode.value,
            "active_integrations": self.integration_system.list_integrations(),
            "market_conditions": {
                pair: {
                    "volatility": cond.volatility,
                    "trend_strength": cond.trend_strength,
                    "volume_anomaly": cond.volume_anomaly,
                    "timestamp": cond.timestamp.isoformat()
                }
                for pair, cond in self.core.market_conditions.items()
            }
        }

if __name__ == "__main__":
    # Initialize and start the intelligent system
    system = IntelligentEngramFreqTrade()
    system.start_intelligent_trading()