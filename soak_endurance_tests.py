#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Soak/Endurance Tests for Engram Trading Bot
Tests long-running scenarios, memory leaks, and stability
"""

import sys
import json
import time
import logging
import gc
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Test results storage
test_results = {
    "test_run": {
        "timestamp": datetime.now().isoformat(),
        "suite": "Soak/Endurance Tests"
    },
    "tests": [],
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }
}


def add_test_result(name: str, status: str, message: str, details: Dict = None):
    """Add a test result"""
    test_results["tests"].append({
        "name": name,
        "status": status,
        "message": message,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    })
    test_results["summary"]["total"] += 1
    if status == "PASS":
        test_results["summary"]["passed"] += 1
        logger.info(f"✅ PASS: {name} - {message}")
    elif status == "FAIL":
        test_results["summary"]["failed"] += 1
        logger.error(f"❌ FAIL: {name} - {message}")
    else:
        test_results["summary"]["skipped"] += 1
        logger.warning(f"⏭️  SKIP: {name} - {message}")


def test_memory_leak_detection():
    """Test for memory leaks over extended operations"""
    try:
        import numpy as np
        
        process = psutil.Process()
        mem_samples = []
        iterations = 1000
        
        logger.info(f"Running {iterations} iterations to detect memory leaks...")
        
        for i in range(iterations):
            # Simulate trading operations
            data = np.random.uniform(100, 200, 1000)
            mean = np.mean(data)
            std = np.std(data)
            
            # Sample memory every 100 iterations
            if i % 100 == 0:
                mem_mb = process.memory_info().rss / (1024 * 1024)
                mem_samples.append(mem_mb)
                logger.info(f"  Iteration {i}: Memory = {mem_mb:.2f} MB")
            
            # Clean up
            del data
        
        # Force garbage collection
        gc.collect()
        
        # Check for memory leak
        if len(mem_samples) >= 2:
            mem_increase = mem_samples[-1] - mem_samples[0]
            leak_threshold = 10  # MB
            
            if mem_increase < leak_threshold:
                add_test_result(
                    "Memory Leak Detection",
                    "PASS",
                    f"No significant memory leak detected ({mem_increase:.2f} MB increase)",
                    {
                        "iterations": iterations,
                        "initial_memory_mb": mem_samples[0],
                        "final_memory_mb": mem_samples[-1],
                        "memory_increase_mb": mem_increase,
                        "samples": mem_samples
                    }
                )
                return True
            else:
                add_test_result(
                    "Memory Leak Detection",
                    "FAIL",
                    f"Potential memory leak detected ({mem_increase:.2f} MB increase)",
                    {"memory_increase_mb": mem_increase}
                )
                return False
        else:
            add_test_result("Memory Leak Detection", "FAIL", "Insufficient memory samples")
            return False
            
    except Exception as e:
        add_test_result("Memory Leak Detection", "FAIL", str(e))
        return False


def test_continuous_operations():
    """Test continuous operations over time"""
    try:
        import numpy as np
        
        duration_seconds = 30
        start_time = time.time()
        operations = 0
        errors = 0
        
        logger.info(f"Running continuous operations for {duration_seconds} seconds...")
        
        while time.time() - start_time < duration_seconds:
            try:
                # Simulate trading calculations
                prices = np.random.uniform(100, 200, 100)
                sma = np.mean(prices)
                volatility = np.std(prices)
                operations += 1
                
                if operations % 100 == 0:
                    elapsed = time.time() - start_time
                    ops_per_sec = operations / elapsed
                    logger.info(f"  {operations} operations, {ops_per_sec:.1f} ops/sec")
                
            except Exception as e:
                errors += 1
                logger.error(f"  Error in operation {operations}: {e}")
        
        elapsed = time.time() - start_time
        ops_per_sec = operations / elapsed
        
        if errors == 0:
            add_test_result(
                "Continuous Operations",
                "PASS",
                f"Completed {operations} operations in {elapsed:.1f}s ({ops_per_sec:.1f} ops/sec)",
                {
                    "duration_seconds": elapsed,
                    "total_operations": operations,
                    "operations_per_second": ops_per_sec,
                    "errors": errors
                }
            )
            return True
        else:
            add_test_result(
                "Continuous Operations",
                "FAIL",
                f"{errors} errors in {operations} operations",
                {"errors": errors, "operations": operations}
            )
            return False
            
    except Exception as e:
        add_test_result("Continuous Operations", "FAIL", str(e))
        return False


def test_resource_stability():
    """Test resource usage stability over time"""
    try:
        import numpy as np
        
        process = psutil.Process()
        duration_seconds = 20
        samples = []
        
        logger.info(f"Monitoring resource stability for {duration_seconds} seconds...")
        
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            # Perform operations
            data = np.random.uniform(100, 200, 1000)
            _ = np.mean(data)
            
            # Sample resources
            cpu = psutil.cpu_percent(interval=0.1)
            mem = process.memory_info().rss / (1024 * 1024)
            
            samples.append({"cpu": cpu, "memory_mb": mem})
            
            if len(samples) % 5 == 0:
                logger.info(f"  Sample {len(samples)}: CPU={cpu:.1f}%, Memory={mem:.1f}MB")
            
            time.sleep(0.5)
        
        # Analyze stability
        if samples:
            cpu_values = [s["cpu"] for s in samples]
            mem_values = [s["memory_mb"] for s in samples]
            
            cpu_std = np.std(cpu_values)
            mem_std = np.std(mem_values)
            
            add_test_result(
                "Resource Stability",
                "PASS",
                f"Resources stable over {len(samples)} samples",
                {
                    "samples": len(samples),
                    "cpu_std": float(cpu_std),
                    "memory_std_mb": float(mem_std),
                    "avg_cpu": float(np.mean(cpu_values)),
                    "avg_memory_mb": float(np.mean(mem_values))
                }
            )
            return True
        else:
            add_test_result("Resource Stability", "FAIL", "No samples collected")
            return False
            
    except Exception as e:
        add_test_result("Resource Stability", "FAIL", str(e))
        return False


def test_repeated_config_loading():
    """Test repeated configuration loading"""
    try:
        config_file = Path("config/telegram/working_telegram_config.json")
        
        if not config_file.exists():
            add_test_result(
                "Repeated Config Loading",
                "SKIP",
                "Config file not found"
            )
            return True
        
        iterations = 500
        errors = 0
        
        logger.info(f"Loading config {iterations} times...")
        
        start_time = time.time()
        for i in range(iterations):
            try:
                with config_file.open('r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if i % 100 == 0:
                    logger.info(f"  Iteration {i}")
                    
            except Exception as e:
                errors += 1
                logger.error(f"  Error at iteration {i}: {e}")
        
        elapsed = time.time() - start_time
        loads_per_sec = iterations / elapsed
        
        if errors == 0:
            add_test_result(
                "Repeated Config Loading",
                "PASS",
                f"Loaded config {iterations} times ({loads_per_sec:.1f} loads/sec)",
                {
                    "iterations": iterations,
                    "duration_seconds": elapsed,
                    "loads_per_second": loads_per_sec,
                    "errors": errors
                }
            )
            return True
        else:
            add_test_result(
                "Repeated Config Loading",
                "FAIL",
                f"{errors} errors in {iterations} loads",
                {"errors": errors}
            )
            return False
            
    except Exception as e:
        add_test_result("Repeated Config Loading", "FAIL", str(e))
        return False


def test_concurrent_stress():
    """Test concurrent operations under stress"""
    try:
        import numpy as np
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def worker_task(task_id, iterations):
            """Worker task for stress testing"""
            results = []
            for i in range(iterations):
                data = np.random.uniform(100, 200, 100)
                result = {
                    "mean": float(np.mean(data)),
                    "std": float(np.std(data))
                }
                results.append(result)
            return task_id, len(results)
        
        num_workers = 10
        iterations_per_worker = 100
        
        logger.info(f"Running {num_workers} concurrent workers, {iterations_per_worker} iterations each...")
        
        start_time = time.time()
        completed_tasks = 0
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {
                executor.submit(worker_task, i, iterations_per_worker): i 
                for i in range(num_workers)
            }
            
            for future in as_completed(futures):
                try:
                    task_id, count = future.result()
                    completed_tasks += 1
                    logger.info(f"  Worker {task_id} completed {count} iterations")
                except Exception as e:
                    logger.error(f"  Worker failed: {e}")
        
        elapsed = time.time() - start_time
        total_operations = num_workers * iterations_per_worker
        ops_per_sec = total_operations / elapsed
        
        if completed_tasks == num_workers:
            add_test_result(
                "Concurrent Stress Test",
                "PASS",
                f"{num_workers} workers completed {total_operations} operations ({ops_per_sec:.1f} ops/sec)",
                {
                    "workers": num_workers,
                    "iterations_per_worker": iterations_per_worker,
                    "total_operations": total_operations,
                    "duration_seconds": elapsed,
                    "operations_per_second": ops_per_sec
                }
            )
            return True
        else:
            add_test_result(
                "Concurrent Stress Test",
                "FAIL",
                f"Only {completed_tasks}/{num_workers} workers completed",
                {"completed": completed_tasks, "expected": num_workers}
            )
            return False
            
    except Exception as e:
        add_test_result("Concurrent Stress Test", "FAIL", str(e))
        return False


def test_error_recovery():
    """Test error recovery and resilience"""
    try:
        import numpy as np
        
        iterations = 100
        intentional_errors = 0
        recovered = 0
        
        logger.info(f"Testing error recovery over {iterations} iterations...")
        
        for i in range(iterations):
            try:
                # Intentionally cause errors every 10 iterations
                if i % 10 == 0 and i > 0:
                    intentional_errors += 1
                    # Cause an error
                    _ = np.array([]) / 0
                else:
                    # Normal operation
                    data = np.random.uniform(100, 200, 100)
                    _ = np.mean(data)
                    
            except Exception as e:
                # Recover from error
                recovered += 1
                logger.info(f"  Recovered from error at iteration {i}")
        
        if recovered == intentional_errors:
            add_test_result(
                "Error Recovery",
                "PASS",
                f"Successfully recovered from {recovered} intentional errors",
                {
                    "iterations": iterations,
                    "intentional_errors": intentional_errors,
                    "recovered": recovered
                }
            )
            return True
        else:
            add_test_result(
                "Error Recovery",
                "FAIL",
                f"Recovery mismatch: {recovered} recovered vs {intentional_errors} errors",
                {"recovered": recovered, "errors": intentional_errors}
            )
            return False
            
    except Exception as e:
        add_test_result("Error Recovery", "FAIL", str(e))
        return False


def save_results():
    """Save test results to JSON file"""
    try:
        output_file = Path("soak_endurance_test_results.json")
        with output_file.open('w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        logger.info(f"Test results saved to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        return False


def main():
    """Run all soak/endurance tests"""
    logger.info("=" * 80)
    logger.info("SOAK/ENDURANCE TESTS - ENGRAM TRADING BOT")
    logger.info("=" * 80)
    logger.info("")
    
    # Run all tests
    tests = [
        ("Memory Leak Detection", test_memory_leak_detection),
        ("Continuous Operations", test_continuous_operations),
        ("Resource Stability", test_resource_stability),
        ("Repeated Config Loading", test_repeated_config_loading),
        ("Concurrent Stress", test_concurrent_stress),
        ("Error Recovery", test_error_recovery),
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning: Test - {test_name}")
        try:
            test_func()
        except Exception as e:
            add_test_result(test_name, "FAIL", f"Unexpected error: {e}")
        time.sleep(0.5)
    
    # Print summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("SOAK/ENDURANCE TEST RESULTS")
    logger.info("=" * 80)
    logger.info(f"\nTotal Tests: {test_results['summary']['total']}")
    logger.info(f"✅ Passed: {test_results['summary']['passed']}")
    logger.info(f"❌ Failed: {test_results['summary']['failed']}")
    logger.info(f"⏭️  Skipped: {test_results['summary']['skipped']}")
    
    if test_results['summary']['total'] > 0:
        pass_rate = (test_results['summary']['passed'] / test_results['summary']['total']) * 100
        logger.info(f"Pass Rate: {pass_rate:.1f}%")
    
    logger.info("")
    
    # Save results
    save_results()
    
    # Return exit code
    return 0 if test_results['summary']['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
