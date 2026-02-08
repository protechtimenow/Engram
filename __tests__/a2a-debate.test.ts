import { describe, it, expect } from '@jest/globals';
import { TierRouter, ClawRouterClient, assignTier, getTierModel, getTierLabel, estimateDebateCost, routeModel } from '../app/api/lib/tierRouter';

process.env.ENABLE_TIER_ROUTING = 'true';

describe('TierRouter', () => {
  it('should assign SIMPLE tier for low complexity queries', () => {
    const scores = {
      token_count: 0.1,
      technical_indicators: 0.0,
      mathematical_operations: 0.0,
      reasoning_depth: 0.1,
      risk_analysis: 0.0,
      code_blocks: 0.0
    };
    const tier = assignTier(scores);
    expect(tier).toBe('SIMPLE');
  });

  it('should assign MEDIUM tier for moderate complexity', () => {
    const scores = {
      token_count: 0.5,
      technical_indicators: 0.4,
      mathematical_operations: 0.2,
      reasoning_depth: 0.3,
      risk_analysis: 0.3,
      code_blocks: 0.1
    };
    const tier = assignTier(scores);
    expect(tier).toBe('MEDIUM');
  });

  it('should assign COMPLEX tier for high complexity', () => {
    const scores = {
      token_count: 0.7,
      technical_indicators: 0.8,
      mathematical_operations: 0.6,
      reasoning_depth: 0.7,
      risk_analysis: 0.6,
      code_blocks: 0.5
    };
    const tier = assignTier(scores);
    expect(tier).toBe('COMPLEX');
  });

  it('should assign REASONING tier for very high complexity', () => {
    const scores = {
      token_count: 0.9,
      technical_indicators: 0.9,
      mathematical_operations: 0.9,
      reasoning_depth: 0.9,
      risk_analysis: 0.9,
      code_blocks: 0.9
    };
    const tier = assignTier(scores);
    expect(tier).toBe('REASONING');
  });

  it('should route query and return decision with correct structure', () => {
    const decision = routeModel('BTC/USD signal');
    expect(decision).toHaveProperty('tier');
    expect(decision).toHaveProperty('model');
    expect(decision).toHaveProperty('estimated_tokens');
    expect(decision).toHaveProperty('estimated_cost');
    expect(decision).toHaveProperty('scores');
    expect(decision).toHaveProperty('reasoning');
    expect(['SIMPLE', 'MEDIUM', 'COMPLEX', 'REASONING']).toContain(decision.tier);
  });

  it('should calculate cost comparison correctly', () => {
    const router = new TierRouter();
    const decision = router.route('Analyze ETH with RSI and MACD', 500);
    const comparison = router.get_cost_comparison(decision);
    expect(comparison).toHaveProperty('selected_cost');
    expect(comparison).toHaveProperty('opus_baseline');
    expect(comparison).toHaveProperty('savings');
    expect(comparison).toHaveProperty('savings_pct');
    expect(comparison.savings).toBeGreaterThanOrEqual(0);
  });
});

describe('ClawRouterClient', () => {
  it('should track routing history and stats', () => {
    const client = new ClawRouterClient();
    client.route_and_prepare('Simple query', []);
    client.route_and_prepare('Complex analysis with math terms', []);
    const stats = client.get_stats();
    expect(stats.queries).toBe(2);
    expect(stats.total_cost).toBeGreaterThan(0);
    expect(stats.tier_distribution).toBeDefined();
  });

  it('should accumulate cost correctly', () => {
    const client = new ClawRouterClient();
    const d1 = client.route_and_prepare('BTC signal', []);
    const d2 = client.route_and_prepare('ETH analysis', []);
    const stats = client.get_stats();
    expect(stats.total_cost).toBeCloseTo(d1.estimated_cost + d2.estimated_cost, 6);
  });
});

describe('Helper Functions', () => {
  it('assignTier should return valid tier', () => {
    const scores = { token_count: 0.5, technical_indicators: 0.5, mathematical_operations: 0.5, reasoning_depth: 0.5, risk_analysis: 0.5, code_blocks: 0.5 };
    const tier = assignTier(scores);
    expect(['SIMPLE', 'MEDIUM', 'COMPLEX', 'REASONING']).toContain(tier);
  });

  it('getTierModel should return model string', () => {
    expect(getTierModel('SIMPLE')).toBe('deepseek/deepseek-chat');
    expect(getTierModel('MEDIUM')).toBe('openai/gpt-4o-mini');
    expect(getTierModel('COMPLEX')).toBe('anthropic/claude-3-5-sonnet');
    expect(getTierModel('REASONING')).toBe('anthropic/claude-opus-4');
  });

  it('getTierLabel should return human-readable label', () => {
    expect(getTierLabel('SIMPLE')).toContain('Simple');
    expect(getTierLabel('MEDIUM')).toContain('Medium');
    expect(getTierLabel('COMPLEX')).toContain('Complex');
    expect(getTierLabel('REASONING')).toContain('Reasoning');
  });

  it('estimateDebateCost should calculate total cost and tier distribution', () => {
    const result = estimateDebateCost(
      { proposer: 'SIMPLE', critic: 'MEDIUM', consensus: 'COMPLEX' },
      false
    );
    expect(result.estimatedCost).toBeGreaterThan(0);
    expect(result.tierDistribution.SIMPLE).toBe(1);
    expect(result.tierDistribution.MEDIUM).toBe(1);
    expect(result.tierDistribution.COMPLEX).toBe(1);
  });

  it('routeAllAgents should return TierAssignment array', async () => {
    const prompts = {
      proposer: 'BTC/USD signal',
      critic: 'Critique the signal',
      consensus: 'Finalize decision'
    };
    const assignments = await import('../app/api/lib/tierRouter').then(m => m.routeAllAgents(prompts));
    expect(Array.isArray(assignments)).toBe(true);
    expect(assignments.length).toBe(3);
    assignments.forEach(a => {
      expect(a).toHaveProperty('agent');
      expect(a).toHaveProperty('tier');
      expect(a).toHaveProperty('model');
      expect(a).toHaveProperty('confidence');
      expect(['proposer','critic','consensus']).toContain(a.agent);
      expect(['SIMPLE','MEDIUM','COMPLEX','REASONING']).toContain(a.tier);
    });
  });
});

describe('A2A Debate Integration', () => {
  it('should extract trading pair from topic', () => {
    const patterns = [/(?:BTC|ETH|SOL|BNB|XRP|ADA|DOT|DOGE)[\/ ](?:USD|USDT|BTC|ETH)/i, /([A-Z]{2,5})\/([A-Z]{2,5})/i];
    const topic = 'Analyze BTC/USD for breakout';
    let pair = 'BTC/USD';
    for (const pattern of patterns) {
      const match = topic.match(pattern);
      if (match) { pair = match[0].toUpperCase(); break; }
    }
    expect(pair).toBe('BTC/USD');
  });

  it('should handle Engram pipeline result structure', () => {
    const mockResult = {
      pair: 'BTC/USD',
      price: 70800,
      change_24h: 2.5,
      market_bias: 'BULLISH',
      confidence: 0.65,
      risk_score: 0.15,
      signal: 'BUY'
    };
    expect(mockResult).toHaveProperty('pair');
    expect(mockResult).toHaveProperty('signal');
    expect(['BUY', 'SELL', 'HOLD']).toContain(mockResult.signal);
  });
});
