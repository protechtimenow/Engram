@echo off
echo ========================================
echo   Engram Complete System Launcher
echo ========================================
echo.

REM Kill any existing processes
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

timeout /t 2 /nobreak >nul

echo [*] Starting Engram Python Agent...
start "Engram Agent" pythonw C:\Users\OFFRSTAR0\Engram\engram.py

timeout /t 3 /nobreak >nul

echo [*] Starting OpenClaw Gateway...
cd C:\Users\OFFRSTAR0\Engram\clawdbot_repo
set OPENCLAW_GATEWAY_TOKEN=2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc
set OPENROUTER_API_KEY=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
set GLM_API_KEY=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
set STEPFUN_API_KEY=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
node dist/entry.js gateway --token 2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc
