"""
Unit tests for Engram Agent
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from agents.engram_agent import EngramAgent


@pytest.fixture
def config():
    """Test configuration"""
    return {
        "lmstudio_host": "localhost",
        "lmstudio_port": 1234,
        "model": "glm-4.7-flash",
        "clawdbot_host": "localhost",
        "clawdbot_port": 18789,
        "clawdbot_token": "test_token",
        "response_format": "clean"
    }


@pytest.fixture
def agent(config):
    """Create agent instance"""
    return EngramAgent(config)


class TestEngramAgent:
    """Test suite for EngramAgent"""
    
    def test_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent is not None
        assert agent.gateway_host == "localhost"
        assert agent.gateway_port == 18789
        assert agent.running is False
    
    @pytest.mark.asyncio
    async def test_handle_ping(self, agent):
        """Test handling ping message"""
        ping_msg = {
            "type": "ping",
            "data": {"timestamp": "2024-01-01T00:00:00"}
        }
        
        agent._send_message = AsyncMock()
        
        response = await agent.handle_message(ping_msg)
        
        assert response["type"] == "pong"
        assert response["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_handle_user_message(self, agent):
        """Test handling user message"""
        user_msg = {
            "type": "message",
            "content": "Analyze BTC/USD",
            "context": {"platform": "telegram"}
        }
        
        # Mock skill response
        agent.skill.process_message = AsyncMock(
            return_value="BTC/USD analysis complete"
        )
        
        response = await agent.handle_message(user_msg)
        
        assert response["type"] == "response"
        assert "analysis" in response["content"].lower()
        assert response["agent"] == "engram"
    
    @pytest.mark.asyncio
    async def test_handle_health_check(self, agent):
        """Test handling health check"""
        health_msg = {
            "type": "health_check"
        }
        
        # Mock skill health check
        agent.skill.health_check = AsyncMock(
            return_value={
                "status": "healthy",
                "lmstudio": True,
                "tools_registered": 4
            }
        )
        
        response = await agent.handle_message(health_msg)
        
        assert response["type"] == "health_response"
        assert response["status"] == "healthy"
        assert "details" in response
    
    @pytest.mark.asyncio
    async def test_handle_unknown_message(self, agent):
        """Test handling unknown message type"""
        unknown_msg = {
            "type": "unknown_type",
            "data": "test"
        }
        
        response = await agent.handle_message(unknown_msg)
        
        assert response["type"] == "error"
        assert "unknown" in response["error"].lower()
    
    @pytest.mark.asyncio
    async def test_send_hello(self, agent):
        """Test sending hello message"""
        agent._send_message = AsyncMock()
        
        await agent._send_hello()
        
        agent._send_message.assert_called_once()
        call_args = agent._send_message.call_args[0][0]
        
        assert call_args["type"] == "hello"
        assert call_args["agent"]["id"] == "engram"
    
    @pytest.mark.asyncio
    async def test_send_pong(self, agent):
        """Test sending pong response"""
        agent._send_message = AsyncMock()
        
        ping_data = {"timestamp": "2024-01-01T00:00:00"}
        await agent._send_pong(ping_data)
        
        agent._send_message.assert_called_once()
        call_args = agent._send_message.call_args[0][0]
        
        assert call_args["type"] == "pong"
        assert call_args["data"] == ping_data
    
    @pytest.mark.asyncio
    async def test_send_message(self, agent):
        """Test sending message via WebSocket"""
        mock_ws = AsyncMock()
        agent.websocket = mock_ws
        
        test_msg = {"type": "test", "data": "hello"}
        await agent._send_message(test_msg)
        
        mock_ws.send.assert_called_once()
        sent_data = mock_ws.send.call_args[0][0]
        
        # Verify JSON formatting
        parsed = json.loads(sent_data)
        assert parsed["type"] == "test"
        assert parsed["data"] == "hello"
    
    @pytest.mark.asyncio
    async def test_send_message_no_websocket(self, agent):
        """Test sending message without WebSocket connection"""
        agent.websocket = None
        
        with pytest.raises(Exception, match="WebSocket not connected"):
            await agent._send_message({"type": "test"})
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_connect_success(self, mock_connect, agent):
        """Test successful WebSocket connection"""
        mock_ws = AsyncMock()
        mock_connect.return_value = mock_ws
        
        agent._send_hello = AsyncMock()
        
        result = await agent.connect()
        
        assert result is True
        assert agent.websocket is not None
        agent._send_hello.assert_called_once()
        
        # Verify connection parameters
        call_kwargs = mock_connect.call_args[1]
        assert "clawdbot-v1" in call_kwargs["subprotocols"]
        assert "Authorization" in call_kwargs["extra_headers"]
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_connect_failure(self, mock_connect, agent):
        """Test failed WebSocket connection"""
        mock_connect.side_effect = Exception("Connection refused")
        
        result = await agent.connect()
        
        assert result is False
        assert agent.websocket is None
    
    @pytest.mark.asyncio
    async def test_shutdown(self, agent):
        """Test graceful shutdown"""
        mock_ws = AsyncMock()
        agent.websocket = mock_ws
        agent.running = True
        agent.skill.shutdown = AsyncMock()
        
        await agent.shutdown()
        
        assert agent.running is False
        mock_ws.close.assert_called_once()
        agent.skill.shutdown.assert_called_once()
    
    def test_reconnect_backoff(self, agent):
        """Test exponential backoff for reconnection"""
        assert agent.reconnect_delay == 1
        
        # Simulate failed connections
        agent.reconnect_delay = 2
        agent.reconnect_delay = min(agent.reconnect_delay * 2, agent.max_reconnect_delay)
        assert agent.reconnect_delay == 4
        
        agent.reconnect_delay = min(agent.reconnect_delay * 2, agent.max_reconnect_delay)
        assert agent.reconnect_delay == 8
        
        # Should cap at max
        for _ in range(10):
            agent.reconnect_delay = min(agent.reconnect_delay * 2, agent.max_reconnect_delay)
        
        assert agent.reconnect_delay == agent.max_reconnect_delay


class TestAgentIntegration:
    """Integration tests for agent"""
    
    @pytest.mark.asyncio
    async def test_message_flow(self, agent):
        """Test complete message flow"""
        # Mock WebSocket
        mock_ws = AsyncMock()
        agent.websocket = mock_ws
        
        # Mock skill
        agent.skill.process_message = AsyncMock(
            return_value="Analysis complete"
        )
        
        # Simulate incoming message
        incoming = {
            "type": "message",
            "content": "Analyze market",
            "context": {}
        }
        
        response = await agent.handle_message(incoming)
        
        assert response["type"] == "response"
        assert response["content"] == "Analysis complete"
        agent.skill.process_message.assert_called_once_with(
            "Analyze market",
            {}
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
