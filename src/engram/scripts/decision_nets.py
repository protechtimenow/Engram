#!/usr/bin/env python3
"""
Decision network builder
Builds decision trees with Bayesian probabilities
"""

import argparse
import json
import random
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class DecisionNodeType(Enum):
    DECISION = "decision"
    CHANCE = "chance"
    TERMINAL = "terminal"


@dataclass
class DecisionNode:
    name: str
    node_type: DecisionNodeType
    children: List['DecisionNode'] = None
    probability: float = 1.0
    value: float = 0.0
    description: str = ""
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


def build_decision_tree(nodes_config: List[Dict], probabilities: Dict[str, float]) -> DecisionNode:
    """
    Build decision tree from configuration
    
    Args:
        nodes_config: List of node configurations
        probabilities: Probabilities for each branch
    
    Returns:
        Root DecisionNode
    """
    if not nodes_config:
        return None
    
    # Build nodes
    node_map = {}
    for config in nodes_config:
        node = DecisionNode(
            name=config["name"],
            node_type=DecisionNodeType(config.get("type", "decision")),
            probability=probabilities.get(config["name"], 1.0),
            value=config.get("value", 0.0),
            description=config.get("description", "")
        )
        node_map[config["name"]] = node
    
    # Build tree structure
    for config in nodes_config:
        node = node_map[config["name"]]
        for child_name in config.get("children", []):
            if child_name in node_map:
                node.children.append(node_map[child_name])
    
    # Find root (node with no parent)
    all_children = set()
    for config in nodes_config:
        all_children.update(config.get("children", []))
    
    root_name = None
    for config in nodes_config:
        if config["name"] not in all_children:
            root_name = config["name"]
            break
    
    return node_map.get(root_name) if root_name else None


def calculate_expected_value(node: DecisionNode, depth: int = 0) -> float:
    """
    Calculate expected value for a decision tree
    
    Args:
        node: Current node
        depth: Current depth (for recursion)
    
    Returns:
        Expected value
    """
    if not node.children:
        return node.value
    
    if node.node_type == DecisionNodeType.DECISION:
        # Choose child with max expected value
        return max(calculate_expected_value(child, depth + 1) for child in node.children)
    
    elif node.node_type == DecisionNodeType.CHANCE:
        # Calculate weighted average
        total_ev = 0.0
        total_prob = 0.0
        for child in node.children:
            child_ev = calculate_expected_value(child, depth + 1)
            total_ev += child.probability * child_ev
            total_prob += child.probability
        return total_ev / total_prob if total_prob > 0 else 0.0
    
    else:  # TERMINAL
        return node.value


def find_optimal_path(node: DecisionNode, path: List[str] = None) -> List[str]:
    """
    Find optimal decision path
    
    Args:
        node: Current node
        path: Current path
    
    Returns:
        Optimal path as list of node names
    """
    if path is None:
        path = []
    
    path.append(node.name)
    
    if not node.children:
        return path
    
    if node.node_type == DecisionNodeType.DECISION:
        # Choose child with max expected value
        best_child = max(node.children, key=lambda c: calculate_expected_value(c))
        return find_optimal_path(best_child, path)
    
    else:
        # For chance nodes, return path with highest probability child
        best_child = max(node.children, key=lambda c: c.probability)
        return find_optimal_path(best_child, path)


def run_monte_carlo(node: DecisionNode, simulations: int = 1000, parameters: Dict = None) -> Dict:
    """
    Run Monte Carlo simulation for scenario outcomes
    
    Args:
        node: Root decision node
        simulations: Number of simulations
        parameters: Scenario parameters
    
    Returns:
        Simulation results
    """
    results = []
    
    for _ in range(simulations):
        outcome = simulate_path(node, parameters)
        results.append(outcome)
    
    # Calculate statistics
    results.sort()
    n = len(results)
    
    mean = sum(results) / n
    median = results[n // 2] if n % 2 == 1 else (results[n // 2 - 1] + results[n // 2]) / 2
    variance = sum((x - mean) ** 2 for x in results) / n
    std_dev = variance ** 0.5
    
    return {
        "mean": round(mean, 4),
        "median": round(median, 4),
        "std_dev": round(std_dev, 4),
        "min": round(min(results), 4),
        "max": round(max(results), 4),
        "percentiles": {
            "5th": round(results[int(n * 0.05)], 4),
            "25th": round(results[int(n * 0.25)], 4),
            "75th": round(results[int(n * 0.75)], 4),
            "95th": round(results[int(n * 0.95)], 4)
        },
        "simulations": simulations
    }


def simulate_path(node: DecisionNode, parameters: Dict = None) -> float:
    """
    Simulate a single path through the decision tree
    
    Args:
        node: Current node
        parameters: Scenario parameters
    
    Returns:
        Outcome value
    """
    if not node.children:
        # Add some randomness to terminal values
        noise = random.gauss(0, 0.1) if parameters else 0
        return node.value * (1 + noise)
    
    if node.node_type == DecisionNodeType.DECISION:
        # Choose best child (with small randomness)
        best_child = max(node.children, key=lambda c: calculate_expected_value(c))
        return simulate_path(best_child, parameters)
    
    elif node.node_type == DecisionNodeType.CHANCE:
        # Randomly select child based on probabilities
        r = random.random()
        cumulative = 0.0
        for child in node.children:
            cumulative += child.probability
            if r <= cumulative:
                return simulate_path(child, parameters)
        return simulate_path(node.children[-1], parameters)
    
    return node.value


def build_risk_matrix(impacts: List[str], probabilities: Dict[str, float]) -> List[Dict]:
    """
    Build risk matrix mapping scenarios to probabilities and values
    
    Args:
        impacts: List of impact levels (high, medium, low)
        probabilities: Probabilities for each impact
    
    Returns:
        Risk matrix
    """
    matrix = []
    impact_values = {"high": 100, "medium": 50, "low": 10}
    
    for impact in impacts:
        prob = probabilities.get(impact, 0.33)
        value = impact_values.get(impact, 50)
        
        matrix.append({
            "scenario": f"{impact}_impact",
            "impact_level": impact,
            "probability": prob,
            "value": value,
            "risk_score": round(prob * value, 2),
            "severity": "high" if prob * value > 50 else "medium" if prob * value > 20 else "low"
        })
    
    return matrix


def kelly_criterion(edge: float, odds: float) -> float:
    """
    Calculate Kelly criterion fraction
    f* = (bp - q) / b
    
    Args:
        edge: Probability of winning (0-1)
        odds: Net odds received (profit/risk)
    
    Returns:
        Optimal fraction of bankroll (0-1)
    """
    if odds <= 0 or edge <= 0 or edge >= 1:
        return 0.0
    
    q = 1 - edge
    kelly = (odds * edge - q) / odds
    
    # Use half-Kelly for safety
    half_kelly = kelly / 2
    
    return max(0.0, min(half_kelly, 0.25))


def analyze_decision(nodes: List[Dict], probabilities: Dict[str, float], 
                     values: Dict[str, float] = None) -> Dict:
    """
    Complete decision analysis
    
    Args:
        nodes: Node configurations
        probabilities: Probabilities for each node
        values: Values for terminal nodes
    
    Returns:
        Complete analysis results
    """
    # Build tree
    root = build_decision_tree(nodes, probabilities)
    
    if not root:
        return {"error": "Could not build decision tree"}
    
    # Calculate expected values
    ev = calculate_expected_value(root)
    
    # Find optimal path
    optimal_path = find_optimal_path(root)
    
    # Run Monte Carlo
    mc_results = run_monte_carlo(root, simulations=1000)
    
    # Build output
    output = {
        "decision_tree": {
            "root": root.name,
            "structure": serialize_tree(root)
        },
        "expected_value": round(ev, 4),
        "optimal_path": optimal_path,
        "monte_carlo": mc_results,
        "risk_profile": {
            "variance": mc_results["std_dev"] ** 2,
            "worst_case": mc_results["min"],
            "best_case": mc_results["max"],
            "tail_risk": "high" if mc_results["percentiles"]["5th"] < -50 else "medium" if mc_results["percentiles"]["5th"] < -20 else "low"
        },
        "recommendations": generate_recommendations(ev, mc_results)
    }
    
    return output


def serialize_tree(node: DecisionNode) -> Dict:
    """Serialize decision tree to dictionary"""
    return {
        "name": node.name,
        "type": node.node_type.value,
        "probability": node.probability,
        "value": node.value,
        "description": node.description,
        "children": [serialize_tree(child) for child in node.children]
    }


def generate_recommendations(ev: float, mc_results: Dict) -> List[str]:
    """Generate recommendations based on analysis"""
    recommendations = []
    
    if ev > 50:
        recommendations.append("High expected value - consider aggressive strategy")
    elif ev > 20:
        recommendations.append("Moderate expected value - standard approach recommended")
    elif ev > 0:
        recommendations.append("Low expected value - proceed with caution")
    else:
        recommendations.append("Negative expected value - avoid this strategy")
    
    if mc_results["std_dev"] > 30:
        recommendations.append("High variance - consider risk reduction measures")
    
    if mc_results["percentiles"]["5th"] < -30:
        recommendations.append("Significant tail risk - implement stop-losses")
    
    recommendations.append("Use Kelly criterion for position sizing: f* = (bp-q)/b")
    
    return recommendations


def main():
    parser = argparse.ArgumentParser(description="Decision Network Builder")
    parser.add_argument("--nodes", help="JSON array of node configurations")
    parser.add_argument("--probabilities", help="JSON object of node probabilities")
    parser.add_argument("--values", help="JSON object of node values")
    parser.add_argument("--scenario", help="Scenario name")
    parser.add_argument("--parameters", help="Scenario parameters (JSON)")
    parser.add_argument("--monte-carlo", action="store_true", help="Run Monte Carlo simulation")
    parser.add_argument("--risk-matrix", action="store_true", help="Build risk matrix")
    parser.add_argument("--impacts", nargs="+", help="Impact levels for risk matrix")
    parser.add_argument("--kelly", action="store_true", help="Calculate Kelly criterion")
    parser.add_argument("--edge", type=float, help="Edge (win probability) for Kelly")
    parser.add_argument("--odds", type=float, help="Odds for Kelly calculation")
    
    args = parser.parse_args()
    
    if args.kelly and args.edge is not None and args.odds is not None:
        kelly = kelly_criterion(args.edge, args.odds)
        print(json.dumps({
            "kelly_fraction": round(kelly, 4),
            "half_kelly": round(kelly / 2, 4),
            "recommendation": f"Allocate {round(kelly * 100, 2)}% of bankroll (or {round(kelly/2 * 100, 2)}% for safety)"
        }, indent=2))
        return
    
    if args.risk_matrix and args.impacts:
        probs = json.loads(args.probabilities) if args.probabilities else {}
        matrix = build_risk_matrix(args.impacts, probs)
        print(json.dumps({"risk_matrix": matrix}, indent=2))
        return
    
    if args.nodes:
        nodes = json.loads(args.nodes)
        probabilities = json.loads(args.probabilities) if args.probabilities else {}
        values = json.loads(args.values) if args.values else {}
        
        # Merge values into nodes
        for node in nodes:
            if node["name"] in values:
                node["value"] = values[node["name"]]
        
        result = analyze_decision(nodes, probabilities, values)
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps({"error": "No nodes provided"}, indent=2))


if __name__ == "__main__":
    main()
