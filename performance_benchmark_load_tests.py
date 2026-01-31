#!/usr/bin/env python3
"""
Comprehensive Performance Benchmarking and Load Tests
Tests: Throughput, latency, memory usage, CPU usage, scalability
"""

import json
import logging
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import deque
import gc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceBenchmarkLoadTests:
    """Comprehensive performance benchmarking and load test suite"""
    
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
    
    def test_throughput_benchmark(self) -> bool:
        """Test message processing throughput"""
        start = time.time()
        try:
            class MessageProcessor:
                def __init__(self):
                    self.processed_count = 0
                
                def process_message(self, message: dict):
                    # Simulate processing
                    _ = json.dumps(message)
                    self.processed_count += 1
            
            processor = MessageProcessor()
            num_messages = 10000
            
            # Process messages
            process_start = time.time()
            for i in range(num_messages):
                processor.process_message({
                    "id": i,
                    "type": "trade",
                    "data": {"symbol": "BTC/USDT", "price": 45000 + i}
                })
            process_duration = time.time() - process_start
            
            # Calculate throughput
            throughput = num_messages / process_duration
            
            if processor.processed_count != num_messages:
                self.log_test("Throughput Benchmark", False, time.time() - start,
                            f"Processed {processor.processed_count}/{num_messages}")
                return False
            
            # Expect at least 1000 messages/second
            if throughput < 1000:
                self.log_test("Throughput Benchmark", False, time.time() - start,
                            f"Throughput too low: {throughput:.0f} msg/s")
                return False
            
            self.log_test("Throughput Benchmark", True, time.time() - start,
                        f"Processed {num_messages} messages at {throughput:.0f} msg/s")
            return True
            
        except Exception as e:
            self.log_test("Throughput Benchmark", False, time.time() - start, str(e))
            return False
    
    def test_latency_measurement(self) -> bool:
        """Test request/response latency"""
        start = time.time()
        try:
            class LatencyTracker:
                def __init__(self):
                    self.latencies = []
                
                def measure_request(self, request_func):
                    req_start = time.time()
                    request_func()
                    latency = (time.time() - req_start) * 1000  # ms
                    self.latencies.append(latency)
                
                def get_stats(self) -> dict:
                    if not self.latencies:
                        return {}
                    
                    sorted_latencies = sorted(self.latencies)
                    return {
                        'min': min(self.latencies),
                        'max': max(self.latencies),
                        'avg': sum(self.latencies) / len(self.latencies),
                        'p50': sorted_latencies[len(sorted_latencies) // 2],
                        'p95': sorted_latencies[int(len(sorted_latencies) * 0.95)],
                        'p99': sorted_latencies[int(len(sorted_latencies) * 0.99)]
                    }
            
            tracker = LatencyTracker()
            
            # Simulate requests
            def mock_request():
                time.sleep(0.001)  # 1ms processing
            
            for _ in range(100):
                tracker.measure_request(mock_request)
            
            stats = tracker.get_stats()
            
            # Verify measurements
            if stats['avg'] > 10:  # Should be around 1ms
                self.log_test("Latency Measurement", False, time.time() - start,
                            f"Average latency too high: {stats['avg']:.2f}ms")
                return False
            
            if stats['p99'] > 20:
                self.log_test("Latency Measurement", False, time.time() - start,
                            f"P99 latency too high: {stats['p99']:.2f}ms")
                return False
            
            self.log_test("Latency Measurement", True, time.time() - start,
                        f"Avg: {stats['avg']:.2f}ms, P95: {stats['p95']:.2f}ms, P99: {stats['p99']:.2f}ms")
            return True
            
        except Exception as e:
            self.log_test("Latency Measurement", False, time.time() - start, str(e))
            return False
    
    def test_memory_usage_tracking(self) -> bool:
        """Test memory usage and leak detection"""
        start = time.time()
        try:
            import sys
            
            class MemoryTracker:
                def __init__(self):
                    self.snapshots = []
                
                def take_snapshot(self):
                    gc.collect()
                    # Approximate memory usage
                    objects = gc.get_objects()
                    self.snapshots.append(len(objects))
                
                def get_growth(self) -> int:
                    if len(self.snapshots) < 2:
                        return 0
                    return self.snapshots[-1] - self.snapshots[0]
            
            tracker = MemoryTracker()
            
            # Initial snapshot
            tracker.take_snapshot()
            
            # Allocate and deallocate memory
            data = []
            for i in range(1000):
                data.append({"id": i, "data": "x" * 100})
            
            tracker.take_snapshot()
            
            # Clear data
            data.clear()
            gc.collect()
            
            tracker.take_snapshot()
            
            # Check for memory leak
            growth = tracker.get_growth()
            
            # Some growth is expected, but should be minimal after cleanup
            if growth > 10000:
                self.log_test("Memory Usage Tracking", False, time.time() - start,
                            f"Possible memory leak: {growth} objects")
                return False
            
            self.log_test("Memory Usage Tracking", True, time.time() - start,
                        f"Memory growth: {growth} objects (acceptable)")
            return True
            
        except Exception as e:
            self.log_test("Memory Usage Tracking", False, time.time() - start, str(e))
            return False
    
    def test_concurrent_load(self) -> bool:
        """Test system under concurrent load"""
        start = time.time()
        try:
            class ConcurrentProcessor:
                def __init__(self):
                    self.processed = []
                    self.lock = threading.Lock()
                    self.errors = []
                
                def process(self, task_id: int):
                    try:
                        # Simulate work
                        time.sleep(0.01)
                        with self.lock:
                            self.processed.append(task_id)
                    except Exception as e:
                        with self.lock:
                            self.errors.append(str(e))
            
            processor = ConcurrentProcessor()
            num_threads = 10
            tasks_per_thread = 10
            
            # Create threads
            threads = []
            for i in range(num_threads):
                for j in range(tasks_per_thread):
                    t = threading.Thread(target=processor.process, args=(i * tasks_per_thread + j,))
                    threads.append(t)
                    t.start()
            
            # Wait for completion
            for t in threads:
                t.join()
            
            # Verify results
            if processor.errors:
                self.log_test("Concurrent Load", False, time.time() - start,
                            f"Errors occurred: {processor.errors[0]}")
                return False
            
            expected_count = num_threads * tasks_per_thread
            if len(processor.processed) != expected_count:
                self.log_test("Concurrent Load", False, time.time() - start,
                            f"Processed {len(processor.processed)}/{expected_count}")
                return False
            
            self.log_test("Concurrent Load", True, time.time() - start,
                        f"{num_threads} threads, {expected_count} tasks completed")
            return True
            
        except Exception as e:
            self.log_test("Concurrent Load", False, time.time() - start, str(e))
            return False
    
    def test_cache_performance(self) -> bool:
        """Test cache hit/miss performance"""
        start = time.time()
        try:
            class PerformanceCache:
                def __init__(self, max_size: int = 100):
                    self.cache = {}
                    self.max_size = max_size
                    self.hits = 0
                    self.misses = 0
                
                def get(self, key: str) -> Any:
                    if key in self.cache:
                        self.hits += 1
                        return self.cache[key]
                    self.misses += 1
                    return None
                
                def set(self, key: str, value: Any):
                    if len(self.cache) >= self.max_size:
                        # Simple eviction: remove first item
                        self.cache.pop(next(iter(self.cache)))
                    self.cache[key] = value
                
                def get_hit_rate(self) -> float:
                    total = self.hits + self.misses
                    return (self.hits / total * 100) if total > 0 else 0
            
            cache = PerformanceCache(max_size=50)
            
            # Populate cache
            for i in range(50):
                cache.set(f"key_{i}", f"value_{i}")
            
            # Test cache hits
            for i in range(50):
                cache.get(f"key_{i}")
            
            # Test cache misses
            for i in range(50, 100):
                cache.get(f"key_{i}")
            
            hit_rate = cache.get_hit_rate()
            
            # Should have 50% hit rate
            if hit_rate < 45 or hit_rate > 55:
                self.log_test("Cache Performance", False, time.time() - start,
                            f"Unexpected hit rate: {hit_rate:.1f}%")
                return False
            
            self.log_test("Cache Performance", True, time.time() - start,
                        f"Hit rate: {hit_rate:.1f}% ({cache.hits} hits, {cache.misses} misses)")
            return True
            
        except Exception as e:
            self.log_test("Cache Performance", False, time.time() - start, str(e))
            return False
    
    def test_batch_processing_efficiency(self) -> bool:
        """Test batch processing vs individual processing"""
        start = time.time()
        try:
            def process_individual(items: List[dict]) -> float:
                """Process items one by one"""
                start_time = time.time()
                results = []
                for item in items:
                    results.append(json.dumps(item))
                return time.time() - start_time
            
            def process_batch(items: List[dict]) -> float:
                """Process items in batch"""
                start_time = time.time()
                results = json.dumps(items)
                return time.time() - start_time
            
            # Generate test data
            items = [{"id": i, "data": f"item_{i}"} for i in range(1000)]
            
            # Test individual processing
            individual_time = process_individual(items)
            
            # Test batch processing
            batch_time = process_batch(items)
            
            # Batch should be faster
            if batch_time >= individual_time:
                self.log_test("Batch Processing Efficiency", False, time.time() - start,
                            f"Batch not faster: {batch_time:.3f}s vs {individual_time:.3f}s")
                return False
            
            speedup = individual_time / batch_time
            
            self.log_test("Batch Processing Efficiency", True, time.time() - start,
                        f"Batch {speedup:.1f}x faster ({batch_time:.3f}s vs {individual_time:.3f}s)")
            return True
            
        except Exception as e:
            self.log_test("Batch Processing Efficiency", False, time.time() - start, str(e))
            return False
    
    def test_queue_performance(self) -> bool:
        """Test queue operations performance"""
        start = time.time()
        try:
            from collections import deque
            
            # Test deque performance
            queue = deque()
            num_operations = 10000
            
            # Enqueue
            enqueue_start = time.time()
            for i in range(num_operations):
                queue.append(i)
            enqueue_time = time.time() - enqueue_start
            
            # Dequeue
            dequeue_start = time.time()
            while queue:
                queue.popleft()
            dequeue_time = time.time() - dequeue_start
            
            # Calculate ops/sec
            enqueue_ops = num_operations / enqueue_time
            dequeue_ops = num_operations / dequeue_time
            
            # Should be very fast (>100k ops/sec)
            if enqueue_ops < 100000 or dequeue_ops < 100000:
                self.log_test("Queue Performance", False, time.time() - start,
                            f"Queue too slow: {enqueue_ops:.0f} enq/s, {dequeue_ops:.0f} deq/s")
                return False
            
            self.log_test("Queue Performance", True, time.time() - start,
                        f"Enqueue: {enqueue_ops:.0f} ops/s, Dequeue: {dequeue_ops:.0f} ops/s")
            return True
            
        except Exception as e:
            self.log_test("Queue Performance", False, time.time() - start, str(e))
            return False
    
    def test_json_serialization_performance(self) -> bool:
        """Test JSON serialization/deserialization performance"""
        start = time.time()
        try:
            # Generate test data
            data = {
                "trades": [
                    {
                        "id": i,
                        "symbol": f"COIN{i % 10}/USDT",
                        "price": 100 + i * 0.1,
                        "amount": 1.0 + i * 0.01,
                        "timestamp": datetime.now().isoformat()
                    }
                    for i in range(1000)
                ]
            }
            
            num_iterations = 100
            
            # Test serialization
            serialize_start = time.time()
            for _ in range(num_iterations):
                json_str = json.dumps(data)
            serialize_time = time.time() - serialize_start
            
            # Test deserialization
            deserialize_start = time.time()
            for _ in range(num_iterations):
                loaded_data = json.loads(json_str)
            deserialize_time = time.time() - deserialize_start
            
            # Calculate ops/sec
            serialize_ops = num_iterations / serialize_time
            deserialize_ops = num_iterations / deserialize_time
            
            # Should be reasonably fast (>10 ops/sec)
            if serialize_ops < 10 or deserialize_ops < 10:
                self.log_test("JSON Serialization Performance", False, time.time() - start,
                            f"Too slow: {serialize_ops:.0f} ser/s, {deserialize_ops:.0f} deser/s")
                return False
            
            self.log_test("JSON Serialization Performance", True, time.time() - start,
                        f"Serialize: {serialize_ops:.0f} ops/s, Deserialize: {deserialize_ops:.0f} ops/s")
            return True
            
        except Exception as e:
            self.log_test("JSON Serialization Performance", False, time.time() - start, str(e))
            return False
    
    def test_stress_test_sustained_load(self) -> bool:
        """Test system under sustained load"""
        start = time.time()
        try:
            class LoadGenerator:
                def __init__(self):
                    self.processed = 0
                    self.errors = 0
                    self.running = True
                
                def process_load(self, duration: float):
                    end_time = time.time() + duration
                    while time.time() < end_time and self.running:
                        try:
                            # Simulate work
                            _ = json.dumps({"id": self.processed, "data": "test"})
                            self.processed += 1
                        except Exception:
                            self.errors += 1
                
                def stop(self):
                    self.running = False
            
            generator = LoadGenerator()
            
            # Run for 2 seconds
            generator.process_load(2.0)
            
            # Calculate throughput
            throughput = generator.processed / 2.0
            
            if generator.errors > 0:
                self.log_test("Stress Test Sustained Load", False, time.time() - start,
                            f"{generator.errors} errors occurred")
                return False
            
            # Should process at least 1000 ops/sec
            if throughput < 1000:
                self.log_test("Stress Test Sustained Load", False, time.time() - start,
                            f"Throughput too low: {throughput:.0f} ops/s")
                return False
            
            self.log_test("Stress Test Sustained Load", True, time.time() - start,
                        f"Sustained {throughput:.0f} ops/s for 2 seconds ({generator.processed} total)")
            return True
            
        except Exception as e:
            self.log_test("Stress Test Sustained Load", False, time.time() - start, str(e))
            return False
    
    def test_scalability_linear_growth(self) -> bool:
        """Test scalability with increasing load"""
        start = time.time()
        try:
            def process_batch(size: int) -> float:
                """Process a batch and return time taken"""
                start_time = time.time()
                data = [{"id": i} for i in range(size)]
                _ = json.dumps(data)
                return time.time() - start_time
            
            # Test with different batch sizes
            sizes = [100, 200, 400, 800]
            times = []
            
            for size in sizes:
                time_taken = process_batch(size)
                times.append(time_taken)
            
            # Check if growth is roughly linear
            # Time for 800 should be ~8x time for 100
            ratio = times[-1] / times[0]
            expected_ratio = sizes[-1] / sizes[0]
            
            # Allow 50% deviation from linear
            if ratio > expected_ratio * 1.5 or ratio < expected_ratio * 0.5:
                self.log_test("Scalability Linear Growth", False, time.time() - start,
                            f"Non-linear scaling: {ratio:.1f}x vs expected {expected_ratio}x")
                return False
            
            self.log_test("Scalability Linear Growth", True, time.time() - start,
                        f"Linear scaling confirmed: {ratio:.1f}x for {expected_ratio}x load")
            return True
            
        except Exception as e:
            self.log_test("Scalability Linear Growth", False, time.time() - start, str(e))
            return False
    
    def run_all_tests(self):
        """Run all performance benchmarking and load tests"""
        logger.info("=" * 80)
        logger.info("PERFORMANCE BENCHMARKING AND LOAD TESTS")
        logger.info("=" * 80)
        
        tests = [
            self.test_throughput_benchmark,
            self.test_latency_measurement,
            self.test_memory_usage_tracking,
            self.test_concurrent_load,
            self.test_cache_performance,
            self.test_batch_processing_efficiency,
            self.test_queue_performance,
            self.test_json_serialization_performance,
            self.test_stress_test_sustained_load,
            self.test_scalability_linear_growth
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
            "test_suite": "Performance Benchmarking and Load Tests",
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
        
        output_file = Path("performance_benchmark_load_test_results.json")
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"✅ Results saved to {output_file}")
        
        return pass_rate >= 80


if __name__ == "__main__":
    tester = PerformanceBenchmarkLoadTests()
    success = tester.run_all_tests()
    exit(0 if success else 1)
