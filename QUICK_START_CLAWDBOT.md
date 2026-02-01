# Quick Start Guide - Engram ClawdBot Integration

## Installation & Setup

### 1. Prerequisites

- Python 3.8+
- LMStudio running with a model loaded
- ClawdBot gateway running (optional)

### 2. Quick Start

```bash
# Navigate to Engram directory
cd c:/Users/OFFRSTAR0/Engram

# Run the integration
python engram_clawdbot_integration.py
```

## Available Commands

### Basic Commands

```
/help
```
Shows all available commands with examples.

```
/status
```
Displays bot health status, LMStudio connection, active alerts, and portfolio items.

### Trading Analysis

```
/analyze BTC/USD
```
Analyzes the specified trading pair and provides:
- Trading signal (BUY/SELL/HOLD)
- Confidence score
- Risk level
- Market analysis
- Actionable suggestions

**Examples:**
- `/analyze BTC/USD`
- `/analyze ETH/USD`
- `/analyze EUR/USD`

### Price Alerts

```
/alert BTC 50000
```
Sets a price alert for the specified symbol at the given price.

**Examples:**
- `/alert BTC 50000` - Alert when BTC reaches $50,000
- `/alert ETH 3000` - Alert when ETH reaches $3,000

```
/alerts
```
Lists all active price alerts grouped by symbol.

### Portfolio

```
/portfolio
```
Displays your portfolio summary including:
- Holdings for each asset
- Average purchase price
- Current value
- Total portfolio value

## Configuration

### Environment Variables

```bash
# LMStudio Configuration
export LMSTUDIO_HOST=localhost
export LMSTUDIO_PORT=1234
export ENGRAM_MODEL=glm-4.7-flash

# ClawdBot Configuration
export CLAWDBOT_HOST=localhost
export CLAWDBOT_PORT=18789

# Optional Settings
export ENGRAM_RESPONSE_FORMAT=clean  # clean, detailed, or raw
export LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
```

### Windows PowerShell

```powershell
$env:LMSTUDIO_HOST="localhost"
$env:LMSTUDIO_PORT="1234"
$env:CLAWDBOT_HOST="localhost"
$env:CLAWDBOT_PORT="18789"

python engram_clawdbot_integration.py
```

## Example Session

```
User: /help
Bot: [Engram Trading Bot - Commands]
     /help - Show this help message
     /status - Check bot status and health
     ...

User: /status
Bot: [Bot Status]
     Status: HEALTHY
     LMStudio: [OK]
     Tools: 4 registered
     Active Alerts: 0
     Portfolio Items: 2
     Uptime: Connected

User: /analyze BTC/USD
Bot: Signal: BUY
     Confidence: 0.75
     Timeframe: 4h
     Risk Level: MEDIUM
     
     Analysis:
     Bitcoin is showing strong bullish momentum...
     
     Suggestions:
     • Consider entering long position
     • Set stop loss at $44,500
     • Target price: $52,000

User: /alert BTC 50000
Bot: [OK] Price alert set for BTC at $50,000.00

User: /alerts
Bot: [Active Price Alerts]
     
     BTC:
       - $50,000.00 (set 2024-01-15)

User: /portfolio
Bot: [Portfolio Summary]
     
     BTC:
       Amount: 0.5
       Avg Price: $45,000.00
       Value: $22,500.00
     
     ETH:
       Amount: 2.0
       Avg Price: $2,800.00
       Value: $5,600.00
     
     Total Value: $28,100.00
```

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to ClawdBot gateway

**Solution:**
1. Ensure ClawdBot gateway is running: `clawdbot gateway`
2. Check the port is correct (default: 18789)
3. Verify no firewall blocking the connection

### LMStudio Issues

**Problem:** LMStudio connection failed

**Solution:**
1. Ensure LMStudio is running
2. Load a model in LMStudio
3. Check LMStudio is listening on the correct port (default: 1234)
4. Verify the model name matches your configuration

### Unicode Errors (Windows)

**Problem:** Seeing garbled characters or encoding errors

**Solution:**
The integration now includes automatic Windows encoding fixes. If issues persist:

```powershell
# Set console to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python engram_clawdbot_integration.py
```

### Command Not Working

**Problem:** Bot doesn't respond to commands

**Solution:**
1. Ensure command starts with `/`
2. Check command spelling (use `/help` to see all commands)
3. Verify bot is connected (check logs for `[OK] Connected to ClawdBot gateway`)

## Logs

Logs are saved to: `c:/Users/OFFRSTAR0/Engram/logs/engram.log`

View logs in real-time:
```bash
# Windows PowerShell
Get-Content logs/engram.log -Wait -Tail 50

# Linux/Mac
tail -f logs/engram.log
```

## Features

### ✓ Fixed Issues
- [OK] WebSocket 1008 error - Event messages now handled correctly
- [OK] Unicode logging - All emojis replaced with ASCII
- [OK] Windows compatibility - Console encoding fixed

### ✓ New Features
- [OK] 6 bot commands (/help, /status, /analyze, /alert, /alerts, /portfolio)
- [OK] Price alert tracking
- [OK] Portfolio management
- [OK] Command routing system

### ✓ Existing Features
- [OK] LMStudio integration with function calling
- [OK] Trading analysis tools
- [OK] Clean response formatting
- [OK] Automatic reconnection
- [OK] Health monitoring

## Advanced Usage

### Custom Response Format

```bash
# Clean format (default) - filters out reasoning
export ENGRAM_RESPONSE_FORMAT=clean

# Detailed format - includes timestamps
export ENGRAM_RESPONSE_FORMAT=detailed

# Raw format - shows everything including reasoning
export ENGRAM_RESPONSE_FORMAT=raw
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python engram_clawdbot_integration.py
```

### Running Without ClawdBot

The integration can run standalone with just LMStudio:

```bash
# LMStudio will be used directly
export LMSTUDIO_HOST=localhost
export LMSTUDIO_PORT=1234
python engram_clawdbot_integration.py
```

## Support

For issues or questions:
1. Check logs in `logs/engram.log`
2. Review `CLAWDBOT_INTEGRATION_FIX_SUMMARY.md` for detailed information
3. See `CRITICAL_FIXES_REQUIRED.md` for known issues

## Next Steps

1. Test all commands to ensure they work
2. Set up price alerts for your favorite trading pairs
3. Monitor your portfolio
4. Use `/analyze` for trading decisions

Happy Trading! 🚀
