# Fix LANET Agent Service Wrapper - Run as Administrator
Write-Host "Fixing LANET Agent Service Wrapper..." -ForegroundColor Green

# Stop service if running
Write-Host "Stopping LANETAgent service..." -ForegroundColor Yellow
sc.exe stop LANETAgent

# Wait a moment
Start-Sleep -Seconds 3

# Copy fixed service wrapper
Write-Host "Copying fixed service wrapper..." -ForegroundColor Yellow
Copy-Item ".\service_wrapper_fixed.py" "C:\Program Files\LANET Agent\service_wrapper.py" -Force

# Verify the fix
Write-Host "Verifying fix..." -ForegroundColor Yellow
$content = Get-Content "C:\Program Files\LANET Agent\service_wrapper.py" | Select-String "ProgramData"
if ($content) {
    Write-Host "✅ Service wrapper fixed successfully!" -ForegroundColor Green
    Write-Host "New log directory: C:/ProgramData/LANET Agent/Logs" -ForegroundColor Cyan
} else {
    Write-Host "❌ Fix failed - ProgramData path not found" -ForegroundColor Red
    exit 1
}

# Test the service wrapper manually
Write-Host ""
Write-Host "Testing service wrapper manually..." -ForegroundColor Yellow
$testProcess = Start-Process -FilePath "C:\Python310\python.exe" -ArgumentList "C:\Program Files\LANET Agent\service_wrapper.py" -Wait -PassThru -WindowStyle Hidden

if ($testProcess.ExitCode -eq 0) {
    Write-Host "✅ Service wrapper test passed!" -ForegroundColor Green
} else {
    Write-Host "❌ Service wrapper test failed with exit code: $($testProcess.ExitCode)" -ForegroundColor Red
}

# Start the service
Write-Host ""
Write-Host "Starting LANETAgent service..." -ForegroundColor Yellow
sc.exe start LANETAgent

# Wait a moment for service to start
Start-Sleep -Seconds 5

# Check service status
Write-Host ""
Write-Host "Final service status:" -ForegroundColor Cyan
sc.exe query LANETAgent

# Check logs
Write-Host ""
Write-Host "Checking service logs..." -ForegroundColor Cyan
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    Write-Host "✅ Service log found!" -ForegroundColor Green
    Write-Host "Recent log entries:" -ForegroundColor Yellow
    Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 10
} else {
    Write-Host "❌ Service log not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
