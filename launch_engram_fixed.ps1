# Enhanced Engram Bot Launcher - With Timeout Fixes
# This script sets all required environment variables and launches the bot

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "🚀 ENHANCED ENGRAM BOT LAUNCHER - TIMEOUT FIXES APPLIED" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

# LMStudio Configuration
Write-Host "📡 Configuring LMStudio..." -ForegroundColor Yellow
$env:LMSTUDIO_URL = "http://100.118.172.23:1234"
$env:LMSTUDIO_TIMEOUT = "180"  # 3 minutes - adjust if needed
Write-Host "   URL: $env:LMSTUDIO_URL" -ForegroundColor Gray
Write-Host "   Timeout: $env:LMSTUDIO_TIMEOUT seconds" -ForegroundColor Gray
Write-Host ""

# Telegram Configuration
Write-Host "📱 Configuring Telegram..." -ForegroundColor Yellow
$env:TELEGRAM_BOT_TOKEN = "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
$env:TELEGRAM_CHAT_ID = "1007321485"
Write-Host "   Bot: Freqtrad3_bot" -ForegroundColor Gray
Write-Host "   Chat ID: $env:TELEGRAM_CHAT_ID" -ForegroundColor Gray
Write-Host ""

# Test LMStudio connection
Write-Host "🔍 Testing LMStudio connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$env:LMSTUDIO_URL/v1/models" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ LMStudio is reachable!" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Warning: Could not reach LMStudio" -ForegroundColor Red
    Write-Host "   The bot will use fallback AI mode" -ForegroundColor Yellow
    Write-Host "   Make sure LMStudio is running at $env:LMSTUDIO_URL" -ForegroundColor Yellow
}
Write-Host ""

# Launch bot
Write-Host "🤖 Launching Enhanced Engram Bot..." -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "   • Send 'hi' to @Freqtrad3_bot to test" -ForegroundColor Gray
Write-Host "   • Use /status to check bot status" -ForegroundColor Gray
Write-Host "   • Use /analyze BTC/USDT for market analysis" -ForegroundColor Gray
Write-Host "   • Press Ctrl+C to stop the bot" -ForegroundColor Gray
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

# Launch
python enhanced_engram_launcher.py

# Cleanup message
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "👋 Bot stopped. Goodbye!" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
