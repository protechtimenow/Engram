#!/usr/bin/env python3
"""
Update LMStudio URLs in all configuration files and Python scripts
Changes from http://100.118.172.23:1234 to http://100.118.172.23:1234
"""

import os
import re
from pathlib import Path

OLD_URL = "100.118.172.23:1234"
NEW_URL = "100.118.172.23:1234"

def update_file(filepath):
    """Update LMStudio URL in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file contains old URL
        if OLD_URL not in content:
            return False
        
        # Replace old URL with new URL
        new_content = content.replace(OLD_URL, NEW_URL)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Count replacements
        count = content.count(OLD_URL)
        print(f"✅ Updated {filepath.name}: {count} replacement(s)")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

def main():
    """Main update function"""
    print("=" * 80)
    print("UPDATING LMSTUDIO URLs")
    print(f"FROM: {OLD_URL}")
    print(f"TO:   {NEW_URL}")
    print("=" * 80)
    
    # Find all Python files
    python_files = list(Path('.').glob('*.py'))
    python_files.extend(Path('.').glob('**/*.py'))
    
    # Find all JSON config files
    json_files = list(Path('.').glob('*.json'))
    json_files.extend(Path('.').glob('config/**/*.json'))
    
    all_files = python_files + json_files
    
    updated_count = 0
    for filepath in all_files:
        if update_file(filepath):
            updated_count += 1
    
    print("=" * 80)
    print(f"✅ Updated {updated_count} file(s)")
    print("=" * 80)

if __name__ == "__main__":
    main()
