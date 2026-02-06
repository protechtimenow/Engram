"""
Dual-Model Proxy for Clawdbot
Bridges Clawdbot's OpenAI-compatible API requests to actual LLM providers
Supports StepFun + GLM models with intelligent routing
"""

import asyncio
import logging
import json
import os
import sys
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import aiohttp, install if not available
try:
    import aiohttp
    from aiohttp import web
except ImportError:
    logger.error("aiohttp not installed. Run: pip install aiohttp")
    raise


class DualModelProxy:
    """
    OpenAI-compatible API proxy that routes requests to different LLM providers
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 17501):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Model configurations
        self.models = {
            "gateway": {
                "id": "gateway",
                "name": "Dual Model Gateway",
                "description": "Intelligent routing between StepFun and GLM",
                "context_window": 128000,
                "max_tokens": 4000
            },
            "stepfun": {
                "id": "stepfun",
                "name": "StepFun AI (via OpenRouter)",
                "api_base": "https://openrouter.ai/api/v1",
                "api_key": os.getenv("OPENROUTER_API_KEY", ""),
                "model": "stepfun/step-3.5-flash:free",
                "context_window": 32000,
                "max_tokens": 4000
            },
            "glm": {
                "id": "glm",
                "name": "GLM-4",
                "api_base": os.getenv("GLM_API_BASE", "http://localhost:1234/v1"),
                "api_key": os.getenv("GLM_API_KEY", "lm-studio"),
                "context_window": 128000,
                "max_tokens": 4000
            }
        }
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get("/v1/models", self.list_models)
        self.app.router.add_post("/v1/chat/completions", self.chat_completions)
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_get("/", self.index)
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def index(self, request: web.Request) -> web.Response:
        """Root endpoint"""
        return web.json_response({
            "name": "Dual-Model Proxy for Clawdbot",
            "version": "1.0.0",
            "models_endpoint": "/v1/models",
            "chat_endpoint": "/v1/chat/completions",
            "health_endpoint": "/health"
        })
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "models_available": list(self.models.keys())
        })
    
    async def list_models(self, request: web.Request) -> web.Response:
        """List available models (OpenAI-compatible)"""
        models_data = []
        for model_id, model_info in self.models.items():
            models_data.append({
                "id": model_info["id"],
                "object": "model",
                "created": int(datetime.utcnow().timestamp()),
                "owned_by": "dual-model-proxy",
                "permission": [],
                "root": model_info["id"],
                "parent": None,
                "name": model_info["name"]
            })
        
        return web.json_response({
            "object": "list",
            "data": models_data
        })
    
    def _select_model_provider(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select the appropriate model provider based on the request
        
        Strategy:
        - Use GLM for simple/quick responses (localhost, low latency)
        - Use StepFun for complex reasoning tasks
        - Default to GLM if available, fallback to StepFun
        """
        model_id = request_data.get("model", "gateway")
        messages = request_data.get("messages", [])
        
        # Analyze message complexity
        total_length = sum(len(m.get("content", "")) for m in messages)
        has_tools = "tools" in request_data and request_data["tools"]
        
        # Simple heuristic for model selection
        if model_id == "gateway":
            # Check if GLM (LMStudio) is available locally
            glm_config = self.models["glm"]
            if glm_config["api_base"].startswith("http://localhost"):
                # Prefer local GLM for speed
                return glm_config
            else:
                # Use StepFun for remote
                return self.models["stepfun"]
        
        # Specific model requested
        if model_id in self.models:
            return self.models[model_id]
        
        # Default to GLM
        return self.models["glm"]
    
    async def chat_completions(self, request: web.Request) -> web.Response:
        """
        Handle chat completion requests (OpenAI-compatible)
        Routes to appropriate backend based on model selection
        """
        try:
            request_data = await request.json()
            logger.info(f"Chat completion request: model={request_data.get('model', 'default')}")
            
            # Select model provider
            provider = self._select_model_provider(request_data)
            logger.info(f"Routing to provider: {provider['name']}")
            
            # Forward request to backend
            session = await self._get_session()
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {provider.get('api_key', '')}"
            }
            
            # Prepare payload
            # Use provider's model if specified (for OpenRouter routing)
            model_id = provider.get("model", provider["id"])
            payload = {
                "model": model_id,
                "messages": request_data.get("messages", []),
                "temperature": request_data.get("temperature", 0.7),
                "max_tokens": request_data.get("max_tokens", provider.get("max_tokens", 4000)),
                "stream": request_data.get("stream", False)
            }
            
            # Add tools if present
            if "tools" in request_data:
                payload["tools"] = request_data["tools"]
            if "tool_choice" in request_data:
                payload["tool_choice"] = request_data["tool_choice"]
            
            # Make request to backend
            api_url = f"{provider['api_base']}/chat/completions"
            
            try:
                async with session.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Backend error: {response.status} - {error_text}")
                        
                        # Try fallback to other provider
                        fallback = self.models["stepfun"] if provider["id"] == "glm" else self.models["glm"]
                        if fallback["id"] != provider["id"]:
                            logger.info(f"Trying fallback to {fallback['name']}")
                            return await self._try_fallback(request_data, fallback)
                        
                        return web.json_response(
                            {"error": f"Backend error: {response.status}"},
                            status=response.status
                        )
                    
                    # Return successful response
                    data = await response.json()
                    return web.json_response(data)
                    
            except asyncio.TimeoutError:
                logger.error("Backend request timeout")
                return web.json_response(
                    {"error": "Backend request timeout"},
                    status=504
                )
            except Exception as e:
                logger.error(f"Backend request failed: {e}")
                
                # Try fallback
                fallback = self.models["stepfun"] if provider["id"] == "glm" else self.models["glm"]
                if fallback["id"] != provider["id"]:
                    logger.info(f"Trying fallback to {fallback['name']}")
                    return await self._try_fallback(request_data, fallback)
                
                return web.json_response(
                    {"error": f"Backend request failed: {str(e)}"},
                    status=502
                )
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request")
            return web.json_response(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return web.json_response(
                {"error": f"Internal error: {str(e)}"},
                status=500
            )
    
    async def _try_fallback(self, request_data: Dict[str, Any], fallback: Dict[str, Any]) -> web.Response:
        """Try fallback provider"""
        try:
            session = await self._get_session()
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {fallback.get('api_key', '')}"
            }
            
            # Use fallback's model if specified (for OpenRouter routing)
            fallback_model = fallback.get("model", fallback["id"])
            payload = {
                "model": fallback_model,
                "messages": request_data.get("messages", []),
                "temperature": request_data.get("temperature", 0.7),
                "max_tokens": request_data.get("max_tokens", fallback.get("max_tokens", 4000))
            }
            
            if "tools" in request_data:
                payload["tools"] = request_data["tools"]
            
            api_url = f"{fallback['api_base']}/chat/completions"
            
            async with session.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return web.json_response(data)
                else:
                    error_text = await response.text()
                    return web.json_response(
                        {"error": f"Fallback also failed: {response.status}"},
                        status=502
                    )
                    
        except Exception as e:
            return web.json_response(
                {"error": f"Fallback failed: {str(e)}"},
                status=502
            )
    
    async def start(self):
        """Start the proxy server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"=" * 60)
        logger.info(f"Dual-Model Proxy started on http://{self.host}:{self.port}")
        logger.info(f"Models available: {list(self.models.keys())}")
        logger.info(f"Health check: http://{self.host}:{self.port}/health")
        logger.info(f"=" * 60)
        
        # Keep running
        while True:
            await asyncio.sleep(3600)
    
    async def stop(self):
        """Stop the proxy server"""
        if self.session:
            await self.session.close()
        logger.info("Dual-Model Proxy stopped")


async def main():
    """Main entry point"""
    # Get configuration from environment
    host = os.getenv("DUAL_MODEL_HOST", "127.0.0.1")
    port = int(os.getenv("DUAL_MODEL_PORT", "17501"))
    
    # Check for required API keys
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY not set - StepFun provider will fail")
    
    proxy = DualModelProxy(host=host, port=port)
    
    try:
        await proxy.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await proxy.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
