#!/usr/bin/env python3
"""
Reusable confidence scoring across domains
Scores claims 0-100% with bias detection
"""

import argparse
import json
import sys
import re
from typing import Dict, List, Tuple

# Add the Engram skills path
sys.path.insert(0, r'C:\Users\OFFRSTAR0\Engram')

from skills.engram.lmstudio_client import LMStudioClient
import asyncio


def detect_anchoring(text: str) -> Dict:
    """Detect anchoring bias - fixation on first information"""
    indicators = [
        r"first (?:data|number|value|estimate)",
        r"initial (?:price|value|estimate)",
        r"started at",
        r"originally (?:said|estimated|priced)"
    ]
    
    matches = []
    for pattern in indicators:
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(pattern)
    
    return {
        "detected": len(matches) > 0,
        "severity": "medium" if len(matches) > 1 else "low" if matches else "none",
        "matches": matches
    }


def detect_availability(text: str) -> Dict:
    """Detect availability heuristic - overweighting recent events"""
    indicators = [
        r"recently",
        r"just (?:happened|occurred)",
        r"(?:last|this) (?:week|month|year)",
        r"(?:remember|recall) when",
        r"(?:big|major) (?:news|event)"
    ]
    
    matches = []
    for pattern in indicators:
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(pattern)
    
    return {
        "detected": len(matches) > 0,
        "severity": "medium" if len(matches) > 2 else "low" if matches else "none",
        "matches": matches
    }


def detect_confirmation_bias(text: str) -> Dict:
    """Detect confirmation bias - seeking confirming evidence"""
    indicators = [
        r"proves (?:that|my)",
        r"confirms (?:that|my)",
        r"as I expected",
        r"I knew",
        r"obviously",
        r"clearly shows"
    ]
    
    matches = []
    for pattern in indicators:
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(pattern)
    
    return {
        "detected": len(matches) > 0,
        "severity": "high" if len(matches) > 2 else "medium" if len(matches) > 1 else "low" if matches else "none",
        "matches": matches
    }


def detect_hindsight(text: str) -> Dict:
    """Detect hindsight bias - overestimating prior knowledge"""
    indicators = [
        r"I knew (?:it|this) would",
        r"(?:obvious|clear) (?:that|in) hindsight",
        r"should have (?:seen|known)",
        r"everyone knew",
        r"predictable"
    ]
    
    matches = []
    for pattern in indicators:
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(pattern)
    
    return {
        "detected": len(matches) > 0,
        "severity": "medium" if len(matches) > 1 else "low" if matches else "none",
        "matches": matches
    }


def detect_authority_bias(text: str) -> Dict:
    """Detect authority bias - over-reliance on authority"""
    indicators = [
        r"expert says",
        r"according to (?:the|an) expert",
        r"(?:famous|renowned) (?:analyst|expert)",
        r"(?:they|he|she) is an expert",
        r"source said"
    ]
    
    matches = []
    for pattern in indicators:
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(pattern)
    
    return {
        "detected": len(matches) > 0,
        "severity": "low" if matches else "none",
        "matches": matches
    }


def calculate_confidence_score(claim: str, evidence: str, bias_results: Dict) -> float:
    """Calculate confidence score based on evidence quality and biases"""
    
    # Base confidence from evidence length/quality
    base_score = min(0.5, len(evidence) / 2000)  # Cap at 0.5 for evidence alone
    
    # Evidence quality indicators
    quality_boost = 0.0
    if re.search(r"\d+\.?\d*%", evidence):  # Contains percentages
        quality_boost += 0.1
    if re.search(r"\d{4}-\d{2}-\d{2}", evidence):  # Contains dates
        quality_boost += 0.05
    if len(evidence.split()) > 50:  # Substantial evidence
        quality_boost += 0.1
    if re.search(r"(?:study|research|data|report)", evidence, re.IGNORECASE):
        quality_boost += 0.1
    
    # Bias penalties
    bias_penalty = 0.0
    for bias_name, bias_data in bias_results.items():
        if bias_data.get("detected"):
            severity = bias_data.get("severity", "low")
            if severity == "high":
                bias_penalty += 0.15
            elif severity == "medium":
                bias_penalty += 0.1
            else:
                bias_penalty += 0.05
    
    # Calculate final score
    confidence = base_score + quality_boost - bias_penalty
    return max(0.0, min(1.0, confidence))  # Clamp to [0, 1]


def build_confidence_breakdown(claim: str, evidence: str, bias_results: Dict) -> Dict:
    """Build detailed confidence breakdown"""
    
    # Evidence quality (0-1)
    evidence_quality = min(1.0, len(evidence) / 1000)
    if re.search(r"(?:study|research|data|source)", evidence, re.IGNORECASE):
        evidence_quality = min(1.0, evidence_quality + 0.2)
    
    # Logical coherence (0-1) - simplified check
    logical_coherence = 0.7  # Default assumption
    if len(claim.split()) > 5:  # Non-trivial claim
        logical_coherence = 0.8
    if not re.search(r"\b(but|however|although)\b", claim, re.IGNORECASE):
        logical_coherence += 0.1  # No contradictions detected
    
    # Source credibility (0-1)
    source_credibility = 0.5  # Default
    if re.search(r"(?:official|government|academic|peer-reviewed)", evidence, re.IGNORECASE):
        source_credibility = 0.8
    elif re.search(r"(?:report|study|survey)", evidence, re.IGNORECASE):
        source_credibility = 0.7
    
    # Consistency (0-1)
    consistency = 0.7
    if bias_results.get("confirmation_bias", {}).get("detected"):
        consistency -= 0.2
    if bias_results.get("anchoring", {}).get("detected"):
        consistency -= 0.1
    
    return {
        "evidence_quality": round(evidence_quality, 2),
        "logical_coherence": round(logical_coherence, 2),
        "source_credibility": round(source_credibility, 2),
        "consistency": round(max(0, consistency), 2)
    }


def estimate_implied_probability(funding_rates: List[float], price: float) -> float:
    """Estimate probability from funding rates"""
    if not funding_rates:
        return 0.5
    
    avg_rate = sum(funding_rates) / len(funding_rates)
    # Normalize to probability (simplified model)
    probability = 0.5 + (avg_rate * 10)
    return max(0.0, min(1.0, probability))


def calculate_kelly_fraction(edge: float, odds: float) -> float:
    """
    Kelly criterion position sizing
    f* = (bp - q) / b = (b*edge - 1) / b
    
    Args:
        edge: Probability of winning (0-1)
        odds: Net odds received (profit/risk)
    
    Returns:
        Optimal fraction of bankroll to allocate
    """
    if odds <= 0 or edge <= 0 or edge >= 1:
        return 0.0
    
    q = 1 - edge  # Probability of loss
    kelly = (odds * edge - q) / odds
    
    # Use half-Kelly for safety
    half_kelly = kelly / 2
    
    return max(0.0, min(half_kelly, 0.25))  # Cap at 25%


async def score_claim(claim: str, evidence: str, bias_check: bool = True) -> Dict:
    """
    Score claim 0-100% with bias detection
    
    Args:
        claim: The claim to evaluate
        evidence: Supporting evidence
        bias_check: Whether to detect cognitive biases
    
    Returns:
        JSON with confidence score, reasoning trace, bias checks
    """
    
    # Detect biases
    bias_results = {}
    if bias_check:
        combined_text = f"{claim} {evidence}"
        bias_results = {
            "anchoring": detect_anchoring(combined_text),
            "availability": detect_availability(combined_text),
            "confirmation_bias": detect_confirmation_bias(combined_text),
            "hindsight": detect_hindsight(combined_text),
            "authority": detect_authority_bias(combined_text)
        }
    
    # Calculate confidence
    confidence = calculate_confidence_score(claim, evidence, bias_results)
    
    # Build breakdown
    breakdown = build_confidence_breakdown(claim, evidence, bias_results)
    
    # Build reasoning trace
    reasoning = [
        {
            "step": 1,
            "description": "Extracted claim and evidence",
            "evidence": f"Claim length: {len(claim)} chars, Evidence length: {len(evidence)} chars"
        },
        {
            "step": 2,
            "description": "Evaluated evidence quality",
            "evidence": f"Evidence quality score: {breakdown['evidence_quality']}"
        }
    ]
    
    if bias_check:
        detected_biases = [k for k, v in bias_results.items() if v.get("detected")]
        reasoning.append({
            "step": 3,
            "description": "Completed bias detection scan",
            "evidence": f"Detected biases: {detected_biases if detected_biases else 'None'}"
        })
    
    # Build output
    output = {
        "claim": claim,
        "confidence": round(confidence, 2),
        "confidence_breakdown": breakdown,
        "reasoning": reasoning,
        "biases_detected": [
            {
                "bias": k,
                "severity": v["severity"],
                "description": f"{k.replace('_', ' ').title()} bias detected" if v["detected"] else f"No {k.replace('_', ' ')} bias"
            }
            for k, v in bias_results.items() if bias_check
        ],
        "evidence_assessment": {
            "supporting": [evidence[:200] + "..." if len(evidence) > 200 else evidence],
            "contradicting": [],
            "missing": []
        },
        "recommendations": [
            "Consider seeking additional independent sources" if confidence < 0.7 else "Evidence quality is acceptable",
            "Review for potential biases" if any(v.get("detected") for v in bias_results.values()) else "No major biases detected"
        ]
    }
    
    return output


def main():
    parser = argparse.ArgumentParser(description="Confidence Scoring")
    parser.add_argument("--claim", required=True, help="The claim to evaluate")
    parser.add_argument("--evidence", default="", help="Supporting evidence")
    parser.add_argument("--context", default="", help="Additional context")
    parser.add_argument("--bias-check", action="store_true", default=True, help="Enable bias detection")
    parser.add_argument("--bias-check-only", action="store_true", help="Only run bias detection")
    
    args = parser.parse_args()
    
    if args.bias_check_only:
        # Only run bias detection
        combined_text = f"{args.claim} {args.evidence}"
        bias_results = {
            "anchoring": detect_anchoring(combined_text),
            "availability": detect_availability(combined_text),
            "confirmation_bias": detect_confirmation_bias(combined_text),
            "hindsight": detect_hindsight(combined_text),
            "authority": detect_authority_bias(combined_text)
        }
        print(json.dumps(bias_results, indent=2))
    else:
        # Full confidence scoring
        result = asyncio.run(score_claim(args.claim, args.evidence, args.bias_check))
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
