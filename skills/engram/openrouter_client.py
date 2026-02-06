"""
OpenRouter Client for Engram
Direct connection to OpenRouter API (no LMStudio)
Routes to StepFun, GLM, and other models
"""

import aiohttp
import logging
import os
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    Async client for OpenRouter API
    Provides access to StepFun, GLM, and many other models
    """
    
    def __init__(self, 
                 model: str = "openai/gpt-4o-mini",
                 api_key: Optional[str] = None,
                 api_base: str = "https://openrouter.ai/api/v1"):
        """
        Initialize OpenRouter client
        
        Args:
            model: Model ID to use (e.g., "stepfun/step-3.5-flash", "nvidia/glm-4.7-flash")
            api_key: OpenRouter API key (or from env OPENROUTER_API_KEY)
            api_base: OpenRouter API base URL
        """
        self.api_base = api_base
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("No OpenRouter API key provided - client will not work")
        
        logger.info(f"OpenRouter client initialized: model={model}, api_base={api_base}")
    
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
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Send chat completion request to OpenRouter
        """
        if not self.api_key:
            raise Exception("OpenRouter API key not configured")
        
        session = await self._get_session()
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://engram.local",
            "X-Title": "Engram Trading Analysis"
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
                    logger.error(f"OpenRouter error {response.status}: {error_text}")
                    raise Exception(f"OpenRouter error {response.status}: {error_text}")
                    
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def list_models(self) -> List[Dict[str, str]]:
        """List available models from OpenRouter"""
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
        Check OpenRouter health
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
            logger.info("OpenRouter client session closed")
