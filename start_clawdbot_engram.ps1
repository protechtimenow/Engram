#!/usr/bin/env pwsh
# ClawdBot + Engram Bot Auto-Start Script
# Starts both services and monitors their health

param(
    [switch]$DebugMode,
    [switch]$NoClawdBot,
    [int]$ClawdBotPort = 18789,
    [string]$LMStudioUrl = "http://100.118.172.23:1234"
)

# Configuration
$ClawdBotCmd = "C:\Users\OFFRSTAR0\.clawdbot\gateway.cmd"
$EngramDir = "C:\Users\OFFRSTAR0\Engram"
$LogDir = "$EngramDir\logs"
$ClawdBotLog = "$LogDir\clawdbot_gateway.log"
$EngramLog = "$LogDir\engram_bot.log"

# Environment Variables
$env:TELEGRAM_BOT_TOKEN = "8517504737:AAELKyE2jC48Ql1d1opfEy8ZMfU5UifB6kA"
$env:TELEGRAM_CHAT_ID = "1007321485"
$env:LMSTUDIO_URL = $LMStudioUrl
$env:CLAWDBOT_WS_URL = "ws://127.0.0.1:$ClawdBotPort"
$env:CLAWDBOT_AUTH_TOKEN = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"

if ($DebugMode) {
    $env:DEBUG_MODE = "true"
    Write-Host "[INFO] Debug mode enabled" -ForegroundColor Yellow
}

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

Write-Host @"
================================================================================
  CLAWDBOT + ENGRAM BOT LAUNCHER
================================================================================
"@ -ForegroundColor Cyan

# Function to check if port is in use
function Test-PortInUse {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $connection -ne $null
}

# Function to check if ClawdBot is running
function Test-ClawdBotHealth {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$ClawdBotPort/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Function to wait for ClawdBot to be ready
function Wait-ClawdBotReady {
    param([int]$TimeoutSeconds = 30)
    $elapsed = 0
    Write-Host "[INFO] Waiting for ClawdBot Gateway to be ready..." -ForegroundColor Yellow -NoNewline
    while ($elapsed -lt $TimeoutSeconds) {
        if (Test-ClawdBotHealth) {
            Write-Host " [OK]" -ForegroundColor Green
            return $true
        }
        Start-Sleep -Milliseconds 500
        $elapsed += 0.5
        Write-Host "." -ForegroundColor Yellow -NoNewline
    }
    Write-Host " [TIMEOUT]" -ForegroundColor Red
    return $false
}

# Check if ClawdBot is already running
if (Test-PortInUse -Port $ClawdBotPort) {
    Write-Host "[OK] ClawdBot Gateway already running on port $ClawdBotPort" -ForegroundColor Green
} elseif (-not $NoClawdBot) {
    # Start ClawdBot Gateway
    Write-Host "[INFO] Starting ClawdBot Gateway..." -ForegroundColor Cyan
    Write-Host "[INFO] Log file: $ClawdBotLog" -ForegroundColor Gray
    
    # Start ClawdBot in background job
    $clawdbotJob = Start-Job -ScriptBlock {
        param($CmdPath, $LogPath)
        $env:CLAWDBOT_GATEWAY_PORT = "18789"
        $env:CLAWDBOT_GATEWAY_TOKEN = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
        & $CmdPath 2>&1 | Tee-Object -FilePath $LogPath -Append
    } -ArgumentList $ClawdBotCmd, $ClawdBotLog
    
    # Wait for ClawdBot to be ready
    if (-not (Wait-ClawdBotReady -TimeoutSeconds 30)) {
        Write-Host "[WARN] ClawdBot Gateway failed to start, continuing with LMStudio fallback..." -ForegroundColor Yellow
    } else {
        Write-Host "[OK] ClawdBot Gateway is ready!" -ForegroundColor Green
    }
} else {
    Write-Host "[INFO] Skipping ClawdBot (NoClawdBot flag set)" -ForegroundColor Yellow
}

# Wait a moment for ClawdBot to fully initialize
Start-Sleep -Seconds 2

# Start Engram Bot
Write-Host "`n[INFO] Starting Engram Bot..." -ForegroundColor Cyan
Write-Host "[INFO] Log file: $EngramLog" -ForegroundColor Gray

# Change to Engram directory
Set-Location $EngramDir

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found! Run: python -m venv .venv" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
. .venv\Scripts\Activate.ps1

# Display startup info
Write-Host @"
--------------------------------------------------------------------------------
  Configuration:
  - Telegram Bot: Enabled
  - LMStudio: $LMStudioUrl
  - ClawdBot: ws://127.0.0.1:$ClawdBotPort
  - Debug Mode: $(if ($DebugMode) { "ON" } else { "OFF" })
--------------------------------------------------------------------------------
"@ -ForegroundColor Gray

# Start Engram Bot in foreground (so user can see output and Ctrl+C to stop)
Write-Host "[OK] Starting Engram Bot... Press Ctrl+C to stop.`n" -ForegroundColor Green

# Create a trap to handle Ctrl+C gracefully
trap {
    Write-Host "`n[INFO] Shutting down..." -ForegroundColor Yellow
    if ($clawdbotJob) {
        Stop-Job $clawdbotJob -ErrorAction SilentlyContinue
        Remove-Job $clawdbotJob -ErrorAction SilentlyContinue
    }
    exit 0
}

try {
    # Run Engram Bot with logging
    python enhanced_engram_launcher.py 2>&1 | Tee-Object -FilePath $EngramLog -Append
} catch {
    Write-Host "[ERROR] Engram Bot crashed: $_" -ForegroundColor Red
} finally {
    # Cleanup
    if ($clawdbotJob) {
        Write-Host "[INFO] Stopping ClawdBot Gateway..." -ForegroundColor Yellow
        Stop-Job $clawdbotJob -ErrorAction SilentlyContinue
        Remove-Job $clawdbotJob -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] Shutdown complete" -ForegroundColor Green
}
