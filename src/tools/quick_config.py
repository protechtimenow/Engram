#!/usr/bin/env python3
"""
===============================================================================
[Antigravity-Finance Quick Configuration]

Non-interactive setup with intelligent defaults.
Jobs-inspired: "It just works" configuration.
==============================================================================="""

import json
from pathlib import Path

def create_optimal_config():
    """Create optimal configuration for immediate deployment."""
    
    config = {
        "profile": "steve_jobs_mode",
        "dashboard_port": 8585,
        "reality_distortion": True,
        "insight_density": 10.0,
        
        "reddit_communities": [
            "r/Quant", "r/finance", "r/SecurityAnalysis", 
            "r/wallstreetbets", "r/personalfinance", "r/Economics",
            "r/stocks", "r/portfolios", "r/investing", 
            "r/ValueInvesting", "r/FluentInFinance"
        ],
        
        "sentiment_threshold": 0.3,
        "trend_detection": True,
        "auto_alerts": True,
        
        "spirit_guides": [
            {"name": "Market Oracle", "channel": "telegram", "personality": "wise"},
            {"name": "Trading Sage", "channel": "discord", "personality": "insightful"},
            {"name": "Risk Guardian", "channel": "slack", "personality": "cautious"},
            {"name": "Trend Seer", "channel": "web", "personality": "visionary"}
        ],
        
        "active_channels": ["telegram", "discord", "slack", "web"],
        "agent_personality": "wise",
        
        "processing_interval": 5,
        "max_insights_per_minute": 100,
        "background_processing": True,
        
        "enable_api": True,
        "api_port": 8000,
        "cors_enabled": True
    }
    
    # Save configuration
    config_file = Path("antigravity_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config

def show_configuration_status():
    """Show current configuration status."""
    
    config_file = Path("antigravity_config.json")
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print("🎯 Antigravity-Finance Configuration Status")
        print("=" * 50)
        print(f"Profile: {config['profile']}")
        print(f"Dashboard: http://localhost:{config['dashboard_port']}")
        print(f"API Server: http://localhost:{config['api_port']}")
        print(f"Reality Distortion: {'✅ ON' if config['reality_distortion'] else '❌ OFF'}")
        print(f"Auto Alerts: {'✅ ON' if config['auto_alerts'] else '❌ OFF'}")
        print(f"Background Processing: {'✅ ON' if config['background_processing'] else '❌ OFF'}")
        print(f"Reddit Communities: {len(config['reddit_communities'])}")
        print(f"Spirit Guides: {len(config['spirit_guides'])}")
        print(f"Active Channels: {len(config['active_channels'])}")
        
        # Show spirit guides
        print("\n🤖 Spirit Guides:")
        for guide in config['spirit_guides']:
            print(f"   {guide['name']} ({guide['channel']}) - {guide['personality']}")
        
        # Show active channels
        print("\n📡 Active Channels:")
        for channel in config['active_channels']:
            print(f"   {channel}")
        
        return config
    else:
        print("❌ Configuration file not found")
        return None

def validate_system():
    """Validate system readiness."""
    
    print("\n🔍 System Validation")
    print("=" * 30)
    
    checks = []
    
    # Check required files
    required_files = [
        "financial_data_manager.py",
        "clawdbot_integration.py", 
        "antigravity_finance.py"
    ]
    
    for file in required_files:
        if Path(file).exists():
            checks.append(f"✅ {file}")
        else:
            checks.append(f"❌ {file}")
    
    # Check directories
    if Path("clawdbot_repo").exists():
        checks.append("✅ Clawdbot repository")
    else:
        checks.append("⚠️  Clawdbot repository (optional)")
    
    # Check dependencies
    try:
        import fastapi
        checks.append("✅ FastAPI")
    except ImportError:
        checks.append("❌ FastAPI (pip install fastapi)")
    
    try:
        import uvicorn
        checks.append("✅ Uvicorn")
    except ImportError:
        checks.append("❌ Uvicorn (pip install uvicorn)")
    
    for check in checks:
        print(f"   {check}")
    
    return checks

def main():
    """Main configuration function."""
    
    print("🚀 Antigravity-Finance Quick Configuration")
    print("   (Jobs style: 'It just works')")
    print("=" * 50)
    
    # Create optimal configuration
    config = create_optimal_config()
    print("✅ Optimal configuration created")
    
    # Show status
    show_configuration_status()
    
    # Validate system
    checks = validate_system()
    
    # Provide next steps
    print("\n🎯 Next Steps:")
    print("1. Install missing dependencies if any:")
    print("   pip install fastapi uvicorn aiohttp")
    print()
    print("2. Start the system:")
    print("   python antigravity_finance.py")
    print()
    print("3. Access your dashboard:")
    print(f"   http://localhost:{config['dashboard_port']}")
    print()
    print("4. Access API endpoints:")
    print(f"   http://localhost:{config['api_port']}/api/engram/financial/sentiment")
    print()
    print("🎉 Configuration complete! Your system is ready to launch.")

if __name__ == "__main__":
    main()