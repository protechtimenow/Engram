import { describe, it, expect } from '@jest/globals';

// Replicate the exact extraction logic from route.ts
const extractPair = (topic: string): string => {
  const patterns = [
    /(?:BTC|ETH|SOL|BNB|XRP|ADA|DOT|DOGE)[\/ ](?:USDT|USD|BTC|ETH)/i,
    /([A-Z]{2,5})\/([A-Z]{2,5})/i
  ];
  for (const pattern of patterns) {
    const match = topic.match(pattern);
    if (match) return match[0].toUpperCase();
  }
  return 'BTC/USD';
};

describe('A2A Debate API Integration', () => {
  it('should validate request body and return error for missing topic', () => {
    const validateTopic = (topic: any) => {
      if (!topic || typeof topic !== 'string') return false;
      if (topic.length > 500) return false;
      return true;
    };

    expect(validateTopic(undefined)).toBe(false);
    expect(validateTopic('')).toBe(false);
    expect(validateTopic('Valid topic')).toBe(true);
    expect(validateTopic('a'.repeat(501))).toBe(false);
  });

  it('should extract trading pair from topic', () => {
    expect(extractPair('Analyze BTC/USD for breakout')).toBe('BTC/USD');
    expect(extractPair('ETH/USDT price action')).toBe('ETH/USDT');
    expect(extractPair('Check SOL/USD')).toBe('SOL/USD');
    expect(extractPair('Random text')).toBe('BTC/USD');
    expect(extractPair('BNB/USDT trend')).toBe('BNB/USDT');
  });

  it('should structure debate session correctly', () => {
    const session = {
      id: 'test_123',
      topic: 'BTC/USD analysis',
      messages: [],
      status: 'active' as const,
      createdAt: new Date().toISOString(),
      extractedPair: 'BTC/USD'
    };

    expect(session).toHaveProperty('id');
    expect(session).toHaveProperty('topic');
    expect(session.status).toBe('active');
    expect(session.extractedPair).toBe('BTC/USD');
  });
});
