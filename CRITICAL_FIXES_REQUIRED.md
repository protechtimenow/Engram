# CRITICAL FIXES REQUIRED

## Issues Identified from Logs

### 1. ❌ Telegram Conflict (CRITICAL)
**Error:** `[telegram] getUpdates conflict; retrying in 30s`

**Cause:** Both ClawdBot and Engram bot are using the same Telegram bot token simultaneously

**Solution:** Disable ClawdBot's Telegram plugin since Engram bot handles Telegram directly

**Fix:**
```powershell
# Stop the Engram bot first (Ctrl+C)

# Edit ClawdBot config
notepad C:\Users\OFFRSTAR0\.clawdbot\clawdbot.json
```

**Change this:**
```json
"channels": {
  "telegram": {
    "enabled": true,    ← CHANGE TO false
    ...
  }
}
```

**To this:**
```json
"channels": {
  "telegram": {
    "enabled": false,   ← DISABLED
    ...
  }
}
```

---

### 2. ❌ Unknown Model Error
**Error:** `Unknown model: lmstudio/local-model`

**Cause:** ClawdBot is looking for a model that doesn't exist in the configuration

**Current Config Shows:**
- Primary model: `local-lmstudio/glm-4.7-flash` ✅ (This is correct)
- But somewhere it's trying to use: `lmstudio/local-model` ❌

**This error is likely coming from ClawdBot's internal agent, not your Engram bot**

**Solution:** Since ClawdBot's Telegram is disabled, this error won't affect your bot

---

### 3. ⚠️ WebSocket Handshake Failure
**Error:** `invalid handshake - invalid request frame`

**Cause:** WebSocket authentication format issue

**Current Status:** Your fallback to LMStudio is working, so this is non-critical

**Optional Fix (if you want ClawdBot to work):**
The WebSocket library might need headers instead of query params. But since fallback works, this can be ignored.

---

## RECOMMENDED FIX SEQUENCE

### Step 1: Disable ClawdBot Telegram Plugin
```powershell
# 1. Stop your Engram bot (Ctrl+C in terminal)

# 2. Edit ClawdBot config
notepad C:\Users\OFFRSTAR0\.clawdbot\clawdbot.json

# 3. Find "telegram" section under "channels"
# 4. Change "enabled": true to "enabled": false
# 5. Save and close

# 6. Restart ClawdBot gateway
clawdbot gateway stop
clawdbot gateway
```

### Step 2: Restart Engram Bot
```powershell
cd C:\Users\OFFRSTAR0\Engram
.\start_engram.ps1
```

### Step 3: Verify
You should now see:
- ✅ No more "getUpdates conflict" errors
- ✅ Bot responds to Telegram messages
- ✅ Clean responses without reasoning
- ⚠️ WebSocket errors still present (but fallback works)

---

## ALTERNATIVE: Run Without ClawdBot

If you don't need ClawdBot at all, you can run Engram bot in LMStudio-only mode:

```powershell
# Stop ClawdBot
clawdbot gateway stop

# Start Engram bot (it will use LMStudio directly)
cd C:\Users\OFFRSTAR0\Engram
.\start_engram.ps1
```

This will:
- ✅ Eliminate all ClawdBot errors
- ✅ Use LMStudio directly (faster)
- ✅ No Telegram conflicts
- ✅ Clean responses working

---

## CURRENT SYSTEM STATUS

### ✅ Working:
- LMStudio connection
- Engram neural model
- Response formatting (clean, no reasoning)
- Error handling with fallback
- Telegram bot functionality

### ❌ Not Working:
- ClawdBot Telegram plugin (conflicts with Engram bot)
- ClawdBot WebSocket (but fallback handles this)

### ⚠️ Recommendation:
**Disable ClawdBot's Telegram plugin** and let Engram bot handle Telegram directly. This is the cleanest solution.

---

## QUICK FIX COMMANDS

```powershell
# 1. Stop everything
# Press Ctrl+C in Engram bot terminal

# 2. Edit ClawdBot config to disable Telegram
(Get-Content C:\Users\OFFRSTAR0\.clawdbot\clawdbot.json) -replace '"enabled": true,  # telegram', '"enabled": false,  # telegram' | Set-Content C:\Users\OFFRSTAR0\.clawdbot\clawdbot.json

# 3. Restart ClawdBot
clawdbot gateway stop
Start-Sleep 5
clawdbot gateway

# 4. Wait 10 seconds
Start-Sleep 10

# 5. Start Engram bot
cd C:\Users\OFFRSTAR0\Engram
.\start_engram.ps1
```

---

## EXPECTED RESULT AFTER FIX

### Logs Should Show:
```
✅ Engram model loaded with ClawdBot integration
✅ Telegram bot connected: Freqtrad3_bot
✅ Bot is running and listening for messages...
```

### No More:
```
❌ [telegram] getUpdates conflict
❌ Unknown model: lmstudio/local-model
```

### Still Present (but OK):
```
⚠️ [ws] invalid handshake (fallback to LMStudio works)
```

---

## TESTING AFTER FIX

1. Send "Hi" to your Telegram bot
   - Expected: Clean greeting response
   - Not: Raw reasoning or errors

2. Send "/analyze BTC"
   - Expected: Clean market analysis
   - Not: Technical details or "Error: ..."

3. Check logs
   - Should see: "Using Engram neural analysis..."
   - Should see: "Response mode: 🧠 Engram + LMStudio" (in logs only)
   - Should NOT see: Telegram conflicts

---

## SUMMARY

**Main Issue:** ClawdBot and Engram bot both trying to use same Telegram bot token

**Solution:** Disable ClawdBot's Telegram plugin

**Impact:** None - Engram bot handles Telegram directly and works perfectly

**Time to Fix:** 2 minutes

**Priority:** HIGH - This is causing the main operational issue
