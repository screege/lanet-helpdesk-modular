# Fix Registration Bug - Copy corrected agent and test
Write-Host "========================================" -ForegroundColor Green
Write-Host "FIXING REGISTRATION BUG" -ForegroundColor Green
Write-Host "Problem: Agent expects data at root level" -ForegroundColor Green
Write-Host "Backend: Returns data inside 'data' field" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 1. Stop service
Write-Host "1. Stopping LANETAgent service..." -ForegroundColor Yellow
sc.exe stop LANETAgent | Out-Null
Start-Sleep -Seconds 3

# 2. Copy corrected agent file
Write-Host "2. Copying corrected agent file..." -ForegroundColor Yellow
takeown /f "C:\Program Files\LANET Agent\lanet_agent.py" /a | Out-Null
icacls "C:\Program Files\LANET Agent\lanet_agent.py" /grant Administrators:F | Out-Null
Copy-Item "C:\lanet-helpdesk-v3\deployment\packages\lanet-agent-windows-v2.py" "C:\Program Files\LANET Agent\lanet_agent.py" -Force

Write-Host "   ✅ Agent file updated with registration fix" -ForegroundColor Green

# 3. Test manual registration
Write-Host "3. Testing manual registration..." -ForegroundColor Yellow
$testOutput = & "C:\Python310\python.exe" "C:\Program Files\LANET Agent\lanet_agent.py" "--register" "LANET-75F6-EC23-85DC9D" 2>&1
Write-Host "Registration test output:" -ForegroundColor Cyan
$testOutput | ForEach-Object {
    if ($_ -match "Registration successful") {
        Write-Host "   $_" -ForegroundColor Green
    } elseif ($_ -match "failed|error|ERROR") {
        Write-Host "   $_" -ForegroundColor Red
    } else {
        Write-Host "   $_" -ForegroundColor White
    }
}

# 4. Start service
Write-Host "4. Starting LANETAgent service..." -ForegroundColor Yellow
sc.exe start LANETAgent

# 5. Wait for service to initialize
Write-Host "5. Waiting for service to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 6. Check service status
Write-Host "6. Checking service status..." -ForegroundColor Cyan
sc.exe query LANETAgent

# 7. Check logs
Write-Host ""
Write-Host "7. Checking service logs..." -ForegroundColor Cyan
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    $logs = Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 10
    Write-Host "Recent service logs:" -ForegroundColor Yellow
    $logs | ForEach-Object {
        if ($_ -match "registration successful|Successfully registered") {
            Write-Host "   $_" -ForegroundColor Green
        } elseif ($_ -match "registration failed|Registration failed|ERROR") {
            Write-Host "   $_" -ForegroundColor Red
        } elseif ($_ -match "Starting agent main loop") {
            Write-Host "   $_" -ForegroundColor Green
        } elseif ($_ -match "Agent not registered, skipping cycle") {
            Write-Host "   $_" -ForegroundColor Red
        } elseif ($_ -match "send_heartbeat|heartbeat") {
            Write-Host "   $_" -ForegroundColor Green
        } else {
            Write-Host "   $_" -ForegroundColor White
        }
    }
} else {
    Write-Host "❌ Service log not found" -ForegroundColor Red
}

# 8. Wait for heartbeat cycle and check backend
Write-Host ""
Write-Host "8. Waiting for heartbeat cycle (60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# 9. Check backend for online status
Write-Host "9. Checking backend for agent status..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001/api/assets/" -Method GET -TimeoutSec 10
    $assets = ($response.Content | ConvertFrom-Json).data.assets
    
    $ourAgent = $assets | Where-Object { $_.name -like "*Agent*" -or $_.name -like "*TEST*" -or $_.name -like "*BENNY*" }
    if ($ourAgent) {
        Write-Host "   📋 Agent found in backend:" -ForegroundColor Cyan
        Write-Host "      Name: $($ourAgent.name)" -ForegroundColor White
        Write-Host "      Status: $($ourAgent.agent_status)" -ForegroundColor $(if($ourAgent.agent_status -eq "online") {"Green"} else {"Yellow"})
        Write-Host "      Connection: $($ourAgent.connection_status)" -ForegroundColor $(if($ourAgent.connection_status -eq "online") {"Green"} else {"Yellow"})
        Write-Host "      Last Heartbeat: $($ourAgent.last_heartbeat)" -ForegroundColor White
        Write-Host "      Client: $($ourAgent.client_name)" -ForegroundColor White
        Write-Host "      Site: $($ourAgent.site_name)" -ForegroundColor White
        
        if ($ourAgent.agent_status -eq "online") {
            Write-Host ""
            Write-Host "   🎉 SUCCESS! Agent is now ONLINE!" -ForegroundColor Green
            Write-Host "   📊 Agent should appear in frontend now!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "   ⚠️ Agent registered but still offline - may need more time" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ❌ Agent not found in backend" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Cannot check backend: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Registration bug fix completed!" -ForegroundColor Green
Write-Host "Check frontend at: http://localhost:5173" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
