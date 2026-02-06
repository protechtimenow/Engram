#!/usr/bin/env python3
"""
Universal Confidence Scoring - Engram Neural Core
Provides 0-100% confidence scoring with bias detection across all domains.

Usage:
    python confidence_scoring.py --claim "Bitcoin will reach $100k" --evidence "Historical patterns"
    python confidence_scoring.py --claim "ETH is undervalued" --bias-check --domain trading
"""

import argparse
import json
import sys
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Domain(Enum):
    """Analysis domains."""
    TRADING = "trading"
    RESEARCH = "research"
    STRATEGY = "strategy"
    JUDGMENT = "judgment"


class BiasType(Enum):
    """Cognitive bias types."""
    CONFIRMATION = "confirmation_bias"
    ANCHORING = "anchoring_bias"
    RECENCY = "recency_bias"
    OVERCONFIDENCE = "overconfidence"
    SURVIVORSHIP = "survivorship_bias"
    HINDSIGHT = "hindsight_bias"
    AVAILABILITY = "availability_heuristic"


@dataclass
class BiasDetection:
    """Detected bias information."""
    bias_type: str
    confidence: float
    evidence: str
    mitigation: str


@dataclass
class ConfidenceResult:
    """Confidence scoring result."""
    claim: str
    domain: str
    confidence_score: float  # 0-100
    uncertainty_range: tuple  # (min, max)
    evidence_strength: float  # 0-1
    logical_consistency: float  # 0-1
    biases_detected: List[BiasDetection]
    key_assumptions: List[str]
    missing_information: List[str]
    recommendation: str


class ConfidenceScorer:
    """Universal confidence scoring engine."""
    
    # Bias detection patterns
    BIAS_PATTERNS = {
        BiasType.CONFIRMATION: [
            r"obviously|clearly|certainly|definitely",
            r"everyone knows|it's well known",
            r"only a fool would|anyone can see"
        ],
        BiasType.ANCHORING: [
            r"started at|began at|originally",
            r"compared to|relative to",
            r"back when it was"
        ],
        BiasType.RECENCY: [
            r"recently|lately|these days",
            r"just happened|last week|yesterday",
            r"trending now|current hype"
        ],
        BiasType.OVERCONFIDENCE: [
            r"guaranteed|sure thing|can't lose",
            r"100%|absolutely|no doubt",
            r"always|never|every time"
        ],
        BiasType.AVAILABILITY: [
            r"I heard|someone said|people are saying",
            r"in the news|media coverage",
            r"everyone is talking about"
        ]
    }
    
    def __init__(self, domain: Domain = Domain.JUDGMENT):
        self.domain = domain
        
    def score(self, claim: str, evidence: Optional[str] = None,
              bias_check: bool = True) -> ConfidenceResult:
        """
        Score confidence of a claim.
        
        Args:
            claim: The claim to evaluate
            evidence: Supporting evidence
            bias_check: Whether to check for cognitive biases
            
        Returns:
            ConfidenceResult with detailed analysis
        """
        biases = []
        if bias_check:
            biases = self._detect_biases(claim, evidence or "")
        
        evidence_strength = self._assess_evidence(claim, evidence)
        logical_consistency = self._check_consistency(claim)
        
        # Calculate base confidence
        base_confidence = (evidence_strength * 40 + 
                          logical_consistency * 30 + 
                          (1 - len(biases) * 0.1) * 30)
        
        # Adjust for domain
        domain_adjustment = self._domain_adjustment()
        
        final_score = max(0, min(100, base_confidence + domain_adjustment))
        
        # Calculate uncertainty range
        uncertainty = self._calculate_uncertainty(biases, evidence)
        
        return ConfidenceResult(
            claim=claim,
            domain=self.domain.value,
            confidence_score=round(final_score, 1),
            uncertainty_range=(
                round(max(0, final_score - uncertainty), 1),
                round(min(100, final_score + uncertainty), 1)
            ),
            evidence_strength=round(evidence_strength, 2),
            logical_consistency=round(logical_consistency, 2),
            biases_detected=biases,
            key_assumptions=self._extract_assumptions(claim),
            missing_information=self._identify_gaps(claim, evidence),
            recommendation=self._generate_recommendation(final_score, biases)
        )
    
    def _detect_biases(self, claim: str, evidence: str) -> List[BiasDetection]:
        """Detect cognitive biases in text."""
        biases = []
        text = f"{claim} {evidence}".lower()
        
        for bias_type, patterns in self.BIAS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    biases.append(BiasDetection(
                        bias_type=bias_type.value,
                        confidence=0.7,
                        evidence=f"Pattern matched: '{pattern}'",
                        mitigation=self._get_mitigation(bias_type)
                    ))
                    break
        
        return biases
    
    def _get_mitigation(self, bias_type: BiasType) -> str:
        """Get mitigation strategy for bias."""
        mitigations = {
            BiasType.CONFIRMATION: "Actively seek disconfirming evidence",
            BiasType.ANCHORING: "Consider multiple reference points",
            BiasType.RECENCY: "Look at longer historical trends",
            BiasType.OVERCONFIDENCE: "Apply 50% confidence discount",
            BiasType.AVAILABILITY: "Seek data beyond personal exposure"
        }
        return mitigations.get(bias_type, "Review with fresh perspective")
    
    def _assess_evidence(self, claim: str, evidence: Optional[str]) -> float:
        """Assess strength of evidence (0-1)."""
        if not evidence:
            return 0.3
        
        score = 0.5
        
        # Check for data/numbers
        if re.search(r'\d+\.?\d*%?', evidence):
            score += 0.15
        
        # Check for sources/references
        if re.search(r'(study|research|data|source|according to)', evidence, re.I):
            score += 0.15
        
        # Check for specificity
        if len(evidence) > 100:
            score += 0.1
        
        return min(1.0, score)
    
    def _check_consistency(self, claim: str) -> float:
        """Check logical consistency (0-1)."""
        # Placeholder - would use more sophisticated logic
        return 0.75
    
    def _domain_adjustment(self) -> float:
        """Adjust score based on domain characteristics."""
        adjustments = {
            Domain.TRADING: -5,  # Markets are uncertain
            Domain.RESEARCH: 0,
            Domain.STRATEGY: -3,
            Domain.JUDGMENT: -2
        }
        return adjustments.get(self.domain, 0)
    
    def _calculate_uncertainty(self, biases: List[BiasDetection], 
                               evidence: Optional[str]) -> float:
        """Calculate uncertainty range."""
        base = 10
        base += len(biases) * 5
        if not evidence:
            base += 10
        return min(30, base)
    
    def _extract_assumptions(self, claim: str) -> List[str]:
        """Extract key assumptions from claim."""
        assumptions = []
        
        # Look for conditional statements
        if re.search(r'if|assuming|provided that', claim, re.I):
            assumptions.append("Conditional outcome depends on stated requirements")
        
        # Look for temporal assumptions
        if re.search(r'will|going to|future', claim, re.I):
            assumptions.append("Future conditions remain favorable")
        
        # Look for causation
        if re.search(r'because|causes|leads to|results in', claim, re.I):
            assumptions.append("Causal relationship holds as stated")
        
        if not assumptions:
            assumptions.append("Claim assumes current trends continue")
        
        return assumptions
    
    def _identify_gaps(self, claim: str, evidence: Optional[str]) -> List[str]:
        """Identify missing information."""
        gaps = []
        
        if not evidence:
            gaps.append("No supporting evidence provided")
        
        if not re.search(r'\d', claim + (evidence or "")):
            gaps.append("Lack of quantitative data")
        
        if not re.search(r'(time|date|when|by)', claim + (evidence or ""), re.I):
            gaps.append("No timeframe specified")
        
        return gaps if gaps else ["Contextual factors not fully explored"]
    
    def _generate_recommendation(self, score: float, 
                                  biases: List[BiasDetection]) -> str:
        """Generate recommendation based on score."""
        if score >= 80:
            return "HIGH_CONFIDENCE: Suitable for action with standard risk management"
        elif score >= 60:
            return "MODERATE_CONFIDENCE: Proceed with caution and additional verification"
        elif score >= 40:
            return "LOW_CONFIDENCE: Requires more research before acting"
        else:
            return "INSUFFICIENT_CONFIDENCE: Do not act based on this claim alone"


def format_output(result: ConfidenceResult, format_type: str = "text") -> str:
    """Format confidence result."""
    if format_type == "json":
        return json.dumps(asdict(result), indent=2, default=str)
    
    bias_text = ""
    if result.biases_detected:
        bias_text = "\n  ⚠️  BIASES DETECTED:\n" + \
            "\n".join(f"    • {b.bias_type} ({b.confidence:.0%} confidence)\n" +
                     f"      Mitigation: {b.mitigation}" for b in result.biases_detected)
    else:
        bias_text = "\n  ✅ No significant biases detected"
    
    output = f"""
╔══════════════════════════════════════════════════════════════╗
║              CONFIDENCE SCORING RESULT                        ║
╠══════════════════════════════════════════════════════════════╣
  Domain: {result.domain.upper()}
  
  📝 CLAIM:
    "{result.claim}"
  
  📊 CONFIDENCE: {result.confidence_score:.1f}%
     Range: {result.uncertainty_range[0]:.1f}% - {result.uncertainty_range[1]:.1f}%
  
  📈 FACTORS:
    • Evidence Strength: {result.evidence_strength:.0%}
    • Logical Consistency: {result.logical_consistency:.0%}{bias_text}
  
  🔑 KEY ASSUMPTIONS:
    {chr(10).join('    • ' + a for a in result.key_assumptions)}
  
  ❓ MISSING INFO:
    {chr(10).join('    • ' + m for m in result.missing_information)}
  
  💡 RECOMMENDATION:
    {result.recommendation}
╚══════════════════════════════════════════════════════════════╝
"""
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Score confidence of claims with bias detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --claim "Bitcoin will reach $100k" --evidence "Halving cycle history"
  %(prog)s --claim "ETH is undervalued" --domain trading --bias-check
  %(prog)s --claim "Strategy X is optimal" --domain strategy --output json
        """
    )
    
    parser.add_argument(
        "--claim", "-c",
        required=True,
        help="Claim to evaluate"
    )
    parser.add_argument(
        "--evidence", "-e",
        help="Supporting evidence"
    )
    parser.add_argument(
        "--domain", "-d",
        choices=[d.value for d in Domain],
        default="judgment",
        help="Analysis domain"
    )
    parser.add_argument(
        "--bias-check",
        action="store_true",
        help="Enable bias detection"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    # Run scoring
    domain = Domain(args.domain)
    scorer = ConfidenceScorer(domain=domain)
    result = scorer.score(
        claim=args.claim,
        evidence=args.evidence,
        bias_check=args.bias_check
    )
    
    # Output results
    print(format_output(result, args.output))
    
    # Exit code based on confidence
    if result.confidence_score >= 70:
        return 0
    elif result.confidence_score >= 50:
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())
