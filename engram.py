#!/usr/bin/env python3
"""
Engram - Neural Trading Analysis System
======================================

Simple CLI entry point for market analysis and trading signals.
Uses dual-model gateway (StepFun + GLM) without LMStudio dependency.

Usage:
    python engram.py analyze BTC/USD --timeframe 1h
    python engram.py signal ETH/USD --context "bullish trend"
    python engram.py risk BTC/USD --position-size 1000
    python engram.py status
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env file if python-dotenv available
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv not installed, rely on system env vars


@dataclass
class ModelConfig:
    """Configuration for model endpoints"""
    name: str
    api_base: str
    api_key: str
    priority: int = 1
    healthy: bool = True


class DualModelClient:
    """
    Client that routes between multiple LLM providers
    No LMStudio required - uses StepFun, GLM, or other OpenAI-compatible APIs
    """
    
    def __init__(self):
        self.endpoints: list[ModelConfig] = []
        self.session = None
        self._load_endpoints()
        
    def _load_endpoints(self):
        """Load endpoints from environment or use defaults"""
        
        # Primary: OpenRouter (recommended - access to many models)
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key and not openrouter_key.startswith("sk-or-v1-2a3b"):  # Skip placeholder
            self.endpoints.append(ModelConfig(
                name="OpenRouter",
                api_base="https://openrouter.ai/api/v1",
                api_key=openrouter_key,
                priority=1
            ))
        
        # Secondary: StepFun direct (if configured)
        stepfun_key = os.getenv("STEPFUN_API_KEY")
        if stepfun_key:
            self.endpoints.append(ModelConfig(
                name="StepFun",
                api_base=os.getenv("STEPFUN_API_BASE", "https://api.stepfun.com/v1"),
                api_key=stepfun_key,
                priority=2
            ))
        
        # Tertiary: GLM/Other OpenAI-compatible
        glm_key = os.getenv("GLM_API_KEY", "")
        glm_base = os.getenv("GLM_API_BASE", "")
        if glm_base and glm_key:
            self.endpoints.append(ModelConfig(
                name="GLM",
                api_base=glm_base,
                api_key=glm_key,
                priority=3
            ))
        
        if not self.endpoints:
            print("[!] No API endpoints configured - running in DEMO mode")
            print("Set one of: STEPFUN_API_KEY, GLM_API_BASE, OPENROUTER_API_KEY for live analysis")
            
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            import aiohttp
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def chat_completion(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Send chat completion request with automatic failover
        """
        if not self.endpoints:
            # Demo mode - return simulated response
            return self._demo_response(messages)
        
        session = await self._get_session()
        
        # Sort by priority
        endpoints = sorted(self.endpoints, key=lambda e: e.priority)
        
        last_error = None
        for endpoint in endpoints:
            if not endpoint.healthy:
                continue
                
            try:
                # Model selection based on endpoint
                if endpoint.name == "OpenRouter":
                    # GLM 4.7 Flash from Zhipu AI (Engram mind integration)
                    model_name = model or "z-ai/glm-4.7-flash"
                elif endpoint.name == "StepFun":
                    model_name = model or "step-1-8k"
                else:
                    model_name = model or "default"
                    
                payload = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {endpoint.api_key}"
                }
                
                # OpenRouter requires additional headers
                if endpoint.name == "OpenRouter":
                    headers["HTTP-Referer"] = "https://engram.local"
                    headers["X-Title"] = "Engram Trading Analysis"
                
                async with session.post(
                    f"{endpoint.api_base}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"].get("content", "")
                        return content
                    else:
                        error_text = await response.text()
                        # Only show error details in verbose mode
                        import logging
                        logging.getLogger(__name__).debug(f"{endpoint.name} error: {response.status} - {error_text[:100]}")
                        endpoint.healthy = False
                        last_error = f"{endpoint.name}: {error_text}"
                        
            except Exception as e:
                print(f"[!] {endpoint.name} failed: {e}")
                endpoint.healthy = False
                last_error = str(e)
        
        # All endpoints failed - fall back to demo mode
        print("[!] All API endpoints failed - falling back to DEMO mode")
        return self._demo_response(messages)
    
    def _demo_response(self, messages: list[dict]) -> str:
        """Generate demo response when no APIs configured"""
        user_msg = messages[-1].get("content", "") if messages else ""
        
        if "analyze" in user_msg.lower():
            pair = user_msg.split()[1] if len(user_msg.split()) > 1 else "BTC/USD"
            return f"""[DEMO MODE - No API configured]

Signal: HOLD
Confidence: 65%
Timeframe: 1h
Risk: MEDIUM

Analysis:
{pair} is currently consolidating after recent volatility. 
Key levels to watch:
- Support: Recent lows
- Resistance: Recent highs

This is a DEMO response. Set STEPFUN_API_KEY or OPENROUTER_API_KEY for live analysis."""
        
        elif "signal" in user_msg.lower():
            pair = user_msg.split()[2] if len(user_msg.split()) > 2 else "BTC/USD"
            return f"""[DEMO MODE - No API configured]

Signal: HOLD
Confidence: 60%
Entry: Wait for breakout
Stop Loss: Below support
Take Profit: Next resistance

Reasoning:
Market conditions are neutral. Waiting for clearer direction.

This is a DEMO response. Set STEPFUN_API_KEY or OPENROUTER_API_KEY for live analysis."""
        
        elif "risk" in user_msg.lower():
            return f"""[DEMO MODE - No API configured]

Risk Level: MEDIUM
Position Size: Reduce by 25%
Max Loss: 2% of portfolio
Risk/Reward: 1:2

Risk Factors:
- Market volatility
- Uncertain trend direction

Recommendations:
- Use stop losses
- Scale into position

This is a DEMO response. Set STEPFUN_API_KEY or OPENROUTER_API_KEY for live analysis."""
        
        else:
            return """[DEMO MODE - No API configured]

I'm running in demo mode. To get live AI analysis:

1. Get an API key from:
   - StepFun: https://platform.stepfun.com
   - OpenRouter: https://openrouter.ai

2. Set environment variable:
   export STEPFUN_API_KEY=your_key
   export OPENROUTER_API_KEY=your_key

Then run your command again for live analysis."""
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()


class EngramAnalyzer:
    """Main analysis engine"""
    
    def __init__(self):
        self.client = DualModelClient()
        self.model = os.getenv("ENGRAM_MODEL")  # Allow model override from env
        
    async def analyze_market(self, pair: str, timeframe: str = "1h") -> str:
        """Analyze market conditions for a trading pair"""
        
        system_prompt = """You are Engram, an expert trading analyst. 
Provide technical analysis including:
- Trend direction
- Support/resistance levels
- Key indicators
- Trading recommendation

Format your response as:
Signal: [BUY/SELL/HOLD]
Confidence: [0-100%]
Timeframe: [timeframe]
Risk: [LOW/MEDIUM/HIGH]

Analysis:
[Your detailed analysis]"""

        user_prompt = f"Analyze {pair} on the {timeframe} timeframe. Provide technical analysis and trading recommendation."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self.client.chat_completion(messages, model=self.model)
            return response
        except Exception as e:
            return f"Error analyzing market: {e}"
    
    async def generate_signal(self, pair: str, context: str = "") -> str:
        """Generate trading signal for a pair"""
        
        system_prompt = """You are Engram, a trading signal generator.
Provide clear BUY, SELL, or HOLD signals with reasoning.

Format:
Signal: [BUY/SELL/HOLD]
Confidence: [0-100%]
Entry: [price or range]
Stop Loss: [price]
Take Profit: [price or range]

Reasoning:
[Why this signal]"""

        user_prompt = f"Generate trading signal for {pair}."
        if context:
            user_prompt += f" Context: {context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self.client.chat_completion(messages, model=self.model)
            return response
        except Exception as e:
            return f"Error generating signal: {e}"
    
    async def assess_risk(self, pair: str, position_size: float) -> str:
        """Assess risk for a trade"""
        
        system_prompt = """You are Engram, a risk management specialist.
Assess trading risk and provide recommendations.

Format:
Risk Level: [LOW/MEDIUM/HIGH]
Position Size: [recommended size]
Max Loss: [amount]
Risk/Reward: [ratio]

Risk Factors:
[List key risks]

Recommendations:
[How to manage risk]"""

        user_prompt = f"Assess risk for trading {pair} with position size ${position_size:,.2f}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self.client.chat_completion(messages, model=self.model)
            return response
        except Exception as e:
            return f"Error assessing risk: {e}"
    
    async def get_status(self) -> str:
        """Get system status"""
        lines = [
            "[Engram System Status]",
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Configured Endpoints:"
        ]
        
        for ep in self.client.endpoints:
            status = "[OK]" if ep.healthy else "[FAIL]"
            lines.append(f"  {status} {ep.name} (priority {ep.priority})")
        
        if not self.client.endpoints:
            lines.append("  [!] No endpoints configured")
            lines.append("")
            lines.append("Set environment variables:")
            lines.append("  export STEPFUN_API_KEY=your_key")
            lines.append("  export OPENROUTER_API_KEY=your_key")
        
        return "\n".join(lines)
    
    async def close(self):
        """Cleanup"""
        await self.client.close()


async def main():
    parser = argparse.ArgumentParser(
        description="Engram - Neural Trading Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python engram.py analyze BTC/USD --timeframe 4h
  python engram.py signal ETH/USD --context "breakout pattern"
  python engram.py risk BTC/USD --position-size 5000
  python engram.py status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze market conditions")
    analyze_parser.add_argument("pair", help="Trading pair (e.g., BTC/USD)")
    analyze_parser.add_argument("--timeframe", default="1h", 
                               choices=["1m", "5m", "15m", "1h", "4h", "1d"],
                               help="Analysis timeframe")
    
    # Signal command
    signal_parser = subparsers.add_parser("signal", help="Generate trading signal")
    signal_parser.add_argument("pair", help="Trading pair")
    signal_parser.add_argument("--context", default="", help="Additional context")
    
    # Risk command
    risk_parser = subparsers.add_parser("risk", help="Assess trade risk")
    risk_parser.add_argument("pair", help="Trading pair")
    risk_parser.add_argument("--position-size", type=float, default=1000,
                            help="Position size in USD")
    
    # Status command
    subparsers.add_parser("status", help="Check system status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    analyzer = EngramAnalyzer()
    
    try:
        if args.command == "analyze":
            print(f"[*] Analyzing {args.pair} ({args.timeframe})...")
            print("=" * 50)
            result = await analyzer.analyze_market(args.pair, args.timeframe)
            print(result)
            
        elif args.command == "signal":
            print(f"[*] Generating signal for {args.pair}...")
            print("=" * 50)
            result = await analyzer.generate_signal(args.pair, args.context)
            print(result)
            
        elif args.command == "risk":
            print(f"[*] Assessing risk for {args.pair}...")
            print("=" * 50)
            result = await analyzer.assess_risk(args.pair, args.position_size)
            print(result)
            
        elif args.command == "status":
            result = await analyzer.get_status()
            print(result)
            
    finally:
        await analyzer.close()


if __name__ == "__main__":
    asyncio.run(main())
