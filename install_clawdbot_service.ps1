#!/usr/bin/env pwsh
# Install ClawdBot Gateway as Windows Service
# Requires Administrator privileges

param(
    [switch]$Uninstall,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Restart,
    [switch]$Status
)

$ServiceName = "ClawdBotGateway"
$ServiceDisplayName = "ClawdBot AI Gateway"
$ServiceDescription = "ClawdBot WebSocket Gateway for AI agent communication"
$ClawdBotCmd = "C:\Users\OFFRSTAR0\.clawdbot\gateway.cmd"
$LogDir = "C:\Users\OFFRSTAR0\Engram\logs"
$ServiceLog = "$LogDir\clawdbot_service.log"

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host "[INFO] Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    exit 1
}

function Get-ServiceStatus {
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        return $service.Status
    }
    return "NotInstalled"
}

function Install-ClawdBotService {
    Write-Host "[INFO] Installing ClawdBot Gateway as Windows Service..." -ForegroundColor Cyan
    
    # Check if service already exists
    if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
        Write-Host "[WARN] Service already exists. Use -Restart to restart it." -ForegroundColor Yellow
        return
    }
    
    # Create the service using nssm (Non-Sucking Service Manager) or sc
    # First, try to use sc.exe (built-in Windows tool)
    
    # Create wrapper script for the service
    $wrapperScript = @"
@echo off
set CLAWDBOT_GATEWAY_PORT=18789
set CLAWDBOT_GATEWAY_TOKEN=2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc
set CLAWDBOT_SERVICE_MARKER=clawdbot
set CLAWDBOT_SERVICE_KIND=gateway
"C:\Program Files\nodejs\node.exe" C:\Users\OFFRSTAR0\AppData\Roaming\npm\node_modules\clawdbot\dist\entry.js gateway --port 18789 >> "$ServiceLog" 2>&1
"@
    
    $wrapperPath = "C:\Users\OFFRSTAR0\.clawdbot\service_wrapper.bat"
    $wrapperScript | Out-File -FilePath $wrapperPath -Encoding ASCII
    
    # Install service using sc.exe
    $binPath = "cmd.exe /c `"$wrapperPath`""
    sc.exe create $ServiceName binPath= $binPath start= auto DisplayName= "$ServiceDisplayName" | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        # Set description
        sc.exe description $ServiceName "$ServiceDescription" | Out-Null
        
        Write-Host "[OK] Service installed successfully!" -ForegroundColor Green
        Write-Host "[INFO] Service Name: $ServiceName" -ForegroundColor Gray
        Write-Host "[INFO] To start: sc start $ServiceName" -ForegroundColor Gray
        Write-Host "[INFO] To stop: sc stop $ServiceName" -ForegroundColor Gray
        
        # Try to start the service
        Start-ClawdBotService
    } else {
        Write-Host "[ERROR] Failed to install service. Exit code: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "[INFO] You may need to use NSSM (Non-Sucking Service Manager) for Node.js apps" -ForegroundColor Yellow
        
        # Alternative: Create scheduled task instead
        Install-ScheduledTaskAlternative
    }
}

function Install-ScheduledTaskAlternative {
    Write-Host "`n[INFO] Installing as Scheduled Task instead (runs at startup)..." -ForegroundColor Cyan
    
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"C:\Users\OFFRSTAR0\.clawdbot\gateway.cmd`"" -WorkingDirectory "C:\Users\OFFRSTAR0\.clawdbot"
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
    $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType ServiceAccount -RunLevel Highest
    
    try {
        Register-ScheduledTask -TaskName $ServiceName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
        Write-Host "[OK] Scheduled task created successfully!" -ForegroundColor Green
        Write-Host "[INFO] Task will run at startup. To start now: Start-ScheduledTask -TaskName '$ServiceName'" -ForegroundColor Gray
    } catch {
        Write-Host "[ERROR] Failed to create scheduled task: $_" -ForegroundColor Red
    }
}

function Uninstall-ClawdBotService {
    Write-Host "[INFO] Uninstalling ClawdBot Gateway service..." -ForegroundColor Cyan
    
    # Stop if running
    Stop-ClawdBotService
    
    # Remove service
    sc.exe delete $ServiceName | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Service uninstalled successfully!" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Service may not exist or already removed" -ForegroundColor Yellow
    }
    
    # Also remove scheduled task if exists
    Unregister-ScheduledTask -TaskName $ServiceName -Confirm:$false -ErrorAction SilentlyContinue
}

function Start-ClawdBotService {
    Write-Host "[INFO] Starting ClawdBot Gateway service..." -ForegroundColor Cyan
    
    $status = Get-ServiceStatus
    if ($status -eq "NotInstalled") {
        Write-Host "[ERROR] Service not installed. Run without -Start first." -ForegroundColor Red
        return
    }
    
    try {
        Start-Service -Name $ServiceName -ErrorAction Stop
        Start-Sleep -Seconds 2
        $newStatus = Get-ServiceStatus
        if ($newStatus -eq "Running") {
            Write-Host "[OK] Service started successfully!" -ForegroundColor Green
            Write-Host "[INFO] Gateway available at: ws://127.0.0.1:18789" -ForegroundColor Gray
        } else {
            Write-Host "[WARN] Service status: $newStatus" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[ERROR] Failed to start service: $_" -ForegroundColor Red
        Write-Host "[INFO] Check Event Viewer for details" -ForegroundColor Yellow
    }
}

function Stop-ClawdBotService {
    Write-Host "[INFO] Stopping ClawdBot Gateway service..." -ForegroundColor Cyan
    
    $status = Get-ServiceStatus
    if ($status -eq "NotInstalled") {
        Write-Host "[WARN] Service not installed" -ForegroundColor Yellow
        return
    }
    
    if ($status -eq "Stopped") {
        Write-Host "[OK] Service already stopped" -ForegroundColor Green
        return
    }
    
    try {
        Stop-Service -Name $ServiceName -ErrorAction Stop -Force
        Write-Host "[OK] Service stopped successfully!" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to stop service: $_" -ForegroundColor Red
    }
}

function Show-Status {
    $status = Get-ServiceStatus
    Write-Host "`nClawdBot Gateway Service Status" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "Service Name: $ServiceName" -ForegroundColor Gray
    Write-Host "Status: $status" -ForegroundColor $(if ($status -eq "Running") { "Green" } elseif ($status -eq "Stopped") { "Yellow" } else { "Red" })
    
    if ($status -eq "Running") {
        $service = Get-Service -Name $ServiceName
        Write-Host "Process ID: $($service.ServiceHandle)" -ForegroundColor Gray
    }
    
    # Check if port is listening
    $portCheck = Get-NetTCPConnection -LocalPort 18789 -ErrorAction SilentlyContinue
    if ($portCheck) {
        Write-Host "Port 18789: LISTENING" -ForegroundColor Green
    } else {
        Write-Host "Port 18789: NOT LISTENING" -ForegroundColor Red
    }
    
    # Check health endpoint
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:18789/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "Health Check: OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "Health Check: UNAVAILABLE" -ForegroundColor Yellow
    }
}

# Main script logic
Write-Host @"
================================================================================
  CLAWDBOT GATEWAY SERVICE MANAGER
================================================================================
"@ -ForegroundColor Cyan

if ($Status) {
    Show-Status
} elseif ($Uninstall) {
    Uninstall-ClawdBotService
} elseif ($Start) {
    Start-ClawdBotService
} elseif ($Stop) {
    Stop-ClawdBotService
} elseif ($Restart) {
    Stop-ClawdBotService
    Start-Sleep -Seconds 2
    Start-ClawdBotService
} else {
    # Default: Install
    Install-ClawdBotService
}

Write-Host "`nDone!" -ForegroundColor Green
