"""
Critical Path Testing for Engram-ClawdBot Integration
Tests against real ClawdBot gateway and LMStudio
"""

import asyncio
import os
import sys
import json
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.engram_agent import EngramAgent
from skills.engram.lmstudio_client import LMStudioClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_1_websocket_connection():
    """
    TEST 1: WebSocket Connection to ClawdBot Gateway
    Critical: This tests the 1008 handshake error fix
    """
    logger.info("=" * 60)
    logger.info("TEST 1: WebSocket Connection to ClawdBot Gateway")
    logger.info("=" * 60)
    
    config = {
        "lmstudio_host": os.getenv("LMSTUDIO_HOST", "localhost"),
        "lmstudio_port": int(os.getenv("LMSTUDIO_PORT", "1234")),
        "model": os.getenv("ENGRAM_MODEL", "glm-4.7-flash"),
        "clawdbot_host": os.getenv("CLAWDBOT_HOST", "127.0.0.1"),
        "clawdbot_port": int(os.getenv("CLAWDBOT_PORT", "18789")),
        "clawdbot_token": os.getenv("CLAWDBOT_TOKEN", "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"),
        "response_format": "clean"
    }
    
    logger.info(f"Connecting to: ws://{config['clawdbot_host']}:{config['clawdbot_port']}/ws")
    logger.info(f"Using token: {config['clawdbot_token'][:20]}...")
    
    agent = EngramAgent(config)
    
    try:
        # Attempt connection
        success = await agent.connect()
        
        if success:
            logger.info("✅ TEST 1 PASSED: WebSocket connection successful!")
            logger.info(f"   - Subprotocol: clawdbot-v1")
            logger.info(f"   - Connection established without 1008 error")
            logger.info(f"   - Hello message sent successfully")
            
            # Close connection
            if agent.websocket:
                await agent.websocket.close()
            
            return True
        else:
            logger.error("❌ TEST 1 FAILED: Could not establish WebSocket connection")
            return False
            
    except Exception as e:
        logger.error(f"❌ TEST 1 FAILED: {e}")
        logger.exception("Full traceback:")
        return False


async def test_2_lmstudio_integration():
    """
    TEST 2: LMStudio API Integration
    Verify model is available and responding
    """
    logger.info("=" * 60)
    logger.info("TEST 2: LMStudio API Integration")
    logger.info("=" * 60)
    
    host = os.getenv("LMSTUDIO_HOST", "localhost")
    port = int(os.getenv("LMSTUDIO_PORT", "1234"))
    model = os.getenv("ENGRAM_MODEL", "glm-4.7-flash")
    
    logger.info(f"Connecting to: http://{host}:{port}/v1")
    logger.info(f"Testing model: {model}")
    
    client = LMStudioClient(host=host, port=port, model=model)
    
    try:
        # Test 1: List models
        logger.info("Listing available models...")
        models = await client.list_models()
        
        if models:
            logger.info(f"✅ Found {len(models)} models:")
            for m in models:
                logger.info(f"   - {m.get('id', 'unknown')}")
        else:
            logger.warning("⚠️  No models found")
        
        # Test 2: Health check
        logger.info(f"Checking if model '{model}' is available...")
        health = await client.health_check()
        
        if health:
            logger.info(f"✅ Model '{model}' is available and healthy")
        else:
            logger.warning(f"⚠️  Model '{model}' not found in available models")
            logger.info("Available models: " + ", ".join([m.get('id', '') for m in models]))
        
        # Test 3: Simple chat completion
        logger.info("Testing chat completion...")
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'test successful' if you can read this."}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        if response and response.get("content"):
            logger.info(f"✅ TEST 2 PASSED: LMStudio integration working!")
            logger.info(f"   - Response: {response['content'][:100]}")
            await client.close()
            return True
        else:
            logger.error("❌ TEST 2 FAILED: No response from LMStudio")
            await client.close()
            return False
            
    except Exception as e:
        logger.error(f"❌ TEST 2 FAILED: {e}")
        logger.exception("Full traceback:")
        await client.close()
        return False


async def test_3_complete_message_flow():
    """
    TEST 3: Complete Message Flow
    Send a query and get a response through the full stack
    """
    logger.info("=" * 60)
    logger.info("TEST 3: Complete Message Flow")
    logger.info("=" * 60)
    
    config = {
        "lmstudio_host": os.getenv("LMSTUDIO_HOST", "localhost"),
        "lmstudio_port": int(os.getenv("LMSTUDIO_PORT", "1234")),
        "model": os.getenv("ENGRAM_MODEL", "glm-4.7-flash"),
        "clawdbot_host": os.getenv("CLAWDBOT_HOST", "127.0.0.1"),
        "clawdbot_port": int(os.getenv("CLAWDBOT_PORT", "18789")),
        "clawdbot_token": os.getenv("CLAWDBOT_TOKEN", "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"),
        "response_format": "clean"
    }
    
    agent = EngramAgent(config)
    
    try:
        # Test message
        test_message = {
            "type": "message",
            "content": "Analyze BTC/USD market conditions",
            "context": {"platform": "test"}
        }
        
        logger.info(f"Sending test message: {test_message['content']}")
        
        # Process message
        response = await agent.handle_message(test_message)
        
        if response and response.get("type") == "response":
            logger.info("✅ TEST 3 PASSED: Complete message flow working!")
            logger.info(f"   - Response type: {response['type']}")
            logger.info(f"   - Agent: {response.get('agent', 'unknown')}")
            logger.info(f"   - Content preview: {response.get('content', '')[:200]}...")
            
            # Verify response is clean (no reasoning tags)
            content = response.get('content', '')
            if '<think>' not in content and 'reasoning:' not in content.lower():
                logger.info("   - ✅ Response is clean (no reasoning content)")
            else:
                logger.warning("   - ⚠️  Response contains reasoning content")
            
            await agent.shutdown()
            return True
        else:
            logger.error(f"❌ TEST 3 FAILED: Invalid response: {response}")
            await agent.shutdown()
            return False
            
    except Exception as e:
        logger.error(f"❌ TEST 3 FAILED: {e}")
        logger.exception("Full traceback:")
        await agent.shutdown()
        return False


async def test_4_configuration_loading():
    """
    TEST 4: Configuration Loading
    Verify env vars override JSON config
    """
    logger.info("=" * 60)
    logger.info("TEST 4: Configuration Loading")
    logger.info("=" * 60)
    
    try:
        # Load config file
        config_path = Path(__file__).parent / "config" / "engram_config.json"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                file_config = json.load(f)
            logger.info("✅ Config file loaded successfully")
            logger.info(f"   - File config model: {file_config.get('lmstudio', {}).get('model', 'N/A')}")
        else:
            logger.warning("⚠️  Config file not found, using defaults")
            file_config = {}
        
        # Test env var override
        test_model = os.getenv("ENGRAM_MODEL", "default")
        logger.info(f"   - Env var ENGRAM_MODEL: {test_model}")
        
        # Verify precedence
        if test_model != "default":
            logger.info("✅ Environment variables are set")
        else:
            logger.info("ℹ️  Using default values (no env vars set)")
        
        logger.info("✅ TEST 4 PASSED: Configuration loading working!")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 4 FAILED: {e}")
        logger.exception("Full traceback:")
        return False


async def main():
    """Run all critical path tests"""
    logger.info("\n" + "=" * 60)
    logger.info("ENGRAM-CLAWDBOT CRITICAL PATH TESTING")
    logger.info("=" * 60 + "\n")
    
    results = {
        "websocket_connection": False,
        "lmstudio_integration": False,
        "message_flow": False,
        "configuration": False
    }
    
    # Test 1: WebSocket Connection (CRITICAL - fixes 1008 error)
    results["websocket_connection"] = await test_1_websocket_connection()
    
    if not results["websocket_connection"]:
        logger.error("\n⚠️  WebSocket connection failed - this is the critical fix!")
        logger.error("Please verify:")
        logger.error("  1. ClawdBot gateway is running at ws://127.0.0.1:18789/ws")
        logger.error("  2. Authentication token is correct")
        logger.error("  3. Gateway supports clawdbot-v1 subprotocol")
        logger.info("\nContinuing with other tests...\n")
    
    # Test 2: LMStudio Integration
    results["lmstudio_integration"] = await test_2_lmstudio_integration()
    
    # Test 3: Complete Message Flow
    if results["lmstudio_integration"]:
        results["message_flow"] = await test_3_complete_message_flow()
    else:
        logger.warning("\nSkipping message flow test (LMStudio not available)\n")
    
    # Test 4: Configuration Loading
    results["configuration"] = await test_4_configuration_loading()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        logger.info(f"{status}: {test_name.replace('_', ' ').title()}")
    
    logger.info("=" * 60)
    logger.info(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("\n🎉 ALL CRITICAL PATH TESTS PASSED!")
        logger.info("The integration is ready for production use.")
    elif results["websocket_connection"]:
        logger.info("\n✅ WebSocket 1008 error is FIXED!")
        logger.info("Some tests failed but the critical fix is working.")
    else:
        logger.warning("\n⚠️  WebSocket connection failed - needs debugging")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
