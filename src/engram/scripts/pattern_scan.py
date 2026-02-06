#!/usr/bin/env python3
"""
Pattern Detection Script - Engram Neural Core
Detects patterns in text/data including cognitive biases and logical fallacies.

Usage:
    python pattern_scan.py --input "Market analysis text..." --detect-fallacies
    python pattern_scan.py --input "data.csv" --pattern-type trend
"""

import argparse
import json
import sys
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class PatternType(Enum):
    """Types of patterns to detect."""
    FALLACY = "fallacy"
    BIAS = "bias"
    TREND = "trend"
    ANOMALY = "anomaly"
    SENTIMENT = "sentiment"


class FallacyType(Enum):
    """Logical fallacy types."""
    AD_HOMINEM = "ad_hominem"
    STRAW_MAN = "straw_man"
    APPEAL_TO_AUTHORITY = "appeal_to_authority"
    FALSE_DICHOTOMY = "false_dichotomy"
    SLIPPERY_SLOPE = "slippery_slope"
    CIRCULAR_REASONING = "circular_reasoning"
    POST_HOC = "post_hoc"
    HASTY_GENERALIZATION = "hasty_generalization"


@dataclass
class PatternMatch:
    """Detected pattern information."""
    pattern_type: str
    subtype: str
    confidence: float
    location: Tuple[int, int]  # start, end
    excerpt: str
    explanation: str
    severity: str  # low, medium, high


@dataclass
class ScanResult:
    """Pattern scan result."""
    input_text: str
    patterns_found: List[PatternMatch]
    summary: Dict[str, Any]
    recommendations: List[str]


class PatternScanner:
    """Scans text for various patterns."""
    
    # Logical fallacy patterns
    FALLACY_PATTERNS = {
        FallacyType.AD_HOMINEM: [
            r'\b(you are|he is|she is)\s+\w+\s+(so|therefore|thus)',
            r'\b(only a|just a)\s+\w+\s+would',
            r'\b(person|people)\s+like\s+you'
        ],
        FallacyType.STRAW_MAN: [
            r'\b(so you are saying|so what you mean|you think that)\b',
            r'\b(extreme|absurd|ridiculous)\s+(version|interpretation)',
        ],
        FallacyType.APPEAL_TO_AUTHORITY: [
            r'\b(expert|professor|doctor|study)\s+says',
            r'\b(research|science)\s+(shows|proves|confirms)',
            r'\baccording to\s+\w+\s+(expert|authority)',
        ],
        FallacyType.FALSE_DICHOTOMY: [
            r'\b(either|whether)\s+.+\s+or\s+(nothing|die|fail)',
            r'\b(you are either|it is either)\s+.+,?\s+or\s+',
            r'\b(black and white|all or nothing)\b',
        ],
        FallacyType.SLIPPERY_SLOPE: [
            r'\b(if we|once we|if you)\s+.+,?\s+then\s+.+,?\s+then',
            r'\b(lead to|result in|open the door to)\s+.+,?\s+which\s+',
            r'\b(domino effect|snowball|avalanche)\b',
        ],
        FallacyType.CIRCULAR_REASONING: [
            r'\b(because|since)\s+.+\s+is\s+true',
            r'\b(it is true that|the reason is)\s+because',
        ],
        FallacyType.POST_HOC: [
            r'\b(after|since|ever since)\s+.+\s+,?\s+(happened|occurred)',
            r'\b(following|subsequent to)\s+.+,?\s+we\s+saw',
        ],
        FallacyType.HASTY_GENERALIZATION: [
            r'\b(everyone|everybody|all people)\s+(knows|agrees|thinks)',
            r'\b(always|never|every time)\s+',
            r'\b(based on|from)\s+(one|single|my)\s+(example|experience)',
        ],
    }
    
    # Cognitive bias patterns (overlap with confidence_scoring)
    BIAS_PATTERNS = {
        "confirmation": [
            r'\b(obviously|clearly|undoubtedly)\b',
            r'\b(everyone knows|as we all know)\b',
        ],
        "anchoring": [
            r'\b(started at|began at)\s+\$?\d+',
            r'\b(down from|up from)\s+\$?\d+',
        ],
        "availability": [
            r'\b(i heard|someone said|people are saying)\b',
            r'\b(in the news|on twitter|everyone is talking about)\b',
        ],
        "recency": [
            r'\b(recently|lately|these days|nowadays)\b',
            r'\b(just|only)\s+(last|this)\s+(week|month|year)\b',
        ],
    }
    
    # Sentiment patterns
    SENTIMENT_PATTERNS = {
        "positive": [
            r'\b(bullish|optimistic|growth|moon|pump|rally|breakout)\b',
            r'\b(strong|solid|robust|excellent|outstanding)\b',
        ],
        "negative": [
            r'\b(bearish|pessimistic|crash|dump|correction|breakdown)\b',
            r'\b(weak|fragile|concerning|alarming|dangerous)\b',
        ],
        "uncertainty": [
            r'\b(uncertain|unclear|might|maybe|possibly|could)\b',
            r'\b(volatility|choppy|sideways|ranging|consolidating)\b',
        ],
    }
    
    def __init__(self):
        self.patterns_found = []
    
    def scan(self, text: str, 
             detect_fallacies: bool = True,
             detect_bias: bool = True,
             detect_sentiment: bool = True) -> ScanResult:
        """
        Scan text for patterns.
        
        Args:
            text: Input text to analyze
            detect_fallacies: Check for logical fallacies
            detect_bias: Check for cognitive biases
            detect_sentiment: Analyze sentiment patterns
            
        Returns:
            ScanResult with detected patterns
        """
        self.patterns_found = []
        
        if detect_fallacies:
            self._detect_fallacies(text)
        
        if detect_bias:
            self._detect_bias(text)
        
        if detect_sentiment:
            self._detect_sentiment(text)
        
        return ScanResult(
            input_text=text[:200] + "..." if len(text) > 200 else text,
            patterns_found=self.patterns_found,
            summary=self._generate_summary(),
            recommendations=self._generate_recommendations()
        )
    
    def _detect_fallacies(self, text: str):
        """Detect logical fallacies."""
        for fallacy_type, patterns in self.FALLACY_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    self.patterns_found.append(PatternMatch(
                        pattern_type="fallacy",
                        subtype=fallacy_type.value,
                        confidence=0.75,
                        location=(match.start(), match.end()),
                        excerpt=text[max(0, match.start()-20):min(len(text), match.end()+20)],
                        explanation=self._get_fallacy_explanation(fallacy_type),
                        severity="high"
                    ))
    
    def _detect_bias(self, text: str):
        """Detect cognitive biases."""
        for bias_type, patterns in self.BIAS_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    self.patterns_found.append(PatternMatch(
                        pattern_type="bias",
                        subtype=bias_type,
                        confidence=0.7,
                        location=(match.start(), match.end()),
                        excerpt=text[max(0, match.start()-20):min(len(text), match.end()+20)],
                        explanation=f"Potential {bias_type} bias detected",
                        severity="medium"
                    ))
    
    def _detect_sentiment(self, text: str):
        """Detect sentiment patterns."""
        for sentiment, patterns in self.SENTIMENT_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    self.patterns_found.append(PatternMatch(
                        pattern_type="sentiment",
                        subtype=sentiment,
                        confidence=0.8,
                        location=(match.start(), match.end()),
                        excerpt=text[max(0, match.start()-20):min(len(text), match.end()+20)],
                        explanation=f"{sentiment.capitalize()} sentiment indicator",
                        severity="low"
                    ))
    
    def _get_fallacy_explanation(self, fallacy_type: FallacyType) -> str:
        """Get explanation for fallacy type."""
        explanations = {
            FallacyType.AD_HOMINEM: "Attacking the person instead of the argument",
            FallacyType.STRAW_MAN: "Misrepresenting someone's argument to make it easier to attack",
            FallacyType.APPEAL_TO_AUTHORITY: "Using authority as sole basis for truth",
            FallacyType.FALSE_DICHOTOMY: "Presenting only two options when more exist",
            FallacyType.SLIPPERY_SLOPE: "Claiming one event will inevitably lead to extreme consequences",
            FallacyType.CIRCULAR_REASONING: "Using conclusion as premise",
            FallacyType.POST_HOC: "Assuming causation from correlation",
            FallacyType.HASTY_GENERALIZATION: "Drawing conclusion from insufficient sample",
        }
        return explanations.get(fallacy_type, "Logical fallacy detected")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate scan summary."""
        by_type = {}
        by_severity = {"low": 0, "medium": 0, "high": 0}
        
        for pattern in self.patterns_found:
            by_type[pattern.pattern_type] = by_type.get(pattern.pattern_type, 0) + 1
            by_severity[pattern.severity] = by_severity.get(pattern.severity, 0) + 1
        
        return {
            "total_patterns": len(self.patterns_found),
            "by_type": by_type,
            "by_severity": by_severity,
            "dominant_sentiment": self._get_dominant_sentiment(),
            "risk_level": self._calculate_risk_level(by_severity)
        }
    
    def _get_dominant_sentiment(self) -> str:
        """Determine dominant sentiment."""
        sentiments = {"positive": 0, "negative": 0, "uncertainty": 0}
        for pattern in self.patterns_found:
            if pattern.pattern_type == "sentiment":
                sentiments[pattern.subtype] = sentiments.get(pattern.subtype, 0) + 1
        
        if not sentiments:
            return "neutral"
        return max(sentiments, key=sentiments.get)
    
    def _calculate_risk_level(self, by_severity: Dict[str, int]) -> str:
        """Calculate overall risk level."""
        if by_severity.get("high", 0) > 0:
            return "high"
        elif by_severity.get("medium", 0) > 2:
            return "elevated"
        elif by_severity.get("medium", 0) > 0:
            return "moderate"
        return "low"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on patterns."""
        recs = []
        
        fallacy_count = sum(1 for p in self.patterns_found if p.pattern_type == "fallacy")
        bias_count = sum(1 for p in self.patterns_found if p.pattern_type == "bias")
        
        if fallacy_count > 0:
            recs.append(f"Review and address {fallacy_count} logical fallacy(s) in reasoning")
        
        if bias_count > 0:
            recs.append(f"Consider {bias_count} detected bias(es) when evaluating conclusions")
        
        if not recs:
            recs.append("No significant patterns detected - standard review recommended")
        
        return recs


def format_output(result: ScanResult, format_type: str = "text") -> str:
    """Format scan result."""
    if format_type == "json":
        return json.dumps(asdict(result), indent=2, default=str)
    
    if not result.patterns_found:
        pattern_text = "\n  ✅ No patterns detected"
    else:
        pattern_text = ""
        current_type = None
        for p in sorted(result.patterns_found, key=lambda x: x.pattern_type):
            if p.pattern_type != current_type:
                pattern_text += f"\n  📌 {p.pattern_type.upper()}:\n"
                current_type = p.pattern_type
            pattern_text += f"    [{p.severity.upper()}] {p.subtype}\n"
            pattern_text += f"    Excerpt: \"...{p.excerpt}...\"\n"
            pattern_text += f"    → {p.explanation}\n\n"
    
    output = f"""
╔══════════════════════════════════════════════════════════════╗
║                 PATTERN SCAN RESULTS                          ║
╠══════════════════════════════════════════════════════════════╣
  Input: {result.input_text[:60]}...
  
  📊 SUMMARY:
    • Total Patterns: {result.summary['total_patterns']}
    • Risk Level: {result.summary['risk_level'].upper()}
    • Dominant Sentiment: {result.summary['dominant_sentiment'].upper()}
    
  📈 BREAKDOWN:
    By Type: {', '.join(f"{k}: {v}" for k, v in result.summary['by_type'].items()) or 'None'}
    By Severity: High: {result.summary['by_severity'].get('high', 0)}, 
                 Medium: {result.summary['by_severity'].get('medium', 0)}, 
                 Low: {result.summary['by_severity'].get('low', 0)}
  
  🔍 DETECTED PATTERNS:{pattern_text}
  
  💡 RECOMMENDATIONS:
    {chr(10).join('    • ' + r for r in result.recommendations)}
╚══════════════════════════════════════════════════════════════╝
"""
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Scan text for patterns, biases, and fallacies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input "Market analysis text..." --detect-fallacies
  %(prog)s --input " bullish trend ahead" --detect-sentiment
  %(prog)s --file analysis.txt --detect-bias --output json
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        help="Input text to analyze"
    )
    parser.add_argument(
        "--file", "-f",
        help="File to analyze"
    )
    parser.add_argument(
        "--detect-fallacies",
        action="store_true",
        help="Detect logical fallacies"
    )
    parser.add_argument(
        "--detect-bias",
        action="store_true",
        help="Detect cognitive biases"
    )
    parser.add_argument(
        "--detect-sentiment",
        action="store_true",
        help="Analyze sentiment patterns"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    # Get input text
    if args.file:
        with open(args.file, 'r') as f:
            text = f.read()
    elif args.input:
        text = args.input
    else:
        parser.error("Either --input or --file is required")
    
    # If no detection flags set, enable all
    detect_all = not (args.detect_fallacies or args.detect_bias or args.detect_sentiment)
    
    # Run scan
    scanner = PatternScanner()
    result = scanner.scan(
        text=text,
        detect_fallacies=args.detect_fallacies or detect_all,
        detect_bias=args.detect_bias or detect_all,
        detect_sentiment=args.detect_sentiment or detect_all
    )
    
    # Output results
    print(format_output(result, args.output))
    
    # Exit code based on risk level
    risk_level = result.summary['risk_level']
    if risk_level == "high":
        return 2
    elif risk_level == "elevated":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
