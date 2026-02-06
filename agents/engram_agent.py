"""
Engram ClawdBot Agent
Handles message routing and response formatting across platforms
"""

import logging
import json
import asyncio
import websockets
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import sys
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.engram.engram_skill import EngramSkill

logger = logging.getLogger(__name__)


class EngramAgent:
    """
    ClawdBot agent for Engram trading analysis
    Handles WebSocket communication with ClawdBot gateway
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Engram agent
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Pass config to skill with provider selection
        skill_config = {
            "model": config.get("model", "step-3.5-flash"),
            "provider": config.get("provider", "stepfun"),
            "openrouter_api_key": config.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY"),
            "stepfun_api_key": config.get("stepfun_api_key") or os.getenv("STEPFUN_API_KEY"),
            "response_format": config.get("response_format", "clean")
        }
        self.skill = EngramSkill(skill_config)
        
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.reconnect_delay = 1
        self.max_reconnect_delay = 60
        
        # ClawdBot gateway settings
        self.gateway_host = config.get("clawdbot_host", "localhost")
        self.gateway_port = config.get("clawdbot_port", 18789)
        self.gateway_token = config.get("clawdbot_token", "")
        
        # Price alerts storage
        self.price_alerts: Dict[str, List[Dict[str, Any]]] = {}
        
        # Portfolio tracking (mock data for now)
        self.portfolio = {
            "BTC": {"amount": 0.5, "avg_price": 45000},
            "ETH": {"amount": 2.0, "avg_price": 2800}
        }
        
        logger.info(f"Engram agent initialized for gateway {self.gateway_host}:{self.gateway_port}")
    
    async def connect(self):
        """
        Connect to ClawdBot gateway via WebSocket
        
        This fixes the 1008 policy violation error by:
        1. Using correct token in query string
        2. Proper authentication challenge-response handshake
        3. Correct message types (chat, auth, etc.)
        """
        # Use token from ClawdBot config
        token = self.gateway_token or "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
        # OpenClaw gateway validates token from connect message, not URL
        uri = f"ws://{self.gateway_host}:{self.gateway_port}"
        
        try:
            logger.info(f"Attempting connection to ws://{self.gateway_host}:{self.gateway_port}")
            
            # Connect without subprotocols - OpenClaw doesn't use them
            # Add timeout to prevent indefinite hanging
            self.websocket = await asyncio.wait_for(websockets.connect(uri), timeout=10)
            
            logger.info(f"[OK] Connected to OpenClaw gateway")
            
            # Handle authentication challenge-response
            if await self._authenticate():
                # Reset reconnect delay on successful connection
                self.reconnect_delay = 1
                return True
            else:
                logger.error("[ERROR] Authentication failed")
                await self.websocket.close()
                return False
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to connect to gateway: {e}")
            return False
    
    async def _authenticate(self) -> bool:
        """
        Handle ClawdBot authentication challenge-response
        Uses proper ClawdBot protocol: send 'connect' request after challenge
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Wait for initial challenge message
            logger.info("Waiting for authentication challenge...")
            message = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            data = json.loads(message)
            
            logger.debug(f"Received: {data}")
            
            # Check if it's a connection challenge
            if data.get("type") == "event" and data.get("event") == "connect.challenge":
                nonce = data.get("payload", {}).get("nonce")
                token = self.gateway_token or "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
                logger.debug(f"Using token: {token[:10]}...{token[-10:]} (length: {len(token)})")
                
                # Send connect request with proper ClawdBot protocol
                connect_msg = {
                    "type": "req",
                    "id": str(uuid.uuid4()),
                    "method": "connect",
                    "params": {
                        "minProtocol": 3,
                        "maxProtocol": 3,
                        "client": {
                            "id": "gateway-client",
                            "displayName": "Engram Trading Assistant",
                            "version": "1.0.0",
                            "platform": "python",
                            "mode": "backend"
                        },
                        "caps": ["chat"],
                        "auth": {
                            "token": token
                        },
                        "role": "operator",
                        "scopes": ["operator.admin"]
                    }
                }
                await self._send_message(connect_msg)
                logger.info("[OK] Sent connect request")
                
                # Wait for connect response
                message = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
                data = json.loads(message)
                
                if data.get("type") == "res" and data.get("ok") == True:
                    logger.info("[OK] Authentication successful")
                    return True
                else:
                    logger.error(f"[ERROR] Authentication failed: {data}")
                    return False
            else:
                logger.warning(f"[WARN] Unexpected initial message: {data}")
                # Continue anyway - might be a different protocol version
                return True
                
        except asyncio.TimeoutError:
            logger.error("[ERROR] Authentication timeout")
            return False
        except Exception as e:
            logger.error(f"[ERROR] Authentication error: {e}")
            return False
    
    async def _send_hello(self):
        """Send hello/handshake message to gateway (not used for ClawdBot)"""
        # ClawdBot uses auth challenge-response instead of hello
        pass
    
    async def _send_message(self, message: Dict[str, Any]):
        """
        Send properly framed JSON message to gateway
        
        Args:
            message: Message dictionary
        """
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        # Proper JSON framing for ClawdBot
        json_str = json.dumps(message)
        await self.websocket.send(json_str)
    
    async def _send_pong(self, ping_data: Any):
        """Respond to ping with pong"""
        pong_msg = {
            "type": "pong",
            "data": ping_data,
            "timestamp": datetime.now().isoformat()
        }
        await self._send_message(pong_msg)
    
    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle incoming message from gateway
        
        Args:
            message: Message dictionary
            
        Returns:
            Response dictionary or None if no response needed
        """
        msg_type = message.get("type")
        
        # Handle ping
        if msg_type == "ping":
            await self._send_pong(message.get("data"))
            return None  # No response needed - pong already sent
        
        # Handle event messages
        if msg_type == "event":
            await self._handle_event(message)
            return None  # Events don't need responses
        
        # Handle pong
        if msg_type == "pong":
            logger.debug("[OK] Received pong from gateway")
            return None
        
        # Handle request frames from ClawdBot (type: "req")
        if msg_type == "req":
            method = message.get("method")
            req_id = message.get("id")
            params = message.get("params", {})
            
            logger.info(f"[REQUEST] Method: {method}, ID: {req_id}")
            
            # Handle chat.send method (Telegram messages routed through ClawdBot)
            if method == "chat.send":
                content = params.get("message", "")
                context = params.get("context", {})
                
                # Check if it's a command
                if content.startswith("/"):
                    response_text = await self._handle_command(content, context)
                else:
                    # Process with skill
                    response_text = await self.skill.process_message(content, context)
                
                # Send response as a response frame
                return {
                    "type": "res",
                    "id": req_id,
                    "ok": True,
                    "payload": {
                        "message": response_text,
                        "agent": "engram"
                    }
                }
            
            # Handle other methods
            logger.info(f"[REQUEST] Unhandled method: {method}")
            return {
                "type": "res",
                "id": req_id,
                "ok": False,
                "error": {
                    "code": "METHOD_NOT_FOUND",
                    "message": f"Method {method} not implemented"
                }
            }
        
        # Handle user chat message (ClawdBot uses 'chat' type)
        if msg_type == "chat" or msg_type == "message":
            content = message.get("message", message.get("content", ""))
            context = message.get("context", {})
            
            # Check if it's a command
            if content.startswith("/"):
                response_text = await self._handle_command(content, context)
            else:
                # Process with skill
                response_text = await self.skill.process_message(content, context)
            
            # Send response back as chat message
            return {
                "type": "chat",
                "message": response_text,
                "agent": "engram"
            }
        
        # Handle response messages (from other agents)
        if msg_type == "response":
            logger.debug(f"[OK] Received response: {message.get('response', '')[:100]}...")
            return None
        
        # Handle health check
        if msg_type == "health_check":
            health = await self.skill.health_check()
            return {
                "type": "health_response",
                "status": health["status"],
                "details": health
            }
        
        # Unknown message type
        logger.warning(f"[WARN] Unknown message type: {msg_type}")
        return None
    
    async def _handle_event(self, event: Dict[str, Any]):
        """
        Handle event messages from ClawdBot gateway
        This prevents 1008 policy violation errors
        
        Args:
            event: Event message dictionary
        """
        event_type = event.get("event", event.get("event_type", "unknown"))
        payload = event.get("payload", event.get("data", {}))
        
        logger.info(f"[EVENT] Received event: {event_type}")
        logger.debug(f"[EVENT] Payload: {payload}")
        
        # Process different event types
        if event_type == "auth.success":
            logger.info("[OK] Agent successfully authenticated with gateway")
        elif event_type == "agent_registered":
            logger.info("[OK] Agent successfully registered with gateway")
        elif event_type == "channel_connected":
            logger.info(f"[OK] Channel connected: {payload.get('channel')}")
        elif event_type == "channel_disconnected":
            logger.warning(f"[WARN] Channel disconnected: {payload.get('channel')}")
        elif event_type == "connect.challenge":
            # Already handled in _authenticate
            pass
        else:
            logger.debug(f"[EVENT] Unhandled event type: {event_type}")
    
    async def _handle_command(self, command: str, context: Dict[str, Any]) -> str:
        """
        Handle bot commands
        
        Args:
            command: Command string (e.g., "/help", "/analyze BTC")
            context: Message context
            
        Returns:
            Response string
        """
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "/help":
            return self._cmd_help()
        elif cmd == "/status":
            return await self._cmd_status()
        elif cmd == "/analyze":
            return await self._cmd_analyze(args)
        elif cmd == "/alert":
            return self._cmd_alert(args)
        elif cmd == "/alerts":
            return self._cmd_alerts()
        elif cmd == "/portfolio":
            return self._cmd_portfolio()
        else:
            return f"Unknown command: {cmd}\nType /help for available commands."
    
    def _cmd_help(self) -> str:
        """Show help message"""
        return """[Engram Trading Bot - Commands]

/help - Show this help message
/status - Check bot status and health
/analyze <symbol> - Analyze trading pair (e.g., /analyze BTC/USD)
/alert <symbol> <price> - Set price alert (e.g., /alert BTC 50000)
/alerts - List active price alerts
/portfolio - View your portfolio

Examples:
  /analyze ETH/USD
  /alert BTC 45000
  /alerts
  /portfolio
"""
    
    async def _cmd_status(self) -> str:
        """Check bot status"""
        health = await self.skill.health_check()
        
        status_lines = [
            "[Bot Status]",
            f"Status: {health.get('status', 'unknown').upper()}",
            f"AI Provider: OpenRouter",
            f"Model: {self.config.get('model', 'openai/gpt-4o-mini')}",
            f"Tools: {health.get('tools_registered', 0)} registered",
            f"Active Alerts: {sum(len(alerts) for alerts in self.price_alerts.values())}",
            f"Portfolio Items: {len(self.portfolio)}",
            f"Uptime: Connected"
        ]
        
        return "\n".join(status_lines)
    
    async def _cmd_analyze(self, symbol: str) -> str:
        """Analyze trading pair"""
        if not symbol:
            return "Please specify a trading pair. Example: /analyze BTC/USD"
        
        # Use skill to analyze
        analysis_request = f"Analyze {symbol} and provide trading signal"
        return await self.skill.process_message(analysis_request, {})
    
    def _cmd_alert(self, args: str) -> str:
        """Set price alert"""
        parts = args.strip().split()
        if len(parts) < 2:
            return "Usage: /alert <symbol> <price>\nExample: /alert BTC 50000"
        
        symbol = parts[0].upper()
        try:
            price = float(parts[1])
        except ValueError:
            return "Invalid price. Please use a number."
        
        # Add alert
        if symbol not in self.price_alerts:
            self.price_alerts[symbol] = []
        
        alert = {
            "price": price,
            "created": datetime.now().isoformat(),
            "triggered": False
        }
        
        self.price_alerts[symbol].append(alert)
        
        return f"[OK] Price alert set for {symbol} at ${price:,.2f}"
    
    def _cmd_alerts(self) -> str:
        """List active alerts"""
        if not self.price_alerts:
            return "No active price alerts.\nSet one with: /alert <symbol> <price>"
        
        lines = ["[Active Price Alerts]"]
        for symbol, alerts in self.price_alerts.items():
            active_alerts = [a for a in alerts if not a.get("triggered")]
            if active_alerts:
                lines.append(f"\n{symbol}:")
                for alert in active_alerts:
                    price = alert["price"]
                    created = alert["created"][:10]  # Just date
                    lines.append(f"  - ${price:,.2f} (set {created})")
        
        if len(lines) == 1:
            return "No active price alerts."
        
        return "\n".join(lines)
    
    def _cmd_portfolio(self) -> str:
        """View portfolio"""
        if not self.portfolio:
            return "Portfolio is empty."
        
        lines = ["[Portfolio Summary]"]
        total_value = 0
        
        for symbol, data in self.portfolio.items():
            amount = data["amount"]
            avg_price = data["avg_price"]
            value = amount * avg_price
            total_value += value
            
            lines.append(f"\n{symbol}:")
            lines.append(f"  Amount: {amount}")
            lines.append(f"  Avg Price: ${avg_price:,.2f}")
            lines.append(f"  Value: ${value:,.2f}")
        
        lines.append(f"\nTotal Value: ${total_value:,.2f}")
        
        return "\n".join(lines)
    
    async def listen(self):
        """Listen for messages from gateway"""
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        try:
            async for message in self.websocket:
                try:
                    # Parse JSON message
                    data = json.loads(message)
                    logger.info(f"[RECV] Type: {data.get('type', 'unknown')}, Event: {data.get('event', 'N/A')}, Method: {data.get('method', 'N/A')}")
                    logger.debug(f"[RECV FULL] {data}")
                    
                    # Handle message
                    response = await self.handle_message(data)
                    
                    # Send response if there is one
                    if response:
                        await self._send_message(response)
                        
                except json.JSONDecodeError as e:
                    logger.error(f"[ERROR] Invalid JSON received: {e}")
                except Exception as e:
                    logger.error(f"[ERROR] Error handling message: {e}")
                    
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning(f"[WARN] WebSocket connection closed: {e}")
        except Exception as e:
            logger.error(f"[ERROR] Error in listen loop: {e}")
    
    async def run(self):
        """
        Main run loop with automatic reconnection
        """
        self.running = True
        
        while self.running:
            try:
                # Connect to gateway
                if await self.connect():
                    # Listen for messages
                    await self.listen()
                
                # Connection lost, attempt reconnect
                if self.running:
                    logger.info(f"Reconnecting in {self.reconnect_delay}s...")
                    await asyncio.sleep(self.reconnect_delay)
                    
                    # Exponential backoff
                    self.reconnect_delay = min(
                        self.reconnect_delay * 2,
                        self.max_reconnect_delay
                    )
                    
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.running = False
            except Exception as e:
                logger.error(f"Error in run loop: {e}")
                if self.running:
                    await asyncio.sleep(self.reconnect_delay)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down Engram agent...")
        self.running = False
        
        if self.websocket:
            await self.websocket.close()
        
        await self.skill.shutdown()
        logger.info("Engram agent shutdown complete")


async def main():
    """Main entry point for standalone agent"""
    # Load configuration from environment
    config = {
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY", ""),
        "model": os.getenv("ENGRAM_MODEL", "openai/gpt-4o-mini"),
        "clawdbot_host": os.getenv("CLAWDBOT_HOST", "localhost"),
        "clawdbot_port": int(os.getenv("CLAWDBOT_PORT", "18789")),
        "clawdbot_token": os.getenv("CLAWDBOT_TOKEN", ""),
        "response_format": os.getenv("ENGRAM_RESPONSE_FORMAT", "clean")
    }
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run agent
    agent = EngramAgent(config)
    
    try:
        await agent.run()
    except KeyboardInterrupt:
        pass
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
