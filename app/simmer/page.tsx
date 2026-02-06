"use client";

import { useState, useEffect } from "react";

interface Market {
  id: string;
  title: string;
  description?: string;
  current_price: number;
  volume: number;
  url: string;
  resolution_date?: string;
}

interface AgentStatus {
  name: string;
  status: string;
  balance: number;
  claim_code: string;
  limits: {
    simmer: boolean;
    real_trading: boolean;
    max_trade_usd: number;
    daily_limit_usd: number;
  };
}

export default function SimmerPage() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [status, setStatus] = useState<AgentStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tradeMarket, setTradeMarket] = useState<Market | null>(null);
  const [tradeAmount, setTradeAmount] = useState(10);
  const [tradeSide, setTradeSide] = useState<"yes" | "no">("yes");
  const [tradeReasoning, setTradeReasoning] = useState("");
  const [tradeResult, setTradeResult] = useState<any>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch agent status
      const statusRes = await fetch("/api/simmer?action=status");
      if (statusRes.ok) {
        const statusData = await statusRes.json();
        setStatus(statusData.data);
      }
      
      // Fetch weather markets
      const marketsRes = await fetch("/api/simmer?action=weather");
      if (marketsRes.ok) {
        const marketsData = await marketsRes.json();
        setMarkets(marketsData.data?.markets || []);
      }
      
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const executeTrade = async () => {
    if (!tradeMarket) return;
    
    try {
      setLoading(true);
      const res = await fetch("/api/simmer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "trade",
          market_id: tradeMarket.id,
          side: tradeSide,
          amount: tradeAmount,
          reasoning: tradeReasoning,
          venue: "simmer",
        }),
      });
      
      const data = await res.json();
      if (data.success) {
        setTradeResult(data.data);
        setTradeMarket(null);
        setTradeReasoning("");
        fetchData(); // Refresh balance
      } else {
        setError(data.error);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !status) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-4">🔮 Simmer Trading</h1>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (error && !status) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-4">🔮 Simmer Trading</h1>
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
            <p className="text-red-400">{error}</p>
            <a 
              href="https://simmer.markets/claim/peak-86VN"
              className="text-blue-400 hover:underline mt-2 inline-block"
            >
              Claim Agent to Enable Trading →
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">🔮 Simmer Trading</h1>
        <p className="text-gray-400 mb-6">Prediction markets for AI agents</p>
        
        {/* Agent Status */}
        {status && (
          <div className="bg-gray-800 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">{status.name}</h2>
                <p className="text-sm text-gray-400">
                  Status: <span className={status.status === "claimed" ? "text-green-400" : "text-yellow-400"}>
                    {status.status}
                  </span>
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-green-400">
                  {status.balance?.toLocaleString()} $SIM
                </p>
                <p className="text-xs text-gray-400">
                  Limits: ${status.limits.max_trade_usd}/trade, ${status.limits.daily_limit_usd}/day
                </p>
              </div>
            </div>
            {status.status === "unclaimed" && (
              <div className="mt-3 p-3 bg-yellow-900/30 border border-yellow-500/50 rounded">
                <p className="text-sm text-yellow-400">
                  ⚠️ Not claimed yet. Real trading disabled.
                </p>
                <a 
                  href={`https://simmer.markets/claim/${status.claim_code}`}
                  className="text-blue-400 hover:underline text-sm"
                >
                  Claim at simmer.markets/claim/{status.claim_code}
                </a>
              </div>
            )}
          </div>
        )}
        
        {/* Trade Modal */}
        {tradeMarket && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full">
              <h3 className="text-lg font-bold mb-2">Trade: {tradeMarket.title}</h3>
              <p className="text-sm text-gray-400 mb-4">Current price: {tradeMarket.current_price}</p>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Side</label>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setTradeSide("yes")}
                      className={`flex-1 py-2 rounded ${
                        tradeSide === "yes" ? "bg-green-600" : "bg-gray-700"
                      }`}
                    >
                      YES
                    </button>
                    <button
                      onClick={() => setTradeSide("no")}
                      className={`flex-1 py-2 rounded ${
                        tradeSide === "no" ? "bg-red-600" : "bg-gray-700"
                      }`}
                    >
                      NO
                    </button>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Amount ($SIM)</label>
                  <input
                    type="number"
                    value={tradeAmount}
                    onChange={(e) => setTradeAmount(Number(e.target.value))}
                    className="w-full bg-gray-700 rounded px-3 py-2"
                    min={1}
                    max={100}
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Reasoning</label>
                  <textarea
                    value={tradeReasoning}
                    onChange={(e) => setTradeReasoning(e.target.value)}
                    className="w-full bg-gray-700 rounded px-3 py-2 h-20"
                    placeholder="Why are you making this trade?"
                  />
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => setTradeMarket(null)}
                    className="flex-1 py-2 bg-gray-700 rounded hover:bg-gray-600"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={executeTrade}
                    disabled={!tradeReasoning || loading}
                    className="flex-1 py-2 bg-blue-600 rounded hover:bg-blue-500 disabled:opacity-50"
                  >
                    {loading ? "..." : "Execute Trade"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Trade Result */}
        {tradeResult && (
          <div className="bg-green-900/30 border border-green-500 rounded-lg p-4 mb-6">
            <h3 className="text-green-400 font-semibold">✅ Trade Executed</h3>
            <p className="text-sm text-gray-300">
              Bought {tradeResult.shares_bought?.toFixed(2)} shares for {tradeResult.cost?.toFixed(2)} $SIM
            </p>
            <button 
              onClick={() => setTradeResult(null)}
              className="text-xs text-gray-400 hover:text-white mt-2"
            >
              Dismiss
            </button>
          </div>
        )}
        
        {/* Markets */}
        <h2 className="text-xl font-semibold mb-4">Weather Markets</h2>
        <div className="grid gap-4">
          {markets.length === 0 ? (
            <p className="text-gray-400">No active markets found.</p>
          ) : (
            markets.map((market) => (
              <div key={market.id} className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{market.title}</h3>
                    {market.description && (
                      <p className="text-sm text-gray-400 mt-1">{market.description}</p>
                    )}
                    <div className="flex gap-4 mt-2 text-sm text-gray-400">
                      <span>Price: {market.current_price}</span>
                      <span>Volume: {market.volume?.toLocaleString()}</span>
                      {market.resolution_date && (
                        <span>Resolves: {new Date(market.resolution_date).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => setTradeMarket(market)}
                      className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-500 text-sm"
                    >
                      Trade
                    </button>
                    <a
                      href={market.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600 text-sm"
                    >
                      View
                    </a>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
        
        {/* Refresh Button */}
        <button
          onClick={fetchData}
          disabled={loading}
          className="mt-6 px-4 py-2 bg-gray-700 rounded hover:bg-gray-600 disabled:opacity-50"
        >
          {loading ? "Refreshing..." : "Refresh Markets"}
        </button>
      </div>
    </div>
  );
}
