import { NextRequest, NextResponse } from "next/server";
import * as path from "path";
import * as fs from "fs";
import { analyzeMarket } from "../../lib/marketAnalyzer";
import { scoreConfidence } from "../../lib/confidenceScorer";
import { calculateKelly } from "../../lib/kellyCalculator";
import {
  routeAllAgents,
  assignTier,
  getTierModel,
  getTierLabel,
  estimateDebateCost,
  TierAssignment,
  TIER_CONFIG
} from "../../lib/tierRouter";

// Feature flag: enable tiered routing
const ENABLE_TIER_ROUTING = process.env.ENABLE_TIER_ROUTING !== "false";

// Rate limiting: simple in-memory store (use Redis in production)
const rateLimitMap = new Map<string, { count: number; resetTime: number }>();
const RATE_LIMIT_MAX = 10; // requests per minute per IP
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute

function checkRateLimit(ip: string): boolean {
  const now = Date.now();
  const entry = rateLimitMap.get(ip);
  if (!entry || now > entry.resetTime) {
    rateLimitMap.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW });
    return true;
  }
  if (entry.count >= RATE_LIMIT_MAX) {
    return false;
  }
  entry.count++;
  return true;
}

// File-based session storage with fallback
const SESSIONS_FILE = path.join(process.cwd(), "a2a_sessions.json");

function loadSessions(): Map<string, DebateSession> {
  try {
    if (fs.existsSync(SESSIONS_FILE)) {
      const data = JSON.parse(fs.readFileSync(SESSIONS_FILE, 'utf-8'));
      const sessions = new Map<string, DebateSession>();
      for (const [key, value] of Object.entries(data)) {
        sessions.set(key, value as DebateSession);
      }
      return sessions;
    }
  } catch (e) {
    console.error("Failed to load sessions:", e);
  }
  return new Map<string, DebateSession>();
}

function saveSessions(sessions: Map<string, DebateSession>) {
  try {
    const data: Record<string, DebateSession> = {};
    sessions.forEach((value, key) => {
      data[key] = value;
    });
    fs.writeFileSync(SESSIONS_FILE, JSON.stringify(data, null, 2));
  } catch (e) {
    console.error("Failed to save sessions:", e);
  }
}

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || "";

// Dynamic model routing based on tier (legacy, kept for compatibility)
const MODELS = {
  proposer: "anthropic/claude-opus-4.6",
  critic: "anthropic/claude-3-5-sonnet",
  consensus: "z-ai/glm-4.7-flash"
};

interface DebateMessage {
  role: "user" | "assistant";
  content: string;
  agent?: "proposer" | "critic" | "consensus";
  timestamp: string;
  scriptData?: any;
}

interface DebateSession {
  id: string;
  topic: string;
  messages: DebateMessage[];
  status: "active" | "completed";
  createdAt: string;
  extractedPair?: string;
  scriptResults?: {
    marketAnalysis?: any;
    confidenceScore?: any;
    kellyCalculation?: any;
  };
  tierDistribution?: {
    proposer: string;
    critic: string;
    consensus: string;
  };
  totalCost?: number;
}

// Helper to extract trading pair from topic
function extractPair(topic: string): string {
  const patterns = [
    /(?:BTC|ETH|SOL|BNB|XRP|ADA|DOT|DOGE)[\/ ](?:USDT|USD|BTC|ETH)/i,
    /([A-Z]{2,5})\/([A-Z]{2,5})/i
  ];
  for (const pattern of patterns) {
    const match = topic.match(pattern);
    if (match) return match[0].toUpperCase();
  }
  return "BTC/USD"; // default
}

// Run Engram neural pipeline (simplified integration)
async function runEngramPipeline(pair: string): Promise<any> {
  try {
    // In production, this would call the actual Engram brain modules
    // For now, return simulated results based on live price fetch
    const priceRes = await fetch(`https://api.binance.com/api/v3/ticker/24hr?symbol=${pair.replace("/", "")}`);
    const priceData = await priceRes.json();
    const change = parseFloat(priceData.priceChangePercent);
    
    return {
      pair,
      price: parseFloat(priceData.lastPrice),
      change_24h: change,
      market_bias: change > 0 ? "BULLISH" : change < 0 ? "BEARISH" : "NEUTRAL",
      confidence: Math.min(0.5 + Math.abs(change) / 200, 0.95),
      risk_score: Math.abs(change) / 100,
      signal: change > 1 ? "BUY" : change < -1 ? "SELL" : "HOLD"
    };
  } catch (e) {
    console.error("Engram pipeline failed:", e);
    return { error: "Failed to fetch market data" };
  }
}

// Main debate orchestration
async function runDebate(topic: string, context?: string): Promise<{
  session: DebateSession;
  cost: number;
  messages: DebateMessage[];
}> {
  const sessionId = `debate_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const now = new Date().toISOString();
  
  // Initialize session
  const session: DebateSession = {
    id: sessionId,
    topic,
    messages: [],
    status: "active",
    createdAt: now,
    extractedPair: extractPair(topic)
  };
  
  const pair = session.extractedPair || "BTC/USD";
  
  // Step 1: Run Engram neural pipeline to get market data
  const pipelineResult = await runEngramPipeline(pair);
  if ("error" in pipelineResult) {
    throw new Error(pipelineResult.error);
  }
  session.scriptResults = {
    marketAnalysis: pipelineResult
  };
  
  // Step 2: Route agents using ClawRouter if enabled
  let tierDistribution: { proposer: string; critic: string; consensus: string } | undefined;
  let totalCost = 0;
  
  if (ENABLE_TIER_ROUTING) {
    const prompts = {
      proposer: `Generate a trading signal for ${pair} based on: ${JSON.stringify(pipelineResult)}. Provide clear BUY/SELL/HOLD with confidence.`,
      critic: `Critique the proposed signal for ${pair}. Consider risk, market conditions, and alternative scenarios. Respond with AGREE/DISAGREE and reasoning.`,
      consensus: `Finalize the decision for ${pair} after critique. Output final signal with adjusted confidence.`
    };
    
    try {
      const assignments = await routeAllAgents(prompts, context);
      tierDistribution = {
        proposer: assignments.find(a => a.agent === 'proposer')?.tier || 'MEDIUM',
        critic: assignments.find(a => a.agent === 'critic')?.tier || 'MEDIUM',
        consensus: assignments.find(a => a.agent === 'consensus')?.tier || 'MEDIUM'
      };
      session.tierDistribution = tierDistribution;
      
      // Estimate cost
      const costEstimate = estimateDebateCost(
        { proposer: tierDistribution.proposer as any, critic: tierDistribution.critic as any, consensus: tierDistribution.consensus as any },
        pipelineResult.change_24h > 2 || pipelineResult.change_24h < -2
      );
      totalCost = costEstimate.estimatedCost;
      session.totalCost = totalCost;
    } catch (e) {
      console.error("ClawRouter routing failed:", e);
      // Fallback to default models
      tierDistribution = { proposer: 'COMPLEX', critic: 'COMPLEX', consensus: 'COMPLEX' };
    }
  } else {
    tierDistribution = { proposer: 'COMPLEX', critic: 'COMPLEX', consensus: 'COMPLEX' };
  }
  
  // Step 3: Simulate agent responses (in production, these would be actual LLM calls)
  const proposerMsg: DebateMessage = {
    role: "assistant",
    agent: "proposer",
    content: `[PROPOSER] Signal: ${pipelineResult.signal} | Confidence: ${(pipelineResult.confidence*100).toFixed(1)}% | Tier: ${tierDistribution.proposer}`,
    timestamp: new Date().toISOString(),
    scriptData: { pipelineResult, tier: tierDistribution.proposer }
  };
  
  const criticMsg: DebateMessage = {
    role: "assistant",
    agent: "critic",
    content: `[CRITIC] Assessment: CAUTIOUS | Reasoning: ${pipelineResult.market_bias} bias with ${(pipelineResult.risk_score*100).toFixed(1)}% risk score. AGREE with signal but suggest monitoring. | Tier: ${tierDistribution.critic}`,
    timestamp: new Date().toISOString(),
    scriptData: { tier: tierDistribution.critic }
  };
  
  const consensusMsg: DebateMessage = {
    role: "assistant",
    agent: "consensus",
    content: `[CONSENSUS] Final Decision: ${pipelineResult.signal} | Final Confidence: ${(pipelineResult.confidence*100).toFixed(1)}% | Total Cost: $${totalCost.toFixed(6)} | Tier: ${tierDistribution.consensus}`,
    timestamp: new Date().toISOString(),
    scriptData: { tier: tierDistribution.consensus, totalCost }
  };
  
  session.messages.push(proposerMsg, criticMsg, consensusMsg);
  session.status = "completed";
  
  return { session, cost: totalCost, messages: session.messages };
}

// Handler
export async function POST(req: NextRequest) {
  try {
    // Rate limiting
    const clientIp = req.headers.get("x-forwarded-for") || req.headers.get("x-real-ip") || "unknown";
    if (!checkRateLimit(clientIp)) {
      return NextResponse.json(
        { error: "Rate limit exceeded. Maximum 10 requests per minute." },
        { status: 429 }
      );
    }
    
    const body = await req.json();
    const { topic, context } = body;
    
    if (!topic || typeof topic !== "string") {
      return NextResponse.json(
        { error: "Missing or invalid 'topic' parameter" },
        { status: 400 }
      );
    }
    
    // Validate topic length
    if (topic.length > 500) {
      return NextResponse.json(
        { error: "Topic too long (max 500 characters)" },
        { status: 400 }
      );
    }
    
    // Run debate
    const result = await runDebate(topic, context);
    
    // Save session
    const sessions = loadSessions();
    sessions.set(result.session.id, result.session);
    saveSessions(sessions);
    
    return NextResponse.json({
      success: true,
      sessionId: result.session.id,
      ...result
    });
    
  } catch (error: any) {
    console.error("A2A Debate error:", error);
    return NextResponse.json(
      { error: error.message || "Internal server error" },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  try {
    const sessions = loadSessions();
    const recent = Array.from(sessions.values())
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 20);
    
    return NextResponse.json({
      total: sessions.size,
      recent
    });
  } catch (error: any) {
    console.error("Failed to list sessions:", error);
    return NextResponse.json(
      { error: error.message || "Internal server error" },
      { status: 500 }
    );
  }
}
// trivial change to force rebuild
