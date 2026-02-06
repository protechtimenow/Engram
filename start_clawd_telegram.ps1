#!/usr/bin/env pwsh
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting ClawdBOT with Telegram" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[*] Stopping any existing ClawdBOT processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*openclaw*" } | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host "[*] Starting ClawdBOT Gateway with Telegram..." -ForegroundColor Yellow
Write-Host "    Port: 17500" -ForegroundColor Gray
Write-Host "    Telegram: Enabled" -ForegroundColor Gray
Write-Host ""

cd C:\Users\OFFRSTAR0\Engram\clawdbot_repo

# Start ClawdBOT WITHOUT skipping channels
$env:OPENCLAW_GATEWAY_TOKEN = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
node dist/entry.js gateway --token "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
