# LMStudio Configuration Guide for Engram Trading Bot

## Overview

This guide explains how to configure and troubleshoot LMStudio integration with the Engram Trading Bot, including timeout handling, retry logic, and fallback mechanisms.

## Table of Contents

1. [LMStudio Setup](#lmstudio-setup)
2. [Network Configuration](#network-configuration)
3. [Timeout Issues](#timeout-issues)
4. [Enhanced Launcher Features](#enhanced-launcher-features)
5. [Troubleshooting](#troubleshooting)
6. [Testing](#testing)

---

## LMStudio Setup

### Prerequisites

- **LMStudio** installed and running
- **GLM-4.7-flash** model loaded
- **API endpoint** accessible at `http://192.168.56.1:1234`

### Correct API Endpoint

The Engram bot uses the **custom endpoint** for LMStudio:

```
POST http://192.168.56.1:1234/api/v1/chat
```

**Request Format:**
```json
{
  "model": "GLM-4.7-flash",
  "system_prompt": "You are a helpful trading assistant.",
  "input": "Your prompt here"
}
```

**Response Format:**
```json
{
  "response": "AI generated response text",
  "model": "GLM-4.7-flash",
  "timestamp": "2026-01-31T03:00:00Z"
}
```

### Testing LMStudio Connectivity

```bash
# Test basic connectivity
curl -X POST http://192.168.56.1:1234/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "GLM-4.7-flash",
    "system_prompt": "You are a helpful assistant.",
    "input": "test"
  }' \
  --max-time 10
```

---

## Network Configuration

### Common Network Issues

1. **Sandbox Environment Isolation**
   - Sandbox environments (like Vercel) cannot access local network addresses (192.168.x.x)
   - LMStudio must be accessible from the deployment environment

2. **VirtualBox Host-Only Network**
   - `192.168.56.1` is typically a VirtualBox host-only adapter
   - Only accessible from VMs on the same host-only network
   - Not accessible from external servers or cloud environments

3. **Firewall Rules**
   - Ensure port 1234 is open on the LMStudio host
   - Check Windows Firewall / Linux iptables rules
   - Verify LMStudio is listening on `0.0.0.0:1234` not `127.0.0.1:1234`

### Solutions

**Option 1: Use Public IP or Domain**
```python
# Instead of local IP
lmstudio_url = "http://192.168.56.1:1234"

# Use public IP or domain
lmstudio_url = "http://your-public-ip:1234"
# or
lmstudio_url = "https://your-domain.com/lmstudio"
```

**Option 2: Deploy Bot on Same Network**
- Run the bot on the same machine as LMStudio
- Or run on a VM in the same VirtualBox host-only network

**Option 3: Use Fallback AI (Recommended for Testing)**
- The enhanced launcher automatically falls back to rule-based AI
- No LMStudio required for basic functionality

---

## Timeout Issues

### Root Causes

1. **Network Unreachable**
   - LMStudio server not accessible from bot environment
   - Error: `Connection refused` or `Network unreachable`

2. **Slow Model Inference**
   - GLM-4.7-flash taking >30s to generate response
   - Complex prompts or long context windows

3. **Server Overload**
   - LMStudio handling multiple requests
   - Insufficient GPU/CPU resources

### Enhanced Timeout Handling

The **Enhanced Launcher V2** (`enhanced_engram_launcher_v2.py`) includes:

#### 1. Configurable Timeouts
```python
client = LMStudioClient(
    base_url="http://192.168.56.1:1234",
    timeout=60,        # Initial timeout: 60 seconds
    max_retries=3      # Retry up to 3 times
)
```

#### 2. Exponential Backoff
```python
# Attempt 1: 60s timeout
# Attempt 2: 120s timeout (60 * 2^1)
# Attempt 3: 240s timeout (60 * 2^2)
```

#### 3. Retry Logic
```python
for attempt in range(max_retries):
    try:
        response = requests.post(url, json=data, timeout=current_timeout)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.Timeout:
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            time.sleep(wait_time)
            continue
```

---

## Enhanced Launcher Features

### Key Improvements

1. **Robust Error Handling**
   - Catches all connection errors gracefully
   - Never crashes on LMStudio failures
   - Logs detailed error information

2. **Intelligent Fallback**
   - Automatically switches to Mock AI when LMStudio unavailable
   - Seamless user experience
   - No manual intervention required

3. **Mock AI Analyzer**
   - Rule-based trading analysis
   - Generates realistic BUY/SELL/HOLD signals
   - Handles general chat queries

4. **Enhanced Logging**
   - Detailed connection status
   - Retry attempt tracking
   - Performance metrics

### Usage

```bash
# Run enhanced launcher
python3 enhanced_engram_launcher_v2.py
```

**Expected Output:**
```
================================================================================
ENHANCED ENGRAM BOT LAUNCHER V2
================================================================================
🚀 Initializing Enhanced Engram Bot...
✅ Telegram credentials loaded (chat_id: 1007321485)
🔌 Initializing LMStudio client...
⚠️  LMStudio not available - using fallback AI
📱 Testing Telegram connection...
✅ Telegram bot connected: @Freqtrad3_bot
✅ All systems initialized successfully
================================================================================
🤖 Bot is running and listening for messages...
📱 Send a message to your Telegram bot to test it!
================================================================================
```

---

## Troubleshooting

### Issue 1: Connection Timeout

**Symptoms:**
```
HTTPConnectionPool(host='192.168.56.1', port=1234): Read timed out. (read timeout=30)
```

**Solutions:**

1. **Increase Timeout**
   ```python
   # In enhanced_engram_launcher_v2.py
   self.lmstudio = LMStudioClient(
       base_url="http://192.168.56.1:1234",
       timeout=120,  # Increase to 120 seconds
       max_retries=3
   )
   ```

2. **Check LMStudio Status**
   ```bash
   # Test connectivity
   curl -v http://192.168.56.1:1234/api/v1/chat
   
   # Check if port is open
   telnet 192.168.56.1 1234
   ```

3. **Use Fallback AI**
   - Enhanced launcher automatically uses fallback
   - No configuration needed

### Issue 2: Connection Refused

**Symptoms:**
```
Failed to connect to 192.168.56.1 port 1234: Connection refused
```

**Solutions:**

1. **Verify LMStudio is Running**
   - Check LMStudio application is open
   - Verify model is loaded
   - Ensure API server is started

2. **Check Network Accessibility**
   ```bash
   # From bot environment
   ping 192.168.56.1
   
   # Test port
   nc -zv 192.168.56.1 1234
   ```

3. **Update LMStudio URL**
   ```python
   # Use localhost if on same machine
   lmstudio_url = "http://localhost:1234"
   
   # Or use public IP
   lmstudio_url = "http://your-public-ip:1234"
   ```

### Issue 3: Slow Responses

**Symptoms:**
- Responses taking >30 seconds
- Frequent timeouts on complex queries

**Solutions:**

1. **Optimize Model Settings**
   - Reduce `max_tokens` in request
   - Lower `temperature` for faster inference
   - Use smaller context window

2. **Upgrade Hardware**
   - Use GPU acceleration
   - Increase RAM allocation
   - Use faster CPU

3. **Implement Caching**
   - Cache common queries
   - Use response templates
   - Pre-generate frequent responses

---

## Testing

### Test LMStudio Integration

```bash
# Run test suite
python3 test_enhanced_launcher.py
```

**Expected Results:**
- ✅ Import Validation
- ✅ Configuration Loading
- ✅ LMStudio Client Init
- ✅ Mock AI Analyzer
- ✅ Retry Logic
- ✅ Fallback Mechanism

### Manual Testing

1. **Test LMStudio Endpoint**
   ```bash
   curl -X POST http://192.168.56.1:1234/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{
       "model": "GLM-4.7-flash",
       "system_prompt": "You are a trading assistant.",
       "input": "Analyze BTC/USDT"
     }'
   ```

2. **Test Bot with Telegram**
   ```bash
   # Start bot
   python3 enhanced_engram_launcher_v2.py
   
   # Send message to @Freqtrad3_bot
   /analyze BTC
   ```

3. **Test Fallback Mechanism**
   ```bash
   # Stop LMStudio
   # Bot should automatically use Mock AI
   # Send message to bot - should still respond
   ```

---

## Configuration Reference

### Environment Variables (Optional)

```bash
# Set LMStudio URL
export LMSTUDIO_URL="http://192.168.56.1:1234"

# Set timeout
export LMSTUDIO_TIMEOUT=60

# Set max retries
export LMSTUDIO_MAX_RETRIES=3

# Enable/disable LMStudio
export LMSTUDIO_ENABLED=true
```

### Config File (config/telegram/working_telegram_config.json)

```json
{
  "telegram": {
    "bot_token": "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA",
    "chat_id": "1007321485"
  },
  "lmstudio": {
    "enabled": true,
    "url": "http://192.168.56.1:1234",
    "endpoint": "/api/v1/chat",
    "model": "GLM-4.7-flash",
    "timeout": 60,
    "max_retries": 3
  },
  "fallback": {
    "enabled": true,
    "type": "mock_ai"
  }
}
```

---

## Best Practices

1. **Always Use Enhanced Launcher**
   - Includes retry logic and fallback
   - Better error handling
   - Production-ready

2. **Monitor LMStudio Performance**
   - Track response times
   - Monitor timeout rates
   - Adjust timeouts based on metrics

3. **Test Fallback Regularly**
   - Ensure Mock AI is working
   - Verify user experience without LMStudio
   - Test all command types

4. **Use Appropriate Timeouts**
   - Short queries: 30-60s
   - Complex analysis: 60-120s
   - Long conversations: 120-240s

5. **Implement Graceful Degradation**
   - LMStudio unavailable → Mock AI
   - Mock AI fails → Simple responses
   - All fails → Error message with retry

---

## Summary

The Enhanced Engram Launcher V2 provides:

✅ **Robust LMStudio Integration** with retry logic and exponential backoff
✅ **Intelligent Fallback** to Mock AI when LMStudio unavailable
✅ **Configurable Timeouts** for different query types
✅ **Comprehensive Error Handling** for all failure scenarios
✅ **Production-Ready** deployment with 24/7 reliability

**Recommended Setup:**
- Use Enhanced Launcher V2 for all deployments
- Configure appropriate timeouts (60-120s)
- Enable fallback AI for reliability
- Monitor LMStudio connectivity
- Test regularly with both LMStudio and fallback

**For Production:**
- Deploy LMStudio on accessible server (not 192.168.x.x)
- Use public IP or domain name
- Implement load balancing for multiple LMStudio instances
- Set up monitoring and alerting
- Keep fallback AI always enabled

---

## Support

For issues or questions:
1. Check bot status: `/status` command
2. Review logs: `logs/bot_runner.log`
3. Test LMStudio: `curl` commands above
4. Verify network: `ping` and `telnet` tests
5. Use fallback: Enhanced launcher handles automatically

**Status Indicators:**
- 🟢 LMStudio Connected
- 🔴 LMStudio Offline (using fallback)
- ⚠️  Partial connectivity (retrying)

---

*Last Updated: 2026-01-31*
*Version: 2.0*
*Author: Engram Trading Bot Team*
