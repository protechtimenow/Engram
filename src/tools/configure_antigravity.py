#!/usr/bin/env python3
"""
===============================================================================
[Antigravity-Finance Configuration Manager]

Steve Jobs-inspired configuration that makes complex setup feel simple.
One file to rule them all - no config hell, just elegant defaults.
===============================================================================
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class JobsInspiredConfig:
    """Jobs-inspired configuration - simple defaults, elegant customization."""
    
    # Core System Settings
    profile: str = "steve_jobs_mode"
    dashboard_port: int = 8585
    reality_distortion: bool = True
    insight_density: float = 10.0
    
    # Financial Settings
    reddit_communities: list = None
    sentiment_threshold: float = 0.3
    trend_detection: bool = True
    auto_alerts: bool = True
    
    # Agent Settings
    spirit_guides: list = None
    active_channels: list = None
    agent_personality: str = "wise"
    
    # Performance Settings
    processing_interval: int = 5  # seconds
    max_insights_per_minute: int = 100
    background_processing: bool = True
    
    # API Settings
    enable_api: bool = True
    api_port: int = 8000
    cors_enabled: bool = True
    
    def __post_init__(self):
        # Set intelligent defaults
        if self.reddit_communities is None:
            self.reddit_communities = [
                "r/Quant", "r/finance", "r/SecurityAnalysis", 
                "r/wallstreetbets", "r/personalfinance", "r/Economics",
                "r/stocks", "r/portfolios", "r/investing", 
                "r/ValueInvesting", "r/FluentInFinance"
            ]
        
        if self.spirit_guides is None:
            self.spirit_guides = [
                {"name": "Market Oracle", "channel": "telegram", "personality": "wise"},
                {"name": "Trading Sage", "channel": "discord", "personality": "insightful"},
                {"name": "Risk Guardian", "channel": "slack", "personality": "cautious"},
                {"name": "Trend Seer", "channel": "web", "personality": "visionary"}
            ]
        
        if self.active_channels is None:
            self.active_channels = ["telegram", "discord", "slack", "web"]

class ConfigurationManager:
    """
    Jobs-inspired configuration manager.
    Makes complex setup feel simple and intuitive.
    """
    
    def __init__(self, config_file: str = "antigravity_config.json"):
        self.config_file = Path(config_file)
        self.config = JobsInspiredConfig()
        
        # Load existing config or create defaults
        self._load_or_create_config()
    
    def _load_or_create_config(self):
        """Load existing config or create intelligent defaults."""
        if self.config_file.exists():
            self._load_config()
        else:
            self._create_default_config()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update config with loaded data
            for key, value in config_data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            print(f"✅ Configuration loaded from {self.config_file}")
            
        except Exception as e:
            print(f"⚠️  Error loading config: {str(e)}")
            print("🔄 Using default configuration")
    
    def _create_default_config(self):
        """Create default configuration file."""
        try:
            # Save default config
            self._save_config()
            
            print(f"✅ Default configuration created at {self.config_file}")
            print("📝 Edit the file to customize your setup")
            
        except Exception as e:
            print(f"⚠️  Error creating config file: {str(e)}")
    
    def _save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
                
        except Exception as e:
            print(f"❌ Error saving config: {str(e)}")
    
    def get_config(self) -> JobsInspiredConfig:
        """Get current configuration."""
        return self.config
    
    def update_config(self, **kwargs):
        """Update configuration with new values."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                print(f"✅ Updated {key}: {value}")
            else:
                print(f"⚠️  Unknown config key: {key}")
        
        # Save updated config
        self._save_config()
    
    def setup_interactive(self) -> JobsInspiredConfig:
        """Interactive setup - Jobs style: ask only what matters."""
        
        print("\n🎯 Antigravity-Finance Setup")
        print("   (Steve Jobs mode: simple questions, elegant results)")
        print("=" * 50)
        
        # Only ask the most important questions
        questions = [
            {
                'key': 'profile',
                'question': 'Choose your profile:',
                'options': ['steve_jobs_mode', 'minimal', 'advanced'],
                'default': 'steve_jobs_mode'
            },
            {
                'key': 'dashboard_port',
                'question': 'Dashboard port (default 8585):',
                'default': 8585
            },
            {
                'key': 'auto_alerts',
                'question': 'Enable automatic alerts? (y/n):',
                'default': True
            },
            {
                'key': 'background_processing',
                'question': 'Enable background processing? (y/n):',
                'default': True
            }
        ]
        
        for q in questions:
            if 'options' in q:
                print(f"\n{q['question']}")
                for i, option in enumerate(q['options'], 1):
                    print(f"  {i}. {option}")
                
                choice = input(f"   Choice (1-{len(q['options'])}, default {q['default']}): ").strip()
                
                if choice.isdigit() and 1 <= int(choice) <= len(q['options']):
                    value = q['options'][int(choice) - 1]
                else:
                    value = q['default']
            else:
                if q['key'] in ['auto_alerts', 'background_processing']:
                    response = input(f"{q['question']} ").strip().lower()
                    value = response in ['y', 'yes', 'true', '1']
                else:
                    response = input(f"{q['question']} ").strip()
                    value = type(q['default'])(response) if response else q['default']
            
            self.update_config(**{q['key']: value})
        
        print("\n✅ Setup complete!")
        return self.config
    
    def show_status(self):
        """Show current configuration status."""
        print("\n📊 Configuration Status")
        print("=" * 30)
        
        print(f"Profile: {self.config.profile}")
        print(f"Dashboard: http://localhost:{self.config.dashboard_port}")
        print(f"Reality Distortion: {'✅ ON' if self.config.reality_distortion else '❌ OFF'}")
        print(f"Auto Alerts: {'✅ ON' if self.config.auto_alerts else '❌ OFF'}")
        print(f"Background Processing: {'✅ ON' if self.config.background_processing else '❌ OFF'}")
        print(f"Reddit Communities: {len(self.config.reddit_communities)}")
        print(f"Spirit Guides: {len(self.config.spirit_guides)}")
        print(f"Active Channels: {len(self.config.active_channels)}")
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status."""
        issues = []
        warnings = []
        
        # Check ports
        if self.config.dashboard_port == self.config.api_port:
            issues.append("Dashboard and API ports conflict")
        
        # Check directories
        if not Path("clawdbot_repo").exists():
            warnings.append("Clawdbot repository not found - some features may be limited")
        
        # Check required files
        required_files = ["financial_data_manager.py", "clawdbot_integration.py"]
        for file in required_files:
            if not Path(file).exists():
                issues.append(f"Required file missing: {file}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'config_file': str(self.config_file)
        }

# Global configuration instance
config_manager = ConfigurationManager()

def get_config() -> JobsInspiredConfig:
    """Get global configuration instance."""
    return config_manager.get_config()

def setup_config() -> JobsInspiredConfig:
    """Run interactive setup."""
    return config_manager.setup_interactive()

if __name__ == "__main__":
    # Run configuration setup
    config = setup_config()
    config_manager.show_status()
    
    # Validate configuration
    validation = config_manager.validate_config()
    
    if validation['valid']:
        print("\n🎉 Configuration is valid and ready!")
        print("🚀 Run: python antigravity_finance.py")
    else:
        print("\n⚠️  Configuration issues found:")
        for issue in validation['issues']:
            print(f"   ❌ {issue}")
        
        if validation['warnings']:
            print("\n⚠️  Warnings:")
            for warning in validation['warnings']:
                print(f"   ⚠️  {warning}")