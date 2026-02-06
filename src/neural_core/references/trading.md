# Trading Domain Reference

## Core Principles

1. **Risk Management First**: Position sizing > Entry timing
2. **Edge Validation**: Every trade needs statistical edge
3. **Asymmetric Returns**: Seek positive risk/reward (minimum 1:2)
4. **Market Context**: Macro conditions affect all technicals

## Analysis Framework

### Technical Analysis
- **Trend**: Identify primary trend (higher timeframe)
- **Support/Resistance**: Key levels from price action
- **Momentum**: RSI, MACD, volume confirmation
- **Patterns**: Breakouts, reversals, continuations

### Risk Assessment
- **Position Size**: Kelly criterion or fixed fraction
- **Stop Loss**: Technical level, not arbitrary %
- **Portfolio Heat**: Max 2% risk per trade, 6% total
- **Correlation**: Avoid correlated positions

### Signal Generation
```
LONG Signal Requirements:
- Trend alignment (bullish)
- Support hold / resistance break
- Volume confirmation
- Risk/reward >= 1:2
- Kelly fraction > 0

SHORT Signal Requirements:
- Trend alignment (bearish)
- Resistance hold / support break
- Volume confirmation
- Risk/reward >= 1:2
- Kelly fraction > 0
```

## Output Format

All trading analysis should include:

```
SIGNAL: (LONG/SHORT/NEUTRAL)
CONFIDENCE: (0-100%)
ENTRY: (price level with rationale)
TARGET: (price level with R:R ratio)
STOP: (price level with technical basis)
POSITION: (% of portfolio with Kelly calc)
RATIONALE: (technical + fundamental)
RISKS: (specific concerns)
```

## Common Biases to Check

- **Confirmation**: Seeking only bullish signals in uptrend
- **Recency**: Overweighting recent price action
- **Anchoring**: Fixating on entry price
- **Overconfidence**: Ignoring risk after wins

## Risk Management Rules

1. Never risk >2% per trade
2. Never risk >6% portfolio at once
3. Use Kelly/2 for position sizing
4. Correlation check before adding positions
5. Pre-define exit before entry
