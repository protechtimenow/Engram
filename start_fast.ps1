#!/usr/bin/env pwsh
# FAST Dual-Agent Startup Script
# Optimized for speed - GLM (main) + StepFun (engram)
# No typing delays, streaming responses, 15s timeout

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FAST Dual-Agent System" -ForegroundColor Cyan
Write-Host "  GLM 4.7 Flash (main) + Engram" -ForegroundColor Cyan
Write-Host "  Timeout: 15s | Streaming: ON" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set API Keys
$env:STEPFUN_API_KEY = "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"
$env:GLM_API_KEY = "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"
$env:OPENROUTER_API_KEY = $env:STEPFUN_API_KEY
$env:OPENCLAW_GATEWAY_TOKEN = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"

# Fast config
$env:ENGRAM_CONFIG = "config/engram_fast.json"
$env:ENGRAM_FAST_MODE = "1"
$env:ENGRAM_STREAMING = "1"

Write-Host "[*] API Keys configured" -ForegroundColor Green
Write-Host "[*] Fast mode enabled (15s timeout)" -ForegroundColor Green
Write-Host "[*] Streaming responses enabled" -ForegroundColor Green

# Stop existing processes
Write-Host "[*] Stopping existing processes..." -ForegroundColor Yellow
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process pythonw -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Start OpenClaw Gateway (FAST MODE)
Write-Host "[*] Starting OpenClaw Gateway (FAST)..." -ForegroundColor Yellow
$gatewayPath = "C:\Users\OFFRSTAR0\Engram\clawdbot_repo"
$gatewayArgs = @{
    FilePath = "cmd.exe"
    ArgumentList = "/k cd /d `"$gatewayPath`" && echo ======================================== && echo   OpenClaw Gateway - FAST MODE && echo   Model: GLM 4.7 Flash && echo   Port: 17500 && echo   Timeout: 15 seconds && echo   Ping: 10s && echo ======================================== && set OPENCLAW_GATEWAY_TOKEN=$env:OPENCLAW_GATEWAY_TOKEN && set GLM_API_KEY=$env:GLM_API_KEY && set OPENROUTER_API_KEY=$env:OPENROUTER_API_KEY && node dist/entry.js gateway --port 17500 --token $env:OPENCLAW_GATEWAY_TOKEN"
    WindowStyle = "Normal"
    WorkingDirectory = $gatewayPath
}
Start-Process @gatewayArgs

Write-Host "[*] Gateway starting... waiting 3 seconds" -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start Engram Agent (FAST MODE)
Write-Host "[*] Starting Engram Agent (FAST)..." -ForegroundColor Yellow
$engramPath = "C:\Users\OFFRSTAR0\Engram"
$engramArgs = @{
    FilePath = "cmd.exe"
    ArgumentList = "/k cd /d `"$engramPath`" && echo ======================================== && echo   Engram Agent - FAST MODE && echo   Config: engram_fast.json && echo   Gateway: ws://localhost:17500 && echo   Mind Modality: ENABLED && echo ======================================== && set ENGRAM_CONFIG=config/engram_fast.json && set ENGRAM_FAST_MODE=1 && set OPENROUTER_API_KEY=$env:OPENROUTER_API_KEY && set OPENCLAW_GATEWAY_TOKEN=$env:OPENCLAW_GATEWAY_TOKEN && .venv\Scripts\python.exe run_engram_fast.py"
    WindowStyle = "Normal"
    WorkingDirectory = $engramPath
}
Start-Process @engramArgs

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  FAST SYSTEM STARTED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Gateway:    ws://localhost:17500" -ForegroundColor Cyan
Write-Host "Model:      GLM 4.7 Flash (fast)" -ForegroundColor Cyan
Write-Host "Timeout:    15 seconds" -ForegroundColor Cyan
Write-Host "Ping:       10 seconds" -ForegroundColor Cyan
Write-Host "Streaming:  ON" -ForegroundColor Cyan
Write-Host "Mind Mode:  ACTIVE" -ForegroundColor Cyan
Write-Host ""
Write-Host "Telegram:   @Freqtrad3_bot" -ForegroundColor Yellow
Write-Host ""
Write-Host "Commands:" -ForegroundColor White
Write-Host "  /engram analyze BTC/USD" -ForegroundColor Gray
Write-Host "  /engram signal ETH/USD" -ForegroundColor Gray
Write-Host "  /engram quick [any query]" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
