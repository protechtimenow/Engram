"""
Unit tests for Engram Skill
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from skills.engram.engram_skill import EngramSkill


@pytest.fixture
def config():
    """Test configuration"""
    return {
        "lmstudio_host": "localhost",
        "lmstudio_port": 1234,
        "model": "glm-4.7-flash",
        "response_format": "clean"
    }


@pytest.fixture
def skill(config):
    """Create skill instance"""
    return EngramSkill(config)


class TestEngramSkill:
    """Test suite for EngramSkill"""
    
    def test_initialization(self, skill):
        """Test skill initializes correctly"""
        assert skill is not None
        assert skill.response_format == "clean"
        assert len(skill.tools) == 4  # 4 registered tools
    
    def test_tool_registration(self, skill):
        """Test tools are registered correctly"""
        tool_names = [t["function"]["name"] for t in skill.tools]
        
        assert "analyze_market" in tool_names
        assert "generate_signal" in tool_names
        assert "get_confidence_score" in tool_names
        assert "assess_risk" in tool_names
    
    def test_system_prompt_generation(self, skill):
        """Test system prompt is generated"""
        prompt = skill._build_system_prompt()
        
        assert "Engram" in prompt
        assert "trading" in prompt.lower()
        assert "analysis" in prompt.lower()
    
    def test_response_formatting_clean(self, skill):
        """Test clean response formatting"""
        raw_response = "<think>reasoning here</think>\nActual response"
        formatted = skill._format_response(raw_response)
        
        assert "<think>" not in formatted
        assert "Actual response" in formatted
    
    def test_response_formatting_detailed(self, config):
        """Test detailed response formatting"""
        config["response_format"] = "detailed"
        skill = EngramSkill(config)
        
        response = skill._format_response("Test response")
        
        assert "[Engram Analysis" in response
        assert "Test response" in response
    
    def test_response_formatting_raw(self, config):
        """Test raw response formatting"""
        config["response_format"] = "raw"
        skill = EngramSkill(config)
        
        raw_content = "<think>reasoning</think>\nResponse"
        formatted = skill._format_response(raw_content)
        
        assert formatted == raw_content
    
    @pytest.mark.asyncio
    async def test_process_message_simple(self, skill):
        """Test processing simple message"""
        # Mock LMStudio response
        mock_response = {
            "content": "Market analysis complete",
            "role": "assistant"
        }
        
        skill.lmstudio.chat_completion = AsyncMock(return_value=mock_response)
        
        result = await skill.process_message("Analyze BTC/USD")
        
        assert result is not None
        assert isinstance(result, str)
        skill.lmstudio.chat_completion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_message_with_tools(self, skill):
        """Test processing message with tool calls"""
        # Mock LMStudio response with tool call
        mock_response_with_tools = {
            "content": "",
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_123",
                    "function": {
                        "name": "analyze_market",
                        "arguments": {"pair": "BTC/USD", "timeframe": "1h"}
                    }
                }
            ]
        }
        
        mock_final_response = {
            "content": "Based on analysis, BTC/USD shows bullish trend",
            "role": "assistant"
        }
        
        skill.lmstudio.chat_completion = AsyncMock(
            side_effect=[mock_response_with_tools, mock_final_response]
        )
        
        result = await skill.process_message("Analyze BTC/USD")
        
        assert result is not None
        assert "bullish" in result.lower() or "analysis" in result.lower()
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, skill):
        """Test health check when healthy"""
        skill.lmstudio.health_check = AsyncMock(return_value=True)
        
        health = await skill.health_check()
        
        assert health["status"] == "healthy"
        assert health["lmstudio"] is True
        assert health["tools_registered"] == 4
    
    @pytest.mark.asyncio
    async def test_health_check_degraded(self, skill):
        """Test health check when degraded"""
        skill.lmstudio.health_check = AsyncMock(return_value=False)
        
        health = await skill.health_check()
        
        assert health["status"] == "degraded"
        assert health["lmstudio"] is False
    
    @pytest.mark.asyncio
    async def test_health_check_error(self, skill):
        """Test health check with error"""
        skill.lmstudio.health_check = AsyncMock(side_effect=Exception("Connection failed"))
        
        health = await skill.health_check()
        
        assert health["status"] == "unhealthy"
        assert "error" in health
    
    @pytest.mark.asyncio
    async def test_execute_tools_analyze_market(self, skill):
        """Test executing analyze_market tool"""
        tool_calls = [
            {
                "id": "call_123",
                "function": {
                    "name": "analyze_market",
                    "arguments": {"pair": "BTC/USD", "timeframe": "1h"}
                }
            }
        ]
        
        results = await skill._execute_tools(tool_calls)
        
        assert len(results) == 1
        assert results[0]["role"] == "tool"
        assert results[0]["tool_call_id"] == "call_123"
    
    @pytest.mark.asyncio
    async def test_execute_tools_unknown(self, skill):
        """Test executing unknown tool"""
        tool_calls = [
            {
                "id": "call_456",
                "function": {
                    "name": "unknown_tool",
                    "arguments": {}
                }
            }
        ]
        
        results = await skill._execute_tools(tool_calls)
        
        assert len(results) == 1
        assert "error" in results[0]["content"].lower()
    
    @pytest.mark.asyncio
    async def test_shutdown(self, skill):
        """Test graceful shutdown"""
        skill.lmstudio.close = AsyncMock()
        
        await skill.shutdown()
        
        skill.lmstudio.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
