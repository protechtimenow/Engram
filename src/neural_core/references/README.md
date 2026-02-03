# Neural Core Domain References

This directory contains progressive disclosure references for different domains.

## Usage

When user queries by domain, load corresponding reference file:

- `trading.md` → Trading analysis, signals, risk assessment
- `research.md` → Pattern detection, confidence scoring, bias detection
- `strategy.md` → Decision frameworks, Bayesian nets, scenario modeling
- `judgment.md` → General reasoning, claim scoring, bias detection

## Structure

Each reference file:
1. Defines domain-specific workflow
2. References Engram scripts
3. Specifies output format (structured JSON)
4. Includes calibration guidelines

## Loading Strategy

Codex loads SKILL.md first (contains domain mapping), then loads only relevant reference file based on query domain. This maintains token efficiency while providing domain-specific guidance.

## Script Locations

All scripts are in `C:\Users\OFFRSTAR0\.clawdbot\skills\engram\scripts\`:
- `analyze_market.py` - Market analysis (trading domain)
- `generate_signal.py` - Signal generation (trading domain)
- `assess_risk.py` - Risk assessment (trading domain)
- `confidence-scoring.py` - Confidence scoring (all domains)
- `pattern-scan.py` - Pattern detection (research/judgment domains)
- `decision-nets.py` - Decision networks (strategy domain)

## Output Format

All domains output structured JSON with:
- `domain`: The domain used
- `confidence`: Overall confidence score (0.0-1.0)
- `reasoning`: Array of reasoning steps
- `analysis`: Domain-specific results
- `next_steps`: Actionable recommendations

## Domain Selection Guide

| User Query | Domain | Reference File |
|------------|--------|----------------|
| "Analyze BTC/USD" | Trading | `trading.md` |
| "Trading signal for EUR/USD" | Trading | `trading.md` |
| "Assess risk for position" | Trading | `trading.md` |
| "Analyze this claim" | Research | `research.md` |
| "Pattern in this data" | Research | `research.md` |
| "Confidence in X" | Judgment | `judgment.md` |
| "Evaluate this argument" | Judgment | `judgment.md` |
| "Decision framework" | Strategy | `strategy.md` |
| "Optimize strategy" | Strategy | `strategy.md` |
| "Scenario analysis" | Strategy | `strategy.md` |

## Integration

These references work with the main `SKILL.md` in the parent directory. The main SKILL.md handles domain detection and routing, while these reference files provide domain-specific implementation details.
