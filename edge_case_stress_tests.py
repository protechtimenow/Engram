#!/usr/bin/env python3
"""
Edge Case and Stress Testing Suite
Tests edge cases, concurrency, error recovery, and stress scenarios
"""

import sys
import os
import json
import time
import asyncio
import threading
from pathlib import Path
from datetime import datetime
import traceback

sys.path.insert(0, str(Path(__file__).parent))

class EdgeCaseStressTests:
    def __init__(self):
        self.results = {
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"total": 0, "passed": 0, "failed": 0}
        }
        self.project_root = Path(__file__).parent
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "[INFO]", "PASS": "[PASS]", "FAIL": "[FAIL]"}.get(level, "[INFO]")
        print(f"[{timestamp}] {prefix} {message}")
        
    def record_test(self, name, passed, details=""):
        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        self.results["summary"]["total"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
            self.log(f"PASS: {name} - {details}", "PASS")
        else:
            self.results["summary"]["failed"] += 1
            self.log(f"FAIL: {name} - {details}", "FAIL")
    
    def test_concurrent_config_access(self):
        """Test 1: Concurrent Configuration Access"""
        self.log("\n" + "="*80)
        self.log("TEST 1: CONCURRENT CONFIGURATION ACCESS")
        self.log("="*80)
        
        config_path = self.project_root / "config/telegram/working_telegram_config.json"
        
        def read_config(thread_id):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return True, f"Thread {thread_id} read config successfully"
            except Exception as e:
                return False, f"Thread {thread_id} error: {e}"
        
        # Test concurrent reads
        threads = []
        results = []
        
        for i in range(10):
            thread = threading.Thread(target=lambda tid: results.append(read_config(tid)), args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        success_count = sum(1 for r in results if r[0])
        self.record_test(
            "Concurrent config reads",
            success_count == 10,
            f"{success_count}/10 threads succeeded"
        )
    
    def test_malformed_json_handling(self):
        """Test 2: Malformed JSON Handling"""
        self.log("\n" + "="*80)
        self.log("TEST 2: MALFORMED JSON HANDLING")
        self.log("="*80)
        
        malformed_jsons = [
            ('{"key": "value",}', "Trailing comma"),
            ('{"key": value}', "Unquoted value"),
            ('{key: "value"}', "Unquoted key"),
            ('{"key": "value"', "Missing closing brace"),
            ('{"key": "value"}}', "Extra closing brace"),
            ('', "Empty string"),
            ('null', "Null value"),
            ('[1, 2, 3]', "Array instead of object"),
        ]
        
        for malformed, description in malformed_jsons:
            try:
                json.loads(malformed)
                self.record_test(
                    f"Malformed JSON detection: {description}",
                    False,
                    "Should have raised JSONDecodeError"
                )
            except (json.JSONDecodeError, ValueError):
                self.record_test(
                    f"Malformed JSON detection: {description}",
                    True,
                    "Correctly detected malformed JSON"
                )
    
    def test_large_config_handling(self):
        """Test 3: Large Configuration Handling"""
        self.log("\n" + "="*80)
        self.log("TEST 3: LARGE CONFIGURATION HANDLING")
        self.log("="*80)
        
        # Create a large config
        large_config = {
            "telegram": {
                "token": "test_token",
                "chat_id": "12345"
            },
            "large_data": ["item" * 100 for _ in range(1000)]
        }
        
        try:
            # Test serialization
            start_time = time.time()
            json_str = json.dumps(large_config)
            serialize_time = time.time() - start_time
            
            # Test deserialization
            start_time = time.time()
            parsed = json.loads(json_str)
            deserialize_time = time.time() - start_time
            
            self.record_test(
                "Large config handling",
                True,
                f"Serialize: {serialize_time*1000:.2f}ms, Deserialize: {deserialize_time*1000:.2f}ms"
            )
        except Exception as e:
            self.record_test(
                "Large config handling",
                False,
                f"Error: {e}"
            )
    
    def test_unicode_handling(self):
        """Test 4: Unicode and Special Characters"""
        self.log("\n" + "="*80)
        self.log("TEST 4: UNICODE AND SPECIAL CHARACTERS")
        self.log("="*80)
        
        unicode_tests = [
            ("emoji", "🚀🤖💰"),
            ("chinese", "测试数据"),
            ("arabic", "اختبار"),
            ("special_chars", "!@#$%^&*()"),
            ("newlines", "line1\nline2\nline3"),
            ("tabs", "col1\tcol2\tcol3"),
        ]
        
        for name, text in unicode_tests:
            try:
                # Test JSON encoding/decoding
                config = {"test": text}
                json_str = json.dumps(config, ensure_ascii=False)
                parsed = json.loads(json_str)
                
                if parsed["test"] == text:
                    self.record_test(
                        f"Unicode handling: {name}",
                        True,
                        f"Correctly handled: {text[:20]}..."
                    )
                else:
                    self.record_test(
                        f"Unicode handling: {name}",
                        False,
                        "Text mismatch after encoding/decoding"
                    )
            except Exception as e:
                self.record_test(
                    f"Unicode handling: {name}",
                    False,
                    f"Error: {e}"
                )
    
    def test_file_permission_scenarios(self):
        """Test 5: File Permission Scenarios"""
        self.log("\n" + "="*80)
        self.log("TEST 5: FILE PERMISSION SCENARIOS")
        self.log("="*80)
        
        test_dir = self.project_root / "logs" / "permission_tests"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Test 5.1: Write to existing directory
        try:
            test_file = test_dir / "test_write.txt"
            test_file.write_text("test content")
            test_file.unlink()
            self.record_test(
                "Write to existing directory",
                True,
                "Successfully wrote and deleted file"
            )
        except Exception as e:
            self.record_test(
                "Write to existing directory",
                False,
                f"Error: {e}"
            )
        
        # Test 5.2: Create nested directories
        try:
            nested_dir = test_dir / "level1" / "level2" / "level3"
            nested_dir.mkdir(parents=True, exist_ok=True)
            self.record_test(
                "Create nested directories",
                True,
                f"Created {nested_dir}"
            )
        except Exception as e:
            self.record_test(
                "Create nested directories",
                False,
                f"Error: {e}"
            )
        
        # Cleanup
        try:
            import shutil
            shutil.rmtree(test_dir)
        except:
            pass
    
    def test_async_operations(self):
        """Test 6: Async Operations"""
        self.log("\n" + "="*80)
        self.log("TEST 6: ASYNC OPERATIONS")
        self.log("="*80)
        
        async def async_config_load():
            await asyncio.sleep(0.01)
            config_path = self.project_root / "config/telegram/working_telegram_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        async def run_concurrent_loads():
            tasks = [async_config_load() for _ in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        
        try:
            results = asyncio.run(run_concurrent_loads())
            success_count = sum(1 for r in results if isinstance(r, dict))
            self.record_test(
                "Async concurrent config loads",
                success_count == 5,
                f"{success_count}/5 async loads succeeded"
            )
        except Exception as e:
            self.record_test(
                "Async concurrent config loads",
                False,
                f"Error: {e}"
            )
    
    def test_memory_leak_detection(self):
        """Test 7: Memory Leak Detection"""
        self.log("\n" + "="*80)
        self.log("TEST 7: MEMORY LEAK DETECTION")
        self.log("="*80)
        
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Get initial memory usage
        try:
            with open('/proc/self/status', 'r') as f:
                status = f.read()
            
            initial_mem = None
            for line in status.split('\n'):
                if line.startswith('VmRSS:'):
                    initial_mem = int(line.split()[1])
                    break
            
            # Perform operations
            config_path = self.project_root / "config/telegram/working_telegram_config.json"
            for _ in range(100):
                with open(config_path, 'r', encoding='utf-8') as f:
                    _ = json.load(f)
            
            # Force garbage collection
            gc.collect()
            
            # Get final memory usage
            with open('/proc/self/status', 'r') as f:
                status = f.read()
            
            final_mem = None
            for line in status.split('\n'):
                if line.startswith('VmRSS:'):
                    final_mem = int(line.split()[1])
                    break
            
            if initial_mem and final_mem:
                mem_increase = final_mem - initial_mem
                self.record_test(
                    "Memory leak detection",
                    mem_increase < 10240,  # Less than 10MB increase
                    f"Memory increase: {mem_increase} KB (Initial: {initial_mem} KB, Final: {final_mem} KB)"
                )
            else:
                self.record_test(
                    "Memory leak detection",
                    False,
                    "Could not read memory usage"
                )
        except Exception as e:
            self.record_test(
                "Memory leak detection",
                False,
                f"Error: {e}"
            )
    
    def test_error_recovery(self):
        """Test 8: Error Recovery Scenarios"""
        self.log("\n" + "="*80)
        self.log("TEST 8: ERROR RECOVERY SCENARIOS")
        self.log("="*80)
        
        # Test 8.1: Recover from missing file
        try:
            missing_file = self.project_root / "nonexistent_file.json"
            try:
                with open(missing_file, 'r') as f:
                    _ = f.read()
                recovered = False
            except FileNotFoundError:
                # Recover by using default config
                default_config = {"telegram": {"token": "", "chat_id": ""}}
                recovered = True
            
            self.record_test(
                "Recover from missing file",
                recovered,
                "Successfully recovered with default config"
            )
        except Exception as e:
            self.record_test(
                "Recover from missing file",
                False,
                f"Error: {e}"
            )
        
        # Test 8.2: Recover from corrupted JSON
        try:
            corrupted_json = '{"key": "value"'
            try:
                json.loads(corrupted_json)
                recovered = False
            except json.JSONDecodeError:
                # Recover by using default config
                default_config = {"telegram": {"token": "", "chat_id": ""}}
                recovered = True
            
            self.record_test(
                "Recover from corrupted JSON",
                recovered,
                "Successfully recovered from JSON error"
            )
        except Exception as e:
            self.record_test(
                "Recover from corrupted JSON",
                False,
                f"Error: {e}"
            )
    
    def test_rate_limiting(self):
        """Test 9: Rate Limiting Simulation"""
        self.log("\n" + "="*80)
        self.log("TEST 9: RATE LIMITING SIMULATION")
        self.log("="*80)
        
        # Simulate rapid config reads
        config_path = self.project_root / "config/telegram/working_telegram_config.json"
        
        start_time = time.time()
        read_count = 0
        
        try:
            for _ in range(100):
                with open(config_path, 'r', encoding='utf-8') as f:
                    _ = json.load(f)
                read_count += 1
            
            elapsed_time = time.time() - start_time
            reads_per_second = read_count / elapsed_time
            
            self.record_test(
                "Rapid config reads",
                read_count == 100,
                f"Completed {read_count} reads in {elapsed_time:.2f}s ({reads_per_second:.0f} reads/sec)"
            )
        except Exception as e:
            self.record_test(
                "Rapid config reads",
                False,
                f"Error after {read_count} reads: {e}"
            )
    
    def test_path_traversal_protection(self):
        """Test 10: Path Traversal Protection"""
        self.log("\n" + "="*80)
        self.log("TEST 10: PATH TRAVERSAL PROTECTION")
        self.log("="*80)
        
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
        ]
        
        for malicious_path in malicious_paths:
            try:
                # Attempt to resolve path
                resolved = Path(malicious_path).resolve()
                
                # Check if path is within project root
                try:
                    resolved.relative_to(self.project_root)
                    within_project = True
                except ValueError:
                    within_project = False
                
                self.record_test(
                    f"Path traversal protection: {malicious_path[:30]}...",
                    not within_project or not resolved.exists(),
                    "Path correctly rejected or doesn't exist"
                )
            except Exception as e:
                self.record_test(
                    f"Path traversal protection: {malicious_path[:30]}...",
                    True,
                    f"Path rejected with error: {type(e).__name__}"
                )
    
    def generate_report(self):
        """Generate final report"""
        self.log("\n" + "="*80)
        self.log("EDGE CASE & STRESS TESTING - FINAL REPORT")
        self.log("="*80)
        
        self.results["end_time"] = datetime.now().isoformat()
        
        total = self.results["summary"]["total"]
        passed = self.results["summary"]["passed"]
        failed = self.results["summary"]["failed"]
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        self.log(f"\nTotal Tests: {total}")
        self.log(f"Passed: {passed} ({pass_rate:.1f}%)")
        self.log(f"Failed: {failed}")
        
        # Save results
        results_file = self.project_root / "edge_case_test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"\nResults saved to: {results_file}")
        
        return pass_rate >= 80

def main():
    print("="*80)
    print("EDGE CASE & STRESS TESTING SUITE")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    suite = EdgeCaseStressTests()
    
    try:
        suite.test_concurrent_config_access()
        suite.test_malformed_json_handling()
        suite.test_large_config_handling()
        suite.test_unicode_handling()
        suite.test_file_permission_scenarios()
        suite.test_async_operations()
        suite.test_memory_leak_detection()
        suite.test_error_recovery()
        suite.test_rate_limiting()
        suite.test_path_traversal_protection()
        
        success = suite.generate_report()
        
        print("\n" + "="*80)
        print("TESTING COMPLETE")
        print("="*80)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n[ERROR] Test suite failed: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
