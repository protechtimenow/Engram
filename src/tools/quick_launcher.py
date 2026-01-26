#!/usr/bin/env python3
"""
Engram-FreqTrade Quick Launcher
===============================

Simplified launcher that checks system status and provides guidance.
"""

import sys
import os
import json
import subprocess
import argparse

def run_cmd(cmd):
    """Run command and return result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_freqtrade_config(config_path):
    """Check if FreqTrade config is valid."""
    success, output, error = run_cmd(f"freqtrade create-userdir --userdir user_data")
    if not success:
        # Directory might already exist, that's ok
        pass
    
    # Try to validate config
    success, output, error = run_cmd(f"freqtrade config --config {config_path}")
    return success, output, error

def start_freqtrade_dryrun(config_path):
    """Start FreqTrade in dry run mode."""
    print("🚀 Starting FreqTrade in dry run mode...")
    cmd = f"freqtrade trade --config {config_path} --dry-run"
    
    print(f"📝 Command: {cmd}")
    print("⚠️  This will start the trading bot in simulation mode")
    print("   Press Ctrl+C to stop")
    
    try:
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n⏹️  Trading stopped by user")
        return True

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(description='Engram-FreqTrade Launcher')
    parser.add_argument('--config', default='engram_freqtrade_config.json', 
                       help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run in dry run mode (simulation)')
    parser.add_argument('--status', action='store_true',
                       help='Check system status')
    parser.add_argument('--validate-config', action='store_true',
                       help='Validate configuration file')
    
    args = parser.parse_args()
    
    config_path = args.config
    
    if args.status:
        print("🔍 Checking system status...")
        success, output, error = run_cmd("python status_check.py")
        if success:
            print(output)
        else:
            print(f"❌ Status check failed: {error}")
        return
    
    if args.validate_config:
        print(f"🔍 Validating config: {config_path}")
        if not os.path.exists(config_path):
            print(f"❌ Config file not found: {config_path}")
            return
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print("✅ Config file is valid JSON")
            
            success, output, error = check_freqtrade_config(config_path)
            if success:
                print("✅ FreqTrade config validation passed")
            else:
                print(f"⚠️  FreqTrade validation: {error}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config: {e}")
        return
    
    if args.dry_run:
        if not os.path.exists(config_path):
            print(f"❌ Config file not found: {config_path}")
            return
        
        print("🚀 Engram-FreqTrade Launcher")
        print("=" * 40)
        print(f"📋 Config: {config_path}")
        print("🎮 Mode: Dry Run (Simulation)")
        
        start_freqtrade_dryrun(config_path)
    else:
        print("🚀 Engram-FreqTrade Launcher")
        print("=" * 40)
        print("📋 Available options:")
        print("  --status          Check system status")
        print("  --validate-config Validate configuration")
        print("  --dry-run         Start simulation trading")
        print("  --config FILE     Use custom config file")
        print()
        print("📝 Example usage:")
        print("  python quick_launcher.py --status")
        print("  python quick_launcher.py --validate-config")
        print("  python quick_launcher.py --dry-run")

if __name__ == "__main__":
    main()