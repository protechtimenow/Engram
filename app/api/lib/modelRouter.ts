/**
 * ClawRouter-Style Model Router for Engram A2A
 * Routes queries to cheapest capable model based on complexity
 * 
 * Tiers:
 * - SIMPLE: DeepSeek/Gemini Flash ($0.27-0.60/M) - 99% savings
 * - MEDIUM: GPT-4o-mini/DeepSeek-chat ($0.60-0.42/M) - 99% savings
 * - COMPLEX: Claude Sonnet/GPT-4o ($15-25/M) - Best quality
 * - REASONING: o3/Claude Opus ($8-75/M) - Deep reasoning
 */

// Model pricing (per million output tokens)
const MODEL_PRICING: Record<string, number> = {
  "deepseek/deepseek-chat": 0.42,
  "google/gemini-2.5-flash": 0.60,
  "openai/gpt-4o-mini": 0.60,
  "anthropic/claude-3-5-sonnet": 15.00,
  "openai/gpt-4o": 15.00,
  "anthropic/claude-opus-4": 75.00,
  "openai/o3": 8.00,
  "google/gemini-2.5-pro": 5.00,
};

// Tier model assignments
const TIER_MODELS = {
  SIMPLE: {
    primary: "deepseek/deepseek-chat",
    fallback: "google/gemini-2.5-flash",
    cost: 0.42,
  },
  MEDIUM: {
    primary: "openai/gpt-4o-mini",
    fallback: "google/gemini-2.5-flash",
    cost: 0.60,
  },
  COMPLEX: {
    primary: "anthropic/claude-3-5-sonnet",
    fallback: "openai/gpt-4o",
    cost: 15.00,
  },
  REASONING: {
    primary: "anthropic/claude-opus-4",
    fallback: "openai/o3",
    cost: 75.00,
  },
};

// Scoring dimensions (14 like ClawRouter)
const SCORING_RULES = [
  { name: "reasoning_markers", weight: 0.18, patterns: [/\b(prove|theorem|proof|derive|step by step|chain of thought|explain why)\b/i] },
  { name: "code_presence", weight: 0.15, patterns: [/\b(function|async|await|import|const|let|var|class|=>|{|}\b|`{3})/i] },
  { name: "simple_indicators", weight: 0.12, patterns: [/\b(what is|define|meaning of|translate|convert|how to say)\b/i] },
  { name: "multi_step", weight: 0.12, patterns: [/\b(first|then|next|finally|step \d|1\.|2\.|3\.)\b/i] },
  { name: "technical_terms", weight: 0.10, patterns: [/\b(algorithm|kubernetes|distributed|microservice|architecture|scale|optimize|complexity)\b/i] },
  { name: "creative_markers", weight: 0.05, patterns: [/\b(story|poem|creative|brainstorm|imagine|write a|draft)\b/i] },
  { name: "question_complexity", weight: 0.05, pattern: (text: string) => (text.match(/\?/g) || []).length >= 3 ? 1 : 0 },
  { name: "imperative_verbs", weight: 0.03, patterns: [/\b(build|create|implement|design|develop|make|construct)\b/i] },
  { name: "output_format", weight: 0.03, patterns: [/\b(json|yaml|xml|schema|markdown|table|list format)\b/i] },
  { name: "constraints", weight: 0.04, patterns: [/\b(O\(n\)|O\(log|O\(1\)|maximum|minimum|at most|at least|must|should not)\b/i] },
];

export type Tier = "SIMPLE" | "MEDIUM" | "COMPLEX" | "REASONING";

export interface RoutingDecision {
  model: string;
  tier: Tier;
  confidence: number;
  method: "rules" | "default";
  reasoning: string;
  costEstimate: number;
  baselineCost: number; // What Opus would cost
  savings: number; // 0-1 percentage
}

// Calculate score for text
function calculateScore(text: string): { score: number; details: string[] } {
  let totalScore = 0;
  const details: string[] = [];

  for (const rule of SCORING_RULES) {
    let ruleScore = 0;

    if (rule.patterns) {
      for (const pattern of rule.patterns) {
        if (pattern.test(text)) {
          ruleScore = 1;
          break;
        }
      }
    }

    // Special case: negate simple indicators if other complex markers present
    if (rule.name === "simple_indicators" && totalScore > 0.3) {
      ruleScore = -0.5;
    }

    const weightedScore = ruleScore * rule.weight;
    totalScore += weightedScore;

    if (ruleScore !== 0) {
      details.push(`${rule.name}: ${ruleScore > 0 ? '+' : ''}${weightedScore.toFixed(3)}`);
    }
  }

  // Token count penalty/bonus
  const tokenEstimate = text.length / 4;
  if (tokenEstimate < 50) {
    totalScore -= 0.05;
    details.push("short_text: -0.050");
  } else if (tokenEstimate > 1000) {
    totalScore += 0.10;
    details.push("long_text: +0.100");
  }

  return { score: totalScore, details };
}

// Sigmoid confidence calibration
function calibrateConfidence(distance: number, steepness: number = 12): number {
  return 1 / (1 + Math.exp(-steepness * distance));
}

// Determine tier from score
function scoreToTier(score: number): { tier: Tier; confidence: number } {
  const boundaries = [
    { tier: "SIMPLE" as Tier, max: 0.00 },
    { tier: "MEDIUM" as Tier, max: 0.15 },
    { tier: "COMPLEX" as Tier, max: 0.25 },
    { tier: "REASONING" as Tier, max: Infinity },
  ];

  let currentTier: Tier = "SIMPLE";
  let distance = Math.abs(score - 0.00);

  for (const boundary of boundaries) {
    if (score < boundary.max) {
      currentTier = boundary.tier;
      // Distance from nearest boundary
      const prevMax = boundaries[boundaries.indexOf(boundary) - 1]?.max || -0.5;
      distance = Math.min(
        Math.abs(score - prevMax),
        Math.abs(score - boundary.max)
      );
      break;
    }
  }

  // Special override: 2+ reasoning markers forces REASONING
  if (score > 0.25) {
    currentTier = "REASONING";
    distance = 0.3; // High confidence
  }

  return {
    tier: currentTier,
    confidence: calibrateConfidence(distance),
  };
}

// Main routing function
export function routeModel(
  prompt: string,
  forceTier?: Tier
): RoutingDecision {
  // Use forced tier if provided
  if (forceTier) {
    const tierConfig = TIER_MODELS[forceTier];
    return {
      model: tierConfig.primary,
      tier: forceTier,
      confidence: 1.0,
      method: "default",
      reasoning: `Forced to ${forceTier} tier`,
      costEstimate: tierConfig.cost / 1000, // Per 1K tokens estimate
      baselineCost: 75.0 / 1000, // Opus baseline
      savings: (75.0 - tierConfig.cost) / 75.0,
    };
  }

  // Calculate score
  const { score, details } = calculateScore(prompt);
  const { tier, confidence } = scoreToTier(score);

  // Select model
  const tierConfig = TIER_MODELS[tier];
  const model = confidence >= 0.70 
    ? tierConfig.primary 
    : tierConfig.fallback;

  // Calculate costs
  const costEstimate = tierConfig.cost / 1000;
  const baselineCost = 75.0 / 1000; // Claude Opus
  const savings = (baselineCost - costEstimate) / baselineCost;

  return {
    model,
    tier,
    confidence,
    method: "rules",
    reasoning: `score=${score.toFixed(3)} | ${details.slice(0, 4).join(", ")}`,
    costEstimate,
    baselineCost,
    savings,
  };
}

// Get routing for A2A agents
export function routeA2AAgents(
  topic: string,
  context: string
): {
  proposer: RoutingDecision;
  critic: RoutingDecision;
  consensus: RoutingDecision;
  totalSavings: number;
} {
  // Proposer: Analyzes the main signal/strategy
  const proposerPrompt = `Analyze trading strategy: ${topic}. ${context}`;
  const proposer = routeModel(proposerPrompt);

  // Critic: Reviews and challenges (can be cheaper if simple critique)
  const criticPrompt = `Review and critique this analysis for biases and risks`;
  const critic = routeModel(criticPrompt);

  // Consensus: Synthesizes final decision (can be cheaper)
  const consensusPrompt = `Make final trading decision based on above`;
  const consensus = routeModel(consensusPrompt);

  const totalSavings = (proposer.savings + critic.savings + consensus.savings) / 3;

  return { proposer, critic, consensus, totalSavings };
}

// Cost tracking
let sessionCosts = {
  simple: 0,
  medium: 0,
  complex: 0,
  reasoning: 0,
  totalRequests: 0,
  totalSaved: 0,
};

export function trackRouting(decision: RoutingDecision, tokensUsed: number = 1000) {
  const actualCost = (decision.costEstimate * tokensUsed) / 1000;
  const baselineCost = (decision.baselineCost * tokensUsed) / 1000;
  const saved = baselineCost - actualCost;

  sessionCosts[decision.tier.toLowerCase() as keyof typeof sessionCosts] += actualCost;
  sessionCosts.totalRequests++;
  sessionCosts.totalSaved += saved;

  return { actualCost, saved };
}

export function getCostStats() {
  return { ...sessionCosts };
}

export function resetCostStats() {
  sessionCosts = {
    simple: 0,
    medium: 0,
    complex: 0,
    reasoning: 0,
    totalRequests: 0,
    totalSaved: 0,
  };
}
