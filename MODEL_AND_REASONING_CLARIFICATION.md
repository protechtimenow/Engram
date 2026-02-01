# Model & Reasoning Issues - Clarification

## Issue 1: DeepSeek Model Being Used

**What you're seeing:**
```
[deepseek/deepseek-r1-0528-qwen3-8b] Model generated tool calls: []
```

**Why this happens:**
- LMStudio uses **whatever model is currently loaded**
- The API request parameter `"model": "local-model"` is **ignored by LMStudio**
- This is **normal LMStudio behavior**, not a bug

**Solution:**
1. Open LMStudio application
2. Click "Unload Model" to unload DeepSeek
3. Load GLM-4.7-flash or GLM-4-9b-chat
4. Restart your bot

**The bot code is correct** - it's just a LMStudio configuration issue.

---

## Issue 2: Reasoning Content in Responses

**What you're seeing:**
Users receive responses with `reasoning_content` visible

**Current code status:**
The `enhanced_engram_launcher.py` **already filters reasoning** in production mode:

```python
# Line 520 - Production mode (DEBUG_MODE=false)
response = result['content']  # Only content, no reasoning
```

**Possible causes:**

### Cause A: DEBUG_MODE is Enabled
Check if DEBUG_MODE environment variable is set:
```powershell
echo $env:DEBUG_MODE
```

If it shows "true", disable it:
```powershell
$env:DEBUG_MODE = "false"
# Or remove it entirely
Remove-Item Env:DEBUG_MODE
```

### Cause B: Multiple Bots Running
You might have multiple bot instances running:
- `enhanced_engram_launcher.py` (correct, filters reasoning)
- Another bot instance (old code, shows reasoning)

**Check running processes:**
```powershell
Get-Process python | Where-Object {$_.CommandLine -like "*engram*"}
```

**Kill all Python processes:**
```powershell
Get-Process python | Stop-Process -Force
```

Then restart ONLY the enhanced launcher:
```powershell
cd C:\Users\OFFRSTAR0\Engram
$env:TELEGRAM_BOT_TOKEN = "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
$env:TELEGRAM_CHAT_ID = "1007321485"
$env:LMSTUDIO_URL = "http://100.118.172.23:1234"
$env:DEBUG_MODE = "false"  # Explicitly set to false
python enhanced_engram_launcher.py
```

### Cause C: Telegram Conflict
If ClawdBot's Telegram plugin is still enabled, it might be sending the responses with reasoning.

**Check ClawdBot config:**
```powershell
notepad C:\Users\OFFRSTAR0\.clawdbot\clawdbot.json
```

Ensure Telegram is disabled:
```json
{
  "channels": {
    "telegram": {
      "enabled": false  ← Must be false
    }
  }
}
```

---

## Quick Fix Steps

1. **Stop all bots:**
   ```powershell
   Get-Process python | Stop-Process -Force
   ```

2. **Disable ClawdBot Telegram (if needed):**
   ```powershell
   # Edit clawdbot.json and set telegram.enabled = false
   ```

3. **Restart ONLY enhanced launcher:**
   ```powershell
   cd C:\Users\OFFRSTAR0\Engram
   $env:TELEGRAM_BOT_TOKEN = "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
   $env:TELEGRAM_CHAT_ID = "1007321485"
   $env:LMSTUDIO_URL = "http://100.118.172.23:1234"
   $env:DEBUG_MODE = "false"
   python enhanced_engram_launcher.py
   ```

4. **Test with simple message:**
   Send "Hi" to your Telegram bot
   
   **Expected:** Clean greeting, no reasoning
   **Not expected:** Reasoning content visible

---

## Verification

After restarting, send `/status` to your bot.

**Expected response:**
```
🤖 Bot Status:

• Status: Running
• Time: 2026-02-01 22:XX:XX
• Engram Model: ✅ Loaded
• LMStudio: ✅ Connected
• Telegram: ✅ Connected
• AI Mode: LMStudio
```

**No reasoning should be visible in user responses!**

---

## Summary

1. **Model Issue:** Load GLM in LMStudio UI (not a code issue)
2. **Reasoning Issue:** Code already filters it - check for:
   - DEBUG_MODE=true
   - Multiple bot instances
   - ClawdBot Telegram conflict

**The code is correct** - it's a configuration/environment issue.
