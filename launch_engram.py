#!/usr/bin/env python3
"""
Engram + ClawdBot Unified Launcher
==================================

Launches the complete Engram trading system with ClawdBot gateway integration.

Usage:
    python launch_engram.py
    python launch_engram.py --mode gateway-only
    python launch_engram.py --mode engram-only
    python launch_engram.py --config custom_config.json

Components:
    1. ClawdBot Gateway (port 18789) - WebSocket API for Telegram/control
    2. LMStudio Proxy (port 17502) - OpenAI-compatible API proxy
    3. Engram Agent - Connects to ClawdBot, handles trading analysis

Model Configuration:
    Models are configured through ClawdBot gateway and selected via:
    - Environment variable: ENGRAM_MODEL
    - Config file: config/engram_config.json
    - Telegram command: /model <model_name>
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EngramLauncher:
    """Unified launcher for Engram + ClawdBot system"""
    
    def __init__(self, config_path: str = "config/engram_config.json"):
        self.config = self._load_config(config_path)
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = False
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "lmstudio": {
                "host": "localhost",
                "port": 1234,
                "model": "glm-4.7-flash"
            },
            "clawdbot": {
                "host": "localhost",
                "port": 18789,
                "token": ""
            },
            "models": {
                "available": [
                    "glm-4.7-flash",
                    "openai/gpt-oss-20b",
                    "deepseek/deepseek-r1-0528-qwen3-8b"
                ],
                "default": "glm-4.7-flash"
            }
        }
    
    def check_port(self, port: int) -> bool:
        """Check if a port is already in use"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0  # Port is in use
        except:
            return False
    
    async def start_lmstudio_proxy(self) -> bool:
        """Start LMStudio proxy on port 17502"""
        if self.check_port(17502):
            logger.info("[OK] LMStudio proxy already running on port 17502")
            return True
        
        logger.info("[*] Starting LMStudio proxy on port 17502...")
        
        # Check if lmstudio_proxy.py exists
        proxy_script = Path("lmstudio_proxy.py")
        if not proxy_script.exists():
            logger.error("[ERROR] lmstudio_proxy.py not found")
            return False
        
        try:
            process = subprocess.Popen(
                [sys.executable, str(proxy_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            self.processes['lmstudio_proxy'] = process
            
            # Wait for it to start
            for i in range(10):
                await asyncio.sleep(0.5)
                if self.check_port(17502):
                    logger.info("[OK] LMStudio proxy started on port 17502")
                    return True
            
            logger.error("[ERROR] LMStudio proxy failed to start")
            return False
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to start LMStudio proxy: {e}")
            return False
    
    async def start_clawdbot_gateway(self) -> bool:
        """Start ClawdBot gateway on port 18789"""
        if self.check_port(18789):
            logger.info("[OK] ClawdBot gateway already running on port 18789")
            return True
        
        logger.info("[*] Starting ClawdBot gateway on port 18789...")
        logger.info("[!] ClawdBot gateway needs to be started manually or is external")
        logger.info("    Expected: ws://localhost:18789")
        
        # For now, assume it's external or manual start
        # You can add auto-start logic here if you have the ClawdBot executable
        return True
    
    async def start_engram_agent(self) -> bool:
        """Start Engram agent"""
        logger.info("[*] Starting Engram agent...")
        
        try:
            # Import and run the agent
            from agents.engram_agent import EngramAgent
            
            agent_config = {
                "lmstudio_host": self.config.get("lmstudio", {}).get("host", "localhost"),
                "lmstudio_port": self.config.get("lmstudio", {}).get("port", 1234),
                "model": os.getenv("ENGRAM_MODEL", self.config.get("lmstudio", {}).get("model", "glm-4.7-flash")),
                "clawdbot_host": self.config.get("clawdbot", {}).get("host", "localhost"),
                "clawdbot_port": self.config.get("clawdbot", {}).get("port", 18789),
                "clawdbot_token": self.config.get("clawdbot", {}).get("token", ""),
                "response_format": "clean"
            }
            
            self.agent = EngramAgent(agent_config)
            
            # Run the agent
            await self.agent.run()
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to start Engram agent: {e}")
            return False
    
    async def run(self, mode: str = "full"):
        """Run the launcher"""
        logger.info("=" * 60)
        logger.info("Engram + ClawdBot Unified Launcher")
        logger.info("=" * 60)
        
        self.running = True
        
        if mode in ["full", "gateway-only"]:
            # Start LMStudio proxy
            if not await self.start_lmstudio_proxy():
                logger.error("[ERROR] Failed to start LMStudio proxy")
                if mode == "gateway-only":
                    return
            
            # Start ClawdBot gateway (or check if running)
            if not await self.start_clawdbot_gateway():
                logger.error("[ERROR] ClawdBot gateway not available")
        
        if mode in ["full", "engram-only"]:
            # Start Engram agent
            await self.start_engram_agent()
    
    def shutdown(self):
        """Shutdown all processes"""
        logger.info("[*] Shutting down...")
        self.running = False
        
        for name, process in self.processes.items():
            logger.info(f"[*] Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        logger.info("[OK] Shutdown complete")


def print_status():
    """Print current system status"""
    import socket
    
    def check_port(port: int) -> str:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return "[RUNNING]" if result == 0 else "[STOPPED]"
        except:
            return "[UNKNOWN]"
    
    print("\n" + "=" * 60)
    print("Engram System Status")
    print("=" * 60)
    print(f"LMStudio Direct (1234):    {check_port(1234)}")
    print(f"LMStudio Proxy (17502):    {check_port(17502)}")
    print(f"ClawdBot Gateway (18789):  {check_port(18789)}")
    print("=" * 60)
    print("\nAvailable Models (from config):")
    
    try:
        with open("config/engram_config.json", 'r') as f:
            config = json.load(f)
            models = config.get("models", {}).get("available", ["glm-4.7-flash"])
            default = config.get("models", {}).get("default", "glm-4.7-flash")
            for model in models:
                marker = " [DEFAULT]" if model == default else ""
                print(f"  - {model}{marker}")
    except:
        print("  - glm-4.7-flash [DEFAULT]")
    
    print("\nEnvironment:")
    print(f"  ENGRAM_MODEL={os.getenv('ENGRAM_MODEL', 'not set')}")
    print(f"  OPENROUTER_API_KEY={'set' if os.getenv('OPENROUTER_API_KEY') else 'not set'}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Engram + ClawdBot Unified Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python launch_engram.py --status          Check system status
    python launch_engram.py                   Launch full system
    python launch_engram.py --mode engram-only  Launch only Engram agent
        """
    )
    
    parser.add_argument("--mode", choices=["full", "gateway-only", "engram-only"],
                       default="full", help="Launch mode")
    parser.add_argument("--config", default="config/engram_config.json",
                       help="Configuration file path")
    parser.add_argument("--status", action="store_true",
                       help="Show system status and exit")
    parser.add_argument("--model", help="Override model (e.g., glm-4.7-flash)")
    
    args = parser.parse_args()
    
    if args.status:
        print_status()
        return
    
    if args.model:
        os.environ["ENGRAM_MODEL"] = args.model
        logger.info(f"[OK] Model overridden: {args.model}")
    
    launcher = EngramLauncher(args.config)
    
    try:
        asyncio.run(launcher.run(args.mode))
    except KeyboardInterrupt:
        logger.info("\n[!] Interrupted by user")
    finally:
        launcher.shutdown()


if __name__ == "__main__":
    main()
