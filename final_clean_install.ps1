# LANET Agent - Final Clean Installation with Bug Fix
Write-Host "========================================" -ForegroundColor Green
Write-Host "LANET Agent - Final Clean Installation" -ForegroundColor Green
Write-Host "Bug Fix: Registration logic corrected" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 1. Complete cleanup
Write-Host "1. Performing complete cleanup..." -ForegroundColor Yellow
sc.exe stop LANETAgent 2>$null | Out-Null
sc.exe delete LANETAgent 2>$null | Out-Null
Remove-Item "C:\Program Files\LANET Agent" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\ProgramData\LANET Agent" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   ✅ Cleanup completed" -ForegroundColor Green

# 2. Fresh installation
Write-Host "2. Installing with corrected registration logic..." -ForegroundColor Yellow
$installProcess = Start-Process -FilePath ".\dist\LANET_Agent_Enterprise_Installer_v2.exe" -ArgumentList "--silent", "--token", "LANET-75F6-EC23-85DC9D", "--server", "http://localhost:5001/api" -Wait -PassThru
if ($installProcess.ExitCode -eq 0) {
    Write-Host "   ✅ Installation completed successfully" -ForegroundColor Green
} else {
    Write-Host "   ❌ Installation failed with exit code: $($installProcess.ExitCode)" -ForegroundColor Red
    exit 1
}

# 3. Wait for installation to settle
Write-Host "3. Waiting for installation to settle..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 4. Start the service
Write-Host "4. Starting LANETAgent service..." -ForegroundColor Yellow
$startResult = sc.exe start LANETAgent
Write-Host "   Start result: $startResult" -ForegroundColor Gray

# 5. Wait for service to initialize
Write-Host "5. Waiting for service to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 6. Check service status
Write-Host "6. Checking service status..." -ForegroundColor Cyan
sc.exe query LANETAgent

# 7. Monitor logs for registration
Write-Host ""
Write-Host "7. Monitoring registration process..." -ForegroundColor Cyan
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    Write-Host "Service log (last 10 lines):" -ForegroundColor Yellow
    Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 10 | ForEach-Object { 
        if ($_ -match "registration successful") {
            Write-Host "   $_" -ForegroundColor Green
        } elseif ($_ -match "registration failed|ERROR") {
            Write-Host "   $_" -ForegroundColor Red
        } else {
            Write-Host "   $_" -ForegroundColor White
        }
    }
} else {
    Write-Host "❌ Service log not found" -ForegroundColor Red
}

# 8. Test backend connectivity
Write-Host ""
Write-Host "8. Testing backend connectivity..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001/api/assets/" -Method GET -TimeoutSec 10
    $assets = ($response.Content | ConvertFrom-Json).data.assets
    Write-Host "   ✅ Backend reachable - Found $($assets.Count) asset(s)" -ForegroundColor Green
    
    # Look for our agent
    $ourAgent = $assets | Where-Object { $_.name -like "*Agent*" -or $_.name -like "*TEST*" -or $_.name -like "*BENNY*" }
    if ($ourAgent) {
        Write-Host "   📋 Our agent found:" -ForegroundColor Cyan
        Write-Host "      Name: $($ourAgent.name)" -ForegroundColor White
        Write-Host "      Status: $($ourAgent.agent_status)" -ForegroundColor $(if($ourAgent.agent_status -eq "online") {"Green"} else {"Yellow"})
        Write-Host "      Last Heartbeat: $($ourAgent.last_heartbeat)" -ForegroundColor White
        Write-Host "      Client: $($ourAgent.client_name)" -ForegroundColor White
        Write-Host "      Site: $($ourAgent.site_name)" -ForegroundColor White
    } else {
        Write-Host "   ⚠️ Our agent not found in assets list" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Backend not reachable: $($_.Exception.Message)" -ForegroundColor Red
}

# 9. Wait a bit more and check for heartbeats
Write-Host ""
Write-Host "9. Waiting for heartbeat cycle (60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# 10. Final status check
Write-Host "10. Final status check..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001/api/assets/" -Method GET -TimeoutSec 10
    $assets = ($response.Content | ConvertFrom-Json).data.assets
    $ourAgent = $assets | Where-Object { $_.name -like "*Agent*" -or $_.name -like "*TEST*" -or $_.name -like "*BENNY*" }
    
    if ($ourAgent -and $ourAgent.agent_status -eq "online") {
        Write-Host "   🎉 SUCCESS! Agent is online and sending heartbeats!" -ForegroundColor Green
        Write-Host "   📊 Agent should now appear in the frontend" -ForegroundColor Green
    } elseif ($ourAgent) {
        Write-Host "   ⚠️ Agent found but still offline - may need more time" -ForegroundColor Yellow
        Write-Host "   Last seen: $($ourAgent.last_seen)" -ForegroundColor White
    } else {
        Write-Host "   ❌ Agent not found - registration may have failed" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Cannot check final status: $($_.Exception.Message)" -ForegroundColor Red
}

# 11. Show final logs
Write-Host ""
Write-Host "11. Final service logs:" -ForegroundColor Cyan
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 5 | ForEach-Object { 
        Write-Host "    $_" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installation and testing completed!" -ForegroundColor Green
Write-Host "Check the frontend at http://localhost:5173" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
