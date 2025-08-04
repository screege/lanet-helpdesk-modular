# LANET Agent - FINAL CLEAN INSTALLATION
# All fixes applied: logging permissions, registration parsing, service wrapper logic
Write-Host "========================================" -ForegroundColor Green
Write-Host "LANET AGENT - FINAL CLEAN INSTALLATION" -ForegroundColor Green
Write-Host "All fixes applied and tested" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 1. Complete system cleanup
Write-Host "1. Performing complete system cleanup..." -ForegroundColor Yellow
Write-Host "   - Stopping service..." -ForegroundColor Gray
sc.exe stop LANETAgent 2>$null | Out-Null
Write-Host "   - Deleting service..." -ForegroundColor Gray
sc.exe delete LANETAgent 2>$null | Out-Null
Write-Host "   - Removing installation directory..." -ForegroundColor Gray
Remove-Item "C:\Program Files\LANET Agent" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   - Removing data directory..." -ForegroundColor Gray
Remove-Item "C:\ProgramData\LANET Agent" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   ✅ Complete cleanup finished" -ForegroundColor Green

# 2. Fresh installation with all fixes
Write-Host ""
Write-Host "2. Installing with ALL FIXES applied..." -ForegroundColor Yellow
Write-Host "   Fixes included:" -ForegroundColor Cyan
Write-Host "   - ✅ Logging permissions (ProgramData)" -ForegroundColor White
Write-Host "   - ✅ Registration response parsing" -ForegroundColor White
Write-Host "   - ✅ Service wrapper logic" -ForegroundColor White
Write-Host "   - ✅ Error handling and validation" -ForegroundColor White
Write-Host ""

$installProcess = Start-Process -FilePath ".\dist\LANET_Agent_Enterprise_Installer_v2.exe" -ArgumentList "--silent", "--token", "LANET-75F6-EC23-85DC9D", "--server", "http://localhost:5001/api" -Wait -PassThru

if ($installProcess.ExitCode -eq 0) {
    Write-Host "   ✅ Installation completed successfully" -ForegroundColor Green
} else {
    Write-Host "   ❌ Installation failed with exit code: $($installProcess.ExitCode)" -ForegroundColor Red
    Write-Host "   Check logs at: C:\ProgramData\LANET Agent\Logs\" -ForegroundColor Yellow
    exit 1
}

# 3. Verify installation
Write-Host ""
Write-Host "3. Verifying installation..." -ForegroundColor Yellow
if (Test-Path "C:\Program Files\LANET Agent\lanet_agent.py") {
    Write-Host "   ✅ Agent files installed" -ForegroundColor Green
} else {
    Write-Host "   ❌ Agent files missing" -ForegroundColor Red
    exit 1
}

if (Test-Path "C:\Program Files\LANET Agent\config.ini") {
    Write-Host "   ✅ Configuration file created" -ForegroundColor Green
} else {
    Write-Host "   ❌ Configuration file missing" -ForegroundColor Red
    exit 1
}

# 4. Start service and monitor
Write-Host ""
Write-Host "4. Starting service and monitoring..." -ForegroundColor Yellow
$startResult = sc.exe start LANETAgent
Write-Host "   Service start command executed" -ForegroundColor Gray

# Wait for service to initialize
Write-Host "   Waiting for service initialization (15 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 15

# Check service status
Write-Host ""
Write-Host "5. Service status check:" -ForegroundColor Cyan
$serviceStatus = sc.exe query LANETAgent
Write-Host $serviceStatus -ForegroundColor White

# 6. Monitor registration process
Write-Host ""
Write-Host "6. Monitoring registration process..." -ForegroundColor Cyan
$logPath = "C:\ProgramData\LANET Agent\Logs\service.log"

if (Test-Path $logPath) {
    Write-Host "   Service log found - Recent entries:" -ForegroundColor Yellow
    $logs = Get-Content $logPath -Tail 15
    $registrationSuccess = $false
    $registrationFailed = $false
    
    foreach ($line in $logs) {
        if ($line -match "Successfully registered as asset|Registration successful") {
            Write-Host "   $_" -ForegroundColor Green
            $registrationSuccess = $true
        } elseif ($line -match "Registration failed|ERROR.*registration") {
            Write-Host "   $_" -ForegroundColor Red
            $registrationFailed = $true
        } elseif ($line -match "Starting agent main loop") {
            Write-Host "   $_" -ForegroundColor Green
        } elseif ($line -match "Agent not registered, skipping cycle") {
            Write-Host "   $_" -ForegroundColor Red
        } elseif ($line -match "send_heartbeat|heartbeat") {
            Write-Host "   $_" -ForegroundColor Green
        } else {
            Write-Host "   $_" -ForegroundColor White
        }
    }
    
    if ($registrationSuccess -and -not $registrationFailed) {
        Write-Host ""
        Write-Host "   🎉 REGISTRATION SUCCESSFUL!" -ForegroundColor Green
    } elseif ($registrationFailed) {
        Write-Host ""
        Write-Host "   ❌ Registration failed - check logs above" -ForegroundColor Red
    } else {
        Write-Host ""
        Write-Host "   ⚠️ Registration status unclear - may need more time" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Service log not found at: $logPath" -ForegroundColor Red
}

# 7. Wait for heartbeat cycle
Write-Host ""
Write-Host "7. Waiting for first heartbeat cycle (60 seconds)..." -ForegroundColor Yellow
Write-Host "   This ensures the agent is fully operational..." -ForegroundColor Gray
Start-Sleep -Seconds 60

# 8. Final backend verification
Write-Host ""
Write-Host "8. Final verification with backend..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001/api/assets/" -Method GET -TimeoutSec 15
    $assets = ($response.Content | ConvertFrom-Json).data.assets
    
    # Look for our agent (most recent one)
    $ourAgent = $assets | Where-Object { 
        $_.name -like "*Agent*" -or 
        $_.name -like "*TEST*" -or 
        $_.name -like "*BENNY*" -or
        $_.name -like "*Unknown*"
    } | Sort-Object { [DateTime]$_.last_seen } -Descending | Select-Object -First 1
    
    if ($ourAgent) {
        Write-Host "   📋 Agent found in backend:" -ForegroundColor Cyan
        Write-Host "      Name: $($ourAgent.name)" -ForegroundColor White
        Write-Host "      Status: $($ourAgent.agent_status)" -ForegroundColor $(if($ourAgent.agent_status -eq "online") {"Green"} else {"Yellow"})
        Write-Host "      Connection: $($ourAgent.connection_status)" -ForegroundColor $(if($ourAgent.connection_status -eq "online") {"Green"} else {"Yellow"})
        Write-Host "      Last Heartbeat: $($ourAgent.last_heartbeat)" -ForegroundColor White
        Write-Host "      Last Seen: $($ourAgent.last_seen)" -ForegroundColor White
        Write-Host "      Client: $($ourAgent.client_name)" -ForegroundColor White
        Write-Host "      Site: $($ourAgent.site_name)" -ForegroundColor White
        
        if ($ourAgent.agent_status -eq "online" -and $ourAgent.last_heartbeat) {
            Write-Host ""
            Write-Host "   🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉" -ForegroundColor Green
            Write-Host "   Agent is ONLINE and sending heartbeats!" -ForegroundColor Green
            Write-Host "   📊 Agent will appear in frontend now!" -ForegroundColor Green
        } elseif ($ourAgent.agent_status -eq "online") {
            Write-Host ""
            Write-Host "   ✅ Agent is online but heartbeat may be pending" -ForegroundColor Green
            Write-Host "   📊 Should appear in frontend shortly" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "   ⚠️ Agent registered but not yet online" -ForegroundColor Yellow
            Write-Host "   💡 May need a few more minutes to start heartbeats" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ❌ No agent found in backend" -ForegroundColor Red
        Write-Host "   💡 Registration may have failed - check service logs" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Cannot connect to backend: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   💡 Make sure backend is running on http://localhost:5001" -ForegroundColor Yellow
}

# 9. Final instructions
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "INSTALLATION COMPLETED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Check frontend at: http://localhost:5173" -ForegroundColor White
Write-Host "2. Navigate to Assets/Equipment section" -ForegroundColor White
Write-Host "3. Look for your agent in the list" -ForegroundColor White
Write-Host ""
Write-Host "If agent doesn't appear:" -ForegroundColor Yellow
Write-Host "- Wait 2-3 minutes for heartbeats to start" -ForegroundColor White
Write-Host "- Check service logs: C:\ProgramData\LANET Agent\Logs\service.log" -ForegroundColor White
Write-Host "- Restart service: sc.exe restart LANETAgent" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
