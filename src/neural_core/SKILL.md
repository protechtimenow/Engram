---
name: neural-core
description: General neural decision intelligence for trading, research, pattern recognition, and strategy. Progressive-disclosure design loads only relevant references per domain. Use when user asks for "analyze [domain]", "pattern recognition", "decision strategy", "confidence assessment", or trading analysis. Triggers on domain-specific queries across trading, research, strategy, and general reasoning.
---

# Neural Core Decision Intelligence

Neural Core provides systematic decision intelligence across domains using Engram's neural capabilities as the underlying engine. The system uses progressive disclosure—loading only the reference file relevant to the user's query.

## Domain Loading Strategy

When user queries by domain, load corresponding reference file and delegate to domain-specific logic:

- **Trading** → Load `references/trading.md` → Use engram scripts (analyze_market, generate_signal, assess_risk)
- **Research** → Load `references/research.md` → Use engram pattern-scan + confidence-scoring
- **Strategy** → Load `references/strategy.md` → Use engram decision-nets + Bayesian frameworks
- **General** → Load `references/judgment.md` → Use engram confidence-scoring + bias detection

## Domain Detection

Determine domain from user query:

**Trading domain indicators:**
- Trading pairs (BTC/USD, EUR/USD, AAPL)
- Market analysis requests
- Signal generation
- Risk assessment for positions
- Keywords: "analyze", "signal", "trade", "position", "market"

**Research domain indicators:**
- Pattern recognition in text/data
- Claim analysis
- Evidence evaluation
- Keywords: "analyze this claim", "pattern", "research", "evidence"

**Strategy domain indicators:**
- Decision frameworks
- Scenario modeling
- Decision trees
- Keywords: "decision", "strategy", "framework", "scenario", "optimize"

**General/Judgment domain indicators:**
- Confidence assessment
- General reasoning
- Bias detection
- Keywords: "confidence", "reasoning", "bias", "judgment", "evaluate"

## Core Capabilities (Reused Across Domains)

1. **Confidence Scoring** - Score any claim 0-100% with bias detection
2. **Pattern Detection** - Find patterns, signals, anomalies in text/data
3. **Decision Frameworks** - Build decision trees, Bayesian nets, value functions
4. **Risk Assessment** - Per-domain risk models

## Output Format

All responses output structured JSON with:
- `domain`: The domain used (trading/research/strategy/judgment)
- `confidence`: Overall confidence score (0.0-1.0)
- `reasoning`: Array of reasoning steps with evidence
- `analysis`: Domain-specific analysis results
- `next_steps`: Actionable recommendations

## Usage Examples

**Trading example:**
User: "Analyze BTC/USD"
1. Load `references/trading.md`
2. Run `analyze_market.py --pair BTC/USD --timeframe 1h`
3. Output JSON with signal, confidence, risk level

**Research example:**
User: "Analyze this claim about AI safety"
1. Load `references/research.md`
2. Run `pattern-scan.py` on claim text
3. Run `confidence-scoring.py` on claim + evidence
4. Output JSON with confidence, biases detected, patterns found

**Strategy example:**
User: "Design decision framework for position sizing"
1. Load `references/strategy.md`
2. Run `decision-nets.py` with nodes and probabilities
3. Run Monte Carlo simulation
4. Output JSON with decision tree, expected value, risk profile

**General example:**
User: "What's the confidence in Trump pardoning Epstein?"
1. Load `references/judgment.md`
2. Run `confidence-scoring.py` on claim
3. Detect cognitive biases
4. Output JSON with confidence score, reasoning trace, bias flags

## Script Locations

All scripts are in `C:\Users\OFFRSTAR0\.clawdbot\skills\engram\scripts\`:
- `analyze_market.py` - Market analysis
- `generate_signal.py` - Signal generation
- `assess_risk.py` - Risk assessment
- `confidence-scoring.py` - Confidence scoring across domains
- `pattern-scan.py` - Pattern detection
- `decision-nets.py` - Decision network building

## Integration with ClawdBot

When this skill triggers:
1. Detect domain from user query
2. Load corresponding reference file
3. Execute appropriate scripts
4. Return structured JSON response
5. Include risk warnings and confidence calibration
