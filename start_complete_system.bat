@echo off
echo ========================================
echo   Complete Dual-Agent System
echo   GLM (main) + StepFun (engram)
echo ========================================
echo.

REM Kill existing processes
echo [*] Stopping existing processes...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Set environment variables
set OPENROUTER_API_KEY=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
set GLM_API_KEY=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
set STEPFUN_API_KEY=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
set OPENCLAW_GATEWAY_TOKEN=2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc

echo [*] Starting OpenClaw Gateway (Terminal 1)...
start "OpenClaw Gateway - GLM" cmd /k "cd C:\Users\OFFRSTAR0\Engram\clawdbot_repo && echo ======================================== && echo   OpenClaw Gateway && echo   Model: GLM 4.7 Flash && echo   Port: 17500 && echo ======================================== && set OPENCLAW_GATEWAY_TOKEN=2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc && set GLM_API_KEY=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 && set OPENROUTER_API_KEY=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 && node dist/entry.js gateway --token 2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"

timeout /t 5 /nobreak >nul

echo [*] Starting Engram Agent (Terminal 2)...
start "Engram Agent - StepFun" cmd /k "cd C:\Users\OFFRSTAR0\Engram && echo ======================================== && echo   Engram Agent && echo   Model: StepFun 3.5 Flash && echo   Gateway: ws://localhost:17500 && echo ======================================== && .venv\Scripts\python.exe run_engram_agent.py"

echo.
echo ========================================
echo   Both agents launching!
echo ========================================
echo.
echo Terminal 1: OpenClaw Gateway (GLM)   
echo Terminal 2: Engram Agent (StepFun)
echo.
echo Wait 10 seconds for both to connect...
echo.
echo Then in Telegram, message @Freqtrad3_bot:
echo   /engram analyze BTC/USD
echo   /engram signal ETH/USD
echo.
echo GLM receives message, delegates to StepFun!
echo.
pause
