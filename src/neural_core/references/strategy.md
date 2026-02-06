# Strategy Domain Reference

## Core Principles

1. **Expected Value**: Decisions = Probability × Payoff
2. **Optionality**: Preserve flexibility when possible
3. **Asymmetric Opportunities**: Seek convexity (limited downside, unlimited upside)
4. **Robustness**: Plans should work across scenarios

## Decision Frameworks

### Expected Value (EV)
```
EV = Σ(P(outcome) × Payoff(outcome))

Decision Rule:
- EV > 0: Positive expected value
- EV < 0: Negative expected value
- Compare EV across options
```

### Kelly Criterion
```
f* = (bp - q) / b

Where:
- f* = optimal fraction of bankroll
- b = net odds received (decimal odds - 1)
- p = probability of winning
- q = probability of losing (1-p)

Practical Use:
- Full Kelly: Aggressive, high variance
- Half Kelly: Recommended (growth + safety)
- Quarter Kelly: Conservative
```

### Bayesian Updating
```
P(H|E) = P(E|H) × P(H) / P(E)

Start with prior belief
Update with new evidence
Revise probability estimate
Repeat as information arrives
```

### Monte Carlo Simulation
```
1. Define probability distributions for inputs
2. Run thousands of random scenarios
3. Analyze distribution of outcomes
4. Identify risk factors and sensitivities
```

## Scenario Planning

### Best/Worst/Base Case
- **Best Case**: Everything goes right (20% probability)
- **Base Case**: Most likely outcome (50% probability)
- **Worst Case**: Significant problems (30% probability)

### Pre-Mortem Analysis
1. Imagine the decision failed
2. List all reasons why
3. Address preventable failures
4. Plan for unpreventable ones

## Output Format

```
DECISION: (what is being decided)
FRAMEWORK: (Kelly/Bayesian/EV/MC)
SCENARIOS:
  - Best: (outcome + probability)
  - Base: (outcome + probability)
  - Worst: (outcome + probability)
EXPECTED_VALUE: (calculated EV)
RISK_ADJUSTED_RETURN: (accounting for variance)
RECOMMENDATION: (specific action with sizing)
FLEXIBILITY_PRESERVED: (optionality maintained)
```

## Strategy Heuristics

1. **Minimize Regret**: What would you regret more?
2. **Reversibility**: Can you undo the decision?
3. **Information Value**: What info is worth acquiring?
4. **Second-Order Effects**: What happens next?
5. **Margin of Safety**: Build in buffers

## Common Strategic Errors

- **Analysis Paralysis**: Over-optimizing minor decisions
- **Sunk Cost Fallacy**: Continuing due to past investment
- **Planning Fallacy**: Underestimating time/difficulty
- **Narrow Framing**: Not considering alternatives
- **Overconfidence**: Underestimating uncertainty
