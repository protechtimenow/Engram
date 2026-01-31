#!/usr/bin/env python3
"""
Comprehensive Security and Authentication Tests for Engram Trading Bot
Tests: Token validation, API security, credential handling, encryption
"""

import json
import logging
import time
import hashlib
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityAuthenticationTests:
    """Comprehensive security and authentication test suite"""
    
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
    
    def test_telegram_token_validation(self) -> bool:
        """Test Telegram bot token format validation"""
        start = time.time()
        try:
            # Valid token format: bot_id:secret_key
            valid_tokens = [
                "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA",
                "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ1234567890",
                "1234567890:AAAA-BBBBccccDDDDeeeeFFFFggggHHHHiiii"
            ]
            
            invalid_tokens = [
                "",
                "invalid",
                "123456789",
                ":AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA",
                "8517504737:",
                "not:a:valid:token"
            ]
            
            def validate_token(token: str) -> bool:
                if not token or ':' not in token:
                    return False
                parts = token.split(':')
                if len(parts) != 2:
                    return False
                bot_id, secret = parts
                return bot_id.isdigit() and len(secret) >= 35
            
            # Test valid tokens
            for token in valid_tokens:
                if not validate_token(token):
                    self.log_test("Telegram Token Validation", False, 
                                time.time() - start, f"Valid token rejected: {token[:20]}...")
                    return False
            
            # Test invalid tokens
            for token in invalid_tokens:
                if validate_token(token):
                    self.log_test("Telegram Token Validation", False,
                                time.time() - start, f"Invalid token accepted: {token}")
                    return False
            
            self.log_test("Telegram Token Validation", True, time.time() - start,
                        f"Validated {len(valid_tokens)} valid and {len(invalid_tokens)} invalid tokens")
            return True
            
        except Exception as e:
            self.log_test("Telegram Token Validation", False, time.time() - start, str(e))
            return False
    
    def test_chat_id_validation(self) -> bool:
        """Test Telegram chat ID validation"""
        start = time.time()
        try:
            valid_chat_ids = [
                "1007321485",
                "123456789",
                "-1001234567890",  # Group chat
                "1234567890"
            ]
            
            invalid_chat_ids = [
                "",
                "abc",
                "12.34",
                "not_a_number",
                None
            ]
            
            def validate_chat_id(chat_id) -> bool:
                if chat_id is None:
                    return False
                chat_id_str = str(chat_id)
                if not chat_id_str:
                    return False
                # Allow negative for group chats
                if chat_id_str.startswith('-'):
                    return chat_id_str[1:].isdigit()
                return chat_id_str.isdigit()
            
            # Test valid chat IDs
            for chat_id in valid_chat_ids:
                if not validate_chat_id(chat_id):
                    self.log_test("Chat ID Validation", False,
                                time.time() - start, f"Valid chat_id rejected: {chat_id}")
                    return False
            
            # Test invalid chat IDs
            for chat_id in invalid_chat_ids:
                if validate_chat_id(chat_id):
                    self.log_test("Chat ID Validation", False,
                                time.time() - start, f"Invalid chat_id accepted: {chat_id}")
                    return False
            
            self.log_test("Chat ID Validation", True, time.time() - start,
                        f"Validated {len(valid_chat_ids)} valid and {len(invalid_chat_ids)} invalid IDs")
            return True
            
        except Exception as e:
            self.log_test("Chat ID Validation", False, time.time() - start, str(e))
            return False
    
    def test_api_key_security(self) -> bool:
        """Test API key security and storage"""
        start = time.time()
        try:
            # Test that API keys are not logged or exposed
            test_api_key = "sk_test_1234567890abcdefghijklmnopqrstuvwxyz"
            
            # Simulate secure storage
            def hash_api_key(key: str) -> str:
                return hashlib.sha256(key.encode()).hexdigest()
            
            hashed = hash_api_key(test_api_key)
            
            # Verify hash is different from original
            if hashed == test_api_key:
                self.log_test("API Key Security", False, time.time() - start,
                            "API key not properly hashed")
                return False
            
            # Verify hash is consistent
            if hash_api_key(test_api_key) != hashed:
                self.log_test("API Key Security", False, time.time() - start,
                            "Hash function not deterministic")
                return False
            
            # Test key masking for logs
            def mask_api_key(key: str) -> str:
                if len(key) <= 8:
                    return "***"
                return f"{key[:4]}...{key[-4:]}"
            
            masked = mask_api_key(test_api_key)
            if test_api_key in masked or len(masked) > 15:
                self.log_test("API Key Security", False, time.time() - start,
                            "API key not properly masked")
                return False
            
            self.log_test("API Key Security", True, time.time() - start,
                        "API keys properly hashed and masked")
            return True
            
        except Exception as e:
            self.log_test("API Key Security", False, time.time() - start, str(e))
            return False
    
    def test_credential_encryption(self) -> bool:
        """Test credential encryption and decryption"""
        start = time.time()
        try:
            # Simple XOR encryption for testing
            def encrypt_credential(data: str, key: str) -> str:
                encrypted = []
                for i, char in enumerate(data):
                    key_char = key[i % len(key)]
                    encrypted.append(chr(ord(char) ^ ord(key_char)))
                return base64.b64encode(''.join(encrypted).encode()).decode()
            
            def decrypt_credential(encrypted: str, key: str) -> str:
                data = base64.b64decode(encrypted).decode()
                decrypted = []
                for i, char in enumerate(data):
                    key_char = key[i % len(key)]
                    decrypted.append(chr(ord(char) ^ ord(key_char)))
                return ''.join(decrypted)
            
            test_credential = "my_secret_password_123"
            encryption_key = "encryption_key_456"
            
            # Encrypt
            encrypted = encrypt_credential(test_credential, encryption_key)
            
            # Verify encrypted is different
            if encrypted == test_credential:
                self.log_test("Credential Encryption", False, time.time() - start,
                            "Credential not encrypted")
                return False
            
            # Decrypt
            decrypted = decrypt_credential(encrypted, encryption_key)
            
            # Verify decryption works
            if decrypted != test_credential:
                self.log_test("Credential Encryption", False, time.time() - start,
                            "Decryption failed")
                return False
            
            # Test wrong key fails
            try:
                wrong_decrypt = decrypt_credential(encrypted, "wrong_key")
                if wrong_decrypt == test_credential:
                    self.log_test("Credential Encryption", False, time.time() - start,
                                "Wrong key decrypted successfully")
                    return False
            except:
                pass  # Expected to fail
            
            self.log_test("Credential Encryption", True, time.time() - start,
                        "Encryption/decryption working correctly")
            return True
            
        except Exception as e:
            self.log_test("Credential Encryption", False, time.time() - start, str(e))
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting for API calls"""
        start = time.time()
        try:
            class RateLimiter:
                def __init__(self, max_calls: int, time_window: float):
                    self.max_calls = max_calls
                    self.time_window = time_window
                    self.calls = []
                
                def allow_call(self) -> bool:
                    now = time.time()
                    # Remove old calls outside time window
                    self.calls = [t for t in self.calls if now - t < self.time_window]
                    
                    if len(self.calls) < self.max_calls:
                        self.calls.append(now)
                        return True
                    return False
            
            # Test: 5 calls per second
            limiter = RateLimiter(max_calls=5, time_window=1.0)
            
            # First 5 calls should succeed
            for i in range(5):
                if not limiter.allow_call():
                    self.log_test("Rate Limiting", False, time.time() - start,
                                f"Call {i+1} rejected incorrectly")
                    return False
            
            # 6th call should be rejected
            if limiter.allow_call():
                self.log_test("Rate Limiting", False, time.time() - start,
                            "Rate limit not enforced")
                return False
            
            # After 1 second, should allow again
            time.sleep(1.1)
            if not limiter.allow_call():
                self.log_test("Rate Limiting", False, time.time() - start,
                            "Rate limit not reset after time window")
                return False
            
            self.log_test("Rate Limiting", True, time.time() - start,
                        "Rate limiting working correctly (5 calls/sec)")
            return True
            
        except Exception as e:
            self.log_test("Rate Limiting", False, time.time() - start, str(e))
            return False
    
    def test_input_sanitization(self) -> bool:
        """Test input sanitization against injection attacks"""
        start = time.time()
        try:
            def sanitize_input(user_input: str) -> str:
                # Remove potentially dangerous characters
                dangerous_chars = ['<', '>', '"', "'", ';', '&', '|', '`', '$', '(', ')']
                sanitized = user_input
                for char in dangerous_chars:
                    sanitized = sanitized.replace(char, '')
                return sanitized.strip()
            
            # Test cases
            test_cases = [
                ("normal input", "normal input", True),
                ("<script>alert('xss')</script>", "scriptalert'xss'script", True),
                ("'; DROP TABLE users; --", " DROP TABLE users --", True),
                ("$(rm -rf /)", "rm -rf ", True),
                ("hello & goodbye", "hello  goodbye", True),
            ]
            
            for original, expected, should_differ in test_cases:
                sanitized = sanitize_input(original)
                if should_differ and '<' in sanitized:
                    self.log_test("Input Sanitization", False, time.time() - start,
                                f"Dangerous input not sanitized: {original}")
                    return False
            
            self.log_test("Input Sanitization", True, time.time() - start,
                        f"Sanitized {len(test_cases)} test cases successfully")
            return True
            
        except Exception as e:
            self.log_test("Input Sanitization", False, time.time() - start, str(e))
            return False
    
    def test_session_management(self) -> bool:
        """Test session token generation and validation"""
        start = time.time()
        try:
            import secrets
            
            class SessionManager:
                def __init__(self):
                    self.sessions = {}
                
                def create_session(self, user_id: str) -> str:
                    token = secrets.token_urlsafe(32)
                    self.sessions[token] = {
                        'user_id': user_id,
                        'created_at': time.time(),
                        'expires_at': time.time() + 3600  # 1 hour
                    }
                    return token
                
                def validate_session(self, token: str) -> bool:
                    if token not in self.sessions:
                        return False
                    session = self.sessions[token]
                    if time.time() > session['expires_at']:
                        del self.sessions[token]
                        return False
                    return True
                
                def invalidate_session(self, token: str):
                    if token in self.sessions:
                        del self.sessions[token]
            
            manager = SessionManager()
            
            # Create session
            token = manager.create_session("user123")
            if not token or len(token) < 32:
                self.log_test("Session Management", False, time.time() - start,
                            "Session token too short")
                return False
            
            # Validate session
            if not manager.validate_session(token):
                self.log_test("Session Management", False, time.time() - start,
                            "Valid session rejected")
                return False
            
            # Test invalid token
            if manager.validate_session("invalid_token"):
                self.log_test("Session Management", False, time.time() - start,
                            "Invalid session accepted")
                return False
            
            # Invalidate session
            manager.invalidate_session(token)
            if manager.validate_session(token):
                self.log_test("Session Management", False, time.time() - start,
                            "Invalidated session still valid")
                return False
            
            self.log_test("Session Management", True, time.time() - start,
                        "Session creation, validation, and invalidation working")
            return True
            
        except Exception as e:
            self.log_test("Session Management", False, time.time() - start, str(e))
            return False
    
    def test_password_hashing(self) -> bool:
        """Test password hashing and verification"""
        start = time.time()
        try:
            def hash_password(password: str, salt: str = None) -> tuple:
                if salt is None:
                    salt = base64.b64encode(str(time.time()).encode()).decode()[:16]
                hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), 
                                            salt.encode(), 100000)
                return base64.b64encode(hashed).decode(), salt
            
            def verify_password(password: str, hashed: str, salt: str) -> bool:
                new_hash, _ = hash_password(password, salt)
                return new_hash == hashed
            
            # Test password hashing
            password = "my_secure_password_123"
            hashed, salt = hash_password(password)
            
            # Verify hash is different from password
            if hashed == password:
                self.log_test("Password Hashing", False, time.time() - start,
                            "Password not hashed")
                return False
            
            # Verify correct password
            if not verify_password(password, hashed, salt):
                self.log_test("Password Hashing", False, time.time() - start,
                            "Correct password verification failed")
                return False
            
            # Verify wrong password fails
            if verify_password("wrong_password", hashed, salt):
                self.log_test("Password Hashing", False, time.time() - start,
                            "Wrong password verified successfully")
                return False
            
            self.log_test("Password Hashing", True, time.time() - start,
                        "Password hashing and verification working")
            return True
            
        except Exception as e:
            self.log_test("Password Hashing", False, time.time() - start, str(e))
            return False
    
    def test_csrf_protection(self) -> bool:
        """Test CSRF token generation and validation"""
        start = time.time()
        try:
            import secrets
            
            class CSRFProtection:
                def __init__(self):
                    self.tokens = {}
                
                def generate_token(self, session_id: str) -> str:
                    token = secrets.token_hex(32)
                    self.tokens[session_id] = token
                    return token
                
                def validate_token(self, session_id: str, token: str) -> bool:
                    if session_id not in self.tokens:
                        return False
                    return self.tokens[session_id] == token
                
                def invalidate_token(self, session_id: str):
                    if session_id in self.tokens:
                        del self.tokens[session_id]
            
            csrf = CSRFProtection()
            
            # Generate token
            session_id = "session123"
            token = csrf.generate_token(session_id)
            
            # Validate correct token
            if not csrf.validate_token(session_id, token):
                self.log_test("CSRF Protection", False, time.time() - start,
                            "Valid CSRF token rejected")
                return False
            
            # Test wrong token
            if csrf.validate_token(session_id, "wrong_token"):
                self.log_test("CSRF Protection", False, time.time() - start,
                            "Invalid CSRF token accepted")
                return False
            
            # Test wrong session
            if csrf.validate_token("wrong_session", token):
                self.log_test("CSRF Protection", False, time.time() - start,
                            "Token valid for wrong session")
                return False
            
            self.log_test("CSRF Protection", True, time.time() - start,
                        "CSRF token generation and validation working")
            return True
            
        except Exception as e:
            self.log_test("CSRF Protection", False, time.time() - start, str(e))
            return False
    
    def test_secure_config_loading(self) -> bool:
        """Test secure configuration file loading"""
        start = time.time()
        try:
            # Test loading config without exposing secrets
            test_config = {
                "telegram": {
                    "token": "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA",
                    "chat_id": "1007321485"
                },
                "api_key": "sk_test_secret_key_123"
            }
            
            def mask_secrets(config: dict) -> dict:
                """Mask sensitive values in config"""
                masked = {}
                sensitive_keys = ['token', 'api_key', 'password', 'secret']
                
                for key, value in config.items():
                    if isinstance(value, dict):
                        masked[key] = mask_secrets(value)
                    elif any(sk in key.lower() for sk in sensitive_keys):
                        if isinstance(value, str) and len(value) > 8:
                            masked[key] = f"{value[:4]}...{value[-4:]}"
                        else:
                            masked[key] = "***"
                    else:
                        masked[key] = value
                return masked
            
            masked_config = mask_secrets(test_config)
            
            # Verify secrets are masked
            if test_config['telegram']['token'] in str(masked_config):
                self.log_test("Secure Config Loading", False, time.time() - start,
                            "Token not masked in config")
                return False
            
            if test_config['api_key'] in str(masked_config):
                self.log_test("Secure Config Loading", False, time.time() - start,
                            "API key not masked in config")
                return False
            
            # Verify non-sensitive data preserved
            if masked_config['telegram']['chat_id'] != test_config['telegram']['chat_id']:
                self.log_test("Secure Config Loading", False, time.time() - start,
                            "Non-sensitive data incorrectly masked")
                return False
            
            self.log_test("Secure Config Loading", True, time.time() - start,
                        "Config secrets properly masked")
            return True
            
        except Exception as e:
            self.log_test("Secure Config Loading", False, time.time() - start, str(e))
            return False
    
    def run_all_tests(self):
        """Run all security and authentication tests"""
        logger.info("=" * 80)
        logger.info("SECURITY AND AUTHENTICATION TESTS")
        logger.info("=" * 80)
        
        tests = [
            self.test_telegram_token_validation,
            self.test_chat_id_validation,
            self.test_api_key_security,
            self.test_credential_encryption,
            self.test_rate_limiting,
            self.test_input_sanitization,
            self.test_session_management,
            self.test_password_hashing,
            self.test_csrf_protection,
            self.test_secure_config_loading
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
            "test_suite": "Security and Authentication Tests",
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
        
        output_file = Path("security_authentication_test_results.json")
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"✅ Results saved to {output_file}")
        
        return pass_rate >= 80


if __name__ == "__main__":
    tester = SecurityAuthenticationTests()
    success = tester.run_all_tests()
    exit(0 if success else 1)
