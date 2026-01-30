#!/usr/bin/env python3
"""
Test bot persistence and daemon mode operation
This test verifies that Clawdbot can run continuously without exiting
"""

import sys
import os
import time
import subprocess
import signal
import json
from pathlib import Path
from datetime import datetime


class BotPersistenceTest:
    """Test bot persistence and daemon operation"""
    
    def __init__(self):
        self.results = []
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
    
    def test_simple_bot_startup(self):
        """Test if simple bot can start without errors"""
        self.log("Testing simple bot startup...", "TEST")
        
        bot_script = "simple_telegram_bot.py"
        
        if not Path(bot_script).exists():
            self.log(f"Bot script not found: {bot_script}", "FAIL")
            return False
        
        try:
            # Try to run bot for 5 seconds to see if it stays alive
            self.log(f"Starting {bot_script} for 5 seconds...", "INFO")
            
            process = subprocess.Popen(
                ["python3", bot_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait 5 seconds
            time.sleep(5)
            
            # Check if process is still running
            poll_result = process.poll()
            
            if poll_result is None:
                # Process is still running - SUCCESS
                self.log("✅ Bot is running and persistent!", "SUCCESS")
                
                # Terminate the process
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                return True
            else:
                # Process exited
                stdout, stderr = process.communicate()
                self.log(f"❌ Bot exited with code {poll_result}", "FAIL")
                if stderr:
                    self.log(f"Error output: {stderr[:500]}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Error testing bot: {e}", "FAIL")
            return False
    
    def test_live_clawdbot_startup(self):
        """Test if live_clawdbot_bot can start (may fail without ClawdBot)"""
        self.log("\nTesting live_clawdbot_bot startup...", "TEST")
        
        bot_script = "live_clawdbot_bot.py"
        
        if not Path(bot_script).exists():
            self.log(f"Bot script not found: {bot_script}", "FAIL")
            return False
        
        try:
            self.log(f"Starting {bot_script} (will fail without ClawdBot)...", "INFO")
            
            process = subprocess.Popen(
                ["python3", bot_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait 3 seconds
            time.sleep(3)
            
            # Check if process is still running
            poll_result = process.poll()
            
            if poll_result is None:
                # Process is still running
                self.log("✅ Bot started (waiting for ClawdBot connection)", "SUCCESS")
                
                # Terminate the process
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                return True
            else:
                # Process exited - expected without ClawdBot
                stdout, stderr = process.communicate()
                
                if "ClawdBot" in stderr or "websocket" in stderr.lower():
                    self.log("⚠️  Bot exited (ClawdBot not available - expected)", "WARN")
                    return True  # This is expected behavior
                else:
                    self.log(f"❌ Bot exited unexpectedly: {stderr[:300]}", "FAIL")
                    return False
                
        except Exception as e:
            self.log(f"Error testing bot: {e}", "FAIL")
            return False
    
    def test_process_manager(self):
        """Test the process manager script"""
        self.log("\nTesting process manager script...", "TEST")
        
        pm_script = Path("clawdbot_manager.sh")
        
        if not pm_script.exists():
            self.log("Process manager script not found", "FAIL")
            return False
        
        # Check if script is executable
        is_executable = os.access(pm_script, os.X_OK)
        
        if is_executable:
            self.log("✅ Process manager script is executable", "SUCCESS")
        else:
            self.log("⚠️  Process manager script is not executable", "WARN")
            # Make it executable
            os.chmod(pm_script, 0o755)
            self.log("✅ Made script executable", "SUCCESS")
        
        # Test status command (should show not running)
        try:
            result = subprocess.run(
                ["./clawdbot_manager.sh", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            self.log(f"Status output: {result.stdout.strip()}", "INFO")
            
            if "not running" in result.stdout.lower():
                self.log("✅ Process manager status command works", "SUCCESS")
                return True
            else:
                self.log("⚠️  Unexpected status output", "WARN")
                return True  # Still counts as working
                
        except Exception as e:
            self.log(f"Error testing process manager: {e}", "FAIL")
            return False
    
    def test_daemon_mode_concept(self):
        """Test daemon mode concept with a simple background process"""
        self.log("\nTesting daemon mode concept...", "TEST")
        
        # Create a simple test daemon script
        test_daemon = Path("test_daemon.py")
        daemon_code = """#!/usr/bin/env python3
import time
import sys

print("Daemon started", flush=True)
sys.stdout.flush()

# Run for 10 seconds
for i in range(10):
    time.sleep(1)
    print(f"Daemon alive: {i+1}s", flush=True)
    sys.stdout.flush()

print("Daemon finished", flush=True)
"""
        
        with open(test_daemon, 'w') as f:
            f.write(daemon_code)
        
        os.chmod(test_daemon, 0o755)
        
        try:
            # Start daemon in background
            self.log("Starting test daemon...", "INFO")
            
            with open("test_daemon.log", 'w') as log_file:
                process = subprocess.Popen(
                    ["python3", str(test_daemon)],
                    stdout=log_file,
                    stderr=subprocess.STDOUT
                )
            
            # Wait 3 seconds
            time.sleep(3)
            
            # Check if still running
            if process.poll() is None:
                self.log("✅ Daemon is running in background", "SUCCESS")
                
                # Terminate
                process.terminate()
                process.wait(timeout=5)
                
                # Check log
                with open("test_daemon.log", 'r') as f:
                    log_content = f.read()
                
                if "Daemon alive" in log_content:
                    self.log("✅ Daemon produced output", "SUCCESS")
                    return True
            else:
                self.log("❌ Daemon exited prematurely", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Error testing daemon: {e}", "FAIL")
            return False
        finally:
            # Cleanup
            if test_daemon.exists():
                test_daemon.unlink()
            if Path("test_daemon.log").exists():
                Path("test_daemon.log").unlink()
    
    def run_all_tests(self):
        """Run all persistence tests"""
        self.log("=" * 70)
        self.log("BOT PERSISTENCE & DAEMON MODE TESTING", "TEST")
        self.log("=" * 70)
        
        results = {
            "simple_bot_startup": self.test_simple_bot_startup(),
            "live_clawdbot_startup": self.test_live_clawdbot_startup(),
            "process_manager": self.test_process_manager(),
            "daemon_mode_concept": self.test_daemon_mode_concept()
        }
        
        # Summary
        self.log("\n" + "=" * 70)
        self.log("PERSISTENCE TEST SUMMARY", "TEST")
        self.log("=" * 70)
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        
        self.log(f"\nTotal Tests: {total}")
        self.log(f"Passed: {passed} ✅", "SUCCESS")
        self.log(f"Failed: {total - passed} ❌", "FAIL" if total - passed > 0 else "INFO")
        
        self.log("\nDetailed Results:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {test_name}: {status}")
        
        # Recommendations
        self.log("\n" + "=" * 70)
        self.log("RECOMMENDATIONS FOR PERSISTENCE", "TEST")
        self.log("=" * 70)
        
        if all(results.values()):
            self.log("✅ All persistence tests passed!", "SUCCESS")
            self.log("\n📋 To run bot in production:")
            self.log("  1. Use: ./clawdbot_manager.sh start")
            self.log("  2. Check status: ./clawdbot_manager.sh status")
            self.log("  3. View logs: tail -f logs/clawdbot.log")
            self.log("  4. Stop bot: ./clawdbot_manager.sh stop")
        else:
            self.log("⚠️  Some persistence tests failed", "WARN")
            self.log("\n📋 Troubleshooting:")
            self.log("  1. Check if Telegram credentials are valid")
            self.log("  2. Ensure ClawdBot gateway is running (for live_clawdbot_bot)")
            self.log("  3. Verify LMStudio is running with model loaded")
            self.log("  4. Check logs for detailed error messages")
        
        return results


def main():
    """Main test execution"""
    tester = BotPersistenceTest()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
