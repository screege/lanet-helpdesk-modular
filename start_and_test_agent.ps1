# Start LANET Agent and Test Communication - Run as Administrator
Write-Host "========================================" -ForegroundColor Green
Write-Host "LANET Agent - Start and Test Communication" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Start the service
Write-Host "1. Starting LANETAgent service..." -ForegroundColor Yellow
$startResult = sc.exe start LANETAgent
Write-Host "Start result: $startResult" -ForegroundColor Gray

# Wait for service to start
Write-Host "2. Waiting for service to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "3. Checking service status..." -ForegroundColor Cyan
sc.exe query LANETAgent

# Check logs
Write-Host ""
Write-Host "4. Checking recent service logs..." -ForegroundColor Cyan
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    Write-Host "Service log (last 15 lines):" -ForegroundColor Yellow
    Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 15 | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
} else {
    Write-Host "❌ Service log not found" -ForegroundColor Red
}

# Test backend connectivity
Write-Host ""
Write-Host "5. Testing backend connectivity..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001/api/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Backend is reachable - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not reachable: $($_.Exception.Message)" -ForegroundColor Red
}

# Check if agent is registered in database
Write-Host ""
Write-Host "6. Checking agent registration..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001/api/assets" -Method GET -TimeoutSec 5
    $assets = $response.Content | ConvertFrom-Json
    Write-Host "Assets in database: $($assets.Count)" -ForegroundColor Yellow
    if ($assets.Count -gt 0) {
        $assets | ForEach-Object { 
            Write-Host "  - Asset: $($_.computer_name) | Client: $($_.client_name) | Site: $($_.site_name)" -ForegroundColor White 
        }
    } else {
        Write-Host "  No assets found in database" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to check assets: $($_.Exception.Message)" -ForegroundColor Red
}

# Manual test of agent registration
Write-Host ""
Write-Host "7. Testing manual agent execution..." -ForegroundColor Cyan
Write-Host "Running agent manually for 30 seconds..." -ForegroundColor Yellow
$agentProcess = Start-Process -FilePath "C:\Python310\python.exe" -ArgumentList "C:\Program Files\LANET Agent\service_wrapper.py" -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 30
if (!$agentProcess.HasExited) {
    $agentProcess.Kill()
    Write-Host "✅ Agent ran successfully for 30 seconds" -ForegroundColor Green
} else {
    Write-Host "❌ Agent exited early with code: $($agentProcess.ExitCode)" -ForegroundColor Red
}

# Check logs again after manual run
Write-Host ""
Write-Host "8. Checking logs after manual run..." -ForegroundColor Cyan
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    Write-Host "Recent service log entries:" -ForegroundColor Yellow
    Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 10 | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Diagnosis completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
