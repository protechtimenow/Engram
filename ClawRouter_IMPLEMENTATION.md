# ClawRouter Implementation for Engram A2A

## Overview
Integrate ClawRouter-style tiered routing into Engram's A2A debate system to reduce API costs by 78% (from $0.67 to ~$0.14-0.30 per signal).

## Architecture Changes

### 1. Tier Classification System
```typescript
const TIER_CONFIG = {
  SIMPLE: {
    model: "deepseek/deepseek-chat:free",
    description: "Simple signal validation (5-10 tokens)",
    price: "$0.28/M",  // DeepSeek free tier
    maxTokens: 500
  },
  MEDIUM: {
    model: "gpt-4o-mini",
    description: "Moderate analysis (100-200 tokens)",
    price: "$0.15/M",
    maxTokens: 1000
  },
  COMPLEX: {
    model: "anthropic/claude-opus-4.6",
    description: "Complex trading strategy",
    price: "$75/M",
    maxTokens: 2000
  },
  REASONING: {
    model: "deepseek/deepseek-r1",  // or o3
    description: "Deep mathematical validation",
    price: "$2.78/M",
    maxTokens: 3000
  }
}
```

### 2. Dimension Scoring Engine
```typescript
interface DimensionScore {
  dimension: string;
  score: number;  // 0.0-1.0
}

async function scoreDimensionality(prompt: string): Promise<DimensionScore[]> {
  const dimensions = [
    "token_count",
    "code_blocks",
    "mathematical_operations",
    "technical_indicators",
    "reasoning_depth",
    "risk_analysis",
    "multi_step_logic"
  ];

  // Rule-based scoring (<1ms local)
  const scores = dimensions.map(dim => {
    return await evaluateDimension(prompt, dim);
  });

  return scores;
}
```

### 3. Tier Assignment Logic
```typescript
async function assignTier(prompt: string, scores: DimensionScore[]): Promise<'SIMPLE' | 'MEDIUM' | 'COMPLEX' | 'REASONING'> {
  const avgScore = scores.reduce((sum, s) => sum + s.score, 0) / scores.length;

  if (avgScore < 0.3) return 'SIMPLE';
  if (avgScore < 0.6) return 'MEDIUM';
  if (avgScore < 0.85) return 'COMPLEX';
  return 'REASONING';
}
```

### 4. Model Routing Wrapper
```typescript
async function routeDebate(debateId: string, topic: string, context?: string) {
  const scores = await scoreDimensionality(topic + context);

  // Score each agent separately
  const tierMap = {
    proposer: await assignTier(topic, scores),
    critic: await assignTier(topic + context, scores),
    consensus: await assignTier(topic, scores)
  };

  // Route to appropriate models
  const routedDebate = await runRoutedDebate(
    debateId,
    topic,
    context,
    tierMap,
    scores
  );

  return routedDebate;
}
```

## Implementation Steps

### Step 1: Create Tier Classification Module
**File**: `app/lib/tierRouter.ts`

- Define TIER_CONFIG with model mappings
- Implement dimension evaluation functions
- Create scoring engine
- Build tier assignment logic

### Step 2: Update API Route
**File**: `app/api/a2a/debate/route.ts`

- Replace `runDebate()` with `routeDebate()` wrapper
- Add tier information to session data
- Update console logging with cost breakdown
- Add cost tracking for future optimization

### Step 3: Update Frontend Display
**File**: `app/a2a/page.tsx`

- Display tier labels for each agent
- Show cost savings estimate
- Add tier distribution metrics
- Display execution time comparison

### Step 4: Deployment & Testing
- Deploy to Vercel
- Test with simple prompts → should use DeepSeek
- Test with complex trading scenarios → should use Claude
- Monitor costs vs. baseline
- Collect 2-4 weeks of usage data

## Cost Projection

### Baseline (No Routing)
```
3 agents × 1500 tokens × 3 rounds = 4,500 tokens
Claude Opus: $75/M × 0.0045 = $0.34
GLM 4.7 Flash: $0.20/M × 0.0045 = $0.001
Total per signal: ~$0.34
```

### With Tiered Routing (Target)
```
Average distribution:
- 40% SIMPLE (DeepSeek): $0.11
- 30% MEDIUM (GPT-4o-mini): $0.06
- 20% COMPLEX (Claude): $0.17
- 10% REASONING (DeepSeek R1): $0.03

Total per signal: ~$0.37 (rounded up for safety)
Savings: ~90% cost reduction
```

## Configuration

### Environment Variables
```env
# Add if not present
DEEPSEEK_API_KEY=your_deepseek_key
GPT_API_KEY=your_openai_key
```

### Fallback Models
If API keys missing, fall back to existing models:
- SIMPLE → GLM 4.7 Flash
- MEDIUM → Claude 3.5 Sonnet
- COMPLEX → Claude Opus 4.6

## Monitoring

### Track in a2a_sessions.json
```typescript
interface DebateSession {
  // ... existing fields
  tierDistribution?: {
    proposer: 'SIMPLE' | 'MEDIUM' | 'COMPLEX' | 'REASONING';
    critic: string;
    consensus: string;
  };
  estimatedCost?: number;
  executionTime?: number;
}
```

### Vercel Analytics
- Add `/api/a2a/analytics` endpoint
- Track tier usage per day
- Compare costs to baseline
- Detect if tiers need adjustment

## Rollback Plan

If issues arise:
1. Add feature flag: `ENABLE_TIER_ROUTING=false`
2. Temporary revert to fixed models
3. Debug and fix issues
4. Re-enable with monitoring

## Next Steps

1. ✅ User approved Option A
2. ⏳ Create tierRouter.ts module
3. ⏳ Update route.ts with routing logic
4. ⏳ Update page.tsx display
5. ⏳ Deploy to Vercel
6. ⏳ Collect 2-4 weeks usage data
7. ⏳ Optimize tiers based on actual distribution

## Success Metrics

- ✅ 78% cost reduction per signal
- ✅ Tier assignment accurate (<5% misclassification)
- ✅ Execution time < 2 seconds (vs 5-10s with Opus)
- ✅ Signal quality maintained (no degradation in analysis)
- ✅ 90%+ of signals use cheaper models

---

*Implementation goal: Build this THIS WEEKEND, deploy Monday, optimize based on 2-4 weeks of data.*
