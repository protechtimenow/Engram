# Engram Bot Architecture

## System Overview

Engram is a standalone AI-powered trading assistant that integrates directly with Telegram and LMStudio, providing real-time market analysis and trading signals.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Layer                            │
│  ┌──────────────┐                                           │
│  │   Telegram   │                                           │
│  │     User     │                                           │
│  └──────┬───────┘                                           │
└─────────┼─────────────────────────────────────────────────────┘
          │
          │ Telegram Bot API
          │
┌─────────▼─────────────────────────────────────────────────────┐
│                    Application Layer                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │         EngramTelegramBot                              │  │
│  │  (bot/telegram_bot.py)                                 │  │
│  │                                                         │  │
│  │  • Command Handlers (/help, /status, /analyze, etc.)  │  │
│  │  • Message Processing                                  │  │
│  │  • Error Handling                                      │  │
│  │  • Price Alert Management                              │  │
│  │  • Portfolio Tracking                                  │  │
│  └────────────────┬───────────────────────────────────────┘  │
└───────────────────┼──────────────────────────────────────────┘
                    │
                    │ Skill Interface
                    │
┌───────────────────▼──────────────────────────────────────────┐
│                    Business Logic Layer                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │         EngramSkill                                    │  │
│  │  (skills/engram/engram_skill.py)                       │  │
│  │                                                         │  │
│  │  • Message Processing                                  │  │
│  │  • Tool Registration                                   │  │
│  │  • Response Formatting                                 │  │
│  │  • Health Monitoring                                   │  │
│  └────────────────┬───────────────────────────────────────┘  │
└───────────────────┼──────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        │                       │
┌───────▼────────┐    ┌────────▼──────────┐
│  LMStudioClient│    │  Trading Tools    │
│                │    │                   │
│  • Chat API    │    │  • analyze_market │
│  • Function    │    │  • generate_signal│
│  • Calling     │    │  • assess_risk    │
│  • Health      │    │  • confidence     │
│    Check       │    │    scoring        │
└───────┬────────┘    └───────────────────┘
        │
        │ HTTP API
        │
┌───────▼─────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         LMStudio Server                                │ │
│  │  (100.118.172.23:1234)                                 │ │
│  │                                                         │ │
│  │  • Model: glm-4.7-flash                                │ │
│  │  • OpenAI-compatible API                               │ │
│  │  • Function Calling Support                            │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Layer

**Telegram User**
- Interacts with bot via Telegram app
- Sends commands and messages
- Receives trading analysis and alerts

### 2. Application Layer

**EngramTelegramBot** (`bot/telegram_bot.py`)

**Responsibilities:**
- Handle Telegram Bot API integration
- Process user commands
- Manage conversation state
- Store price alerts
- Track portfolio

**Key Methods:**
- `start_command()` - Welcome message
- `help_command()` - Show available commands
- `status_command()` - Bot health status
- `analyze_command()` - Trading analysis
- `alert_command()` - Set price alerts
- `alerts_command()` - List alerts
- `portfolio_command()` - View portfolio
- `handle_message()` - Process natural language

**Data Structures:**
```python
price_alerts: Dict[str, List[Dict[str, Any]]] = {
    "BTC": [
        {
            "price": 50000,
            "created": "2024-01-15T12:00:00",
            "triggered": False
        }
    ]
}

portfolio: Dict[str, Dict[str, float]] = {
    "BTC": {
        "amount": 0.5,
        "avg_price": 45000
    }
}
```

### 3. Business Logic Layer

**EngramSkill** (`skills/engram/engram_skill.py`)

**Responsibilities:**
- Process trading queries
- Coordinate with LMStudio
- Execute trading tools
- Format responses
- Monitor health

**Tool Registration:**
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_market",
            "description": "Analyze market conditions",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_signal",
            "description": "Generate trading signal",
            "parameters": {...}
        }
    },
    ...
]
```

**Response Formats:**
- `clean` - Filtered, user-friendly (default)
- `detailed` - With timestamps and metadata
- `raw` - Unfiltered model output

**LMStudioClient** (`skills/engram/lmstudio_client.py`)

**Responsibilities:**
- HTTP communication with LMStudio
- Chat completion requests
- Function calling
- Error handling
- Health checks

**API Endpoints:**
- `POST /v1/chat/completions` - Chat with function calling
- `GET /v1/models` - List available models

**Trading Tools** (`skills/engram/tools.py`)

**Available Tools:**
- `analyze_market(pair, timeframe)` - Market analysis
- `generate_signal(pair, context)` - Trading signals
- `get_confidence_score(signal, data)` - Confidence scoring
- `assess_risk(pair, position_size)` - Risk assessment

### 4. External Services

**LMStudio Server**
- Host: 100.118.172.23
- Port: 1234
- Model: glm-4.7-flash
- API: OpenAI-compatible

## Data Flow

### Command Processing Flow

```
1. User sends: "/analyze BTC/USD"
   ↓
2. Telegram Bot API receives message
   ↓
3. EngramTelegramBot.analyze_command() called
   ↓
4. Extract symbol: "BTC/USD"
   ↓
5. Send typing indicator
   ↓
6. Call EngramSkill.process_message("Analyze BTC/USD...")
   ↓
7. EngramSkill builds request with tools
   ↓
8. LMStudioClient.chat_completion() called
   ↓
9. HTTP POST to LMStudio API
   ↓
10. LMStudio processes with glm-4.7-flash
    ↓
11. Model decides to call analyze_market tool
    ↓
12. EngramSkill executes tool
    ↓
13. Tool returns market data
    ↓
14. LMStudio generates final response
    ↓
15. EngramSkill formats response (clean mode)
    ↓
16. EngramTelegramBot sends to user
    ↓
17. User receives analysis
```

### Natural Language Flow

```
1. User sends: "Should I buy Bitcoin now?"
   ↓
2. EngramTelegramBot.handle_message() called
   ↓
3. Send typing indicator
   ↓
4. Call EngramSkill.process_message()
   ↓
5. LMStudio analyzes query
   ↓
6. Model calls generate_signal("BTC")
   ↓
7. Tool returns signal data
   ↓
8. Model generates natural response
   ↓
9. Response formatted and sent to user
```

## Configuration

### Environment Variables

```bash
# LMStudio
LMSTUDIO_HOST=100.118.172.23
LMSTUDIO_PORT=1234
ENGRAM_MODEL=glm-4.7-flash

# Telegram
TELEGRAM_BOT_TOKEN=your_token_here

# Optional
ENGRAM_RESPONSE_FORMAT=clean
LOG_LEVEL=INFO
```

### Config File (`config/engram_config.json`)

```json
{
  "lmstudio": {
    "host": "100.118.172.23",
    "port": 1234,
    "model": "glm-4.7-flash",
    "timeout": 60,
    "max_retries": 3
  },
  "agent": {
    "response_format": "clean"
  },
  "trading": {
    "default_timeframe": "1h",
    "risk_tolerance": "medium"
  }
}
```

## Error Handling

### Levels of Error Handling

1. **Application Level** (EngramTelegramBot)
   - Catches all exceptions
   - Sends user-friendly error messages
   - Logs errors for debugging

2. **Business Logic Level** (EngramSkill)
   - Handles tool execution errors
   - Provides fallback responses
   - Logs processing errors

3. **API Level** (LMStudioClient)
   - Retries on network errors
   - Handles timeouts
   - Validates responses

### Error Flow

```
Error occurs in LMStudio
    ↓
LMStudioClient catches and logs
    ↓
Returns error to EngramSkill
    ↓
EngramSkill provides fallback response
    ↓
EngramTelegramBot receives fallback
    ↓
User gets friendly error message
```

## Logging

### Log Levels

- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages

### Log Format

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Log Files

- `logs/engram_bot.log` - Main log file
- Rotates automatically
- Includes all components

## Security

### API Keys

- Telegram bot token stored in environment variable
- Never committed to version control
- Loaded at runtime

### Input Validation

- All user inputs validated
- Command arguments checked
- Price values verified

### Rate Limiting

- Telegram Bot API handles rate limiting
- LMStudio has no built-in limits
- Consider implementing application-level limits

## Performance

### Optimization Strategies

1. **Async/Await**
   - All I/O operations are async
   - Non-blocking message processing
   - Concurrent request handling

2. **Connection Pooling**
   - HTTP connections reused
   - Reduces latency
   - Improves throughput

3. **Response Caching**
   - Consider caching market data
   - Reduce LMStudio calls
   - Faster responses

### Scalability

**Current Limitations:**
- Single-instance deployment
- In-memory alert storage
- No database persistence

**Future Improvements:**
- Multi-instance with load balancer
- Redis for alert storage
- Database for persistence
- Message queue for async processing

## Why No ClawdBot WebSocket?

### The Issue

ClawdBot's WebSocket gateway (`ws://localhost:18789/ws`) returns:
```
[ws] invalid handshake - invalid request frame
[ws] closed before connect code=1008
```

### Root Cause

ClawdBot's WebSocket gateway is designed for:
1. **Web UI** - Browser-based connections
2. **Internal Plugins** - Code running inside ClawdBot
3. **NOT External Agents** - No support for external WebSocket clients

### Our Solution

**Standalone Architecture:**
- Direct Telegram integration
- Direct LMStudio integration
- No ClawdBot dependency
- Simpler, more reliable

### Alternative ClawdBot Integration

If ClawdBot integration is required:

1. **Plugin Approach**
   - Write ClawdBot plugin
   - Runs inside ClawdBot process
   - Has access to ClawdBot APIs

2. **Telegram Channel**
   - Use ClawdBot's Telegram support
   - Share bot token
   - Let ClawdBot handle Telegram

3. **HTTP API**
   - If ClawdBot exposes HTTP APIs
   - More reliable than WebSocket

## Deployment

### Development

```bash
python start_engram_bot.py
```

### Production

**Systemd Service (Linux):**
```bash
sudo systemctl start engram-bot
sudo systemctl enable engram-bot
```

**Windows Service:**
```powershell
# Use Task Scheduler or NSSM
nssm install EngramBot python start_engram_bot.py
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "start_engram_bot.py"]
```

## Monitoring

### Health Checks

- `/status` command shows bot health
- LMStudio connection status
- Tool registration count
- Active alerts count

### Metrics to Track

- Messages processed
- Commands executed
- LMStudio response times
- Error rates
- Active users

## Summary

**Engram Bot is a production-ready standalone trading assistant with:**

✅ Clean architecture
✅ Async/await for performance
✅ Comprehensive error handling
✅ Detailed logging
✅ Direct integrations (no ClawdBot WebSocket)
✅ Scalable design
✅ Security best practices

**To run:**
```bash
python start_engram_bot.py
