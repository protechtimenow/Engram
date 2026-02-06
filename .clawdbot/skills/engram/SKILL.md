# Engram Bridge Skill

**Version:** 1.0.0  
**Description:** Connects ClawdBot to Freqtrade bridges for live trading with BarChart, Tradovate, and CSV export

## Overview

This skill provides ClawdBot with direct access to:
- **BarChart WebSocket**: Real-time futures data (ES, NQ, GC, XAUUSD)
- **Tradovate API**: Live order placement, kill switch, liquidation
- **CSV Export**: Trade journal export with pandas/stdlib fallback

## Architecture

```
ClawdBot → EngramBridgeSkill → NeuralBridgeAdapter → Freqtrade Bridges
                ↓
           Neural Core (AI signals)
```

## Configuration

Add to your `clawdbot.json`:

```json
{
  "skills": {
    "engram_bridge": {
      "enabled": true,
      "barchart_api_key": "your_key_here",
      "tradovate_api_key": "your_key_here",
      "tradovate_api_secret": "your_secret_here",
      "tradovate_account_id": 12345
    }
  }
}
```

## Commands

### Get Market Data
```json
{
  "command": "get_market_data",
  "args": {"symbol": "ES"}
}
```

### Get Positions
```json
{
  "command": "get_positions"
}
```

### Execute Trading Signal
```json
{
  "command": "execute_signal",
  "args": {
    "symbol": "ES",
    "signal_type": "BUY",
    "confidence": 0.85,
    "reasoning": "EMA cross detected",
    "metadata": {"quantity": 1},
    "timestamp": "2026-02-03T05:30:00"
  }
}
```

### Emergency Liquidate
```json
{
  "command": "emergency_liquidate"
}
```

### Export Trades
```json
{
  "command": "export_trades",
  "args": {
    "output_path": "trades.csv",
    "filters": {"market": "FUTURES"}
  }
}
```

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Skill entry point, imports from freqtrade/bridges |
| `neural_bridge_adapter.py` | Master implementation (in freqtrade/bridges) |
| `barchart_bridge.py` | BarChart WebSocket (in freqtrade/bridges) |
| `tradovate_bridge.py` | Tradovate API (in freqtrade/bridges) |
| `csv_export_bridge.py` | CSV export (in freqtrade/bridges) |

## Integration with Neural Core

The skill forwards all market data to Neural Core for AI analysis:
- Real-time ticks → Neural Core → Trading signals
- Position updates → Risk management
- Order updates → Performance tracking

## Dependencies

- `websockets` (for BarChart)
- `aiohttp` (for Tradovate)
- `pandas` (optional, for CSV export)

## Troubleshooting

### Connection Timeout Issues

If the agent fails to connect to the OpenClaw gateway:

1. **Check Gateway Status**: Ensure the gateway is running on port 17500
2. **Verify Token**: Token should be in `config/engram_fast.json` under `clawdbot.token`
3. **Connection Timeout**: The agent uses `asyncio.wait_for(websockets.connect(uri), timeout=10)` to prevent indefinite hanging
4. **Gateway Logs**: Check gateway logs for authentication errors

### Authentication Flow

1. Agent connects to `ws://localhost:17500` (no token in URL)
2. Gateway sends `connect.challenge` event with nonce
3. Agent responds with `connect` request containing token in `params.auth.token`
4. Gateway validates and responds with success/failure

## Configuration Reference

**Token Location**: `config/engram_fast.json`
```json
{
  "clawdbot": {
    "token": "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
  }
}
```

**Environment Variables** (optional):
- `OPENROUTER_API_KEY` - For AI model access
- `STEPFUN_API_KEY` - Alternative AI provider

## Testing

Run integration tests:
```bash
cd freqtrade/bridges
python full_integration_test.py
```

## License

Same as Engram project
