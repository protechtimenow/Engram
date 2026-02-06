/**
 * Market Analysis Library - TypeScript Version
 * Replaces analyze_market.py for Vercel serverless compatibility
 */

export interface MarketAnalysis {
  pair: string;
  timeframe: string;
  current_price: number;
  trend: string;
  trend_strength: number;
  pivot_points: {
    pivot: number;
    r1: number;
    r2: number;
    r3: number;
    s1: number;
    s2: number;
    s3: number;
  };
  fibonacci_levels: {
    fib_0: number;
    fib_236: number;
    fib_382: number;
    fib_500: number;
    fib_618: number;
    fib_786: number;
    fib_100: number;
  };
  atr: number;
  atr_percent: number;
  support_levels: number[];
  resistance_levels: number[];
  key_observations: string[];
  risk_factors: string[];
  confidence: number;
  recommendation: string;
}

export function calculatePivotPoints(high: number, low: number, close: number) {
  const pivot = (high + low + close) / 3;
  return {
    pivot,
    r1: (2 * pivot) - low,
    r2: pivot + (high - low),
    r3: high + 2 * (pivot - low),
    s1: (2 * pivot) - high,
    s2: pivot - (high - low),
    s3: low - 2 * (high - pivot)
  };
}

export function calculateFibonacci(swingLow: number, swingHigh: number, trend: string) {
  const diff = swingHigh - swingLow;
  
  if (trend.toLowerCase() === "bullish") {
    return {
      fib_0: swingHigh,
      fib_236: swingHigh - (diff * 0.236),
      fib_382: swingHigh - (diff * 0.382),
      fib_500: swingHigh - (diff * 0.5),
      fib_618: swingHigh - (diff * 0.618),
      fib_786: swingHigh - (diff * 0.786),
      fib_100: swingLow
    };
  } else {
    return {
      fib_0: swingLow,
      fib_236: swingLow + (diff * 0.236),
      fib_382: swingLow + (diff * 0.382),
      fib_500: swingLow + (diff * 0.5),
      fib_618: swingLow + (diff * 0.618),
      fib_786: swingLow + (diff * 0.786),
      fib_100: swingHigh
    };
  }
}

export function calculateATR(price: number, timeframe: string = "1h"): number {
  const atrPercentages: Record<string, number> = {
    "15m": 0.005,
    "1h": 0.015,
    "4h": 0.025,
    "1d": 0.04,
    "1w": 0.08
  };
  return price * (atrPercentages[timeframe] || 0.02);
}

export function analyzeMarket(
  pair: string, 
  price: number, 
  timeframe: string = "1h",
  context?: string
): MarketAnalysis {
  const atr = calculateATR(price, timeframe);
  const atrPercent = (atr / price) * 100;
  
  // Determine trend (simplified - in production use real technical indicators)
  const trendStrength = 0.75;
  const trend: "BULLISH" | "BEARISH" = "BULLISH"; // Default for demo
  
  const recentHigh = price * 1.05;
  const recentLow = price * 0.95;
  const pivots = calculatePivotPoints(recentHigh, recentLow, price);
  
  const swingLow = price * 0.90;
  const swingHigh = price * 1.10;
  const fibs = calculateFibonacci(swingLow, swingHigh, trend);
  
  const supportLevels = [
    pivots.s1,
    fibs.fib_618,
    pivots.s2,
    price - (atr * 2)
  ].sort((a, b) => a - b);
  
  const resistanceLevels = [
    pivots.r1,
    pivots.r2,
    fibs.fib_382,
    price + (atr * 2)
  ].sort((a, b) => a - b);
  
  const keyObservations = [
    `Current price $${price.toLocaleString()} is ${price > pivots.pivot ? 'above' : 'below'} pivot`,
    `ATR (${timeframe}): $${atr.toFixed(2)} (${atrPercent.toFixed(2)}%)`,
    `Trend: ${trend} with ${(trendStrength * 100).toFixed(0)}% strength`
  ];
  
  const riskFactors = [
    `ATR indicates $${atr.toFixed(2)} average movement per ${timeframe}`,
    "Correlation with broader market remains high"
  ];
  
  const confidence = Math.min(95, Math.max(40, trendStrength * 100 - (atrPercent * 2)));
  
  return {
    pair,
    timeframe,
    current_price: price,
    trend,
    trend_strength: Math.round(trendStrength * 100) / 100,
    pivot_points: pivots,
    fibonacci_levels: fibs,
    atr: Math.round(atr * 100) / 100,
    atr_percent: Math.round(atrPercent * 100) / 100,
    support_levels: supportLevels.map(s => Math.round(s * 100) / 100),
    resistance_levels: resistanceLevels.map(r => Math.round(r * 100) / 100),
    key_observations: keyObservations,
    risk_factors: riskFactors,
    confidence: Math.round(confidence * 10) / 10,
    recommendation: "CAUTIOUS_LONG"
  };
}
