# Engram-FreqTrade Integration 🤖📊

An advanced cryptocurrency trading system that combines FreqTrade's robust trading framework with Engram's neural architecture for intelligent market analysis and natural language interaction.

## 🌟 Features

### 🧠 AI-Powered Trading
- **Neural N-gram Analysis**: Advanced pattern recognition using Engram's neural hashing
- **Real-time Market Sentiment**: AI-driven market analysis and predictions
- **Risk Management**: Intelligent position sizing and stop-loss optimization
- **Multi-timeframe Analysis**: Simultaneous analysis across different timeframes

### 📱 Enhanced Telegram Interface
- **Natural Language Commands**: Talk to your bot in plain English
- **AI Chat Assistant**: Get trading advice and market insights
- **Smart Alerts**: AI-powered notifications for trading opportunities
- **Portfolio Intelligence**: AI analysis of your trading performance

### 🚀 Advanced Strategy
- **Hybrid Approach**: Combines technical analysis with neural predictions
- **Adaptive Learning**: System learns from market patterns
- **Dynamic Signal Generation**: Context-aware trading signals
- **Multi-pair Support**: Trade multiple cryptocurrencies simultaneously

## 📋 Prerequisites

- Python 3.9+
- 8GB+ RAM (16GB recommended for Engram model)
- Linux/macOS/Windows with WSL2
- Telegram Bot Token
- Exchange API Keys (Binance, Bybit, etc.)

## 🛠️ Installation

### 1. Clone and Setup

```bash
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade

# Copy the integration files
cp /path/to/engram_trading_strategy.py .
cp /path/to/engram_telegram_bot.py .
cp /path/to/launch_engram_trader.py .
cp /path/to/engram_freqtrade_config.json .
cp /path/to/requirements_engram_integration.txt .
```

### 2. Install Dependencies

```bash
# Install FreqTrade
pip install -e .

# Install integration dependencies
pip install -r requirements_engram_integration.txt

# Install TA-Lib (system dependency)
# Ubuntu/Debian:
sudo apt-get install build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..

# macOS (using Homebrew):
brew install ta-lib

# Windows: Download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
```

### 3. Configuration

1. **Telegram Bot Setup**:
   ```bash
   # Create a bot with @BotFather on Telegram
   # Get your bot token and update the config
   ```

2. **Exchange API Keys**:
   ```json
   "exchange": {
     "name": "binance",
     "key": "your_api_key",
     "secret": "your_api_secret"
   }
   ```

3. **Update Configuration**:
   ```bash
   # Edit engram_freqtrade_config.json
   nano engram_freqtrade_config.json
   
   # Update these fields:
   # - telegram.token
   # - telegram.chat_id  
   # - exchange.key and exchange.secret
   # - engram.trading settings
   ```

## 🚀 Quick Start

### 1. Test in Dry-Run Mode

```bash
python launch_engram_trader.py --dry-run
```

### 2. Check System Status

```bash
python launch_engram_trader.py --status
```

### 3. Start Live Trading (After Testing)

```bash
python launch_engram_trader.py
```

## 📱 Telegram Commands

### Standard Commands
- `/status` - Current trading status
- `/profit` - Profit/loss summary
- `/balance` - Account balance
- `/trades` - Open and closed trades
- `/help` - Help message

### Engram AI Commands
- `/analysis` - 🧠 AI market analysis
- `/engram_status` - 🔬 Engram system status
- `/chat <query>` - 💬 Natural language trading questions
- `/predict` - 🔮 AI trading predictions
- `/smart_alerts` - 🎯 Set intelligent alerts
- `/portfolio_insights` - 📋 AI portfolio analysis

### Natural Language Examples

```
/chat Should I buy BTC now?
/chat What's the market sentiment?
/chat Analyze my current positions
/chat Show me risky trades
```

## 🧠 How Engram Works

### Neural Architecture
- **N-gram Hash Network**: Processes market data as sequences
- **Multi-head Attention**: Identifies complex patterns
- **Neural Hashing**: Efficient pattern recognition
- **Context Analysis**: Understands market context

### Trading Integration
- **Signal Generation**: Combines TA indicators with neural predictions
- **Risk Assessment**: AI-powered risk evaluation
- **Market Analysis**: Real-time sentiment and pattern detection
- **Portfolio Optimization**: Intelligent position management

## 📊 Configuration Options

### Engram Settings
```json
"engram": {
  "enabled": true,
  "max_ngram_size": 3,
  "n_embed_per_ngram": 512,
  "n_head_per_ngram": 8,
  "trading": {
    "confidence_threshold": 0.7,
    "max_signals_per_pair": 3,
    "analysis_interval": 15
  }
}
```

### Telegram Features
```json
"telegram": {
  "engram_features": {
    "enabled": true,
    "natural_language_processing": true,
    "ai_predictions": true,
    "smart_alerts": true
  }
}
```

## 🔧 Advanced Usage

### Custom Strategy Development

1. **Extend EngramStrategy**:
```python
class MyEngramStrategy(EngramStrategy):
    def populate_entry_trend(self, dataframe, metadata):
        # Custom logic
        return super().populate_entry_trend(dataframe, metadata)
```

2. **Add Custom Indicators**:
```python
def _populate_engram_indicators(self, dataframe, metadata):
    # Custom neural indicators
    return super()._populate_engram_indicators(dataframe, metadata)
```

### Backtesting

```bash
freqtrade backtesting \
  --strategy EngramStrategy \
  --strategy-path . \
  --timerange 20230101-20231231 \
  --timeframe 5m
```

### Performance Optimization

```bash
# Enable GPU acceleration (if available)
export CUDA_VISIBLE_DEVICES=0

# Optimize memory usage
export OMP_NUM_THREADS=4
```

## 📈 Monitoring and Logs

### Log Files
- `engram_trader.log` - Main system log
- FreqTrade logs - Standard FreqTrade logging

### Performance Metrics
- Signal accuracy rate
- Profit/loss tracking
- Engram confidence scores
- Trade execution speed

## ⚠️ Risk Management

### Trading Safeguards
- **Position Sizing**: Automatic risk-based position calculation
- **Stop Loss**: Dynamic stop-loss based on market volatility
- **Confidence Thresholds**: Only trade high-confidence signals
- **Portfolio Limits**: Maximum exposure per asset

### Best Practices
1. **Start with Dry-Run**: Always test before real trading
2. **Monitor Performance**: Regularly review trading results
3. **Adjust Parameters**: Optimize based on market conditions
4. **Risk Management**: Never risk more than you can afford

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 Documentation

- [FreqTrade Documentation](https://www.freqtrade.io/)
- [Engram Architecture](./engram_architecture.md)
- [API Reference](./api_reference.md)
- [Troubleshooting](./troubleshooting.md)

## ⚡ Performance Tips

### System Optimization
```bash
# For optimal performance:
# Use SSD storage
# Ensure sufficient RAM (16GB+)
# Use multi-core CPU (8+ cores recommended)
```

### Engram Tuning
```json
"engram": {
  "max_ngram_size": 4,        // Higher for more complex patterns
  "n_embed_per_ngram": 1024,  // Larger for better representation
  "confidence_threshold": 0.8 // Higher for more selective trading
}
```

## 🆘 Troubleshooting

### Common Issues
1. **Memory Issues**: Reduce embedding dimensions or use smaller models
2. **Slow Performance**: Enable GPU acceleration or reduce analysis frequency
3. **Connection Errors**: Check API keys and network connectivity
4. **Telegram Issues**: Verify bot token and chat ID

### Getting Help
- Check the logs: `tail -f engram_trader.log`
- Join our Discord community
- Open an issue on GitHub

## 📜 License

This integration is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- FreqTrade development team
- Engram architecture researchers
- Community contributors and testers

---

**⚠️ Disclaimer**: This software is for educational and research purposes. Cryptocurrency trading involves substantial risk of loss. Use at your own risk and never invest more than you can afford to lose.