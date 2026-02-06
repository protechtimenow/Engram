"""
StepFun Client for Engram
Direct connection to StepFun API (https://api.stepfun.ai)
Provides access to StepFun models including step-3.5-flash
"""

import aiohttp
import logging
import os
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)


class StepFunClient:
    """
    Async client for StepFun API
    Direct API access to StepFun models
    """
    
    DEFAULT_API_BASE = "https://api.stepfun.ai/v1"
    
    def __init__(self, 
                 model: str = "step-3.5-flash",
                 api_key: Optional[str] = None,
                 api_base: str = DEFAULT_API_BASE):
        """
        Initialize StepFun client
        
        Args:
            model: Model ID to use (e.g., "step-3.5-flash", "step-1-8k")
            api_key: StepFun API key (or from env STEPFUN_API_KEY)
            api_base: StepFun API base URL
        """
        self.api_base = api_base
        self.api_key = api_key or os.getenv("STEPFUN_API_KEY")
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("No StepFun API key provided - client will not work")
        else:
            # Mask key for logging
            masked_key = self.api_key[:10] + "..." if len(self.api_key) > 10 else "***"
            logger.info(f"StepFun client initialized: model={model}, api_base={api_base}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 0.9,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send chat completion request to StepFun API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions for function calling
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling value
            stream: Whether to stream the response
            
        Returns:
            Dict with 'content', 'role', and optionally 'tool_calls'
        """
        if not self.api_key:
            raise Exception("StepFun API key not configured. Set STEPFUN_API_KEY environment variable.")
        
        session = await self._get_session()
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            async with session.post(
                f"{self.api_base}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract response
                    choice = data["choices"][0]
                    message = choice["message"]
                    
                    result = {
                        "content": message.get("content", ""),
                        "role": message.get("role", "assistant")
                    }
                    
                    if "tool_calls" in message:
                        result["tool_calls"] = message["tool_calls"]
                    
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"StepFun error {response.status}: {error_text}")
                    raise Exception(f"StepFun API error {response.status}: {error_text}")
                    
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def list_models(self) -> List[Dict[str, str]]:
        """List available models from StepFun"""
        if not self.api_key:
            return []
        
        session = await self._get_session()
        
        try:
            async with session.get(
                f"{self.api_base}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check StepFun API health
        
        Returns:
            Dict with health status information
        """
        if not self.api_key:
            return {
                "healthy": False,
                "error": "No API key configured",
                "model": self.model
            }
        
        session = await self._get_session()
        
        try:
            async with session.get(
                f"{self.api_base}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                healthy = response.status == 200
                result = {
                    "healthy": healthy,
                    "api_base": self.api_base,
                    "model": self.model
                }
                if healthy:
                    data = await response.json()
                    result["available_models"] = len(data.get("data", []))
                return result
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "model": self.model
            }
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("StepFun client session closed")


# Simple test function
async def test_stepfun():
    """Test the StepFun client"""
    client = StepFunClient()
    
    print("Testing StepFun Client")
    print("=" * 50)
    
    # Health check
    health = await client.health_check()
    print(f"Health: {health}")
    
    if health["healthy"]:
        # Test chat
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! What model are you?"}
            ]
        )
        print(f"Response: {response['content']}")
    
    await client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_stepfun())
