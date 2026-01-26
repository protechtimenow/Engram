import json
import requests
import sys

def verify_telegram():
    print("🔍 Reading configuration...")
    try:
        with open('simple_config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return

    tg_config = config.get('telegram', {})
    token = tg_config.get('token')
    chat_id = tg_config.get('chat_id')

    print(f"📋 Config Check:")
    print(f"   Token found: {'Yes' if token else 'No'}")
    print(f"   Chat ID: {chat_id} (Type: {type(chat_id).__name__})")

    if not isinstance(chat_id, int):
        # FreqTrade often requires int, but the API accepts string. 
        # We explicitly fixed it to int in the config, so checking that.
        print("⚠️  Warning: Chat ID is not an integer in config (FreqTrade usually prefers int).")
    else:
        print("✅ Chat ID format is correct (int).")

    if not token or not chat_id:
        print("❌ Token or Chat ID missing.")
        return

    print("\n🚀 Testing connectivity to Telegram API...")
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        resp = requests.get(url, timeout=10)
        resp_data = resp.json()
        if resp_data.get('ok'):
            bot_name = resp_data['result']['first_name']
            username = resp_data['result']['username']
            print(f"✅ Bot Connection Successful!")
            print(f"   Bot Name: {bot_name}")
            print(f"   Username: @{username}")
        else:
            print(f"❌ Bot connection failed: {resp_data}")
            return
    except Exception as e:
        print(f"❌ Network request failed: {e}")
        return

    print("\n📨 Sending test message to chat...")
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': '🔔 Verification: Engram-FreqTrade config is valid and Chat ID is correct.'
    }
    try:
        resp = requests.post(send_url, json=payload, timeout=10)
        resp_data = resp.json()
        if resp_data.get('ok'):
            print("✅ Message delivered successfully!")
        else:
            print(f"❌ Message failed: {resp_data}")
    except Exception as e:
        print(f"❌ Send request failed: {e}")

if __name__ == "__main__":
    verify_telegram()
