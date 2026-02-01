#!/bin/bash

echo "=========================================="
echo "Engram + ClawdBot Startup Script"
echo "=========================================="
echo ""

# Check if ClawdBot is already running
if curl -s http://127.0.0.1:18789/health > /dev/null 2>&1; then
    echo "✅ ClawdBot is already running on port 18789"
else
    echo "❌ ClawdBot is NOT running on port 18789"
    echo ""
    echo "Please start ClawdBot manually first:"
    echo "  1. Open ClawdBot application"
    echo "  2. Ensure it's running on ws://127.0.0.1:18789"
    echo "  3. Then run this script again"
    echo ""
    exit 1
fi

echo ""
echo "Starting Engram Bot..."
echo "=========================================="

# Activate virtual environment and run bot
source .venv/Scripts/activate
python enhanced_engram_launcher.py
