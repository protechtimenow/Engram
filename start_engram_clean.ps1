#!/usr/bin/env pwsh
# CLEAN Engram + OpenClaw Gateway Launcher
# Uses token from ClawdBot config - NO MORE AUTH FAILURES

$ErrorActionPreference = "Stop"

# Get the REAL token from ClawdBot config
$clawdbotConfig = Get-Content "$env:USERPROFILE\.clawdbot\clawdbot.json" | ConvertFrom-Json
$GATEWAY_TOKEN = $clawdbotConfig.gateway.auth.token
$GATEWAY_PORT = 17500

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CLEAN Engram + OpenClaw Launch" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Token: $($GATEWAY_TOKEN.Substring(0,10))...$($GATEWAY_TOKEN.Substring($GATEWAY_TOKEN.Length-10))" -ForegroundColor Gray
Write-Host "Port: $GATEWAY_PORT" -ForegroundColor Gray
Write-Host ""

# Kill any existing processes
Write-Host "[*] Stopping existing processes..." -ForegroundColor Yellow
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Set environment variables
$env:OPENCLAW_GATEWAY_TOKEN = $GATEWAY_TOKEN
$env:OPENROUTER_API_KEY = "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"
$env:ENGRAM_CONFIG = "config/engram_fast.json"

# Update the config file with the correct token
$configPath = "config/engram_fast.json"
$config = Get-Content $configPath | ConvertFrom-Json
$config.clawdbot.token = $GATEWAY_TOKEN
$config.clawdbot.port = $GATEWAY_PORT
$config | ConvertTo-Json -Depth 10 | Set-Content $configPath
Write-Host "[*] Updated config/engram_fast.json with correct token" -ForegroundColor Green

# Start OpenClaw Gateway
Write-Host "[*] Starting OpenClaw Gateway on port $GATEWAY_PORT..." -ForegroundColor Yellow
$gatewayPath = "$PWD\clawdbot_repo"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d `"$gatewayPath`" && set OPENCLAW_GATEWAY_TOKEN=$GATEWAY_TOKEN && node dist/entry.js gateway --port $GATEWAY_PORT --token $GATEWAY_TOKEN" -WindowStyle Normal

Write-Host "[*] Waiting 4 seconds for gateway..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

# Start Engram Agent
Write-Host "[*] Starting Engram Agent..." -ForegroundColor Yellow
# Create a temporary batch file to set environment variables and run Python
$batchContent = @"
set OPENCLAW_GATEWAY_TOKEN=$GATEWAY_TOKEN
set OPENROUTER_API_KEY=$env:OPENROUTER_API_KEY
set ENGRAM_CONFIG=config/engram_fast.json
cd /d "$PWD"
.venv\Scripts\python.exe run_engram_fast.py
"@
$batchPath = "$env:TEMP\start_engram_agent.bat"
$batchContent | Set-Content -Path $batchPath -Encoding ASCII
Start-Process -FilePath "cmd.exe" -ArgumentList "/k `"$batchPath`"" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SYSTEM STARTED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Gateway: ws://localhost:$GATEWAY_PORT" -ForegroundColor Cyan
Write-Host "Token:   (loaded from ClawdBot config)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Both windows should show successful connection." -ForegroundColor White
Write-Host "If you see 'Authentication failed', check the gateway window for errors." -ForegroundColor Gray
