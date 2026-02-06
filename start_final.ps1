#!/usr/bin/env pwsh
# Final Dual-Agent Startup Script
# GLM (main) + StepFun (engram)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Complete Dual-Agent System" -ForegroundColor Cyan
Write-Host "  GLM (main) + StepFun (engram)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set API Keys
$env:STEPFUN_API_KEY = "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"
$env:GLM_API_KEY = "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"
$env:OPENROUTER_API_KEY = $env:STEPFUN_API_KEY
$env:OPENCLAW_GATEWAY_TOKEN = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"

Write-Host "[*] API Keys configured" -ForegroundColor Green

# Stop existing processes
Write-Host "[*] Stopping existing processes..." -ForegroundColor Yellow
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process pythonw -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start OpenClaw Gateway
Write-Host "[*] Starting OpenClaw Gateway on port 17500..." -ForegroundColor Yellow
$gatewayPath = "C:\Users\OFFRSTAR0\Engram\clawdbot_repo"
$gatewayArgs = @{
    FilePath = "cmd.exe"
    ArgumentList = "/k cd /d `"$gatewayPath`" && echo ======================================== && echo   OpenClaw Gateway && echo   Model: GLM 4.7 Flash && echo   Port: 17500 && echo   Timeout: DISABLED && echo ======================================== && set OPENCLAW_GATEWAY_TOKEN=$env:OPENCLAW_GATEWAY_TOKEN && set GLM_API_KEY=$env:GLM_API_KEY && set OPENROUTER_API_KEY=$env:OPENROUTER_API_KEY && node dist/entry.js gateway --port 17500 --token $env:OPENCLAW_GATEWAY_TOKEN"
    WindowStyle = "Normal"
    WorkingDirectory = $gatewayPath
}
Start-Process @gatewayArgs

Write-Host "[*] Gateway starting... waiting 5 seconds" -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Engram Agent
Write-Host "[*] Starting Engram Agent (StepFun)..." -ForegroundColor Yellow
$engramPath = "C:\Users\OFFRSTAR0\Engram"
$engramArgs = @{
    FilePath = "cmd.exe"
    ArgumentList = "/k cd /d `"$engramPath`" && echo ======================================== && echo   Engram Agent && echo   Model: StepFun 3.5 Flash && echo   Gateway: ws://localhost:17500 && echo ======================================== && .venv\Scripts\python.exe run_engram_agent.py"
    WindowStyle = "Normal"
    WorkingDirectory = $engramPath
}
Start-Process @engramArgs

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  BOTH AGENTS STARTED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Gateway:    ws://localhost:17500" -ForegroundColor Cyan
Write-Host "Model:      GLM 4.7 Flash (main)" -ForegroundColor Cyan
Write-Host "Engram:     StepFun 3.5 Flash" -ForegroundColor Cyan
Write-Host "Timeout:    DISABLED (0 seconds)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Telegram:   @Freqtrad3_bot" -ForegroundColor Yellow
Write-Host "Allowlist:  1007321485" -ForegroundColor Yellow
Write-Host ""
Write-Host "Commands:" -ForegroundColor White
Write-Host "  /engram analyze BTC/USD" -ForegroundColor Gray
Write-Host "  /engram signal ETH/USD" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
