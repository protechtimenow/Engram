# Research Domain (Neural Core)

Use engram for systematic research and pattern recognition. This reference file provides domain-specific guidance for research queries.

## Available Scripts

### 1. Pattern Scanning
```bash
python scripts/pattern-scan.py --input "[text]" --type "[text|data]"
```

Parameters:
- `--input`: Text or data to scan
- `--type`: Type of input (text or data)
- `--patterns`: Specific regex patterns to look for (optional)

Returns: Patterns found, confidence per pattern, anomalies detected

### 2. Confidence Scoring
```bash
python scripts/confidence-scoring.py --claim "[claim]" --evidence "[evidence]"
```

Parameters:
- `--claim`: The claim to evaluate
- `--evidence`: Supporting evidence
- `--bias-check`: Enable bias detection (default: true)

Returns: Confidence score (0-100%), reasoning trace, bias flags

### 3. Bias Detection
```bash
python scripts/confidence-scoring.py --claim "[claim]" --evidence "[evidence]" --bias-check-only
```

Returns: List of detected cognitive biases

## Research Process

1. **Extract Claims** → Identify key claims from user input
2. **Gather Evidence** → Collect supporting/contradicting evidence
3. **Pattern Scan** → Run pattern detection on text/data
4. **Score Confidence** → Evaluate each claim's confidence
5. **Detect Biases** → Run automated bias checklist
6. **Synthesize** → Combine results into structured output

## Output Format

Research analysis returns structured JSON:

```json
{
  "domain": "research",
  "claims": [
    {
      "claim": "...",
      "confidence": 0.XX,
      "evidence_quality": "high/medium/low",
      "bias_check": "...",
      "supporting_evidence": ["..."],
      "contradicting_evidence": ["..."]
    }
  ],
  "patterns": [
    {
      "pattern": "...",
      "confidence": 0.XX,
      "locations": ["..."]
    }
  ],
  "anomalies": ["..."],
  "biases_detected": [
    {
      "bias": "anchoring|availability|confirmation|hindsight",
      "severity": "high/medium/low",
      "description": "..."
    }
  ],
  "overall_confidence": 0.XX,
  "reasoning": [
    {"step": "...", "evidence": "..."}
  ],
  "next_steps": ["...", "..."]
}
```

## Cognitive Bias Detection

### Anchoring Bias
- **Signs**: Fixation on first piece of information
- **Detection**: Check if initial data point disproportionately influences conclusions
- **Mitigation**: Explicitly consider alternative starting points

### Availability Heuristic
- **Signs**: Overweighting recent or memorable events
- **Detection**: Check if analysis over-relies on recent examples
- **Mitigation**: Actively seek historical data and base rates

### Confirmation Bias
- **Signs**: Seeking only confirming evidence, ignoring contradictions
- **Detection**: Check if contradicting evidence was considered
- **Mitigation**: Actively search for disconfirming evidence

### Hindsight Bias
- **Signs**: Overestimating prior knowledge after outcome known
- **Detection**: Check if "I knew it all along" language present
- **Mitigation**: Document predictions before outcomes known

### Authority Bias
- **Signs**: Over-reliance on authority figures
- **Detection**: Check if claims accepted based on source alone
- **Mitigation**: Evaluate evidence independently of source

## Research Principles

1. **Source Credibility** → Prioritize credible, verifiable sources
2. **Information Asymmetry** → Check for gaps in available information
3. **Bayesian Updating** → Update confidence when new evidence arrives
4. **Avoid Overconfidence** → Be explicit about uncertainty ranges
5. **Falsifiability** → Good claims can be proven wrong
6. **Base Rates** → Consider historical frequencies and probabilities

## Calibration Guidelines

### Evidence Quality Levels
- **High**: Multiple independent sources, verifiable data, expert consensus
- **Medium**: Limited sources, some verification, mixed expert opinion
- **Low**: Single source, unverified claims, no expert consensus

### Confidence Calibration
- 90-100%: Established facts, verified data, strong consensus
- 70-90%: Well-supported claims, some uncertainty
- 50-70%: Weakly supported claims, significant uncertainty
- 30-50%: Speculative claims, limited evidence
- 0-30%: Unsupported claims, contradictory evidence

## Workflow

1. **Detect research query** → User asks to analyze claim, pattern, or evidence
2. **Extract claims** → Identify specific claims to evaluate
3. **Run pattern scan** → Detect patterns in text/data
4. **Score confidence** → Evaluate claim confidence with bias detection
5. **Synthesize results** → Combine into structured JSON
6. **Present findings** → Show confidence scores, biases, next steps
