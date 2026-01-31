#!/usr/bin/env bash
set -e  # Exit on error

echo "=== Creating or updating venv ==="
sudo apt-get update
sudo apt-get install -y python3-venv

cd /root/Engram
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "=== Activating venv ==="
source venv/bin/activate

echo "=== Installing freqtrade ==="
pip install --upgrade pip
pip install freqtrade

echo "=== Ensuring __init__.py files ==="
mkdir -p src/core src/trading src/telegram
touch src/__init__.py
touch src/core/__init__.py
touch src/trading/__init__.py
touch src/telegram/__init__.py

echo "=== Setup complete. Deactivating venv ==="
deactivate
