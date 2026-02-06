/**
 * Simmer SDK Integration for Engram Trading System
 * 
 * Simmer is the prediction market interface for AI agents.
 * - Virtual trading: 10,000 $SIM starting balance
 * - Real trading: USDC on Polymarket (after claiming)
 * - Safety rails: $100/trade, $500/day limits
 */

const SIMMER_API_BASE = "https://api.simmer.markets/api/sdk";

// Load credentials from file or environment
function getCredentials(): { api_key: string; agent_id: string } | null {
  try {
    // Try environment variable first
    if (process.env.SIMMER_API_KEY) {
      return {
        api_key: process.env.SIMMER_API_KEY,
        agent_id: process.env.SIMMER_AGENT_ID || "",
      };
    }
    
    // Try credentials file
    const fs = require("fs");
    const path = require("path");
    const credsPath = path.join(process.cwd(), ".simmer_credentials.json");
    
    if (fs.existsSync(credsPath)) {
      const creds = JSON.parse(fs.readFileSync(credsPath, "utf8"));
      return {
        api_key: creds.api_key,
        agent_id: creds.agent_id,
      };
    }
    
    return null;
  } catch {
    return null;
  }
}

// API request helper
async function simmerRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<any> {
  const creds = getCredentials();
  if (!creds) {
    throw new Error("Simmer credentials not found. Run registration first.");
  }

  const url = `${SIMMER_API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Authorization": `Bearer ${creds.api_key}`,
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Simmer API error: ${response.status} - ${error}`);
  }

  return response.json();
}

// Agent status
export async function getAgentStatus() {
  return simmerRequest("/agents/me");
}

// List active markets
export async function getMarkets(params?: {
  q?: string;
  tags?: string;
  status?: string;
  limit?: number;
  import_source?: string;
}) {
  const queryParams = new URLSearchParams();
  if (params?.q) queryParams.append("q", params.q);
  if (params?.tags) queryParams.append("tags", params.tags);
  if (params?.status) queryParams.append("status", params.status);
  if (params?.limit) queryParams.append("limit", params.limit.toString());
  if (params?.import_source) queryParams.append("import_source", params.import_source);
  
  const query = queryParams.toString() ? `?${queryParams.toString()}` : "";
  return simmerRequest(`/markets${query}`);
}

// Get market context (warnings, position info)
export async function getMarketContext(marketId: string) {
  return simmerRequest(`/context/${marketId}`);
}

// Execute trade
export async function executeTrade(params: {
  market_id: string;
  side: "yes" | "no";
  amount: number;
  venue?: "simmer" | "polymarket";
  reasoning: string;
  source?: string;
}) {
  return simmerRequest("/trade", {
    method: "POST",
    body: JSON.stringify({
      venue: "simmer", // Default to virtual trading
      source: "engram-a2a",
      ...params,
    }),
  });
}

// Get portfolio
export async function getPortfolio() {
  return simmerRequest("/portfolio");
}

// Get positions
export async function getPositions() {
  return simmerRequest("/positions");
}

// Weather-specific markets
export async function getWeatherMarkets(limit: number = 20) {
  return getMarkets({ tags: "weather", status: "active", limit });
}

// Import Polymarket event
export async function importPolymarketEvent(polymarketUrl: string) {
  return simmerRequest("/markets/import", {
    method: "POST",
    body: JSON.stringify({ polymarket_url: polymarketUrl }),
  });
}

// Check if Simmer is configured
export function isSimmerConfigured(): boolean {
  return getCredentials() !== null;
}
