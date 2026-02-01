# LMStudio Context Window Fix

## Problem

The error `Cannot truncate prompt with n_keep (656) >= n_ctx (256)` means LMStudio's model is configured with a **256-token context window**, which is too small for our prompts.

## Root Cause

The `n_ctx` parameter in the API request is **ignored by LMStudio**. The context window must be configured in **LMStudio's UI settings**, not via API.

## Solution

### Option 1: Increase Context Window in LMStudio (RECOMMENDED)

1. **Open LMStudio Application**
2. **Go to Model Settings** (gear icon or settings tab)
3. **Find "Context Length" or "n_ctx" setting**
4. **Change from 256 to 4096 or higher**
5. **Reload the model** (unload and load again)
6. **Restart the bot**: `python start_engram_bot.py`

### Option 2: Use a Different Model

Some models have larger default context windows:

1. In LMStudio, load a model with larger context (e.g., 4096+)
2. Update `config/engram_config.json`:
   ```json
   {
     "lmstudio": {
       "model": "your-new-model-name"
     }
   }
   ```
3. Restart the bot

### Option 3: Reduce Prompt Size (TEMPORARY WORKAROUND)

If you can't change LMStudio settings, we can reduce the system prompt:

**Edit `skills/engram/engram_skill.py`:**

Find the `_build_system_prompt()` method and replace with:

```python
def _build_system_prompt(self) -> str:
    """Build system prompt for Engram"""
    return """You are Engram, a trading assistant.

Provide:
- Signal: BUY/SELL/HOLD
- Confidence: 0-1
- Risk: LOW/MED/HIGH
- Brief analysis

Be concise."""
```

This reduces the prompt from ~400 tokens to ~50 tokens.

## Verification

After applying the fix, test with:

```bash
python start_engram_bot.py
```

Send `/status` command in Telegram. You should see:
- No "Cannot truncate prompt" errors
- Bot responds successfully

## Current Status

**LMStudio Configuration:**
- Host: 100.118.172.23:1234
- Model: glm-4.7-flash
- Current Context: 256 tokens ❌
- Required Context: 4096+ tokens ✅

**Bot Status:**
- Telegram: Connected ✅
- LMStudio: Connected ✅
- Commands: Working (except analysis due to context limit) ⚠️

## Recommended Action

**Increase LMStudio's context window to 4096 tokens in the LMStudio UI.**

This is the proper fix and will allow all features to work correctly.

## Alternative: Simplified Bot

If you cannot change LMStudio settings, I can create a simplified version that works with 256 tokens:

- Shorter prompts
- No tool calling
- Direct responses only
- Basic analysis

Let me know if you need this version!
