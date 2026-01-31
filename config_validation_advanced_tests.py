#!/usr/bin/env python3
"""
Comprehensive Configuration Validation and Advanced Edge Case Tests
Tests: Config validation, schema checking, environment variables, edge cases
"""

import json
import logging
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConfigValidationAdvancedTests:
    """Comprehensive configuration validation and edge case test suite"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        
    def log_test(self, name: str, passed: bool, duration: float, details: str = ""):
        """Log test result"""
        result = {
            "name": name,
            "passed": passed,
            "duration_ms": round(duration * 1000, 2),
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {name} ({duration*1000:.2f}ms)")
        if details:
            logger.info(f"  Details: {details}")
    
    def test_config_schema_validation(self) -> bool:
        """Test configuration schema validation"""
        start = time.time()
        try:
            class ConfigValidator:
                @staticmethod
                def validate_schema(config: dict, schema: dict) -> tuple[bool, str]:
                    """Validate config against schema"""
                    for key, rules in schema.items():
                        # Check required fields
                        if rules.get('required', False) and key not in config:
                            return False, f"Missing required field: {key}"
                        
                        if key in config:
                            value = config[key]
                            
                            # Check type
                            expected_type = rules.get('type')
                            if expected_type and not isinstance(value, expected_type):
                                return False, f"Field {key} has wrong type: expected {expected_type.__name__}"
                            
                            # Check min/max for numbers
                            if isinstance(value, (int, float)):
                                if 'min' in rules and value < rules['min']:
                                    return False, f"Field {key} below minimum: {value} < {rules['min']}"
                                if 'max' in rules and value > rules['max']:
                                    return False, f"Field {key} above maximum: {value} > {rules['max']}"
                            
                            # Check allowed values
                            if 'allowed' in rules and value not in rules['allowed']:
                                return False, f"Field {key} has invalid value: {value}"
                    
                    return True, "Valid"
            
            # Define schema
            schema = {
                'max_trades': {'type': int, 'required': True, 'min': 1, 'max': 100},
                'risk_level': {'type': str, 'required': True, 'allowed': ['low', 'medium', 'high']},
                'stop_loss': {'type': float, 'required': False, 'min': 0.0, 'max': 1.0}
            }
            
            # Valid config
            valid_config = {
                'max_trades': 5,
                'risk_level': 'medium',
                'stop_loss': 0.05
            }
            
            is_valid, msg = ConfigValidator.validate_schema(valid_config, schema)
            if not is_valid:
                self.log_test("Config Schema Validation", False, time.time() - start,
                            f"Valid config rejected: {msg}")
                return False
            
            # Invalid configs
            invalid_configs = [
                ({'risk_level': 'medium'}, "Missing max_trades"),
                ({'max_trades': 5, 'risk_level': 'invalid'}, "Invalid risk_level"),
                ({'max_trades': 0, 'risk_level': 'low'}, "max_trades below min"),
                ({'max_trades': 200, 'risk_level': 'low'}, "max_trades above max"),
            ]
            
            for config, expected_error in invalid_configs:
                is_valid, msg = ConfigValidator.validate_schema(config, schema)
                if is_valid:
                    self.log_test("Config Schema Validation", False, time.time() - start,
                                f"Invalid config accepted: {config}")
                    return False
            
            self.log_test("Config Schema Validation", True, time.time() - start,
                        f"Validated 1 valid and {len(invalid_configs)} invalid configs")
            return True
            
        except Exception as e:
            self.log_test("Config Schema Validation", False, time.time() - start, str(e))
            return False
    
    def test_environment_variable_override(self) -> bool:
        """Test environment variable configuration override"""
        start = time.time()
        try:
            class ConfigManager:
                def __init__(self, defaults: dict):
                    self.config = defaults.copy()
                
                def load_from_env(self, env_mapping: dict):
                    """Load config from environment variables"""
                    for config_key, env_var in env_mapping.items():
                        value = os.environ.get(env_var)
                        if value is not None:
                            # Try to convert to appropriate type
                            if value.isdigit():
                                self.config[config_key] = int(value)
                            elif value.replace('.', '').isdigit():
                                self.config[config_key] = float(value)
                            elif value.lower() in ['true', 'false']:
                                self.config[config_key] = value.lower() == 'true'
                            else:
                                self.config[config_key] = value
                
                def get(self, key: str, default=None):
                    return self.config.get(key, default)
            
            # Set environment variables
            os.environ['TEST_MAX_TRADES'] = '10'
            os.environ['TEST_RISK_LEVEL'] = 'high'
            os.environ['TEST_DRY_RUN'] = 'true'
            
            # Create config with defaults
            defaults = {
                'max_trades': 5,
                'risk_level': 'low',
                'dry_run': False
            }
            
            manager = ConfigManager(defaults)
            
            # Load from environment
            env_mapping = {
                'max_trades': 'TEST_MAX_TRADES',
                'risk_level': 'TEST_RISK_LEVEL',
                'dry_run': 'TEST_DRY_RUN'
            }
            
            manager.load_from_env(env_mapping)
            
            # Verify overrides
            if manager.get('max_trades') != 10:
                self.log_test("Environment Variable Override", False, time.time() - start,
                            f"max_trades not overridden: {manager.get('max_trades')}")
                return False
            
            if manager.get('risk_level') != 'high':
                self.log_test("Environment Variable Override", False, time.time() - start,
                            "risk_level not overridden")
                return False
            
            if manager.get('dry_run') != True:
                self.log_test("Environment Variable Override", False, time.time() - start,
                            "dry_run not overridden")
                return False
            
            # Cleanup
            del os.environ['TEST_MAX_TRADES']
            del os.environ['TEST_RISK_LEVEL']
            del os.environ['TEST_DRY_RUN']
            
            self.log_test("Environment Variable Override", True, time.time() - start,
                        "3 config values overridden from environment")
            return True
            
        except Exception as e:
            self.log_test("Environment Variable Override", False, time.time() - start, str(e))
            return False
    
    def test_config_merge_strategy(self) -> bool:
        """Test configuration merging from multiple sources"""
        start = time.time()
        try:
            def deep_merge(base: dict, override: dict) -> dict:
                """Deep merge two dictionaries"""
                result = base.copy()
                for key, value in override.items():
                    if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = deep_merge(result[key], value)
                    else:
                        result[key] = value
                return result
            
            # Base config
            base_config = {
                'trading': {
                    'max_trades': 5,
                    'risk_level': 'low'
                },
                'telegram': {
                    'enabled': True,
                    'chat_id': '123456'
                }
            }
            
            # User config (override)
            user_config = {
                'trading': {
                    'max_trades': 10  # Override
                },
                'telegram': {
                    'notifications': True  # Add new field
                }
            }
            
            # Merge
            merged = deep_merge(base_config, user_config)
            
            # Verify merge
            if merged['trading']['max_trades'] != 10:
                self.log_test("Config Merge Strategy", False, time.time() - start,
                            "max_trades not overridden")
                return False
            
            if merged['trading']['risk_level'] != 'low':
                self.log_test("Config Merge Strategy", False, time.time() - start,
                            "risk_level was lost")
                return False
            
            if not merged['telegram'].get('notifications'):
                self.log_test("Config Merge Strategy", False, time.time() - start,
                            "New field not added")
                return False
            
            if merged['telegram']['chat_id'] != '123456':
                self.log_test("Config Merge Strategy", False, time.time() - start,
                            "Existing field was lost")
                return False
            
            self.log_test("Config Merge Strategy", True, time.time() - start,
                        "Deep merge successful (2 levels, 5 fields)")
            return True
            
        except Exception as e:
            self.log_test("Config Merge Strategy", False, time.time() - start, str(e))
            return False
    
    def test_config_hot_reload(self) -> bool:
        """Test configuration hot reload without restart"""
        start = time.time()
        try:
            import tempfile
            
            class HotReloadConfig:
                def __init__(self, config_file: Path):
                    self.config_file = config_file
                    self.config = {}
                    self.last_modified = 0
                    self.reload_count = 0
                
                def load(self):
                    """Load config from file"""
                    if self.config_file.exists():
                        with open(self.config_file, 'r') as f:
                            self.config = json.load(f)
                        self.last_modified = self.config_file.stat().st_mtime
                        self.reload_count += 1
                
                def check_and_reload(self) -> bool:
                    """Check if file changed and reload"""
                    if not self.config_file.exists():
                        return False
                    
                    current_mtime = self.config_file.stat().st_mtime
                    if current_mtime > self.last_modified:
                        self.load()
                        return True
                    return False
                
                def get(self, key: str, default=None):
                    return self.config.get(key, default)
            
            # Create temp config file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                config_file = Path(f.name)
                json.dump({'value': 100}, f)
            
            # Load config
            config = HotReloadConfig(config_file)
            config.load()
            
            if config.get('value') != 100:
                config_file.unlink()
                self.log_test("Config Hot Reload", False, time.time() - start,
                            "Initial load failed")
                return False
            
            # Modify config file
            time.sleep(0.1)  # Ensure mtime changes
            with open(config_file, 'w') as f:
                json.dump({'value': 200}, f)
            
            # Check and reload
            reloaded = config.check_and_reload()
            
            if not reloaded:
                config_file.unlink()
                self.log_test("Config Hot Reload", False, time.time() - start,
                            "Reload not triggered")
                return False
            
            if config.get('value') != 200:
                config_file.unlink()
                self.log_test("Config Hot Reload", False, time.time() - start,
                            "New value not loaded")
                return False
            
            if config.reload_count != 2:
                config_file.unlink()
                self.log_test("Config Hot Reload", False, time.time() - start,
                            f"Expected 2 reloads, got {config.reload_count}")
                return False
            
            # Cleanup
            config_file.unlink()
            
            self.log_test("Config Hot Reload", True, time.time() - start,
                        "Hot reload successful (2 loads, value updated)")
            return True
            
        except Exception as e:
            self.log_test("Config Hot Reload", False, time.time() - start, str(e))
            return False
    
    def test_config_validation_edge_cases(self) -> bool:
        """Test configuration validation edge cases"""
        start = time.time()
        try:
            def validate_config(config: dict) -> tuple[bool, str]:
                """Validate config with edge case handling"""
                # Check for None values
                for key, value in config.items():
                    if value is None:
                        return False, f"Field {key} is None"
                
                # Check for empty strings
                if 'api_key' in config and config['api_key'] == '':
                    return False, "API key is empty"
                
                # Check for negative numbers where not allowed
                if 'max_trades' in config and config['max_trades'] < 0:
                    return False, "max_trades cannot be negative"
                
                # Check for circular references (simplified)
                if 'parent' in config and config.get('parent') == config:
                    return False, "Circular reference detected"
                
                return True, "Valid"
            
            # Test cases
            test_cases = [
                ({'max_trades': 5, 'api_key': 'valid'}, True, "Valid config"),
                ({'max_trades': None}, False, "None value"),
                ({'api_key': ''}, False, "Empty string"),
                ({'max_trades': -5}, False, "Negative number"),
            ]
            
            passed = 0
            for config, should_pass, description in test_cases:
                is_valid, msg = validate_config(config)
                
                if should_pass and not is_valid:
                    self.log_test("Config Validation Edge Cases", False, time.time() - start,
                                f"{description} rejected: {msg}")
                    return False
                
                if not should_pass and is_valid:
                    self.log_test("Config Validation Edge Cases", False, time.time() - start,
                                f"{description} accepted")
                    return False
                
                passed += 1
            
            self.log_test("Config Validation Edge Cases", True, time.time() - start,
                        f"Validated {passed} edge cases successfully")
            return True
            
        except Exception as e:
            self.log_test("Config Validation Edge Cases", False, time.time() - start, str(e))
            return False
    
    def test_unicode_handling(self) -> bool:
        """Test Unicode and special character handling"""
        start = time.time()
        try:
            test_strings = [
                "Hello World",  # ASCII
                "Привет мир",  # Cyrillic
                "你好世界",  # Chinese
                "مرحبا بالعالم",  # Arabic
                "🚀💰📈",  # Emojis
                "Test\nNewline\tTab",  # Control characters
            ]
            
            for test_str in test_strings:
                # Test JSON encoding/decoding
                encoded = json.dumps({"text": test_str})
                decoded = json.loads(encoded)
                
                if decoded["text"] != test_str:
                    self.log_test("Unicode Handling", False, time.time() - start,
                                f"Unicode mismatch: {test_str}")
                    return False
            
            self.log_test("Unicode Handling", True, time.time() - start,
                        f"Handled {len(test_strings)} Unicode test cases")
            return True
            
        except Exception as e:
            self.log_test("Unicode Handling", False, time.time() - start, str(e))
            return False
    
    def test_large_config_handling(self) -> bool:
        """Test handling of large configuration files"""
        start = time.time()
        try:
            # Generate large config
            large_config = {
                "strategies": [
                    {
                        "id": i,
                        "name": f"strategy_{i}",
                        "parameters": {
                            "param1": i * 1.5,
                            "param2": i * 2.0,
                            "param3": f"value_{i}"
                        }
                    }
                    for i in range(1000)
                ]
            }
            
            # Serialize
            json_str = json.dumps(large_config)
            size_kb = len(json_str) / 1024
            
            # Deserialize
            loaded_config = json.loads(json_str)
            
            # Verify
            if len(loaded_config["strategies"]) != 1000:
                self.log_test("Large Config Handling", False, time.time() - start,
                            "Strategy count mismatch")
                return False
            
            if loaded_config["strategies"][500]["id"] != 500:
                self.log_test("Large Config Handling", False, time.time() - start,
                            "Data integrity issue")
                return False
            
            self.log_test("Large Config Handling", True, time.time() - start,
                        f"Handled {size_kb:.1f}KB config with 1000 strategies")
            return True
            
        except Exception as e:
            self.log_test("Large Config Handling", False, time.time() - start, str(e))
            return False
    
    def test_config_versioning(self) -> bool:
        """Test configuration version compatibility"""
        start = time.time()
        try:
            class ConfigVersionManager:
                CURRENT_VERSION = 3
                
                @staticmethod
                def migrate_v1_to_v2(config: dict) -> dict:
                    """Migrate from v1 to v2"""
                    config['version'] = 2
                    config['new_field'] = 'default_value'
                    return config
                
                @staticmethod
                def migrate_v2_to_v3(config: dict) -> dict:
                    """Migrate from v2 to v3"""
                    config['version'] = 3
                    if 'old_field' in config:
                        config['renamed_field'] = config.pop('old_field')
                    return config
                
                @classmethod
                def migrate_to_current(cls, config: dict) -> dict:
                    """Migrate config to current version"""
                    version = config.get('version', 1)
                    
                    if version < 2:
                        config = cls.migrate_v1_to_v2(config)
                    if version < 3:
                        config = cls.migrate_v2_to_v3(config)
                    
                    return config
            
            # Test v1 config
            v1_config = {'version': 1, 'old_field': 'value'}
            migrated = ConfigVersionManager.migrate_to_current(v1_config)
            
            if migrated['version'] != 3:
                self.log_test("Config Versioning", False, time.time() - start,
                            f"Version not updated: {migrated['version']}")
                return False
            
            if 'new_field' not in migrated:
                self.log_test("Config Versioning", False, time.time() - start,
                            "new_field not added during migration")
                return False
            
            if 'renamed_field' not in migrated:
                self.log_test("Config Versioning", False, time.time() - start,
                            "Field not renamed during migration")
                return False
            
            self.log_test("Config Versioning", True, time.time() - start,
                        "Migrated from v1 to v3 successfully")
            return True
            
        except Exception as e:
            self.log_test("Config Versioning", False, time.time() - start, str(e))
            return False
    
    def test_config_encryption(self) -> bool:
        """Test sensitive configuration field encryption"""
        start = time.time()
        try:
            import base64
            
            def encrypt_field(value: str, key: str) -> str:
                """Simple XOR encryption"""
                encrypted = []
                for i, char in enumerate(value):
                    key_char = key[i % len(key)]
                    encrypted.append(chr(ord(char) ^ ord(key_char)))
                return base64.b64encode(''.join(encrypted).encode()).decode()
            
            def decrypt_field(encrypted: str, key: str) -> str:
                """Simple XOR decryption"""
                data = base64.b64decode(encrypted).decode()
                decrypted = []
                for i, char in enumerate(data):
                    key_char = key[i % len(key)]
                    decrypted.append(chr(ord(char) ^ ord(key_char)))
                return ''.join(decrypted)
            
            # Test encryption
            api_key = "sk_test_1234567890"
            encryption_key = "my_secret_key"
            
            encrypted = encrypt_field(api_key, encryption_key)
            
            if encrypted == api_key:
                self.log_test("Config Encryption", False, time.time() - start,
                            "Field not encrypted")
                return False
            
            # Test decryption
            decrypted = decrypt_field(encrypted, encryption_key)
            
            if decrypted != api_key:
                self.log_test("Config Encryption", False, time.time() - start,
                            "Decryption failed")
                return False
            
            self.log_test("Config Encryption", True, time.time() - start,
                        "Encryption/decryption successful")
            return True
            
        except Exception as e:
            self.log_test("Config Encryption", False, time.time() - start, str(e))
            return False
    
    def test_config_defaults_fallback(self) -> bool:
        """Test configuration defaults and fallback values"""
        start = time.time()
        try:
            class ConfigWithDefaults:
                DEFAULTS = {
                    'max_trades': 5,
                    'risk_level': 'medium',
                    'dry_run': True,
                    'timeout': 30
                }
                
                def __init__(self, user_config: dict = None):
                    self.config = self.DEFAULTS.copy()
                    if user_config:
                        self.config.update(user_config)
                
                def get(self, key: str, default=None):
                    return self.config.get(key, default)
            
            # Test with partial user config
            user_config = {'max_trades': 10}
            config = ConfigWithDefaults(user_config)
            
            # Verify user override
            if config.get('max_trades') != 10:
                self.log_test("Config Defaults Fallback", False, time.time() - start,
                            "User override not applied")
                return False
            
            # Verify defaults
            if config.get('risk_level') != 'medium':
                self.log_test("Config Defaults Fallback", False, time.time() - start,
                            "Default not applied")
                return False
            
            # Test with no user config
            config_empty = ConfigWithDefaults()
            if config_empty.get('timeout') != 30:
                self.log_test("Config Defaults Fallback", False, time.time() - start,
                            "Default not used when no user config")
                return False
            
            self.log_test("Config Defaults Fallback", True, time.time() - start,
                        "Defaults and overrides working correctly")
            return True
            
        except Exception as e:
            self.log_test("Config Defaults Fallback", False, time.time() - start, str(e))
            return False
    
    def run_all_tests(self):
        """Run all configuration validation and advanced tests"""
        logger.info("=" * 80)
        logger.info("CONFIGURATION VALIDATION AND ADVANCED TESTS")
        logger.info("=" * 80)
        
        tests = [
            self.test_config_schema_validation,
            self.test_environment_variable_override,
            self.test_config_merge_strategy,
            self.test_config_hot_reload,
            self.test_config_validation_edge_cases,
            self.test_unicode_handling,
            self.test_large_config_handling,
            self.test_config_versioning,
            self.test_config_encryption,
            self.test_config_defaults_fallback
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} crashed: {e}")
                self.log_test(test.__name__, False, 0, f"Test crashed: {e}")
        
        # Calculate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['passed'])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        total_duration = time.time() - self.start_time
        
        logger.info("=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ({pass_rate:.1f}%)")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Total Duration: {total_duration:.2f}s")
        logger.info("=" * 80)
        
        # Save results
        results_data = {
            "test_suite": "Configuration Validation and Advanced Tests",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": round(pass_rate, 2),
                "duration_seconds": round(total_duration, 2)
            },
            "tests": self.results
        }
        
        output_file = Path("config_validation_advanced_test_results.json")
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"✅ Results saved to {output_file}")
        
        return pass_rate >= 80


if __name__ == "__main__":
    tester = ConfigValidationAdvancedTests()
    success = tester.run_all_tests()
    exit(0 if success else 1)
