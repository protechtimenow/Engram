import os
import sys
sys.path.insert(0, '.')

# Simulate what run_engram_fast.py does
config_path = 'config/engram_fast.json'
import json
fast_config = {}
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        fast_config = json.load(f)

config = {
    'clawdbot_token': os.getenv('OPENCLAW_GATEWAY_TOKEN', '2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc'),
}

print(f'Environment OPENCLAW_GATEWAY_TOKEN: {repr(os.getenv("OPENCLAW_GATEWAY_TOKEN"))}')
print(f'Config clawdbot_token: {repr(config["clawdbot_token"])}')
print(f'Config file clawdbot.token: {repr(fast_config.get("clawdbot", {}).get("token"))}')
