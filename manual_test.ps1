# Manual Test - Update service wrapper and test registration
Write-Host "Manual Test - Updating service wrapper with bug fix" -ForegroundColor Green
Write-Host ""

# 1. Stop service
Write-Host "1. Stopping service..." -ForegroundColor Yellow
sc.exe stop LANETAgent | Out-Null

# 2. Update service wrapper with corrected version
Write-Host "2. Updating service wrapper..." -ForegroundColor Yellow
$serviceWrapperContent = @'
#!/usr/bin/env python3
"""
LANET Agent Service Wrapper
Runs the LANET agent as a Windows service without pywin32 dependency
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging for the service"""
    try:
        log_dir = Path("C:/ProgramData/LANET Agent/Logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "service.log"),
                logging.StreamHandler()
            ]
        )
    except Exception as e:
        # Fallback to console only if file logging fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to setup file logging: {e}")
        return logger
    
    return logging.getLogger(__name__)

def run_agent():
    """Run the LANET agent"""
    logger = setup_logging()
    logger.info("LANET Agent Service starting...")

    try:
        # Import the agent class
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Import and initialize the agent
        from lanet_agent import LANETAgentV2
        agent = LANETAgentV2()

        # Check if agent needs registration
        if not agent.registered:
            logger.info("Agent not registered, attempting registration...")
            installation_token = agent.config.get('REGISTRATION', 'installation_token', fallback='')
            if installation_token:
                try:
                    if agent.register_with_token(installation_token):
                        logger.info("Agent registration successful")
                    else:
                        logger.error("Agent registration failed")
                        return
                except Exception as e:
                    logger.error(f"Agent registration failed: {e}")
                    return
            else:
                logger.error("No installation token found")
                return

        # Main service loop
        logger.info("Starting agent main loop...")
        while True:
            try:
                # Run agent cycle
                if agent.registered:
                    agent.send_heartbeat()
                    agent.send_inventory()
                    agent.send_metrics()
                else:
                    logger.warning("Agent not registered, skipping cycle")

                # Wait for next cycle
                time.sleep(60)  # 1 minute between cycles

            except KeyboardInterrupt:
                logger.info("Service interrupted by user")
                break
            except Exception as e:
                logger.error(f"Agent cycle error: {e}")
                time.sleep(30)  # Wait 30 seconds on error

    except Exception as e:
        logger.error(f"Service error: {e}")
        raise

if __name__ == '__main__':
    run_agent()
'@

# Write the corrected service wrapper
$serviceWrapperContent | Out-File -FilePath "C:\Program Files\LANET Agent\service_wrapper.py" -Encoding UTF8 -Force

Write-Host "   ✅ Service wrapper updated with bug fix" -ForegroundColor Green

# 3. Test manual execution
Write-Host "3. Testing manual execution..." -ForegroundColor Yellow
$testProcess = Start-Process -FilePath "C:\Python310\python.exe" -ArgumentList "C:\Program Files\LANET Agent\service_wrapper.py" -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 30
if (!$testProcess.HasExited) {
    $testProcess.Kill()
    Write-Host "   ✅ Manual test successful - agent ran for 30 seconds" -ForegroundColor Green
} else {
    Write-Host "   ❌ Manual test failed - agent exited with code: $($testProcess.ExitCode)" -ForegroundColor Red
}

# 4. Check logs
Write-Host "4. Checking logs..." -ForegroundColor Yellow
if (Test-Path "C:\ProgramData\LANET Agent\Logs\service.log") {
    $logs = Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 10
    Write-Host "Recent logs:" -ForegroundColor Cyan
    $logs | ForEach-Object {
        if ($_ -match "registration successful") {
            Write-Host "   $_" -ForegroundColor Green
        } elseif ($_ -match "registration failed|ERROR") {
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

# 5. Start service
Write-Host "5. Starting service..." -ForegroundColor Yellow
sc.exe start LANETAgent

Write-Host ""
Write-Host "Manual test completed!" -ForegroundColor Green
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
'@

# Save and execute
$manualTestContent | Out-File -FilePath "manual_test_temp.ps1" -Encoding UTF8 -Force
Start-Process PowerShell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File manual_test_temp.ps1"
