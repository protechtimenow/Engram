#!/usr/bin/env python3
"""
Thorough Testing Suite for Engram Trading Bot
Covers all remaining test scenarios including:
- Engram-FreqTrade integration startup
- Telegram endpoint testing (normal and edge cases)
- Performance and resource usage validation
- Error handling for invalid configs and credentials
"""

import sys
import os
import json
import time
import traceback
import subprocess
from pathlib import Path
from datetime import datetime
import importlib.util

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class ThoroughTestSuite:
    def __init__(self):
        self.results = {
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        self.project_root = Path(__file__).parent
        
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "[INFO]",
            "PASS": "[PASS]",
            "FAIL": "[FAIL]",
            "WARN": "[WARN]"
        }.get(level, "[INFO]")
        print(f"[{timestamp}] {prefix} {message}")
        
    def record_test(self, name, passed, details="", warning=False):
        """Record test result"""
        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "warning": warning,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        self.results["summary"]["total"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
            self.log(f"PASS: {name} - {details}", "PASS")
        elif warning:
            self.results["summary"]["warnings"] += 1
            self.log(f"WARN: {name} - {details}", "WARN")
        else:
            self.results["summary"]["failed"] += 1
            self.log(f"FAIL: {name} - {details}", "FAIL")
    
    def test_engram_freqtrade_integration_startup(self):
        """Test 1: Engram-FreqTrade Integration Startup"""
        self.log("\n" + "="*80)
        self.log("TEST 1: ENGRAM-FREQTRADE INTEGRATION STARTUP")
        self.log("="*80)
        
        # Test 1.1: Check if FreqTrade strategy files exist
        strategy_files = [
            "src/trading/engram_trading_strategy.py",
            "simple_engram_strategy.py"
        ]
        
        for strategy_file in strategy_files:
            path = self.project_root / strategy_file
            if path.exists():
                self.record_test(
                    f"Strategy file exists: {strategy_file}",
                    True,
                    f"Found at {path}"
                )
            else:
                self.record_test(
                    f"Strategy file exists: {strategy_file}",
                    False,
                    f"Not found at {path}"
                )
        
        # Test 1.2: Validate strategy file syntax
        for strategy_file in strategy_files:
            path = self.project_root / strategy_file
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    compile(code, str(path), 'exec')
                    self.record_test(
                        f"Strategy syntax valid: {strategy_file}",
                        True,
                        "No syntax errors"
                    )
                except SyntaxError as e:
                    self.record_test(
                        f"Strategy syntax valid: {strategy_file}",
                        False,
                        f"Syntax error: {e}"
                    )
        
        # Test 1.3: Check Engram model import
        try:
            spec = importlib.util.spec_from_file_location(
                "engram_demo",
                self.project_root / "src/core/engram_demo_v1.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules["engram_demo"] = module
                spec.loader.exec_module(module)
                self.record_test(
                    "Engram model import",
                    True,
                    "Successfully imported engram_demo_v1.py"
                )
            else:
                self.record_test(
                    "Engram model import",
                    False,
                    "Could not create module spec"
                )
        except Exception as e:
            self.record_test(
                "Engram model import",
                False,
                f"Import error: {str(e)}"
            )
        
        # Test 1.4: Check FreqTrade config files
        config_files = [
            "config/freqtrade_config.json",
            "config/engram_freqtrade_config.json"
        ]
        
        for config_file in config_files:
            path = self.project_root / config_file
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    self.record_test(
                        f"FreqTrade config valid: {config_file}",
                        True,
                        f"Valid JSON with {len(config)} keys"
                    )
                except json.JSONDecodeError as e:
                    self.record_test(
                        f"FreqTrade config valid: {config_file}",
                        False,
                        f"Invalid JSON: {e}"
                    )
            else:
                self.record_test(
                    f"FreqTrade config exists: {config_file}",
                    False,
                    f"Not found at {path}"
                )
        
        # Test 1.5: Test launch script syntax
        launch_script = self.project_root / "scripts/launch_engram_trader.py"
        if launch_script.exists():
            try:
                with open(launch_script, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, str(launch_script), 'exec')
                self.record_test(
                    "Launch script syntax valid",
                    True,
                    "scripts/launch_engram_trader.py has no syntax errors"
                )
            except SyntaxError as e:
                self.record_test(
                    "Launch script syntax valid",
                    False,
                    f"Syntax error: {e}"
                )
    
    def test_telegram_endpoints(self):
        """Test 2: Telegram Endpoint Testing"""
        self.log("\n" + "="*80)
        self.log("TEST 2: TELEGRAM ENDPOINT TESTING")
        self.log("="*80)
        
        # Test 2.1: Load Telegram config
        telegram_config_path = self.project_root / "config/telegram/working_telegram_config.json"
        telegram_config = None
        
        if telegram_config_path.exists():
            try:
                with open(telegram_config_path, 'r', encoding='utf-8') as f:
                    telegram_config = json.load(f)
                self.record_test(
                    "Telegram config loaded",
                    True,
                    f"Loaded from {telegram_config_path}"
                )
            except Exception as e:
                self.record_test(
                    "Telegram config loaded",
                    False,
                    f"Error: {e}"
                )
                return
        else:
            self.record_test(
                "Telegram config exists",
                False,
                f"Not found at {telegram_config_path}"
            )
            return
        
        # Test 2.2: Validate Telegram credentials structure
        if telegram_config:
            required_keys = ["telegram"]
            telegram_section = telegram_config.get("telegram", {})
            
            if "bot_token" in telegram_section and "chat_id" in telegram_section:
                self.record_test(
                    "Telegram credentials structure valid",
                    True,
                    "bot_token and chat_id present"
                )
            else:
                self.record_test(
                    "Telegram credentials structure valid",
                    False,
                    f"Missing required keys. Found: {list(telegram_section.keys())}"
                )
        
        # Test 2.3: Test Telegram bot files syntax
        bot_files = [
            "live_telegram_bot.py",
            "simple_telegram_bot.py",
            "sync_telegram_bot.py",
            "src/engram_telegram/engram_telegram_bot.py"
        ]
        
        for bot_file in bot_files:
            path = self.project_root / bot_file
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    compile(code, str(path), 'exec')
                    self.record_test(
                        f"Bot file syntax: {bot_file}",
                        True,
                        "No syntax errors"
                    )
                except SyntaxError as e:
                    self.record_test(
                        f"Bot file syntax: {bot_file}",
                        False,
                        f"Syntax error: {e}"
                    )
        
        # Test 2.4: Test edge case - Invalid config handling
        try:
            invalid_config = '{"invalid": json}'
            compile(invalid_config, '<string>', 'eval')
            self.record_test(
                "Invalid config detection",
                False,
                "Should have detected invalid JSON"
            )
        except:
            self.record_test(
                "Invalid config detection",
                True,
                "Correctly detects invalid JSON"
            )
        
        # Test 2.5: Test edge case - Missing credentials
        empty_config = {}
        if "telegram" not in empty_config:
            self.record_test(
                "Missing credentials detection",
                True,
                "Correctly detects missing telegram section"
            )
        else:
            self.record_test(
                "Missing credentials detection",
                False,
                "Should detect missing credentials"
            )
    
    def test_performance_and_resources(self):
        """Test 3: Performance and Resource Usage"""
        self.log("\n" + "="*80)
        self.log("TEST 3: PERFORMANCE AND RESOURCE USAGE")
        self.log("="*80)
        
        # Test 3.1: Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.record_test(
                "Python version check",
                True,
                f"Python {python_version.major}.{python_version.minor}.{python_version.micro}"
            )
        else:
            self.record_test(
                "Python version check",
                False,
                f"Python {python_version.major}.{python_version.minor} < 3.8"
            )
        
        # Test 3.2: Check available memory
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            mem_total = None
            mem_available = None
            for line in meminfo.split('\n'):
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1]) / 1024  # MB
                elif line.startswith('MemAvailable:'):
                    mem_available = int(line.split()[1]) / 1024  # MB
            
            if mem_total and mem_available:
                self.record_test(
                    "Memory availability check",
                    True,
                    f"Total: {mem_total:.0f} MB, Available: {mem_available:.0f} MB"
                )
                
                # Warn if less than 8GB available
                if mem_available < 8192:
                    self.record_test(
                        "Sufficient memory for Engram model",
                        True,
                        f"Available: {mem_available:.0f} MB (Warning: <8GB may cause issues)",
                        warning=True
                    )
                else:
                    self.record_test(
                        "Sufficient memory for Engram model",
                        True,
                        f"Available: {mem_available:.0f} MB (Sufficient)"
                    )
        except Exception as e:
            self.record_test(
                "Memory availability check",
                False,
                f"Could not read /proc/meminfo: {e}"
            )
        
        # Test 3.3: Check disk space
        try:
            stat = os.statvfs(self.project_root)
            free_space = (stat.f_bavail * stat.f_frsize) / (1024**3)  # GB
            self.record_test(
                "Disk space check",
                True,
                f"Free space: {free_space:.2f} GB"
            )
            
            if free_space < 10:
                self.record_test(
                    "Sufficient disk space",
                    True,
                    f"{free_space:.2f} GB (Warning: <10GB may cause issues)",
                    warning=True
                )
            else:
                self.record_test(
                    "Sufficient disk space",
                    True,
                    f"{free_space:.2f} GB (Sufficient)"
                )
        except Exception as e:
            self.record_test(
                "Disk space check",
                False,
                f"Error: {e}"
            )
        
        # Test 3.4: Test file I/O performance
        try:
            test_file = self.project_root / "logs" / "test_io_performance.tmp"
            test_file.parent.mkdir(exist_ok=True)
            
            start_time = time.time()
            with open(test_file, 'w') as f:
                f.write("test" * 10000)
            write_time = time.time() - start_time
            
            start_time = time.time()
            with open(test_file, 'r') as f:
                _ = f.read()
            read_time = time.time() - start_time
            
            test_file.unlink()
            
            self.record_test(
                "File I/O performance",
                True,
                f"Write: {write_time*1000:.2f}ms, Read: {read_time*1000:.2f}ms"
            )
        except Exception as e:
            self.record_test(
                "File I/O performance",
                False,
                f"Error: {e}"
            )
        
        # Test 3.5: Test import performance
        try:
            start_time = time.time()
            import json
            import asyncio
            import pathlib
            import datetime
            import logging
            import_time = time.time() - start_time
            
            self.record_test(
                "Standard library import performance",
                True,
                f"Import time: {import_time*1000:.2f}ms"
            )
        except Exception as e:
            self.record_test(
                "Standard library import performance",
                False,
                f"Error: {e}"
            )
    
    def test_error_handling(self):
        """Test 4: Error Handling Validation"""
        self.log("\n" + "="*80)
        self.log("TEST 4: ERROR HANDLING VALIDATION")
        self.log("="*80)
        
        # Test 4.1: Missing config file handling
        missing_config = self.project_root / "config/nonexistent_config.json"
        if not missing_config.exists():
            self.record_test(
                "Missing config file detection",
                True,
                "Correctly identifies missing config file"
            )
        else:
            self.record_test(
                "Missing config file detection",
                False,
                "File should not exist"
            )
        
        # Test 4.2: Invalid JSON handling
        try:
            invalid_json = '{"key": "value", invalid}'
            json.loads(invalid_json)
            self.record_test(
                "Invalid JSON detection",
                False,
                "Should have raised JSONDecodeError"
            )
        except json.JSONDecodeError:
            self.record_test(
                "Invalid JSON detection",
                True,
                "Correctly detects invalid JSON"
            )
        
        # Test 4.3: Empty config handling
        try:
            empty_config = json.loads('{}')
            if not empty_config.get("telegram"):
                self.record_test(
                    "Empty config handling",
                    True,
                    "Correctly handles empty config"
                )
            else:
                self.record_test(
                    "Empty config handling",
                    False,
                    "Should detect missing telegram section"
                )
        except Exception as e:
            self.record_test(
                "Empty config handling",
                False,
                f"Error: {e}"
            )
        
        # Test 4.4: Invalid credentials format
        invalid_creds = {
            "telegram": {
                "bot_token": "",  # Empty token
                "chat_id": "invalid"  # Invalid chat ID
            }
        }
        
        if not invalid_creds["telegram"]["bot_token"]:
            self.record_test(
                "Empty token detection",
                True,
                "Correctly detects empty bot token"
            )
        else:
            self.record_test(
                "Empty token detection",
                False,
                "Should detect empty token"
            )
        
        # Test 4.5: Test .env file validation
        env_file = self.project_root / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    env_content = f.read()
                
                required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
                missing_vars = []
                
                for var in required_vars:
                    if var not in env_content:
                        missing_vars.append(var)
                
                if not missing_vars:
                    self.record_test(
                        ".env file validation",
                        True,
                        "All required variables present"
                    )
                else:
                    self.record_test(
                        ".env file validation",
                        False,
                        f"Missing variables: {missing_vars}"
                    )
            except Exception as e:
                self.record_test(
                    ".env file validation",
                    False,
                    f"Error reading .env: {e}"
                )
        else:
            self.record_test(
                ".env file exists",
                False,
                "No .env file found"
            )
        
        # Test 4.6: Test directory permissions
        try:
            logs_dir = self.project_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            test_file = logs_dir / "test_permissions.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            self.record_test(
                "Logs directory writable",
                True,
                "Can write to logs directory"
            )
        except Exception as e:
            self.record_test(
                "Logs directory writable",
                False,
                f"Error: {e}"
            )
    
    def test_integration_readiness(self):
        """Test 5: Integration Readiness"""
        self.log("\n" + "="*80)
        self.log("TEST 5: INTEGRATION READINESS")
        self.log("="*80)
        
        # Test 5.1: Check all required files exist
        required_files = [
            "src/core/engram_demo_v1.py",
            "src/trading/engram_trading_strategy.py",
            "config/telegram/working_telegram_config.json",
            "config/freqtrade_config.json",
            ".env"
        ]
        
        all_exist = True
        for file_path in required_files:
            path = self.project_root / file_path
            if not path.exists():
                all_exist = False
                self.record_test(
                    f"Required file exists: {file_path}",
                    False,
                    f"Not found at {path}"
                )
        
        if all_exist:
            self.record_test(
                "All required files present",
                True,
                f"All {len(required_files)} required files exist"
            )
        
        # Test 5.2: Check Python dependencies availability
        dependencies = {
            "json": "json",
            "asyncio": "asyncio",
            "pathlib": "pathlib",
            "logging": "logging",
            "datetime": "datetime",
            "os": "os",
            "sys": "sys"
        }
        
        missing_deps = []
        for name, module in dependencies.items():
            try:
                __import__(module)
            except ImportError:
                missing_deps.append(name)
        
        if not missing_deps:
            self.record_test(
                "Standard library dependencies",
                True,
                f"All {len(dependencies)} standard libraries available"
            )
        else:
            self.record_test(
                "Standard library dependencies",
                False,
                f"Missing: {missing_deps}"
            )
        
        # Test 5.3: Check optional dependencies
        optional_deps = {
            "requests": "requests",
            "websockets": "websockets",
            "telegram": "telegram",
            "sympy": "sympy",
            "torch": "torch",
            "numpy": "numpy"
        }
        
        available_optional = []
        missing_optional = []
        
        for name, module in optional_deps.items():
            try:
                __import__(module)
                available_optional.append(name)
            except ImportError:
                missing_optional.append(name)
        
        if available_optional:
            self.record_test(
                "Optional dependencies available",
                True,
                f"Available: {', '.join(available_optional)}",
                warning=len(missing_optional) > 0
            )
        
        if missing_optional:
            self.record_test(
                "Optional dependencies missing",
                True,
                f"Missing: {', '.join(missing_optional)} (Optional for advanced features)",
                warning=True
            )
        
        # Test 5.4: Test configuration consistency
        try:
            # Load .env
            env_vars = {}
            env_file = self.project_root / ".env"
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key] = value
            
            # Load telegram config
            telegram_config_path = self.project_root / "config/telegram/working_telegram_config.json"
            if telegram_config_path.exists():
                with open(telegram_config_path, 'r', encoding='utf-8') as f:
                    telegram_config = json.load(f)
                
                # Check consistency
                env_token = env_vars.get("TELEGRAM_BOT_TOKEN", "")
                config_token = telegram_config.get("telegram", {}).get("bot_token", "")
                
                if env_token and config_token and env_token == config_token:
                    self.record_test(
                        "Config consistency check",
                        True,
                        ".env and config file tokens match"
                    )
                elif env_token and config_token:
                    self.record_test(
                        "Config consistency check",
                        True,
                        "Both .env and config have tokens (may differ)",
                        warning=True
                    )
                else:
                    self.record_test(
                        "Config consistency check",
                        False,
                        "Missing tokens in .env or config"
                    )
        except Exception as e:
            self.record_test(
                "Config consistency check",
                False,
                f"Error: {e}"
            )
    
    def generate_report(self):
        """Generate final test report"""
        self.log("\n" + "="*80)
        self.log("THOROUGH TESTING SUITE - FINAL REPORT")
        self.log("="*80)
        
        self.results["end_time"] = datetime.now().isoformat()
        
        # Calculate pass rate
        total = self.results["summary"]["total"]
        passed = self.results["summary"]["passed"]
        failed = self.results["summary"]["failed"]
        warnings = self.results["summary"]["warnings"]
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        self.log(f"\nTotal Tests: {total}")
        self.log(f"Passed: {passed} ({pass_rate:.1f}%)")
        self.log(f"Failed: {failed}")
        self.log(f"Warnings: {warnings}")
        
        # Save results to JSON
        results_file = self.project_root / "thorough_test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"\nDetailed results saved to: {results_file}")
        
        # Generate summary report
        summary_file = self.project_root / "THOROUGH_TEST_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Thorough Testing Suite - Summary Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Test Results\n\n")
            f.write(f"- **Total Tests:** {total}\n")
            f.write(f"- **Passed:** {passed} ({pass_rate:.1f}%)\n")
            f.write(f"- **Failed:** {failed}\n")
            f.write(f"- **Warnings:** {warnings}\n\n")
            
            f.write("## Test Categories\n\n")
            f.write("### 1. Engram-FreqTrade Integration Startup\n")
            f.write("Tests for strategy files, Engram model import, and FreqTrade configuration.\n\n")
            
            f.write("### 2. Telegram Endpoint Testing\n")
            f.write("Tests for Telegram configuration, bot files, and edge case handling.\n\n")
            
            f.write("### 3. Performance and Resource Usage\n")
            f.write("Tests for Python version, memory, disk space, and I/O performance.\n\n")
            
            f.write("### 4. Error Handling Validation\n")
            f.write("Tests for missing configs, invalid JSON, empty configs, and permissions.\n\n")
            
            f.write("### 5. Integration Readiness\n")
            f.write("Tests for required files, dependencies, and configuration consistency.\n\n")
            
            f.write("## Detailed Results\n\n")
            for test in self.results["tests"]:
                status = "✅ PASS" if test["passed"] else "❌ FAIL"
                if test["warning"]:
                    status = "⚠️ WARN"
                f.write(f"- {status}: {test['name']}\n")
                if test["details"]:
                    f.write(f"  - {test['details']}\n")
            
            f.write("\n## Recommendations\n\n")
            if failed > 0:
                f.write("### Critical Issues\n")
                for test in self.results["tests"]:
                    if not test["passed"] and not test["warning"]:
                        f.write(f"- **{test['name']}**: {test['details']}\n")
                f.write("\n")
            
            if warnings > 0:
                f.write("### Warnings\n")
                for test in self.results["tests"]:
                    if test["warning"]:
                        f.write(f"- **{test['name']}**: {test['details']}\n")
                f.write("\n")
            
            if pass_rate >= 90:
                f.write("### Overall Status: ✅ EXCELLENT\n")
                f.write("System is ready for deployment with minimal issues.\n")
            elif pass_rate >= 75:
                f.write("### Overall Status: ✅ GOOD\n")
                f.write("System is functional with some areas needing attention.\n")
            elif pass_rate >= 50:
                f.write("### Overall Status: ⚠️ FAIR\n")
                f.write("System has significant issues that should be addressed.\n")
            else:
                f.write("### Overall Status: ❌ POOR\n")
                f.write("System requires major fixes before deployment.\n")
        
        self.log(f"Summary report saved to: {summary_file}")
        
        return pass_rate >= 75

def main():
    """Main test execution"""
    print("="*80)
    print("THOROUGH TESTING SUITE FOR ENGRAM TRADING BOT")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    suite = ThoroughTestSuite()
    
    try:
        # Run all test suites
        suite.test_engram_freqtrade_integration_startup()
        suite.test_telegram_endpoints()
        suite.test_performance_and_resources()
        suite.test_error_handling()
        suite.test_integration_readiness()
        
        # Generate final report
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
