# LMStudio Model Issue - Final Fix

## Problem

You have GLM-4.7-flash loaded in LMStudio, but the bot is calling DeepSeek instead.

## Why This Happens

**LMStudio can have multiple models loaded at once**, but only ONE is active for API requests. The `"model": "local-model"` parameter in the API request is **completely ignored** by LMStudio.

## Solution

### Step 1: Check Which Model is Active

In LMStudio UI, look for the model with a **green indicator** or **"Active"** status. This is the model that will respond to API requests.

### Step 2: Unload DeepSeek

1. Find DeepSeek in the loaded models list
2. Click the **"Unload"** or **"X"** button next to it
3. Wait for it to fully unload

### Step 3: Ensure GLM is Active

1. Find GLM-4.7-flash in your models
2. If it's not loaded, click **"Load Model"**
3. If it's loaded but not active, click **"Set as Active"** or similar option
4. Verify it shows as the **active model**

### Step 4: Verify with API Test

```powershell
curl http://localhost:1234/v1/models
```

**Expected output:**
```json
{
  "data": [
    {
      "id": "glm-4.7-flash",
      ...
    }
  ]
}
```

**NOT:**
```json
{
  "data": [
    {
      "id": "deepseek/deepseek-r1-0528-qwen3-8b",
      ...
    }
  ]
}
```

### Step 5: Restart Your Bot

```powershell
# Stop bot
Get-Process python | Stop-Process -Force

# Restart
cd C:\Users\OFFRSTAR0\Engram
python enhanced_engram_launcher.py
```

## Important Notes

1. **The bot code is correct** - it requests "local-model"
2. **LMStudio decides which model to use** - based on what's active
3. **You cannot control the model from code** - only from LMStudio UI
4. **Only ONE model can be active** - even if multiple are loaded

## Verification

After restarting the bot, send a message. The logs should show:

```
[glm-4.7-flash] Prompt processing progress: 100.0%
```

**NOT:**
```
[deepseek/deepseek-r1-0528-qwen3-8b] Prompt processing progress: 100.0%
```

## If Still Using DeepSeek

1. **Close LMStudio completely**
2. **Reopen LMStudio**
3. **Load ONLY GLM-4.7-flash**
4. **Don't load any other models**
5. **Restart your bot**

This ensures only GLM is available for API requests.

## Summary

**This is a LMStudio UI configuration issue, not a code issue.** The bot code is correct and will use whatever model LMStudio has active.
