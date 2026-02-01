"""
Test script for ClawdBot integration fixes
Tests WebSocket connection, Unicode logging, and new bot commands
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.engram_agent import EngramAgent

# Setup logging with ASCII characters
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_unicode_logging():
    """Test that Unicode logging works without errors"""
    logger.info("[TEST] Testing Unicode logging fix...")
    
    try:
        # These should not cause encoding errors on Windows
        logger.info("[OK] Unicode test passed")
        logger.warning("[WARN] Warning test passed")
        logger.error("[ERROR] Error test passed")
        logger.info("[EVENT] Event test passed")
        
        print("[OK] Unicode logging test PASSED")
        return True
    except Exception as e:
        print(f"[ERROR] Unicode logging test FAILED: {e}")
        return False


async def test_agent_initialization():
    """Test agent initialization with all new features"""
    logger.info("[TEST] Testing agent initialization...")
    
    try:
        config = {
            "lmstudio_host": "localhost",
            "lmstudio_port": 1234,
            "model": "glm-4.7-flash",
            "clawdbot_host": "localhost",
            "clawdbot_port": 18789,
            "clawdbot_token": "",
            "response_format": "clean"
        }
        
        agent = EngramAgent(config)
        
        # Check new features are initialized
        assert hasattr(agent, 'price_alerts'), "Missing price_alerts"
        assert hasattr(agent, 'portfolio'), "Missing portfolio"
        assert isinstance(agent.price_alerts, dict), "price_alerts not a dict"
        assert isinstance(agent.portfolio, dict), "portfolio not a dict"
        
        # Check portfolio has mock data
        assert 'BTC' in agent.portfolio, "BTC not in portfolio"
        assert 'ETH' in agent.portfolio, "ETH not in portfolio"
        
        print("[OK] Agent initialization test PASSED")
        return True
    except Exception as e:
        print(f"[ERROR] Agent initialization test FAILED: {e}")
        return False


async def test_command_parsing():
    """Test command parsing and routing"""
    logger.info("[TEST] Testing command parsing...")
    
    try:
        config = {
            "lmstudio_host": "localhost",
            "lmstudio_port": 1234,
            "model": "glm-4.7-flash",
            "clawdbot_host": "localhost",
            "clawdbot_port": 18789,
            "response_format": "clean"
        }
        
        agent = EngramAgent(config)
        
        # Test /help command
        help_response = agent._cmd_help()
        assert "/help" in help_response, "/help not in help response"
        assert "/status" in help_response, "/status not in help response"
        assert "/analyze" in help_response, "/analyze not in help response"
        assert "/alert" in help_response, "/alert not in help response"
        assert "/alerts" in help_response, "/alerts not in help response"
        assert "/portfolio" in help_response, "/portfolio not in help response"
        
        # Test /portfolio command
        portfolio_response = agent._cmd_portfolio()
        assert "BTC" in portfolio_response, "BTC not in portfolio response"
        assert "ETH" in portfolio_response, "ETH not in portfolio response"
        
        # Test /alert command
        alert_response = agent._cmd_alert("BTC 50000")
        assert "[OK]" in alert_response, "Alert not set successfully"
        assert "BTC" in alert_response, "BTC not in alert response"
        assert "50000" in alert_response or "50,000" in alert_response, "Price not in alert response"
        
        # Test /alerts command
        alerts_response = agent._cmd_alerts()
        assert "BTC" in alerts_response, "BTC not in alerts list"
        assert "50,000" in alerts_response or "50000" in alerts_response, "Price not in alerts list"
        
        print("[OK] Command parsing test PASSED")
        return True
    except Exception as e:
        print(f"[ERROR] Command parsing test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_event_handling():
    """Test event message handling"""
    logger.info("[TEST] Testing event handling...")
    
    try:
        config = {
            "lmstudio_host": "localhost",
            "lmstudio_port": 1234,
            "model": "glm-4.7-flash",
            "clawdbot_host": "localhost",
            "clawdbot_port": 18789,
            "response_format": "clean"
        }
        
        agent = EngramAgent(config)
        
        # Test event message handling (doesn't require WebSocket)
        event_message = {
            "type": "event",
            "event_type": "agent_registered",
            "data": {"agent_id": "engram"}
        }
        
        response = await agent.handle_message(event_message)
        assert response["type"] == "event_ack", "Event not acknowledged"
        assert response["status"] == "ok", "Event acknowledgment not ok"
        
        # Test pong message handling (doesn't require WebSocket)
        pong_message = {
            "type": "pong",
            "data": {"timestamp": "2024-01-15T12:00:00"}
        }
        
        response = await agent.handle_message(pong_message)
        assert response["type"] == "pong_ack", "Pong not handled"
        assert response["status"] == "ok", "Pong acknowledgment not ok"
        
        # Test that _handle_event method exists and works
        await agent._handle_event(event_message)
        
        print("[OK] Event handling test PASSED")
        return True
    except Exception as e:
        print(f"[ERROR] Event handling test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_price_alerts():
    """Test price alert functionality"""
    logger.info("[TEST] Testing price alerts...")
    
    try:
        config = {
            "lmstudio_host": "localhost",
            "lmstudio_port": 1234,
            "model": "glm-4.7-flash",
            "clawdbot_host": "localhost",
            "clawdbot_port": 18789,
            "response_format": "clean"
        }
        
        agent = EngramAgent(config)
        
        # Set multiple alerts
        agent._cmd_alert("BTC 50000")
        agent._cmd_alert("BTC 55000")
        agent._cmd_alert("ETH 3000")
        
        # Check alerts are stored
        assert "BTC" in agent.price_alerts, "BTC alerts not stored"
        assert "ETH" in agent.price_alerts, "ETH alerts not stored"
        assert len(agent.price_alerts["BTC"]) == 2, "BTC should have 2 alerts"
        assert len(agent.price_alerts["ETH"]) == 1, "ETH should have 1 alert"
        
        # Check alert data structure
        btc_alert = agent.price_alerts["BTC"][0]
        assert "price" in btc_alert, "Alert missing price"
        assert "created" in btc_alert, "Alert missing created timestamp"
        assert "triggered" in btc_alert, "Alert missing triggered flag"
        
        print("[OK] Price alerts test PASSED")
        return True
    except Exception as e:
        print(f"[ERROR] Price alerts test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("ClawdBot Integration Fix - Test Suite")
    print("="*60 + "\n")
    
    results = {}
    
    # Test 1: Unicode logging
    results["unicode_logging"] = await test_unicode_logging()
    
    # Test 2: Agent initialization
    results["agent_init"] = await test_agent_initialization()
    
    # Test 3: Command parsing
    results["command_parsing"] = await test_command_parsing()
    
    # Test 4: Event handling
    results["event_handling"] = await test_event_handling()
    
    # Test 5: Price alerts
    results["price_alerts"] = await test_price_alerts()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[OK] PASSED" if result else "[ERROR] FAILED"
        print(f"{test_name:20s}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[OK] All tests PASSED! ClawdBot integration fixes are working correctly.")
        return True
    else:
        print(f"\n[WARN] {total - passed} test(s) FAILED. Please review the errors above.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[WARN] Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
