import os
# Check if env var is set to empty string vs not set at all
print(f'OPENCLAW_GATEWAY_TOKEN in os.environ: {"OPENCLAW_GATEWAY_TOKEN" in os.environ}')
print(f'Value: {repr(os.getenv("OPENCLAW_GATEWAY_TOKEN"))}')
# Check default behavior
token = os.getenv('OPENCLAW_GATEWAY_TOKEN', '2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc')
print(f'Token after default: {repr(token)}')
