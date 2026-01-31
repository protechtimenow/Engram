# Engram Bot - Quick Start Guide

**Status:** ✅ READY FOR DEPLOYMENT  
**Last Updated:** 2026-01-31

---

## 🚀 5-Minute Deployment

### Prerequisites
- Server with Python 3.8+ (tested on 3.9.25)
- Git installed
- Internet connection

### Step 1: Clone Repository
```bash
git clone https://github.com/protechtimenow/Engram.git
cd Engram
```

### Step 2: Verify Setup
```bash
python3 simple_bot_test.py
```

**Expected Output:**
```
✅ Passed: 10/10 (100.0%)
Status: READY FOR DEPLOYMENT
```

### Step 3: Launch Bot
```bash
# Option A: Direct launch
python3 live_bot_runner.py &

# Option B: Process manager
chmod +x clawdbot_manager.sh
./clawdbot_manager.sh start
```

### Step 4: Monitor
```bash
tail -f logs/bot_runner.log
```

**That's it! Your bot is running.**

---

## 📱 Test Your Bot

Send a message to your Telegram bot:
- Bot: **Freqtrad3_bot**
- Commands: `/start`, `/help`, `/status`

---

## 🛠️ Process Management

### Start Bot
```bash
./clawdbot_manager.sh start
```

### Stop Bot
```bash
./clawdbot_manager.sh stop
```

### Check Status
```bash
./clawdbot_manager.sh status
```

### Restart Bot
```bash
./clawdbot_manager.sh restart
```

### View Logs
```bash
./clawdbot_manager.sh logs
```

---

## 🔧 Configuration

### Bot Credentials
File: `config/telegram/working_telegram_config.json`
```json
{
  "telegram": {
    "bot_token": "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA",
    "chat_id": "1007321485"
  }
}
```

### Environment Variables
File: `.env`
```bash
TELEGRAM_BOT_TOKEN=8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA
TELEGRAM_CHAT_ID=1007321485
```

---

## 🐛 Troubleshooting

### Bot Won't Start
```bash
# Check Python version
python3 --version

# Check syntax
python3 -m py_compile live_telegram_bot.py

# View errors
cat logs/bot_runner.log
```

### Can't Connect to Telegram
```bash
# Test API
curl -I https://api.telegram.org

# Verify config
python3 simple_bot_test.py
```

### Process Not Running
```bash
# Check if running
ps aux | grep python

# Kill stuck processes
pkill -f live_bot_runner.py

# Restart
./clawdbot_manager.sh start
```

---

## 📊 Test Results

### Simple Test Suite (Critical Path)
```
Total Tests: 10
✅ Passed: 10 (100.0%)
Status: READY
```

### Comprehensive Test Suite (Full System)
```
Total Tests: 25
✅ Passed: 19 (76.0%)
Status: CORE READY
```

---

## 🎯 Next Steps

### After 24 Hours
1. Check logs: `tail -100 logs/bot_runner.log`
2. Verify uptime: `./clawdbot_manager.sh status`
3. Test message handling via Telegram

### Add Advanced Features
```bash
# Install dependencies
pip3 install python-telegram-bot requests websockets sympy torch numpy

# Test advanced features
python3 comprehensive_test_suite.py
```

---

## 📞 Support

### Documentation
- `DEPLOYMENT_SUMMARY.md` - Full deployment guide
- `FINAL_TEST_REPORT.md` - Test documentation
- `README.md` - Project overview

### Test Scripts
- `simple_bot_test.py` - Quick validation (100% pass)
- `comprehensive_test_suite.py` - Full system test (76% pass)

### Process Management
- `clawdbot_manager.sh` - Start/stop/status/restart

---

## ✅ Deployment Checklist

- [x] Repository cloned
- [x] Tests passing (100% on simple suite)
- [x] Configuration validated
- [x] Bot launched
- [ ] Logs monitored for 24 hours
- [ ] Message handling verified
- [ ] Backup strategy implemented

---

**Generated:** 2026-01-31  
**Commit:** e582dd2016644788e2d8958d36391914d8f227ed  
**Status:** ✅ READY FOR DEPLOYMENT
