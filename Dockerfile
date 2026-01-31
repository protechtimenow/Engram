FROM python:3.13-slim

# Set working directory in the container
WORKDIR /app

# Copy your Engram code into the container
COPY . /app

# Install dependencies
RUN python -m pip install --upgrade pip \
    && pip install freqtrade

# Ensure __init__.py files for Python module recognition
RUN mkdir -p src/core src/trading src/telegram \
    && touch src/__init__.py src/core/__init__.py src/trading/__init__.py src/telegram/__init__.py

# Expose any ports you might need (e.g., 1234 if needed)
EXPOSE 1234

# Default command to run your Engram-FreqTrade integration
CMD ["python", "scripts/launch_engram_trader.py", "--config", "config/engram_freqtrade_config.json"]
