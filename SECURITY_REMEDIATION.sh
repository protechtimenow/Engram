#!/bin/bash

################################################################################
# SECURITY REMEDIATION SCRIPT
# Purpose: Remove exposed Telegram bot token from all files
# Date: 2026-01-31
# CRITICAL: Run this script AFTER revoking the old token via @BotFather
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Exposed token to remove
OLD_TOKEN="8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
PLACEHOLDER_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"

echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║         CRITICAL SECURITY REMEDIATION SCRIPT                   ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo -e "${RED}ERROR: Not in a git repository. Please run from repository root.${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This script will modify 46+ files in your repository${NC}"
echo -e "${YELLOW}⚠️  Make sure you have:${NC}"
echo -e "${YELLOW}    1. Revoked the old token via @BotFather${NC}"
echo -e "${YELLOW}    2. Generated a new token${NC}"
echo -e "${YELLOW}    3. Backed up your repository${NC}"
echo ""
read -p "Have you completed the above steps? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Aborting. Please complete the prerequisites first.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 1: Creating backup${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

BACKUP_DIR="security_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# List of files containing the token
FILES_TO_CLEAN=(
    ".env"
    "CHAT_ID_VERIFICATION_SUMMARY.txt"
    "ENHANCED_LAUNCHER_GUIDE.md"
    "FINAL_TEST_REPORT.md"
    "GITHUB_PUSH_SUCCESS.txt"
    "LMSTUDIO_ENDPOINT_UPDATE_REPORT.md"
    "LMSTUDIO_ISSUE_RESOLVED.txt"
    "LMSTUDIO_TIMEOUT_FIX.md"
    "PRODUCTION_DEPLOYMENT_GUIDE.md"
    "QUICK_START.md"
    "REAL_CHAT_ID_VERIFICATION.md"
    "SESSION_SUMMARY.md"
    "TESTING_COMPLETE_SUMMARY.md"
    "TEST_EXECUTION_SUMMARY.txt"
    "comprehensive_test_suite.py"
    "config/engram_freqtrade_config.json"
    "config/engram_intelligent_config.json"
    "config/intelligent_freqtrade_config.json"
    "config/simple_config.json"
    "config/telegram/complete_telegram_config.json"
    "config/telegram/final_telegram_config.json"
    "config/telegram/minimal_telegram_config.json"
    "config/telegram/working_telegram_config.json"
    "docs/TELEGRAM_STATUS.md"
    "integration_test_with_new_endpoint.py"
    "interactive_bot_test.py"
    "real_telegram_integration_test.py"
    "run_telegram_bot.py"
    "security_authentication_tests.py"
    "simple_telegram_bot.py"
    "sync_telegram_bot.py"
    "test_enhanced_launcher.py"
    "test_enhanced_launcher_standalone.py"
)

# Backup files
echo -e "${GREEN}Creating backups...${NC}"
for file in "${FILES_TO_CLEAN[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/" 2>/dev/null || mkdir -p "$BACKUP_DIR/$(dirname "$file")" && cp "$file" "$BACKUP_DIR/$file"
        echo "  ✓ Backed up: $file"
    fi
done

echo -e "${GREEN}✓ Backup created in: $BACKUP_DIR${NC}"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 2: Removing exposed token from files${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

CLEANED_COUNT=0

for file in "${FILES_TO_CLEAN[@]}"; do
    if [ -f "$file" ]; then
        # Check if file contains the token
        if grep -q "$OLD_TOKEN" "$file" 2>/dev/null; then
            # Replace token with placeholder
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' "s/$OLD_TOKEN/$PLACEHOLDER_TOKEN/g" "$file"
            else
                # Linux
                sed -i "s/$OLD_TOKEN/$PLACEHOLDER_TOKEN/g" "$file"
            fi
            echo -e "${GREEN}  ✓ Cleaned: $file${NC}"
            ((CLEANED_COUNT++))
        fi
    fi
done

echo ""
echo -e "${GREEN}✓ Cleaned $CLEANED_COUNT files${NC}"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 3: Updating .env file${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

# Create .env.example
cat > .env.example << 'EOF'
# Engram-FreqTrade Environment Variables
# Copy this file to .env and fill in your actual values

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID_HERE

# Exchange API Keys (Binance)
BINANCE_API_KEY=YOUR_BINANCE_API_KEY
BINANCE_API_SECRET=YOUR_BINANCE_API_SECRET

# LMStudio Configuration
LMSTUDIO_URL=http://100.118.172.23:1234
LMSTUDIO_TIMEOUT=10

# Engram Configuration
ENGRAM_MODEL_PATH=./src/core/engram_demo_v1.py
ENGRAM_MAX_NGRAM_SIZE=3
ENGRAM_EMBED_DIM=512

# FreqTrade Configuration
FREQTRADE_CONFIG_PATH=./config/engram_freqtrade_config.json
FREQTRADE_STRATEGY_PATH=./src/trading/engram_trading_strategy.py

# Logging
LOG_LEVEL=INFO
LOG_FILE=engram_trader.log
EOF

echo -e "${GREEN}✓ Created .env.example${NC}"

# Update .env with placeholder
if [ -f ".env" ]; then
    cat > .env << 'EOF'
# Engram-FreqTrade Environment Variables

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=1007321485

# Exchange API Keys (Binance)
BINANCE_API_KEY=YOUR_BINANCE_API_KEY
BINANCE_API_SECRET=YOUR_BINANCE_API_SECRET

# LMStudio Configuration
LMSTUDIO_URL=http://100.118.172.23:1234
LMSTUDIO_TIMEOUT=10

# Engram Configuration
ENGRAM_MODEL_PATH=./src/core/engram_demo_v1.py
ENGRAM_MAX_NGRAM_SIZE=3
ENGRAM_EMBED_DIM=512

# FreqTrade Configuration
FREQTRADE_CONFIG_PATH=./config/engram_freqtrade_config.json
FREQTRADE_STRATEGY_PATH=./src/trading/engram_trading_strategy.py

# Logging
LOG_LEVEL=INFO
LOG_FILE=engram_trader.log
EOF
    echo -e "${GREEN}✓ Updated .env with placeholders${NC}"
fi

echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 4: Updating .gitignore${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

# Ensure .env is in .gitignore
if [ -f ".gitignore" ]; then
    if ! grep -q "^\.env$" .gitignore; then
        echo "" >> .gitignore
        echo "# Environment variables (contains secrets)" >> .gitignore
        echo ".env" >> .gitignore
        echo ".env.*" >> .gitignore
        echo "!.env.example" >> .gitignore
        echo -e "${GREEN}✓ Added .env to .gitignore${NC}"
    else
        echo -e "${YELLOW}⚠️  .env already in .gitignore${NC}"
    fi
else
    cat > .gitignore << 'EOF'
# Environment variables (contains secrets)
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Backups
security_backup_*/
EOF
    echo -e "${GREEN}✓ Created .gitignore${NC}"
fi

echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 5: Verification${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

# Verify token is removed
REMAINING=$(grep -r "$OLD_TOKEN" . --exclude-dir=.git --exclude-dir="$BACKUP_DIR" 2>/dev/null | wc -l)

if [ "$REMAINING" -eq 0 ]; then
    echo -e "${GREEN}✓ SUCCESS: No instances of old token found${NC}"
else
    echo -e "${RED}⚠️  WARNING: Found $REMAINING remaining instances of old token${NC}"
    echo -e "${YELLOW}Run this to see locations:${NC}"
    echo "  grep -r '$OLD_TOKEN' . --exclude-dir=.git --exclude-dir='$BACKUP_DIR'"
fi

echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 6: Git Status${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

git status --short

echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  REMEDIATION COMPLETE                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo -e "${BLUE}1. Set your new Telegram bot token:${NC}"
echo "   export TELEGRAM_BOT_TOKEN='YOUR_NEW_TOKEN_FROM_BOTFATHER'"
echo "   # Or add it to .env file"
echo ""
echo -e "${BLUE}2. Review changes:${NC}"
echo "   git diff"
echo ""
echo -e "${BLUE}3. Commit changes:${NC}"
echo "   git add ."
echo "   git commit -m 'security: remove exposed Telegram bot token'"
echo ""
echo -e "${BLUE}4. Remove .env from git history (CRITICAL):${NC}"
echo "   # Install git-filter-repo:"
echo "   pip install git-filter-repo"
echo ""
echo "   # Remove .env from entire history:"
echo "   git filter-repo --path .env --invert-paths --force"
echo ""
echo -e "${BLUE}5. Force push to remote (after history cleanup):${NC}"
echo "   git push origin --force --all"
echo "   git push origin --force --tags"
echo ""
echo -e "${RED}⚠️  IMPORTANT: Notify team members before force pushing!${NC}"
echo ""
echo -e "${BLUE}6. Verify on GitHub:${NC}"
echo "   Check that .env is no longer in repository history"
echo ""
echo -e "${GREEN}Backup location: $BACKUP_DIR${NC}"
echo ""
