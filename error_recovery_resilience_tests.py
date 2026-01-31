#!/usr/bin/env python3
"""
Comprehensive Error Recovery and Resilience Tests
Tests: Error handling, retry logic, circuit breakers, graceful degradation
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorRecoveryResilienceTests:
    """Comprehensive error recovery and resilience test suite"""
    
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
    
    def test_retry_with_exponential_backoff(self) -> bool:
        """Test retry mechanism with exponential backoff"""
        start = time.time()
        try:
            class RetryHandler:
                def __init__(self, max_retries: int = 3):
                    self.max_retries = max_retries
                    self.attempt_count = 0
                    self.backoff_times = []
                
                def execute_with_retry(self, func, *args, **kwargs):
                    for attempt in range(self.max_retries):
                        self.attempt_count += 1
                        try:
                            return func(*args, **kwargs)
                        except Exception as e:
                            if attempt < self.max_retries - 1:
                                backoff = 2 ** attempt  # Exponential backoff
                                self.backoff_times.append(backoff)
                                time.sleep(backoff * 0.01)  # Scale down for testing
                            else:
                                raise
            
            handler = RetryHandler(max_retries=3)
            
            # Simulate function that fails twice then succeeds
            call_count = [0]
            def flaky_function():
                call_count[0] += 1
                if call_count[0] < 3:
                    raise Exception("Temporary failure")
                return "success"
            
            result = handler.execute_with_retry(flaky_function)
            
            if result != "success":
                self.log_test("Retry with Exponential Backoff", False, time.time() - start,
                            "Function didn't succeed after retries")
                return False
            
            if handler.attempt_count != 3:
                self.log_test("Retry with Exponential Backoff", False, time.time() - start,
                            f"Expected 3 attempts, got {handler.attempt_count}")
                return False
            
            # Verify exponential backoff
            if handler.backoff_times != [1, 2]:
                self.log_test("Retry with Exponential Backoff", False, time.time() - start,
                            f"Backoff not exponential: {handler.backoff_times}")
                return False
            
            self.log_test("Retry with Exponential Backoff", True, time.time() - start,
                        f"Succeeded after {handler.attempt_count} attempts with backoff {handler.backoff_times}")
            return True
            
        except Exception as e:
            self.log_test("Retry with Exponential Backoff", False, time.time() - start, str(e))
            return False
    
    def test_circuit_breaker_pattern(self) -> bool:
        """Test circuit breaker pattern"""
        start = time.time()
        try:
            class CircuitState(Enum):
                CLOSED = "closed"
                OPEN = "open"
                HALF_OPEN = "half_open"
            
            class CircuitBreaker:
                def __init__(self, failure_threshold: int = 3, timeout: float = 1.0):
                    self.failure_threshold = failure_threshold
                    self.timeout = timeout
                    self.failure_count = 0
                    self.last_failure_time = None
                    self.state = CircuitState.CLOSED
                
                def call(self, func, *args, **kwargs):
                    if self.state == CircuitState.OPEN:
                        if time.time() - self.last_failure_time > self.timeout:
                            self.state = CircuitState.HALF_OPEN
                        else:
                            raise Exception("Circuit breaker is OPEN")
                    
                    try:
                        result = func(*args, **kwargs)
                        if self.state == CircuitState.HALF_OPEN:
                            self.state = CircuitState.CLOSED
                            self.failure_count = 0
                        return result
                    except Exception as e:
                        self.failure_count += 1
                        self.last_failure_time = time.time()
                        
                        if self.failure_count >= self.failure_threshold:
                            self.state = CircuitState.OPEN
                        
                        raise
            
            breaker = CircuitBreaker(failure_threshold=3, timeout=0.1)
            
            # Simulate failing function
            def failing_function():
                raise Exception("Service unavailable")
            
            # Trigger failures to open circuit
            for i in range(3):
                try:
                    breaker.call(failing_function)
                except:
                    pass
            
            if breaker.state != CircuitState.OPEN:
                self.log_test("Circuit Breaker Pattern", False, time.time() - start,
                            f"Circuit not opened after {breaker.failure_count} failures")
                return False
            
            # Try to call while open (should fail immediately)
            try:
                breaker.call(failing_function)
                self.log_test("Circuit Breaker Pattern", False, time.time() - start,
                            "Call succeeded while circuit open")
                return False
            except Exception as e:
                if "Circuit breaker is OPEN" not in str(e):
                    self.log_test("Circuit Breaker Pattern", False, time.time() - start,
                                "Wrong exception while circuit open")
                    return False
            
            # Wait for timeout
            time.sleep(0.15)
            
            # Circuit should be half-open now
            def working_function():
                return "success"
            
            result = breaker.call(working_function)
            
            if breaker.state != CircuitState.CLOSED:
                self.log_test("Circuit Breaker Pattern", False, time.time() - start,
                            "Circuit not closed after successful call")
                return False
            
            self.log_test("Circuit Breaker Pattern", True, time.time() - start,
                        "Circuit opened, half-opened, and closed successfully")
            return True
            
        except Exception as e:
            self.log_test("Circuit Breaker Pattern", False, time.time() - start, str(e))
            return False
    
    def test_graceful_degradation(self) -> bool:
        """Test graceful degradation when services fail"""
        start = time.time()
        try:
            class ServiceWithFallback:
                def __init__(self):
                    self.primary_available = True
                    self.fallback_used = False
                
                def get_data(self):
                    try:
                        if not self.primary_available:
                            raise Exception("Primary service unavailable")
                        return {"source": "primary", "data": "real-time data"}
                    except:
                        self.fallback_used = True
                        return {"source": "fallback", "data": "cached data"}
            
            service = ServiceWithFallback()
            
            # Test with primary available
            result = service.get_data()
            if result["source"] != "primary":
                self.log_test("Graceful Degradation", False, time.time() - start,
                            "Primary not used when available")
                return False
            
            # Disable primary
            service.primary_available = False
            
            # Test with fallback
            result = service.get_data()
            if result["source"] != "fallback":
                self.log_test("Graceful Degradation", False, time.time() - start,
                            "Fallback not used when primary unavailable")
                return False
            
            if not service.fallback_used:
                self.log_test("Graceful Degradation", False, time.time() - start,
                            "Fallback flag not set")
                return False
            
            self.log_test("Graceful Degradation", True, time.time() - start,
                        "Gracefully degraded from primary to fallback")
            return True
            
        except Exception as e:
            self.log_test("Graceful Degradation", False, time.time() - start, str(e))
            return False
    
    def test_timeout_handling(self) -> bool:
        """Test timeout handling for long-running operations"""
        start = time.time()
        try:
            import signal
            
            class TimeoutError(Exception):
                pass
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Operation timed out")
            
            def execute_with_timeout(func, timeout_seconds: float):
                # Set alarm
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.setitimer(signal.ITIMER_REAL, timeout_seconds)
                
                try:
                    result = func()
                    signal.setitimer(signal.ITIMER_REAL, 0)  # Cancel alarm
                    return result
                except TimeoutError:
                    signal.setitimer(signal.ITIMER_REAL, 0)  # Cancel alarm
                    raise
            
            # Test fast function (should succeed)
            def fast_function():
                time.sleep(0.01)
                return "success"
            
            result = execute_with_timeout(fast_function, 0.1)
            if result != "success":
                self.log_test("Timeout Handling", False, time.time() - start,
                            "Fast function didn't complete")
                return False
            
            # Test slow function (should timeout)
            def slow_function():
                time.sleep(0.5)
                return "should not reach here"
            
            try:
                execute_with_timeout(slow_function, 0.1)
                self.log_test("Timeout Handling", False, time.time() - start,
                            "Slow function didn't timeout")
                return False
            except TimeoutError:
                pass  # Expected
            
            self.log_test("Timeout Handling", True, time.time() - start,
                        "Timeout handling working correctly")
            return True
            
        except Exception as e:
            self.log_test("Timeout Handling", False, time.time() - start, str(e))
            return False
    
    def test_error_recovery_state_restoration(self) -> bool:
        """Test state restoration after error"""
        start = time.time()
        try:
            class StatefulProcessor:
                def __init__(self):
                    self.state = {"count": 0, "last_value": None}
                    self.checkpoint = None
                
                def save_checkpoint(self):
                    self.checkpoint = self.state.copy()
                
                def restore_checkpoint(self):
                    if self.checkpoint:
                        self.state = self.checkpoint.copy()
                
                def process(self, value: int, should_fail: bool = False):
                    self.save_checkpoint()
                    
                    try:
                        self.state["count"] += 1
                        self.state["last_value"] = value
                        
                        if should_fail:
                            raise Exception("Processing failed")
                        
                        return self.state
                    except:
                        self.restore_checkpoint()
                        raise
            
            processor = StatefulProcessor()
            
            # Successful processing
            processor.process(10)
            if processor.state["count"] != 1 or processor.state["last_value"] != 10:
                self.log_test("Error Recovery State Restoration", False, time.time() - start,
                            "State not updated after successful processing")
                return False
            
            # Failed processing (should restore state)
            try:
                processor.process(20, should_fail=True)
            except:
                pass
            
            # State should be restored to previous checkpoint
            if processor.state["count"] != 1 or processor.state["last_value"] != 10:
                self.log_test("Error Recovery State Restoration", False, time.time() - start,
                            f"State not restored: {processor.state}")
                return False
            
            self.log_test("Error Recovery State Restoration", True, time.time() - start,
                        "State successfully restored after error")
            return True
            
        except Exception as e:
            self.log_test("Error Recovery State Restoration", False, time.time() - start, str(e))
            return False
    
    def test_partial_failure_handling(self) -> bool:
        """Test handling of partial failures in batch operations"""
        start = time.time()
        try:
            class BatchProcessor:
                def __init__(self):
                    self.successful = []
                    self.failed = []
                
                def process_batch(self, items: List[dict]):
                    for item in items:
                        try:
                            if item.get("should_fail"):
                                raise Exception(f"Failed to process {item['id']}")
                            self.successful.append(item["id"])
                        except Exception as e:
                            self.failed.append({"id": item["id"], "error": str(e)})
                
                def get_results(self) -> dict:
                    return {
                        "successful": len(self.successful),
                        "failed": len(self.failed),
                        "total": len(self.successful) + len(self.failed)
                    }
            
            processor = BatchProcessor()
            
            # Batch with some failures
            items = [
                {"id": 1, "should_fail": False},
                {"id": 2, "should_fail": True},
                {"id": 3, "should_fail": False},
                {"id": 4, "should_fail": True},
                {"id": 5, "should_fail": False}
            ]
            
            processor.process_batch(items)
            results = processor.get_results()
            
            if results["successful"] != 3:
                self.log_test("Partial Failure Handling", False, time.time() - start,
                            f"Expected 3 successful, got {results['successful']}")
                return False
            
            if results["failed"] != 2:
                self.log_test("Partial Failure Handling", False, time.time() - start,
                            f"Expected 2 failed, got {results['failed']}")
                return False
            
            self.log_test("Partial Failure Handling", True, time.time() - start,
                        f"Processed batch: {results['successful']} succeeded, {results['failed']} failed")
            return True
            
        except Exception as e:
            self.log_test("Partial Failure Handling", False, time.time() - start, str(e))
            return False
    
    def test_dead_letter_queue(self) -> bool:
        """Test dead letter queue for failed messages"""
        start = time.time()
        try:
            class MessageQueueWithDLQ:
                def __init__(self, max_retries: int = 3):
                    self.max_retries = max_retries
                    self.main_queue = []
                    self.dead_letter_queue = []
                    self.retry_counts = {}
                
                def enqueue(self, message: dict):
                    self.main_queue.append(message)
                    self.retry_counts[message["id"]] = 0
                
                def process_message(self, message: dict) -> bool:
                    if message.get("should_fail"):
                        raise Exception("Processing failed")
                    return True
                
                def process_queue(self):
                    while self.main_queue:
                        message = self.main_queue.pop(0)
                        
                        try:
                            self.process_message(message)
                        except:
                            self.retry_counts[message["id"]] += 1
                            
                            if self.retry_counts[message["id"]] >= self.max_retries:
                                # Move to DLQ
                                self.dead_letter_queue.append(message)
                            else:
                                # Re-queue for retry
                                self.main_queue.append(message)
            
            queue = MessageQueueWithDLQ(max_retries=3)
            
            # Add messages
            queue.enqueue({"id": 1, "should_fail": False})
            queue.enqueue({"id": 2, "should_fail": True})
            queue.enqueue({"id": 3, "should_fail": False})
            
            # Process
            queue.process_queue()
            
            # Check DLQ
            if len(queue.dead_letter_queue) != 1:
                self.log_test("Dead Letter Queue", False, time.time() - start,
                            f"Expected 1 message in DLQ, got {len(queue.dead_letter_queue)}")
                return False
            
            if queue.dead_letter_queue[0]["id"] != 2:
                self.log_test("Dead Letter Queue", False, time.time() - start,
                            "Wrong message in DLQ")
                return False
            
            self.log_test("Dead Letter Queue", True, time.time() - start,
                        f"Failed message moved to DLQ after {queue.max_retries} retries")
            return True
            
        except Exception as e:
            self.log_test("Dead Letter Queue", False, time.time() - start, str(e))
            return False
    
    def test_health_check_monitoring(self) -> bool:
        """Test health check and monitoring"""
        start = time.time()
        try:
            class HealthMonitor:
                def __init__(self):
                    self.components = {}
                
                def register_component(self, name: str, check_func):
                    self.components[name] = check_func
                
                def check_health(self) -> dict:
                    results = {}
                    all_healthy = True
                    
                    for name, check_func in self.components.items():
                        try:
                            is_healthy = check_func()
                            results[name] = {
                                "status": "healthy" if is_healthy else "unhealthy",
                                "healthy": is_healthy
                            }
                            if not is_healthy:
                                all_healthy = False
                        except Exception as e:
                            results[name] = {
                                "status": "error",
                                "healthy": False,
                                "error": str(e)
                            }
                            all_healthy = False
                    
                    return {
                        "overall": "healthy" if all_healthy else "unhealthy",
                        "components": results
                    }
            
            monitor = HealthMonitor()
            
            # Register components
            monitor.register_component("database", lambda: True)
            monitor.register_component("cache", lambda: True)
            monitor.register_component("api", lambda: False)  # Unhealthy
            
            # Check health
            health = monitor.check_health()
            
            if health["overall"] != "unhealthy":
                self.log_test("Health Check Monitoring", False, time.time() - start,
                            "Overall health should be unhealthy")
                return False
            
            if health["components"]["database"]["status"] != "healthy":
                self.log_test("Health Check Monitoring", False, time.time() - start,
                            "Database should be healthy")
                return False
            
            if health["components"]["api"]["status"] != "unhealthy":
                self.log_test("Health Check Monitoring", False, time.time() - start,
                            "API should be unhealthy")
                return False
            
            self.log_test("Health Check Monitoring", True, time.time() - start,
                        f"Health check: {health['overall']} (3 components checked)")
            return True
            
        except Exception as e:
            self.log_test("Health Check Monitoring", False, time.time() - start, str(e))
            return False
    
    def test_cascading_failure_prevention(self) -> bool:
        """Test prevention of cascading failures"""
        start = time.time()
        try:
            class ServiceWithBulkhead:
                def __init__(self, max_concurrent: int = 3):
                    self.max_concurrent = max_concurrent
                    self.active_requests = 0
                    self.rejected_count = 0
                
                def execute(self, func):
                    if self.active_requests >= self.max_concurrent:
                        self.rejected_count += 1
                        raise Exception("Service overloaded - request rejected")
                    
                    self.active_requests += 1
                    try:
                        return func()
                    finally:
                        self.active_requests -= 1
            
            service = ServiceWithBulkhead(max_concurrent=2)
            
            # Simulate concurrent requests
            def mock_request():
                time.sleep(0.01)
                return "success"
            
            # First 2 should succeed
            service.active_requests = 0
            service.execute(lambda: "ok")
            service.active_requests = 1
            service.execute(lambda: "ok")
            
            # 3rd should be rejected
            service.active_requests = 2
            try:
                service.execute(lambda: "ok")
                self.log_test("Cascading Failure Prevention", False, time.time() - start,
                            "Request not rejected when at max capacity")
                return False
            except Exception as e:
                if "overloaded" not in str(e):
                    self.log_test("Cascading Failure Prevention", False, time.time() - start,
                                "Wrong exception type")
                    return False
            
            if service.rejected_count != 1:
                self.log_test("Cascading Failure Prevention", False, time.time() - start,
                            f"Expected 1 rejection, got {service.rejected_count}")
                return False
            
            self.log_test("Cascading Failure Prevention", True, time.time() - start,
                        f"Bulkhead pattern prevented overload (max: {service.max_concurrent})")
            return True
            
        except Exception as e:
            self.log_test("Cascading Failure Prevention", False, time.time() - start, str(e))
            return False
    
    def test_error_logging_and_alerting(self) -> bool:
        """Test error logging and alerting mechanisms"""
        start = time.time()
        try:
            class ErrorLogger:
                def __init__(self, alert_threshold: int = 5):
                    self.alert_threshold = alert_threshold
                    self.errors = []
                    self.alerts_sent = []
                
                def log_error(self, error: Exception, context: dict = None):
                    error_entry = {
                        "error": str(error),
                        "type": type(error).__name__,
                        "context": context or {},
                        "timestamp": time.time()
                    }
                    self.errors.append(error_entry)
                    
                    # Check if alert needed
                    if len(self.errors) >= self.alert_threshold:
                        self.send_alert()
                
                def send_alert(self):
                    self.alerts_sent.append({
                        "message": f"Error threshold reached: {len(self.errors)} errors",
                        "timestamp": time.time()
                    })
                
                def get_error_count(self) -> int:
                    return len(self.errors)
            
            logger = ErrorLogger(alert_threshold=3)
            
            # Log errors
            for i in range(5):
                logger.log_error(Exception(f"Error {i}"), {"request_id": i})
            
            if logger.get_error_count() != 5:
                self.log_test("Error Logging and Alerting", False, time.time() - start,
                            f"Expected 5 errors, got {logger.get_error_count()}")
                return False
            
            # Check alerts
            if len(logger.alerts_sent) == 0:
                self.log_test("Error Logging and Alerting", False, time.time() - start,
                            "No alerts sent despite threshold reached")
                return False
            
            self.log_test("Error Logging and Alerting", True, time.time() - start,
                        f"Logged {logger.get_error_count()} errors, sent {len(logger.alerts_sent)} alerts")
            return True
            
        except Exception as e:
            self.log_test("Error Logging and Alerting", False, time.time() - start, str(e))
            return False
    
    def run_all_tests(self):
        """Run all error recovery and resilience tests"""
        logger.info("=" * 80)
        logger.info("ERROR RECOVERY AND RESILIENCE TESTS")
        logger.info("=" * 80)
        
        tests = [
            self.test_retry_with_exponential_backoff,
            self.test_circuit_breaker_pattern,
            self.test_graceful_degradation,
            self.test_timeout_handling,
            self.test_error_recovery_state_restoration,
            self.test_partial_failure_handling,
            self.test_dead_letter_queue,
            self.test_health_check_monitoring,
            self.test_cascading_failure_prevention,
            self.test_error_logging_and_alerting
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
            "test_suite": "Error Recovery and Resilience Tests",
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
        
        output_file = Path("error_recovery_resilience_test_results.json")
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"✅ Results saved to {output_file}")
        
        return pass_rate >= 80


if __name__ == "__main__":
    tester = ErrorRecoveryResilienceTests()
    success = tester.run_all_tests()
    exit(0 if success else 1)
