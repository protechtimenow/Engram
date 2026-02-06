"""
Dual-Model Gateway for Clawdbot
Coordinates between Clawdbot Gateway (port 17501) and LMStudio Proxy (port 17502)
Provides automatic failover between multiple LMStudio endpoints
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EndpointType(Enum):
    PROXY = "proxy"      # Port 17502 - OpenAI-compatible proxy
    DIRECT = "direct"    # Port 1234 - Direct LMStudio
    GATEWAY = "gateway"  # Port 17501 - Clawdbot Gateway (WebSocket)


@dataclass
class Endpoint:
    name: str
    url: str
    port: int
    type: EndpointType
    priority: int  # Lower = higher priority
    healthy: bool = True
    last_error: Optional[str] = None


class DualModelGateway:
    """
    Manages multiple LMStudio endpoints with automatic failover
    """
    
    def __init__(self):
        self.endpoints: List[Endpoint] = [
            Endpoint("Proxy", "http://localhost:17502/v1", 17502, EndpointType.PROXY, 1),
            Endpoint("Direct", "http://localhost:1234/v1", 1234, EndpointType.DIRECT, 2),
        ]
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_endpoint: Optional[Endpoint] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Check health of all endpoints"""
        session = await self._get_session()
        results = {}
        
        for endpoint in self.endpoints:
            try:
                async with session.get(
                    f"{endpoint.url}/models",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    endpoint.healthy = response.status == 200
                    if response.status == 200:
                        data = await response.json()
                        models = [m.get("id") for m in data.get("data", [])]
                        results[endpoint.name] = {
                            "healthy": True,
                            "port": endpoint.port,
                            "models": models[:5]  # First 5 models
                        }
                    else:
                        endpoint.healthy = False
                        results[endpoint.name] = {
                            "healthy": False,
                            "port": endpoint.port,
                            "error": f"HTTP {response.status}"
                        }
            except Exception as e:
                endpoint.healthy = False
                endpoint.last_error = str(e)
                results[endpoint.name] = {
                    "healthy": False,
                    "port": endpoint.port,
                    "error": str(e)
                }
        
        return results
    
    def get_best_endpoint(self) -> Optional[Endpoint]:
        """Get the highest priority healthy endpoint"""
        healthy_endpoints = [e for e in self.endpoints if e.healthy]
        if not healthy_endpoints:
            return None
        return min(healthy_endpoints, key=lambda e: e.priority)
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request with automatic failover
        """
        session = await self._get_session()
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        # Try endpoints in priority order
        for endpoint in sorted(self.endpoints, key=lambda e: e.priority):
            if not endpoint.healthy:
                continue
                
            try:
                logger.info(f"Trying {endpoint.name} ({endpoint.url})...")
                async with session.post(
                    f"{endpoint.url}/chat/completions",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.current_endpoint = endpoint
                        logger.info(f"Success via {endpoint.name}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.warning(f"{endpoint.name} returned {response.status}: {error_text}")
                        endpoint.healthy = False
                        endpoint.last_error = f"HTTP {response.status}"
                        
            except Exception as e:
                logger.warning(f"{endpoint.name} failed: {e}")
                endpoint.healthy = False
                endpoint.last_error = str(e)
        
        raise Exception("All endpoints failed")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current gateway status"""
        health = await self.health_check_all()
        best = self.get_best_endpoint()
        
        return {
            "status": "healthy" if best else "unhealthy",
            "active_endpoint": best.name if best else None,
            "endpoints": health,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()


class ClawdbotBridge:
    """
    Bridge between Clawdbot Gateway and LMStudio endpoints
    Allows Clawdbot to use the dual-model gateway
    """
    
    def __init__(self, gateway: DualModelGateway):
        self.gateway = gateway
        self.default_model = "z-ai/glm-4.7-flash"
        
    async def handle_message(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Handle a message from Clawdbot
        """
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": message}
        ]
        
        try:
            response = await self.gateway.chat_completion(
                model=self.default_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response["choices"][0]["message"].get("content", "")
            return content
            
        except Exception as e:
            logger.error(f"Failed to get response: {e}")
            return f"[Error: {str(e)}]"


async def main():
    """Test the dual model gateway"""
    gateway = DualModelGateway()
    
    print("=" * 60)
    print("Dual-Model Gateway Status Check")
    print("=" * 60)
    
    status = await gateway.get_status()
    print(f"\nStatus: {status['status']}")
    print(f"Active Endpoint: {status['active_endpoint']}")
    
    print("\nEndpoints:")
    for name, info in status['endpoints'].items():
        health = "OK" if info['healthy'] else "FAIL"
        print(f"  [{health}] {name} (port {info['port']})")
        if info['healthy'] and 'models' in info:
            print(f"      Models: {', '.join(info['models'][:3])}")
    
    print("\n" + "=" * 60)
    print("Testing Chat Completion")
    print("=" * 60)
    
    try:
        response = await gateway.chat_completion(
            model="z-ai/glm-4.7-flash",
            messages=[{"role": "user", "content": "Hello from Engram"}]
        )
        content = response["choices"][0]["message"].get("content", "")
        print(f"\nResponse: {content}")
        print(f"Used endpoint: {gateway.current_endpoint.name if gateway.current_endpoint else 'unknown'}")
    except Exception as e:
        print(f"\nError: {e}")
    
    await gateway.close()


if __name__ == "__main__":
    asyncio.run(main())
