## MODIFIED Requirements

### Requirement: Real-time Visualization
The Hub UI SHALL poll the `/api/engram/fingerprint` endpoint every 5 seconds or upon project mutation and display financial context.

#### Scenario: Financial fingerprint visualization
- **WHEN** financial data is processed
- **THEN** the UI must display financial neural fingerprints alongside project fingerprints

## ADDED Requirements

### Requirement: Financial API Endpoints
The Hub SHALL provide specialized financial analysis endpoints.

#### Scenario: Financial sentiment endpoint
- **WHEN** clients request `/api/engram/financial/sentiment`
- **THEN** the system must return current financial sentiment scores and trends

#### Scenario: Market trends endpoint
- **WHEN** clients request `/api/engram/financial/trends`
- **THEN** the system must return detected market trends and strength indicators

#### Scenario: Financial analysis endpoint
- **WHEN** clients request `/api/engram/financial/analysis`
- **THEN** the system must return comprehensive financial analysis including sentiment, trends, and predictions

### Requirement: Financial Metadata Schema
Every response SHALL include extended financial metadata in the `engram` object.

#### Scenario: Financial metadata inclusion
- **WHEN** financial analysis is active
- **THEN** responses must include financial sentiment, trend data, and community influence scores

```json
{
  "engram": {
    "hashing_active": true,
    "current_fingerprint": "8a3f...",
    "context_utilization": 0.85,
    "financial": {
      "sentiment_score": 0.42,
      "trend_direction": "bullish",
      "trend_strength": 0.78,
      "community_consensus": {
        "r/Quant": 0.65,
        "r/wallstreetbets": 0.89,
        "r/ValueInvesting": 0.34
      }
    }
  }
}
```