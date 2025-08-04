# Fix LANET Agent Configuration - Run as Administrator
Write-Host "Fixing LANET Agent Configuration..." -ForegroundColor Green

# Stop service
Write-Host "Stopping service..." -ForegroundColor Yellow
sc.exe stop LANETAgent | Out-Null

# Take ownership and copy correct config
Write-Host "Updating config.ini with installation token..." -ForegroundColor Yellow
takeown /f "C:\Program Files\LANET Agent\config.ini" /a | Out-Null
icacls "C:\Program Files\LANET Agent\config.ini" /grant Administrators:F | Out-Null
Copy-Item "C:\Program Files\LANET Agent\config\agent.ini" "C:\Program Files\LANET Agent\config.ini" -Force

# Verify config
Write-Host "Verifying configuration..." -ForegroundColor Yellow
$tokenLine = Get-Content "C:\Program Files\LANET Agent\config.ini" | Select-String "installation_token = LANET-75F6-EC23-85DC9D"
if ($tokenLine) {
    Write-Host "✅ Configuration updated successfully!" -ForegroundColor Green
    Write-Host "Token found: $tokenLine" -ForegroundColor Cyan
} else {
    Write-Host "❌ Configuration update failed!" -ForegroundColor Red
    exit 1
}

# Start service
Write-Host "Starting LANETAgent service..." -ForegroundColor Yellow
sc.exe start LANETAgent

# Wait for service to start
Start-Sleep -Seconds 10

# Check service status
Write-Host "Service status:" -ForegroundColor Cyan
sc.exe query LANETAgent

# Check logs
Write-Host ""
Write-Host "Recent service logs:" -ForegroundColor Cyan
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 10
} else {
    Write-Host "Service log not found" -ForegroundColor Red
}

if (Test-Path "C:\ProgramData\LANET Agent\Logs\agent.log") {
    Write-Host ""
    Write-Host "Recent agent logs:" -ForegroundColor Cyan
    Get-Content "C:\ProgramData\LANET Agent\Logs\agent.log" -Tail 10
}

Write-Host ""
Write-Host "Configuration fix completed!" -ForegroundColor Green
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
