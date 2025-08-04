# Force copy corrected agent file - Run as Administrator
Write-Host "Force copying corrected lanet_agent.py..." -ForegroundColor Green

# Stop service first
Write-Host "Stopping LANETAgent service..." -ForegroundColor Yellow
sc.exe stop LANETAgent | Out-Null

# Wait a moment
Start-Sleep -Seconds 3

# Take ownership and set permissions
Write-Host "Taking ownership of target file..." -ForegroundColor Yellow
takeown /f "C:\Program Files\LANET Agent\lanet_agent.py" /a
icacls "C:\Program Files\LANET Agent\lanet_agent.py" /grant Administrators:F

# Copy the corrected file
Write-Host "Copying corrected file..." -ForegroundColor Yellow
Copy-Item "C:\lanet-helpdesk-v3\deployment\packages\lanet-agent-windows-v2.py" "C:\Program Files\LANET Agent\lanet_agent.py" -Force

# Verify the copy
Write-Host "Verifying copy..." -ForegroundColor Yellow
$content = Get-Content "C:\Program Files\LANET Agent\lanet_agent.py" | Select-String "ProgramData"
if ($content) {
    Write-Host "✅ File copied successfully!" -ForegroundColor Green
    Write-Host "Found: $content" -ForegroundColor Cyan
} else {
    Write-Host "❌ Copy failed - ProgramData path not found" -ForegroundColor Red
    exit 1
}

# Test the service wrapper
Write-Host ""
Write-Host "Testing service wrapper..." -ForegroundColor Yellow
$testResult = & "C:\Python310\python.exe" "C:\Program Files\LANET Agent\service_wrapper.py" 2>&1
Write-Host "Test output: $testResult" -ForegroundColor Gray

# Start the service
Write-Host ""
Write-Host "Starting LANETAgent service..." -ForegroundColor Yellow
sc.exe start LANETAgent

# Wait for service to start
Start-Sleep -Seconds 5

# Check final status
Write-Host ""
Write-Host "Final service status:" -ForegroundColor Cyan
sc.exe query LANETAgent

# Check logs
Write-Host ""
Write-Host "Checking logs..." -ForegroundColor Cyan
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    Write-Host "✅ Service log found!" -ForegroundColor Green
    Write-Host "Recent entries:" -ForegroundColor Yellow
    Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 5
}

if (Test-Path "C:\ProgramData\LANET Agent\Logs\agent.log") {
    Write-Host ""
    Write-Host "✅ Agent log found!" -ForegroundColor Green
    Write-Host "Recent entries:" -ForegroundColor Yellow
    Get-Content "C:\ProgramData\LANET Agent\Logs\agent.log" -Tail 5
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
