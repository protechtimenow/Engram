# How to Start Engram Bot with ClawdBot Gateway

## Prerequisites
1. LMStudio running on `http://100.118.172.23:1234`
2. ClawdBot application installed and configured

## Startup Steps

### Step 1: Start ClawdBot Gateway
You need to manually start ClawdBot first. Based on your configuration in `../.clawdbot/clawdbot.json`:

**ClawdBot should be running on:**
- WebSocket: `ws://127.0.0.1:18789`
- Auth Token: `2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc`
- Primary Model: `lmstudio/local-model` → `http://100.118.172.23:1234/v1`

**How to start ClawdBot:**
- Open your ClawdBot application
- Ensure it's configured to use the settings in `../.clawdbot/clawdbot.json`
- Start the gateway service
- Verify it's running on port 18789

### Step 2: Verify ClawdBot is Running
Test the connection:
```bash
curl http://127.0.0.1:18789/health
```

Or check if the WebSocket is accessible:
```bash
wscat -c ws://127.0.0.1:18789
```

### Step 3: Start Engram Bot
Once ClawdBot is confirmed running:

**Option A - Using the startup script (WSL/Git Bash):**
```bash
bash start_engram_with_clawdbot.sh
```

**Option B - Manual start:**
```bash
source .venv/Scripts/activate
python enhanced_engram_launcher.py
```

## Architecture Flow
```
Telegram Message
    ↓
Enhanced Engram Bot (enhanced_engram_launcher.py)
    ↓
Engram Neural Network (src/core/engram_demo_v1.py)
    ↓
ClawdBot Gateway (ws://127.0.0.1:18789)
    ↓
LMStudio (http://100.118.172.23:1234/v1)
    ↓
Response flows back through the chain
```

## Configuration Files

### ClawdBot Config: `../.clawdbot/clawdbot.json`
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "lmstudio/local-model"
      },
      "models": {
        "lmstudio/local-model": {
          "alias": "LMStudio Local",
          "baseURL": "http://100.118.172.23:1234/v1"
        }
      }
    }
  },
  "gateway": {
    "port": 18789,
    "bind": "loopback"
  }
}
```

### Engram Bot Config: `enhanced_engram_launcher.py`
```python
# Initialize Engram with ClawdBot integration
clawdbot_ws_url = os.getenv('CLAWDBOT_WS_URL', 'ws://127.0.0.1:18789')
self.engram_model = EngramModel(
    use_clawdbot=True,
    clawdbot_ws_url=clawdbot_ws_url
)
```

## Environment Variables (Optional)
You can override defaults with:
```bash
export CLAWDBOT_WS_URL="ws://127.0.0.1:18789"
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

## Troubleshooting

### Error: "ClawdBot not available"
**Cause:** ClawdBot gateway is not running or not accessible
**Solution:** 
1. Start ClawdBot application first
2. Verify it's listening on port 18789
3. Check firewall settings

### Error: "Connection refused"
**Cause:** Port 18789 is not open or ClawdBot not started
**Solution:**
1. Check if ClawdBot is running: `netstat -an | grep 18789`
2. Restart ClawdBot application

### Error: "LMStudio not responding"
**Cause:** LMStudio is not running or wrong URL
**Solution:**
1. Start LMStudio on `http://100.118.172.23:1234`
2. Verify with: `curl http://100.118.172.23:1234/v1/models`

## Testing the Setup

Once both services are running, test with Telegram:
```
/status  - Check bot status
/analyze BTC/USDT - Test market analysis
Hi - Test general chat
```

You should see responses with mode indicator: `🔧 Mode: 🧠 Engram + ClawdBot`
