#!/usr/bin/env python3
"""
Test LMStudio API connection.
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_lmstudio():
    """Test LMStudio API."""
    url = "http://192.168.56.1:1234/v1/chat/completions"

    payload = {
        "model": "glm-4.7b-chat",
        "messages": [{"role": "user", "content": "Hello, this is a test. Please respond with a short message."}],
        "max_tokens": 100,
        "temperature": 0.7,
        "stream": False
    }

    try:
        logger.info(f"Testing LMStudio at {url}...")
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        logger.info("✅ LMStudio responded!")
        logger.info(f"Response: {result}")

        if 'choices' in result and result['choices']:
            message = result['choices'][0]['message']['content']
            logger.info(f"AI Response: {message}")
        else:
            logger.warning("No choices in response")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ LMStudio connection failed: {e}")
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    test_lmstudio()
