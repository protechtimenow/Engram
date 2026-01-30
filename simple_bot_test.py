#!/usr/bin/env python3
"""
Simple Clawdbot Test Suite - No External Dependencies
Tests bot configuration and structure without requiring external libraries
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import asyncio
import subprocess

class SimpleBotTester:
    def __init__(self):
        self.results = {
            "test_run_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }
        self.passed = 0
        self.failed = 0
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {
            "INFO": "ℹ️",
            "PASS": "✅",
            "FAIL": "❌",
            "WARN": "⚠️",
            "TEST": "🧪"
        }
        symbol = symbols.get(level, "•")
        print(f"[{timestamp}] {symbol} {message}")
        
    def test(self, name, func):
        """Run a test function and record results"""
        self.log(f"\n--- {name} ---", "TEST")
        try:
            result = func()
            if result:
                self.log(f"PASS: {name}", "PASS")
                self.passed += 1
                self.results["tests"].append({
                    "name": name,
                    "status": "PASS",
                    "timestamp": datetime.now().isoformat()
                })
                return True
            else:
                self.log(f"FAIL: {name}", "FAIL")
                self.failed += 1
                self.results["tests"].append({
                    "name": name,
                    "status": "FAIL",
                    "timestamp": datetime.now().isoformat()
                })
                return False
        except Exception as e:
            self.log(f"FAIL: {name} - {str(e)}", "FAIL")
            self.failed += 1
            self.results["tests"].append({
                "name": name,
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def test_config_files(self):
        """Test configuration files exist and are valid"""
        config_path = Path("/vercel/sandbox/config/telegram/working_telegram_config.json")
        if not config_path.exists():
            return False
        
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            # Check for telegram section (nested structure)
            if "telegram" in config:
                telegram_config = config["telegram"]
                if "token" not in telegram_config or "chat_id" not in telegram_config:
                    self.log("Missing telegram token or chat_id in nested config", "FAIL")
                    return False
                
                self.log(f"Config valid - Bot token: {telegram_config['token'][:20]}...", "INFO")
                self.log(f"Chat ID: {telegram_config['chat_id']}", "INFO")
                return True
            
            # Check for flat structure
            required = ["telegram_bot_token", "telegram_chat_id"]
            for field in required:
                if field not in config:
                    self.log(f"Missing field: {field}", "FAIL")
                    return False
            
            self.log(f"Config valid - Bot token: {config['telegram_bot_token'][:20]}...", "INFO")
            self.log(f"Chat ID: {config['telegram_chat_id']}", "INFO")
            return True
        except Exception as e:
            self.log(f"Config error: {e}", "FAIL")
            return False
    
    def test_env_file(self):
        """Test .env file exists and has required variables"""
        env_path = Path("/vercel/sandbox/.env")
        if not env_path.exists():
            return False
        
        with open(env_path) as f:
            content = f.read()
        
        required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
        for var in required_vars:
            if var not in content:
                self.log(f"Missing env var: {var}", "FAIL")
                return False
        
        return True
    
    def test_bot_files(self):
        """Test bot Python files exist"""
        bot_files = [
            "/vercel/sandbox/live_telegram_bot.py",
            "/vercel/sandbox/live_clawdbot_bot.py",
            "/vercel/sandbox/live_bot_runner.py"
        ]
        
        for bot_file in bot_files:
            if not Path(bot_file).exists():
                self.log(f"Missing: {bot_file}", "FAIL")
                return False
        
        return True
    
    def test_bot_structure(self):
        """Test bot files have proper async structure"""
        bot_path = Path("/vercel/sandbox/live_telegram_bot.py")
        
        with open(bot_path) as f:
            content = f.read()
        
        # Check for async patterns
        required_patterns = [
            "async def main",
            "run_polling",
            "Application.builder()",
            "CommandHandler"
        ]
        
        for pattern in required_patterns:
            if pattern not in content:
                self.log(f"Missing pattern: {pattern}", "FAIL")
                return False
        
        self.log("Bot has proper async/polling structure", "INFO")
        return True
    
    def test_directory_structure(self):
        """Test required directories exist"""
        required_dirs = [
            "/vercel/sandbox/config",
            "/vercel/sandbox/config/telegram",
            "/vercel/sandbox/logs",
            "/vercel/sandbox/src"
        ]
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                self.log(f"Missing directory: {dir_path}", "FAIL")
                return False
        
        return True
    
    def test_python_version(self):
        """Test Python version is adequate"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.log(f"Python {version.major}.{version.minor}.{version.micro}", "INFO")
            return True
        return False
    
    def test_bot_syntax(self):
        """Test bot files have valid Python syntax"""
        bot_files = [
            "/vercel/sandbox/live_telegram_bot.py",
            "/vercel/sandbox/live_clawdbot_bot.py"
        ]
        
        for bot_file in bot_files:
            try:
                with open(bot_file) as f:
                    compile(f.read(), bot_file, 'exec')
                self.log(f"Valid syntax: {Path(bot_file).name}", "INFO")
            except SyntaxError as e:
                self.log(f"Syntax error in {bot_file}: {e}", "FAIL")
                return False
        
        return True
    
    def test_process_manager(self):
        """Test process manager script exists and is executable"""
        manager_path = Path("/vercel/sandbox/clawdbot_manager.sh")
        
        if not manager_path.exists():
            return False
        
        # Check if executable
        if not os.access(manager_path, os.X_OK):
            self.log("Manager script not executable", "WARN")
        
        with open(manager_path) as f:
            content = f.read()
        
        # Check for required functions
        required_funcs = ["start()", "stop()", "status()"]
        for func in required_funcs:
            if func not in content:
                self.log(f"Missing function: {func}", "FAIL")
                return False
        
        return True
    
    def test_log_directory(self):
        """Test log directory is writable"""
        log_dir = Path("/vercel/sandbox/logs")
        
        if not log_dir.exists():
            return False
        
        # Try to create a test file
        test_file = log_dir / "test_write.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception as e:
            self.log(f"Log directory not writable: {e}", "FAIL")
            return False
    
    def test_telegram_api_reachability(self):
        """Test if Telegram API is reachable (using subprocess curl)"""
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 "https://api.telegram.org", "--max-time", "5"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip() in ["200", "302", "301"]:
                self.log(f"Telegram API reachable (HTTP {result.stdout.strip()})", "INFO")
                return True
            else:
                self.log(f"Telegram API unreachable (HTTP {result.stdout.strip()})", "WARN")
                return False
        except Exception as e:
            self.log(f"Cannot test API reachability: {e}", "WARN")
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        self.log("=" * 70, "INFO")
        self.log("SIMPLE CLAWDBOT TEST SUITE (No External Dependencies)", "TEST")
        self.log("=" * 70, "INFO")
        self.log(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
        
        # Run tests
        self.test("Configuration Files Valid", self.test_config_files)
        self.test("Environment File Valid", self.test_env_file)
        self.test("Bot Files Exist", self.test_bot_files)
        self.test("Bot Async Structure", self.test_bot_structure)
        self.test("Directory Structure", self.test_directory_structure)
        self.test("Python Version >= 3.8", self.test_python_version)
        self.test("Bot Syntax Valid", self.test_bot_syntax)
        self.test("Process Manager Exists", self.test_process_manager)
        self.test("Log Directory Writable", self.test_log_directory)
        self.test("Telegram API Reachable", self.test_telegram_api_reachability)
        
        # Summary
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        self.log("", "INFO")
        self.log("=" * 70, "INFO")
        self.log("TEST SUMMARY", "TEST")
        self.log("=" * 70, "INFO")
        self.log(f"Total Tests: {total}", "INFO")
        self.log(f"Passed: {self.passed} ✅", "PASS")
        self.log(f"Failed: {self.failed} ❌", "FAIL")
        self.log(f"Pass Rate: {pass_rate:.1f}%", "INFO")
        
        self.results["summary"] = {
            "total": total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": pass_rate
        }
        
        # Save results
        results_file = Path("/vercel/sandbox/simple_test_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"\n📄 Results saved to: {results_file}", "INFO")
        
        # Recommendations
        self.log("", "INFO")
        self.log("=" * 70, "INFO")
        self.log("RECOMMENDATIONS", "TEST")
        self.log("=" * 70, "INFO")
        
        if self.failed == 0:
            self.log("✅ All tests passed! Bot is ready for deployment.", "PASS")
            self.log("", "INFO")
            self.log("Next Steps:", "INFO")
            self.log("1. Start bot: python3 live_bot_runner.py &", "INFO")
            self.log("2. Or use manager: ./clawdbot_manager.sh start", "INFO")
            self.log("3. Monitor logs: tail -f logs/bot_runner.log", "INFO")
        elif self.failed <= 2:
            self.log("⚠️  Minor issues detected. Review and fix before deployment.", "WARN")
        else:
            self.log("❌ Multiple failures. Significant work needed.", "FAIL")
        
        self.log("=" * 70, "INFO")
        
        return pass_rate >= 80

if __name__ == "__main__":
    tester = SimpleBotTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
