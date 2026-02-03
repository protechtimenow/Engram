#!/usr/bin/env python3
"""
ClawdBot Connection Test Suite
Tests WebSocket connection, authentication, and message flow
"""

import asyncio
import json
import sys
import time
import websockets
import requests
from datetime import datetime

# Configuration
CLAWDBOT_WS_URL = "ws://127.0.0.1:18789"
CLAWDBOT_AUTH_TOKEN = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
LMSTUDIO_URL = "http://100.118.172.23:1234"

class Colors:
    OK = "\033[92m"      # Green
    WARN = "\033[93m"    # Yellow
    ERROR = "\033[91m"   # Red
    INFO = "\033[94m"    # Blue
    RESET = "\033[0m"

def print_header(text):
    print(f"\n{Colors.INFO}{'='*80}{Colors.RESET}")
    print(f"{Colors.INFO}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.INFO}{'='*80}{Colors.RESET}\n")

def print_ok(text):
    print(f"{Colors.OK}[OK]{Colors.RESET} {text}")

def print_warn(text):
    print(f"{Colors.WARN}[WARN]{Colors.RESET} {text}")

def print_error(text):
    print(f"{Colors.ERROR}[ERROR]{Colors.RESET} {text}")

def print_info(text):
    print(f"{Colors.INFO}[INFO]{Colors.RESET} {text}")

class ClawdBotTester:
    def __init__(self):
        self.websocket = None
        self.session_id = None
        self.tests_passed = 0
        self.tests_failed = 0
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print_header("CLAWDBOT GATEWAY TEST SUITE")
        print_info(f"Testing against: {CLAWDBOT_WS_URL}")
        print_info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test 1: Health Check
        await self.test_health_check()
        
        # Test 2: WebSocket Connection
        await self.test_websocket_connection()
        
        # Test 3: Authentication
        await self.test_authentication()
        
        # Test 4: Message Exchange
        await self.test_message_exchange()
        
        # Test 5: Ping/Pong
        await self.test_ping_pong()
        
        # Test 6: LMStudio Integration
        await self.test_lmstudio_integration()
        
        # Summary
        self.print_summary()
    
    async def test_health_check(self):
        """Test HTTP health endpoint"""
        print_header("TEST 1: Health Check")
        try:
            response = requests.get(f"http://127.0.0.1:18789/health", timeout=5)
            if response.status_code == 200:
                print_ok(f"Health endpoint responding (200 OK)")
                print_info(f"Response: {response.text}")
                self.tests_passed += 1
            else:
                print_warn(f"Health endpoint returned status {response.status_code}")
                self.tests_failed += 1
        except requests.exceptions.ConnectionError:
            print_error("Cannot connect to health endpoint - ClawdBot may not be running")
            self.tests_failed += 1
        except Exception as e:
            print_error(f"Health check failed: {e}")
            self.tests_failed += 1
    
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        print_header("TEST 2: WebSocket Connection")
        try:
            # Build URL with auth token
            ws_url = f"{CLAWDBOT_WS_URL}?token={CLAWDBOT_AUTH_TOKEN}"
            
            print_info(f"Connecting to {CLAWDBOT_WS_URL}...")
            self.websocket = await websockets.connect(
                ws_url,
                subprotocols=["clawdbot-v1"],
                ping_interval=30,
                ping_timeout=10
            )
            
            print_ok("WebSocket connected successfully")
            self.tests_passed += 1
            
        except websockets.exceptions.InvalidHandshake as e:
            print_error(f"WebSocket handshake failed: {e}")
            print_info("This may indicate authentication issues or incorrect subprotocol")
            self.tests_failed += 1
        except ConnectionRefusedError:
            print_error("Connection refused - ClawdBot Gateway is not running")
            print_info("Start ClawdBot with: .\\.clawdbot\\gateway.cmd")
            self.tests_failed += 1
        except Exception as e:
            print_error(f"WebSocket connection failed: {e}")
            self.tests_failed += 1
    
    async def test_authentication(self):
        """Test authentication flow"""
        print_header("TEST 3: Authentication")
        
        if not self.websocket:
            print_warn("Skipping - WebSocket not connected")
            return
        
        try:
            # Send hello message
            hello_msg = {
                "type": "hello",
                "version": "1",
                "userAgent": "ClawdBotTest/1.0"
            }
            
            print_info("Sending hello message...")
            await self.websocket.send(json.dumps(hello_msg))
            
            # Wait for response
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            if data.get("type") == "hello":
                self.session_id = data.get("sessionId")
                print_ok(f"Authentication successful")
                print_info(f"Session ID: {self.session_id}")
                self.tests_passed += 1
            else:
                print_warn(f"Unexpected response type: {data.get('type')}")
                self.tests_failed += 1
                
        except asyncio.TimeoutError:
            print_error("Timeout waiting for authentication response")
            self.tests_failed += 1
        except Exception as e:
            print_error(f"Authentication failed: {e}")
            self.tests_failed += 1
    
    async def test_message_exchange(self):
        """Test message sending and receiving"""
        print_header("TEST 4: Message Exchange")
        
        if not self.websocket or not self.session_id:
            print_warn("Skipping - Not authenticated")
            return
        
        try:
            # Send a test message
            test_msg = {
                "type": "message",
                "sessionId": self.session_id,
                "message": "Hello ClawdBot! This is a test message.",
                "thinking": "low"
            }
            
            print_info("Sending test message...")
            await self.websocket.send(json.dumps(test_msg))
            
            # Wait for response with timeout
            print_info("Waiting for response...")
            response = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
            data = json.loads(response)
            
            if data.get("type") in ["message", "chunk"]:
                content = data.get("text", data.get("content", "N/A"))
                print_ok("Message exchange successful")
                print_info(f"Response type: {data.get('type')}")
                print_info(f"Response preview: {content[:100]}...")
                self.tests_passed += 1
            else:
                print_warn(f"Unexpected response: {data}")
                self.tests_failed += 1
                
        except asyncio.TimeoutError:
            print_error("Timeout waiting for message response")
            print_info("This may indicate LMStudio is not responding")
            self.tests_failed += 1
        except Exception as e:
            print_error(f"Message exchange failed: {e}")
            self.tests_failed += 1
    
    async def test_ping_pong(self):
        """Test ping/pong keepalive"""
        print_header("TEST 5: Ping/Pong")
        
        if not self.websocket:
            print_warn("Skipping - WebSocket not connected")
            return
        
        try:
            ping_msg = {
                "type": "ping",
                "timestamp": datetime.now().isoformat()
            }
            
            print_info("Sending ping...")
            await self.websocket.send(json.dumps(ping_msg))
            
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            if data.get("type") == "pong":
                print_ok("Ping/Pong successful")
                self.tests_passed += 1
            else:
                print_warn(f"Expected pong, got: {data.get('type')}")
                self.tests_failed += 1
                
        except asyncio.TimeoutError:
            print_error("Timeout waiting for pong")
            self.tests_failed += 1
        except Exception as e:
            print_error(f"Ping/Pong failed: {e}")
            self.tests_failed += 1
    
    async def test_lmstudio_integration(self):
        """Test LMStudio connectivity"""
        print_header("TEST 6: LMStudio Integration")
        
        try:
            print_info(f"Checking LMStudio at {LMSTUDIO_URL}...")
            response = requests.get(f"{LMSTUDIO_URL}/v1/models", timeout=5)
            
            if response.status_code == 200:
                models = response.json()
                model_list = [m.get('id', 'unknown') for m in models.get('data', [])]
                print_ok("LMStudio is accessible")
                print_info(f"Available models: {', '.join(model_list)}")
                self.tests_passed += 1
            else:
                print_warn(f"LMStudio returned status {response.status_code}")
                self.tests_failed += 1
                
        except requests.exceptions.ConnectionError:
            print_error("Cannot connect to LMStudio")
            print_info(f"Ensure LMStudio is running at {LMSTUDIO_URL}")
            self.tests_failed += 1
        except Exception as e:
            print_error(f"LMStudio check failed: {e}")
            self.tests_failed += 1
    
    def print_summary(self):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        print_info(f"Tests Passed: {self.tests_passed}")
        print_info(f"Tests Failed: {self.tests_failed}")
        print_info(f"Success Rate: {pass_rate:.1f}%")
        
        if self.tests_failed == 0:
            print_ok("All tests passed! ClawdBot Gateway is fully operational.")
        elif self.tests_passed > 0:
            print_warn("Partial success - Some features may be limited")
        else:
            print_error("All tests failed - Check configuration and services")
        
        print(f"\n{Colors.INFO}{'='*80}{Colors.RESET}\n")
    
    async def cleanup(self):
        """Clean up resources"""
        if self.websocket:
            await self.websocket.close()
            print_info("WebSocket connection closed")

async def main():
    tester = ClawdBotTester()
    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print_info("\nTest interrupted by user")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    # Windows color support
    if sys.platform == 'win32':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    
    print_info("Starting ClawdBot Connection Tests...")
    print_info("Make sure ClawdBot Gateway is running on port 18789")
    print_info("Press Ctrl+C to stop\n")
    
    asyncio.run(main())
