# Apply Final Fix to Installed Agent - Run as Administrator
Write-Host "APPLYING FINAL FIX TO INSTALLED AGENT" -ForegroundColor Green
Write-Host ""

# Stop service
Write-Host "1. Stopping service..." -ForegroundColor Yellow
sc.exe stop LANETAgent | Out-Null

# Copy the corrected agent file
Write-Host "2. Copying corrected agent file..." -ForegroundColor Yellow
takeown /f "C:\Program Files\LANET Agent\lanet_agent.py" /a | Out-Null
icacls "C:\Program Files\LANET Agent\lanet_agent.py" /grant Administrators:F | Out-Null
Copy-Item "C:\lanet-helpdesk-v3\deployment\packages\lanet-agent-windows-v2.py" "C:\Program Files\LANET Agent\lanet_agent.py" -Force

Write-Host "   ✅ Agent file updated with all fixes" -ForegroundColor Green

# Test the agent manually
Write-Host "3. Testing agent manually..." -ForegroundColor Yellow
$testOutput = & "C:\Python310\python.exe" "C:\Program Files\LANET Agent\lanet_agent.py" 2>&1
Write-Host "Test output (first 10 lines):" -ForegroundColor Cyan
$testOutput | Select-Object -First 10 | ForEach-Object {
    if ($_ -match "Successfully registered|Registration successful") {
        Write-Host "   $_" -ForegroundColor Green
    } elseif ($_ -match "Registration failed|ERROR") {
        Write-Host "   $_" -ForegroundColor Red
    } else {
        Write-Host "   $_" -ForegroundColor White
    }
}

# Start service
Write-Host ""
Write-Host "4. Starting service..." -ForegroundColor Yellow
sc.exe start LANETAgent

# Wait and check
Write-Host "5. Waiting for service to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "6. Checking service status..." -ForegroundColor Cyan
sc.exe query LANETAgent

# Check logs
Write-Host ""
Write-Host "7. Checking recent logs..." -ForegroundColor Cyan
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    $logs = Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 10
    Write-Host "Recent service logs:" -ForegroundColor Yellow
    $logs | ForEach-Object {
        if ($_ -match "Successfully registered|Registration successful") {
            Write-Host "   $_" -ForegroundColor Green
        } elseif ($_ -match "Registration failed|ERROR") {
            Write-Host "   $_" -ForegroundColor Red
        } elseif ($_ -match "Starting agent main loop") {
            Write-Host "   $_" -ForegroundColor Green
        } elseif ($_ -match "Agent not registered, skipping cycle") {
            Write-Host "   $_" -ForegroundColor Red
        } else {
            Write-Host "   $_" -ForegroundColor White
        }
    }
}

# Wait for heartbeat and check backend
Write-Host ""
Write-Host "8. Waiting for heartbeat cycle (60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

Write-Host "9. Checking backend..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001/api/assets/" -Method GET -TimeoutSec 10
    $assets = ($response.Content | ConvertFrom-Json).data.assets
    
    $ourAgent = $assets | Where-Object { 
        $_.name -like "*Agent*" -or $_.name -like "*TEST*" -or $_.name -like "*BENNY*" -or $_.name -like "*Unknown*"
    } | Sort-Object { [DateTime]$_.last_seen } -Descending | Select-Object -First 1
    
    if ($ourAgent) {
        Write-Host "   📋 Latest agent found:" -ForegroundColor Cyan
        Write-Host "      Name: $($ourAgent.name)" -ForegroundColor White
        Write-Host "      Status: $($ourAgent.agent_status)" -ForegroundColor $(if($ourAgent.agent_status -eq "online") {"Green"} else {"Yellow"})
        Write-Host "      Last Heartbeat: $($ourAgent.last_heartbeat)" -ForegroundColor White
        Write-Host "      Client: $($ourAgent.client_name)" -ForegroundColor White
        Write-Host "      Site: $($ourAgent.site_name)" -ForegroundColor White
        
        if ($ourAgent.agent_status -eq "online") {
            Write-Host ""
            Write-Host "   🎉 SUCCESS! Agent is ONLINE!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "   ⚠️ Agent found but still offline" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ❌ No agent found in backend" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Cannot check backend: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Fix application completed!" -ForegroundColor Green
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
