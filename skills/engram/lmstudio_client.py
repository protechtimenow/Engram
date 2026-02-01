"""
LMStudio API Client
Handles communication with LMStudio local inference server
"""

import aiohttp
import logging
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)


class LMStudioClient:
    """
    Async client for LMStudio API
    """
    
    def __init__(self, host: str = "localhost", port: int = 1234, model: str = "glm-4.7-flash"):
        """
        Initialize LMStudio client
        
        Args:
            host: LMStudio server host
            port: LMStudio server port
            model: Model ID to use
        """
        self.base_url = f"http://{host}:{port}/v1"
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info(f"LMStudio client initialized: {self.base_url}, model: {model}")
    
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
        Send chat completion request to LMStudio
        
        Args:
            messages: List of message dictionaries
            tools: Optional list of tool schemas
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response dictionary with content and optional tool_calls
        """
        session = await self._get_session()
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "n_ctx": 4096  # Set context window to 4096 tokens
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        try:
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"LMStudio API error: {response.status} - {error_text}")
                    raise Exception(f"LMStudio API error: {response.status}")
                
                data = await response.json()
                
                # Extract response
                choice = data["choices"][0]
                message = choice["message"]
                
                result = {
                    "content": message.get("content", ""),
                    "role": message.get("role", "assistant")
                }
                
                # Include tool calls if present
                if "tool_calls" in message:
                    result["tool_calls"] = message["tool_calls"]
                
                # Filter out reasoning content if present
                if "reasoning_content" in message:
                    logger.debug(f"Reasoning filtered: {message['reasoning_content'][:100]}...")
                
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"Network error communicating with LMStudio: {e}")
            raise Exception(f"Failed to connect to LMStudio: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from LMStudio: {e}")
            raise Exception(f"Invalid response from LMStudio: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in chat_completion: {e}")
            raise
    
    async def list_models(self) -> List[Dict[str, str]]:
        """
        List available models
        
        Returns:
            List of model dictionaries
        """
        session = await self._get_session()
        
        try:
            async with session.get(
                f"{self.base_url}/models",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    raise Exception(f"Failed to list models: {response.status}")
                
                data = await response.json()
                return data.get("data", [])
                
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    async def health_check(self) -> bool:
        """
        Check if LMStudio is accessible
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            models = await self.list_models()
            # Check if our model is available
            model_ids = [m.get("id") for m in models]
            if self.model in model_ids:
                logger.info(f"Health check passed: model {self.model} available")
                return True
            else:
                logger.warning(f"Model {self.model} not found. Available: {model_ids}")
                return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("LMStudio client session closed")
