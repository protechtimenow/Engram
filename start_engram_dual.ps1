#!/usr/bin/env pwsh
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Engram Dual-Agent Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# API Keys
$env:OPENROUTER_API_KEY = "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"
$env:GLM_API_KEY = "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"
$env:STEPFUN_API_KEY = "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"

Write-Host "[*] Stopping any existing processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "[*] Starting OpenClaw Gateway with Dual Agents..." -ForegroundColor Green
Write-Host "    Port: 17500" -ForegroundColor Gray
Write-Host "    Agents: main (GLM) + engram (StepFun)" -ForegroundColor Gray
Write-Host "    Telegram: @Freqtrad3_bot" -ForegroundColor Gray
Write-Host ""

cd C:\Users\OFFRSTAR0\Engram\clawdbot_repo

$env:OPENCLAW_GATEWAY_TOKEN = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
node dist/entry.js gateway --token "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
