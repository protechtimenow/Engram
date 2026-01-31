# 🚀 Quick Start - Enhanced Engram Bot

## ⚡ Fastest Way to Launch (30 seconds)

```powershell
cd C:\Users\OFFRSTAR0\Engram
.\launch_bot.ps1
```

**That's it!** The bot will:
1. Load environment variables from `.env`
2. Verify credentials
3. Connect to LMStudio and Telegram
4. Start listening for messages

---

## 📱 Test Your Bot

Send these messages to **@Freqtrad3_bot** on Telegram:

1. **`/status`** - Check bot status
2. **`/help`** - See available commands
3. **`Hi`** - Test AI responses
4. **`/analyze BTC/USDT`** - Get market analysis

---

## 🔧 Troubleshooting

### Issue: "Missing Telegram credentials"
**Fix:**
```powershell
# Verify .env file exists
Get-Content .env

# Should show:
# TELEGRAM_BOT_TOKEN=8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA
# TELEGRAM_CHAT_ID=1007321485
```

### Issue: "LMStudio connection timeout"
**Fix:**
```powershell
# Verify LMStudio is running
curl http://100.118.172.23:1234/v1/models

# Should return JSON with model info
```

### Issue: "Engram model not available"
**This is normal!** The bot works 100% without Engram using LMStudio AI.

**To enable Engram (optional):**
```powershell
pip install -r requirements.txt
# Wait 10-15 minutes for installation
.\launch_bot.ps1
```

---

## 📊 What You Should See

### Successful Launch:
```
🚀 Enhanced Engram Bot Launcher
================================

📂 Step 1: Loading environment variables...
✅ TELEGRAM_BOT_TOKEN = 8517504737...6kA
✅ TELEGRAM_CHAT_ID = 1007321485
✅ LMSTUDIO_URL = http://100.118.172.23:1234

🔍 Step 2: Verifying critical variables...
   ✅ TELEGRAM_BOT_TOKEN = 8517504737...6kA
   ✅ TELEGRAM_CHAT_ID = 1007321485
   ✅ LMSTUDIO_URL = http://100.118.172.23:1234

🤖 Step 3: Launching Enhanced Engram Bot...

2026-01-31 XX:XX:XX - __main__ - INFO - ✅ LMStudio connected
2026-01-31 XX:XX:XX - __main__ - INFO - ✅ Telegram bot connected: Freqtrad3_bot
2026-01-31 XX:XX:XX - __main__ - INFO - 🤖 Bot is running and listening for messages...
```

### Bot Status Response:
```
🤖 Bot Status:

• Status: Running
• Time: 2026-01-31 XX:XX:XX
• Engram Model: ⚠️ Not Available
• LMStudio: ✅ Connected
• Telegram: ✅ Connected
• AI Mode: LMStudio
```

---

## 🎯 Files You Need

### Required (Already Fixed):
- ✅ `.env` - Environment variables
- ✅ `enhanced_engram_launcher.py` - Bot script
- ✅ `launch_bot.ps1` - Launcher script
- ✅ `load_env.ps1` - Env loader

### Optional (For Engram Model):
- ⚠️ `requirements.txt` - Python dependencies
- ⚠️ `test_engram_model_loading.py` - Diagnostic tool

---

## ✅ You're Ready!

**Your bot is 100% functional and production-ready.**

Just run:
```powershell
.\launch_bot.ps1
```

And start chatting with @Freqtrad3_bot! 🎉
