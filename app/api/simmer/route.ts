import { NextRequest, NextResponse } from "next/server";
import {
  getAgentStatus,
  getMarkets,
  getMarketContext,
  executeTrade,
  getPortfolio,
  getPositions,
  getWeatherMarkets,
  isSimmerConfigured,
} from "../../lib/simmerTrader";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get("action");

    if (!isSimmerConfigured()) {
      return NextResponse.json(
        { error: "Simmer not configured", claim_url: "https://simmer.markets/claim/peak-86VN" },
        { status: 400 }
      );
    }

    switch (action) {
      case "status":
        const status = await getAgentStatus();
        return NextResponse.json({ success: true, data: status });

      case "markets":
        const q = searchParams.get("q") || undefined;
        const tags = searchParams.get("tags") || undefined;
        const limit = parseInt(searchParams.get("limit") || "20");
        const markets = await getMarkets({ q, tags, limit, status: "active" });
        return NextResponse.json({ success: true, data: markets });

      case "weather":
        const weatherMarkets = await getWeatherMarkets(20);
        return NextResponse.json({ success: true, data: weatherMarkets });

      case "portfolio":
        const portfolio = await getPortfolio();
        return NextResponse.json({ success: true, data: portfolio });

      case "positions":
        const positions = await getPositions();
        return NextResponse.json({ success: true, data: positions });

      case "context":
        const marketId = searchParams.get("market_id");
        if (!marketId) {
          return NextResponse.json(
            { error: "Missing market_id parameter" },
            { status: 400 }
          );
        }
        const context = await getMarketContext(marketId);
        return NextResponse.json({ success: true, data: context });

      default:
        return NextResponse.json(
          { error: "Unknown action. Use: status, markets, weather, portfolio, positions, context" },
          { status: 400 }
        );
    }
  } catch (error: any) {
    console.error("Simmer API Error:", error);
    return NextResponse.json(
      { error: error.message || "Simmer API error" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    if (!isSimmerConfigured()) {
      return NextResponse.json(
        { error: "Simmer not configured", claim_url: "https://simmer.markets/claim/peak-86VN" },
        { status: 400 }
      );
    }

    const body = await request.json();
    const { action } = body;

    switch (action) {
      case "trade":
        const { market_id, side, amount, reasoning, venue } = body;
        if (!market_id || !side || !amount || !reasoning) {
          return NextResponse.json(
            { error: "Missing required fields: market_id, side, amount, reasoning" },
            { status: 400 }
          );
        }
        const result = await executeTrade({
          market_id,
          side,
          amount,
          reasoning,
          venue: venue || "simmer",
        });
        return NextResponse.json({ success: true, data: result });

      default:
        return NextResponse.json(
          { error: "Unknown action. Use: trade" },
          { status: 400 }
        );
    }
  } catch (error: any) {
    console.error("Simmer API Error:", error);
    return NextResponse.json(
      { error: error.message || "Simmer API error" },
      { status: 500 }
    );
  }
}
