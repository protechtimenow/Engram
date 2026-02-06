#!/usr/bin/env pwsh
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Agent-to-Agent: Engram + ClawdBOT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Load environment variables from .env file
$envPath = "C:\Users\OFFRSTAR0\Engram\.env"
if (Test-Path $envPath) {
    Write-Host "[*] Loading environment variables..." -ForegroundColor Yellow
    Get-Content $envPath | ForEach-Object {
        if ($_ -match '^([^#][^=]*)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Agent-to-Agent Configuration
# Same OpenRouter account, different models for each agent
$OPENROUTER_KEY = "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"

# Engram Agent -> StepFun
$ENGRAM_MODEL = "stepfun/step-3.5-flash:free"

# ClawdBOT Gateway -> GLM
$CLAWDBOT_MODEL = "openrouter/z-ai/glm-4.7-flash"

Write-Host ""
Write-Host "[*] Agent Configuration:" -ForegroundColor Yellow
Write-Host "    Engram Agent  -> StepFun ($ENGRAM_MODEL)" -ForegroundColor Cyan
Write-Host "    ClawdBOT      -> GLM ($CLAWDBOT_MODEL)" -ForegroundColor Cyan
Write-Host ""

# Stop any existing processes
Write-Host "[*] Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*openclaw*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start ClawdBOT Gateway with GLM (Port 17500)
Write-Host "[*] Starting ClawdBOT Gateway (GLM)..." -ForegroundColor Yellow
$clawdPath = "C:\Users\OFFRSTAR0\Engram\clawdbot_repo"
$env:OPENCLAW_GATEWAY_TOKEN = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"

# ClawdBOT uses GLM model
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$clawdPath'; `$env:OPENROUTER_API_KEY='$OPENROUTER_KEY'; `$env:ENGRAM_MODEL='$CLAWDBOT_MODEL'; `$env:OPENCLAW_GATEWAY_TOKEN='2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc'; node dist/entry.js gateway --token '2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc'" -WindowStyle Normal

# Wait for gateway to initialize
Write-Host "[*] Waiting for gateway to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Start Engram Agent with StepFun
Write-Host "[*] Starting Engram Agent (StepFun)..." -ForegroundColor Yellow
$engramPath = "C:\Users\OFFRSTAR0\Engram"

# Engram uses StepFun model
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$engramPath'; `$env:OPENROUTER_API_KEY='$OPENROUTER_KEY'; `$env:ENGRAM_MODEL='$ENGRAM_MODEL'; python engram_clawdbot_integration.py" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Agent-to-Agent System Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Telegram Bot: @Freqtrad3_bot" -ForegroundColor Cyan
Write-Host "Gateway: ws://localhost:17500" -ForegroundColor Cyan
Write-Host ""
Write-Host "Agent Routing:" -ForegroundColor Yellow
Write-Host "  ClawdBOT (Telegram) -> GLM 4.7 Flash" -ForegroundColor Cyan
Write-Host "  Engram (Trading)    -> StepFun 3.5 Flash" -ForegroundColor Cyan
Write-Host ""
Write-Host "Send /start to your Telegram bot!" -ForegroundColor Yellow
Start-Sleep -Seconds 2
