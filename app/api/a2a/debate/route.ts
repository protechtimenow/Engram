import { NextRequest, NextResponse } from "next/server";
import * as path from "path";
import * as fs from "fs";
import { analyzeMarket } from "../../lib/marketAnalyzer";
import { scoreConfidence } from "../../lib/confidenceScorer";
import { calculateKelly } from "../../lib/kellyCalculator";

// File-based session storage
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
}

const debateSessions: Map<string, DebateSession> = loadSessions();

function extractTradingPair(text: string): string | null {
  const patterns = [
    /\b([A-Z]{2,5})\s*\/\s*([A-Z]{2,5})\b/,
    /\b([A-Z]{2,5})\s*-\s*([A-Z]{2,5})\b/,
    /\b([A-Z]{2,5})(USD|EUR|GBP|JPY|USDT)\b/,
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      if (match[2] && !match[2].match(/^(USD|EUR|GBP|JPY|USDT|BTC|ETH)$/)) {
        continue;
      }
      return match[2] ? `${match[1]}/${match[2]}` : match[0];
    }
  }
  return null;
}

function extractPriceLevels(text: string): { entry?: number; target?: number; stop?: number } {
  const levels: { entry?: number; target?: number; stop?: number } = {};
  const pricePattern = /\$?([\d,]+\.?\d*)/g;
  const prices: number[] = [];
  let match;
  
  while ((match = pricePattern.exec(text)) !== null) {
    const price = parseFloat(match[1].replace(/,/g, ""));
    if (price > 100) prices.push(price);
  }
  
  if (prices.length >= 1) levels.entry = prices[0];
  if (prices.length >= 2) levels.target = Math.max(...prices);
  if (prices.length >= 3) {
    const sorted = [...prices].sort((a, b) => a - b);
    levels.stop = sorted[0];
    levels.entry = sorted[1];
    levels.target = sorted[sorted.length - 1];
  }
  
  return levels;
}

async function callModel(model: string, messages: { role: string; content: string }[], systemPrompt?: string) {
  const apiMessages = systemPrompt 
    ? [{ role: "system", content: systemPrompt }, ...messages]
    : messages;

  const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
      "HTTP-Referer": "https://engram.vercel.app",
      "X-Title": "Engram A2A"
    },
    body: JSON.stringify({
      model: model,
      messages: apiMessages,
      max_tokens: 2000,
      temperature: 0.7,
      ...(model.includes("claude") && { reasoning: { enabled: true } })
    }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error?.message || "API error");
  }
  return data.choices[0].message.content;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, debateId, topic, message, context, useScripts } = body;

    if (action === "start") {
      const id = Date.now().toString(36) + Math.random().toString(36).substr(2);
      const extractedPair = extractTradingPair(topic);
      
      const session: DebateSession = {
        id,
        topic: topic || "Trading Analysis",
        messages: [],
        status: "active",
        createdAt: new Date().toISOString(),
        extractedPair: extractedPair || undefined,
        scriptResults: {}
      };
      debateSessions.set(id, session);
      saveSessions(debateSessions);

      const results = await runDebate(id, topic, context, useScripts !== false);
      
      return NextResponse.json({ 
        success: true, 
        debateId: id,
        session: debateSessions.get(id),
        results,
        extractedPair
      });
    }

    if (action === "continue" && debateId) {
      const session = debateSessions.get(debateId);
      if (!session) {
        return NextResponse.json({ error: "Debate not found" }, { status: 404 });
      }

      session.messages.push({
        role: "user",
        content: message,
        timestamp: new Date().toISOString()
      });
      saveSessions(debateSessions);

      const results = await continueDebate(debateId, message, useScripts !== false);
      
      return NextResponse.json({
        success: true,
        session: debateSessions.get(debateId),
        results
      });
    }

    if (action === "status" && debateId) {
      const session = debateSessions.get(debateId);
      if (!session) {
        return NextResponse.json({ error: "Debate not found" }, { status: 404 });
      }
      return NextResponse.json({ session });
    }

    return NextResponse.json({ error: "Invalid action" }, { status: 400 });

  } catch (error) {
    console.error("A2A Debate Error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}

async function runDebate(debateId: string, topic: string, context?: string, useScripts: boolean = true) {
  const session = debateSessions.get(debateId)!;
  const messages: { role: string; content: string }[] = [];
  
  let marketAnalysis: any = null;
  let confidenceScore: any = null;
  let kellyCalculation: any = null;
  let currentPrice: number | null = null;
  
  // Use TypeScript market analysis instead of Python
  if (useScripts && session.extractedPair) {
    console.log(`Running analysis for pair: ${session.extractedPair}`);
    
    try {
      // Extract price from pair or use default
      const symbol = session.extractedPair.replace('/', '');
      currentPrice = symbol.includes('BTC') ? 65000 : 
                     symbol.includes('ETH') ? 3500 : 
                     symbol.includes('SOL') ? 150 : 1000;
      
      marketAnalysis = analyzeMarket(
        session.extractedPair,
        currentPrice,
        "1h",
        context
      );
      
      session.scriptResults!.marketAnalysis = marketAnalysis;
      currentPrice = marketAnalysis.current_price;
      console.log("Market analysis complete:", currentPrice);
    } catch (e) {
      console.error("Market analysis failed:", e);
    }
  }
  
  // Build prompt with current price
  let initialPrompt = `Analyze this trading scenario: ${topic}`;
  
  if (currentPrice) {
    initialPrompt += `\n\n**CRITICAL: Current market price is $${currentPrice.toLocaleString()}.**`;
    initialPrompt += `\n**All analysis MUST be based on this CURRENT price.**`;
  }
  
  if (context) {
    initialPrompt += `\n\nContext: ${context}`;
  }
  if (marketAnalysis) {
    initialPrompt += `\n\n[TECHNICAL DATA]\n${JSON.stringify(marketAnalysis, null, 2)}`;
  }
  
  messages.push({ role: "user", content: initialPrompt });

  // Proposer Agent
  const proposerPrompt = `You are the PROPOSER agent in a trading analysis debate.
${currentPrice ? `**CRITICAL**: Current price is $${currentPrice.toLocaleString()}. Entry must be NEAR this level (within 5-10%).` : ''}

Format your response with:
- SIGNAL: (LONG/SHORT/NEUTRAL)
- ENTRY: (price level - NEAR current price)
- TARGET: (price target)
- STOP: (stop loss)
- POSITION: (% of portfolio)
- RATIONALE: (your analysis)
- RISKS: (key concerns)`;

  const proposerResponse = await callModel(MODELS.proposer, messages, proposerPrompt);
  session.messages.push({
    role: "assistant",
    content: proposerResponse,
    agent: "proposer",
    timestamp: new Date().toISOString(),
    scriptData: marketAnalysis
  });

  // Confidence Scoring (TypeScript)
  const proposerClaim = proposerResponse.split('\n')[0].slice(0, 100) || "Trade proposal";
  
  if (useScripts) {
    try {
      confidenceScore = scoreConfidence(proposerClaim, undefined, "trading");
      session.scriptResults!.confidenceScore = confidenceScore;
      console.log("Confidence scoring complete");
    } catch (e) {
      console.error("Confidence scoring failed:", e);
    }
  }

  // Critic Agent
  const criticPrompt = `You are the CRITIC agent. Review the analysis critically.`;

  const criticMessages = [
    ...messages,
    { role: "assistant", content: proposerResponse }
  ];
  
  const criticResponse = await callModel(MODELS.critic, criticMessages, criticPrompt);
  session.messages.push({
    role: "assistant",
    content: criticResponse,
    agent: "critic",
    timestamp: new Date().toISOString(),
    scriptData: confidenceScore
  });

  // Kelly Calculation (TypeScript)
  const priceLevels = extractPriceLevels(proposerResponse);
  
  if (useScripts && priceLevels.entry && priceLevels.target) {
    try {
      const edge = 0.6;
      const odds = priceLevels.target / priceLevels.entry;
      
      kellyCalculation = calculateKelly(edge, odds);
      session.scriptResults!.kellyCalculation = kellyCalculation;
      console.log("Kelly calculation complete");
    } catch (e) {
      console.error("Kelly calculation failed:", e);
    }
  }

  // Consensus Agent
  const consensusPrompt = `You are the CONSENSUS agent.
${currentPrice ? `**Current price: $${currentPrice.toLocaleString()}**` : ''}
${kellyCalculation ? `**Kelly recommends: ${kellyCalculation.half_kelly}% position (Half Kelly)**` : ''}

Format your response with:
- FINAL SIGNAL: (LONG/SHORT/NEUTRAL/WAIT)
- ADJUSTED ENTRY: (realistic level)
- ADJUSTED TARGET: (price target)
- ADJUSTED STOP: (stop loss)
- POSITION SIZE: (% of portfolio)
- CONFIDENCE: (HIGH/MEDIUM/LOW)
- SUMMARY: (concise rationale)`;

  const consensusMessages = [
    ...messages,
    { role: "assistant", content: proposerResponse },
    { role: "assistant", content: criticResponse }
  ];
  
  const consensusResponse = await callModel(MODELS.consensus, consensusMessages, consensusPrompt);
  session.messages.push({
    role: "assistant",
    content: consensusResponse,
    agent: "consensus",
    timestamp: new Date().toISOString(),
    scriptData: kellyCalculation
  });
  
  saveSessions(debateSessions);

  return {
    proposer: proposerResponse,
    critic: criticResponse,
    consensus: consensusResponse,
    scriptResults: {
      marketAnalysis,
      confidenceScore,
      kellyCalculation
    }
  };
}

async function continueDebate(debateId: string, message: string, useScripts: boolean = true) {
  const session = debateSessions.get(debateId)!;
  const debateHistory = session.messages
    .filter(m => m.agent)
    .map(m => ({ 
      role: "assistant" as const, 
      content: `[${m.agent?.toUpperCase()}]: ${m.content}` 
    }));

  const messages = [
    ...debateHistory,
    { role: "user", content: message }
  ];

  // Confidence scoring for follow-up
  let confidenceScore: any = null;
  if (useScripts && message.toLowerCase().match(/confidence|risk|bias/)) {
    try {
      const claim = message.slice(0, 100);
      confidenceScore = scoreConfidence(claim, undefined, "trading");
    } catch (e) {
      console.error("Follow-up confidence scoring failed:", e);
    }
  }

  const [proposer, critic, consensus] = await Promise.all([
    callModel(MODELS.proposer, messages, "Respond to the follow-up question."),
    callModel(MODELS.critic, messages, "Respond critically."),
    callModel(MODELS.consensus, messages, "Synthesize the response.")
  ]);

  session.messages.push(
    { role: "assistant", content: proposer, agent: "proposer", timestamp: new Date().toISOString() },
    { role: "assistant", content: critic, agent: "critic", timestamp: new Date().toISOString(), scriptData: confidenceScore },
    { role: "assistant", content: consensus, agent: "consensus", timestamp: new Date().toISOString() }
  );
  
  saveSessions(debateSessions);

  return { proposer, critic, consensus };
}
