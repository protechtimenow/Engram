# Telegram Bot Setup Guide

## 🤖 Creating a Telegram Bot with BotFather

### Step 1: Find and Start BotFather
1. Open Telegram
2. Search for `@BotFather` (it has a blue checkmark)
3. Click "Start" to begin the conversation

### Step 2: Create a New Bot
1. Send the command: `/newbot`
2. BotFather will ask for a bot name (can be anything, e.g., "Engram Trader")
3. BotFather will ask for a username (must end in `bot`, e.g., "EngramTraderBot")

### Step 3: Get Your Bot Token
BotFather will respond with your bot token like this:
```
Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Step 4: Get Your Chat ID
1. Send any message to your new bot
2. Use this method to get your Chat ID:
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Replace `<YOUR_BOT_TOKEN>` with your actual token
   - Look for `"chat": {"id": 123456789}` in the response

### Step 5: Test the Connection
```bash
# Test your bot token
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
```

## 🔧 Current Configuration Files

Once you have your token and chat ID, update them in:
- `engram_freqtrade_config.json` (full integration)
- `freqtrade_config.json` (basic config)

## 📝 Example Configuration

```json
"telegram": {
    "enabled": true,
    "token": "YOUR_BOT_TOKEN_HERE",
    "chat_id": "YOUR_CHAT_ID_HERE"
}
```

## 🚀 Next Steps After Setup

1. Update the config file with your token and chat ID
2. Test the bot with FreqTrade
3. Enable advanced Engram features when dependencies are resolved

## 🛡️ Security Notes

- Never share your bot token publicly
- Anyone with the token can control your bot
- Keep your chat ID private as well

Ready to proceed? Follow the steps above and let me know when you have your bot token and chat ID!