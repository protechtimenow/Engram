@echo off
REM Engram Agent Launcher - Windows
REM Passes OpenClaw environment variables to Python agent

echo ========================================
echo   Engram Agent - Starting...
echo ========================================
echo.

REM Check if OpenClaw is running (common issue: agent can't find env vars)
where openclaw >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] OpenClaw CLI not found in PATH
    echo [INFO] Run this from your OpenClaw terminal where env vars are loaded
    echo.
    echo Alternative: Set env vars directly:
    echo   set OPENROUTER_API_KEY=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
    echo   set STEPFUN_API_KEY=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
    echo   python run_engram_fast.py
    echo.
    pause
    exit /b 1
)

REM Pass OpenClaw environment variables to Python agent
set OPENROUTER_API_KEY=%GLM_API_KEY%
set STEPFUN_API_KEY=%STEPFUN_API_KEY%

echo [OK] OpenClaw found
echo [OK] OPENROUTER_API_KEY set (length: %len%)
echo [OK] STEPFUN_API_KEY set (length: %len%)
echo.
echo [START] Launching Engram agent...
echo ========================================
echo.

python run_engram_fast.py

echo.
echo ========================================
echo [DONE] Engram agent stopped
echo ========================================
pause
