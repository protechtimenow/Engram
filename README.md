# Engram Trading Skill for Clawdbot

🧠 **AI-Powered Financial Intelligence Platform**

This skill integrates the complete Engram Trading System into Clawdbot, enabling intelligent financial analysis, automated trading, and multi-channel alerts.

## 🎯 What This Skill Does

The Engram Trading skill transforms Clawdbot into a sophisticated financial intelligence platform that combines:

- **Neural Analysis**: Engram's advanced neural hashing for pattern recognition
- **Sentiment Analysis**: Real-time market sentiment from Reddit and social media
- **Automated Trading**: FreqTrade integration with AI-enhanced strategies
- **Multi-Channel Alerts**: Telegram, Discord, Slack notifications
- **Real-Time Dashboard**: Web-based monitoring interface

## 📦 Installation

### 1. Install the Skill

The skill has been packaged and is ready to use:

**Location**: `clawdbot_repo/skills/engram-trading.skill`

To install in Clawdbot:
```bash
# Copy the skill file to your Clawdbot skills directory
cp clawdbot_repo/skills/engram-trading.skill ~/.clawdbot/skills/

# Or install directly
clawdbot skill install clawdbot_repo/skills/engram-trading.skill
```

### 2. Skill Structure

```
engram-trading/
├── SKILL.md                          # Main skill documentation
├── scripts/
│   └── master_launcher.py           # Unified system launcher
└── references/
    ├── setup-guide.md               # Complete setup instructions
    ├── api-reference.md             # API documentation
    ├── strategies.md                # Trading strategies guide
    ├── trading-config.md            # Configuration reference
    └── troubleshooting.md           # Common issues & solutions
```

## 🚀 Quick Start

### Using the Skill with Clawdbot

Once installed, Clawdbot will automatically use this skill when you ask about:

- Starting the Engram trading system
- Financial market analysis
- Trading bot operations
- Sentiment analysis
- Multi-channel alerts

**Example Interactions**:

```
You: "Start the Engram trading system in dry-run mode"
Clawdbot: [Uses engram-trading skill]
          🚀 Launching Engram Trading System...
          📊 Dashboard: http://localhost:8585
          🤖 Trading bot started in dry-run mode
          📱 Telegram alerts enabled

You: "What's the current market sentiment for BTC?"
Clawdbot: [Uses engram-trading skill]
          📊 Analyzing BTC sentiment...
          Market Sentiment: 0.65 (Bullish)
          Confidence: 85%
          Trend: Strong upward momentum

You: "Create a price alert for BTC at $45,000"
Clawdbot: [Uses engram-trading skill]
          ✅ Alert created for BTC at $45,000
          Channels: Telegram, Discord
          You'll be notified when price crosses threshold
```

## 🛠️ Components Included

### 1. Master Launcher (`scripts/master_launcher.py`)

Orchestrates all Engram components:
- Financial intelligence system
- Engram neural core
- FreqTrade trading engine
- Telegram bot
- API server
- Web dashboard

**Usage**:
```bash
# Full system
python scripts/master_launcher.py --mode full --dry-run

# Trading only
python scripts/master_launcher.py --mode trading

# Intelligence only
python scripts/master_launcher.py --mode intelligence
```

### 2. Reference Documentation

Complete guides for:
- **Setup**: Step-by-step installation and configuration
- **API**: All endpoints and usage examples
- **Strategies**: AI trading strategies and customization
- **Configuration**: Complete config reference
- **Troubleshooting**: Common issues and solutions

## 📊 Features

### Financial Intelligence
- Real-time sentiment analysis from 11+ Reddit communities
- Market trend detection with momentum analysis
- Entity recognition (stocks, crypto, financial terms)
- Neural pattern recognition using Engram architecture

### Trading Capabilities
- AI-enhanced trading strategies
- Sentiment-aware entry/exit signals
- Adaptive risk management
- Multi-timeframe analysis
- Backtesting and optimization

### Multi-Channel Integration
- **Telegram**: Commands, alerts, analysis
- **Discord**: Embeds, reactions, notifications
- **Slack**: Blocks, modals, updates
- **Web Dashboard**: Real-time monitoring

### API Endpoints
- `/api/engram/financial/sentiment` - Market sentiment
- `/api/engram/financial/trends` - Trend analysis
- `/api/clawdbot/status` - Agent network status
- `/api/clawdbot/alert` - Create alerts
- `/api/dashboard/data` - Unified dashboard data

## 🔧 Configuration

### Required Setup

1. **Exchange API Keys** (for live trading)
2. **Telegram Bot Token** (for alerts)
3. **Reddit API Credentials** (for sentiment)
4. **LMStudio** (optional, for local AI)

See `references/setup-guide.md` for detailed instructions.

### Quick Configuration

```json
{
  "exchange": {
    "name": "binance",
    "key": "YOUR_API_KEY",
    "secret": "YOUR_API_SECRET"
  },
  "telegram": {
    "enabled": true,
    "token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  },
  "engram": {
    "enabled": true,
    "sentiment_weight": 0.3,
    "trend_weight": 0.4
  }
}
```

## 📈 Usage Examples

### Start Full System
```bash
python scripts/master_launcher.py --mode full --dry-run
```

### Get Market Sentiment
```bash
curl http://localhost:8000/api/engram/financial/sentiment
```

### Create Alert
```bash
curl -X POST http://localhost:8000/api/clawdbot/alert \
  -H "Content-Type: application/json" \
  -d '{"asset":"BTC","threshold":45000,"channels":["telegram"]}'
```

### Telegram Commands
```
/status - System status
/balance - Portfolio balance
/analyze BTC/USDT - AI analysis
/sentiment - Market sentiment
/trends - Trend analysis
```

## 🎓 Learning Resources

### Documentation
- **Setup Guide**: Complete installation walkthrough
- **API Reference**: All endpoints with examples
- **Strategies Guide**: Trading strategies and customization
- **Config Reference**: All configuration options
- **Troubleshooting**: Common issues and solutions

### Key Concepts
- **Engram Neural Hashing**: Pattern recognition in market data
- **Sentiment Analysis**: Extracting market mood from social media
- **AI Trading Strategies**: Combining neural analysis with technical indicators
- **Multi-Agent System**: Coordinating multiple AI agents across platforms

## 🔒 Safety & Risk Management

### Always Start with Dry-Run
```json
{
  "dry_run": true,
  "dry_run_wallet": 1000
}
```

### Risk Limits
- Max open trades: 3 (configurable)
- Stop loss: 2% (configurable)
- Max stake per trade: 10% of portfolio
- Daily loss limit: 5%

### Monitoring
- Check dashboard regularly
- Review logs in `logs/` directory
- Set up alerts for significant events
- Monitor API health endpoints

## 🐛 Troubleshooting

Common issues and solutions are documented in `references/troubleshooting.md`:

- Installation problems
- Configuration errors
- Runtime issues
- Performance optimization
- Network problems

## 📝 File Structure in Main Project

The skill integrates with your existing Engram project:

```
Engram/
├── scripts/
│   ├── master_launcher.py       # Created by skill
│   ├── launch_engram_trader.py  # Existing
│   └── quick_start_financial.py # Existing
├── src/
│   ├── core/                    # Engram neural core
│   ├── trading/                 # Trading strategies
│   ├── engram_telegram/         # Telegram integration
│   └── tools/                   # Utilities
├── config/                      # Configuration files
├── freqtrade/                   # FreqTrade framework
└── clawdbot_repo/
    └── skills/
        └── engram-trading/      # This skill
```

## 🤝 Integration with Clawdbot

This skill enables Clawdbot to:

1. **Understand Financial Queries**: Automatically triggers on trading/finance questions
2. **Execute Trading Operations**: Start/stop bots, analyze markets, create alerts
3. **Provide Real-Time Insights**: Access live sentiment and trend data
4. **Manage Multi-Channel Alerts**: Send notifications across platforms
5. **Monitor System Health**: Check status of all components

## 🎯 Next Steps

1. **Install the skill** in Clawdbot
2. **Review setup guide** for configuration
3. **Start in dry-run mode** to test
4. **Explore API endpoints** for integration
5. **Customize strategies** for your needs
6. **Monitor and adjust** based on performance

## 📚 Additional Resources

- **Engram Paper**: `Engram_paper.pdf` - Neural architecture details
- **FreqTrade Docs**: https://www.freqtrade.io/
- **Clawdbot Docs**: See clawdbot_repo/docs/
- **API Examples**: `references/api-reference.md`

## 🏆 Features Summary

✅ **Financial Intelligence** - Real-time sentiment and trend analysis  
✅ **AI Trading** - Neural network-enhanced strategies  
✅ **Multi-Channel** - Telegram, Discord, Slack integration  
✅ **Web Dashboard** - Real-time monitoring interface  
✅ **API Gateway** - RESTful + WebSocket support  
✅ **Risk Management** - Adaptive position sizing and stop losses  
✅ **Backtesting** - Test strategies on historical data  
✅ **Monitoring** - Health checks and performance metrics  

## 📄 License

See LICENSE file in the main Engram project.

---

**Built with ❤️ for intelligent financial trading**

🧠 Engram Neural Architecture + 🤖 Clawdbot Multi-Agent System = 🚀 Powerful Trading Platform
