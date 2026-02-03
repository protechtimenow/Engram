# Trading Domain (Neural Core)

Use engram scripts for trading analysis. This reference file provides domain-specific guidance for trading queries.

## Available Scripts

### 1. Market Analysis
```bash
python scripts/analyze_market.py --pair [BTC/USD] --timeframe [1h]
```

Parameters:
- `--pair`: Trading pair (e.g., BTC/USD, EUR/USD, AAPL)
- `--timeframe`: Analysis timeframe (1m, 5m, 15m, 1h, 4h, 1d)

Returns: Technical analysis, support/resistance levels, trend direction

### 2. Signal Generation
```bash
python scripts/generate_signal.py --pair [EUR/USD] --context [bullish trend]
```

Parameters:
- `--pair`: Trading pair
- `--context`: Additional market context (optional)

Returns: BUY/SELL/HOLD signal with confidence score and reasoning

### 3. Risk Assessment
```bash
python scripts/assess_risk.py --pair [BTC/USD] --position-size [1000]
```

Parameters:
- `--pair`: Trading pair
- `--position-size`: Position size in USD (default: 1000)

Returns: Risk level (LOW/MEDIUM/HIGH) with recommendations

## Output Format

All trading analysis returns structured JSON:

```json
{
  "domain": "trading",
  "signal": "BUY/SELL/HOLD",
  "confidence": 0.XX,
  "timeframe": "1h",
  "risk_level": "LOW/MEDIUM/HIGH",
  "analysis": "Technical and fundamental analysis text",
  "suggestions": [
    "Actionable suggestion 1",
    "Actionable suggestion 2",
    "Actionable suggestion 3"
  ],
  "reasoning": [
    {"step": "...", "evidence": "..."}
  ],
  "next_steps": ["...", "..."]
}
```

## Calibration Guidelines

### Position Sizing (Kelly Criterion)
Use Kelly criterion for optimal position sizing:
- f* = (bp - q) / b
- Where: b = odds, p = win probability, q = loss probability (1-p)
- Never risk more than 2-5% of portfolio on single trade

### Risk Management
- Always use stop-losses
- Account for correlation across markets
- Apply Bayesian updating when new data arrives
- Include maximum drawdown limits

### Confidence Calibration
- 90%+ confidence: High conviction, larger position size
- 70-90% confidence: Moderate conviction, standard position
- 50-70% confidence: Low conviction, reduced position or skip
- <50% confidence: No trade, wait for better setup

### Market Context Factors
Consider these factors in analysis:
- Macro trends (bull/bear market)
- Volatility regime (high/low volatility)
- Correlation with other assets
- News and event risks
- Liquidity conditions

## Risk Warnings

**Always include these warnings in trading advice:**

1. Past performance does not guarantee future results
2. Trading involves substantial risk of loss
3. Never trade with money you cannot afford to lose
4. This analysis is for informational purposes only, not financial advice
5. Always do your own research and consult a financial advisor

## Workflow

1. **Detect trading query** → User mentions trading pair or asks for market analysis
2. **Determine analysis type** → Market analysis, signal, or risk assessment
3. **Select appropriate script** → Run corresponding engram script
4. **Parse JSON output** → Extract signal, confidence, risk level
5. **Add risk warnings** → Include mandatory risk disclaimers
6. **Present results** → Format for user with actionable suggestions
