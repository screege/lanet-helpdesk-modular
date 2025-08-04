# Final fix for LANET Agent - Run as Administrator
Write-Host "========================================" -ForegroundColor Green
Write-Host "LANET Agent Final Fix - Service Startup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Stop service
Write-Host "1. Stopping LANETAgent service..." -ForegroundColor Yellow
sc.exe stop LANETAgent | Out-Null
Start-Sleep -Seconds 3

# Take ownership and copy corrected agent file
Write-Host "2. Updating lanet_agent.py with error handling..." -ForegroundColor Yellow
takeown /f "C:\Program Files\LANET Agent\lanet_agent.py" /a | Out-Null
icacls "C:\Program Files\LANET Agent\lanet_agent.py" /grant Administrators:F | Out-Null
Copy-Item "C:\lanet-helpdesk-v3\deployment\packages\lanet-agent-windows-v2.py" "C:\Program Files\LANET Agent\lanet_agent.py" -Force

# Create logs directory with proper permissions
Write-Host "3. Creating logs directory with proper permissions..." -ForegroundColor Yellow
New-Item -Path "C:\ProgramData\LANET Agent\Logs" -ItemType Directory -Force | Out-Null
icacls "C:\ProgramData\LANET Agent\Logs" /grant "SYSTEM:F" /grant "Administradores:F" /grant "Usuarios:M" | Out-Null

# Create log files with proper permissions
Write-Host "4. Creating log files..." -ForegroundColor Yellow
New-Item -Path "C:\ProgramData\LANET Agent\Logs\service.log" -ItemType File -Force | Out-Null
New-Item -Path "C:\ProgramData\LANET Agent\Logs\agent.log" -ItemType File -Force | Out-Null
icacls "C:\ProgramData\LANET Agent\Logs\*.log" /grant "SYSTEM:F" /grant "Administradores:F" /grant "Usuarios:M" | Out-Null

# Verify files are updated
Write-Host "5. Verifying file updates..." -ForegroundColor Yellow
$serviceWrapper = Get-Content "C:\Program Files\LANET Agent\service_wrapper.py" | Select-String "ProgramData"
$agentFile = Get-Content "C:\Program Files\LANET Agent\lanet_agent.py" | Select-String "ProgramData"

if ($serviceWrapper -and $agentFile) {
    Write-Host "✅ Both files updated successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ File update failed!" -ForegroundColor Red
    exit 1
}

# Test service wrapper manually
Write-Host "6. Testing service wrapper..." -ForegroundColor Yellow
$testOutput = & "C:\Python310\python.exe" "C:\Program Files\LANET Agent\service_wrapper.py" 2>&1
Write-Host "Test result: $($testOutput -join ' ')" -ForegroundColor Gray

# Start the service
Write-Host "7. Starting LANETAgent service..." -ForegroundColor Yellow
$startResult = sc.exe start LANETAgent
Write-Host "Start command result: $startResult" -ForegroundColor Gray

# Wait for service to start
Start-Sleep -Seconds 10

# Check final status
Write-Host "8. Checking final service status..." -ForegroundColor Cyan
sc.exe query LANETAgent

# Check logs
Write-Host ""
Write-Host "9. Checking logs..." -ForegroundColor Cyan
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    Write-Host "✅ Service log found!" -ForegroundColor Green
    $serviceLogContent = Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -ErrorAction SilentlyContinue
    if ($serviceLogContent) {
        Write-Host "Service log content:" -ForegroundColor Yellow
        $serviceLogContent | Select-Object -Last 10 | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
    }
} else {
    Write-Host "❌ Service log not found" -ForegroundColor Red
}

if (Test-Path "C:\ProgramData\LANET Agent\Logs\agent.log") {
    Write-Host ""
    Write-Host "✅ Agent log found!" -ForegroundColor Green
    $agentLogContent = Get-Content "C:\ProgramData\LANET Agent\Logs\agent.log" -ErrorAction SilentlyContinue
    if ($agentLogContent) {
        Write-Host "Agent log content:" -ForegroundColor Yellow
        $agentLogContent | Select-Object -Last 10 | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
    }
} else {
    Write-Host "❌ Agent log not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Fix completed! Check service status above." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
