# 🔒 Security Best Practices for Engram Trading Bot

**Last Updated:** 2026-01-31  
**Version:** 1.0

---

## Table of Contents

1. [Secrets Management](#secrets-management)
2. [Environment Variables](#environment-variables)
3. [Git Security](#git-security)
4. [Pre-Commit Hooks](#pre-commit-hooks)
5. [API Key Security](#api-key-security)
6. [Telegram Bot Security](#telegram-bot-security)
7. [Exchange API Security](#exchange-api-security)
8. [Monitoring & Auditing](#monitoring--auditing)
9. [Incident Response](#incident-response)
10. [Compliance Checklist](#compliance-checklist)

---

## 1. Secrets Management

### ✅ DO

**Use Environment Variables:**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set")
```

**Use Secret Management Services:**
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Cloud Secret Manager

**Use .env Files (Never Commit):**
```bash
# .env (add to .gitignore)
TELEGRAM_BOT_TOKEN=your_actual_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

### ❌ DON'T

**Never Hardcode Secrets:**
```python
# BAD ❌
TELEGRAM_TOKEN = "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
BINANCE_API_KEY = "abc123xyz789"
```

**Never Commit .env Files:**
```bash
# BAD ❌
git add .env
git commit -m "Add configuration"
```

**Never Share Secrets in:**
- Source code
- Documentation
- Chat messages
- Email
- Screenshots
- Log files

---

## 2. Environment Variables

### Configuration Template

Create `.env.example` (safe to commit):
```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID_HERE

# Exchange API Keys
BINANCE_API_KEY=YOUR_BINANCE_API_KEY
BINANCE_API_SECRET=YOUR_BINANCE_API_SECRET

# LMStudio Configuration
LMSTUDIO_URL=http://100.118.172.23:1234
LMSTUDIO_TIMEOUT=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=engram_trader.log
```

### Loading Environment Variables

**Python (using python-dotenv):**
```python
from dotenv import load_dotenv
import os

# Load from .env file
load_dotenv()

# Access variables
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

# With defaults
log_level = os.getenv('LOG_LEVEL', 'INFO')
```

**Shell:**
```bash
# Load from .env
export $(cat .env | xargs)

# Or use source
source .env

# Run application
python3 enhanced_engram_launcher.py
```

---

## 3. Git Security

### .gitignore Configuration

```gitignore
# Environment variables (contains secrets)
.env
.env.*
!.env.example

# API Keys and Secrets
*.key
*.pem
*.p12
secrets/
credentials/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp

# Logs (may contain sensitive data)
*.log
logs/

# Backups
*.bak
security_backup_*/

# OS
.DS_Store
Thumbs.db
```

### Remove Secrets from Git History

**Method 1: git-filter-repo (Recommended)**
```bash
# Install
pip install git-filter-repo

# Remove specific file from entire history
git filter-repo --path .env --invert-paths --force

# Remove specific text pattern
git filter-repo --replace-text <(echo "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA==>REDACTED")
```

**Method 2: BFG Repo-Cleaner**
```bash
# Download BFG
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# Remove file
java -jar bfg-1.14.0.jar --delete-files .env

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**Force Push After Cleanup:**
```bash
# Push cleaned history
git push origin --force --all
git push origin --force --tags

# Notify team members!
```

---

## 4. Pre-Commit Hooks

### Install detect-secrets

```bash
# Install
pip install detect-secrets

# Initialize baseline
detect-secrets scan > .secrets.baseline

# Audit findings
detect-secrets audit .secrets.baseline
```

### Configure Pre-Commit

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package.lock.json

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: detect-private-key
```

Install hooks:
```bash
pip install pre-commit
pre-commit install
```

### Custom Pre-Commit Hook

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash

# Check for common secret patterns
if git diff --cached | grep -E "(api_key|api_secret|password|token|secret)" | grep -v "YOUR_.*_HERE"; then
    echo "ERROR: Potential secret detected in staged files!"
    echo "Please review your changes and remove any secrets."
    exit 1
fi

# Check for .env file
if git diff --cached --name-only | grep -q "^\.env$"; then
    echo "ERROR: Attempting to commit .env file!"
    echo "This file should never be committed."
    exit 1
fi

exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 5. API Key Security

### Telegram Bot Token

**Best Practices:**
- Rotate tokens every 90 days
- Use separate bots for dev/staging/production
- Revoke immediately if exposed
- Monitor bot activity via @BotFather

**Revoke Compromised Token:**
```
1. Open Telegram
2. Message @BotFather
3. Send: /revoke
4. Select your bot
5. Confirm revocation
6. Generate new token: /token
```

**Validate Token:**
```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### Exchange API Keys (Binance)

**Security Settings:**
- Enable IP whitelist
- Restrict to trading only (no withdrawals)
- Use separate keys for different strategies
- Enable 2FA on exchange account
- Set withdrawal whitelist

**API Key Permissions:**
```
✅ Enable Reading
✅ Enable Spot & Margin Trading
❌ Disable Withdrawals
❌ Disable Internal Transfer
```

**IP Whitelist:**
```
# Add your server IPs only
203.0.113.1
203.0.113.2
```

---

## 6. Telegram Bot Security

### Bot Configuration

**Restrict Access:**
```python
ALLOWED_CHAT_IDS = [1007321485]  # Your chat ID only

def is_authorized(chat_id):
    return chat_id in ALLOWED_CHAT_IDS

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not is_authorized(message.chat.id):
        bot.reply_to(message, "Unauthorized access")
        return
    # Process message
```

**Rate Limiting:**
```python
from functools import wraps
from time import time

def rate_limit(max_calls=10, period=60):
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time()
            calls[:] = [c for c in calls if c > now - period]
            
            if len(calls) >= max_calls:
                raise Exception("Rate limit exceeded")
            
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=10, period=60)
def process_command(message):
    # Process command
    pass
```

**Input Validation:**
```python
import re

def validate_command(text):
    # Only allow alphanumeric and specific characters
    if not re.match(r'^[a-zA-Z0-9\s/_-]+$', text):
        raise ValueError("Invalid command format")
    return text
```

---

## 7. Exchange API Security

### Secure API Client

```python
import hmac
import hashlib
import time
from typing import Dict

class SecureExchangeClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.binance.com"
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_headers(self) -> Dict:
        """Get request headers"""
        return {
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def make_request(self, endpoint: str, params: Dict = None):
        """Make authenticated request"""
        if params is None:
            params = {}
        
        # Add timestamp
        params['timestamp'] = int(time.time() * 1000)
        
        # Generate signature
        params['signature'] = self._generate_signature(params)
        
        # Make request with timeout
        response = requests.get(
            f"{self.base_url}{endpoint}",
            params=params,
            headers=self._get_headers(),
            timeout=10
        )
        
        return response.json()
```

### API Key Rotation

```python
import os
from datetime import datetime, timedelta

def check_api_key_age():
    """Check if API key needs rotation"""
    key_created = os.getenv('API_KEY_CREATED_DATE')
    if not key_created:
        return True
    
    created_date = datetime.fromisoformat(key_created)
    age = datetime.now() - created_date
    
    # Rotate every 90 days
    if age > timedelta(days=90):
        print("⚠️  API key is older than 90 days. Consider rotating.")
        return True
    
    return False
```

---

## 8. Monitoring & Auditing

### Security Logging

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    'security.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
security_logger.addHandler(handler)

# Log security events
def log_security_event(event_type, details):
    security_logger.info(f"{event_type}: {details}")

# Usage
log_security_event("AUTH_ATTEMPT", f"Chat ID: {chat_id}")
log_security_event("API_CALL", f"Endpoint: {endpoint}")
log_security_event("TOKEN_REFRESH", "Telegram bot token refreshed")
```

### Audit Trail

```python
import json
from datetime import datetime

class AuditLogger:
    def __init__(self, log_file='audit.log'):
        self.log_file = log_file
    
    def log(self, action, user, details=None):
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'user': user,
            'details': details or {}
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

# Usage
audit = AuditLogger()
audit.log('TRADE_EXECUTED', 'bot', {'pair': 'BTC/USDT', 'amount': 0.01})
audit.log('CONFIG_CHANGED', 'admin', {'setting': 'max_position_size'})
```

### Monitoring Alerts

```python
def send_security_alert(message):
    """Send security alert via Telegram"""
    import requests
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': f"🚨 SECURITY ALERT\n\n{message}",
        'parse_mode': 'Markdown'
    }
    
    requests.post(url, json=payload)

# Usage
send_security_alert("Unauthorized access attempt detected")
send_security_alert("API key rotation required")
```

---

## 9. Incident Response

### Incident Response Plan

**1. Detection**
- Monitor logs for suspicious activity
- Set up alerts for failed authentication
- Track API usage patterns

**2. Containment**
- Immediately revoke compromised credentials
- Block suspicious IP addresses
- Disable affected services

**3. Investigation**
- Review audit logs
- Identify scope of breach
- Document timeline

**4. Remediation**
- Rotate all credentials
- Update security measures
- Patch vulnerabilities

**5. Recovery**
- Restore services with new credentials
- Verify system integrity
- Monitor for continued threats

**6. Post-Incident**
- Document lessons learned
- Update security procedures
- Train team members

### Emergency Contacts

```
Security Team: security@example.com
On-Call: +44 7585 185906
Telegram: @YourSecurityBot
```

### Incident Checklist

```markdown
- [ ] Identify compromised credentials
- [ ] Revoke Telegram bot token
- [ ] Rotate exchange API keys
- [ ] Review recent transactions
- [ ] Check for unauthorized access
- [ ] Update all passwords
- [ ] Enable 2FA everywhere
- [ ] Review git commit history
- [ ] Scan for malware
- [ ] Notify affected parties
- [ ] Document incident
- [ ] Update security procedures
```

---

## 10. Compliance Checklist

### Daily
- [ ] Review security logs
- [ ] Check for failed authentication attempts
- [ ] Monitor API usage

### Weekly
- [ ] Review audit trail
- [ ] Check for software updates
- [ ] Verify backup integrity

### Monthly
- [ ] Rotate development credentials
- [ ] Review access permissions
- [ ] Update dependencies
- [ ] Security scan (detect-secrets)

### Quarterly
- [ ] Rotate production API keys
- [ ] Security audit
- [ ] Penetration testing
- [ ] Review incident response plan

### Annually
- [ ] Comprehensive security review
- [ ] Update security policies
- [ ] Team security training
- [ ] Third-party security audit

---

## Additional Resources

### Tools
- **detect-secrets:** https://github.com/Yelp/detect-secrets
- **git-filter-repo:** https://github.com/newren/git-filter-repo
- **BFG Repo-Cleaner:** https://rtyley.github.io/bfg-repo-cleaner/
- **pre-commit:** https://pre-commit.com/

### Documentation
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Binance API:** https://binance-docs.github.io/apidocs/
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **CWE Top 25:** https://cwe.mitre.org/top25/

### Security Standards
- **NIST Cybersecurity Framework:** https://www.nist.gov/cyberframework
- **ISO 27001:** Information Security Management
- **PCI DSS:** Payment Card Industry Data Security Standard

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-31  
**Next Review:** 2026-04-30
