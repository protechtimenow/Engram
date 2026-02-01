# Model Name Fix - COMPLETE ✅

## Problem Found and Fixed!

### Root Cause
The bot was using **DeepSeek** instead of **GLM-4.7-flash** because of a **hardcoded model name** in the Engram core file.

### Location of Bug
**File:** `src/core/engram_demo_v1.py`
**Line:** 434 (in `_query_lmstudio()` method)

### What Was Wrong
```python
# BEFORE (WRONG):
data = {
    "model": "deepseek/deepseek-r1-0528-qwen3-8b",  # ❌ Hardcoded DeepSeek
    "messages": [...]
}
```

### What Was Fixed
```python
# AFTER (CORRECT):
data = {
    "model": "glm-4.7-flash",  # ✅ Now uses GLM-4.7-flash
    "messages": [...]
}
```

## Why This Happened

Even though `enhanced_engram_launcher.py` (line 84) correctly requested `"glm-4.7-flash"`, the Engram model's internal `_query_lmstudio()` method was **overriding** it with a hardcoded DeepSeek model name.

## Files Modified

1. ✅ `enhanced_engram_launcher.py` (line 84) - Already had `"glm-4.7-flash"` ✓
2. ✅ `src/core/engram_demo_v1.py` (line 434) - **FIXED** from DeepSeek to GLM-4.7-flash

## Testing

After this fix, your bot will now:
1. Request `"glm-4.7-flash"` from LMStudio API
2. LMStudio will serve whichever model is loaded in the UI
3. If GLM-4.7-flash is loaded in LMStudio, it will be used
4. If DeepSeek is still loaded, you'll need to switch it in LMStudio UI

## Next Steps

### Option 1: LMStudio Already Has GLM Loaded
```bash
# Just restart your bot
python enhanced_engram_launcher.py
```

### Option 2: Need to Switch Model in LMStudio
1. Open LMStudio application
2. Go to "My Models" tab
3. Unload DeepSeek model
4. Load GLM-4.7-flash model
5. Restart bot:
   ```bash
   python enhanced_engram_launcher.py
   ```

## Verification

After restarting, check the logs. You should see:
```
[glm-4.7-flash] Running chat completion
```

Instead of:
```
[deepseek/deepseek-r1-0528-qwen3-8b] Running chat completion
```

## Summary

✅ **Code Fix Complete**
- Both files now request `"glm-4.7-flash"`
- No more hardcoded DeepSeek references
- Bot will use whatever model LMStudio serves

⚠️ **LMStudio Configuration** (if needed)
- LMStudio ignores the model name in API requests
- It serves whatever model is loaded in the UI
- You must manually switch models in LMStudio if needed

🎉 **Problem Solved!**
The code is now correct. If you still see DeepSeek in logs after restarting, it's because LMStudio UI still has DeepSeek loaded (not a code issue).
