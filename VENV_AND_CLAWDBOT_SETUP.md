# Virtual Environment & ClawdBot Setup Guide

## Quick Answer: Virtual Environment Activation

### PowerShell (Windows)
```powershell
cd C:\Users\OFFRSTAR0\Engram
.venv\Scripts\Activate.ps1
```

### WSL/Bash
```bash
source .venv/Scripts/activate
```

---

## What Was Fixed

### 1. Response Formatting ✅
**Problem:** Telegram responses showed technical details (reasoning, mode indicators)

**Solution:** Added DEBUG_MODE flag
- **Production Mode (default):** Clean, natural responses only
- **Debug Mode:** Shows technical details for troubleshooting

**Enable Debug Mode:**
```powershell
$env:DEBUG_MODE="true"
python enhanced_engram_launcher.py
```

### 2. ClawdBot Configuration ✅
**Problems Fixed:**
- Model name: `lmstudio/local-model` → `local-lmstudio/glm-4.7-flash`
- LMStudio IP: `192.168.56.1` → `100.118.172.23`
- Added WebSocket authentication token

**Files Modified:**
- `../.clawdbot/clawdbot.json`
- `../.clawdbot/credentials/auth-profiles.json`
- `src/core/engram_demo_v1.py`
- `enhanced_engram_launcher.py`

### 3. Known Issue: WebSocket Authentication ⚠️
**Status:** Still seeing "invalid handshake" errors

**Current Workaround:** The bot falls back to direct LMStudio connection, which works fine

**To Fix (if needed):**
The websockets library may need a different auth method. For now, the bot works without ClawdBot by connecting directly to LMStudio.

---

## System Architecture

### Current Working Setup:
```
Telegram Messages
    ↓
Enhanced Engram Bot
    ↓
LMStudio Direct (http://100.118.172.23:1234/v1)
    ↓
glm-4.7-flash Model
```

### Intended Setup (when WebSocket auth is fixed):
```
Telegram Messages
    ↓
Enhanced Engram Bot
    ↓
Engram Neural Network
    ↓
ClawdBot Gateway (ws://127.0.0.1:18789)
    ↓
LMStudio (http://100.118.172.23:1234/v1)
    ↓
glm-4.7-flash Model
```

---

## How to Start

### Easy Method (Recommended):
```powershell
cd C:\Users\OFFRSTAR0\Engram
.\start_engram.ps1
```

### Manual Method:
```powershell
# 1. Navigate to Engram directory
cd C:\Users\OFFRSTAR0\Engram

# 2. Activate virtual environment
.venv\Scripts\Activate.ps1

# 3. Run bot
python enhanced_engram_launcher.py
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG_MODE` | `false` | Show technical details in responses |
| `LMSTUDIO_URL` | `http://100.118.172.23:1234` | LMStudio API endpoint |
| `LMSTUDIO_TIMEOUT` | `180` | Timeout in seconds |
| `CLAWDBOT_WS_URL` | `ws://127.0.0.1:18789` | ClawdBot WebSocket URL |
| `CLAWDBOT_AUTH_TOKEN` | (auto) | ClawdBot authentication token |
| `TELEGRAM_BOT_TOKEN` | (from config) | Telegram bot token |
| `TELEGRAM_CHAT_ID` | (from config) | Telegram chat ID |

---

## Response Examples

### Production Mode (Clean):
**User:** "Hi"  
**Bot:** "Hello! How can I assist you today?"

**User:** "/analyze BTC/USDT"  
**Bot:** "Based on current market conditions, I recommend holding your position. The trend shows neutral to bullish momentum with support at $40k."

### Debug Mode (Technical):
**User:** "Hi"  
**Bot:**
```
💭 Thinking Process:
Engram Neural Analysis:
Signal: HOLD
Confidence: 0.82

📝 Response:
Hello! How can I assist you today?

🔧 Mode: 🧠 Engram + LMStudio
```

---

## Troubleshooting

### Bot not responding?
1. Check if LMStudio is running
2. Verify Telegram credentials
3. Check logs for errors

### Want to see technical details?
```powershell
$env:DEBUG_MODE="true"
python enhanced_engram_launcher.py
```

### ClawdBot not connecting?
The bot will automatically fall back to direct LMStudio connection. This is normal and works fine.

---

## Status

✅ Virtual environment activation documented  
✅ Response formatting cleaned up  
✅ ClawdBot configuration fixed  
✅ LMStudio direct connection working  
⚠️ ClawdBot WebSocket auth (known issue, has workaround)  

**The bot is fully functional and ready to use!**
