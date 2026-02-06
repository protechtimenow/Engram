@echo off
echo ==========================================
echo LOG MONITOR - Clawdbot + Engram
echo ==========================================
echo.
echo Press Ctrl+C to stop
echo.

:loop
cls
echo [%date% %time%]
echo ==========================================
echo.

echo --- CLAWDBOT LAST 10 LINES ---
powershell -Command "Get-Content \tmp\clawdbot\clawdbot-*.log -Tail 10 -ErrorAction SilentlyContinue"

echo.
echo --- ENGRAM AGENT HEALTH ---
powershell -Command "try { $r = Invoke-RestMethod http://localhost:18789/health -TimeoutSec 2; Write-Host 'Gateway: OK' } catch { Write-Host 'Gateway: Check status' }"

timeout /t 3 /nobreak >nul
goto loop
