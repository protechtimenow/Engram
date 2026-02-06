# Neural Core - ClawdBot Skill

Meta-skill providing progressive-disclosure intelligence across multiple domains.

## Overview

Neural Core extends Engram's capabilities through domain-specific analysis with:
- **Progressive Disclosure**: Load capabilities only when needed (90% token reduction)
- **Multi-Domain Support**: Trading, Research, Strategy, Judgment
- **Universal Scripts**: Reusable analysis tools across all domains
- **Local AI**: LMStudio integration for privacy and speed

## Domains

### Trading
Market analysis, signal generation, risk assessment
- Entry: `analyze_market`, `generate_signal`, `assess_risk`
- Scripts: `analyze_market.py`, `confidence_scoring.py`

### Research
Pattern detection, claim analysis, bias detection
- Entry: `scan_patterns`, `verify_claim`, `detect_bias`
- Scripts: `pattern_scan.py`, `confidence_scoring.py`

### Strategy
Decision frameworks, scenario modeling, optimization
- Entry: `decision_analysis`, `optimize_strategy`, `model_scenarios`
- Scripts: `decision_nets.py` (Kelly, Bayesian, Monte Carlo)

### Judgment
General reasoning, confidence assessment, logical analysis
- Entry: `evaluate_claim`, `check_reasoning`, `assess_confidence`
- Scripts: `confidence_scoring.py`, `pattern_scan.py`

## Architecture

```
User Query
    ↓
Domain Detection (keywords/classifier)
    ↓
Domain Router → Specific Handler
    ↓
Progressive Disclosure (load only needed context)
    ↓
Universal Scripts (reusable analysis)
    ↓
LMStudio / OpenRouter
    ↓
Structured Response
```

## Universal Scripts

All scripts located in `src/engram/scripts/`:

| Script | Purpose | Domains |
|--------|---------|---------|
| `analyze_market.py` | Technical analysis | Trading |
| `confidence_scoring.py` | 0-100% confidence with bias | All |
| `pattern_scan.py` | Fallacy/bias detection | Research, Judgment |
| `decision_nets.py` | Kelly/Bayesian/MC | Strategy, Trading |

## Usage

### Direct Script Usage
```bash
# Trading analysis
python src/engram/scripts/analyze_market.py --pair BTC/USD

# Confidence scoring
python src/engram/scripts/confidence_scoring.py --claim "ETH bullish" --bias-check

# Decision framework
python src/engram/scripts/decision_nets.py --kelly --edge 0.6 --odds 2.0
```

### Via ClawdBot
```
User: "Analyze BTC/USD for a long entry"
→ Domain: Trading
→ Script: analyze_market.py --pair BTC/USD --context "long entry"
→ Response: Structured market analysis

User: "How confident should I be that SOL will reach $200?"
→ Domain: Judgment
→ Script: confidence_scoring.py --claim "SOL will reach $200" --bias-check
→ Response: Confidence score with bias detection
```

## Configuration

Environment variables:
```bash
LMSTUDIO_HOST=localhost
LMSTUDIO_PORT=1234
ENGRAM_MODEL=glm-4.7-flash
OPENROUTER_KEY=sk-or-...
```

## Progressive Disclosure

Instead of loading all domain knowledge upfront:

1. **Lightweight Detection**: Simple keyword matching
2. **Domain Loading**: Load only relevant domain context
3. **Script Execution**: Run appropriate analysis script
4. **Result Synthesis**: Combine script output with AI reasoning

Token efficiency: 90% reduction vs loading all contexts.

## Integration with A2A

Neural Core scripts integrate with A2A debate:

```
A2A Debate on "BTC long at $43k"
    ↓
Proposer: Uses analyze_market.py for technical setup
Critic: Uses confidence_scoring.py to challenge assumptions
Consensus: Uses decision_nets.py --kelly for position sizing
```

## File Structure

```
src/neural_core/
├── SKILL.md              # This file
├── references/           # Domain-specific guidance
│   ├── trading.md        # Trading domain context
│   ├── research.md       # Research domain context
│   ├── strategy.md       # Strategy domain context
│   └── judgment.md       # Judgment domain context
└── __init__.py           # Core routing logic
```

## Version

v2.0.0 - Multi-domain progressive disclosure
