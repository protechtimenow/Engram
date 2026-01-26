# Engram Hub API Specification (OpenResponses)

This specification defines the universal response schema for the Engram Hub, ensuring compatibility with OpenCode-driven mutations and Neural Hashing visualizations.

## Endpoint: `/v1/chat/completions`

Compliant with OpenAI/OpenResponses specifications.

### Custom Metadata
Every response SHALL include an `engram` object in the `usage` or `metadata` block.

```json
{
  "engram": {
    "hashing_active": true,
    "current_fingerprint": "8a3f...",
    "context_utilization": 0.85
  }
}
```

## Endpoint: `/api/engram/fingerprint`

Retrieves the live neural fingerprints for project context anchoring.

### Response Schema
```json
{
  "file_path": {
    "token_id": 12345,
    "label": "filename.py",
    "hash_v": "..."
  }
}
```

## Requirement: Real-time Visualization
The Hub UI SHALL poll the `/api/engram/fingerprint` endpoint every 5 seconds or upon project mutation.
