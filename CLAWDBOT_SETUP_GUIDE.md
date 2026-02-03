# ClawdBot Gateway Setup Guide

Complete setup guide for running ClawdBot Gateway with Engram Bot.

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `start_clawdbot_engram.ps1` | Auto-start both ClawdBot and Engram Bot |
| `install_clawdbot_service.ps1` | Install ClawdBot as Windows Service |
| `test_clawdbot_connection.py` | Test ClawdBot connectivity |
| `CLAWDBOT_SETUP_GUIDE.md` | This guide |

---

## 🚀 Quick Start (Easiest Method)

### Step 1: Start Everything Automatically

```powershell
# Navigate to Engram directory
cd C:\Users\OFFRSTAR0\Engram

# Run the auto-start script (starts both ClawdBot and Engram)
.\start_clawdbot_engram.ps1
```

**What happens:**
1. Starts ClawdBot Gateway in background (port 18789)
2. Waits for it to be ready
3. Starts Engram Bot
4. Shows logs in real-time
5. Press `Ctrl+C` to stop both

### Step 2: Test the Connection

Open a **new PowerShell window**:

```powershell
cd C:\Users\OFFRSTAR0\Engram
python test_clawdbot_connection.py
```

Expected output:
```
[OK] Health endpoint responding (200 OK)
[OK] WebSocket connected successfully
[OK] Authentication successful
[OK] Message exchange successful
[OK] LMStudio is accessible
```

### Step 3: Chat with Your Bot

Open Telegram and message `@Freqtrad3_bot`:
- Type `/status` - Check system status
- Type `/analyze BTC/USD` - Get market analysis
- Type `Hello!` - General conversation

---

## 🪟 Option: Run as Windows Service (Background)

This runs ClawdBot automatically at Windows startup, even if you're not logged in.

### Install the Service (Run as Administrator!)

```powershell
# Open PowerShell as Administrator
# Right-click PowerShell → "Run as Administrator"

cd C:\Users\OFFRSTAR0\Engram
.\install_clawdbot_service.ps1
```

**What happens:**
- Creates Windows Service "ClawdBotGateway"
- Sets to start automatically at boot
- Starts the service immediately

### Manage the Service

```powershell
# Check status
.\install_clawdbot_service.ps1 -Status

# Start service
.\install_clawdbot_service.ps1 -Start

# Stop service
.\install_clawdbot_service.ps1 -Stop

# Restart service
.\install_clawdbot_service.ps1 -Restart

# Uninstall service
.\install_clawdbot_service.ps1 -Uninstall
```

### Alternative: Manual Service Commands

```powershell
# Check status
sc query ClawdBotGateway
Get-Service ClawdBotGateway

# Start/Stop
sc start ClawdBotGateway
sc stop ClawdBotGateway

# View logs
Get-Content C:\Users\OFFRSTAR0\Engram\logs\clawdbot_service.log -Tail 50 -Wait
```

---

## 🧪 Testing & Troubleshooting

### Run Connection Tests

```powershell
cd C:\Users\OFFRSTAR0\Engram

# Full test suite
python test_clawdbot_connection.py

# Expected results:
# - Health Check: PASS
# - WebSocket Connection: PASS
# - Authentication: PASS
# - Message Exchange: PASS
# - Ping/Pong: PASS
# - LMStudio Integration: PASS
```

### Common Issues & Fixes

#### Issue 1: "Connection refused"
**Cause:** ClawdBot Gateway not running
```powershell
# Fix: Start ClawdBot manually
cd C:\Users\OFFRSTAR0\.clawdbot
.\gateway.cmd
```

#### Issue 2: "Port 18789 already in use"
**Cause:** Another instance is running
```powershell
# Find and kill the process
Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force

# Or use the script
.\start_clawdbot_engram.ps1
```

#### Issue 3: "WebSocket handshake failed"
**Cause:** Authentication or protocol mismatch
- Check auth token in `.clawdbot/clawdbot.json`
- Ensure using correct subprotocol: `clawdbot-v1`

#### Issue 4: "LMStudio not accessible"
**Cause:** LMStudio not running or wrong IP
```powershell
# Test LMStudio
curl http://100.118.172.23:1234/v1/models

# If no response, check LMStudio is running and server is enabled
```

### View Logs

```powershell
# ClawdBot Gateway logs
Get-Content C:\Users\OFFRSTAR0\Engram\logs\clawdbot_gateway.log -Tail 50 -Wait

# Engram Bot logs
Get-Content C:\Users\OFFRSTAR0\Engram\logs\engram_bot.log -Tail 50 -Wait

# Service logs
Get-Content C:\Users\OFFRSTAR0\Engram\logs\clawdbot_service.log -Tail 50 -Wait
```

---

## 📊 Architecture Overview

### With ClawdBot Gateway (Full Setup)
```
┌──────────────┐      WebSocket       ┌──────────────────┐      HTTP       ┌──────────────┐
│   Telegram   │◄────────────────────►│  ClawdBot        │◄───────────────►│   LMStudio   │
│    User      │                      │  Gateway         │                 │  (AI Model)  │
└──────────────┘                      │  (Port 18789)    │                 └──────────────┘
                                      └──────────────────┘
                                                ▲
                                                │ WebSocket
                                       ┌────────┴─────────┐
                                       │   Engram Bot     │
                                       │  (This project)  │
                                       └──────────────────┘
```

### Without ClawdBot (Fallback Mode)
```
┌──────────────┐                      ┌──────────────────┐      HTTP       ┌──────────────┐
│   Telegram   │◄────────────────────►│   Engram Bot     │◄───────────────►│   LMStudio   │
│    User      │                      │  (Direct Mode)   │                 │  (AI Model)  │
└──────────────┘                      └──────────────────┘                 └──────────────┘
```

---

## 🎛️ Advanced Options

### Debug Mode

```powershell
# Enable debug output (shows reasoning, technical details)
.\start_clawdbot_engram.ps1 -DebugMode
```

### Skip ClawdBot (LMStudio Direct Only)

```powershell
# Run without ClawdBot gateway
.\start_clawdbot_engram.ps1 -NoClawdBot
```

### Custom Port

```powershell
# Use different port for ClawdBot
.\start_clawdbot_engram.ps1 -ClawdBotPort 18888
```

---

## 🔒 Security Notes

- **Auth Token:** Stored in `C:\Users\OFFRSTAR0\.clawdbot\clawdbot.json`
- **Token:** `2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc`
- **Port:** 18789 (local only, not exposed to internet)
- **Logs:** May contain message content - review before sharing

---

## 📞 Quick Reference

### Start Everything
```powershell
cd C:\Users\OFFRSTAR0\Engram
.\start_clawdbot_engram.ps1
```

### Test Connection
```powershell
python test_clawdbot_connection.py
```

### Check Status
```powershell
.\install_clawdbot_service.ps1 -Status
```

### View Logs
```powershell
# Real-time log viewer
Get-Content logs\engram_bot.log -Wait -Tail 20
```

### Stop Everything
```powershell
# If running interactively, press Ctrl+C

# If running as service
.\install_clawdbot_service.ps1 -Stop
```

---

## ✅ Verification Checklist

- [ ] ClawdBot Gateway starts without errors
- [ ] Engram Bot connects to ClawdBot
- [ ] Test suite passes all checks
- [ ] Telegram bot responds to `/status`
- [ ] Telegram bot responds to messages
- [ ] LMStudio integration working

---

## 🆘 Still Having Issues?

1. **Check all services are running:**
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -match "node|python"}
   ```

2. **Verify ports are listening:**
   ```powershell
   Get-NetTCPConnection -LocalPort 18789,1234
   ```

3. **Review error logs:**
   ```powershell
   Get-ChildItem logs\*.log | Get-Content -Tail 20
   ```

4. **Restart everything:**
   ```powershell
   # Stop all
   Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force
   
   # Start fresh
   .\start_clawdbot_engram.ps1
   ```

---

**Your ClawdBot + Engram setup is ready! 🚀**
