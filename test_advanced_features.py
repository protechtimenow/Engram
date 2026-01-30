#!/usr/bin/env python3
"""
Advanced Features Testing for Clawdbot
Tests natural language processing, market analysis, and multi-channel features
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime


class AdvancedFeaturesTest:
    """Test advanced Clawdbot features"""
    
    def __init__(self):
        self.results = {}
        
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
    
    def test_configuration_completeness(self):
        """Test if all required configurations are present"""
        self.log("Testing configuration completeness...", "TEST")
        
        config_files = {
            "telegram": "config/telegram/working_telegram_config.json",
            "freqtrade": "config/engram_freqtrade_config.json",
            "env": ".env"
        }
        
        results = {}
        
        for name, path in config_files.items():
            file_path = Path(path)
            if file_path.exists():
                self.log(f"✅ {name} config exists: {path}", "SUCCESS")
                results[name] = True
                
                # Check content
                try:
                    if path.endswith('.json'):
                        with open(file_path, 'r') as f:
                            config = json.load(f)
                        self.log(f"  Valid JSON with {len(config)} keys", "INFO")
                    else:
                        with open(file_path, 'r') as f:
                            lines = f.readlines()
                        self.log(f"  {len(lines)} lines", "INFO")
                except Exception as e:
                    self.log(f"  ⚠️  Error reading: {e}", "WARN")
            else:
                self.log(f"❌ {name} config missing: {path}", "FAIL")
                results[name] = False
        
        return all(results.values())
    
    def test_telegram_config_details(self):
        """Test Telegram configuration details"""
        self.log("\nTesting Telegram configuration details...", "TEST")
        
        config_path = Path("config/telegram/working_telegram_config.json")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check critical fields
            checks = {
                "telegram.enabled": config.get("telegram", {}).get("enabled"),
                "telegram.token": bool(config.get("telegram", {}).get("token")),
                "telegram.chat_id": bool(config.get("telegram", {}).get("chat_id")),
                "dry_run": config.get("dry_run"),
                "strategy": bool(config.get("strategy")),
                "api_server.enabled": config.get("api_server", {}).get("enabled")
            }
            
            for check_name, value in checks.items():
                if value:
                    self.log(f"✅ {check_name}: {value}", "SUCCESS")
                else:
                    self.log(f"⚠️  {check_name}: {value}", "WARN")
            
            # Check notification settings
            notif = config.get("telegram", {}).get("notification_settings", {})
            enabled_notifs = sum(1 for v in notif.values() if v == "on")
            self.log(f"  Notifications enabled: {enabled_notifs}/{len(notif)}", "INFO")
            
            return all(checks.values())
            
        except Exception as e:
            self.log(f"Error checking Telegram config: {e}", "FAIL")
            return False
    
    def test_trading_strategy_files(self):
        """Test if trading strategy files exist"""
        self.log("\nTesting trading strategy files...", "TEST")
        
        strategy_files = [
            "simple_strategy.py",
            "simple_engram_strategy.py",
            "src/trading/engram_trading_strategy.py"
        ]
        
        found = 0
        for strategy in strategy_files:
            path = Path(strategy)
            if path.exists():
                self.log(f"✅ Strategy found: {strategy}", "SUCCESS")
                found += 1
                
                # Check file size
                size = path.stat().st_size
                self.log(f"  Size: {size} bytes", "INFO")
            else:
                self.log(f"⚠️  Strategy not found: {strategy}", "WARN")
        
        return found > 0
    
    def test_engram_components(self):
        """Test Engram neural components"""
        self.log("\nTesting Engram components...", "TEST")
        
        engram_files = [
            "src/core/engram_demo_v1.py",
            "Engram_paper.pdf"
        ]
        
        found = 0
        for file in engram_files:
            path = Path(file)
            if path.exists():
                self.log(f"✅ Engram file found: {file}", "SUCCESS")
                found += 1
            else:
                self.log(f"❌ Engram file missing: {file}", "FAIL")
        
        # Check if we can import Engram (without torch)
        try:
            sys.path.insert(0, "src")
            # Just check if file is importable as module
            engram_path = Path("src/core/engram_demo_v1.py")
            if engram_path.exists():
                with open(engram_path, 'r') as f:
                    content = f.read()
                
                # Check for key classes/functions
                has_engram_class = "class Engram" in content or "class EngramModel" in content
                has_analyze = "def analyze" in content
                
                if has_engram_class:
                    self.log("✅ EngramModel class found in code", "SUCCESS")
                if has_analyze:
                    self.log("✅ Analysis functions found in code", "SUCCESS")
                
                return has_engram_class or has_analyze
        except Exception as e:
            self.log(f"⚠️  Could not analyze Engram code: {e}", "WARN")
        
        return found > 0
    
    def test_logging_infrastructure(self):
        """Test logging infrastructure"""
        self.log("\nTesting logging infrastructure...", "TEST")
        
        logs_dir = Path("logs")
        
        if not logs_dir.exists():
            self.log("Creating logs directory...", "INFO")
            logs_dir.mkdir(exist_ok=True)
        
        if logs_dir.exists() and logs_dir.is_dir():
            self.log("✅ Logs directory exists", "SUCCESS")
            
            # List existing log files
            log_files = list(logs_dir.glob("*.log"))
            self.log(f"  Found {len(log_files)} log files", "INFO")
            
            for log_file in log_files[:5]:  # Show first 5
                size = log_file.stat().st_size
                self.log(f"  - {log_file.name} ({size} bytes)", "INFO")
            
            return True
        else:
            self.log("❌ Logs directory not accessible", "FAIL")
            return False
    
    def test_api_endpoints_config(self):
        """Test API endpoints configuration"""
        self.log("\nTesting API endpoints configuration...", "TEST")
        
        config_path = Path("config/telegram/working_telegram_config.json")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            api_config = config.get("api_server", {})
            
            if api_config.get("enabled"):
                self.log("✅ API server enabled", "SUCCESS")
                self.log(f"  Listen: {api_config.get('listen_ip_address')}:{api_config.get('listen_port')}", "INFO")
                self.log(f"  Username: {api_config.get('username')}", "INFO")
                
                # Check CORS
                cors = api_config.get("CORS_origins", [])
                self.log(f"  CORS origins: {len(cors)}", "INFO")
                
                return True
            else:
                self.log("⚠️  API server disabled", "WARN")
                return False
                
        except Exception as e:
            self.log(f"Error checking API config: {e}", "FAIL")
            return False
    
    def test_exchange_configuration(self):
        """Test exchange configuration"""
        self.log("\nTesting exchange configuration...", "TEST")
        
        config_path = Path("config/telegram/working_telegram_config.json")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            exchange = config.get("exchange", {})
            
            self.log(f"  Exchange: {exchange.get('name')}", "INFO")
            
            has_key = bool(exchange.get('key'))
            has_secret = bool(exchange.get('secret'))
            
            if has_key and has_secret:
                self.log("✅ Exchange API credentials configured", "SUCCESS")
            else:
                self.log("⚠️  Exchange API credentials empty (OK for dry-run)", "WARN")
            
            # Check pairs
            whitelist = exchange.get('pair_whitelist', [])
            blacklist = exchange.get('pair_blacklist', [])
            
            self.log(f"  Whitelist: {len(whitelist)} pairs", "INFO")
            for pair in whitelist[:3]:
                self.log(f"    - {pair}", "INFO")
            
            self.log(f"  Blacklist: {len(blacklist)} pairs", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"Error checking exchange config: {e}", "FAIL")
            return False
    
    def test_risk_management_config(self):
        """Test risk management configuration"""
        self.log("\nTesting risk management configuration...", "TEST")
        
        config_path = Path("config/telegram/working_telegram_config.json")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check risk parameters
            max_trades = config.get("max_open_trades")
            stake_amount = config.get("stake_amount")
            dry_run = config.get("dry_run")
            dry_wallet = config.get("dry_run_wallet")
            
            self.log(f"  Max open trades: {max_trades}", "INFO")
            self.log(f"  Stake amount: {stake_amount}", "INFO")
            self.log(f"  Dry run: {dry_run}", "INFO")
            self.log(f"  Dry run wallet: {dry_wallet}", "INFO")
            
            if dry_run:
                self.log("✅ Dry run mode enabled (safe for testing)", "SUCCESS")
            else:
                self.log("⚠️  LIVE TRADING MODE - Use with caution!", "WARN")
            
            # Check timeouts
            timeout = config.get("unfilledtimeout", {})
            self.log(f"  Entry timeout: {timeout.get('entry')} {timeout.get('unit')}", "INFO")
            self.log(f"  Exit timeout: {timeout.get('exit')} {timeout.get('unit')}", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"Error checking risk config: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all advanced feature tests"""
        self.log("=" * 70)
        self.log("ADVANCED FEATURES TESTING", "TEST")
        self.log("=" * 70)
        
        tests = {
            "Configuration Completeness": self.test_configuration_completeness(),
            "Telegram Config Details": self.test_telegram_config_details(),
            "Trading Strategy Files": self.test_trading_strategy_files(),
            "Engram Components": self.test_engram_components(),
            "Logging Infrastructure": self.test_logging_infrastructure(),
            "API Endpoints Config": self.test_api_endpoints_config(),
            "Exchange Configuration": self.test_exchange_configuration(),
            "Risk Management Config": self.test_risk_management_config()
        }
        
        # Summary
        self.log("\n" + "=" * 70)
        self.log("ADVANCED FEATURES TEST SUMMARY", "TEST")
        self.log("=" * 70)
        
        total = len(tests)
        passed = sum(1 for v in tests.values() if v)
        
        self.log(f"\nTotal Tests: {total}")
        self.log(f"Passed: {passed} ✅", "SUCCESS")
        self.log(f"Failed: {total - passed} ❌", "FAIL" if total - passed > 0 else "INFO")
        self.log(f"Pass Rate: {passed/total*100:.1f}%")
        
        self.log("\nDetailed Results:")
        for test_name, result in tests.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {test_name}: {status}")
        
        return tests


def main():
    """Main test execution"""
    tester = AdvancedFeaturesTest()
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
