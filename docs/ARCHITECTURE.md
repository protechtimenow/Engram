# Engram + Neural Core Architecture

## Overview

Engram is a neural trading intelligence system with a progressive-disclosure architecture. The system combines domain-specific trading analysis with general-purpose decision intelligence through the Neural Core meta-skill.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interface Layer                        │
│         (Telegram, CLI, WebSocket, HTTP API)                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      ClawdBot Gateway                           │
│              (WebSocket: ws://127.0.0.1:18789)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     Neural Core Meta-Skill                      │
│              (Progressive-Disclosure Decision Hub)              │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────┐ │
│  │   Trading   │  Research   │  Strategy   │    Judgment     │ │
│  │   Domain    │   Domain    │   Domain    │     Domain      │ │
│  └─────────────┴─────────────┴─────────────┴─────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      Engram Core Engine                         │
│         (Neural Trading Analysis & Intelligence)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │    Market    │  │    Signal    │  │       Risk           │ │
│  │   Analysis   │  │  Generation  │  │    Assessment        │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Confidence  │  │    Pattern   │  │    Decision          │ │
│  │   Scoring    │  │    Scan      │  │     Nets             │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      LMStudio Backend                           │
│              (Local AI Inference: glm-4.7-flash)               │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Neural Core Meta-Skill

The Neural Core provides a unified interface for decision intelligence across multiple domains:

- **Progressive Disclosure**: Only loads relevant domain references
- **Domain Routing**: Automatically routes queries to appropriate domain
- **Consistent Output**: All domains return structured JSON

**Domains:**
- **Trading**: Market analysis, signal generation, risk assessment
- **Research**: Pattern detection, claim analysis, bias detection
- **Strategy**: Decision frameworks, scenario modeling, optimization
- **Judgment**: General reasoning, confidence assessment, logical analysis

### 2. Engram Core Engine

The neural engine that powers all analysis:

**Scripts:**
- `analyze_market.py` - Technical analysis, support/resistance, trends
- `generate_signal.py` - BUY/SELL/HOLD signals with confidence
- `assess_risk.py` - Position risk evaluation
- `confidence_scoring.py` - Universal claim evaluation (0-100%)
- `pattern_scan.py` - Text/data pattern and bias detection
- `decision_nets.py` - Bayesian decision frameworks

### 3. Integration Layer

ClawdBot Gateway provides:
- WebSocket interface for real-time communication
- Telegram bot integration
- Authentication and security
- Session management

## Data Flow

```
1. User Query → ClawdBot Gateway
2. Gateway → Neural Core (domain detection)
3. Neural Core → Load Domain Reference
4. Domain Reference → Execute Engram Scripts
5. Engram → LMStudio (AI inference)
6. LMStudio → Engram (structured output)
7. Engram → Neural Core (JSON results)
8. Neural Core → Gateway (formatted response)
9. Gateway → User
```

## Progressive Disclosure

The system uses progressive disclosure to maintain token efficiency:

1. **Level 1**: SKILL.md metadata (always loaded) ~100 tokens
2. **Level 2**: Domain reference file (loaded on demand) ~1k tokens
3. **Level 3**: Engram scripts (executed, not loaded) ~0 tokens

This design allows the system to handle complex multi-domain queries without context window overflow.

## Configuration

### Environment Variables

```bash
LMSTUDIO_HOST=localhost
LMSTUDIO_PORT=1234
ENGRAM_MODEL=glm-4.7-flash
CLAWDBOT_HOST=localhost
CLAWDBOT_PORT=18789
```

### File Structure

```
Engram/
├── src/
│   ├── engram/
│   │   └── scripts/
│   │       ├── analyze_market.py
│   │       ├── generate_signal.py
│   │       ├── assess_risk.py
│   │       ├── confidence_scoring.py
│   │       ├── pattern_scan.py
│   │       └── decision_nets.py
│   └── neural_core/
│       ├── SKILL.md
│       └── references/
│           ├── trading.md
│           ├── research.md
│           ├── strategy.md
│           ├── judgment.md
│           └── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── NEURAL_CORE.md
│   └── REFACTORING.md
├── tests/
├── config/
└── README.md
```

## Performance Characteristics

- **Latency**: <100ms (excluding AI inference)
- **Memory**: ~50MB base + model size
- **Throughput**: 100+ queries/minute
- **Context Efficiency**: 90% reduction via progressive disclosure

## Security

- Token-based authentication
- Input validation on all scripts
- No sensitive data in logs
- Local AI inference (no data leaves machine)

## Future Enhancements

1. Additional domains (medical, legal, scientific)
2. Multi-modal analysis (images, audio)
3. Real-time data feeds
4. Collaborative decision-making
5. Automated strategy optimization
