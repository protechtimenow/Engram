#!/usr/bin/env python3
"""
Text/data pattern detection
Finds patterns, signals, anomalies in text or data
"""

import argparse
import json
import re
from typing import Dict, List, Any
from collections import Counter


def detect_repeated_patterns(text: str, min_length: int = 3) -> List[Dict]:
    """Detect repeated phrases or patterns in text"""
    words = text.lower().split()
    patterns = []
    
    # Find repeated n-grams
    for n in range(min_length, min(10, len(words))):
        ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
        counts = Counter(ngrams)
        
        for ngram, count in counts.items():
            if count > 1 and len(ngram) > 10:
                patterns.append({
                    "pattern": ngram,
                    "type": "repeated_phrase",
                    "count": count,
                    "confidence": min(0.9, 0.5 + count * 0.1)
                })
    
    return patterns[:5]  # Top 5 patterns


def detect_structural_patterns(text: str) -> List[Dict]:
    """Detect structural patterns (lists, headers, etc.)"""
    patterns = []
    
    # Detect lists
    list_patterns = [
        (r"^\s*[\*\-\+]\s+", "bullet_list"),
        (r"^\s*\d+\.\s+", "numbered_list"),
        (r"^\s*\(\d+\)\s+", "parenthesized_list")
    ]
    
    for pattern, pattern_type in list_patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        if len(matches) > 2:
            patterns.append({
                "pattern": f"{pattern_type}_structure",
                "type": "structural",
                "count": len(matches),
                "confidence": 0.85
            })
    
    # Detect headers
    header_matches = re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE)
    if header_matches:
        patterns.append({
            "pattern": "header_hierarchy",
            "type": "structural",
            "count": len(header_matches),
            "confidence": 0.9
        })
    
    return patterns


def detect_linguistic_patterns(text: str) -> List[Dict]:
    """Detect linguistic patterns (passive voice, complex sentences, etc.)"""
    patterns = []
    
    # Passive voice detection
    passive_indicators = [r"\b(?:was|were|been|be|being)\s+\w+ed\b", r"\b(?:is|are)\s+\w+ed\b"]
    passive_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in passive_indicators)
    if passive_count > 2:
        patterns.append({
            "pattern": "passive_voice",
            "type": "linguistic",
            "count": passive_count,
            "confidence": 0.8
        })
    
    # Complex sentences (multiple clauses)
    complex_indicators = len(re.findall(r"\b(?:although|because|since|while|whereas|however|therefore|thus)\b", text, re.IGNORECASE))
    if complex_indicators > 3:
        patterns.append({
            "pattern": "complex_sentence_structure",
            "type": "linguistic",
            "count": complex_indicators,
            "confidence": 0.75
        })
    
    # Superlatives
    superlatives = len(re.findall(r"\b(?:most|least|best|worst|greatest|smallest|always|never)\b", text, re.IGNORECASE))
    if superlatives > 2:
        patterns.append({
            "pattern": "superlative_usage",
            "type": "linguistic",
            "count": superlatives,
            "confidence": 0.7
        })
    
    return patterns


def detect_anomalies(text: str) -> List[Dict]:
    """Detect anomalies or unusual patterns"""
    anomalies = []
    
    # Sudden shifts in tone
    positive_words = len(re.findall(r"\b(?:good|great|excellent|amazing|best|love|perfect)\b", text, re.IGNORECASE))
    negative_words = len(re.findall(r"\b(?:bad|terrible|awful|worst|hate|horrible|disaster)\b", text, re.IGNORECASE))
    
    if positive_words > 3 and negative_words > 3:
        anomalies.append({
            "anomaly": "tone_inconsistency",
            "description": "Mix of strongly positive and negative language",
            "severity": "medium",
            "confidence": 0.75
        })
    
    # Unusual punctuation patterns
    exclamation_count = text.count('!')
    question_count = text.count('?')
    
    if exclamation_count > 5:
        anomalies.append({
            "anomaly": "excessive_exclamation",
            "description": f"High exclamation mark usage ({exclamation_count})",
            "severity": "low",
            "confidence": 0.8
        })
    
    # Repetitive characters
    repetitive = re.findall(r'(.)\1{3,}', text)
    if repetitive:
        anomalies.append({
            "anomaly": "repetitive_characters",
            "description": f"Repeated characters: {set(repetitive)}",
            "severity": "low",
            "confidence": 0.9
        })
    
    return anomalies


def detect_cognitive_biases(text: str) -> List[Dict]:
    """Detect cognitive biases in text"""
    biases = []
    
    bias_patterns = {
        "anchoring": [
            r"first (?:data|number|value)",
            r"initial (?:price|estimate)",
            r"started at"
        ],
        "availability": [
            r"recently",
            r"just happened",
            r"(?:last|this) (?:week|month)"
        ],
        "confirmation": [
            r"proves that",
            r"confirms",
            r"as I expected",
            r"obviously"
        ],
        "hindsight": [
            r"I knew it would",
            r"obvious in hindsight",
            r"should have known"
        ],
        "authority": [
            r"expert says",
            r"according to",
            r"famous analyst"
        ]
    }
    
    for bias_name, patterns in bias_patterns.items():
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text, re.IGNORECASE))
        
        if matches:
            biases.append({
                "bias": bias_name,
                "severity": "medium" if len(matches) > 2 else "low",
                "matches": matches[:3],
                "confidence": min(0.9, 0.5 + len(matches) * 0.1)
            })
    
    return biases


def detect_logical_fallacies(text: str) -> List[Dict]:
    """Detect logical fallacies in text"""
    fallacies = []
    
    fallacy_patterns = {
        "ad_hominem": [
            r"\b(?:idiot|stupid|moron|clown)\b",
            r"(?:he|she|they) (?:is|are) (?:just|only) a"
        ],
        "straw_man": [
            r"so (?:you're|you are) saying",
            r"basically (?:you|they) think"
        ],
        "false_dichotomy": [
            r"(?:either|or) (?:you|we) (?:are|must)",
            r"only two (?:options|choices|possibilities)"
        ],
        "slippery_slope": [
            r"lead to",
            r"next thing you know",
            r"slippery slope"
        ],
        "appeal_to_emotion": [
            r"think of the (?:children|victims)",
            r"heartless",
            r"cruel"
        ]
    }
    
    for fallacy_name, patterns in fallacy_patterns.items():
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text, re.IGNORECASE))
        
        if matches:
            fallacies.append({
                "fallacy": fallacy_name,
                "description": f"Potential {fallacy_name.replace('_', ' ')} detected",
                "matches": len(matches),
                "confidence": min(0.8, 0.4 + len(matches) * 0.15)
            })
    
    return fallacies


def scan_text(text: str, patterns: List[str] = None) -> Dict:
    """
    Find patterns, signals, anomalies in text
    
    Args:
        text: Text to scan
        patterns: Specific regex patterns to look for (optional)
    
    Returns:
        JSON with patterns found, confidence per pattern, anomalies
    """
    
    results = {
        "patterns": [],
        "anomalies": [],
        "biases_detected": [],
        "logical_fallacies": [],
        "custom_patterns": []
    }
    
    # Detect various pattern types
    results["patterns"].extend(detect_repeated_patterns(text))
    results["patterns"].extend(detect_structural_patterns(text))
    results["patterns"].extend(detect_linguistic_patterns(text))
    
    # Detect anomalies
    results["anomalies"] = detect_anomalies(text)
    
    # Detect biases
    results["biases_detected"] = detect_cognitive_biases(text)
    
    # Detect logical fallacies
    results["logical_fallacies"] = detect_logical_fallacies(text)
    
    # Custom pattern matching
    if patterns:
        for pattern in patterns:
            try:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    results["custom_patterns"].append({
                        "pattern": pattern,
                        "matches": matches,
                        "count": len(matches)
                    })
            except re.error:
                results["custom_patterns"].append({
                    "pattern": pattern,
                    "error": "Invalid regex pattern"
                })
    
    # Calculate overall confidence
    all_confidences = [p.get("confidence", 0.5) for p in results["patterns"]]
    results["overall_confidence"] = round(sum(all_confidences) / len(all_confidences), 2) if all_confidences else 0.5
    
    # Summary statistics
    results["summary"] = {
        "total_patterns": len(results["patterns"]),
        "total_anomalies": len(results["anomalies"]),
        "total_biases": len(results["biases_detected"]),
        "total_fallacies": len(results["logical_fallacies"]),
        "text_length": len(text),
        "word_count": len(text.split())
    }
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Pattern Scan")
    parser.add_argument("--input", required=True, help="Text to scan")
    parser.add_argument("--type", default="text", choices=["text", "data"], help="Input type")
    parser.add_argument("--patterns", nargs="+", help="Custom regex patterns to look for")
    parser.add_argument("--detect-fallacies", action="store_true", help="Detect logical fallacies")
    parser.add_argument("--output-file", help="Save results to file")
    
    args = parser.parse_args()
    
    # Scan text
    results = scan_text(args.input, args.patterns)
    
    # Output results
    output = json.dumps(results, indent=2)
    print(output)
    
    # Save to file if specified
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(output)
        print(f"\nResults saved to {args.output_file}")


if __name__ == "__main__":
    main()
