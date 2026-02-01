# Engram-ClawdBot Integration Setup Guide

Complete guide for setting up and troubleshooting the Engram-ClawdBot integration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Integration](#running-the-integration)
5. [Troubleshooting](#troubleshooting)
6. [Testing](#testing)
7. [Advanced Configuration](#advanced-configuration)

## Prerequisites

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- Network access to LMStudio and ClawdBot gateway

### Required Services
1. **LMStudio** - Running locally or remotely
2. **ClawdBot Gateway** - Running and accessible
3. **Model** - glm-4.7-flash or compatible model loaded in LMStudio

### Python Dependencies
```bash
pip install websockets>=12.0 aiohttp>=3.9.0
```

For testing:
```bash
pip install pytest>=7.4.0 pytest-asyncio>=0.21.0
```

## Installation

### Step 1: Clone/Download Integration Files

Ensure you have the following directory structure:
```
your-project/
├── skills/engram/
├── agents/
├── config/
├── tests/
├── docs/
└── engram_clawdbot_integration.py
```

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/Mac/WSL:
source .venv/bin/activate

# Install dependencies
pip install websockets aiohttp
```

### Step 3: Verify LMStudio

```bash
# Check if LMStudio is running
curl http://localhost:1234/v1/models

# Expected response: JSON with available models
```

### Step 4: Verify ClawdBot Gateway

```bash
# Check if ClawdBot is running
# (Adjust host/port as needed)
curl http://localhost:18789/health

# Or check WebSocket endpoint
wscat -c ws://localhost:18789/ws
```

## Configuration

### Method 1: Environment Variables (Recommended)

Create a `.env` file or export variables:

```bash
# LMStudio Configuration
export LMSTUDIO_HOST=localhost
export LMSTUDIO_PORT=1234
export ENGRAM_MODEL=glm-4.7-flash

# ClawdBot Gateway Configuration
export CLAWDBOT_HOST=localhost
export CLAWDBOT_PORT=18789
export CLAWDBOT_TOKEN=your_auth_token_here

# Agent Configuration
export ENGRAM_RESPONSE_FORMAT=clean  # clean, detailed, or raw
export LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Method 2: Configuration File

Edit `config/engram_config.json`:

```json
{
  "lmstudio": {
    "host": "localhost",
    "port": 1234,
    "model": "glm-4.7-flash"
  },
  "clawdbot": {
    "host": "localhost",
    "port": 18789,
    "token": "your_token_here"
  },
  "agent": {
    "response_format": "clean"
  }
}
```

**Note**: Environment variables override config file settings.

## Running the Integration

### Basic Usage

```bash
python engram_clawdbot_integration.py
```

### With Custom Configuration

```bash
# Set environment variables
export LMSTUDIO_HOST=192.168.1.100
export LMSTUDIO_PORT=1234
export CLAWDBOT_HOST=192.168.1.101
export CLAWDBOT_PORT=18789

# Run
python engram_clawdbot_integration.py
```

### Expected Output

```
============================================================
Engram-ClawdBot Integration Starting
============================================================
2024-01-15 10:30:45 - __main__ - INFO - Configuration:
2024-01-15 10:30:45 - __main__ - INFO -   LMStudio: localhost:1234
2024-01-15 10:30:45 - __main__ - INFO -   Model: glm-4.7-flash
2024-01-15 10:30:45 - __main__ - INFO -   ClawdBot Gateway: localhost:18789
2024-01-15 10:30:45 - __main__ - INFO -   Response Format: clean
2024-01-15 10:30:45 - __main__ - INFO - Starting Engram agent...
2024-01-15 10:30:45 - engram_agent - INFO - Connected to ClawdBot gateway: ws://localhost:18789/ws
2024-01-15 10:30:45 - engram_agent - INFO - Sent hello message to gateway
```

### Stopping the Integration

Press `Ctrl+C` to gracefully shutdown:

```
^C2024-01-15 10:35:20 - __main__ - INFO - Received shutdown signal (Ctrl+C)
2024-01-15 10:35:20 - __main__ - INFO - Shutting down...
2024-01-15 10:35:20 - engram_agent - INFO - Shutting down Engram agent...
2024-01-15 10:35:20 - engram_agent - INFO - Engram agent shutdown complete
2024-01-15 10:35:20 - __main__ - INFO - Shutdown complete
```

## Troubleshooting

### Issue 1: WebSocket 1008 Policy Violation

**Symptom:**
```
websockets.exceptions.InvalidStatusCode: server rejected WebSocket connection: HTTP 1008
```

**Solution:**
This is fixed in the integration by using the correct `clawdbot-v1` subprotocol. If you still see this:

1. Verify ClawdBot gateway is running
2. Check ClawdBot supports `clawdbot-v1` subprotocol
3. Verify authentication token is correct
4. Check firewall/network settings

### Issue 2: Connection Refused

**Symptom:**
```
Failed to connect to gateway: [Errno 111] Connection refused
```

**Solution:**
1. Verify ClawdBot gateway is running:
   ```bash
   netstat -an | grep 18789
   ```
2. Check host/port configuration
3. Verify firewall allows connections
4. Try connecting manually:
   ```bash
   wscat -c ws://localhost:18789/ws
   ```

### Issue 3: LMStudio Not Responding

**Symptom:**
```
Failed to connect to LMStudio: Connection timeout
```

**Solution:**
1. Verify LMStudio is running:
   ```bash
   curl http://localhost:1234/v1/models
   ```
2. Check model is loaded in LMStudio
3. Verify host/port configuration
4. Check LMStudio logs for errors

### Issue 4: Model Not Found

**Symptom:**
```
Model glm-4.7-flash not found. Available: [...]
```

**Solution:**
1. List available models:
   ```bash
   curl http://localhost:1234/v1/models
   ```
2. Update `ENGRAM_MODEL` environment variable to match available model
3. Or load the correct model in LMStudio

### Issue 5: Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'websockets'
```

**Solution:**
```bash
pip install websockets aiohttp
```

### Issue 6: Permission Denied (Logs)

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: 'logs/engram.log'
```

**Solution:**
```bash
# Create logs directory with proper permissions
mkdir -p logs
chmod 755 logs
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_engram_skill.py -v
pytest tests/test_agent.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=skills --cov=agents --cov-report=html
```

### Manual Testing

1. **Test LMStudio Connection:**
   ```python
   from skills.engram.lmstudio_client import LMStudioClient
   import asyncio
   
   async def test():
       client = LMStudioClient()
       health = await client.health_check()
       print(f"LMStudio healthy: {health}")
   
   asyncio.run(test())
   ```

2. **Test Skill:**
   ```python
   from skills.engram.engram_skill import EngramSkill
   import asyncio
   
   async def test():
       config = {
           "lmstudio_host": "localhost",
           "lmstudio_port": 1234,
           "model": "glm-4.7-flash",
           "response_format": "clean"
       }
       skill = EngramSkill(config)
       response = await skill.process_message("Analyze BTC/USD")
       print(response)
   
   asyncio.run(test())
   ```

## Advanced Configuration

### Custom Response Formats

**Clean Format** (default):
- Filters out reasoning content
- User-friendly output
- No technical metadata

**Detailed Format**:
- Includes timestamps
- Shows agent metadata
- Useful for debugging

**Raw Format**:
- Complete unfiltered output
- Includes reasoning content
- For development/debugging

### Logging Configuration

Set log level via environment:
```bash
export LOG_LEVEL=DEBUG  # Very verbose
export LOG_LEVEL=INFO   # Normal (default)
export LOG_LEVEL=WARNING  # Only warnings/errors
export LOG_LEVEL=ERROR  # Only errors
```

### Reconnection Settings

Edit `config/engram_config.json`:
```json
{
  "clawdbot": {
    "reconnect_delay": 1,
    "max_reconnect_delay": 60,
    "ping_interval": 30
  }
}
```

### Trading Parameters

Configure analysis settings:
```json
{
  "trading": {
    "default_timeframe": "1h",
    "risk_tolerance": "medium",
    "max_position_size": 10000
  },
  "analysis": {
    "indicators": {
      "rsi": {
        "enabled": true,
        "period": 14,
        "overbought": 70,
        "oversold": 30
      }
    }
  }
}
```

## Production Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/engram-clawdbot.service`:

```ini
[Unit]
Description=Engram ClawdBot Integration
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/integration
Environment="LMSTUDIO_HOST=localhost"
Environment="LMSTUDIO_PORT=1234"
Environment="CLAWDBOT_HOST=localhost"
Environment="CLAWDBOT_PORT=18789"
ExecStart=/path/to/.venv/bin/python engram_clawdbot_integration.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable engram-clawdbot
sudo systemctl start engram-clawdbot
sudo systemctl status engram-clawdbot
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "engram_clawdbot_integration.py"]
```

Build and run:
```bash
docker build -t engram-clawdbot .
docker run -d \
  -e LMSTUDIO_HOST=host.docker.internal \
  -e LMSTUDIO_PORT=1234 \
  -e CLAWDBOT_HOST=host.docker.internal \
  -e CLAWDBOT_PORT=18789 \
  --name engram-clawdbot \
  engram-clawdbot
```

## Support

For issues or questions:
1. Check this guide's troubleshooting section
2. Review logs in `logs/engram.log`
3. Run with `LOG_LEVEL=DEBUG` for detailed output
4. Check ClawdBot and LMStudio logs
5. Open an issue on the project repository

## Additional Resources

- [ClawdBot Documentation](https://clawdbot.dev/docs)
- [LMStudio Documentation](https://lmstudio.ai/docs)
- [WebSocket Protocol Spec](https://datatracker.ietf.org/doc/html/rfc6455)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
