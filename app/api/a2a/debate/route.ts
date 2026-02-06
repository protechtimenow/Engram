import { NextRequest, NextResponse } from "next/server";

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || "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";

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
}

interface DebateSession {
  id: string;
  topic: string;
  messages: DebateMessage[];
  status: "active" | "completed";
  createdAt: string;
}

// In-memory storage for debate sessions
const debateSessions: Map<string, DebateSession> = new Map();

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
      max_tokens: 1500,
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
    const { action, debateId, topic, message, context } = body;

    // Start a new debate
    if (action === "start") {
      const id = Date.now().toString(36) + Math.random().toString(36).substr(2);
      const session: DebateSession = {
        id,
        topic: topic || "Trading Analysis",
        messages: [],
        status: "active",
        createdAt: new Date().toISOString()
      };
      debateSessions.set(id, session);

      // Run the debate rounds
      const results = await runDebate(id, topic, context);
      
      return NextResponse.json({ 
        success: true, 
        debateId: id,
        session: debateSessions.get(id),
        results
      });
    }

    // Continue an existing debate
    if (action === "continue" && debateId) {
      const session = debateSessions.get(debateId);
      if (!session) {
        return NextResponse.json({ error: "Debate not found" }, { status: 404 });
      }

      // Add user message
      session.messages.push({
        role: "user",
        content: message,
        timestamp: new Date().toISOString()
      });

      // Get responses from all agents
      const results = await continueDebate(debateId, message);
      
      return NextResponse.json({
        success: true,
        session: debateSessions.get(debateId),
        results
      });
    }

    // Get debate status
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

async function runDebate(debateId: string, topic: string, context?: string) {
  const session = debateSessions.get(debateId)!;
  const messages: { role: string; content: string }[] = [
    { role: "user", content: `Analyze this trading scenario: ${topic}${context ? `\n\nContext: ${context}` : ""}` }
  ];

  // Proposer Agent
  const proposerPrompt = `You are the PROPOSER agent in a trading analysis debate. Your role is to:
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
    timestamp: new Date().toISOString()
  });

  // Critic Agent
  const criticPrompt = `You are the CRITIC agent in a trading analysis debate. Your role is to:
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
    { role: "assistant", content: proposerResponse }
  ];
  const criticResponse = await callModel(MODELS.critic, criticMessages, criticPrompt);
  session.messages.push({
    role: "assistant",
    content: criticResponse,
    agent: "critic",
    timestamp: new Date().toISOString()
  });

  // Consensus Agent
  const consensusPrompt = `You are the CONSENSUS agent in a trading analysis debate. Your role is to:
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
    { role: "assistant", content: criticResponse }
  ];
  const consensusResponse = await callModel(MODELS.consensus, consensusMessages, consensusPrompt);
  session.messages.push({
    role: "assistant",
    content: consensusResponse,
    agent: "consensus",
    timestamp: new Date().toISOString()
  });

  return {
    proposer: proposerResponse,
    critic: criticResponse,
    consensus: consensusResponse
  };
}

async function continueDebate(debateId: string, message: string) {
  const session = debateSessions.get(debateId)!;
  const debateHistory = session.messages
    .filter(m => m.agent)
    .map(m => ({ role: "assistant", content: `[${m.agent?.toUpperCase()}]: ${m.content}` }));

  const messages = [
    ...debateHistory,
    { role: "user", content: message }
  ];

  // All agents respond to the follow-up
  const [proposer, critic, consensus] = await Promise.all([
    callModel(MODELS.proposer, messages, "You are the PROPOSER. Respond to the user's follow-up question based on the debate history."),
    callModel(MODELS.critic, messages, "You are the CRITIC. Respond to the user's follow-up question based on the debate history."),
    callModel(MODELS.consensus, messages, "You are the CONSENSUS. Respond to the user's follow-up question based on the debate history.")
  ]);

  session.messages.push(
    { role: "assistant", content: proposer, agent: "proposer", timestamp: new Date().toISOString() },
    { role: "assistant", content: critic, agent: "critic", timestamp: new Date().toISOString() },
    { role: "assistant", content: consensus, agent: "consensus", timestamp: new Date().toISOString() }
  );

  return { proposer, critic, consensus };
}
