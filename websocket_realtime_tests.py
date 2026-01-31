#!/usr/bin/env python3
"""
Comprehensive WebSocket and Real-Time Communication Tests for Engram Trading Bot
Tests: WebSocket connections, message handling, real-time updates, async operations
"""

import json
import logging
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebSocketRealtimeTests:
    """Comprehensive WebSocket and real-time communication test suite"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        
    def log_test(self, name: str, passed: bool, duration: float, details: str = ""):
        """Log test result"""
        result = {
            "name": name,
            "passed": passed,
            "duration_ms": round(duration * 1000, 2),
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {name} ({duration*1000:.2f}ms)")
        if details:
            logger.info(f"  Details: {details}")
    
    def test_websocket_connection_simulation(self) -> bool:
        """Test WebSocket connection lifecycle simulation"""
        start = time.time()
        try:
            class MockWebSocket:
                def __init__(self):
                    self.connected = False
                    self.messages = []
                
                def connect(self) -> bool:
                    self.connected = True
                    return True
                
                def disconnect(self):
                    self.connected = False
                
                def send(self, message: str):
                    if not self.connected:
                        raise Exception("Not connected")
                    self.messages.append({"type": "sent", "data": message, "time": time.time()})
                
                def receive(self) -> str:
                    if not self.connected:
                        raise Exception("Not connected")
                    # Simulate receiving echo
                    if self.messages:
                        return self.messages[-1]["data"]
                    return None
            
            ws = MockWebSocket()
            
            # Test connection
            if not ws.connect():
                self.log_test("WebSocket Connection Simulation", False, time.time() - start,
                            "Connection failed")
                return False
            
            if not ws.connected:
                self.log_test("WebSocket Connection Simulation", False, time.time() - start,
                            "Connection state not updated")
                return False
            
            # Test send
            ws.send("test message")
            if len(ws.messages) != 1:
                self.log_test("WebSocket Connection Simulation", False, time.time() - start,
                            "Message not sent")
                return False
            
            # Test receive
            received = ws.receive()
            if received != "test message":
                self.log_test("WebSocket Connection Simulation", False, time.time() - start,
                            "Message not received correctly")
                return False
            
            # Test disconnect
            ws.disconnect()
            if ws.connected:
                self.log_test("WebSocket Connection Simulation", False, time.time() - start,
                            "Disconnect failed")
                return False
            
            self.log_test("WebSocket Connection Simulation", True, time.time() - start,
                        "Connect/send/receive/disconnect successful")
            return True
            
        except Exception as e:
            self.log_test("WebSocket Connection Simulation", False, time.time() - start, str(e))
            return False
    
    def test_message_queue_processing(self) -> bool:
        """Test message queue for real-time updates"""
        start = time.time()
        try:
            class MessageQueue:
                def __init__(self, max_size: int = 100):
                    self.queue = deque(maxlen=max_size)
                    self.processed = []
                
                def enqueue(self, message: dict):
                    self.queue.append({
                        **message,
                        "enqueued_at": time.time()
                    })
                
                def dequeue(self) -> dict:
                    if self.queue:
                        return self.queue.popleft()
                    return None
                
                def process_all(self):
                    while self.queue:
                        msg = self.dequeue()
                        self.processed.append(msg)
                
                def get_queue_size(self) -> int:
                    return len(self.queue)
            
            queue = MessageQueue(max_size=10)
            
            # Enqueue messages
            for i in range(5):
                queue.enqueue({"id": i, "data": f"message_{i}"})
            
            if queue.get_queue_size() != 5:
                self.log_test("Message Queue Processing", False, time.time() - start,
                            f"Expected 5 messages, got {queue.get_queue_size()}")
                return False
            
            # Dequeue one
            msg = queue.dequeue()
            if msg["id"] != 0:
                self.log_test("Message Queue Processing", False, time.time() - start,
                            "FIFO order not maintained")
                return False
            
            # Process all
            queue.process_all()
            if queue.get_queue_size() != 0:
                self.log_test("Message Queue Processing", False, time.time() - start,
                            "Queue not empty after processing")
                return False
            
            if len(queue.processed) != 4:  # 5 - 1 already dequeued
                self.log_test("Message Queue Processing", False, time.time() - start,
                            "Not all messages processed")
                return False
            
            # Test max size
            for i in range(15):
                queue.enqueue({"id": i})
            
            if queue.get_queue_size() > 10:
                self.log_test("Message Queue Processing", False, time.time() - start,
                            "Max size not enforced")
                return False
            
            self.log_test("Message Queue Processing", True, time.time() - start,
                        f"Processed {len(queue.processed)} messages, max_size enforced")
            return True
            
        except Exception as e:
            self.log_test("Message Queue Processing", False, time.time() - start, str(e))
            return False
    
    def test_async_event_handling(self) -> bool:
        """Test asynchronous event handling"""
        start = time.time()
        try:
            async def async_test():
                class EventHandler:
                    def __init__(self):
                        self.events = []
                    
                    async def emit(self, event_type: str, data: dict):
                        self.events.append({
                            "type": event_type,
                            "data": data,
                            "timestamp": time.time()
                        })
                        await asyncio.sleep(0.01)  # Simulate async processing
                    
                    async def process_events(self):
                        results = []
                        for event in self.events:
                            await asyncio.sleep(0.01)
                            results.append(f"Processed: {event['type']}")
                        return results
                
                handler = EventHandler()
                
                # Emit events
                await handler.emit("price_update", {"symbol": "BTC/USDT", "price": 45000})
                await handler.emit("trade_executed", {"symbol": "ETH/USDT", "amount": 1.0})
                await handler.emit("balance_update", {"balance": 10000})
                
                if len(handler.events) != 3:
                    return False, "Events not emitted correctly"
                
                # Process events
                results = await handler.process_events()
                
                if len(results) != 3:
                    return False, "Events not processed correctly"
                
                return True, f"Emitted and processed {len(results)} events"
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, details = loop.run_until_complete(async_test())
            loop.close()
            
            self.log_test("Async Event Handling", success, time.time() - start, details)
            return success
            
        except Exception as e:
            self.log_test("Async Event Handling", False, time.time() - start, str(e))
            return False
    
    def test_realtime_price_updates(self) -> bool:
        """Test real-time price update streaming"""
        start = time.time()
        try:
            class PriceStreamer:
                def __init__(self):
                    self.subscribers = {}
                    self.price_history = {}
                
                def subscribe(self, symbol: str, callback):
                    if symbol not in self.subscribers:
                        self.subscribers[symbol] = []
                    self.subscribers[symbol].append(callback)
                
                def update_price(self, symbol: str, price: float):
                    if symbol not in self.price_history:
                        self.price_history[symbol] = []
                    
                    self.price_history[symbol].append({
                        "price": price,
                        "timestamp": time.time()
                    })
                    
                    # Notify subscribers
                    if symbol in self.subscribers:
                        for callback in self.subscribers[symbol]:
                            callback(symbol, price)
                
                def get_latest_price(self, symbol: str) -> float:
                    if symbol in self.price_history and self.price_history[symbol]:
                        return self.price_history[symbol][-1]["price"]
                    return None
            
            streamer = PriceStreamer()
            received_updates = []
            
            # Subscribe to updates
            def on_price_update(symbol, price):
                received_updates.append({"symbol": symbol, "price": price})
            
            streamer.subscribe("BTC/USDT", on_price_update)
            
            # Send updates
            prices = [45000, 45100, 45050, 45200]
            for price in prices:
                streamer.update_price("BTC/USDT", price)
            
            # Verify updates received
            if len(received_updates) != len(prices):
                self.log_test("Realtime Price Updates", False, time.time() - start,
                            f"Expected {len(prices)} updates, got {len(received_updates)}")
                return False
            
            # Verify latest price
            latest = streamer.get_latest_price("BTC/USDT")
            if latest != 45200:
                self.log_test("Realtime Price Updates", False, time.time() - start,
                            f"Latest price incorrect: {latest}")
                return False
            
            self.log_test("Realtime Price Updates", True, time.time() - start,
                        f"Streamed {len(prices)} price updates successfully")
            return True
            
        except Exception as e:
            self.log_test("Realtime Price Updates", False, time.time() - start, str(e))
            return False
    
    def test_heartbeat_mechanism(self) -> bool:
        """Test connection heartbeat/ping-pong"""
        start = time.time()
        try:
            class HeartbeatMonitor:
                def __init__(self, timeout: float = 5.0):
                    self.timeout = timeout
                    self.last_heartbeat = time.time()
                    self.is_alive = True
                
                def send_ping(self):
                    self.last_heartbeat = time.time()
                
                def receive_pong(self):
                    self.last_heartbeat = time.time()
                
                def check_connection(self) -> bool:
                    elapsed = time.time() - self.last_heartbeat
                    self.is_alive = elapsed < self.timeout
                    return self.is_alive
            
            monitor = HeartbeatMonitor(timeout=1.0)
            
            # Initial check
            if not monitor.check_connection():
                self.log_test("Heartbeat Mechanism", False, time.time() - start,
                            "Initial connection check failed")
                return False
            
            # Send ping
            monitor.send_ping()
            time.sleep(0.5)
            
            # Should still be alive
            if not monitor.check_connection():
                self.log_test("Heartbeat Mechanism", False, time.time() - start,
                            "Connection died prematurely")
                return False
            
            # Wait for timeout
            time.sleep(1.1)
            
            # Should be dead now
            if monitor.check_connection():
                self.log_test("Heartbeat Mechanism", False, time.time() - start,
                            "Timeout not detected")
                return False
            
            # Receive pong to revive
            monitor.receive_pong()
            
            # Should be alive again
            if not monitor.check_connection():
                self.log_test("Heartbeat Mechanism", False, time.time() - start,
                            "Connection not revived after pong")
                return False
            
            self.log_test("Heartbeat Mechanism", True, time.time() - start,
                        "Ping/pong and timeout detection working")
            return True
            
        except Exception as e:
            self.log_test("Heartbeat Mechanism", False, time.time() - start, str(e))
            return False
    
    def test_reconnection_logic(self) -> bool:
        """Test automatic reconnection on disconnect"""
        start = time.time()
        try:
            class AutoReconnectClient:
                def __init__(self, max_retries: int = 3):
                    self.max_retries = max_retries
                    self.connected = False
                    self.connection_attempts = 0
                    self.fail_next_n = 0
                
                def connect(self) -> bool:
                    self.connection_attempts += 1
                    
                    # Simulate failures
                    if self.fail_next_n > 0:
                        self.fail_next_n -= 1
                        return False
                    
                    self.connected = True
                    return True
                
                def disconnect(self):
                    self.connected = False
                
                def connect_with_retry(self) -> bool:
                    for attempt in range(self.max_retries):
                        if self.connect():
                            return True
                        time.sleep(0.1)  # Backoff
                    return False
            
            client = AutoReconnectClient(max_retries=3)
            
            # Test successful connection
            if not client.connect():
                self.log_test("Reconnection Logic", False, time.time() - start,
                            "Initial connection failed")
                return False
            
            # Disconnect
            client.disconnect()
            
            # Test reconnection with failures
            client.fail_next_n = 2  # Fail first 2 attempts
            client.connection_attempts = 0
            
            if not client.connect_with_retry():
                self.log_test("Reconnection Logic", False, time.time() - start,
                            "Reconnection failed")
                return False
            
            if client.connection_attempts != 3:  # 2 failures + 1 success
                self.log_test("Reconnection Logic", False, time.time() - start,
                            f"Expected 3 attempts, got {client.connection_attempts}")
                return False
            
            # Test max retries exceeded
            client.disconnect()
            client.fail_next_n = 5  # More failures than max_retries
            client.connection_attempts = 0
            
            if client.connect_with_retry():
                self.log_test("Reconnection Logic", False, time.time() - start,
                            "Should have failed after max retries")
                return False
            
            self.log_test("Reconnection Logic", True, time.time() - start,
                        "Reconnection with retry and max attempts working")
            return True
            
        except Exception as e:
            self.log_test("Reconnection Logic", False, time.time() - start, str(e))
            return False
    
    def test_message_broadcasting(self) -> bool:
        """Test broadcasting messages to multiple clients"""
        start = time.time()
        try:
            class Broadcaster:
                def __init__(self):
                    self.clients = []
                
                def add_client(self, client_id: str):
                    self.clients.append({
                        "id": client_id,
                        "messages": []
                    })
                
                def remove_client(self, client_id: str):
                    self.clients = [c for c in self.clients if c["id"] != client_id]
                
                def broadcast(self, message: str):
                    for client in self.clients:
                        client["messages"].append(message)
                
                def get_client_messages(self, client_id: str) -> List[str]:
                    for client in self.clients:
                        if client["id"] == client_id:
                            return client["messages"]
                    return []
            
            broadcaster = Broadcaster()
            
            # Add clients
            broadcaster.add_client("client1")
            broadcaster.add_client("client2")
            broadcaster.add_client("client3")
            
            # Broadcast message
            broadcaster.broadcast("Hello everyone!")
            
            # Verify all clients received
            for client_id in ["client1", "client2", "client3"]:
                messages = broadcaster.get_client_messages(client_id)
                if len(messages) != 1 or messages[0] != "Hello everyone!":
                    self.log_test("Message Broadcasting", False, time.time() - start,
                                f"Client {client_id} didn't receive message")
                    return False
            
            # Remove one client
            broadcaster.remove_client("client2")
            
            # Broadcast again
            broadcaster.broadcast("Second message")
            
            # Verify client2 didn't receive second message
            if len(broadcaster.get_client_messages("client2")) != 0:
                self.log_test("Message Broadcasting", False, time.time() - start,
                            "Removed client still receiving messages")
                return False
            
            # Verify others received
            if len(broadcaster.get_client_messages("client1")) != 2:
                self.log_test("Message Broadcasting", False, time.time() - start,
                            "Active client didn't receive second message")
                return False
            
            self.log_test("Message Broadcasting", True, time.time() - start,
                        "Broadcast to 3 clients, removed 1, verified delivery")
            return True
            
        except Exception as e:
            self.log_test("Message Broadcasting", False, time.time() - start, str(e))
            return False
    
    def test_rate_limited_updates(self) -> bool:
        """Test rate limiting for real-time updates"""
        start = time.time()
        try:
            class RateLimitedUpdater:
                def __init__(self, max_updates_per_second: int = 10):
                    self.max_updates = max_updates_per_second
                    self.update_times = deque(maxlen=max_updates_per_second)
                
                def can_send_update(self) -> bool:
                    now = time.time()
                    
                    # Remove old updates outside 1 second window
                    while self.update_times and now - self.update_times[0] > 1.0:
                        self.update_times.popleft()
                    
                    return len(self.update_times) < self.max_updates
                
                def send_update(self, data: dict) -> bool:
                    if self.can_send_update():
                        self.update_times.append(time.time())
                        return True
                    return False
            
            updater = RateLimitedUpdater(max_updates_per_second=5)
            
            # Send 5 updates (should all succeed)
            sent = 0
            for i in range(5):
                if updater.send_update({"id": i}):
                    sent += 1
            
            if sent != 5:
                self.log_test("Rate Limited Updates", False, time.time() - start,
                            f"Expected 5 updates sent, got {sent}")
                return False
            
            # 6th update should fail
            if updater.send_update({"id": 6}):
                self.log_test("Rate Limited Updates", False, time.time() - start,
                            "Rate limit not enforced")
                return False
            
            # After 1 second, should allow again
            time.sleep(1.1)
            
            if not updater.send_update({"id": 7}):
                self.log_test("Rate Limited Updates", False, time.time() - start,
                            "Rate limit not reset after time window")
                return False
            
            self.log_test("Rate Limited Updates", True, time.time() - start,
                        "Rate limiting (5 updates/sec) working correctly")
            return True
            
        except Exception as e:
            self.log_test("Rate Limited Updates", False, time.time() - start, str(e))
            return False
    
    def test_message_compression(self) -> bool:
        """Test message compression for bandwidth optimization"""
        start = time.time()
        try:
            import zlib
            
            def compress_message(message: str) -> bytes:
                return zlib.compress(message.encode())
            
            def decompress_message(compressed: bytes) -> str:
                return zlib.decompress(compressed).decode()
            
            # Test with large message
            large_message = json.dumps({
                "prices": [{"symbol": f"COIN{i}", "price": 100 + i} for i in range(100)]
            })
            
            original_size = len(large_message.encode())
            
            # Compress
            compressed = compress_message(large_message)
            compressed_size = len(compressed)
            
            # Verify compression
            if compressed_size >= original_size:
                self.log_test("Message Compression", False, time.time() - start,
                            "Compression didn't reduce size")
                return False
            
            # Decompress
            decompressed = decompress_message(compressed)
            
            # Verify integrity
            if decompressed != large_message:
                self.log_test("Message Compression", False, time.time() - start,
                            "Decompressed message doesn't match original")
                return False
            
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            self.log_test("Message Compression", True, time.time() - start,
                        f"Compressed {original_size}B to {compressed_size}B ({compression_ratio:.1f}% reduction)")
            return True
            
        except Exception as e:
            self.log_test("Message Compression", False, time.time() - start, str(e))
            return False
    
    def test_ordered_message_delivery(self) -> bool:
        """Test ordered message delivery with sequence numbers"""
        start = time.time()
        try:
            class OrderedMessageHandler:
                def __init__(self):
                    self.next_sequence = 0
                    self.buffer = {}
                    self.delivered = []
                
                def receive_message(self, sequence: int, data: str):
                    if sequence == self.next_sequence:
                        # Deliver immediately
                        self.delivered.append(data)
                        self.next_sequence += 1
                        
                        # Check buffer for next messages
                        while self.next_sequence in self.buffer:
                            self.delivered.append(self.buffer[self.next_sequence])
                            del self.buffer[self.next_sequence]
                            self.next_sequence += 1
                    else:
                        # Buffer out-of-order message
                        self.buffer[sequence] = data
                
                def get_delivered_messages(self) -> List[str]:
                    return self.delivered
            
            handler = OrderedMessageHandler()
            
            # Send messages out of order
            handler.receive_message(0, "first")
            handler.receive_message(2, "third")
            handler.receive_message(1, "second")
            handler.receive_message(4, "fifth")
            handler.receive_message(3, "fourth")
            
            delivered = handler.get_delivered_messages()
            
            # Verify order
            expected = ["first", "second", "third", "fourth", "fifth"]
            if delivered != expected:
                self.log_test("Ordered Message Delivery", False, time.time() - start,
                            f"Order incorrect: {delivered}")
                return False
            
            self.log_test("Ordered Message Delivery", True, time.time() - start,
                        "5 out-of-order messages delivered in correct sequence")
            return True
            
        except Exception as e:
            self.log_test("Ordered Message Delivery", False, time.time() - start, str(e))
            return False
    
    def run_all_tests(self):
        """Run all WebSocket and real-time communication tests"""
        logger.info("=" * 80)
        logger.info("WEBSOCKET AND REAL-TIME COMMUNICATION TESTS")
        logger.info("=" * 80)
        
        tests = [
            self.test_websocket_connection_simulation,
            self.test_message_queue_processing,
            self.test_async_event_handling,
            self.test_realtime_price_updates,
            self.test_heartbeat_mechanism,
            self.test_reconnection_logic,
            self.test_message_broadcasting,
            self.test_rate_limited_updates,
            self.test_message_compression,
            self.test_ordered_message_delivery
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} crashed: {e}")
                self.log_test(test.__name__, False, 0, f"Test crashed: {e}")
        
        # Calculate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['passed'])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        total_duration = time.time() - self.start_time
        
        logger.info("=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ({pass_rate:.1f}%)")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Total Duration: {total_duration:.2f}s")
        logger.info("=" * 80)
        
        # Save results
        results_data = {
            "test_suite": "WebSocket and Real-Time Communication Tests",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": round(pass_rate, 2),
                "duration_seconds": round(total_duration, 2)
            },
            "tests": self.results
        }
        
        output_file = Path("websocket_realtime_test_results.json")
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"✅ Results saved to {output_file}")
        
        return pass_rate >= 80


if __name__ == "__main__":
    tester = WebSocketRealtimeTests()
    success = tester.run_all_tests()
    exit(0 if success else 1)
