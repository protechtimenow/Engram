# Strategy Domain (Neural Core)

Use engram for decision framework design and strategic analysis. This reference file provides domain-specific guidance for strategy queries.

## Available Scripts

### 1. Decision Network Building
```bash
python scripts/decision-nets.py --nodes "[node1,node2,...]" --probabilities "[0.6,0.4,...]"
```

Parameters:
- `--nodes`: Decision nodes and actions (JSON array)
- `--probabilities`: Probabilities for each branch (JSON array)
- `--values`: Value/utility for outcomes (JSON array, optional)

Returns: Decision tree structure, expected value, risk profile

### 2. Scenario Modeling
```bash
python scripts/decision-nets.py --scenario "[scenario_name]" --parameters "[json_params]"
```

Parameters:
- `--scenario`: Scenario name
- `--parameters`: Scenario parameters (JSON)
- `--monte-carlo`: Run Monte Carlo simulation

Returns: Scenario outcomes, probability distributions

### 3. Risk Matrix Analysis
```bash
python scripts/decision-nets.py --risk-matrix --impacts "[high,medium,low]" --probabilities "[0.3,0.5,0.2]"
```

Returns: Risk matrix mapping scenarios to probabilities and values

## Decision Framework Process

1. **Identify Decision Nodes** → Map all decision points and branches
2. **Assign Probabilities** → Use Bayesian reasoning for branch probabilities
3. **Assign Values** → Determine utility/value for each outcome
4. **Calculate Expected Value** → EV = Σ(P(outcome) × Value(outcome))
5. **Assess Risk Profile** → Analyze variance, tail risks, worst-case scenarios
6. **Optimize Decision** → Choose path with best risk-adjusted return
7. **Run Monte Carlo** → Test robustness to parameter variations

## Output Format

Strategy analysis returns structured JSON:

```json
{
  "domain": "strategy",
  "decision_tree": {
    "root": "Decision name",
    "branches": [
      {
        "condition": "...",
        "action": "...",
        "probability": 0.XX,
        "expected_value": 0.XX,
        "sub_branches": [...]
      }
    ]
  },
  "expected_value": 0.XX,
  "risk_profile": {
    "variance": 0.XX,
    "worst_case": 0.XX,
    "best_case": 0.XX,
    "tail_risk": "low/medium/high"
  },
  "scenario_analysis": [
    {
      "scenario": "...",
      "probability": 0.XX,
      "outcome": 0.XX,
      "key_assumptions": ["..."]
    }
  ],
  "monte_carlo_results": {
    "mean": 0.XX,
    "median": 0.XX,
    "std_dev": 0.XX,
    "percentiles": {
      "5th": 0.XX,
      "95th": 0.XX
    }
  },
  "optimal_strategy": "...",
  "exit_conditions": ["..."],
  "reasoning": [
    {"step": "...", "evidence": "..."}
  ],
  "next_steps": ["...", "..."]
}
```

## Decision Frameworks

### Expected Value Maximization
Choose action with highest expected value:
```
EV(Action) = Σ P(Outcome|Action) × Value(Outcome)
Best Action = argmax EV(Action)
```

### Kelly Criterion (for sizing decisions)
Optimal fraction to allocate:
```
f* = (bp - q) / b
Where:
- b = net odds received (profit/risk)
- p = probability of win
- q = probability of loss (1-p)
- f* = fraction of bankroll to allocate
```

### Minimax (Risk-Averse)
Choose action that minimizes maximum possible loss:
```
Best Action = argmin max Loss(Outcome|Action)
```

### Savage Regret Minimization
Minimize maximum regret:
```
Regret = Value(Best Action for Outcome) - Value(Chosen Action)
Best Action = argmin max Regret
```

## Strategic Principles

### 1. Account for Sunk Costs
- Past investments should not influence future decisions
- Evaluate decisions based on marginal costs/benefits only
- "Don't throw good money after bad"

### 2. Option Value
- Preserve flexibility when uncertainty is high
- Delay irreversible decisions when possible
- Value of waiting = information gained

### 3. Robustness Testing
- Test strategy against parameter variations
- Identify critical assumptions
- Plan for scenario where assumptions fail

### 4. Exit Conditions
- Define clear exit criteria before entering
- Include stop-losses (financial and temporal)
- Plan for both success and failure scenarios

### 5. Asymmetric Payoffs
- Prefer strategies with limited downside, unlimited upside
- Avoid strategies with unlimited downside, limited upside
- Consider convexity (positive gamma)

## Monte Carlo Simulation

Use Monte Carlo to test robustness:

1. **Define Parameters** → Identify uncertain parameters
2. **Set Distributions** → Assign probability distributions
3. **Run Simulations** → 10,000+ iterations
4. **Analyze Distribution** → Mean, median, percentiles
5. **Identify Tail Risks** → 5th and 95th percentile outcomes
6. **Adjust Strategy** → Modify based on simulation results

## Calibration Guidelines

### Probability Calibration
- Use historical base rates when available
- Adjust for specific context
- Be explicit about uncertainty ranges
- Update with new information (Bayesian)

### Value Assignment
- Use utility functions for non-linear value
- Account for risk aversion
- Consider time preferences (discount rates)
- Include non-monetary factors

### Risk Assessment
- Distinguish between risk (known probabilities) and uncertainty (unknown)
- Use scenario planning for deep uncertainty
- Build in safety margins
- Monitor leading indicators

## Workflow

1. **Detect strategy query** → User asks for decision framework, strategy, or optimization
2. **Identify decision structure** → Map nodes, branches, outcomes
3. **Assign probabilities and values** → Use Bayesian reasoning
4. **Build decision tree** → Run `decision-nets.py`
5. **Calculate expected values** → Optimize for risk-adjusted return
6. **Run Monte Carlo** → Test robustness
7. **Present strategy** → Show optimal path, exit conditions, risk profile
