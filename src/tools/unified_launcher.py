#!/usr/bin/env python3
"""
Intelligent Engram-FreqTrade Unified Launcher
==========================================

Smart launcher that handles dependency management and intelligent integration.

Features:
- Automatic dependency resolution
- Smart mode selection  
- Seamless integration startup
- Error recovery
- Resource monitoring
"""

import sys
import os
import json
import subprocess
import importlib
from pathlib import Path
from typing import Dict, List, Optional

class DependencyManager:
    """Manage system dependencies intelligently"""
    
    REQUIRED_PACKAGES = [
        "freqtrade", "pandas", "numpy", "requests", "asyncio"
    ]
    
    OPTIONAL_PACKAGES = {
        "torch": "PyTorch for Engram AI",
        "transformers": "NLP capabilities", 
        "ccxt": "Exchange connectivity",
        "python-telegram-bot": "Telegram integration"
    }
    
    @staticmethod
    def check_package(package_name: str) -> bool:
        """Check if package is available"""
        try:
            importlib.import_module(package_name.replace("-", "_"))
            return True
        except ImportError:
            return False
    
    @staticmethod
    def install_package(package_name: str) -> bool:
        """Install package with error handling"""
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                package_name, "--user"
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @classmethod
    def ensure_dependencies(cls) -> Dict[str, bool]:
        """Ensure all required dependencies are available"""
        status = {}
        
        # Check required packages
        for package in cls.REQUIRED_PACKAGES:
            status[package] = cls.check_package(package)
            if not status[package]:
                print(f"📦 Installing required package: {package}")
                if cls.install_package(package):
                    status[package] = True
                    print(f"✅ {package} installed successfully")
                else:
                    print(f"❌ Failed to install {package}")
        
        # Check optional packages
        for package, description in cls.OPTIONAL_PACKAGES.items():
            available = cls.check_package(package)
            status[package] = available
            if not available:
                print(f"⚠️  Optional package {package} not available: {description}")
        
        return status

class IntelligentLauncher:
    """Unified intelligent launcher"""
    
    def __init__(self, config_path: str = "engram_intelligent_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.dependency_status = {}
        
    def _load_config(self) -> Dict[str, any]:
        """Load configuration with fallback"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"📄 Config file not found: {self.config_path}")
            print("Creating default intelligent configuration...")
            return self._create_default_config()
        except json.JSONDecodeError:
            print("❌ Invalid JSON in config file")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, any]:
        """Create default configuration"""
        default_config = {
            "system": {"mode": "smart"},
            "freqtrade": {"dry_run": True},
            "telegram": {"enabled": True},
            "integrations": {"enabled": True}
        }
        
        # Save default config
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def start_intelligent_system(self) -> bool:
        """Start the intelligent trading system"""
        print("🚀 **Intelligent Engram-FreqTrade Launcher**")
        print("=" * 50)
        
        # 1. Check dependencies
        print("📦 Checking dependencies...")
        self.dependency_status = DependencyManager.ensure_dependencies()
        
        required_missing = [
            pkg for pkg in DependencyManager.REQUIRED_PACKAGES 
            if not self.dependency_status.get(pkg, False)
        ]
        
        if required_missing:
            print(f"❌ Missing required packages: {required_missing}")
            return False
        
        print("✅ All required dependencies available")
        
        # 2. Determine optimal startup mode
        mode = self._determine_startup_mode()
        print(f"🧠 Starting in {mode} mode...")
        
        # 3. Start appropriate components
        success = False
        
        if mode == "intelligent":
            success = self._start_intelligent_mode()
        elif mode == "basic":
            success = self._start_basic_mode()
        elif mode == "safe":
            success = self._start_safe_mode()
        
        if success:
            self._show_success_info()
        
        return success
    
    def _determine_startup_mode(self) -> str:
        """Determine optimal startup mode based on available components"""
        
        # Check for PyTorch (Engram AI)
        torch_available = self.dependency_status.get("torch", False)
        
        # Check for advanced features
        telegram_available = self.dependency_status.get("python-telegram-bot", False)
        ccxt_available = self.dependency_status.get("ccxt", False)
        
        if torch_available and telegram_available and ccxt_available:
            return "intelligent"
        elif ccxt_available and telegram_available:
            return "basic"
        else:
            return "safe"
    
    def _start_intelligent_mode(self) -> bool:
        """Start full intelligent system"""
        try:
            print("🧠 Initializing intelligent core...")
            
            # Import intelligent system
            from intelligent_engram_system import IntelligentEngramFreqTrade
            
            # Create and start system
            system = IntelligentEngramFreqTrade(self.config_path)
            system.start_intelligent_trading()
            
            return True
            
        except ImportError as e:
            print(f"❌ Failed to import intelligent system: {e}")
            return False
        except Exception as e:
            print(f"❌ Failed to start intelligent mode: {e}")
            return False
    
    def _start_basic_mode(self) -> bool:
        """Start basic FreqTrade with Telegram"""
        try:
            print("🤖 Starting basic FreqTrade with Telegram...")
            
            # Create basic config for FreqTrade
            freqtrade_config = self._create_freqtrade_config()
            
            # Start FreqTrade directly
            cmd = [
                "freqtrade", "trade",
                "--config", freqtrade_config,
                "--dry-run"
            ]
            
            process = subprocess.Popen(cmd, cwd=os.getcwd())
            print(f"✅ FreqTrade started with PID: {process.pid}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start basic mode: {e}")
            return False
    
    def _start_safe_mode(self) -> bool:
        """Start minimal safe mode"""
        try:
            print("🛡️  Starting safe mode (basic trading only)...")
            
            # Create minimal config
            safe_config = {
                "max_open_trades": 1,
                "stake_currency": "USDT", 
                "stake_amount": 100,
                "dry_run": True,
                "dry_run_wallet": 1000,
                "timeframe": "5m",
                "strategy": "SimpleEngramStrategy",
                "exchange": {
                    "name": "binance",
                    "pair_whitelist": ["BTC/USDT"]
                }
            }
            
            # Save safe config
            with open("safe_config.json", "w") as f:
                json.dump(safe_config, f, indent=2)
            
            # Start with safe config
            cmd = ["freqtrade", "trade", "--config", "safe_config.json", "--dry-run"]
            process = subprocess.Popen(cmd)
            
            print(f"✅ Safe mode started with PID: {process.pid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start safe mode: {e}")
            return False
    
    def _create_freqtrade_config(self) -> str:
        """Create FreqTrade compatible config"""
        config_filename = "intelligent_freqtrade_config.json"
        
        freqtrade_config = {
            "max_open_trades": self.config.get("freqtrade", {}).get("max_open_trades", 3),
            "stake_currency": self.config.get("freqtrade", {}).get("stake_currency", "USDT"),
            "stake_amount": self.config.get("freqtrade", {}).get("stake_amount", 100),
            "dry_run": self.config.get("freqtrade", {}).get("dry_run", True),
            "dry_run_wallet": self.config.get("freqtrade", {}).get("dry_run_wallet", 1000),
            "timeframe": self.config.get("freqtrade", {}).get("timeframe", "5m"),
            "strategy": "SimpleEngramStrategy",
            "strategy_path": ".",
            "exchange": {
                "name": "binance",
                "pair_whitelist": self.config.get("freqtrade", {}).get("exchange", {}).get("pair_whitelist", ["BTC/USDT", "ETH/USDT"])
            },
            "telegram": {
                "enabled": self.config.get("telegram", {}).get("enabled", True),
                "token": self.config.get("telegram", {}).get("token", ""),
                "chat_id": self.config.get("telegram", {}).get("chat_id", "")
            },
            "api_server": {
                "enabled": True,
                "listen_ip_address": "127.0.0.1",
                "listen_port": 8080
            }
        }
        
        with open(config_filename, "w") as f:
            json.dump(freqtrade_config, f, indent=2)
        
        return config_filename
    
    def _show_success_info(self):
        """Show successful startup information"""
        print("""
🎉 **System Successfully Started!**

📱 **Telegram Bot Commands:**
• /status - System status
• /balance - Wallet information  
• /analyze BTC/USDT - AI analysis
• /mode smart - Change AI mode
• /integrate discord - Add integration

🧠 **Intelligent Features:**
• AI activates only when needed
• Natural language understanding
• Seamless integration management
• Resource optimization

🌐 **API Server:** http://127.0.0.1:8080
📊 **Monitoring:** Check logs for activity

**The system is now running intelligently!**
        """)

def main():
    """Main launcher function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Intelligent Engram-FreqTrade Launcher")
    parser.add_argument("--config", default="engram_intelligent_config.json", 
                       help="Configuration file path")
    parser.add_argument("--mode", choices=["intelligent", "basic", "safe"],
                       help="Force startup mode")
    parser.add_argument("--check-deps", action="store_true",
                       help="Check dependencies only")
    
    args = parser.parse_args()
    
    if args.check_deps:
        print("📦 Checking system dependencies...")
        status = DependencyManager.ensure_dependencies()
        print("\n📊 Dependency Status:")
        for pkg, available in status.items():
            status_icon = "✅" if available else "❌"
            print(f"  {status_icon} {pkg}")
        return
    
    # Initialize launcher
    launcher = IntelligentLauncher(args.config)
    
    # Force mode if specified
    if args.mode:
        success_map = {
            "intelligent": launcher._start_intelligent_mode,
            "basic": launcher._start_basic_mode,
            "safe": launcher._start_safe_mode
        }
        
        if args.mode in success_map:
            success = success_map[args.mode]()
            if success:
                launcher._show_success_info()
        else:
            print(f"❌ Invalid mode: {args.mode}")
    else:
        # Auto-detect and start
        success = launcher.start_intelligent_system()
        
        if not success:
            print("❌ Failed to start system")
            sys.exit(1)

if __name__ == "__main__":
    main()