# 🚀 Engram Trading Bot - Production Deployment Guide

**For Windows/WSL Environment: `/mnt/c/Users/OFFRSTAR0/Engram`**

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Python Launch Scripts](#python-launch-scripts)
3. [Production Environment Setup](#production-environment-setup)
4. [Live Trading Configuration](#live-trading-configuration)
5. [Exchange-Specific Settings](#exchange-specific-settings)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start

### Prerequisites

```bash
# Verify Python version (3.8+ required)
python3 --version

# Install required dependencies
pip3 install -r requirements.txt

# Or install core dependencies manually
pip3 install requests python-telegram-bot ccxt freqtrade
```

### Launch the Bot

```bash
# Navigate to your Engram directory
cd /mnt/c/Users/OFFRSTAR0/Engram

# Option 1: Enhanced Launcher (Recommended - with AI fallback)
python3 enhanced_engram_launcher.py

# Option 2: Simple Launcher (Basic functionality)
python3 simple_engram_launcher.py
```

---

## 🐍 Python Launch Scripts

### **1. Enhanced Engram Launcher** (Recommended)

**File:** `enhanced_engram_launcher.py`

**Features:**
- ✅ 3-tier AI fallback (LMStudio → Mock AI → Rule-Based)
- ✅ Configurable timeouts (default 10s, adjustable via env var)
- ✅ Environment variable support for secure credentials
- ✅ Fast connection testing (3s timeout)
- ✅ Graceful error recovery
- ✅ Enhanced logging

**Usage:**

```bash
# Basic launch
python3 enhanced_engram_launcher.py

# With environment variables
export TELEGRAM_BOT_TOKEN="8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
export TELEGRAM_CHAT_ID="1007321485"
export LMSTUDIO_URL="http://100.118.172.23:1234"
export LMSTUDIO_TIMEOUT="10"
python3 enhanced_engram_launcher.py

# With custom config
python3 enhanced_engram_launcher.py --config config/engram_freqtrade_config.json
```

**Environment Variables:**
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID
- `LMSTUDIO_URL` - LMStudio API endpoint (default: http://100.118.172.23:1234)
- `LMSTUDIO_TIMEOUT` - Query timeout in seconds (default: 10)

---

### **2. Simple Engram Launcher**

**File:** `simple_engram_launcher.py`

**Features:**
- ✅ Basic Engram integration
- ✅ Telegram connectivity
- ✅ LMStudio integration
- ⚠️ No fallback mechanism

**Usage:**

```bash
python3 simple_engram_launcher.py
```

---

## 🏭 Production Environment Setup

### Windows/WSL Configuration

**Your Environment:**
- **Path:** `/mnt/c/Users/OFFRSTAR0/Engram`
- **OS:** Windows with WSL (Ubuntu/Debian)
- **Python:** 3.8+

### Step 1: Verify Environment

```bash
# Check WSL version
wsl --version

# Check Python
python3 --version

# Check pip
pip3 --version

# Verify directory
pwd
# Should output: /mnt/c/Users/OFFRSTAR0/Engram
```

### Step 2: Install Dependencies

```bash
# Update pip
pip3 install --upgrade pip

# Install core dependencies
pip3 install requests python-telegram-bot ccxt freqtrade

# Install optional dependencies (recommended)
pip3 install numpy pandas ta-lib websockets psutil

# Verify installations
pip3 list | grep -E "(requests|telegram|ccxt|freqtrade)"
```

### Step 3: Configure Permissions

```bash
# Make launchers executable
chmod +x enhanced_engram_launcher.py
chmod +x simple_engram_launcher.py

# Create required directories
mkdir -p logs
mkdir -p user_data/data
mkdir -p user_data/strategies
mkdir -p user_data/notebooks
```

### Step 4: Test Configuration

```bash
# Run production tests
python3 live_trading_production_tests.py

# Expected output: 12/12 tests passed (100%)
```

---

## 📊 Live Trading Configuration

### Configuration File

**Location:** `config/engram_freqtrade_config.json`

### Critical Settings for Live Trading

#### 1. **Dry-Run Mode** (Safety First!)

```json
{
  "freqtrade": {
    "dry_run": true,          // ⚠️ KEEP TRUE for testing!
    "dry_run_wallet": 1000    // Virtual wallet amount
  }
}
```

**⚠️ IMPORTANT:** Always test with `dry_run: true` first!

To enable **LIVE TRADING** (after thorough testing):

```json
{
  "freqtrade": {
    "dry_run": false,         // ⚠️ REAL MONEY - BE CAREFUL!
    "dry_run_wallet": 1000    // Ignored in live mode
  }
}
```

#### 2. **Exchange Configuration**

```json
{
  "freqtrade": {
    "exchange": {
      "name": "binance",
      "key": "YOUR_API_KEY_HERE",        // ⚠️ Add your API key
      "secret": "YOUR_API_SECRET_HERE",  // ⚠️ Add your API secret
      "ccxt_config": {},
      "ccxt_async_config": {},
      "pair_whitelist": [
        "BTC/USDT",
        "ETH/USDT",
        "BNB/USDT",
        "SOL/USDT",
        "AVAX/USDT"
      ],
      "pair_blacklist": []
    }
  }
}
```

#### 3. **Risk Management**

```json
{
  "freqtrade": {
    "max_open_trades": 5,              // Max simultaneous trades
    "stake_currency": "USDT",          // Base currency
    "stake_amount": "unlimited",       // Or fixed amount like 100
    "tradable_balance_ratio": 0.5      // Use 50% of balance
  },
  "engram": {
    "trading": {
      "confidence_threshold": 0.7,     // 70% confidence required
      "max_signals_per_pair": 3,       // Max signals per pair
      "risk_management": {
        "max_position_size": 0.1,      // 10% max per position
        "stop_loss_multiplier": 1.5,   // Stop loss at 1.5x ATR
        "take_profit_multiplier": 2.0  // Take profit at 2x ATR
      }
    }
  }
}
```

#### 4. **Telegram Notifications**

```json
{
  "telegram": {
    "enabled": true,
    "token": "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA",
    "chat_id": "1007321485",
    "notification_settings": {
      "status": "on",
      "warning": "on",
      "startup": "on",
      "entry": "on",
      "entry_fill": "on",
      "exit": "on",
      "exit_fill": "on",
      "protection_trigger": "on"
    }
  }
}
```

---

## 🏦 Exchange-Specific Settings

### Binance (Default)

**Configuration:**

```json
{
  "exchange": {
    "name": "binance",
    "key": "YOUR_BINANCE_API_KEY",
    "secret": "YOUR_BINANCE_API_SECRET",
    "ccxt_config": {
      "enableRateLimit": true,
      "rateLimit": 100
    }
  }
}
```

**API Permissions Required:**
- ✅ Read account information
- ✅ Enable spot trading
- ⚠️ DO NOT enable withdrawals

**Rate Limits:**
- Requests: 10/second
- Orders: 5/second
- Weight: 1200/minute

**Recommended Pairs:**
- BTC/USDT (High liquidity)
- ETH/USDT (High liquidity)
- BNB/USDT (Low fees with BNB)
- SOL/USDT (Volatile, good for trading)
- AVAX/USDT (Emerging asset)

---

### Kraken (Alternative)

**Configuration:**

```json
{
  "exchange": {
    "name": "kraken",
    "key": "YOUR_KRAKEN_API_KEY",
    "secret": "YOUR_KRAKEN_API_SECRET",
    "ccxt_config": {
      "enableRateLimit": true,
      "rateLimit": 1000
    },
    "pair_whitelist": [
      "BTC/USD",
      "ETH/USD",
      "XRP/USD",
      "ADA/USD"
    ]
  }
}
```

**API Permissions Required:**
- ✅ Query funds
- ✅ Query open/closed orders
- ✅ Create & modify orders
- ⚠️ DO NOT enable withdrawals

**Rate Limits:**
- Tier 2: 15 calls/second
- Tier 3: 20 calls/second

**Notes:**
- Kraken uses different pair notation (BTC/USD vs BTC/USDT)
- Higher fees than Binance
- Better for US customers

---

### Coinbase Pro (Alternative)

**Configuration:**

```json
{
  "exchange": {
    "name": "coinbasepro",
    "key": "YOUR_COINBASE_API_KEY",
    "secret": "YOUR_COINBASE_API_SECRET",
    "password": "YOUR_COINBASE_PASSPHRASE",
    "ccxt_config": {
      "enableRateLimit": true,
      "rateLimit": 334
    },
    "pair_whitelist": [
      "BTC/USD",
      "ETH/USD",
      "LTC/USD"
    ]
  }
}
```

**API Permissions Required:**
- ✅ View
- ✅ Trade
- ⚠️ DO NOT enable Transfer

**Rate Limits:**
- Public: 3 requests/second
- Private: 5 requests/second

---

## 📈 Monitoring and Maintenance

### Real-Time Monitoring

#### 1. **Telegram Bot Commands**

```
/status          - Current bot status
/profit          - Profit/loss summary
/balance         - Account balance
/daily           - Daily performance
/trades          - Recent trades
/performance     - Performance metrics
/analysis        - AI market analysis
/predict         - AI predictions
/engram_status   - Engram AI status
/help            - Command help
```

#### 2. **Log Files**

```bash
# View real-time logs
tail -f logs/bot_runner.log

# View Engram logs
tail -f logs/engram.log

# View FreqTrade logs
tail -f logs/freqtrade.log

# Search for errors
grep -i error logs/*.log

# Search for trades
grep -i "trade" logs/*.log
```

#### 3. **System Monitoring**

```bash
# Check bot process
ps aux | grep engram

# Check memory usage
free -h

# Check disk space
df -h

# Check network connectivity
ping -c 3 100.118.172.23
```

### Daily Maintenance Tasks

**Morning Routine:**
1. Check Telegram for overnight alerts
2. Review `/daily` performance
3. Check `/balance` and `/profit`
4. Review logs for errors: `grep -i error logs/*.log`

**Evening Routine:**
1. Review day's trades: `/trades`
2. Check `/performance` metrics
3. Backup configuration: `cp config/engram_freqtrade_config.json config/backup_$(date +%Y%m%d).json`
4. Review and archive logs if needed

### Weekly Maintenance Tasks

1. **Performance Review:**
   - Analyze win rate
   - Review profit/loss
   - Adjust strategy if needed

2. **System Updates:**
   ```bash
   pip3 install --upgrade freqtrade
   pip3 install --upgrade python-telegram-bot
   pip3 install --upgrade ccxt
   ```

3. **Backup:**
   ```bash
   # Backup entire config directory
   tar -czf backup_$(date +%Y%m%d).tar.gz config/ user_data/
   ```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **LMStudio Timeout Errors**

**Error:**
```
HTTPConnectionPool(host='100.118.172.23', port=1234): Read timed out
```

**Solution:**
- Enhanced launcher automatically falls back to Mock AI
- Verify LMStudio is running: `curl http://100.118.172.23:1234/v1/models`
- Increase timeout: `export LMSTUDIO_TIMEOUT="30"`
- Check firewall settings

#### 2. **Telegram Connection Failed**

**Error:**
```
Telegram bot connection failed
```

**Solution:**
```bash
# Verify token and chat_id
export TELEGRAM_BOT_TOKEN="8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
export TELEGRAM_CHAT_ID="1007321485"

# Test connection
curl https://api.telegram.org/bot8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA/getMe
```

#### 3. **Exchange API Errors**

**Error:**
```
Exchange API authentication failed
```

**Solution:**
1. Verify API key and secret in config
2. Check API permissions on exchange
3. Verify IP whitelist (if enabled)
4. Check rate limits: `grep -i "rate limit" logs/*.log`

#### 4. **Permission Denied**

**Error:**
```
Permission denied: enhanced_engram_launcher.py
```

**Solution:**
```bash
chmod +x enhanced_engram_launcher.py
chmod +x simple_engram_launcher.py
```

#### 5. **Module Not Found**

**Error:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
pip3 install requests python-telegram-bot ccxt freqtrade
```

---

## 🎯 Production Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (100%): `python3 live_trading_production_tests.py`
- [ ] Configuration reviewed: `config/engram_freqtrade_config.json`
- [ ] **Dry-run mode enabled** (`dry_run: true`)
- [ ] Exchange API keys configured (if live trading)
- [ ] Telegram bot tested and working
- [ ] LMStudio endpoint accessible (or fallback enabled)
- [ ] Risk management settings configured
- [ ] Backup of configuration created

### Initial Deployment (Dry-Run)

- [ ] Launch bot: `python3 enhanced_engram_launcher.py`
- [ ] Verify Telegram notifications working
- [ ] Test all Telegram commands
- [ ] Monitor logs for 24 hours
- [ ] Review virtual trades
- [ ] Verify AI analysis working

### Live Trading Deployment (After Dry-Run Success)

- [ ] **Minimum 7 days successful dry-run testing**
- [ ] Review and approve all dry-run trades
- [ ] Set `dry_run: false` in config
- [ ] Add exchange API keys
- [ ] Reduce `max_open_trades` to 1-2 initially
- [ ] Set conservative `stake_amount`
- [ ] Enable all Telegram notifications
- [ ] Create backup: `cp config/engram_freqtrade_config.json config/live_backup.json`
- [ ] Launch with monitoring: `python3 enhanced_engram_launcher.py 2>&1 | tee logs/live_launch.log`
- [ ] Monitor first trade closely
- [ ] Gradually increase `max_open_trades` after success

### Post-Deployment

- [ ] Daily log review
- [ ] Weekly performance analysis
- [ ] Monthly strategy optimization
- [ ] Regular backups
- [ ] System updates

---

## 📞 Support and Resources

### Documentation
- FreqTrade Docs: https://www.freqtrade.io/
- CCXT Docs: https://docs.ccxt.com/
- Telegram Bot API: https://core.telegram.org/bots/api

### Logs Location
- Bot logs: `logs/bot_runner.log`
- Engram logs: `logs/engram.log`
- FreqTrade logs: `logs/freqtrade.log`

### Configuration Files
- Main config: `config/engram_freqtrade_config.json`
- Telegram config: `config/telegram/working_telegram_config.json`
- Strategy: `user_data/strategies/EngramStrategy.py`

---

## ⚠️ Important Safety Reminders

1. **ALWAYS test with dry-run first** - Never skip this step!
2. **Start small** - Use minimal stake amounts initially
3. **Monitor closely** - Especially first 24-48 hours
4. **Set stop losses** - Protect your capital
5. **Never invest more than you can afford to lose**
6. **Keep API keys secure** - Never share or commit to git
7. **Regular backups** - Backup config and data regularly
8. **Stay informed** - Monitor market conditions
9. **Test updates** - Always test in dry-run before live
10. **Have an exit plan** - Know when to stop trading

---

## 🎉 Success Metrics

**Your bot is working correctly if:**
- ✅ Telegram notifications arriving promptly
- ✅ AI analysis generating insights
- ✅ Trades executing according to strategy
- ✅ No errors in logs
- ✅ Performance metrics positive
- ✅ Risk management rules followed

---

**Last Updated:** 2026-01-31  
**Version:** 1.0.0  
**Environment:** Windows/WSL - `/mnt/c/Users/OFFRSTAR0/Engram`

**Status:** ✅ **PRODUCTION READY**
