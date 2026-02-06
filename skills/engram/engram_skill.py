"""
Engram Trading Analysis Skill
Provides market analysis, signal generation, and risk assessment
Supports multiple AI providers: OpenRouter, StepFun (direct)
"""

import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from .openrouter_client import OpenRouterClient
from .stepfun_client import StepFunClient
from .tools import (
    analyze_market,
    generate_signal,
    get_confidence_score,
    assess_risk,
    format_trading_response
)

logger = logging.getLogger(__name__)


class EngramSkill:
    """
    ClawdBot skill for Engram trading analysis
    Supports multiple AI providers: OpenRouter, StepFun (direct)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Engram skill
        
        Args:
            config: Configuration dictionary with model settings
        """
        self.config = config
        self.response_format = config.get("response_format", "clean")
        
        # Initialize clients based on configuration
        self.openrouter_client = None
        self.stepfun_client = None
        self.active_client = None
        self.active_provider = None
        
        # Determine which provider to use
        # GLM 4.7 Flash from Zhipu AI - integrated with Engram mind (PRIMARY)
        provider = config.get("provider", "auto").lower()
        model = config.get("model", "z-ai/glm-4.7-flash")
        
        # Initialize OpenRouter client (PRIMARY - for GLM 4.7 Flash)
        openrouter_key = config.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            self.openrouter_client = OpenRouterClient(
                model=model,
                api_key=openrouter_key
            )
            self.active_client = self.openrouter_client
            self.active_provider = "openrouter"
            logger.info(f"Engram skill initialized with OpenRouter: {model}")
        
        # Initialize StepFun client via OpenRouter (FALLBACK)
        stepfun_model = os.getenv("STEPFUN_MODEL", "stepfun/step-3.5-flash:free")
        if openrouter_key:
            self.stepfun_client = OpenRouterClient(
                model=stepfun_model,
                api_key=openrouter_key
            )
            logger.info(f"StepFun fallback configured via OpenRouter: {stepfun_model}")
        
        # If no client is active, use OpenRouter as default (will fail gracefully)
        if not self.active_client:
            self.openrouter_client = OpenRouterClient(model=model)
            self.active_client = self.openrouter_client
            self.active_provider = "openrouter"
            logger.warning("No API keys configured - skill will run in demo mode")
        
        self.tools = self._register_tools()
    
    def _register_tools(self) -> List[Dict[str, Any]]:
        """Register available tools for function calling"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "analyze_market",
                    "description": "Analyze market conditions for a trading pair",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pair": {
                                "type": "string",
                                "description": "Trading pair (e.g., BTC/USD, EUR/USD)"
                            },
                            "timeframe": {
                                "type": "string",
                                "enum": ["1m", "5m", "15m", "1h", "4h", "1d"],
                                "description": "Analysis timeframe"
                            }
                        },
                        "required": ["pair"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_signal",
                    "description": "Generate trading signal for a pair",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pair": {
                                "type": "string",
                                "description": "Trading pair"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional market context"
                            }
                        },
                        "required": ["pair"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_confidence_score",
                    "description": "Calculate confidence score for a signal",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "signal": {
                                "type": "string",
                                "enum": ["BUY", "SELL", "HOLD"],
                                "description": "Trading signal"
                            },
                            "market_data": {
                                "type": "object",
                                "description": "Market data for analysis"
                            }
                        },
                        "required": ["signal"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assess_risk",
                    "description": "Assess risk level for a trade",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pair": {
                                "type": "string",
                                "description": "Trading pair"
                            },
                            "position_size": {
                                "type": "number",
                                "description": "Position size in base currency"
                            }
                        },
                        "required": ["pair"]
                    }
                }
            }
        ]
    
    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process user message and generate response"""
        try:
            system_prompt = self._build_system_prompt()
            
            response = await self.active_client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                tools=self.tools
            )
            
            # Handle tool calls if present
            if response.get("tool_calls"):
                tool_results = await self._execute_tools(response["tool_calls"])
                final_response = await self.active_client.chat_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": response.get("content", ""), "tool_calls": response["tool_calls"]},
                        *tool_results
                    ]
                )
                return self._format_response(final_response.get("content", ""))
            
            return self._format_response(response.get("content", ""))
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"[ERROR] {str(e)}"
    
    async def _execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
        """Execute tool calls and return results"""
        results = []
        
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]
            
            try:
                if function_name == "analyze_market":
                    result = await analyze_market(**arguments)
                elif function_name == "generate_signal":
                    result = await generate_signal(**arguments)
                elif function_name == "get_confidence_score":
                    result = await get_confidence_score(**arguments)
                elif function_name == "assess_risk":
                    result = await assess_risk(**arguments)
                else:
                    result = {"error": f"Unknown tool: {function_name}"}
                
                results.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": str(result)
                })
                
            except Exception as e:
                logger.error(f"Error executing tool {function_name}: {e}")
                results.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": f"Error: {str(e)}"
                })
        
        return results
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for Engram"""
        return """You are Engram, an advanced neural trading analysis assistant.

Your capabilities include:
1. Market Analysis - Analyze price action, trends, and patterns
2. Signal Generation - Generate BUY/SELL/HOLD signals with confidence scores
3. Risk Assessment - Evaluate risk levels for trading positions
4. Trading Insights - Provide actionable trading recommendations

When providing analysis, use this format:

Signal: [BUY/SELL/HOLD]
Confidence: [0.XX]
Timeframe: [timeframe]
Risk Level: [LOW/MEDIUM/HIGH]

Analysis:
[Brief technical and fundamental analysis]

Suggestions:
- [Actionable suggestion 1]
- [Actionable suggestion 2]
- [Actionable suggestion 3]

Always be clear, concise, and professional. Focus on data-driven insights."""
    
    def _format_response(self, content: str) -> str:
        """Format response based on configured format"""
        if self.response_format == "raw":
            return content
        
        if self.response_format == "detailed":
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return f"[Engram Analysis - {timestamp}]\n\n{content}"
        
        # Clean format (default)
        lines = content.split('\n')
        clean_lines = [line for line in lines if not line.strip().startswith(('<think>', '</think>', 'reasoning:'))]
        return '\n'.join(clean_lines).strip()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check skill health status"""
        result = {
            "status": "unknown",
            "provider": self.active_provider,
            "model": self.active_client.model if self.active_client else "none",
            "tools_registered": len(self.tools),
            "response_format": self.response_format
        }
        
        try:
            if self.active_client:
                client_status = await self.active_client.health_check()
                result["status"] = "healthy" if client_status.get("healthy") else "degraded"
                result[self.active_provider] = client_status
            else:
                result["status"] = "unhealthy"
                result["error"] = "No active client"
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            result["status"] = "unhealthy"
            result["error"] = str(e)
        
        return result
    
    async def shutdown(self):
        """Clean shutdown of skill resources"""
        if self.openrouter_client:
            await self.openrouter_client.close()
        if self.stepfun_client:
            await self.stepfun_client.close()
        logger.info("Engram skill shutdown complete")
