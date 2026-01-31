#!/bin/bash

################################################################################
# Git Submodule Fix Script - Engram Repository
# Purpose: Remove unpopulated submodules and clean up git configuration
# Usage: ./fix_submodules.sh [option]
# Options: remove, fix, convert
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository!"
        exit 1
    fi
    print_success "Git repository detected"
}

# Function to backup current state
backup_state() {
    print_status "Creating backup..."
    local backup_dir=".git_backup_$(date +%Y%m%d_%H%M%S)"
    
    # Backup .gitmodules if it exists
    if [ -f .gitmodules ]; then
        cp .gitmodules "${backup_dir}_gitmodules" 2>/dev/null || true
        print_success "Backed up .gitmodules to ${backup_dir}_gitmodules"
    fi
    
    # Backup git config
    git config --list > "${backup_dir}_config.txt" 2>/dev/null || true
    print_success "Backed up git config to ${backup_dir}_config.txt"
}

# Option 1: Remove submodules completely
remove_submodules() {
    print_status "========================================="
    print_status "OPTION 1: Removing Unpopulated Submodules"
    print_status "========================================="
    
    backup_state
    
    print_status "Step 1: Deinitializing submodules..."
    git submodule deinit -f clawdbot_repo 2>/dev/null || true
    git submodule deinit -f freqtrade 2>/dev/null || true
    git submodule deinit -f --all 2>/dev/null || true
    print_success "Submodules deinitialized"
    
    print_status "Step 2: Removing from git config..."
    git config --remove-section submodule.clawdbot_repo 2>/dev/null || true
    git config --remove-section submodule.freqtrade 2>/dev/null || true
    print_success "Git config cleaned"
    
    print_status "Step 3: Removing .git/modules..."
    rm -rf .git/modules/clawdbot_repo 2>/dev/null || true
    rm -rf .git/modules/freqtrade 2>/dev/null || true
    print_success ".git/modules cleaned"
    
    print_status "Step 4: Removing from git index..."
    git rm --cached clawdbot_repo 2>/dev/null || true
    git rm --cached freqtrade 2>/dev/null || true
    print_success "Git index cleaned"
    
    print_status "Step 5: Removing .gitmodules..."
    if [ -f .gitmodules ]; then
        rm -f .gitmodules
        git add .gitmodules 2>/dev/null || true
        print_success ".gitmodules removed"
    else
        print_warning ".gitmodules not found (already removed)"
    fi
    
    print_status "Step 6: Removing empty directories..."
    rm -rf clawdbot_repo freqtrade
    print_success "Empty directories removed"
    
    print_status "Step 7: Staging changes..."
    git add -A
    print_success "Changes staged"
    
    print_status "Step 8: Checking status..."
    git status
    
    print_success "========================================="
    print_success "Submodules removed successfully!"
    print_success "========================================="
    print_warning "Next steps:"
    echo "  1. Review changes with: git status"
    echo "  2. Commit changes with: git commit -m 'fix(submodules): remove unpopulated submodules'"
    echo "  3. Push changes with: git push origin main"
}

# Option 2: Fix submodules with correct URLs
fix_submodules() {
    print_status "========================================="
    print_status "OPTION 2: Fixing Submodules with Correct URLs"
    print_status "========================================="
    
    backup_state
    
    print_warning "This option requires correct repository URLs"
    print_status "Current .gitmodules content:"
    
    if [ -f .gitmodules ]; then
        cat .gitmodules
    else
        print_warning ".gitmodules not found"
    fi
    
    print_status "Step 1: Removing empty directories..."
    rm -rf clawdbot_repo freqtrade
    print_success "Empty directories removed"
    
    print_status "Step 2: Syncing submodules..."
    git submodule sync --recursive || print_warning "Sync failed (expected if URLs are invalid)"
    
    print_status "Step 3: Updating submodules..."
    git submodule update --init --recursive || print_error "Update failed - check URLs in .gitmodules"
    
    print_status "Step 4: Checking submodule status..."
    git submodule status --recursive
    
    print_success "========================================="
    print_success "Submodule fix attempted!"
    print_success "========================================="
    print_warning "If this failed, you need to:"
    echo "  1. Edit .gitmodules with correct repository URLs"
    echo "  2. Run: git submodule sync --recursive"
    echo "  3. Run: git submodule update --init --recursive"
}

# Option 3: Convert to regular directories
convert_to_directories() {
    print_status "========================================="
    print_status "OPTION 3: Converting to Regular Directories"
    print_status "========================================="
    
    backup_state
    
    print_status "Step 1: Removing .gitmodules..."
    rm -f .gitmodules
    print_success ".gitmodules removed"
    
    print_status "Step 2: Removing from git cache..."
    git rm --cached clawdbot_repo freqtrade 2>/dev/null || true
    print_success "Git cache cleaned"
    
    print_status "Step 3: Removing empty directories..."
    rm -rf clawdbot_repo freqtrade
    print_success "Empty directories removed"
    
    print_status "Step 4: Creating regular directories..."
    mkdir -p clawdbot_repo freqtrade
    
    echo "# Clawdbot Repository" > clawdbot_repo/README.md
    echo "" >> clawdbot_repo/README.md
    echo "This directory contains Clawdbot integration code." >> clawdbot_repo/README.md
    echo "" >> clawdbot_repo/README.md
    echo "Previously a git submodule, now converted to regular directory." >> clawdbot_repo/README.md
    
    echo "# FreqTrade Integration" > freqtrade/README.md
    echo "" >> freqtrade/README.md
    echo "This directory contains FreqTrade integration code." >> freqtrade/README.md
    echo "" >> freqtrade/README.md
    echo "Previously a git submodule, now converted to regular directory." >> freqtrade/README.md
    
    print_success "Regular directories created with README files"
    
    print_status "Step 5: Staging changes..."
    git add .
    print_success "Changes staged"
    
    print_status "Step 6: Checking status..."
    git status
    
    print_success "========================================="
    print_success "Converted to regular directories!"
    print_success "========================================="
    print_warning "Next steps:"
    echo "  1. Review changes with: git status"
    echo "  2. Commit changes with: git commit -m 'fix(structure): convert submodules to regular directories'"
    echo "  3. Push changes with: git push origin main"
}

# Display usage information
show_usage() {
    echo "========================================="
    echo "Git Submodule Fix Script"
    echo "========================================="
    echo ""
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  remove    - Remove unpopulated submodules (RECOMMENDED)"
    echo "  fix       - Fix submodules with correct URLs"
    echo "  convert   - Convert submodules to regular directories"
    echo "  status    - Show current submodule status"
    echo ""
    echo "Examples:"
    echo "  $0 remove"
    echo "  $0 fix"
    echo "  $0 convert"
    echo ""
}

# Show current status
show_status() {
    print_status "========================================="
    print_status "Current Git Submodule Status"
    print_status "========================================="
    
    print_status "Git Status:"
    git status
    
    echo ""
    print_status "Submodule Status:"
    git submodule status --recursive || print_warning "No submodules or error reading submodules"
    
    echo ""
    print_status ".gitmodules content:"
    if [ -f .gitmodules ]; then
        cat .gitmodules
    else
        print_warning ".gitmodules not found"
    fi
    
    echo ""
    print_status "Submodule directories:"
    ls -la clawdbot_repo 2>/dev/null || print_warning "clawdbot_repo not found"
    ls -la freqtrade 2>/dev/null || print_warning "freqtrade not found"
    
    echo ""
    print_status "Git config (submodule entries):"
    git config --list | grep submodule || print_warning "No submodule entries in git config"
}

# Main script logic
main() {
    check_git_repo
    
    case "${1:-}" in
        remove)
            remove_submodules
            ;;
        fix)
            fix_submodules
            ;;
        convert)
            convert_to_directories
            ;;
        status)
            show_status
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
