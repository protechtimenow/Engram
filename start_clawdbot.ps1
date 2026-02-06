#!/usr/bin/env pwsh
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting ClawdBOT + Engram System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Start ClawdBOT Gateway (Port 18789)
Write-Host "[*] Starting ClawdBOT Gateway..." -ForegroundColor Yellow
$gatewayPath = "C:\Users\OFFRSTAR0\Engram\clawdbot_repo"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$gatewayPath'; pnpm gateway:dev" -WindowStyle Normal

# Wait for gateway to initialize
Start-Sleep -Seconds 5

# Start Engram Agent (uses OpenRouter directly)
Write-Host "[*] Starting Engram Agent..." -ForegroundColor Yellow
$engramPath = "C:\Users\OFFRSTAR0\Engram"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$engramPath'; python engram_clawdbot_integration.py" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "All services starting in separate windows" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "AI Provider: OpenRouter (direct)" -ForegroundColor Cyan
Start-Sleep -Seconds 2
