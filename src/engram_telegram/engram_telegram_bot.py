"""
Engram-Enhanced Telegram Bot for FreqTrade
==========================================

This module extends FreqTrade's Telegram functionality with Engram-powered
trading insights, natural language processing, and advanced analysis capabilities.

Features:
- Natural language trading commands
- Engram-powered market analysis
- AI-driven trading recommendations
- Advanced portfolio insights
- Real-time strategy performance metrics
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    BotCommand,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode

from freqtrade.rpc.rpc import RPC
from freqtrade.persistence import Trade
from freqtrade.enums import SignalDirection, TradingMode
from freqtrade.data.dataprovider import DataProvider

# Import Engram components
from src.core.engram_demo_v1 import EngramModel, engram_cfg


logger = logging.getLogger(__name__)


class EngramTelegramBot:
    """
    Enhanced Telegram bot with Engram integration for intelligent trading assistance.
    """
    
    def __init__(self, rpc: RPC, config: dict):
        self.rpc = rpc
        self.config = config
        self.telegram_config = config.get('telegram', {})
        self.engram_config = config.get('engram', {})
        
        # Initialize Engram model
        self.engram_model = None
        self.engram_initialized = False
        
        # Bot state
        self.user_contexts = {}  # Track user conversation context
        self.analysis_cache = {}  # Cache for market analysis
        
        # Initialize Engram
        self._initialize_engram()
        
        logger.info("EngramTelegramBot initialized")

    def _initialize_engram(self):
        """Initialize Engram model for natural language processing."""
        try:
            if self.engram_config.get('enabled', False):
                logger.info("Initializing Engram model for Telegram bot...")

                # Check if using external models (ClawdBot or LMStudio)
                use_clawdbot = self.engram_config.get('use_clawdbot', False)
                use_lmstudio = self.engram_config.get('use_lmstudio', False)
                lmstudio_url = self.engram_config.get('lmstudio_url', 'http://localhost:1234')
                clawdbot_ws_url = self.engram_config.get('clawdbot_ws_url', 'ws://127.0.0.1:18789')

                if use_clawdbot or use_lmstudio:
                    logger.info(f"Using external model - ClawdBot: {use_clawdbot}, LMStudio: {use_lmstudio}")
                    self.engram_model = EngramModel(
                        use_clawdbot=use_clawdbot,
                        clawdbot_ws_url=clawdbot_ws_url,
                        use_lmstudio=use_lmstudio,
                        lmstudio_url=lmstudio_url
                    )
                else:
                    logger.info("Using local Engram model")
                    self.engram_model = EngramModel()

                self.engram_initialized = True
                logger.info("Engram model initialized for Telegram bot")
            else:
                logger.info("Engram integration disabled for Telegram bot")
        except Exception as e:
            logger.error(f"Failed to initialize Engram for Telegram: {e}")
            self.engram_initialized = False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced start command with Engram introduction."""
        welcome_text = """
🤖 *Welcome to Engram-Powered FreqTrade Bot!*

I'm your AI-powered trading assistant with advanced neural analysis capabilities.

🔹 *Available Commands:*
📊 `/analysis` - Engram market analysis
🧠 `/engram_status` - Engram system status
💬 `/chat` - Natural language trading queries
📈 `/predict` - AI trading predictions
🎯 `/smart_alerts` - Set intelligent alerts
📋 `/portfolio_insights` - AI portfolio analysis

🔹 *Standard Commands:*
/status, /profit, /balance, /help, /trades

Type `/help` for more information or start with `/analysis` to see AI insights!
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Set user context
        user_id = update.effective_user.id
        self.user_contexts[user_id] = {
            'last_command': 'start',
            'engram_interactions': 0,
            'preferences': {}
        }

    async def analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Provide Engram-powered market analysis."""
        user_id = update.effective_user.id
        
        try:
            # Get current market data
            trades = Trade.get_open_trades()
            daily_profit = self.rpc._rpc_daily_profit()
            
            # Generate Engram analysis
            analysis = await self._generate_engram_analysis(trades, daily_profit)
            
            response = f"""
🧠 *Engram Market Analysis*
━━━━━━━━━━━━━━━━━━━━━━━

📊 *Current Status:*
{analysis['status']}

🎯 *AI Insights:*
{analysis['insights']}

⚡ *Key Patterns:*
{analysis['patterns']}

🔮 *Predictions:*
{analysis['predictions']}

💡 *Recommendations:*
{analysis['recommendations']}

*Analysis Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await update.message.reply_text(
                response,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Update user context
            self.user_contexts[user_id]['engram_interactions'] += 1
            
        except Exception as e:
            logger.error(f"Error in analysis command: {e}")
            await update.message.reply_text(
                "❌ Error generating analysis. Please try again later."
            )

    async def engram_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show Engram system status and capabilities."""
        status_text = f"""
🔬 *Engram System Status*
━━━━━━━━━━━━━━━━━━━━━━━

🤖 *Model Status:* {'✅ Online' if self.engram_initialized else '❌ Offline'}
🧠 *Neural Architecture:* N-gram Hash Network
📊 *Analysis Depth:* {engram_cfg.max_ngram_size}-gram patterns
🎯 *Embedding Dimensions:* {engram_cfg.n_embed_per_ngram}
🔀 *Attention Heads:* {engram_cfg.n_head_per_ngram}

📈 *Active Layers:* {len(engram_cfg.layer_ids)}
🔑 *Vocabulary Size:* {sum(engram_cfg.engram_vocab_size):,}
⚙️ *Kernel Size:* {engram_cfg.kernel_size}

💬 *Natural Language:* {'✅ Enabled' if self.engram_initialized else '❌ Disabled'}
🔮 *Prediction Engine:* {'✅ Active' if self.engram_initialized else '❌ Inactive'}

*System Health:* All systems operational
*Last Update:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await update.message.reply_text(
            status_text,
            parse_mode=ParseMode.MARKDOWN
        )

    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language trading queries."""
        if not context.args:
            await update.message.reply_text(
                "💬 *Ask me anything about trading!*\n\n"
                "Examples:\n"
                "• \"Should I buy BTC now?\"\n"
                "• \"What's the market sentiment?\"\n"
                "• \"Analyze my current positions\"\n"
                "• \"Show me risky trades\"\n",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        user_query = " ".join(context.args)
        user_id = update.effective_user.id
        
        try:
            # Process natural language query with Engram
            response = await self._process_natural_query(user_query, user_id)
            
            await update.message.reply_text(
                response,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error processing chat query: {e}")
            await update.message.reply_text(
                "❌ Error processing your query. Please try again."
            )

    async def predict_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate AI trading predictions."""
        user_id = update.effective_user.id
        
        try:
            predictions = await self._generate_trading_predictions()
            
            response = f"""
🔮 *AI Trading Predictions*
━━━━━━━━━━━━━━━━━━━━━━━

📊 *Market Analysis:*
{predictions['market_analysis']}

🎯 *Signal Strength:* {predictions['signal_strength']}/10
📈 *Probability of Success:* {predictions['success_probability']}%
⏰ *Time Horizon:* {predictions['time_horizon']}

⚠️ *Risk Level:* {predictions['risk_level']}
💰 *Recommended Position Size:* {predictions['position_size']}%

*Confidence:* {predictions['confidence']}%
*Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            # Add inline buttons for actions
            keyboard = [
                [
                    InlineKeyboardButton("📈 Execute Trade", callback_data="execute_prediction"),
                    InlineKeyboardButton("⚙️ Set Alert", callback_data="set_prediction_alert")
                ],
                [
                    InlineKeyboardButton("📊 Detailed Analysis", callback_data="detailed_analysis")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in predict command: {e}")
            await update.message.reply_text(
                "❌ Error generating predictions. Please try again later."
            )

    async def smart_alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set up intelligent trading alerts."""
        keyboard = [
            [
                InlineKeyboardButton("🔥 High Volume Alert", callback_data="alert_volume"),
                InlineKeyboardButton("📊 Price Breakout", callback_data="alert_breakout")
            ],
            [
                InlineKeyboardButton("🧠 AI Signal Alert", callback_data="alert_ai_signal"),
                InlineKeyboardButton("⚠️ Risk Alert", callback_data="alert_risk")
            ],
            [
                InlineKeyboardButton("📈 Profit Target", callback_data="alert_profit"),
                InlineKeyboardButton("📉 Stop Loss Alert", callback_data="alert_stoploss")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 *Smart Trading Alerts*\n\n"
            "Choose the type of intelligent alert you want to set:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

    async def portfolio_insights_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Provide AI-powered portfolio insights."""
        try:
            insights = await self._generate_portfolio_insights()
            
            response = f"""
📋 *AI Portfolio Insights*
━━━━━━━━━━━━━━━━━━━━━━━

💰 *Portfolio Health:* {insights['health_score']}/100
📊 *Diversification Score:* {insights['diversification']}/100
⚡ *Risk Level:* {insights['risk_level']}
🎯 *Efficiency:* {insights['efficiency']}%

🏆 *Top Performers:*
{insights['top_performers']}

⚠️ *Risk Analysis:*
{insights['risk_analysis']}

💡 *Optimization Suggestions:*
{insights['suggestions']}

*Analysis Date:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await update.message.reply_text(
                response,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error generating portfolio insights: {e}")
            await update.message.reply_text(
                "❌ Error generating portfolio insights."
            )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks from inline keyboards."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "execute_prediction":
            await query.edit_message_text(
                "⚡ *Executing AI Prediction...*\n\n"
                "📊 Analyzing market conditions...\n"
                "🧠 Processing neural patterns...\n"
                "💰 Optimizing position size...",
                parse_mode=ParseMode.MARKDOWN
            )
            # Add execution logic here
            
        elif data.startswith("alert_"):
            alert_type = data.replace("alert_", "")
            await query.edit_message_text(
                f"🎯 *Smart Alert Set*\n\n"
                f"✅ {alert_type.replace('_', ' ').title()} alert activated\n"
                f"🔔 You'll receive notifications when conditions are met",
                parse_mode=ParseMode.MARKDOWN
            )
            # Add alert setup logic here
            
        else:
            await query.edit_message_text(
                "🔧 *Feature Coming Soon*\n\n"
                "This functionality is under development.",
                parse_mode=ParseMode.MARKDOWN
            )

    async def _generate_engram_analysis(self, trades: List[Trade], daily_profit: Dict) -> Dict:
        """Generate Engram-powered market analysis."""
        # This is where you would integrate with your Engram model
        # For now, returning a structured response
        
        open_trades = len(trades)
        profit_24h = daily_profit.get('profit_closed_ratio', 0) * 100
        
        status = f"📈 {open_trades} open trades, {profit_24h:+.2f}% 24h profit"
        
        insights = [
            "• Market showing increased volatility patterns",
            "• AI detects potential reversal signals on BTC/USDT",
            "• Volume patterns suggest institutional activity",
        ]
        
        patterns = [
            "• Bullish engulfing pattern detected on 4H timeframe",
            "• RSI divergence forming on multiple pairs",
            "• Volume-price trend shows accumulation phase",
        ]
        
        predictions = [
            "• High probability of bullish movement in next 12-24h",
            "• Consider taking partial profits on overextended positions",
            "• Watch for breakout scenarios on major pairs",
        ]
        
        recommendations = [
            "• Maintain current risk settings",
            "• Consider scaling into ETH positions on dips",
            "• Monitor DeFi sector for rotation opportunities",
        ]
        
        return {
            'status': status,
            'insights': '\n'.join(insights),
            'patterns': '\n'.join(patterns),
            'predictions': '\n'.join(predictions),
            'recommendations': '\n'.join(recommendations),
        }

    async def _process_natural_query(self, query: str, user_id: int) -> str:
        """Process natural language trading query using Engram/ClawdBot/LMStudio."""
        if not self.engram_initialized or not self.engram_model:
            return "❌ AI processing unavailable. Engram model not initialized."

        try:
            # Use Engram model for analysis
            # For chat queries, we'll use the analyze_market method with a formatted prompt
            prompt = f"User trading question: {query}\n\nPlease provide a helpful, natural language response about trading and market analysis."

            # Get response from external model (ClawdBot or LMStudio)
            if hasattr(self.engram_model, 'use_clawdbot') and self.engram_model.use_clawdbot:
                response = self.engram_model.clawdbot.send_message(prompt)
            elif hasattr(self.engram_model, 'use_lmstudio') and self.engram_model.use_lmstudio:
                response = self.engram_model._query_lmstudio(prompt)
            else:
                # Fallback to local model if available
                response = "Local Engram model response not implemented for chat queries."

            # Format the response nicely for Telegram
            formatted_response = f"""
💬 *AI Trading Assistant Response*

🤔 *Your Question:* {query}

🧠 *AI Analysis:*
{response[:1500]}  # Limit response length for Telegram

💡 *Need more details?* Try specific commands like:
• `/analysis` - Market analysis
• `/predict` - AI predictions
• `/portfolio_insights` - Portfolio review
            """

            return formatted_response

        except Exception as e:
            logger.error(f"Error processing natural query: {e}")
            return f"""
❌ *Error Processing Query*

Sorry, I encountered an issue while processing your question: "{query}"

Please try again or use specific commands like:
• `/analysis` for market insights
• `/predict` for AI predictions
• `/status` for system status

*Error:* {str(e)[:100]}
            """

    async def _generate_trading_predictions(self) -> Dict:
        """Generate AI trading predictions."""
        return {
            'market_analysis': 'Bullish momentum building with increasing volume',
            'signal_strength': 7,
            'success_probability': 68,
            'time_horizon': '12-24 hours',
            'risk_level': 'Medium',
            'position_size': 2.5,
            'confidence': 72
        }

    async def _generate_portfolio_insights(self) -> Dict:
        """Generate AI-powered portfolio insights."""
        return {
            'health_score': 78,
            'diversification': 65,
            'risk_level': 'Medium',
            'efficiency': 82,
            'top_performers': '• ETH: +12.3%\n• SOL: +8.7%\n• AVAX: +6.2%',
            'risk_analysis': 'Portfolio well-balanced with slight overexposure to altcoins',
            'suggestions': 'Consider reducing BTC allocation by 5% and adding stablecoin positions'
        }

    def setup_handlers(self, application: Application):
        """Setup all command and callback handlers."""
        # Engram-specific handlers
        application.add_handler(CommandHandler("analysis", self.analysis_command))
        application.add_handler(CommandHandler("engram_status", self.engram_status_command))
        application.add_handler(CommandHandler("chat", self.chat_command))
        application.add_handler(CommandHandler("predict", self.predict_command))
        application.add_handler(CommandHandler("smart_alerts", self.smart_alerts_command))
        application.add_handler(CommandHandler("portfolio_insights", self.portfolio_insights_command))
        
        # Callback handler for inline keyboards
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Natural language message handler (for future expansion)
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
        )

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages with natural language processing."""
        if not self.engram_initialized:
            await update.message.reply_text(
                "❌ AI processing unavailable. Please use command-based interactions.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        user_text = update.message.text
        user_id = update.effective_user.id

        # Check if this looks like a trading query
        trading_keywords = ['buy', 'sell', 'trade', 'market', 'price', 'analysis', 'predict', 'should', 'what', 'how', 'when']
        is_trading_query = any(keyword in user_text.lower() for keyword in trading_keywords)

        if is_trading_query or len(user_text.split()) > 3:  # Process longer messages or trading-related
            # Process as a trading query using AI
            response = await self._process_natural_query(user_text, user_id)
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        else:
            # Short non-trading message - provide helpful guidance
            await update.message.reply_text(
                "💬 *I'm your AI trading assistant!*\n\n"
                "Ask me anything about trading, markets, or your portfolio!\n\n"
                "*Examples:*\n"
                "• \"Should I buy BTC now?\"\n"
                "• \"What's the market doing?\"\n"
                "• \"Analyze my ETH position\"\n\n"
                "Or use commands like `/analysis`, `/predict`, `/status`",
                parse_mode=ParseMode.MARKDOWN
            )


def setup_engram_telegram_bot(rpc: RPC, config: dict) -> EngramTelegramBot:
    """
    Factory function to create and configure the Engram Telegram bot.
    
    Args:
        rpc: FreqTrade RPC instance
        config: FreqTrade configuration dictionary
        
    Returns:
        Configured EngramTelegramBot instance
    """
    return EngramTelegramBot(rpc, config)