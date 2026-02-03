# Neural Core Documentation

## Overview

Neural Core is a progressive-disclosure decision intelligence system that extends Engram's neural capabilities across multiple domains.

## Design Philosophy

### Progressive Disclosure

Instead of loading all domain knowledge at once, Neural Core loads only what's needed:

1. **Query Analysis**: Detect domain from user query
2. **Reference Loading**: Load only relevant domain reference
3. **Script Execution**: Run appropriate Engram scripts
4. **Structured Output**: Return consistent JSON format

This approach reduces token usage by ~90% compared to monolithic systems.

## Domains

### 1. Trading Domain

**Purpose**: Market analysis, signal generation, risk assessment

**Triggers**:
- Trading pairs (BTC/USD, EUR/USD)
- Market analysis requests
- Signal generation
- Risk assessment

**Scripts**:
```bash
python src/engram/scripts/analyze_market.py --pair BTC/USD --timeframe 1h
python src/engram/scripts/generate_signal.py --pair EUR/USD
python src/engram/scripts/assess_risk.py --pair BTC/USD --position-size 1000
```

**Output Format**:
```json
{
  "domain": "trading",
  "signal": "BUY",
  "confidence": 0.75,
  "timeframe": "1h",
  "risk_level": "MEDIUM",
  "analysis": "...",
  "suggestions": ["..."]
}
```

### 2. Research Domain

**Purpose**: Pattern detection, claim analysis, bias detection

**Triggers**:
- "Analyze this claim"
- "Pattern in this data"
- "Evaluate evidence"

**Scripts**:
```bash
python src/engram/scripts/pattern_scan.py --input "..." --detect-fallacies
python src/engram/scripts/confidence_scoring.py --claim "..." --evidence "..."
```

**Output Format**:
```json
{
  "domain": "research",
  "claims": [{"claim": "...", "confidence": 0.85}],
  "patterns": [{"pattern": "...", "confidence": 0.9}],
  "biases_detected": [{"bias": "anchoring", "severity": "medium"}],
  "overall_confidence": 0.82
}
```

### 3. Strategy Domain

**Purpose**: Decision frameworks, scenario modeling, optimization

**Triggers**:
- "Decision framework for X"
- "Optimize strategy"
- "Scenario analysis"

**Scripts**:
```bash
python src/engram/scripts/decision_nets.py --nodes "[...]" --probabilities "{...}"
python src/engram/scripts/decision_nets.py --kelly --edge 0.6 --odds 2.0
```

**Output Format**:
```json
{
  "domain": "strategy",
  "expected_value": 45.2,
  "optimal_path": ["node1", "node2"],
  "monte_carlo": {"mean": 42.5, "std_dev": 15.3},
  "risk_profile": {"tail_risk": "medium"}
}
```

### 4. Judgment Domain

**Purpose**: General reasoning, confidence assessment, logical analysis

**Triggers**:
- "Confidence in X"
- "Evaluate this argument"
- "Is this logical?"

**Scripts**:
```bash
python src/engram/scripts/confidence_scoring.py --claim "..." --bias-check
python src/engram/scripts/pattern_scan.py --input "..."
```

**Output Format**:
```json
{
  "domain": "judgment",
  "claim": "...",
  "confidence": 0.68,
  "confidence_breakdown": {
    "evidence_quality": 0.7,
    "logical_coherence": 0.8,
    "source_credibility": 0.6,
    "consistency": 0.65
  },
  "biases_detected": [{"bias": "confirmation", "severity": "low"}],
  "logical_fallacies": []
}
```

## Universal Scripts

### Confidence Scoring

Scores any claim 0-100% with detailed breakdown:

```python
# Usage
python src/engram/scripts/confidence_scoring.py \
  --claim "Bitcoin will reach $100k" \
  --evidence "Historical growth, institutional adoption" \
  --bias-check

# Features
- Evidence quality assessment
- Logical coherence check
- Source credibility evaluation
- Consistency analysis
- Bias detection (5 types)
```

### Pattern Scan

Detects patterns, biases, and fallacies in text:

```python
# Usage
python src/engram/scripts/pattern_scan.py \
  --input "The market is obviously going to crash..." \
  --detect-fallacies

# Features
- Repeated phrase detection
- Structural pattern detection
- Linguistic pattern analysis
- Cognitive bias detection
- Logical fallacy detection
- Anomaly detection
```

### Decision Nets

Builds Bayesian decision frameworks:

```python
# Usage
python src/engram/scripts/decision_nets.py \
  --nodes '[{"name": "A", "type": "decision", "children": ["B"]}]' \
  --probabilities '{"B": 0.6}'

# Features
- Decision tree building
- Expected value calculation
- Monte Carlo simulation
- Risk matrix generation
- Kelly criterion calculation
- Optimal path finding
```

## Integration Guide

### Adding a New Domain

1. Create reference file: `src/neural_core/references/new_domain.md`
2. Define triggers in reference file
3. Specify which scripts to use
4. Define output format
5. Update SKILL.md with domain mapping

### Adding a New Script

1. Create script in `src/engram/scripts/`
2. Follow existing script patterns
3. Accept JSON input/output
4. Add to appropriate domain reference
5. Document in README

### Testing

```bash
# Test specific domain
python src/engram/scripts/analyze_market.py --pair BTC/USD

# Test confidence scoring
python src/engram/scripts/confidence_scoring.py --claim "Test claim"

# Test pattern scanning
python src/engram/scripts/pattern_scan.py --input "Test input"
```

## Best Practices

1. **Always validate inputs** before processing
2. **Return structured JSON** for consistency
3. **Include confidence scores** for all claims
4. **Detect biases** in all analyses
5. **Provide actionable next steps**
6. **Use progressive disclosure** to manage tokens

## Troubleshooting

### Script Not Found
```bash
# Ensure you're in the correct directory
cd C:\Users\OFFRSTAR0\Engram
python src/engram/scripts/script_name.py
```

### LMStudio Connection Error
```bash
# Check LMStudio is running
curl http://localhost:1234/v1/models
```

### Domain Not Detected
- Check query matches domain triggers
- Verify SKILL.md domain mapping
- Review reference file triggers
