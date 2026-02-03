# Neural Core

Progressive-disclosure decision intelligence system for multi-domain analysis.

## Overview

Neural Core extends Engram's neural capabilities across four domains:
- **Trading** - Market analysis, signals, risk assessment
- **Research** - Pattern detection, claim analysis, bias detection  
- **Strategy** - Decision frameworks, scenario modeling, optimization
- **Judgment** - General reasoning, confidence assessment, logical analysis

## Quick Start

```bash
# Trading Analysis
python ../engram/scripts/analyze_market.py --pair BTC/USD --timeframe 1h

# Confidence Scoring
python ../engram/scripts/confidence_scoring.py --claim "Claim text" --evidence "Evidence"

# Pattern Detection
python ../engram/scripts/pattern_scan.py --input "Text to analyze" --detect-fallacies

# Decision Framework
python ../engram/scripts/decision_nets.py --kelly --edge 0.6 --odds 2.0
```

## Architecture

```
User Query → Domain Detection → Reference Loading → Script Execution → JSON Output
```

## Domain References

- `trading.md` - Trading analysis guidance
- `research.md` - Research methodology
- `strategy.md` - Strategic decision frameworks
- `judgment.md` - General reasoning principles

## Universal Scripts

All scripts output structured JSON with confidence scores:

| Script | Purpose | Domains |
|--------|---------|---------|
| `confidence_scoring.py` | Claim evaluation 0-100% | All |
| `pattern_scan.py` | Pattern/bias detection | Research, Judgment |
| `decision_nets.py` | Bayesian decision trees | Strategy |

## Integration

Neural Core integrates with ClawdBot as a skill. See `SKILL.md` for ClawdBot integration details.
