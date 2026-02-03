# General Judgment Domain (Neural Core)

Use engram for general reasoning, confidence assessment, and bias detection. This reference file provides domain-specific guidance for general judgment queries.

## Available Scripts

### 1. Claim Confidence Scoring
```bash
python scripts/confidence-scoring.py --claim "[claim]" --evidence "[evidence]"
```

Parameters:
- `--claim`: The claim to evaluate
- `--evidence`: Supporting or related evidence
- `--context`: Additional context (optional)
- `--bias-check`: Enable bias detection (default: true)

Returns: Confidence score (0-100%), reasoning trace, bias flags

### 2. Pattern Detection
```bash
python scripts/pattern-scan.py --input "[text]" --type "text"
```

Parameters:
- `--input`: Text to analyze
- `--type`: Input type (text)
- `--detect-fallacies`: Detect logical fallacies (optional)

Returns: Patterns found, logical fallacies detected, anomalies

### 3. Bias Detection
```bash
python scripts/confidence-scoring.py --text "[text]" --bias-check-only
```

Returns: List of detected cognitive biases with severity

## Judgment Process

1. **Extract Claim** → Identify the core claim or proposition
2. **Gather Evidence** → Collect supporting and contradicting evidence
3. **Scan for Patterns** → Detect patterns, logical fallacies, anomalies
4. **Score Confidence** → Evaluate claim confidence (0-100%)
5. **Detect Biases** → Run automated bias checklist
6. **Build Reasoning Trace** → Document step-by-step reasoning
7. **Synthesize Output** → Combine into structured judgment

## Output Format

General judgment returns structured JSON:

```json
{
  "domain": "judgment",
  "claim": "...",
  "confidence": 0.XX,
  "confidence_breakdown": {
    "evidence_quality": 0.XX,
    "logical_coherence": 0.XX,
    "source_credibility": 0.XX,
    "consistency": 0.XX
  },
  "reasoning": [
    {
      "step": 1,
      "description": "...",
      "evidence": "...",
      "inference": "..."
    }
  ],
  "biases_detected": [
    {
      "bias": "anchoring|availability|confirmation|hindsight|authority",
      "severity": "high/medium/low",
      "description": "...",
      "mitigation": "..."
    }
  ],
  "logical_fallacies": [
    {
      "fallacy": "ad_hominem|straw_man|false_dichotomy|slippery_slope",
      "description": "..."
    }
  ],
  "evidence_assessment": {
    "supporting": ["..."],
    "contradicting": ["..."],
    "missing": ["..."]
  },
  "alternative_explanations": ["..."],
  "uncertainty_factors": ["..."],
  "recommendations": ["..."],
  "next_steps": ["..."]
}
```

## Confidence Calibration

### Confidence Levels

**90-100% (Virtually Certain)**
- Established facts with overwhelming evidence
- Mathematical/logical truths
- Directly observable phenomena
- Strong expert consensus

**70-90% (Highly Likely)**
- Well-supported claims with good evidence
- Strong but not conclusive proof
- Minor uncertainties remain

**50-70% (More Likely Than Not)**
- Weakly supported claims
- Conflicting evidence
- Significant uncertainty

**30-50% (Unlikely)**
- Weak evidence
- Contradictory information
- Speculative claims

**0-30% (Very Unlikely)**
- Contradicted by evidence
- Logical inconsistencies
- No supporting evidence

### Confidence Factors

**Evidence Quality (25% weight)**
- Strength of supporting evidence
- Independence of sources
- Verifiability
- Recency

**Logical Coherence (25% weight)**
- Internal consistency
- Logical validity
- Absence of fallacies
- Parsimony (Occam's razor)

**Source Credibility (25% weight)**
- Expertise of sources
- Track record
- Potential biases
- Independence

**Consistency (25% weight)**
- Consistency with known facts
- Consistency across sources
- Consistency with base rates

## Cognitive Bias Detection

### Systematic Biases

**Anchoring**
- Over-reliance on first information received
- Insufficient adjustment from initial value
- *Detection*: Check if conclusions shift when starting point changes

**Availability Heuristic**
- Judging probability by ease of recall
- Overweighting recent or vivid events
- *Detection*: Compare to base rates; check for recency bias

**Confirmation Bias**
- Seeking confirming evidence, ignoring disconfirming
- Interpretation bias
- *Detection*: Check if contradictory evidence was considered

**Hindsight Bias**
- "I knew it all along" after outcome known
- Overestimating prior predictability
- *Detection*: Check if prediction documented before outcome

**Authority Bias**
- Accepting claims based on authority alone
- Deference to expertise without evaluation
- *Detection*: Check if evidence evaluated independently

**Dunning-Kruger Effect**
- Overconfidence in novices, underconfidence in experts
- *Detection*: Check expertise level vs. confidence calibration

### Logical Fallacies

**Ad Hominem** - Attacking person instead of argument
**Straw Man** - Misrepresenting opponent's position
**False Dichotomy** - Presenting only two options when more exist
**Slippery Slope** - Assuming chain reaction without evidence
**Appeal to Emotion** - Using emotion instead of evidence
**Circular Reasoning** - Conclusion assumed in premise
**Post Hoc** - Assuming causation from correlation

## Judgment Principles

1. **Be Explicit About Uncertainty**
   - State confidence levels clearly
   - Provide uncertainty ranges
   - Distinguish facts from inferences

2. **Update with New Evidence**
   - Use Bayesian updating
   - Revise confidence when new information arrives
   - Be willing to change mind

3. **Flag Weak Reasoning**
   - Identify logical gaps
   - Point out missing evidence
   - Note unsupported assumptions

4. **Prefer Simple Explanations**
   - Apply Occam's razor
   - Favor explanations with fewer assumptions
   - Avoid unnecessary complexity

5. **Consider Alternative Explanations**
   - Generate multiple hypotheses
   - Evaluate each against evidence
   - Avoid premature convergence

6. **Confidence ≠ Probability**
   - Confidence reflects evidence quality
   - Probability reflects frequency
   - Distinguish epistemic from aleatory uncertainty

## Calibration Exercises

### Overconfidence Test
When confidence is X%, verify that claim is true X% of time:
- 90% confident → Should be correct 9/10 times
- 70% confident → Should be correct 7/10 times
- 50% confident → Should be correct 5/10 times

If systematically over/under-confident, adjust calibration.

### Base Rate Consideration
Always consider base rates:
- What's the historical frequency?
- What would we expect by chance?
- How does this compare to similar cases?

### Falsifiability Check
Good claims can be proven wrong:
- What evidence would disprove this?
- Is the claim testable?
- Are there hidden assumptions?

## Workflow

1. **Detect judgment query** → User asks for evaluation, confidence, or reasoning
2. **Extract claim** → Identify the core proposition
3. **Scan for patterns** → Detect fallacies and biases
4. **Score confidence** → Evaluate using confidence factors
5. **Build reasoning trace** → Document step-by-step logic
6. **Present judgment** → Show confidence, biases, reasoning, alternatives
