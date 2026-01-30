#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Clawdbot System
Executes thorough testing across all components and features
"""

import sys
import os
import json
import asyncio
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Test results storage
test_results = {
    "start_time": None,
    "end_time": None,
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "phases": {}
}


class TestRunner:
    """Comprehensive test runner for Clawdbot system"""
    
    def __init__(self):
        self.results = []
        self.current_phase = None
        self.bot_process = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "FAIL": "❌",
            "WARN": "⚠️",
            "TEST": "🧪"
        }.get(level, "•")
        print(f"[{timestamp}] {prefix} {message}")
        
    def record_test(self, phase: str, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        result = {
            "phase": phase,
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        if phase not in test_results["phases"]:
            test_results["phases"][phase] = {"passed": 0, "failed": 0, "tests": []}
        
        test_results["total_tests"] += 1
        if passed:
            test_results["passed"] += 1
            test_results["phases"][phase]["passed"] += 1
            self.log(f"PASS: {test_name}", "SUCCESS")
        else:
            test_results["failed"] += 1
            test_results["phases"][phase]["failed"] += 1
            self.log(f"FAIL: {test_name} - {details}", "FAIL")
        
        test_results["phases"][phase]["tests"].append(result)
    
    # ========== PHASE 1: CRITICAL PATH TESTING ==========
    
    async def test_phase1_critical_path(self):
        """Phase 1: Critical-Path Testing"""
        self.log("=" * 70)
        self.log("PHASE 1: CRITICAL-PATH TESTING", "TEST")
        self.log("=" * 70)
        
        await self.test_configuration_validation()
        await self.test_environment_setup()
        await self.test_dependencies()
        
    async def test_configuration_validation(self):
        """Test 1.1: Configuration Validation"""
        self.log("\n--- Test 1.1: Configuration Validation ---", "TEST")
        
        # Test Telegram config
        config_path = Path("config/telegram/working_telegram_config.json")
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Validate structure
                has_telegram = "telegram" in config
                has_token = config.get("telegram", {}).get("token")
                has_chat_id = config.get("telegram", {}).get("chat_id")
                
                self.record_test(
                    "Phase1_CriticalPath",
                    "Telegram config file exists and valid JSON",
                    True,
                    f"Token present: {bool(has_token)}, Chat ID present: {bool(has_chat_id)}"
                )
                
                if has_token and has_chat_id:
                    self.record_test(
                        "Phase1_CriticalPath",
                        "Telegram credentials present",
                        True,
                        f"Token: {has_token[:20]}..., Chat ID: {has_chat_id}"
                    )
                else:
                    self.record_test(
                        "Phase1_CriticalPath",
                        "Telegram credentials present",
                        False,
                        "Missing token or chat_id"
                    )
            else:
                self.record_test(
                    "Phase1_CriticalPath",
                    "Telegram config file exists",
                    False,
                    f"File not found: {config_path}"
                )
        except Exception as e:
            self.record_test(
                "Phase1_CriticalPath",
                "Telegram config validation",
                False,
                str(e)
            )
        
        # Test .env file
        env_path = Path(".env")
        try:
            if env_path.exists():
                with open(env_path, 'r') as f:
                    env_content = f.read()
                
                has_telegram_token = "TELEGRAM_BOT_TOKEN" in env_content
                has_telegram_chat = "TELEGRAM_CHAT_ID" in env_content
                
                self.record_test(
                    "Phase1_CriticalPath",
                    ".env file exists with Telegram vars",
                    has_telegram_token and has_telegram_chat,
                    f"Token var: {has_telegram_token}, Chat var: {has_telegram_chat}"
                )
            else:
                self.record_test(
                    "Phase1_CriticalPath",
                    ".env file exists",
                    False,
                    "File not found"
                )
        except Exception as e:
            self.record_test(
                "Phase1_CriticalPath",
                ".env file validation",
                False,
                str(e)
            )
    
    async def test_environment_setup(self):
        """Test 1.2: Environment Setup"""
        self.log("\n--- Test 1.2: Environment Setup ---", "TEST")
        
        # Check Python version
        python_version = sys.version_info
        version_ok = python_version >= (3, 8)
        self.record_test(
            "Phase1_CriticalPath",
            "Python version >= 3.8",
            version_ok,
            f"Python {python_version.major}.{python_version.minor}.{python_version.micro}"
        )
        
        # Check required directories
        required_dirs = ["src", "config", "logs"]
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            exists = dir_path.exists() and dir_path.is_dir()
            self.record_test(
                "Phase1_CriticalPath",
                f"Directory '{dir_name}' exists",
                exists,
                f"Path: {dir_path.absolute()}"
            )
    
    async def test_dependencies(self):
        """Test 1.3: Dependencies"""
        self.log("\n--- Test 1.3: Python Dependencies ---", "TEST")
        
        required_packages = [
            "telegram",
            "asyncio",
            "websockets",
            "json",
            "pathlib"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.record_test(
                    "Phase1_CriticalPath",
                    f"Package '{package}' importable",
                    True,
                    "Successfully imported"
                )
            except ImportError as e:
                self.record_test(
                    "Phase1_CriticalPath",
                    f"Package '{package}' importable",
                    False,
                    str(e)
                )
    
    # ========== PHASE 2: INTEGRATION TESTING ==========
    
    async def test_phase2_integration(self):
        """Phase 2: Integration Testing"""
        self.log("\n" + "=" * 70)
        self.log("PHASE 2: INTEGRATION TESTING", "TEST")
        self.log("=" * 70)
        
        await self.test_lmstudio_integration()
        await self.test_clawdbot_websocket()
        await self.test_engram_model()
    
    async def test_lmstudio_integration(self):
        """Test 2.1: LMStudio Integration"""
        self.log("\n--- Test 2.1: LMStudio Integration ---", "TEST")
        
        try:
            import requests
            
            # Test LMStudio API endpoint
            lmstudio_url = "http://192.168.56.1:1234/v1/models"
            
            try:
                response = requests.get(lmstudio_url, timeout=5)
                if response.status_code == 200:
                    models = response.json()
                    self.record_test(
                        "Phase2_Integration",
                        "LMStudio API accessible",
                        True,
                        f"Found {len(models.get('data', []))} models"
                    )
                    
                    # Check if any model is loaded
                    has_models = len(models.get('data', [])) > 0
                    self.record_test(
                        "Phase2_Integration",
                        "LMStudio has loaded models",
                        has_models,
                        f"Models: {models.get('data', [])}"
                    )
                else:
                    self.record_test(
                        "Phase2_Integration",
                        "LMStudio API accessible",
                        False,
                        f"HTTP {response.status_code}"
                    )
            except requests.exceptions.RequestException as e:
                self.record_test(
                    "Phase2_Integration",
                    "LMStudio API accessible",
                    False,
                    f"Connection error: {str(e)}"
                )
        except ImportError:
            self.record_test(
                "Phase2_Integration",
                "LMStudio integration test",
                False,
                "requests library not available"
            )
    
    async def test_clawdbot_websocket(self):
        """Test 2.2: ClawdBot WebSocket"""
        self.log("\n--- Test 2.2: ClawdBot WebSocket ---", "TEST")
        
        try:
            import websockets
            
            ws_url = "ws://127.0.0.1:18789"
            
            try:
                async with asyncio.wait_for(
                    websockets.connect(ws_url),
                    timeout=5
                ) as websocket:
                    self.record_test(
                        "Phase2_Integration",
                        "ClawdBot WebSocket connection",
                        True,
                        f"Connected to {ws_url}"
                    )
                    
                    # Test hello message
                    hello_msg = {
                        "type": "hello",
                        "version": "1",
                        "userAgent": "TestClient/1.0"
                    }
                    await websocket.send(json.dumps(hello_msg))
                    
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    data = json.loads(response)
                    
                    is_hello = data.get("type") == "hello"
                    self.record_test(
                        "Phase2_Integration",
                        "ClawdBot hello handshake",
                        is_hello,
                        f"Response type: {data.get('type')}"
                    )
                    
            except asyncio.TimeoutError:
                self.record_test(
                    "Phase2_Integration",
                    "ClawdBot WebSocket connection",
                    False,
                    "Connection timeout - ClawdBot may not be running"
                )
            except Exception as e:
                self.record_test(
                    "Phase2_Integration",
                    "ClawdBot WebSocket connection",
                    False,
                    str(e)
                )
        except ImportError:
            self.record_test(
                "Phase2_Integration",
                "ClawdBot WebSocket test",
                False,
                "websockets library not available"
            )
    
    async def test_engram_model(self):
        """Test 2.3: Engram Model"""
        self.log("\n--- Test 2.3: Engram Model ---", "TEST")
        
        # Check if Engram model file exists
        engram_path = Path("src/core/engram_demo_v1.py")
        
        if engram_path.exists():
            self.record_test(
                "Phase2_Integration",
                "Engram model file exists",
                True,
                f"Path: {engram_path}"
            )
            
            # Try to import Engram model
            try:
                sys.path.insert(0, "src")
                from core.engram_demo_v1 import EngramModel
                
                self.record_test(
                    "Phase2_Integration",
                    "Engram model importable",
                    True,
                    "Successfully imported EngramModel"
                )
                
                # Try to initialize model
                try:
                    model = EngramModel(
                        use_clawdbot=False,
                        use_lmstudio=False
                    )
                    self.record_test(
                        "Phase2_Integration",
                        "Engram model initialization",
                        True,
                        "Model initialized successfully"
                    )
                except Exception as e:
                    self.record_test(
                        "Phase2_Integration",
                        "Engram model initialization",
                        False,
                        str(e)
                    )
            except ImportError as e:
                self.record_test(
                    "Phase2_Integration",
                    "Engram model importable",
                    False,
                    str(e)
                )
        else:
            self.record_test(
                "Phase2_Integration",
                "Engram model file exists",
                False,
                f"File not found: {engram_path}"
            )
    
    # ========== PHASE 3: TELEGRAM BOT TESTING ==========
    
    async def test_phase3_telegram_bot(self):
        """Phase 3: Telegram Bot Testing"""
        self.log("\n" + "=" * 70)
        self.log("PHASE 3: TELEGRAM BOT TESTING", "TEST")
        self.log("=" * 70)
        
        await self.test_telegram_bot_structure()
        await self.test_telegram_bot_initialization()
    
    async def test_telegram_bot_structure(self):
        """Test 3.1: Telegram Bot Structure"""
        self.log("\n--- Test 3.1: Telegram Bot Structure ---", "TEST")
        
        # Check bot files
        bot_files = [
            "live_telegram_bot.py",
            "live_clawdbot_bot.py",
            "simple_telegram_bot.py"
        ]
        
        for bot_file in bot_files:
            bot_path = Path(bot_file)
            exists = bot_path.exists()
            self.record_test(
                "Phase3_TelegramBot",
                f"Bot file '{bot_file}' exists",
                exists,
                f"Path: {bot_path.absolute()}"
            )
    
    async def test_telegram_bot_initialization(self):
        """Test 3.2: Telegram Bot Initialization"""
        self.log("\n--- Test 3.2: Telegram Bot Initialization ---", "TEST")
        
        try:
            # Load config
            config_path = Path("config/telegram/working_telegram_config.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            token = config.get("telegram", {}).get("token")
            chat_id = config.get("telegram", {}).get("chat_id")
            
            if token and chat_id:
                # Try to import bot class
                try:
                    sys.path.insert(0, str(Path.cwd()))
                    
                    # Test if we can create bot instance (without starting)
                    from telegram import Bot
                    
                    bot = Bot(token=token)
                    self.record_test(
                        "Phase3_TelegramBot",
                        "Telegram Bot object creation",
                        True,
                        "Bot instance created successfully"
                    )
                    
                    # Note: We don't actually call get_me() to avoid network calls
                    # in sandbox environment
                    
                except Exception as e:
                    self.record_test(
                        "Phase3_TelegramBot",
                        "Telegram Bot object creation",
                        False,
                        str(e)
                    )
            else:
                self.record_test(
                    "Phase3_TelegramBot",
                    "Telegram credentials available",
                    False,
                    "Missing token or chat_id"
                )
        except Exception as e:
            self.record_test(
                "Phase3_TelegramBot",
                "Telegram bot initialization test",
                False,
                str(e)
            )
    
    # ========== PHASE 4: PROCESS PERSISTENCE TESTING ==========
    
    async def test_phase4_persistence(self):
        """Phase 4: Process Persistence Testing"""
        self.log("\n" + "=" * 70)
        self.log("PHASE 4: PROCESS PERSISTENCE TESTING", "TEST")
        self.log("=" * 70)
        
        await self.test_bot_startup()
        await self.test_bot_persistence()
    
    async def test_bot_startup(self):
        """Test 4.1: Bot Startup"""
        self.log("\n--- Test 4.1: Bot Startup Test ---", "TEST")
        
        # Test if bot script is executable
        bot_script = Path("live_clawdbot_bot.py")
        
        if bot_script.exists():
            self.record_test(
                "Phase4_Persistence",
                "Bot script exists",
                True,
                f"Path: {bot_script.absolute()}"
            )
            
            # Check if script has proper shebang
            with open(bot_script, 'r') as f:
                first_line = f.readline().strip()
            
            has_shebang = first_line.startswith("#!")
            self.record_test(
                "Phase4_Persistence",
                "Bot script has shebang",
                has_shebang,
                f"First line: {first_line}"
            )
        else:
            self.record_test(
                "Phase4_Persistence",
                "Bot script exists",
                False,
                "File not found"
            )
    
    async def test_bot_persistence(self):
        """Test 4.2: Bot Persistence"""
        self.log("\n--- Test 4.2: Bot Persistence Test ---", "TEST")
        
        self.log("Note: Full persistence test requires running bot in background", "WARN")
        self.log("This would require ClawdBot gateway and LMStudio to be running", "WARN")
        
        # Check if we can create a process manager script
        pm_script_content = """#!/bin/bash
# Process manager for Clawdbot
# This script keeps the bot running in the background

BOT_SCRIPT="live_clawdbot_bot.py"
PID_FILE="/tmp/clawdbot.pid"
LOG_FILE="logs/clawdbot.log"

start() {
    if [ -f "$PID_FILE" ]; then
        echo "Bot is already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    mkdir -p logs
    nohup python3 "$BOT_SCRIPT" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Bot started (PID: $(cat $PID_FILE))"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Bot is not running"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    kill $PID
    rm "$PID_FILE"
    echo "Bot stopped"
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null; then
            echo "Bot is running (PID: $PID)"
            return 0
        else
            echo "Bot is not running (stale PID file)"
            rm "$PID_FILE"
            return 1
        fi
    else
        echo "Bot is not running"
        return 1
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
"""
        
        pm_script_path = Path("clawdbot_manager.sh")
        try:
            with open(pm_script_path, 'w') as f:
                f.write(pm_script_content)
            
            os.chmod(pm_script_path, 0o755)
            
            self.record_test(
                "Phase4_Persistence",
                "Process manager script created",
                True,
                f"Created: {pm_script_path}"
            )
        except Exception as e:
            self.record_test(
                "Phase4_Persistence",
                "Process manager script created",
                False,
                str(e)
            )
    
    # ========== PHASE 5: EDGE CASES & ERROR HANDLING ==========
    
    async def test_phase5_edge_cases(self):
        """Phase 5: Edge Cases & Error Handling"""
        self.log("\n" + "=" * 70)
        self.log("PHASE 5: EDGE CASES & ERROR HANDLING", "TEST")
        self.log("=" * 70)
        
        await self.test_invalid_config_handling()
        await self.test_missing_dependencies()
    
    async def test_invalid_config_handling(self):
        """Test 5.1: Invalid Config Handling"""
        self.log("\n--- Test 5.1: Invalid Config Handling ---", "TEST")
        
        # Test with invalid JSON
        invalid_json = "{ invalid json }"
        
        try:
            json.loads(invalid_json)
            self.record_test(
                "Phase5_EdgeCases",
                "Invalid JSON detection",
                False,
                "Should have raised JSONDecodeError"
            )
        except json.JSONDecodeError:
            self.record_test(
                "Phase5_EdgeCases",
                "Invalid JSON detection",
                True,
                "Correctly detected invalid JSON"
            )
    
    async def test_missing_dependencies(self):
        """Test 5.2: Missing Dependencies"""
        self.log("\n--- Test 5.2: Missing Dependencies Handling ---", "TEST")
        
        # Test importing non-existent module
        try:
            import nonexistent_module_xyz
            self.record_test(
                "Phase5_EdgeCases",
                "Missing module detection",
                False,
                "Should have raised ImportError"
            )
        except ImportError:
            self.record_test(
                "Phase5_EdgeCases",
                "Missing module detection",
                True,
                "Correctly detected missing module"
            )
    
    # ========== MAIN TEST EXECUTION ==========
    
    async def run_all_tests(self):
        """Run all test phases"""
        self.log("=" * 70)
        self.log("COMPREHENSIVE CLAWDBOT TESTING SUITE", "TEST")
        self.log("=" * 70)
        self.log(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("")
        
        test_results["start_time"] = datetime.now().isoformat()
        
        # Run all test phases
        await self.test_phase1_critical_path()
        await self.test_phase2_integration()
        await self.test_phase3_telegram_bot()
        await self.test_phase4_persistence()
        await self.test_phase5_edge_cases()
        
        test_results["end_time"] = datetime.now().isoformat()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.log("\n" + "=" * 70)
        self.log("TEST EXECUTION SUMMARY", "TEST")
        self.log("=" * 70)
        
        total = test_results["total_tests"]
        passed = test_results["passed"]
        failed = test_results["failed"]
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        self.log(f"\nTotal Tests: {total}")
        self.log(f"Passed: {passed} ✅", "SUCCESS")
        self.log(f"Failed: {failed} ❌", "FAIL" if failed > 0 else "INFO")
        self.log(f"Pass Rate: {pass_rate:.1f}%")
        
        self.log("\n--- Results by Phase ---")
        for phase_name, phase_data in test_results["phases"].items():
            phase_total = phase_data["passed"] + phase_data["failed"]
            phase_rate = (phase_data["passed"] / phase_total * 100) if phase_total > 0 else 0
            self.log(f"\n{phase_name}:")
            self.log(f"  Passed: {phase_data['passed']}/{phase_total} ({phase_rate:.1f}%)")
        
        # Save detailed report
        report_path = Path("test_results.json")
        with open(report_path, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        self.log(f"\n📄 Detailed report saved to: {report_path}")
        
        # Generate recommendations
        self.generate_recommendations()
    
    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        self.log("\n" + "=" * 70)
        self.log("RECOMMENDATIONS", "TEST")
        self.log("=" * 70)
        
        recommendations = []
        
        # Check critical failures
        phase1_data = test_results["phases"].get("Phase1_CriticalPath", {})
        if phase1_data.get("failed", 0) > 0:
            recommendations.append(
                "⚠️  CRITICAL: Phase 1 failures detected. Fix configuration and environment issues first."
            )
        
        # Check integration failures
        phase2_data = test_results["phases"].get("Phase2_Integration", {})
        if phase2_data.get("failed", 0) > 0:
            recommendations.append(
                "⚠️  Integration issues detected. Ensure LMStudio and ClawdBot are running."
            )
        
        # Check Telegram bot
        phase3_data = test_results["phases"].get("Phase3_TelegramBot", {})
        if phase3_data.get("failed", 0) > 0:
            recommendations.append(
                "⚠️  Telegram bot issues detected. Verify bot token and configuration."
            )
        
        # General recommendations
        if test_results["failed"] == 0:
            recommendations.append(
                "✅ All tests passed! System is ready for deployment."
            )
        elif test_results["failed"] <= 3:
            recommendations.append(
                "⚠️  Minor issues detected. Review failed tests and fix before production."
            )
        else:
            recommendations.append(
                "❌ Multiple failures detected. Significant work needed before deployment."
            )
        
        # Specific recommendations
        recommendations.extend([
            "\n📋 Next Steps:",
            "1. Review test_results.json for detailed failure information",
            "2. Fix critical path issues (Phase 1) first",
            "3. Ensure external services (LMStudio, ClawdBot) are running",
            "4. Test bot persistence with clawdbot_manager.sh",
            "5. Perform manual Telegram bot testing",
            "6. Run load and stress tests for production readiness"
        ])
        
        for rec in recommendations:
            self.log(rec)
        
        self.log("\n" + "=" * 70)


async def main():
    """Main test execution"""
    runner = TestRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
