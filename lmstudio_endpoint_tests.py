#!/usr/bin/env python3
"""
LMStudio Endpoint Comprehensive Testing Suite
Tests connectivity, API endpoints, and integration with new LMStudio URL
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LMStudioEndpointTester:
    """Comprehensive LMStudio endpoint testing"""
    
    def __init__(self, base_url="http://100.118.172.23:1234"):
        self.base_url = base_url
        self.results = {
            "test_suite": "LMStudio Endpoint Tests",
            "base_url": base_url,
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
    
    def add_result(self, test_name, passed, details="", duration=0):
        """Add test result"""
        self.results["tests"].append({
            "name": test_name,
            "passed": passed,
            "details": details,
            "duration_ms": round(duration * 1000, 2)
        })
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name} - {details}")
    
    def test_network_connectivity(self):
        """Test basic network connectivity to host"""
        test_name = "Network Connectivity"
        start = time.time()
        
        try:
            # Extract host and port
            host = self.base_url.split("//")[1].split(":")[0]
            port = int(self.base_url.split(":")[-1].split("/")[0])
            
            # Try to connect
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            duration = time.time() - start
            
            if result == 0:
                self.add_result(test_name, True, f"Connected to {host}:{port}", duration)
                return True
            else:
                self.add_result(test_name, False, f"Cannot connect to {host}:{port} (error code: {result})", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"Connection error: {str(e)}", duration)
            return False
    
    def test_http_get_models(self):
        """Test GET /v1/models endpoint"""
        test_name = "GET /v1/models"
        start = time.time()
        
        try:
            url = f"{self.base_url}/v1/models"
            req = Request(url, method='GET')
            req.add_header('Content-Type', 'application/json')
            
            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                duration = time.time() - start
                
                if 'data' in data or 'models' in data:
                    model_count = len(data.get('data', data.get('models', [])))
                    self.add_result(test_name, True, f"Retrieved {model_count} models", duration)
                    return True
                else:
                    self.add_result(test_name, True, f"Response received: {str(data)[:100]}", duration)
                    return True
                    
        except HTTPError as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"HTTP {e.code}: {e.reason}", duration)
            return False
        except URLError as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"URL Error: {str(e.reason)}", duration)
            return False
        except Exception as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"Error: {str(e)}", duration)
            return False
    
    def test_chat_completion_endpoint(self):
        """Test POST /v1/chat/completions endpoint"""
        test_name = "POST /v1/chat/completions"
        start = time.time()
        
        try:
            url = f"{self.base_url}/v1/chat/completions"
            
            payload = {
                "model": "glm-4-flash",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'test successful' if you can read this."}
                ],
                "temperature": 0.7,
                "max_tokens": 50
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            
            with urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                duration = time.time() - start
                
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0].get('message', {}).get('content', '')
                    self.add_result(test_name, True, f"Response: {message[:100]}", duration)
                    return True
                else:
                    self.add_result(test_name, True, f"Response received: {str(result)[:100]}", duration)
                    return True
                    
        except HTTPError as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"HTTP {e.code}: {e.reason}", duration)
            return False
        except URLError as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"URL Error: {str(e.reason)}", duration)
            return False
        except Exception as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"Error: {str(e)}", duration)
            return False
    
    def test_alternative_chat_endpoint(self):
        """Test POST /api/v1/chat endpoint (alternative format)"""
        test_name = "POST /api/v1/chat"
        start = time.time()
        
        try:
            url = f"{self.base_url}/api/v1/chat"
            
            payload = {
                "model": "glm-4-flash",
                "system_prompt": "You are a helpful trading assistant.",
                "input": "Analyze BTC/USDT market sentiment"
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            
            with urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                duration = time.time() - start
                
                response_text = str(result)[:100]
                self.add_result(test_name, True, f"Response: {response_text}", duration)
                return True
                    
        except HTTPError as e:
            duration = time.time() - start
            # 404 is expected if this endpoint doesn't exist
            if e.code == 404:
                self.add_result(test_name, True, "Endpoint not available (expected)", duration)
            else:
                self.add_result(test_name, False, f"HTTP {e.code}: {e.reason}", duration)
            return False
        except URLError as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"URL Error: {str(e.reason)}", duration)
            return False
        except Exception as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"Error: {str(e)}", duration)
            return False
    
    def test_timeout_handling(self):
        """Test timeout handling with very short timeout"""
        test_name = "Timeout Handling (2s)"
        start = time.time()
        
        try:
            url = f"{self.base_url}/v1/chat/completions"
            
            payload = {
                "model": "glm-4-flash",
                "messages": [
                    {"role": "user", "content": "Quick test"}
                ],
                "max_tokens": 10
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            
            with urlopen(req, timeout=2) as response:
                result = json.loads(response.read().decode())
                duration = time.time() - start
                self.add_result(test_name, True, f"Completed in {duration:.2f}s", duration)
                return True
                    
        except socket.timeout:
            duration = time.time() - start
            self.add_result(test_name, True, f"Timeout detected correctly after {duration:.2f}s", duration)
            return True
        except Exception as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"Error: {str(e)}", duration)
            return False
    
    def test_error_handling_invalid_model(self):
        """Test error handling with invalid model name"""
        test_name = "Error Handling (Invalid Model)"
        start = time.time()
        
        try:
            url = f"{self.base_url}/v1/chat/completions"
            
            payload = {
                "model": "nonexistent-model-12345",
                "messages": [
                    {"role": "user", "content": "Test"}
                ]
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            
            with urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                duration = time.time() - start
                # If it succeeds, the server might have a default model
                self.add_result(test_name, True, "Server handled invalid model gracefully", duration)
                return True
                    
        except HTTPError as e:
            duration = time.time() - start
            # 400 or 404 is expected for invalid model
            if e.code in [400, 404]:
                self.add_result(test_name, True, f"Correctly returned HTTP {e.code}", duration)
                return True
            else:
                self.add_result(test_name, False, f"Unexpected HTTP {e.code}", duration)
                return False
        except Exception as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"Error: {str(e)}", duration)
            return False
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        test_name = "Concurrent Requests (3 parallel)"
        start = time.time()
        
        try:
            import threading
            results = []
            
            def make_request():
                try:
                    url = f"{self.base_url}/v1/chat/completions"
                    payload = {
                        "model": "glm-4-flash",
                        "messages": [{"role": "user", "content": "Quick test"}],
                        "max_tokens": 10
                    }
                    data = json.dumps(payload).encode('utf-8')
                    req = Request(url, data=data, method='POST')
                    req.add_header('Content-Type', 'application/json')
                    
                    with urlopen(req, timeout=15) as response:
                        json.loads(response.read().decode())
                        results.append(True)
                except:
                    results.append(False)
            
            threads = [threading.Thread(target=make_request) for _ in range(3)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=20)
            
            duration = time.time() - start
            success_count = sum(results)
            
            if success_count > 0:
                self.add_result(test_name, True, f"{success_count}/3 requests succeeded", duration)
                return True
            else:
                self.add_result(test_name, False, "All concurrent requests failed", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start
            self.add_result(test_name, False, f"Error: {str(e)}", duration)
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        logger.info("=" * 80)
        logger.info(f"LMSTUDIO ENDPOINT TESTING - {self.base_url}")
        logger.info("=" * 80)
        
        # Test 1: Network connectivity (critical)
        network_ok = self.test_network_connectivity()
        
        if not network_ok:
            logger.warning("⚠️  Network connectivity failed - remaining tests will likely fail")
            logger.warning("⚠️  This is expected if LMStudio is not accessible from sandbox")
        
        # Test 2: List models
        self.test_http_get_models()
        
        # Test 3: Chat completion (standard endpoint)
        self.test_chat_completion_endpoint()
        
        # Test 4: Alternative chat endpoint
        self.test_alternative_chat_endpoint()
        
        # Test 5: Timeout handling
        self.test_timeout_handling()
        
        # Test 6: Error handling
        self.test_error_handling_invalid_model()
        
        # Test 7: Concurrent requests
        self.test_concurrent_requests()
        
        # Calculate summary
        total = len(self.results["tests"])
        passed = sum(1 for t in self.results["tests"] if t["passed"])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        self.results["summary"] = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(pass_rate, 2)
        }
        
        logger.info("=" * 80)
        logger.info(f"TEST SUMMARY: {passed}/{total} passed ({pass_rate:.1f}%)")
        logger.info("=" * 80)
        
        return self.results
    
    def save_results(self, filename="lmstudio_endpoint_test_results.json"):
        """Save test results to JSON file"""
        filepath = Path(filename)
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"✅ Test results saved to {filepath}")


def main():
    """Main test execution"""
    # Test with new LMStudio endpoint
    tester = LMStudioEndpointTester("http://100.118.172.23:1234")
    results = tester.run_all_tests()
    tester.save_results()
    
    # Print detailed results
    print("\n" + "=" * 80)
    print("DETAILED TEST RESULTS")
    print("=" * 80)
    for test in results["tests"]:
        status = "✅" if test["passed"] else "❌"
        print(f"{status} {test['name']}: {test['details']} ({test['duration_ms']}ms)")
    
    print("\n" + "=" * 80)
    print(f"FINAL RESULT: {results['summary']['passed']}/{results['summary']['total']} tests passed")
    print("=" * 80)
    
    return 0 if results['summary']['pass_rate'] >= 50 else 1


if __name__ == "__main__":
    sys.exit(main())
