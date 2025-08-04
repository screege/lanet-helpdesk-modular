# Install LANET Agent as Windows Service with SYSTEM privileges for BitLocker access
param(
    [string]$Token = "LANET-75F6-EC23-85DC9D"
)

Write-Host "🔐 LANET Agent Service Installation with BitLocker Support" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green
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
    }
    
    if ($protectedCount -eq 0) {
        Write-Host "⚠️ No BitLocker protected volumes found!" -ForegroundColor Yellow
        Write-Host "The agent will still be installed but BitLocker data will be empty." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ BitLocker access failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "The agent will be installed but may not collect BitLocker data." -ForegroundColor Yellow
}

Write-Host ""

# Stop and remove existing service if it exists
Write-Host "🛑 Stopping existing LANET Agent service..." -ForegroundColor Yellow
try {
    Stop-Service -Name "LANETAgent" -Force -ErrorAction SilentlyContinue
    sc.exe delete "LANETAgent" | Out-Null
    Write-Host "   ✅ Existing service removed" -ForegroundColor Green
} catch {
    Write-Host "   ℹ️ No existing service found" -ForegroundColor Gray
}

# Create service installation directory
$servicePath = "C:\Program Files\LANET Agent Service"
Write-Host "📁 Creating service directory: $servicePath" -ForegroundColor Yellow

if (Test-Path $servicePath) {
    Remove-Item $servicePath -Recurse -Force
}
New-Item -ItemType Directory -Path $servicePath -Force | Out-Null

# Copy agent files
Write-Host "📋 Copying agent files..." -ForegroundColor Yellow
$sourceDir = "C:\lanet-helpdesk-v3\production_installer\agent_files"
Copy-Item "$sourceDir\*" $servicePath -Recurse -Force

# Create service configuration
Write-Host "⚙️ Creating service configuration..." -ForegroundColor Yellow

$serviceConfig = @"
{
    "server": {
        "url": "http://localhost:5001/api",
        "heartbeat_interval": 300,
        "inventory_interval": 3600,
        "metrics_interval": 300
    },
    "agent": {
        "name": "LANET Agent Service",
        "version": "2.0.0",
        "installation_token": "$Token",
        "log_level": "INFO"
    },
    "service": {
        "name": "LANETAgent",
        "display_name": "LANET Helpdesk Agent",
        "description": "LANET Helpdesk Agent - System monitoring and BitLocker data collection",
        "start_type": "auto"
    }
}
"@

$serviceConfig | Out-File -FilePath "$servicePath\config\agent_config.json" -Encoding UTF8 -Force

# Create service wrapper script
$serviceWrapper = @"
import sys
import os
import time
import logging
from pathlib import Path

# Add the agent directory to Python path
agent_dir = Path(__file__).parent
sys.path.insert(0, str(agent_dir))
sys.path.insert(0, str(agent_dir / 'modules'))
sys.path.insert(0, str(agent_dir / 'core'))

def run_agent_service():
    '''Run the LANET agent as a Windows service'''
    
    # Setup logging
    log_dir = agent_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'service.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger('lanet_service')
    logger.info('🚀 LANET Agent Service starting with SYSTEM privileges...')
    logger.info('🔐 BitLocker access should be available with SYSTEM privileges')
    
    try:
        # Import and run the agent
        from main import main as agent_main
        
        # Set the token for registration
        sys.argv = ['main.py', '--register', '$Token']
        
        logger.info('Starting agent main function...')
        agent_main()
        
    except KeyboardInterrupt:
        logger.info('Service stopped by user')
    except Exception as e:
        logger.error(f'Service error: {e}', exc_info=True)
        raise

if __name__ == '__main__':
    run_agent_service()
"@

$serviceWrapper | Out-File -FilePath "$servicePath\service_runner.py" -Encoding UTF8 -Force

# Install the service using sc.exe
Write-Host "🔧 Installing Windows service..." -ForegroundColor Yellow

$pythonPath = (Get-Command python).Source
$serviceCommand = "`"$pythonPath`" `"$servicePath\service_runner.py`""

# Create the service
$createResult = sc.exe create LANETAgent binPath= $serviceCommand obj= LocalSystem start= auto DisplayName= "LANET Helpdesk Agent"

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Service created successfully" -ForegroundColor Green
    
    # Set service description
    sc.exe description LANETAgent "LANET Helpdesk Agent - System monitoring and BitLocker data collection with SYSTEM privileges"
    
    # Start the service
    Write-Host "🚀 Starting LANET Agent service..." -ForegroundColor Yellow
    $startResult = sc.exe start LANETAgent
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Service started successfully" -ForegroundColor Green
        
        # Wait a moment for the service to initialize
        Start-Sleep -Seconds 10
        
        # Check service status
        Write-Host "📊 Checking service status..." -ForegroundColor Yellow
        $serviceStatus = Get-Service -Name LANETAgent
        Write-Host "   Service Status: $($serviceStatus.Status)" -ForegroundColor White
        
        # Check logs
        $logFile = "$servicePath\logs\service.log"
        if (Test-Path $logFile) {
            Write-Host "📋 Recent service logs:" -ForegroundColor Yellow
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
        
        Write-Host ""
        Write-Host "🎉 LANET Agent Service Installation Complete!" -ForegroundColor Green
        Write-Host "=========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Service Details:" -ForegroundColor Cyan
        Write-Host "- Name: LANETAgent" -ForegroundColor White
        Write-Host "- Running as: SYSTEM (required for BitLocker access)" -ForegroundColor White
        Write-Host "- Auto-start: Enabled" -ForegroundColor White
        Write-Host "- Token: $Token" -ForegroundColor White
        Write-Host "- Expected BitLocker: $protectedCount/$totalCount volumes protected" -ForegroundColor White
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Yellow
        Write-Host "1. Wait 2-3 minutes for initial registration and heartbeat" -ForegroundColor White
        Write-Host "2. Check frontend at: http://localhost:5173" -ForegroundColor White
        Write-Host "3. Look for your computer with BitLocker data" -ForegroundColor White
        Write-Host ""
        Write-Host "To check service logs: Get-Content '$servicePath\logs\service.log' -Tail 20" -ForegroundColor Gray
        
    } else {
        Write-Host "   ❌ Failed to start service" -ForegroundColor Red
        Write-Host "   Check Windows Event Log for details" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "   ❌ Failed to create service" -ForegroundColor Red
    Write-Host "   Error: $createResult" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
