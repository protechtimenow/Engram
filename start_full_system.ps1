#!/usr/bin/env pwsh
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Full ClawdBOT + Engram System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Load environment variables from .env file
$envPath = "C:\Users\OFFRSTAR0\Engram\.env"
if (Test-Path $envPath) {
    Write-Host "[*] Loading environment variables from .env..." -ForegroundColor Yellow
    Get-Content $envPath | ForEach-Object {
        if ($_ -match '^([^#][^=]*)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Stop any existing processes
Write-Host "[*] Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*openclaw*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start ClawdBOT Gateway with Telegram (Port 17500)
Write-Host "[*] Starting ClawdBOT Gateway with Telegram..." -ForegroundColor Yellow
$clawdPath = "C:\Users\OFFRSTAR0\Engram\clawdbot_repo"
$env:OPENCLAW_GATEWAY_TOKEN = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$clawdPath'; `$env:OPENROUTER_API_KEY='$env:OPENROUTER_API_KEY'; `$env:OPENCLAW_GATEWAY_TOKEN='2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc'; node dist/entry.js gateway --token '2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc'" -WindowStyle Normal

# Wait for gateway to initialize
Write-Host "[*] Waiting for gateway to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Start Engram Agent (uses OpenRouter directly)
Write-Host "[*] Starting Engram Agent..." -ForegroundColor Yellow
$engramPath = "C:\Users\OFFRSTAR0\Engram"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$engramPath'; python engram_clawdbot_integration.py" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "All services starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Telegram Bot: @Freqtrad3_bot" -ForegroundColor Cyan
Write-Host "Gateway: ws://localhost:17500" -ForegroundColor Cyan
Write-Host "AI Provider: OpenRouter (GLM 4.7 Flash + StepFun)" -ForegroundColor Cyan
Write-Host "Primary Model: GLM 4.7 Flash (Zhipu AI - Engram Mind)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Send /start to your Telegram bot to begin!" -ForegroundColor Yellow
Start-Sleep -Seconds 2
