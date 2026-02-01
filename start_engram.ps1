# Engram Bot Startup Script for PowerShell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Engram + ClawdBot Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if ClawdBot is running
Write-Host "Checking ClawdBot Gateway..." -ForegroundColor Yellow
$clawdbotRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:18789/" -TimeoutSec 2 -ErrorAction SilentlyContinue
    $clawdbotRunning = $true
} catch {
    $clawdbotRunning = $false
}

if ($clawdbotRunning) {
    Write-Host "✅ ClawdBot is running on port 18789" -ForegroundColor Green
} else {
    Write-Host "❌ ClawdBot is NOT running on port 18789" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start ClawdBot first:" -ForegroundColor Yellow
    Write-Host "  1. Open a new PowerShell terminal" -ForegroundColor White
    Write-Host "  2. Run: cd ..; clawdbot gateway" -ForegroundColor White
    Write-Host "  3. Then run this script again" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Starting Engram Bot..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Activate virtual environment and run bot
& "$PSScriptRoot\.venv\Scripts\Activate.ps1"
python "$PSScriptRoot\enhanced_engram_launcher.py"
