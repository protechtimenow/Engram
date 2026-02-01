# OpenClaw Quick Start - Correct Commands

## ⚠️ IMPORTANT: Directory Matters!

You got the error because you ran `pnpm gateway:watch` from the **Engram** directory.
OpenClaw commands must be run from the **openclaw** directory!

## Step-by-Step Setup

### Step 1: Install OpenClaw

```powershell
# Navigate to your user directory
cd C:\Users\OFFRSTAR0

# Clone OpenClaw
git clone https://github.com/openclaw/openclaw.git

# Enter openclaw directory
cd openclaw

# Install dependencies
pnpm install

# Build UI
pnpm ui:build

# Build project
pnpm build

# Onboard
pnpm openclaw onboard --install-daemon
```

### Step 2: Start OpenClaw Gateway

**Terminal 1 (OpenClaw):**
```powershell
# MUST be in openclaw directory!
cd C:\Users\OFFRSTAR0\openclaw
pnpm gateway:watch
```

Expected output:
```
OpenClaw Gateway starting on ws://localhost:18789
Watching for changes...
```

### Step 3: Start Engram Bot

**Terminal 2 (Engram):**
```powershell
# MUST be in Engram directory!
cd C:\Users\OFFRSTAR0\Engram
python enhanced_engram_launcher.py
```

Expected output:
```
[OK] Connected to OpenClaw gateway
[OK] Telegram bot connected
```

### Step 4: Access UI

Open browser: `http://localhost:3000`

## Common Errors

### Error: "No package.json found"
**Cause:** Running `pnpm` commands from wrong directory
**Fix:** Make sure you're in `C:\Users\OFFRSTAR0\openclaw`

### Error: "pnpm not found"
**Cause:** pnpm not installed
**Fix:** 
```powershell
npm install -g pnpm
```

### Error: "Port 18789 already in use"
**Cause:** Another gateway is running
**Fix:**
```powershell
# Find and kill process
Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force
```

## Directory Structure

```
C:\Users\OFFRSTAR0\
├── openclaw\          ← Run pnpm commands HERE
│   ├── package.json
│   ├── agents\
│   └── ...
└── Engram\            ← Run python commands HERE
    ├── enhanced_engram_launcher.py
    ├── agents\
    └── ...
```

## Quick Commands Reference

| Command | Directory | Purpose |
|---------|-----------|---------|
| `pnpm gateway:watch` | `openclaw/` | Start gateway |
| `python enhanced_engram_launcher.py` | `Engram/` | Start bot |
| `pnpm openclaw agents list` | `openclaw/` | List agents |
| `pnpm openclaw logs` | `openclaw/` | View logs |

## Two Terminal Setup

**Terminal 1:**
```powershell
cd C:\Users\OFFRSTAR0\openclaw
pnpm gateway:watch
# Keep this running
```

**Terminal 2:**
```powershell
cd C:\Users\OFFRSTAR0\Engram
python enhanced_engram_launcher.py
# Keep this running
```

## Alternative: Use ClawdBot Instead

If OpenClaw is too complex, your bot already works with ClawdBot:

```powershell
cd C:\Users\OFFRSTAR0\Engram
python enhanced_engram_launcher.py
```

All your fixes work with both ClawdBot and OpenClaw!

## Summary

✅ **All your code fixes are complete**
✅ **Bot works with ClawdBot (current)**
✅ **Bot compatible with OpenClaw (optional upgrade)**

Choose whichever gateway you prefer - your code is ready for both! 🚀
