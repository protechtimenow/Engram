@echo off
echo ========================================
echo Starting ClawdBOT + Engram System
echo ========================================
echo AI Provider: OpenRouter (direct)
echo.

REM Start ClawdBOT Gateway (Port 18789)
echo [*] Starting ClawdBOT Gateway...
cd /d C:\Users\OFFRSTAR0\Engram\clawdbot_repo
start "ClawdBOT Gateway" cmd /k "pnpm gateway:dev"

REM Wait for gateway to initialize
timeout /t 5 /nobreak >nul

REM Start Engram Agent (uses OpenRouter directly)
echo [*] Starting Engram Agent...
cd /d C:\Users\OFFRSTAR0\Engram
start "Engram Agent" cmd /k "python engram_clawdbot_integration.py"

echo.
echo ========================================
echo All services starting in separate windows
echo ========================================
timeout /t 2
