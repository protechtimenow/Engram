# OpenClaw + Engram Fixed Startup Script
# Configured with separate API keys for StepFun and GLM

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OpenClaw + Engram Fixed Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set API Keys
$env:STEPFUN_API_KEY = "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"
$env:GLM_API_KEY = "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"
$env:OPENROUTER_API_KEY = $env:STEPFUN_API_KEY  # For Engram compatibility

Write-Host "API Keys Configured:" -ForegroundColor Yellow
Write-Host "  - STEPFUN_API_KEY:  $($env:STEPFUN_API_KEY.Substring(0, 20))..." -ForegroundColor Gray
Write-Host "  - GLM_API_KEY:      $($env:GLM_API_KEY.Substring(0, 20))..." -ForegroundColor Gray
Write-Host "  - OPENROUTER_API_KEY: (same as STEPFUN_API_KEY for Engram)" -ForegroundColor Gray
Write-Host ""

# Kill any existing processes
Write-Host "Stopping any existing processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -match "node|python|openclaw"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start OpenClaw Gateway
Write-Host ""
Write-Host "Starting OpenClaw Gateway on port 17500..." -ForegroundColor Green
Write-Host "  Model: openrouter/z-ai/glm-4.7-flash" -ForegroundColor Gray
Write-Host "  API Key: GLM_API_KEY" -ForegroundColor Gray
Write-Host ""

$gatewayJob = Start-Job -ScriptBlock {
    $env:STEPFUN_API_KEY = "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"
    $env:GLM_API_KEY = "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"
    $env:OPENROUTER_API_KEY = $env:STEPFUN_API_KEY
    clawdbot gateway
}

# Wait for gateway to start
Start-Sleep -Seconds 5

# Check gateway status
Write-Host "Checking Gateway Status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:17500/health" -Method GET -ErrorAction SilentlyContinue
    Write-Host "  Gateway is RUNNING" -ForegroundColor Green
} catch {
    Write-Host "  Gateway starting (may take a moment)..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  System Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ClawdBOT (Telegram):" -ForegroundColor Yellow
Write-Host "  - Port: 17500" -ForegroundColor Gray
Write-Host "  - Model: openrouter/z-ai/glm-4.7-flash" -ForegroundColor Gray
Write-Host "  - API Key: GLM_API_KEY" -ForegroundColor Gray
Write-Host ""
Write-Host "Engram Agent:" -ForegroundColor Yellow
Write-Host "  - WebSocket: ws://localhost:17500" -ForegroundColor Gray
Write-Host "  - Model: stepfun/step-3.5-flash:free" -ForegroundColor Gray
Write-Host "  - API Key: STEPFUN_API_KEY" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# Show gateway job output
Write-Host ""
Write-Host "Gateway Output:" -ForegroundColor Green
Receive-Job -Job $gatewayJob -Keep | Select-Object -Last 20

Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Red

# Keep script running
while ($true) {
    Receive-Job -Job $gatewayJob | Out-Null
    Start-Sleep -Seconds 1
}
