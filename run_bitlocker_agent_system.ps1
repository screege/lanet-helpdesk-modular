# Run LANET Agent with SYSTEM privileges for BitLocker access
Write-Host "🔐 LANET Agent - SYSTEM Privileges for BitLocker" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Running with Administrator privileges" -ForegroundColor Green

# Test BitLocker access first
Write-Host ""
Write-Host "🔍 Testing BitLocker access..." -ForegroundColor Yellow
try {
    $bitlockerVolumes = Get-BitLockerVolume -ErrorAction Stop
    $protectedCount = ($bitlockerVolumes | Where-Object { $_.ProtectionStatus -eq 'On' }).Count
    $totalCount = $bitlockerVolumes.Count
    
    Write-Host "✅ BitLocker access successful!" -ForegroundColor Green
    Write-Host "   Total volumes: $totalCount" -ForegroundColor White
    Write-Host "   Protected volumes: $protectedCount" -ForegroundColor White
    
    foreach ($volume in $bitlockerVolumes) {
        $status = if ($volume.ProtectionStatus -eq 'On') { "🔒 Protected" } else { "🔓 Unprotected" }
        Write-Host "   - $($volume.MountPoint): $status" -ForegroundColor White
        
        if ($volume.ProtectionStatus -eq 'On') {
            # Try to get recovery key
            $keyProtectors = $volume.KeyProtector
            $recoveryKey = $keyProtectors | Where-Object { $_.KeyProtectorType -eq 'RecoveryPassword' } | Select-Object -First 1
            if ($recoveryKey) {
                Write-Host "     Recovery Key ID: $($recoveryKey.KeyProtectorId)" -ForegroundColor Cyan
                Write-Host "     Recovery Password: $($recoveryKey.RecoveryPassword)" -ForegroundColor Cyan
            }
        }
    }
    
    if ($protectedCount -eq 0) {
        Write-Host "⚠️ No BitLocker protected volumes found!" -ForegroundColor Yellow
        Write-Host "Make sure BitLocker is enabled on at least one drive." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ BitLocker access failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "This indicates a permission issue." -ForegroundColor Yellow
}

Write-Host ""

# Clean up any existing service
Write-Host "🧹 Cleaning up existing service..." -ForegroundColor Yellow
sc.exe stop LANETAgent 2>$null | Out-Null
sc.exe delete LANETAgent 2>$null | Out-Null
Write-Host "   ✅ Cleanup completed" -ForegroundColor Green

# Create a simple Python script that runs the agent
Write-Host "📝 Creating BitLocker agent script..." -ForegroundColor Yellow

$agentScript = @"
import sys
import os
import logging
import subprocess
import json
from pathlib import Path

# Setup logging
log_dir = Path('C:/Program Files/LANET Agent/logs')
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'bitlocker_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('bitlocker_agent')

def test_bitlocker_access():
    '''Test BitLocker access with current privileges'''
    try:
        logger.info('🔍 Testing BitLocker access...')
        
        result = subprocess.run([
            'powershell', '-Command', 
            'Get-BitLockerVolume | ConvertTo-Json -Depth 3'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            bitlocker_data = json.loads(result.stdout)
            if isinstance(bitlocker_data, dict):
                bitlocker_data = [bitlocker_data]
            
            protected_count = sum(1 for vol in bitlocker_data if vol.get('ProtectionStatus') == 'On')
            total_count = len(bitlocker_data)
            
            logger.info(f'✅ BitLocker access successful: {protected_count}/{total_count} volumes protected')
            
            for volume in bitlocker_data:
                mount_point = volume.get('MountPoint', 'Unknown')
                protection_status = volume.get('ProtectionStatus', 'Unknown')
                logger.info(f'   - {mount_point}: {protection_status}')
            
            return True, protected_count, total_count
        else:
            logger.error(f'❌ BitLocker access failed: {result.stderr}')
            return False, 0, 0
            
    except Exception as e:
        logger.error(f'❌ BitLocker test exception: {e}')
        return False, 0, 0

def run_agent():
    '''Run the LANET agent'''
    try:
        # Test BitLocker first
        bitlocker_ok, protected, total = test_bitlocker_access()
        
        if not bitlocker_ok:
            logger.warning('⚠️ BitLocker access failed - agent may not collect BitLocker data')
        
        # Add agent directory to path
        agent_dir = Path('C:/lanet-helpdesk-v3/production_installer/agent_files')
        sys.path.insert(0, str(agent_dir))
        sys.path.insert(0, str(agent_dir / 'modules'))
        sys.path.insert(0, str(agent_dir / 'core'))
        
        # Change to agent directory
        os.chdir(str(agent_dir))
        
        logger.info('🚀 Starting LANET Agent with BitLocker support...')
        logger.info(f'Expected BitLocker result: {protected}/{total} volumes protected')
        
        # Import and run the agent
        from main import main as agent_main
        
        # Set command line arguments for registration
        sys.argv = ['main.py', '--register', 'LANET-75F6-EC23-85DC9D']
        
        # Run the agent
        agent_main()
        
    except KeyboardInterrupt:
        logger.info('Agent stopped by user')
    except Exception as e:
        logger.error(f'Agent error: {e}', exc_info=True)

if __name__ == '__main__':
    run_agent()
"@

# Create the agent directory and script
$agentDir = "C:\Program Files\LANET Agent"
if (-not (Test-Path $agentDir)) {
    New-Item -ItemType Directory -Path $agentDir -Force | Out-Null
}

$agentScript | Out-File -FilePath "$agentDir\bitlocker_agent.py" -Encoding UTF8 -Force

Write-Host "   ✅ Agent script created" -ForegroundColor Green

# Run the agent with SYSTEM privileges using Task Scheduler
Write-Host "🚀 Running agent with SYSTEM privileges..." -ForegroundColor Yellow

$taskName = "LANET_BitLocker_Agent"

# Delete existing task if it exists
schtasks /delete /tn $taskName /f 2>$null | Out-Null

# Create scheduled task to run as SYSTEM
$taskAction = "python `"$agentDir\bitlocker_agent.py`""
$createTask = schtasks /create /tn $taskName /tr $taskAction /sc once /st 23:59 /ru SYSTEM /f

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Scheduled task created" -ForegroundColor Green
    
    # Run the task immediately
    Write-Host "   🏃 Starting task..." -ForegroundColor Yellow
    schtasks /run /tn $taskName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Task started successfully" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "🎉 LANET Agent is now running with SYSTEM privileges!" -ForegroundColor Green
        Write-Host "===============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Expected Results:" -ForegroundColor Cyan
        Write-Host "- BitLocker data should be collected: $protectedCount/$totalCount volumes" -ForegroundColor White
        Write-Host "- Agent should register and send heartbeats" -ForegroundColor White
        Write-Host "- Data should appear in frontend within 2-3 minutes" -ForegroundColor White
        Write-Host ""
        Write-Host "To check logs:" -ForegroundColor Yellow
        Write-Host "Get-Content '$agentDir\logs\bitlocker_agent.log' -Tail 20" -ForegroundColor Gray
        Write-Host ""
        Write-Host "To stop the agent:" -ForegroundColor Yellow
        Write-Host "schtasks /end /tn $taskName" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Frontend URL: http://localhost:5173" -ForegroundColor Cyan
        
        # Wait a moment and show initial logs
        Write-Host "⏳ Waiting for agent to initialize..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15
        
        $logFile = "$agentDir\logs\bitlocker_agent.log"
        if (Test-Path $logFile) {
            Write-Host ""
            Write-Host "📋 Initial agent logs:" -ForegroundColor Yellow
            Get-Content $logFile -Tail 10 | ForEach-Object {
                if ($_ -match "BitLocker|protected|volumes") {
                    Write-Host "   $_" -ForegroundColor Green
                } elseif ($_ -match "ERROR|Failed|failed") {
                    Write-Host "   $_" -ForegroundColor Red
                } else {
                    Write-Host "   $_" -ForegroundColor White
                }
            }
        }
        
    } else {
        Write-Host "   ❌ Failed to start task" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ Failed to create scheduled task" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to continue"
