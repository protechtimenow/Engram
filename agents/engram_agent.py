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
        self.skill = EngramSkill(config)
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
        1. Using correct clawdbot-v1 subprotocol
        2. Proper JSON message framing
        3. Correct authentication headers
        """
        uri = f"ws://{self.gateway_host}:{self.gateway_port}/ws"
        
        headers = {
            "User-Agent": "Engram-Agent/1.0",
            "X-Agent-ID": "engram",
            "X-Agent-Version": "1.0.0"
        }
        
        # Use token from ClawdBot config if not provided
        token = self.gateway_token or "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            # DEBUG: Log headers being sent
            logger.info(f"Attempting connection to {uri}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Subprotocols: ['clawdbot-v1']")
            
            # Use clawdbot-v1 subprotocol to fix 1008 error
            self.websocket = await websockets.connect(
                uri,
                subprotocols=["clawdbot-v1"],
                additional_headers=headers,
                ping_interval=30,
                ping_timeout=10
            )
            
            logger.info(f"[OK] Connected to ClawdBot gateway: {uri}")
            logger.info(f"[OK] Connection User-Agent: {headers.get('User-Agent')}")
            
            # Don't send hello immediately - wait for ClawdBot to send first message
            # ClawdBot will send an event message first
            
            # Reset reconnect delay on successful connection
            self.reconnect_delay = 1
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to gateway: {e}")
            return False
    
    async def _send_hello(self):
        """Send hello/handshake message to gateway"""
        hello_msg = {
            "type": "hello",
            "agent": {
                "id": "engram",
                "name": "Engram Trading Assistant",
                "version": "1.0.0",
                "capabilities": ["trading_analysis", "market_signals", "risk_assessment"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
        await self._send_message(hello_msg)
        logger.info("Sent hello message to gateway")
    
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
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming message from gateway
        
        Args:
            message: Message dictionary
            
        Returns:
            Response dictionary
        """
        msg_type = message.get("type")
        
        # Handle ping
        if msg_type == "ping":
            await self._send_pong(message.get("data"))
            return {"type": "pong", "status": "ok"}
        
        # Handle event messages (FIX for 1008 error)
        if msg_type == "event":
            await self._handle_event(message)
            return {"type": "event_ack", "status": "ok"}
        
        # Handle pong
        if msg_type == "pong":
            logger.debug("[OK] Received pong from gateway")
            return {"type": "pong_ack", "status": "ok"}
        
        # Handle user message
        if msg_type == "message":
            content = message.get("content", "")
            context = message.get("context", {})
            
            # Check if it's a command
            if content.startswith("/"):
                response_text = await self._handle_command(content, context)
            else:
                # Process with skill
                response_text = await self.skill.process_message(content, context)
            
            return {
                "type": "response",
                "content": response_text,
                "agent": "engram",
                "timestamp": datetime.now().isoformat()
            }
        
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
        return {
            "type": "error",
            "error": f"Unknown message type: {msg_type}"
        }
    
    async def _handle_event(self, event: Dict[str, Any]):
        """
        Handle event messages from ClawdBot gateway
        This prevents 1008 policy violation errors
        
        Args:
            event: Event message dictionary
        """
        event_type = event.get("event_type", "unknown")
        event_data = event.get("data", {})
        
        logger.info(f"[EVENT] Received event: {event_type}")
        logger.debug(f"[EVENT] Event data: {event_data}")
        
        # Process different event types
        if event_type == "agent_registered":
            logger.info("[OK] Agent successfully registered with gateway")
        elif event_type == "channel_connected":
            logger.info(f"[OK] Channel connected: {event_data.get('channel')}")
        elif event_type == "channel_disconnected":
            logger.warning(f"[WARN] Channel disconnected: {event_data.get('channel')}")
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
            f"LMStudio: {'[OK]' if health.get('lmstudio') else '[ERROR]'}",
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
                    
                    # Handle message
                    response = await self.handle_message(data)
                    
                    # Send response if not a pong or event_ack (already handled)
                    if response.get("type") not in ["pong", "pong_ack", "event_ack"]:
                        await self._send_message(response)
                        
                except json.JSONDecodeError as e:
                    logger.error(f"[ERROR] Invalid JSON received: {e}")
                except Exception as e:
                    logger.error(f"[ERROR] Error handling message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("[WARN] WebSocket connection closed")
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
        "lmstudio_host": os.getenv("LMSTUDIO_HOST", "100.118.172.23"),
        "lmstudio_port": int(os.getenv("LMSTUDIO_PORT", "1234")),
        "model": os.getenv("ENGRAM_MODEL", "glm-4.7-flash"),
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
