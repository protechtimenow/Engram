import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import * as path from "path";
import * as fs from "fs";

const execAsync = promisify(exec);

// File-based session storage for persistence across server restarts
const SESSIONS_FILE = path.join(process.cwd(), "a2a_sessions.json");

// Load sessions from file if it exists
function loadSessions(): Map<string, DebateSession> {
  try {
    if (fs.existsSync(SESSIONS_FILE)) {
      const data = JSON.parse(fs.readFileSync(SESSIONS_FILE, 'utf-8'));
      const sessions = new Map<string, DebateSession>();
      for (const [key, value] of Object.entries(data)) {
        sessions.set(key, value as DebateSession);
      }
      console.log(`Loaded ${sessions.size} sessions from file`);
      return sessions;
    }
  } catch (e) {
    console.error("Failed to load sessions:", e);
  }
  return new Map<string, DebateSession>();
}

// Save sessions to file
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

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || "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";

const MODELS = {
  proposer: "anthropic/claude-opus-4.6",
  critic: "anthropic/claude-3-5-sonnet",
  consensus: "z-ai/glm-4.7-flash"
};

// Path to Python scripts
const SCRIPTS_DIR = path.join(process.cwd(), "src", "engram", "scripts");

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

// Initialize sessions from file
const debateSessions: Map<string, DebateSession> = loadSessions();

// Utility: Quote argument for shell (Windows-compatible)
function quoteArg(arg: string): string {
  // If arg contains spaces, wrap in double quotes
  if (arg.includes(' ')) {
    return `"${arg.replace(/"/g, '""')}"`;
  }
  return arg;
}

// Utility: Execute Python script
async function runPythonScript(scriptName: string, args: string[]): Promise<any> {
  try {
    const scriptPath = path.join(SCRIPTS_DIR, scriptName);
    const quotedArgs = args.map(quoteArg).join(" ");
    const command = `python "${scriptPath}" ${quotedArgs}`;
    
    console.log(`Executing: ${command}`);
    const { stdout, stderr } = await execAsync(command, { timeout: 30000 });
    
    if (stderr && !stderr.includes("UserWarning")) {
      console.warn(`Script stderr: ${stderr}`);
    }
    
    // Try to parse as JSON
    try {
      return JSON.parse(stdout);
    } catch {
      // Return as text if not JSON
      return { text: stdout.trim() };
    }
  } catch (error) {
    console.error(`Script execution error: ${error}`);
    return { error: String(error) };
  }
}

// Utility: Extract trading pair from text
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

// Utility: Extract price levels from text
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
      "HTTP-Referer": "http://localhost:3000",
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
        extractedPair,
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

    if (action === "script") {
      const { script, args } = body;
      const result = await runPythonScript(script, args || []);
      return NextResponse.json({ success: true, result });
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
  
  if (useScripts && session.extractedPair) {
    console.log(`Running scripts for pair: ${session.extractedPair}`);
    
    try {
      marketAnalysis = await runPythonScript("analyze_market.py", [
        "--pair", session.extractedPair,
        "--output", "json",
        "--live-data"
      ]);
      session.scriptResults!.marketAnalysis = marketAnalysis;
      console.log("Market analysis complete");
    } catch (e) {
      console.error("Market analysis failed:", e);
    }
    
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  let initialPrompt = `Analyze this trading scenario: ${topic}`;
  if (context) {
    initialPrompt += `\n\nContext: ${context}`;
  }
  if (marketAnalysis && !marketAnalysis.error) {
    initialPrompt += `\n\n[TECHNICAL DATA]\n${JSON.stringify(marketAnalysis, null, 2)}`;
  }
  
  messages.push({ role: "user", content: initialPrompt });

  const proposerPrompt = `You are the PROPOSER agent in a trading analysis debate. 
${marketAnalysis && !marketAnalysis.error ? 'You have been provided with technical analysis data above. Use this data to inform your recommendation, but add your own insights and reasoning.' : 'Analyze the trading scenario thoroughly.'}

Your role is to:
1. Analyze the trading scenario thoroughly
2. Propose a clear trading strategy (entry, exit, stop-loss, position sizing)
3. Provide technical and fundamental rationale
4. Be confident but acknowledge key risks

Format your response with:
- SIGNAL: (LONG/SHORT/NEUTRAL)
- ENTRY: (price level)
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

  // Extract a shorter claim for confidence scoring (first line or first 100 chars)
  const proposerClaim = proposerResponse.split('\n')[0].slice(0, 100) || "Trade proposal analysis";
  
  if (useScripts) {
    try {
      confidenceScore = await runPythonScript("confidence_scoring.py", [
        "--claim", proposerClaim,
        "--domain", "trading",
        "--bias-check",
        "--output", "json"
      ]);
      session.scriptResults!.confidenceScore = confidenceScore;
      console.log("Confidence scoring complete");
    } catch (e) {
      console.error("Confidence scoring failed:", e);
    }
    
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  const criticPrompt = `You are the CRITIC agent in a trading analysis debate.
${confidenceScore && !confidenceScore.error ? `You have been provided with confidence scoring data for the proposer's claim. Use this to identify specific weaknesses.` : 'Review the proposer\'s analysis critically.'}

Your role is to:
1. Review the proposer's analysis critically
2. Identify flaws, blind spots, or overlooked risks
3. Challenge assumptions with data-driven counterarguments
4. Suggest improvements or alternative scenarios
5. Be constructive but rigorous - don't just agree

Format your response with:
- ASSESSMENT: (VALID/CONCERNS/REJECT)
- CONCERNS: (specific issues with the proposal)
- ALTERNATIVES: (different approaches to consider)
- RISK FACTORS: (what could go wrong)
- RECOMMENDATIONS: (how to improve the trade)`;

  const criticMessages = [
    ...messages,
    { role: "assistant", content: proposerResponse },
    ...(confidenceScore && !confidenceScore.error ? [{ 
      role: "system", 
      content: `[CONFIDENCE ANALYSIS]\n${JSON.stringify(confidenceScore, null, 2)}` 
    }] : [])
  ];
  
  const criticResponse = await callModel(MODELS.critic, criticMessages, criticPrompt);
  session.messages.push({
    role: "assistant",
    content: criticResponse,
    agent: "critic",
    timestamp: new Date().toISOString(),
    scriptData: confidenceScore
  });

  const priceLevels = extractPriceLevels(proposerResponse);
  
  if (useScripts && priceLevels.entry && priceLevels.target) {
    try {
      const edge = 0.6;
      const odds = priceLevels.target / priceLevels.entry;
      
      kellyCalculation = await runPythonScript("decision_nets.py", [
        "--kelly",
        "--edge", edge.toString(),
        "--odds", odds.toFixed(2),
        "--output", "json"
      ]);
      session.scriptResults!.kellyCalculation = kellyCalculation;
      console.log("Kelly calculation complete");
    } catch (e) {
      console.error("Kelly calculation failed:", e);
    }
  }

  const consensusPrompt = `You are the CONSENSUS agent in a trading analysis debate.
${kellyCalculation && !kellyCalculation.error ? `You have been provided with Kelly criterion calculations for position sizing. Use this in your final recommendation.` : 'Synthesize the debate into a final recommendation.'}

Your role is to:
1. Synthesize the proposer's strategy and critic's feedback
2. Make a final recommendation that balances opportunity and risk
3. Provide clear, actionable guidance
4. Include specific price levels and risk management

Format your response with:
- FINAL SIGNAL: (LONG/SHORT/NEUTRAL/WAIT)
- ADJUSTED ENTRY: (price level)
- ADJUSTED TARGET: (price target)
- ADJUSTED STOP: (stop loss)
- POSITION SIZE: (% of portfolio with rationale)
- EXECUTION: (immediate/conditional on what)
- CONFIDENCE: (HIGH/MEDIUM/LOW with explanation)
- SUMMARY: (concise rationale for the final decision)`;

  const consensusMessages = [
    ...messages,
    { role: "assistant", content: proposerResponse },
    { role: "assistant", content: criticResponse },
    ...(kellyCalculation && !kellyCalculation.error ? [{ 
      role: "system", 
      content: `[POSITION SIZING DATA]\n${JSON.stringify(kellyCalculation, null, 2)}` 
    }] : [])
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

  let confidenceScore: any = null;
  if (useScripts && message.toLowerCase().match(/confidence|risk|bias|uncertainty/)) {
    try {
      const claim = message.slice(0, 100);
      confidenceScore = await runPythonScript("confidence_scoring.py", [
        "--claim", claim,
        "--domain", "trading",
        "--bias-check",
        "--output", "json"
      ]);
    } catch (e) {
      console.error("Follow-up confidence scoring failed:", e);
    }
  }

  const [proposer, critic, consensus] = await Promise.all([
    callModel(MODELS.proposer, messages, "You are the PROPOSER. Respond to the user's follow-up question based on the debate history."),
    callModel(MODELS.critic, [
      ...messages,
      ...(confidenceScore && !confidenceScore.error ? [{ 
        role: "system" as const, 
        content: `[CONFIDENCE DATA]\n${JSON.stringify(confidenceScore, null, 2)}` 
      }] : [])
    ], "You are the CRITIC. Respond to the user's follow-up question based on the debate history."),
    callModel(MODELS.consensus, messages, "You are the CONSENSUS. Respond to the user's follow-up question based on the debate history.")
  ]);

  session.messages.push(
    { role: "assistant", content: proposer, agent: "proposer", timestamp: new Date().toISOString() },
    { role: "assistant", content: critic, agent: "critic", timestamp: new Date().toISOString(), scriptData: confidenceScore },
    { role: "assistant", content: consensus, agent: "consensus", timestamp: new Date().toISOString() }
  );
  
  saveSessions(debateSessions);

  return { proposer, critic, consensus };
}
