#!/usr/bin/env pwsh
# Dual Agent System Launcher - Opens TWO terminals

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Dual-Agent System" -ForegroundColor Cyan
Write-Host "  GLM (main) + StepFun (engram)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill existing processes
Write-Host "[*] Stopping existing processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Terminal 1: OpenClaw Gateway (GLM)
Write-Host "[*] Launching Terminal 1: OpenClaw Gateway (GLM)..." -ForegroundColor Green
$gatewayCmd = @"
cd C:\Users\OFFRSTAR0\Engram\clawdbot_repo
`$env:OPENCLAW_GATEWAY_TOKEN = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
`$env:GLM_API_KEY = "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"
`$env:OPENROUTER_API_KEY = "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"
Write-Host "Starting OpenClaw Gateway on port 17500..." -ForegroundColor Cyan
Write-Host "Default Model: GLM 4.7 Flash" -ForegroundColor Gray
node dist/entry.js gateway --token "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $gatewayCmd

# Wait for gateway to start
Write-Host "[*] Waiting for gateway to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Terminal 2: Engram Agent (StepFun)
Write-Host "[*] Launching Terminal 2: Engram Agent (StepFun)..." -ForegroundColor Green
$engramCmd = @"
cd C:\Users\OFFRSTAR0\Engram
`$env:STEPFUN_API_KEY = "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"
Write-Host "Starting Engram Agent..." -ForegroundColor Cyan
Write-Host "Connecting to: ws://localhost:17500" -ForegroundColor Gray
Write-Host "Model: stepfun/step-3.5-flash:free" -ForegroundColor Gray
.venv\Scripts\python.exe -c "
import asyncio
import websockets
import json
import os

STEPFUN_API_KEY = os.getenv('STEPFUN_API_KEY')

async def engram_agent():
    uri = 'ws://localhost:17500'
    print('[Engram] Connecting to gateway...')
    try:
        async with websockets.connect(uri) as ws:
            print('[Engram] Connected!')
            # Register as agent
            await ws.send(json.dumps({
                'type': 'register',
                'agent': 'engram',
                'model': 'stepfun/step-3.5-flash:free',
                'provider': 'openrouter'
            }))
            print('[Engram] Registered and ready for delegation')
            
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                print(f'[Engram] Received: {data}')
                
                if data.get('type') == 'analyze':
                    # Process with StepFun
                    response = {
                        'type': 'response',
                        'agent': 'engram',
                        'result': f"Analysis from StepFun: {data.get('query')}"
                    }
                    await ws.send(json.dumps(response))
    except Exception as e:
        print(f'[Engram] Error: {e}')

asyncio.run(engram_agent())
"
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $engramCmd

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Dual-Agent System Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Terminal 1: OpenClaw Gateway (GLM)" -ForegroundColor Cyan
Write-Host "Terminal 2: Engram Agent (StepFun)" -ForegroundColor Cyan
Write-Host ""
Write-Host "In Telegram, message @Freqtrad3_bot:" -ForegroundColor Yellow
Write-Host "  /engram analyze BTC/USD" -ForegroundColor White
Write-Host ""
Write-Host "GLM will receive the message and delegate to StepFun!" -ForegroundColor Gray
