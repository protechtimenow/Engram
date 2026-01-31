# 🔧 LMStudio Timeout Fix - Complete Implementation

## ✅ Issues Fixed

### 1. **Permanent LMStudio Disable After First Timeout** ✅ FIXED
**Problem:** After a single timeout, `lmstudio_available = False` was set permanently, forcing all future queries to use fallback mode.

**Solution:** Removed the permanent disable. Now each query attempt is independent - if one times out, the next query will still try LMStudio.

```python
# OLD (BAD):
except requests.exceptions.Timeout:
    logger.warning(f"LMStudio query timeout after {self.timeout}s - using fallback")
    self.lmstudio_available = False  # ❌ Permanent disable!
    return None

# NEW (GOOD):
except requests.exceptions.Timeout:
    logger.warning(f"⚠️ LMStudio query timeout after {self.timeout}s - using fallback for this request")
    # DO NOT permanently disable - just fall back for this request
    # self.lmstudio_available = False
    return None
```

### 2. **glm-4.7-flash Empty Content Response** ✅ FIXED
**Problem:** The model returns `content: ""` and puts actual text in `reasoning_content`, causing empty responses.

**Solution:** Check both `content` and `reasoning_content` fields:

```python
# Handle different response formats (especially glm-4.7-flash)
choice = (result.get("choices") or [{}])[0]
msg = choice.get("message") or {}

# Try content first, then reasoning_content (for glm-4.7-flash)
text = (msg.get("content") or "").strip()
if not text:
    text = (msg.get("reasoning_content") or "").strip()

if text:
    logger.info(f"✅ LMStudio response received ({len(text)} chars)")
    return text
else:
    logger.warning("⚠️ LMStudio returned empty response")
    return None
```

### 3. **Proper Connect/Read Timeout Separation** ✅ FIXED
**Problem:** Single timeout value applied to both connection and read, causing slow generations to be killed.

**Solution:** Use tuple `(connect_timeout, read_timeout)`:

```python
# Connection test: 5s connect, 10s read
timeout=(5, 10)

# Query: 5s connect, user-configured read timeout (default 180s)
timeout=(5, self.timeout)
```

### 4. **Default Timeout Too Short** ✅ FIXED
**Problem:** Default 10s timeout is too short for LLM generation.

**Solution:** Environment variable with sensible default:

```python
lmstudio_timeout = int(os.getenv('LMSTUDIO_TIMEOUT', '180'))  # 3 minutes default
```

---

## 🚀 How to Use the Fixed Launcher

### **Option 1: Set Environment Variables (Recommended)**

In PowerShell (Windows):
```powershell
# Set LMStudio configuration
$env:LMSTUDIO_URL="http://100.118.172.23:1234"
$env:LMSTUDIO_TIMEOUT="180"  # 3 minutes for slow generations

# Set Telegram credentials
$env:TELEGRAM_BOT_TOKEN="8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
$env:TELEGRAM_CHAT_ID="1007321485"

# Launch bot
python enhanced_engram_launcher.py
```

In Bash (Linux/WSL):
```bash
# Set LMStudio configuration
export LMSTUDIO_URL="http://100.118.172.23:1234"
export LMSTUDIO_TIMEOUT="180"  # 3 minutes for slow generations

# Set Telegram credentials
export TELEGRAM_BOT_TOKEN="8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
export TELEGRAM_CHAT_ID="1007321485"

# Launch bot
python3 enhanced_engram_launcher.py
```

### **Option 2: One-Line Launch (PowerShell)**

```powershell
$env:LMSTUDIO_URL="http://100.118.172.23:1234"; $env:LMSTUDIO_TIMEOUT="180"; $env:TELEGRAM_BOT_TOKEN="8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"; $env:TELEGRAM_CHAT_ID="1007321485"; python enhanced_engram_launcher.py
```

### **Option 3: Create Launch Script**

Create `launch_engram.ps1`:
```powershell
# Engram Bot Launcher
$env:LMSTUDIO_URL="http://100.118.172.23:1234"
$env:LMSTUDIO_TIMEOUT="180"
$env:TELEGRAM_BOT_TOKEN="8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
$env:TELEGRAM_CHAT_ID="1007321485"

Write-Host "🚀 Launching Enhanced Engram Bot..." -ForegroundColor Green
python enhanced_engram_launcher.py
```

Then run: `.\launch_engram.ps1`

---

## 🧪 Testing the Fix

### **Step 1: Verify LMStudio is Running**

```bash
curl http://100.118.172.23:1234/v1/models
```

Expected output:
```json
{
  "object": "list",
  "data": [...]
}
```

### **Step 2: Launch Bot with Verbose Logging**

```powershell
$env:LMSTUDIO_URL="http://100.118.172.23:1234"
$env:LMSTUDIO_TIMEOUT="180"
$env:TELEGRAM_BOT_TOKEN="8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
$env:TELEGRAM_CHAT_ID="1007321485"
python enhanced_engram_launcher.py
```

### **Step 3: Look for These Log Lines**

✅ **Success indicators:**
```
✅ LMStudio connected
✅ Telegram bot connected: Freqtrad3_bot
✅ All systems initialized successfully
🤖 Bot is running and listening for messages...
```

⚠️ **Warning indicators (non-fatal):**
```
⚠️ LMStudio connection timeout - using fallback AI
⚠️ Engram model not available: [error]
```

❌ **Error indicators (fatal):**
```
❌ Config file not found
❌ Missing Telegram credentials
❌ Telegram API error
❌ Initialization failed
```

### **Step 4: Send Test Message**

Send "hi" to your Telegram bot (@Freqtrad3_bot)

**Expected log output:**
```
📨 Processing: hi...
✅ LMStudio response received (XXX chars)
📤 Sent: [response preview]...
```

**If you see timeout:**
```
⚠️ LMStudio query timeout after 180s - using fallback for this request
Using fallback AI (mock mode)
📤 Sent: 🤖 Mock AI Response...
```

This is OK! The bot will try LMStudio again on the next message.

---

## 📊 What Changed in the Code

### **File: `enhanced_engram_launcher.py`**

#### **Change 1: Connection Test Timeout**
```python
# Line ~48
response = requests.get(
    f"{self.lmstudio_url}/v1/models",
    timeout=(5, 10)  # ✅ NEW: 5s connect, 10s read
)
```

#### **Change 2: Query Timeout**
```python
# Line ~74
response = requests.post(
    f"{self.lmstudio_url}/v1/chat/completions",
    json={...},
    timeout=(5, self.timeout)  # ✅ NEW: 5s connect, configurable read
)
```

#### **Change 3: Response Parsing**
```python
# Line ~84-95
# ✅ NEW: Handle glm-4.7-flash response format
choice = (result.get("choices") or [{}])[0]
msg = choice.get("message") or {}

# Try content first, then reasoning_content
text = (msg.get("content") or "").strip()
if not text:
    text = (msg.get("reasoning_content") or "").strip()

if text:
    logger.info(f"✅ LMStudio response received ({len(text)} chars)")
    return text
```

#### **Change 4: No Permanent Disable**
```python
# Line ~100-103
except requests.exceptions.Timeout:
    logger.warning(f"⚠️ LMStudio query timeout after {self.timeout}s - using fallback for this request")
    # ✅ NEW: DO NOT permanently disable
    # self.lmstudio_available = False  # ❌ REMOVED
    return None
```

#### **Change 5: Default Timeout**
```python
# Line ~218
lmstudio_timeout = int(os.getenv('LMSTUDIO_TIMEOUT', '180'))  # ✅ NEW: 180s default (was 10s)
```

---

## 🔍 Troubleshooting

### **Issue: Still getting timeouts after 10 seconds**

**Cause:** Environment variable not set before launching bot.

**Solution:** Set `LMSTUDIO_TIMEOUT` in the same shell session before running:
```powershell
$env:LMSTUDIO_TIMEOUT="180"
python enhanced_engram_launcher.py
```

### **Issue: LMStudio connected but responses are empty**

**Cause:** Model returns `reasoning_content` instead of `content`.

**Solution:** ✅ Already fixed! The code now checks both fields.

### **Issue: Bot uses fallback mode even though LMStudio is running**

**Cause:** Connection test failed during startup.

**Solution:** 
1. Verify LMStudio is accessible: `curl http://100.118.172.23:1234/v1/models`
2. Check firewall/network settings
3. Restart bot - it will retry connection

### **Issue: "LMStudio query timeout" on every message**

**Cause:** Model is too slow or timeout is too short.

**Solution:** Increase timeout:
```powershell
$env:LMSTUDIO_TIMEOUT="300"  # 5 minutes
```

Or use a faster model in LMStudio.

---

## 📈 Performance Expectations

| Timeout Setting | Use Case | Expected Behavior |
|----------------|----------|-------------------|
| 30s | Fast models (< 1B params) | Quick responses, may timeout on complex queries |
| 60s | Medium models (1-7B params) | Good balance for most use cases |
| 180s (default) | Large models (7B+ params) | Handles complex reasoning, slow generations |
| 300s+ | Very large models (13B+) | Maximum patience for detailed analysis |

**Recommended:** Start with 180s (default), adjust based on your model's performance.

---

## ✅ Verification Checklist

After launching the bot, verify:

- [ ] Log shows "✅ LMStudio connected"
- [ ] Log shows "✅ Telegram bot connected"
- [ ] Log shows "✅ All systems initialized successfully"
- [ ] Sending "hi" to bot triggers "📨 Processing: hi..."
- [ ] Log shows "✅ LMStudio response received" (not timeout)
- [ ] Bot responds with actual AI-generated text (not mock response)
- [ ] Subsequent messages also get LMStudio responses (not permanently disabled)

---

## 🎯 Summary

**What was broken:**
1. ❌ 10s default timeout too short for LLM generation
2. ❌ Single timeout killed slow generations
3. ❌ First timeout permanently disabled LMStudio
4. ❌ glm-4.7-flash responses appeared empty

**What is fixed:**
1. ✅ 180s default timeout (configurable via env var)
2. ✅ Separate connect (5s) and read (180s) timeouts
3. ✅ Timeouts only affect individual queries, not permanent
4. ✅ Handles both `content` and `reasoning_content` fields

**How to use:**
```powershell
$env:LMSTUDIO_URL="http://100.118.172.23:1234"
$env:LMSTUDIO_TIMEOUT="180"
$env:TELEGRAM_BOT_TOKEN="8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
$env:TELEGRAM_CHAT_ID="1007321485"
python enhanced_engram_launcher.py
```

**Expected result:** Bot connects to LMStudio, handles slow generations gracefully, and provides AI-powered responses via Telegram! 🚀
