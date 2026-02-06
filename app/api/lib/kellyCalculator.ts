/**
 * Kelly Criterion Calculator - TypeScript Version
 * Replaces decision_nets.py for Vercel compatibility
 */

export interface KellyResult {
  edge: number;
  odds: number;
  win_probability: number;
  lose_probability: number;
  full_kelly: number;
  half_kelly: number;
  quarter_kelly: number;
  expected_growth: number;
  risk_of_ruin: number;
}

export function calculateKelly(
  edge: number,
  odds: number,
  winProbability?: number
): KellyResult {
  // Calculate win probability from edge if not provided
  const winProb = winProbability || Math.min(0.95, Math.max(0.05, 0.5 + edge / 2));
  const loseProb = 1 - winProb;
  
  // Kelly formula: f* = (bp - q) / b
  const b = odds - 1;
  let fullKelly = 0;
  
  if (b > 0) {
    fullKelly = (b * winProb - loseProb) / b;
  }
  
  // Ensure valid range
  fullKelly = Math.max(0, Math.min(1, fullKelly));
  
  // Conservative fractions
  const halfKelly = fullKelly / 2;
  const quarterKelly = fullKelly / 4;
  
  // Expected growth
  let expectedGrowth = 0;
  if (fullKelly > 0 && b > 0) {
    expectedGrowth = (winProb * Math.log(1 + fullKelly * b)) + 
                    (loseProb * Math.log(1 - fullKelly));
  }
  
  // Risk of ruin (simplified)
  let riskOfRuin = 0.02;
  if (fullKelly > 0.5) riskOfRuin = 0.3;
  else if (fullKelly > 0.25) riskOfRuin = 0.1;
  
  return {
    edge,
    odds,
    win_probability: Math.round(winProb * 100) / 100,
    lose_probability: Math.round(loseProb * 100) / 100,
    full_kelly: Math.round(fullKelly * 100 * 100) / 100,
    half_kelly: Math.round(halfKelly * 100 * 100) / 100,
    quarter_kelly: Math.round(quarterKelly * 100 * 100) / 100,
    expected_growth: Math.round(expectedGrowth * 100 * 100) / 100,
    risk_of_ruin: Math.round(riskOfRuin * 100 * 100) / 100
  };
}

export function calculatePositionSize(
  entryPrice: number,
  targetPrice: number,
  stopPrice: number,
  portfolioValue: number,
  riskPercent: number = 2
): {
  positionSize: number;
  shares: number;
  riskAmount: number;
  potentialProfit: number;
  rRatio: number;
} {
  const riskPerShare = Math.abs(entryPrice - stopPrice);
  const rewardPerShare = Math.abs(targetPrice - entryPrice);
  const riskAmount = portfolioValue * (riskPercent / 100);
  
  const shares = riskPerShare > 0 ? riskAmount / riskPerShare : 0;
  const positionSize = shares * entryPrice;
  const potentialProfit = shares * rewardPerShare;
  const rRatio = riskPerShare > 0 ? rewardPerShare / riskPerShare : 0;
  
  return {
    positionSize: Math.round(positionSize * 100) / 100,
    shares: Math.round(shares * 10000) / 10000,
    riskAmount: Math.round(riskAmount * 100) / 100,
    potentialProfit: Math.round(potentialProfit * 100) / 100,
    rRatio: Math.round(rRatio * 100) / 100
  };
}
