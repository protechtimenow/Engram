#!/bin/bash
# Fix invalid filenames in git history
# Run this on Linux/Mac or WSL

# Remove the invalid file from history
git filter-repo --path 'archive/?dry' --invert-paths

# Force push to update the repository
git push origin --force --all
