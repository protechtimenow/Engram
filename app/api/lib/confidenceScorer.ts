/**
 * Confidence Scoring Library - TypeScript Version
 * Replaces confidence_scoring.py for Vercel compatibility
 */

export interface BiasDetection {
  bias_type: string;
  confidence: number;
  evidence: string;
  mitigation: string;
}

export interface ConfidenceResult {
  claim: string;
  domain: string;
  confidence_score: number;
  uncertainty_range: [number, number];
  evidence_strength: number;
  logical_consistency: number;
  biases_detected: BiasDetection[];
  key_assumptions: string[];
  missing_information: string[];
  recommendation: string;
}

const BIAS_PATTERNS: Record<string, RegExp[]> = {
  confirmation: [
    /\b(obviously|clearly|undoubtedly|certainly|definitely)\b/i,
    /\b(everyone knows|as we all know)\b/i
  ],
  anchoring: [
    /\b(started at|began at)\s+\$?\d+/i,
    /\b(down from|up from)\s+\$?\d+/i
  ],
  availability: [
    /\b(i heard|someone said|people are saying)\b/i,
    /\b(in the news|everyone is talking about)\b/i
  ],
  overconfidence: [
    /\b(guaranteed|sure thing|can't lose|100%)\b/i,
    /\b(always|never|every time)\b/i
  ]
};

export function scoreConfidence(
  claim: string,
  evidence?: string,
  domain: string = "trading"
): ConfidenceResult {
  const text = `${claim} ${evidence || ''}`.toLowerCase();
  
  // Detect biases
  const biases: BiasDetection[] = [];
  for (const [biasType, patterns] of Object.entries(BIAS_PATTERNS)) {
    for (const pattern of patterns) {
      if (pattern.test(text)) {
        biases.push({
          bias_type: biasType,
          confidence: 0.7,
          evidence: `Pattern matched in text`,
          mitigation: getMitigation(biasType)
        });
        break;
      }
    }
  }
  
  // Assess evidence strength
  let evidenceStrength = 0.3;
  if (evidence) {
    if (/\d+\.?\d*%?/.test(evidence)) evidenceStrength += 0.15;
    if (/(study|research|data|source)/i.test(evidence)) evidenceStrength += 0.15;
    if (evidence.length > 100) evidenceStrength += 0.1;
  }
  evidenceStrength = Math.min(1, evidenceStrength);
  
  // Logical consistency (simplified)
  const logicalConsistency = 0.75;
  
  // Calculate base confidence
  let baseConfidence = (evidenceStrength * 40) + (logicalConsistency * 30) + (1 - biases.length * 0.1) * 30;
  
  // Domain adjustment
  if (domain === "trading") baseConfidence -= 5;
  
  const finalScore = Math.max(0, Math.min(100, baseConfidence));
  const uncertainty = 10 + (biases.length * 5) + (evidence ? 0 : 10);
  
  return {
    claim,
    domain,
    confidence_score: Math.round(finalScore * 10) / 10,
    uncertainty_range: [
      Math.round(Math.max(0, finalScore - uncertainty) * 10) / 10,
      Math.round(Math.min(100, finalScore + uncertainty) * 10) / 10
    ],
    evidence_strength: Math.round(evidenceStrength * 100) / 100,
    logical_consistency: Math.round(logicalConsistency * 100) / 100,
    biases_detected: biases,
    key_assumptions: ["Claim assumes current trends continue"],
    missing_information: evidence ? [] : ["No supporting evidence provided"],
    recommendation: finalScore >= 70 
      ? "HIGH_CONFIDENCE: Suitable for action"
      : finalScore >= 50
      ? "MODERATE_CONFIDENCE: Proceed with caution"
      : "LOW_CONFIDENCE: Requires more research"
  };
}

function getMitigation(biasType: string): string {
  const mitigations: Record<string, string> = {
    confirmation: "Actively seek disconfirming evidence",
    anchoring: "Consider multiple reference points",
    availability: "Seek data beyond personal exposure",
    overconfidence: "Apply 50% confidence discount"
  };
  return mitigations[biasType] || "Review with fresh perspective";
}
