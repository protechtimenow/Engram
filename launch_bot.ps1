# Enhanced Engram Bot Launcher for PowerShell
# This script loads environment variables and launches the bot

Write-Host "🚀 Enhanced Engram Bot Launcher" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Load environment variables
Write-Host "📂 Step 1: Loading environment variables..." -ForegroundColor Yellow
. .\load_env.ps1

if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
    Write-Host "`n❌ Failed to load environment variables" -ForegroundColor Red
    exit 1
}

# Verify critical environment variables
Write-Host "`n🔍 Step 2: Verifying critical variables..." -ForegroundColor Yellow

$requiredVars = @{
    "TELEGRAM_BOT_TOKEN" = $env:TELEGRAM_BOT_TOKEN
    "TELEGRAM_CHAT_ID" = $env:TELEGRAM_CHAT_ID
    "LMSTUDIO_URL" = $env:LMSTUDIO_URL
}

$missingVars = @()
foreach ($var in $requiredVars.GetEnumerator()) {
    if ([string]::IsNullOrWhiteSpace($var.Value)) {
        Write-Host "   ❌ Missing: $($var.Key)" -ForegroundColor Red
        $missingVars += $var.Key
    }
    else {
        $displayValue = $var.Value
        # Mask sensitive tokens
        if ($var.Key -eq "TELEGRAM_BOT_TOKEN") {
            $displayValue = $var.Value.Substring(0, 10) + "..." + $var.Value.Substring($var.Value.Length - 4)
        }
        Write-Host "   ✅ $($var.Key) = $displayValue" -ForegroundColor Green
    }
}

if ($missingVars.Count -gt 0) {
    Write-Host "`n❌ Missing required environment variables: $($missingVars -join ', ')" -ForegroundColor Red
    Write-Host "   Please update your .env file and try again." -ForegroundColor Yellow
    exit 1
}

# Launch the bot
Write-Host "`n🤖 Step 3: Launching Enhanced Engram Bot..." -ForegroundColor Yellow
Write-Host "   Press Ctrl+C to stop the bot`n" -ForegroundColor Gray

python enhanced_engram_launcher.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Bot exited with error code: $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n✅ Bot stopped successfully" -ForegroundColor Green
