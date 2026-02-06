import { NextRequest, NextResponse } from "next/server";
import { routeA2AAgents, getCostStats, resetCostStats, RoutingDecision } from "../lib/modelRouter";

// Track routing decisions for the session
const routingHistory: RoutingDecision[] = [];

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get("action");

  switch (action) {
    case "costs":
      const stats = getCostStats();
      return NextResponse.json({
        success: true,
        data: stats,
        routingHistory: routingHistory.slice(-10), // Last 10 decisions
      });

    case "reset":
      resetCostStats();
      routingHistory.length = 0;
      return NextResponse.json({
        success: true,
        message: "Cost tracking reset",
      });

    case "test":
      // Test routing with sample queries
      const tests = [
        { query: "What is the price of BTC?", expected: "SIMPLE" },
        { query: "Explain RSI indicator", expected: "MEDIUM" },
        { query: "Build a Python trading bot with backtesting", expected: "COMPLEX" },
        { query: "Prove why this strategy has positive expected value", expected: "REASONING" },
      ];

      const results = tests.map(t => {
        const { routeModel } = require("../lib/modelRouter");
        const decision = routeModel(t.query);
        return {
          query: t.query,
          routed: decision.tier,
          expected: t.expected,
          match: decision.tier === t.expected,
          model: decision.model,
          savings: `${(decision.savings * 100).toFixed(0)}%`,
        };
      });

      return NextResponse.json({
        success: true,
        tests: results,
      });

    default:
      return NextResponse.json({
        success: true,
        endpoints: [
          "/api/a2a?action=costs - Get cost tracking stats",
          "/api/a2a?action=reset - Reset cost tracking",
          "/api/a2a?action=test - Test routing classifier",
        ],
      });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, topic, context, asset, price, forceTier } = body;

    if (action === "route") {
      // Test routing for a specific prompt
      const { routeModel } = require("../lib/modelRouter");
      const decision = routeModel(topic || context || "", forceTier);
      
      routingHistory.push(decision);

      return NextResponse.json({
        success: true,
        routing: decision,
        savings: `${(decision.savings * 100).toFixed(0)}%`,
        wouldHaveCost: `$${decision.baselineCost.toFixed(4)}`,
        willCost: `$${decision.costEstimate.toFixed(4)}`,
      });
    }

    if (action === "debate") {
      // Route A2A agents with cost optimization
      const { proposer, critic, consensus, totalSavings } = routeA2AAgents(
        topic || "",
        context || ""
      );

      routingHistory.push(proposer, critic, consensus);

      return NextResponse.json({
        success: true,
        routing: {
          proposer: {
            model: proposer.model,
            tier: proposer.tier,
            confidence: proposer.confidence,
          },
          critic: {
            model: critic.model,
            tier: critic.tier,
            confidence: critic.confidence,
          },
          consensus: {
            model: consensus.model,
            tier: consensus.tier,
            confidence: consensus.confidence,
          },
        },
        costOptimization: {
          avgSavings: `${(totalSavings * 100).toFixed(0)}%`,
          sessionStats: getCostStats(),
        },
        ready: true,
      });
    }

    return NextResponse.json(
      { error: "Unknown action. Use: route, debate" },
      { status: 400 }
    );

  } catch (error: any) {
    console.error("A2A Router Error:", error);
    return NextResponse.json(
      { error: error.message || "Internal error" },
      { status: 500 }
    );
  }
}
