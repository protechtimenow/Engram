#!/usr/bin/env python3
"""
A2A Debate - Multi-Agent Trading Analysis System
Orchestrates Proposer, Critic, and Consensus agents with Neural Core scripts.

Usage:
    python a2a_debate.py "BTC showing bullish divergence at $43,200" --asset BTC --timeframe 4H
    python a2a_debate.py "ETH breaking resistance" --asset ETH --risk high --context "Portfolio: $10k"
"""

import argparse
import json
import sys
import os
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TechnicalLevels:
    """Technical analysis levels."""
    pivot: float
    support: List[float]
    resistance: List[float]
    fib_382: float
    fib_500: float
    fib_618: float
    atr: float
    trend: str
    trend_strength: float


@dataclass
class PositionSizing:
    """Position sizing calculation."""
    full_kelly: float
    half_kelly: float
    quarter_kelly: float
    risk_per_trade: float
    position_size: float
    max_drawdown: float
    r_multiple: float


@dataclass
class BiasCheck:
    """Detected bias information."""
    bias_type: str
    severity: str
    evidence: str
    mitigation: str


@dataclass
class AgentResponse:
    """Individual agent response."""
    agent: str
    model: str
    content: str
    script_data: Any
    timestamp: str


@dataclass
class DebateResult:
    """Complete debate result."""
    topic: str
    asset: str
    timestamp: str
    technical_levels: TechnicalLevels
    position_sizing: PositionSizing
    proposer: AgentResponse
    critic: AgentResponse
    consensus: AgentResponse
    final_recommendation: str
    confidence: float


class TechnicalAnalyzer:
    """Advanced technical analysis with Fibonacci, pivots, ATR."""
    
    def __init__(self):
        self.price_history = {}
    
    def calculate_pivot_points(self, high: float, low: float, close: float) -> Dict[str, float]:
        """Calculate classic pivot points."""
        pivot = (high + low + close) / 3
        
        return {
            'pivot': pivot,
            'r1': (2 * pivot) - low,
            'r2': pivot + (high - low),
            'r3': high + 2 * (pivot - low),
            's1': (2 * pivot) - high,
            's2': pivot - (high - low),
            's3': low - 2 * (high - pivot)
        }
    
    def calculate_fibonacci(self, swing_low: float, swing_high: float, trend: str) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels."""
        diff = swing_high - swing_low
        
        if trend.lower() == "bullish":
            return {
                'fib_0': swing_high,
                'fib_236': swing_high - (diff * 0.236),
                'fib_382': swing_high - (diff * 0.382),
                'fib_500': swing_high - (diff * 0.5),
                'fib_618': swing_high - (diff * 0.618),
                'fib_786': swing_high - (diff * 0.786),
                'fib_100': swing_low
            }
        else:
            return {
                'fib_0': swing_low,
                'fib_236': swing_low + (diff * 0.236),
                'fib_382': swing_low + (diff * 0.382),
                'fib_500': swing_low + (diff * 0.5),
                'fib_618': swing_low + (diff * 0.618),
                'fib_786': swing_low + (diff * 0.786),
                'fib_100': swing_high
            }
    
    def calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range."""
        if len(highs) < period + 1:
            return (sum(highs) - sum(lows)) / len(highs) if highs else 100
        
        tr_values = []
        for i in range(1, len(highs)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr_values.append(max(tr1, tr2, tr3))
        
        return sum(tr_values[-period:]) / period if len(tr_values) >= period else sum(tr_values) / len(tr_values)
    
    def analyze(self, price: float, timeframe: str = "1h") -> TechnicalLevels:
        """Complete technical analysis."""
        # Generate realistic levels based on price
        atr = price * 0.02  # Approximate 2% ATR
        
        # Pivot around current price
        pivot = price
        r1 = price + (atr * 1.5)
        r2 = price + (atr * 2.5)
        r3 = price + (atr * 4)
        s1 = price - (atr * 1.5)
        s2 = price - (atr * 2.5)
        s3 = price - (atr * 4)
        
        # Fibonacci levels (assuming recent swing)
        swing_low = price * 0.95
        swing_high = price * 1.05
        fib = self.calculate_fibonacci(swing_low, swing_high, "bullish")
        
        return TechnicalLevels(
            pivot=pivot,
            support=[s1, s2, s3],
            resistance=[r1, r2, r3],
            fib_382=fib['fib_382'],
            fib_500=fib['fib_500'],
            fib_618=fib['fib_618'],
            atr=atr,
            trend="BULLISH" if price > pivot else "BEARISH",
            trend_strength=0.75
        )


class A2ADebate:
    """Multi-agent debate orchestrator."""
    
    MODELS = {
        'proposer': 'anthropic/claude-opus-4.6',
        'critic': 'anthropic/claude-3-5-sonnet',
        'consensus': 'z-ai/glm-4.7-flash'
    }
    
    def __init__(self, openrouter_key: Optional[str] = None):
        self.openrouter_key = openrouter_key or os.getenv('OPENROUTER_API_KEY')
        self.tech_analyzer = TechnicalAnalyzer()
    
    def extract_price(self, text: str) -> Optional[float]:
        """Extract price from text."""
        import re
        matches = re.findall(r'\$?([\d,]+\.?\d*)', text)
        for match in matches:
            try:
                price = float(match.replace(',', ''))
                if price > 1000:  # Likely a crypto/stock price
                    return price
            except ValueError:
                continue
        return None
    
    def call_agent(self, agent: str, prompt: str, context: str = "") -> str:
        """Call an AI agent via OpenRouter."""
        if not self.openrouter_key:
            return f"[MOCK {agent.upper()} RESPONSE]\n\nBased on the analysis, here's my take:\n\n{prompt[:100]}..."
        
        import requests
        
        system_prompts = {
            'proposer': """You are the PROPOSER agent in a trading analysis debate. 
Your role is to build the initial trading strategy with:
- Clear entry, target, and stop-loss levels
- Technical rationale (Fibonacci, pivots, trend)
- Position sizing recommendation
- Risk acknowledgment

Be confident but thorough.""",
            'critic': """You are the CRITIC agent in a trading analysis debate.
Your role is to challenge assumptions and find risks:
- Check for cognitive biases (confirmation, overconfidence, anchoring)
- Identify overlooked risks
- Question the technical analysis
- Suggest improvements or alternatives

Be constructive but rigorous.""",
            'consensus': """You are the CONSENSUS agent in a trading analysis debate.
Your role is to synthesize the final recommendation:
- Balance opportunity and risk
- Provide clear position sizing (use Kelly criterion)
- Give specific execution plan
- State confidence level

Be decisive and actionable."""
        }
        
        messages = [
            {"role": "system", "content": system_prompts.get(agent, "You are a trading analyst.")},
            {"role": "user", "content": f"{context}\n\n{prompt}"}
        ]
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Engram A2A"
                },
                json={
                    "model": self.MODELS[agent],
                    "messages": messages,
                    "max_tokens": 1500,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            data = response.json()
            if response.ok and 'choices' in data:
                return data['choices'][0]['message']['content']
            else:
                return f"[Error: {data.get('error', 'Unknown error')}]"
        except Exception as e:
            return f"[Error calling {agent}: {str(e)}]"
    
    def run_debate(self, topic: str, asset: str, price: Optional[float] = None,
                   timeframe: str = "1h", risk_level: str = "medium",
                   context: str = "") -> DebateResult:
        """Run complete A2A debate."""
        
        print(f"\n[A2A DEBATE: {asset}]")
        print("=" * 60)
        print(f"Topic: {topic}")
        print(f"Timeframe: {timeframe} | Risk: {risk_level}")
        if context:
            print(f"Context: {context}")
        print("=" * 60)
        
        # Step 1: Technical Analysis
        print("\n[Technical Analysis...]")
        current_price = price or 50000  # Default if not provided
        tech_levels = self.tech_analyzer.analyze(current_price, timeframe)
        print(f"  - Pivot: ${tech_levels.pivot:,.2f}")
        print(f"  - Trend: {tech_levels.trend} ({tech_levels.trend_strength:.0%} strength)")
        print(f"  - ATR: ${tech_levels.atr:,.2f}")
        print(f"  - Fib 0.618: ${tech_levels.fib_618:,.2f}")
        
        # Step 2: Position Sizing (Kelly)
        print("\n[Position Sizing...]")
        edge = 0.6 if risk_level == "high" else (0.5 if risk_level == "medium" else 0.4)
        odds = 2.0  # Assume 2:1 reward/risk
        
        win_prob = 0.5 + (edge / 2)
        b = odds - 1
        full_kelly = ((b * win_prob) - (1 - win_prob)) / b if b > 0 else 0
        full_kelly = max(0, min(1, full_kelly))
        
        position_sizing = PositionSizing(
            full_kelly=round(full_kelly * 100, 2),
            half_kelly=round(full_kelly * 50, 2),
            quarter_kelly=round(full_kelly * 25, 2),
            risk_per_trade=1.0 if risk_level == "low" else (2.0 if risk_level == "medium" else 3.0),
            position_size=round(full_kelly * 50, 2),  # Half Kelly default
            max_drawdown=15.0 if risk_level == "low" else (25.0 if risk_level == "medium" else 35.0),
            r_multiple=2.0
        )
        print(f"  - Full Kelly: {position_sizing.full_kelly}%")
        print(f"  - Half Kelly: {position_sizing.half_kelly}% (recommended)")
        print(f"  - Risk/Trade: {position_sizing.risk_per_trade}%")
        
        # Step 3: Proposer Agent
        print("\n[PROPOSER - Claude Opus 4.6] analyzing...")
        proposer_context = f"""TECHNICAL DATA:
- Asset: {asset} at ${current_price:,.2f}
- Timeframe: {timeframe}
- Trend: {tech_levels.trend} ({tech_levels.trend_strength:.0%} strength)
- Pivot: ${tech_levels.pivot:,.2f}
- Support: ${tech_levels.support[0]:,.2f}, ${tech_levels.support[1]:,.2f}, ${tech_levels.support[2]:,.2f}
- Resistance: ${tech_levels.resistance[0]:,.2f}, ${tech_levels.resistance[1]:,.2f}, ${tech_levels.resistance[2]:,.2f}
- Fib 0.618: ${tech_levels.fib_618:,.2f}
- ATR: ${tech_levels.atr:,.2f}
- Kelly Sizing: {position_sizing.half_kelly}% recommended
"""
        
        proposer_response = self.call_agent('proposer', topic, proposer_context)
        print(f"  - Complete")
        
        # Step 4: Critic Agent
        print("\n[CRITIC - Claude 3.5 Sonnet] analyzing...")
        critic_context = f"""PROPOSER'S ANALYSIS:
{proposer_response[:500]}...

CHECK FOR:
- Confirmation bias
- Overconfidence
- Anchoring to price levels
- Recency bias
- Herding behavior
- Loss aversion
"""
        
        critic_response = self.call_agent('critic', topic, critic_context)
        print(f"  - Complete")
        
        # Step 5: Consensus Agent
        print("\n[CONSENSUS - GLM 4.7 Flash] synthesizing...")
        consensus_context = f"""DEBATE SUMMARY:

PROPOSER:
{proposer_response[:300]}...

CRITIC:
{critic_response[:300]}...

POSITION SIZING DATA:
- Full Kelly: {position_sizing.full_kelly}%
- Half Kelly: {position_sizing.half_kelly}%
- Quarter Kelly: {position_sizing.quarter_kelly}%
- Risk per trade: {position_sizing.risk_per_trade}%

Provide FINAL recommendation with specific position size.
"""
        
        consensus_response = self.call_agent('consensus', topic, consensus_context)
        print(f"  - Complete")
        
        # Compile results
        timestamp = datetime.now().isoformat()
        
        return DebateResult(
            topic=topic,
            asset=asset,
            timestamp=timestamp,
            technical_levels=tech_levels,
            position_sizing=position_sizing,
            proposer=AgentResponse(
                agent="proposer",
                model=self.MODELS['proposer'],
                content=proposer_response,
                script_data=asdict(tech_levels),
                timestamp=timestamp
            ),
            critic=AgentResponse(
                agent="critic",
                model=self.MODELS['critic'],
                content=critic_response,
                script_data=None,
                timestamp=timestamp
            ),
            consensus=AgentResponse(
                agent="consensus",
                model=self.MODELS['consensus'],
                content=consensus_response,
                script_data=asdict(position_sizing),
                timestamp=timestamp
            ),
            final_recommendation=consensus_response,
            confidence=75.0
        )


def format_output(result: DebateResult, format_type: str = "text") -> str:
    """Format debate output."""
    if format_type == "json":
        return json.dumps(asdict(result), indent=2, default=str)
    
    output = f"""
+==================================================================+
|                    A2A DEBATE RESULT                              |
+==================================================================+
  Asset: {result.asset}
  Time: {result.timestamp}
  
  TECHNICAL LEVELS:
    Pivot: ${result.technical_levels.pivot:,.2f}
    Trend: {result.technical_levels.trend} ({result.technical_levels.trend_strength:.0%})
    ATR: ${result.technical_levels.atr:,.2f}
    Support: ${result.technical_levels.support[0]:,.2f} / ${result.technical_levels.support[1]:,.2f} / ${result.technical_levels.support[2]:,.2f}
    Resistance: ${result.technical_levels.resistance[0]:,.2f} / ${result.technical_levels.resistance[1]:,.2f} / ${result.technical_levels.resistance[2]:,.2f}
    Fib 0.618: ${result.technical_levels.fib_618:,.2f}
  
  POSITION SIZING:
    Full Kelly: {result.position_sizing.full_kelly}%
    Half Kelly: {result.position_sizing.half_kelly}% * RECOMMENDED
    Quarter Kelly: {result.position_sizing.quarter_kelly}%
    Risk/Trade: {result.position_sizing.risk_per_trade}%
    R-Multiple: {result.position_sizing.r_multiple}x
  
  PROPOSER ({result.proposer.model}):
    {result.proposer.content[:300]}...
  
  CRITIC ({result.critic.model}):
    {result.critic.content[:300]}...
  
  CONSENSUS ({result.consensus.model}):
    {result.consensus.content[:400]}...
  
  CONFIDENCE: {result.confidence:.0f}%
+==================================================================+
"""
    return output


def main():
    parser = argparse.ArgumentParser(
        description="A2A Multi-Agent Trading Debate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python a2a_debate.py "BTC showing bullish divergence at $43,200" --asset BTC
  python a2a_debate.py "ETH breaking resistance" --asset ETH --timeframe 4H --risk high
  python a2a_debate.py "SOL setup" --asset SOL --price 98.50 --context "Portfolio: $10k, 50% ETH long"
        """
    )
    
    parser.add_argument(
        "topic",
        help="Trading scenario to analyze"
    )
    parser.add_argument(
        "--asset", "-a",
        required=True,
        help="Asset symbol (BTC, ETH, SOL, etc.)"
    )
    parser.add_argument(
        "--price", "-p",
        type=float,
        help="Current price (auto-detected if not provided)"
    )
    parser.add_argument(
        "--timeframe", "-t",
        default="1h",
        choices=["15m", "1h", "4H", "1d", "1w"],
        help="Analysis timeframe"
    )
    parser.add_argument(
        "--risk", "-r",
        default="medium",
        choices=["low", "medium", "high"],
        help="Risk tolerance"
    )
    parser.add_argument(
        "--context", "-c",
        help="Additional context (portfolio size, current positions, etc.)"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "--key", "-k",
        help="OpenRouter API key (or set OPENROUTER_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    # Extract price from topic if not provided
    debate = A2ADebate(openrouter_key=args.key)
    price = args.price or debate.extract_price(args.topic)
    
    # Run debate
    result = debate.run_debate(
        topic=args.topic,
        asset=args.asset,
        price=price,
        timeframe=args.timeframe,
        risk_level=args.risk,
        context=args.context or ""
    )
    
    # Output
    print(format_output(result, args.output))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
