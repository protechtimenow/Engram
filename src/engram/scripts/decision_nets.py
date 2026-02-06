#!/usr/bin/env python3
"""
Decision Frameworks - Engram Neural Core
Bayesian networks, Monte Carlo simulation, and Kelly criterion calculations.

Usage:
    python decision_nets.py --kelly --edge 0.6 --odds 2.0
    python decision_nets.py --bayesian --nodes "[A,B,C]" --probabilities "{...}"
    python decision_nets.py --monte-carlo --simulations 10000 --win-rate 0.55
"""

import argparse
import json
import sys
import random
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class DecisionType(Enum):
    """Types of decision frameworks."""
    KELLY = "kelly"
    BAYESIAN = "bayesian"
    MONTE_CARLO = "monte_carlo"
    EXPECTED_VALUE = "expected_value"


@dataclass
class KellyResult:
    """Kelly criterion calculation result."""
    edge: float
    odds: float
    win_probability: float
    lose_probability: float
    full_kelly: float  # Optimal fraction
    half_kelly: float  # Conservative
    quarter_kelly: float  # Very conservative
    expected_growth: float
    risk_of_ruin: float


@dataclass
class BayesianNode:
    """Node in Bayesian network."""
    name: str
    probability: float
    parents: List[str]
    conditional_probabilities: Dict[Tuple, float]


@dataclass
class BayesianResult:
    """Bayesian inference result."""
    nodes: List[BayesianNode]
    posterior_probabilities: Dict[str, float]
    most_likely_state: str
    confidence: float


@dataclass
class MonteCarloResult:
    """Monte Carlo simulation result."""
    simulations: int
    win_rate: float
    avg_return: float
    max_drawdown: float
    sharpe_ratio: float
    percentile_5: float
    percentile_95: float
    probability_profit: float
    expected_value: float


@dataclass
class ExpectedValueResult:
    """Expected value calculation result."""
    scenarios: List[Dict[str, Any]]
    expected_value: float
    best_case: Dict[str, Any]
    worst_case: Dict[str, Any]
    risk_adjusted_return: float


class DecisionEngine:
    """Decision framework calculations."""
    
    def kelly_criterion(self, edge: float, odds: float, 
                        win_probability: Optional[float] = None) -> KellyResult:
        """
        Calculate Kelly criterion position sizing.
        
        Kelly Formula: f* = (bp - q) / b
        Where:
        - f* = fraction of bankroll to bet
        - b = odds received (decimal - 1)
        - p = probability of winning
        - q = probability of losing (1 - p)
        
        Args:
            edge: Expected edge/profit margin (e.g., 0.6 for 60%)
            odds: Decimal odds (e.g., 2.0 for even money)
            win_probability: Override win probability (calculated from edge if None)
            
        Returns:
            KellyResult with position sizing recommendations
        """
        # Calculate win probability from edge if not provided
        if win_probability is None:
            # Simplified: edge implies win rate
            win_probability = min(0.95, max(0.05, 0.5 + edge / 2))
        
        lose_probability = 1 - win_probability
        
        # Kelly calculation: f* = (bp - q) / b
        # b = odds - 1 (net odds)
        b = odds - 1
        full_kelly = (b * win_probability - lose_probability) / b if b > 0 else 0
        
        # Ensure valid range
        full_kelly = max(0, min(1, full_kelly))
        
        # Conservative fractions
        half_kelly = full_kelly / 2
        quarter_kelly = full_kelly / 4
        
        # Expected growth rate
        if full_kelly > 0:
            expected_growth = (win_probability * math.log(1 + full_kelly * b) + 
                             lose_probability * math.log(1 - full_kelly))
        else:
            expected_growth = 0
        
        # Risk of ruin (simplified)
        if full_kelly > 0.5:
            risk_of_ruin = 0.3
        elif full_kelly > 0.25:
            risk_of_ruin = 0.1
        else:
            risk_of_ruin = 0.02
        
        return KellyResult(
            edge=edge,
            odds=odds,
            win_probability=win_probability,
            lose_probability=lose_probability,
            full_kelly=round(full_kelly * 100, 2),
            half_kelly=round(half_kelly * 100, 2),
            quarter_kelly=round(quarter_kelly * 100, 2),
            expected_growth=round(expected_growth * 100, 2),
            risk_of_ruin=round(risk_of_ruin * 100, 2)
        )
    
    def bayesian_inference(self, nodes_config: List[Dict], 
                          evidence: Dict[str, bool]) -> BayesianResult:
        """
        Perform Bayesian network inference.
        
        Args:
            nodes_config: List of node configurations
            evidence: Observed evidence
            
        Returns:
            BayesianResult with posterior probabilities
        """
        nodes = []
        for config in nodes_config:
            node = BayesianNode(
                name=config['name'],
                probability=config.get('probability', 0.5),
                parents=config.get('parents', []),
                conditional_probabilities=config.get('conditional_probabilities', {})
            )
            nodes.append(node)
        
        # Simplified inference (would use proper Bayesian network library)
        posterior = {}
        for node in nodes:
            if node.name in evidence:
                posterior[node.name] = 1.0 if evidence[node.name] else 0.0
            else:
                # Update based on parents
                prob = node.probability
                for parent in node.parents:
                    if parent in evidence and evidence[parent]:
                        prob = min(0.95, prob * 1.5)
                    elif parent in evidence:
                        prob = max(0.05, prob * 0.5)
                posterior[node.name] = round(prob, 3)
        
        most_likely = max(posterior, key=posterior.get)
        confidence = posterior[most_likely]
        
        return BayesianResult(
            nodes=nodes,
            posterior_probabilities=posterior,
            most_likely_state=most_likely,
            confidence=round(confidence * 100, 1)
        )
    
    def monte_carlo_simulation(self, simulations: int = 10000,
                               win_rate: float = 0.5,
                               avg_win: float = 1.0,
                               avg_loss: float = -1.0,
                               initial_capital: float = 10000,
                               bet_size: float = 0.1) -> MonteCarloResult:
        """
        Run Monte Carlo simulation for trading strategy.
        
        Args:
            simulations: Number of simulation runs
            win_rate: Probability of winning trade
            avg_win: Average win amount (%)
            avg_loss: Average loss amount (%)
            initial_capital: Starting capital
            bet_size: Fraction of capital per trade
            
        Returns:
            MonteCarloResult with simulation statistics
        """
        final_returns = []
        max_drawdowns = []
        
        for _ in range(simulations):
            capital = initial_capital
            peak = capital
            drawdown = 0
            trades = 100  # Simulate 100 trades
            
            for _ in range(trades):
                if random.random() < win_rate:
                    # Win
                    capital *= (1 + bet_size * avg_win / 100)
                else:
                    # Loss
                    capital *= (1 + bet_size * avg_loss / 100)
                
                # Track drawdown
                if capital > peak:
                    peak = capital
                dd = (peak - capital) / peak
                drawdown = max(drawdown, dd)
            
            final_returns.append((capital - initial_capital) / initial_capital)
            max_drawdowns.append(drawdown)
        
        # Calculate statistics
        final_returns.sort()
        n = len(final_returns)
        
        avg_return = sum(final_returns) / n * 100
        max_dd = max(max_drawdowns) * 100
        
        # Percentiles
        p5_idx = int(n * 0.05)
        p95_idx = int(n * 0.95)
        
        # Sharpe ratio approximation
        returns_std = (sum((r - avg_return/100)**2 for r in final_returns) / n) ** 0.5
        sharpe = (avg_return / 100) / returns_std if returns_std > 0 else 0
        
        # Probability of profit
        profitable = sum(1 for r in final_returns if r > 0)
        prob_profit = profitable / n * 100
        
        return MonteCarloResult(
            simulations=simulations,
            win_rate=win_rate * 100,
            avg_return=round(avg_return, 2),
            max_drawdown=round(max_dd, 2),
            sharpe_ratio=round(sharpe, 2),
            percentile_5=round(final_returns[p5_idx] * 100, 2),
            percentile_95=round(final_returns[p95_idx] * 100, 2),
            probability_profit=round(prob_profit, 1),
            expected_value=round(avg_return * prob_profit / 100, 2)
        )
    
    def expected_value(self, scenarios: List[Dict[str, Any]]) -> ExpectedValueResult:
        """
        Calculate expected value from multiple scenarios.
        
        Args:
            scenarios: List of {name, probability, payoff} dictionaries
            
        Returns:
            ExpectedValueResult with EV calculation
        """
        total_prob = sum(s['probability'] for s in scenarios)
        
        # Normalize probabilities if they don't sum to 1
        if total_prob != 1.0:
            for s in scenarios:
                s['probability'] /= total_prob
        
        ev = sum(s['probability'] * s['payoff'] for s in scenarios)
        
        best = max(scenarios, key=lambda x: x['payoff'])
        worst = min(scenarios, key=lambda x: x['payoff'])
        
        # Risk-adjusted (simple variance-based)
        variance = sum(s['probability'] * (s['payoff'] - ev)**2 for s in scenarios)
        risk_adj = ev / (1 + math.sqrt(variance)) if variance > 0 else ev
        
        return ExpectedValueResult(
            scenarios=scenarios,
            expected_value=round(ev, 2),
            best_case=best,
            worst_case=worst,
            risk_adjusted_return=round(risk_adj, 2)
        )


def format_kelly(result: KellyResult, format_type: str = "text") -> str:
    """Format Kelly result."""
    if format_type == "json":
        return json.dumps(asdict(result), indent=2)
    
    return f"""
╔══════════════════════════════════════════════════════════════╗
║              KELLY CRITERION ANALYSIS                         ║
╠══════════════════════════════════════════════════════════════╣
  Inputs:
    • Edge (Advantage): {result.edge:.1%}
    • Odds: {result.odds:.2f}x
    • Win Probability: {result.win_probability:.1%}
  
  📊 POSITION SIZING RECOMMENDATIONS:
    • Full Kelly:   {result.full_kelly:.2f}% of bankroll (AGGRESSIVE)
    • Half Kelly:   {result.half_kelly:.2f}% of bankroll (RECOMMENDED)
    • Quarter Kelly: {result.quarter_kelly:.2f}% of bankroll (CONSERVATIVE)
  
  📈 EXPECTED GROWTH: {result.expected_growth:.2f}%
  ⚠️  RISK OF RUIN: {result.risk_of_ruin:.1f}%
  
  💡 RECOMMENDATION:
    Use {result.half_kelly:.2f}% (Half Kelly) for optimal 
    growth with manageable risk.
╚══════════════════════════════════════════════════════════════╝
"""


def format_bayesian(result: BayesianResult, format_type: str = "text") -> str:
    """Format Bayesian result."""
    if format_type == "json":
        return json.dumps(asdict(result), indent=2, default=str)
    
    probs = "\n".join(f"    • {k}: {v:.1%}" for k, v in result.posterior_probabilities.items())
    
    return f"""
╔══════════════════════════════════════════════════════════════╗
║              BAYESIAN INFERENCE RESULT                        ║
╠══════════════════════════════════════════════════════════════╣
  Nodes: {len(result.nodes)}
  
  📊 POSTERIOR PROBABILITIES:
{probs}
  
  🎯 MOST LIKELY STATE: {result.most_likely_state}
  📈 CONFIDENCE: {result.confidence:.1f}%
╚══════════════════════════════════════════════════════════════╝
"""


def format_monte_carlo(result: MonteCarloResult, format_type: str = "text") -> str:
    """Format Monte Carlo result."""
    if format_type == "json":
        return json.dumps(asdict(result), indent=2)
    
    return f"""
╔══════════════════════════════════════════════════════════════╗
║              MONTE CARLO SIMULATION                           ║
╠══════════════════════════════════════════════════════════════╣
  Simulations: {result.simulations:,}
  Win Rate: {result.win_rate:.1f}%
  
  📊 RESULTS:
    • Average Return: {result.avg_return:+.2f}%
    • Max Drawdown: {result.max_drawdown:.2f}%
    • Sharpe Ratio: {result.sharpe_ratio:.2f}
    
  📈 DISTRIBUTION:
    • 5th Percentile: {result.percentile_5:+.2f}%
    • 95th Percentile: {result.percentile_95:+.2f}%
    
  🎯 PROBABILITY OF PROFIT: {result.probability_profit:.1f}%
  💰 EXPECTED VALUE: {result.expected_value:+.2f}%
╚══════════════════════════════════════════════════════════════╝
"""


def format_expected_value(result: ExpectedValueResult, format_type: str = "text") -> str:
    """Format Expected Value result."""
    if format_type == "json":
        return json.dumps(asdict(result), indent=2)
    
    scenarios_text = "\n".join(
        f"    • {s['name']}: {s['probability']:.1%} chance → ${s['payoff']:,.2f}"
        for s in result.scenarios
    )
    
    return f"""
╔══════════════════════════════════════════════════════════════╗
║              EXPECTED VALUE ANALYSIS                          ║
╠══════════════════════════════════════════════════════════════╣
  SCENARIOS:
{scenarios_text}
  
  📊 RESULTS:
    • Expected Value: ${result.expected_value:,.2f}
    • Risk-Adjusted: ${result.risk_adjusted_return:,.2f}
    
  🎯 BEST CASE: {result.best_case['name']} (+${result.best_case['payoff']:,.2f})
  ⚠️  WORST CASE: {result.worst_case['name']} (${result.worst_case['payoff']:,.2f})
╚══════════════════════════════════════════════════════════════╝
"""


def main():
    parser = argparse.ArgumentParser(
        description="Decision frameworks for optimal choices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Kelly Criterion
  %(prog)s --kelly --edge 0.6 --odds 2.0
  
  # Bayesian Network
  %(prog)s --bayesian --nodes '[{"name":"bull_market","probability":0.6}]'
  
  # Monte Carlo
  %(prog)s --monte-carlo --simulations 10000 --win-rate 0.55
  
  # Expected Value
  %(prog)s --expected-value --scenarios '[
      {"name":"success","probability":0.3,"payoff":10000},
      {"name":"failure","probability":0.7,"payoff":-2000}
  ]'
        """
    )
    
    # Framework selection
    parser.add_argument("--kelly", action="store_true", help="Kelly criterion")
    parser.add_argument("--bayesian", action="store_true", help="Bayesian inference")
    parser.add_argument("--monte-carlo", action="store_true", help="Monte Carlo simulation")
    parser.add_argument("--expected-value", "--ev", action="store_true", help="Expected value")
    
    # Kelly parameters
    parser.add_argument("--edge", type=float, help="Edge/profit margin (0-1)")
    parser.add_argument("--odds", type=float, help="Decimal odds")
    parser.add_argument("--win-probability", type=float, help="Win probability override")
    
    # Bayesian parameters
    parser.add_argument("--nodes", help="JSON node configuration")
    parser.add_argument("--evidence", help="JSON evidence")
    
    # Monte Carlo parameters
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--win-rate", type=float, help="Trade win rate")
    parser.add_argument("--avg-win", type=float, default=1.0)
    parser.add_argument("--avg-loss", type=float, default=-1.0)
    parser.add_argument("--initial-capital", type=float, default=10000)
    parser.add_argument("--bet-size", type=float, default=0.1)
    
    # Expected value parameters
    parser.add_argument("--scenarios", help="JSON scenarios array")
    
    # Output
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    
    args = parser.parse_args()
    
    engine = DecisionEngine()
    
    # Run selected framework
    if args.kelly:
        if not args.edge or not args.odds:
            parser.error("--kelly requires --edge and --odds")
        result = engine.kelly_criterion(args.edge, args.odds, args.win_probability)
        print(format_kelly(result, args.output))
        return 0 if result.full_kelly > 0 else 1
    
    elif args.bayesian:
        if not args.nodes:
            parser.error("--bayesian requires --nodes")
        nodes = json.loads(args.nodes)
        evidence = json.loads(args.evidence) if args.evidence else {}
        result = engine.bayesian_inference(nodes, evidence)
        print(format_bayesian(result, args.output))
        return 0 if result.confidence > 50 else 1
    
    elif args.monte_carlo:
        if not args.win_rate:
            parser.error("--monte-carlo requires --win-rate")
        result = engine.monte_carlo_simulation(
            args.simulations, args.win_rate, args.avg_win,
            args.avg_loss, args.initial_capital, args.bet_size
        )
        print(format_monte_carlo(result, args.output))
        return 0 if result.probability_profit > 50 else 1
    
    elif args.expected_value:
        if not args.scenarios:
            parser.error("--expected-value requires --scenarios")
        scenarios = json.loads(args.scenarios)
        result = engine.expected_value(scenarios)
        print(format_expected_value(result, args.output))
        return 0 if result.expected_value > 0 else 1
    
    else:
        parser.error("Select a framework: --kelly, --bayesian, --monte-carlo, or --expected-value")


if __name__ == "__main__":
    sys.exit(main())
