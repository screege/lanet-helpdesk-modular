# Install LANET Agent as Administrator
Write-Host "Installing LANET Agent with corrected logging permissions..." -ForegroundColor Green
Write-Host "Token: LANET-75F6-EC23-85DC9D" -ForegroundColor Yellow
Write-Host "Server: http://localhost:5001/api" -ForegroundColor Yellow
Write-Host ""

# Run installer
$process = Start-Process -FilePath ".\dist\LANET_Agent_Enterprise_Installer_v2.exe" -ArgumentList "--silent", "--token", "LANET-75F6-EC23-85DC9D", "--server", "http://localhost:5001/api" -Wait -PassThru

Write-Host ""
Write-Host "Installation completed with exit code: $($process.ExitCode)" -ForegroundColor $(if($process.ExitCode -eq 0) {"Green"} else {"Red"})

# Check service status
Write-Host ""
Write-Host "Checking service status..." -ForegroundColor Cyan
sc.exe query LANETAgent

# Try to start the service
Write-Host ""
Write-Host "Attempting to start service..." -ForegroundColor Cyan
sc.exe start LANETAgent

# Wait a moment and check status again
Start-Sleep -Seconds 5
Write-Host ""
Write-Host "Final service status:" -ForegroundColor Cyan
sc.exe query LANETAgent

# Check logs
Write-Host ""
Write-Host "Checking service logs..." -ForegroundColor Cyan
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    Write-Host "Service log content:" -ForegroundColor Yellow
    Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 10
} else {
    Write-Host "Service log not found at C:\ProgramData\LANET Agent\Logs\service.log" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
