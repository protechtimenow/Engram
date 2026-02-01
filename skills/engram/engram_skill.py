"""
Engram Trading Analysis Skill
Provides market analysis, signal generation, and risk assessment capabilities
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .lmstudio_client import LMStudioClient
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
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Engram skill
        
        Args:
            config: Configuration dictionary with LMStudio settings
        """
        self.config = config
        self.lmstudio = LMStudioClient(
            host=config.get("lmstudio_host", "localhost"),
            port=config.get("lmstudio_port", 1234),
            model=config.get("model", "glm-4.7-flash")
        )
        self.response_format = config.get("response_format", "clean")
        self.tools = self._register_tools()
        logger.info("Engram skill initialized")
    
    def _register_tools(self) -> List[Dict[str, Any]]:
        """
        Register available tools for function calling
        
        Returns:
            List of tool schemas in OpenAI format
        """
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
        """
        Process user message and generate response
        
        Args:
            message: User message
            context: Optional context (platform, user_id, etc.)
            
        Returns:
            Response string
        """
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt()
            
            # Query LMStudio with tools
            response = await self.lmstudio.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                tools=self.tools
            )
            
            # Handle tool calls if present
            if response.get("tool_calls"):
                tool_results = await self._execute_tools(response["tool_calls"])
                # Get final response with tool results
                final_response = await self.lmstudio.chat_completion(
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
            return f"I encountered an error analyzing the market. Please try again."
    
    async def _execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
        """
        Execute tool calls and return results
        
        Args:
            tool_calls: List of tool call objects
            
        Returns:
            List of tool result messages
        """
        results = []
        
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]
            
            try:
                # Execute the appropriate tool
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
        """
        Build system prompt for Engram
        
        Returns:
            System prompt string
        """
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
• [Actionable suggestion 1]
• [Actionable suggestion 2]
• [Actionable suggestion 3]

Always be clear, concise, and professional. Focus on data-driven insights."""
    
    def _format_response(self, content: str) -> str:
        """
        Format response based on configured format
        
        Args:
            content: Raw response content
            
        Returns:
            Formatted response
        """
        if self.response_format == "raw":
            return content
        
        if self.response_format == "detailed":
            return f"[Engram Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n\n{content}"
        
        # Clean format (default)
        # Remove any reasoning tags or metadata
        lines = content.split('\n')
        clean_lines = [line for line in lines if not line.strip().startswith(('<think>', '</think>', 'reasoning:'))]
        return '\n'.join(clean_lines).strip()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check skill health status
        
        Returns:
            Health status dictionary
        """
        try:
            lmstudio_status = await self.lmstudio.health_check()
            return {
                "status": "healthy" if lmstudio_status else "degraded",
                "lmstudio": lmstudio_status,
                "tools_registered": len(self.tools),
                "response_format": self.response_format
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def shutdown(self):
        """Clean shutdown of skill resources"""
        await self.lmstudio.close()
        logger.info("Engram skill shutdown complete")
