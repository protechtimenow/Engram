#!/bin/bash

################################################################################
# TRANSFER FILES FROM SANDBOX TO LOCAL REPOSITORY
# 
# This script helps identify and prepare files for transfer from the Vercel
# sandbox to your local Engram repository at /mnt/c/Users/OFFRSTAR0/Engram
#
# Usage: ./TRANSFER_FILES_SCRIPT.sh [option]
#   list     - List all files to transfer
#   archive  - Create tar.gz archive of all files
#   critical - Show only critical production files
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
SANDBOX_DIR="/vercel/sandbox"
ARCHIVE_NAME="engram_production_files_$(date +%Y%m%d_%H%M%S).tar.gz"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}ENGRAM FILE TRANSFER UTILITY${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to list critical production files
list_critical_files() {
    echo -e "${GREEN}CRITICAL PRODUCTION FILES:${NC}"
    echo ""
    
    local critical_files=(
        "enhanced_engram_launcher.py"
        "enhanced_engram_launcher_v2.py"
        "simple_engram_launcher.py"
        "live_trading_production_tests.py"
        "PRODUCTION_DEPLOYMENT_GUIDE.md"
        "FINAL_PRODUCTION_CHECKLIST.md"
        "COMPLETE_TEST_COVERAGE_REPORT.md"
    )
    
    for file in "${critical_files[@]}"; do
        if [ -f "$SANDBOX_DIR/$file" ]; then
            size=$(ls -lh "$SANDBOX_DIR/$file" | awk '{print $5}')
            echo -e "  ${GREEN}✓${NC} $file ($size)"
        else
            echo -e "  ${RED}✗${NC} $file (NOT FOUND)"
        fi
    done
    echo ""
}

# Function to list all test files
list_test_files() {
    echo -e "${YELLOW}TEST SUITE FILES:${NC}"
    echo ""
    
    find "$SANDBOX_DIR" -maxdepth 1 -name "*test*.py" -type f | while read file; do
        filename=$(basename "$file")
        size=$(ls -lh "$file" | awk '{print $5}')
        echo -e "  ${YELLOW}•${NC} $filename ($size)"
    done
    echo ""
}

# Function to list all documentation files
list_documentation_files() {
    echo -e "${BLUE}DOCUMENTATION FILES:${NC}"
    echo ""
    
    find "$SANDBOX_DIR" -maxdepth 1 -name "*.md" -type f | while read file; do
        filename=$(basename "$file")
        size=$(ls -lh "$file" | awk '{print $5}')
        echo -e "  ${BLUE}•${NC} $filename ($size)"
    done
    echo ""
}

# Function to list all result files
list_result_files() {
    echo -e "${GREEN}TEST RESULT FILES:${NC}"
    echo ""
    
    find "$SANDBOX_DIR" -maxdepth 1 -name "*results*.json" -o -name "*RESULTS*.json" -o -name "FINAL_*.json" | while read file; do
        filename=$(basename "$file")
        size=$(ls -lh "$file" | awk '{print $5}')
        echo -e "  ${GREEN}•${NC} $filename ($size)"
    done
    echo ""
}

# Function to create archive
create_archive() {
    echo -e "${GREEN}Creating archive of all production files...${NC}"
    echo ""
    
    cd "$SANDBOX_DIR"
    
    # Create list of files to archive
    local files_to_archive=(
        # Critical launchers
        enhanced_engram_launcher.py
        enhanced_engram_launcher_v2.py
        simple_engram_launcher.py
        
        # Test suites
        live_trading_production_tests.py
        security_authentication_tests.py
        database_persistence_tests.py
        websocket_realtime_tests.py
        config_validation_advanced_tests.py
        performance_benchmark_load_tests.py
        error_recovery_resilience_tests.py
        lmstudio_endpoint_tests.py
        integration_test_with_new_endpoint.py
        real_telegram_integration_test.py
        test_enhanced_launcher.py
        test_enhanced_launcher_standalone.py
        
        # Utility scripts
        update_lmstudio_urls.py
        consolidate_all_tests.py
        
        # Documentation
        PRODUCTION_DEPLOYMENT_GUIDE.md
        FINAL_PRODUCTION_CHECKLIST.md
        COMPLETE_TEST_COVERAGE_REPORT.md
        LMSTUDIO_CONFIGURATION_GUIDE.md
        ENHANCED_LAUNCHER_GUIDE.md
        GIT_COMMIT_PROMPT.md
        GITHUB_UPDATE_GUIDE.md
        PROMPTS_FOR_FUTURE_SESSIONS.md
        SESSION_SUMMARY.md
        LMSTUDIO_ENDPOINT_UPDATE_REPORT.md
        TESTING_COMPLETE_SUMMARY.md
        FINAL_TESTING_SUMMARY.md
        COMPREHENSIVE_TEST_SUMMARY.md
        LMSTUDIO_TROUBLESHOOTING_SUMMARY.md
        FINAL_LMSTUDIO_RESOLUTION.md
        REAL_CHAT_ID_VERIFICATION.md
        
        # Test results
        live_trading_production_test_results.json
        security_authentication_test_results.json
        database_persistence_test_results.json
        websocket_realtime_test_results.json
        config_validation_advanced_test_results.json
        performance_benchmark_test_results.json
        error_recovery_test_results.json
        lmstudio_endpoint_test_results.json
        integration_test_results.json
        real_telegram_test_results.json
        FINAL_DELIVERABLES_SUMMARY.json
        FINAL_CONSOLIDATED_TEST_RESULTS.json
        CONSOLIDATED_TEST_RESULTS.json
        
        # Summary files
        PRODUCTION_READY_FINAL.md
        DEPLOYMENT_READY.md
        DEPLOYMENT_SUMMARY.md
        COMPREHENSIVE_TESTING_REPORT.md
        
        # Quick reference
        QUICK_START.txt
        TESTING_COMPLETE_FINAL.txt
        FINAL_TESTING_SUMMARY.txt
        LMSTUDIO_RESOLUTION_SUMMARY.txt
        LMSTUDIO_ISSUE_RESOLVED.txt
        CHAT_ID_VERIFICATION_SUMMARY.txt
        WHAT_TO_PROMPT.txt
        
        # Scripts
        QUICK_GITHUB_COMMANDS.sh
        clawdbot_manager.sh
    )
    
    # Filter to only existing files
    local existing_files=()
    for file in "${files_to_archive[@]}"; do
        if [ -f "$file" ]; then
            existing_files+=("$file")
        fi
    done
    
    # Create archive
    if [ ${#existing_files[@]} -gt 0 ]; then
        tar -czf "$ARCHIVE_NAME" "${existing_files[@]}"
        
        echo -e "${GREEN}✓ Archive created successfully!${NC}"
        echo ""
        echo -e "  File: ${YELLOW}$ARCHIVE_NAME${NC}"
        echo -e "  Size: $(ls -lh "$ARCHIVE_NAME" | awk '{print $5}')"
        echo -e "  Files: ${#existing_files[@]}"
        echo ""
        echo -e "${BLUE}To extract on your local machine:${NC}"
        echo -e "  tar -xzf $ARCHIVE_NAME"
        echo ""
    else
        echo -e "${RED}✗ No files found to archive${NC}"
        exit 1
    fi
}

# Function to show file statistics
show_statistics() {
    echo -e "${BLUE}FILE STATISTICS:${NC}"
    echo ""
    
    local py_count=$(find "$SANDBOX_DIR" -maxdepth 1 -name "*.py" -type f | wc -l)
    local md_count=$(find "$SANDBOX_DIR" -maxdepth 1 -name "*.md" -type f | wc -l)
    local json_count=$(find "$SANDBOX_DIR" -maxdepth 1 -name "*.json" -type f | wc -l)
    local txt_count=$(find "$SANDBOX_DIR" -maxdepth 1 -name "*.txt" -type f | wc -l)
    local sh_count=$(find "$SANDBOX_DIR" -maxdepth 1 -name "*.sh" -type f | wc -l)
    
    local total=$((py_count + md_count + json_count + txt_count + sh_count))
    
    echo -e "  Python files (.py):       ${GREEN}$py_count${NC}"
    echo -e "  Documentation (.md):      ${BLUE}$md_count${NC}"
    echo -e "  JSON files (.json):       ${YELLOW}$json_count${NC}"
    echo -e "  Text files (.txt):        $txt_count"
    echo -e "  Shell scripts (.sh):      $sh_count"
    echo -e "  ${GREEN}TOTAL:                    $total${NC}"
    echo ""
}

# Main script logic
case "${1:-list}" in
    list)
        show_statistics
        list_critical_files
        list_test_files
        list_documentation_files
        list_result_files
        ;;
    
    critical)
        list_critical_files
        ;;
    
    archive)
        create_archive
        ;;
    
    stats)
        show_statistics
        ;;
    
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo ""
        echo "Usage: $0 [option]"
        echo "  list     - List all files to transfer (default)"
        echo "  critical - Show only critical production files"
        echo "  archive  - Create tar.gz archive of all files"
        echo "  stats    - Show file statistics"
        exit 1
        ;;
esac

echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}Transfer these files to:${NC}"
echo -e "  /mnt/c/Users/OFFRSTAR0/Engram"
echo -e "${BLUE}================================${NC}"
