# ========================================================================
# LANET HELPDESK AGENT - ENTERPRISE DEPLOYMENT INSTALLER
# Version: 2.0.0 Production
# Purpose: Silent installation for 2000+ client computers
# Requirements: PowerShell 5.0+, Administrator privileges
# ========================================================================

param(
    [string]$Token = "LANET-75F6-EC23-85DC9D",
    [string]$ServerUrl = "http://localhost:5001/api",
    [switch]$Silent,
    [switch]$Uninstall,
    [switch]$Verify
)

# Configuration
$AgentVersion = "2.0.0"
$ServiceName = "LANETAgent"
$InstallDir = "C:\Program Files\LANET Agent"
$LogDir = "C:\ProgramData\LANET Agent\Logs"
$LogFile = "$LogDir\installation.log"

# Create log directory
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $logEntry
    if (-not $Silent) {
        switch ($Level) {
            "ERROR" { Write-Host $Message -ForegroundColor Red }
            "WARNING" { Write-Host $Message -ForegroundColor Yellow }
            "SUCCESS" { Write-Host $Message -ForegroundColor Green }
            default { Write-Host $Message -ForegroundColor White }
        }
    }
}

# Initialize installation
Write-Log "LANET Agent Enterprise Installation Started"
Write-Log "Version: $AgentVersion"
Write-Log "Token: $Token"
Write-Log "Server: $ServerUrl"
Write-Log "Silent Mode: $Silent"

if (-not $Silent) {
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host "LANET HELPDESK AGENT - ENTERPRISE INSTALLER v$AgentVersion" -ForegroundColor Cyan
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Installation Token: $Token" -ForegroundColor White
    Write-Host "Server URL: $ServerUrl" -ForegroundColor White
    Write-Host "Installation Directory: $InstallDir" -ForegroundColor White
    Write-Host ""
}

# Check administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Log "ERROR: Administrator privileges required" "ERROR"
    if (-not $Silent) {
        Write-Host "This installer must be run as Administrator!" -ForegroundColor Red
        Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
    }
    exit 1
}

Write-Log "Administrator privileges confirmed"

# Handle uninstall
if ($Uninstall) {
    Write-Log "Uninstalling LANET Agent"
    if (-not $Silent) { Write-Host "Uninstalling LANET Agent..." -ForegroundColor Yellow }
    
    # Stop and remove service
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    sc.exe delete $ServiceName | Out-Null
    
    # Remove installation directory
    if (Test-Path $InstallDir) {
        Remove-Item $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Write-Log "Uninstallation completed" "SUCCESS"
    if (-not $Silent) { Write-Host "Uninstallation completed successfully!" -ForegroundColor Green }
    exit 0
}

# Handle verification
if ($Verify) {
    Write-Log "Verifying LANET Agent installation"
    if (-not $Silent) { Write-Host "Verifying installation..." -ForegroundColor Yellow }
    
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq "Running") {
        Write-Log "Verification successful - Service is running" "SUCCESS"
        if (-not $Silent) {
            Write-Host "✅ Service Status: Running" -ForegroundColor Green
            Write-Host "✅ Installation Directory: $(Test-Path $InstallDir)" -ForegroundColor Green
            Write-Host "✅ Log Directory: $(Test-Path $LogDir)" -ForegroundColor Green
        }
        exit 0
    } else {
        Write-Log "Verification failed - Service not running" "ERROR"
        if (-not $Silent) { Write-Host "❌ Service is not running" -ForegroundColor Red }
        exit 1
    }
}

# Test BitLocker access
if (-not $Silent) { Write-Host "Testing BitLocker access..." -ForegroundColor Yellow }
try {
    $bitlockerVolumes = Get-BitLockerVolume -ErrorAction Stop
    $protectedCount = ($bitlockerVolumes | Where-Object { $_.ProtectionStatus -eq 'On' }).Count
    $totalCount = $bitlockerVolumes.Count
    
    Write-Log "BitLocker access successful - $protectedCount/$totalCount volumes protected"
    if (-not $Silent) {
        Write-Host "✅ BitLocker access confirmed" -ForegroundColor Green
        Write-Host "   Protected volumes: $protectedCount/$totalCount" -ForegroundColor White
    }
} catch {
    Write-Log "BitLocker access test failed: $($_.Exception.Message)" "WARNING"
    if (-not $Silent) {
        Write-Host "⚠️ BitLocker access may be limited" -ForegroundColor Yellow
    }
}

# Stop existing installation
if (-not $Silent) { Write-Host "Removing existing installation..." -ForegroundColor Yellow }
Write-Log "Stopping existing service"

try {
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    sc.exe delete $ServiceName | Out-Null
    Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*LANET*" } | Stop-Process -Force
} catch {
    Write-Log "Error stopping existing service: $($_.Exception.Message)" "WARNING"
}

# Remove existing installation
if (Test-Path $InstallDir) {
    Write-Log "Removing existing installation directory"
    Remove-Item $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
}

# Create installation directory
if (-not $Silent) { Write-Host "Creating installation directory..." -ForegroundColor Yellow }
Write-Log "Creating installation directory"

New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\modules" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\core" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\config" -Force | Out-Null

# Copy agent files
if (-not $Silent) { Write-Host "Installing agent files..." -ForegroundColor Yellow }
Write-Log "Copying agent files"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceDir = Join-Path $scriptDir "..\production_installer\agent_files"

if (-not (Test-Path "$sourceDir\main.py")) {
    Write-Log "ERROR: Source agent files not found at $sourceDir" "ERROR"
    if (-not $Silent) {
        Write-Host "ERROR: Agent source files not found!" -ForegroundColor Red
        Write-Host "Expected location: $sourceDir" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
    }
    exit 1
}

try {
    Copy-Item "$sourceDir\*" $InstallDir -Recurse -Force
    Write-Log "Agent files copied successfully"
} catch {
    Write-Log "ERROR: Failed to copy agent files: $($_.Exception.Message)" "ERROR"
    if (-not $Silent) {
        Write-Host "ERROR: Failed to copy agent files" -ForegroundColor Red
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Create service configuration
if (-not $Silent) { Write-Host "Creating service configuration..." -ForegroundColor Yellow }
Write-Log "Creating service configuration"

$config = @{
    server = @{
        url = $ServerUrl
        heartbeat_interval = 300
        inventory_interval = 3600
        metrics_interval = 300
    }
    agent = @{
        name = "LANET Helpdesk Agent"
        version = $AgentVersion
        installation_token = $Token
        log_level = "INFO"
    }
    service = @{
        name = $ServiceName
        display_name = "LANET Helpdesk Agent"
        description = "LANET Helpdesk monitoring agent with BitLocker support"
        start_type = "auto"
    }
}

$config | ConvertTo-Json -Depth 3 | Out-File "$InstallDir\config\agent_config.json" -Encoding UTF8

# Create service wrapper
Write-Log "Creating service wrapper"

$serviceWrapper = @"
import sys
import os
import time
import logging
from pathlib import Path

# Setup paths
agent_dir = Path(r"$InstallDir")
sys.path.insert(0, str(agent_dir))
sys.path.insert(0, str(agent_dir / "modules"))
sys.path.insert(0, str(agent_dir / "core"))

# Setup logging
log_dir = Path(r"$LogDir")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "service.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('lanet_service')

def main():
    try:
        logger.info('🚀 LANET Agent Service starting with SYSTEM privileges')
        logger.info('🔐 BitLocker access available with SYSTEM account')
        
        # Change to agent directory
        os.chdir(str(agent_dir))
        
        # Import and run agent
        from main import main as agent_main
        
        # Set registration token
        sys.argv = ['main.py', '--register', '$Token']
        
        # Run agent
        agent_main()
        
    except KeyboardInterrupt:
        logger.info('Service stopped by user')
    except Exception as e:
        logger.error(f'Service error: {e}', exc_info=True)
        time.sleep(60)  # Keep service alive for debugging

if __name__ == '__main__':
    main()
"@

$serviceWrapper | Out-File "$InstallDir\service_wrapper.py" -Encoding UTF8

# Install Windows service
if (-not $Silent) { Write-Host "Installing Windows service..." -ForegroundColor Yellow }
Write-Log "Installing Windows service"

# Find Python executable
$pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonExe) {
    Write-Log "ERROR: Python not found in PATH" "ERROR"
    if (-not $Silent) {
        Write-Host "ERROR: Python not found! Please install Python 3.10+ and add to PATH" -ForegroundColor Red
        Read-Host "Press Enter to exit"
    }
    exit 1
}

Write-Log "Using Python: $pythonExe"

# Create service
$serviceCommand = "`"$pythonExe`" `"$InstallDir\service_wrapper.py`""
$createResult = sc.exe create $ServiceName binPath= $serviceCommand obj= LocalSystem start= auto DisplayName= "LANET Helpdesk Agent"

if ($LASTEXITCODE -eq 0) {
    Write-Log "Windows service created successfully"
    
    # Set service description
    sc.exe description $ServiceName "LANET Helpdesk monitoring agent with BitLocker data collection (SYSTEM privileges)" | Out-Null
    
    # Start service
    if (-not $Silent) { Write-Host "Starting service..." -ForegroundColor Yellow }
    Write-Log "Starting service"
    
    $startResult = sc.exe start $ServiceName
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Service started successfully"
        
        # Wait for service initialization
        if (-not $Silent) { Write-Host "Waiting for service initialization..." -ForegroundColor Yellow }
        Write-Log "Waiting for service initialization"
        Start-Sleep -Seconds 15
        
        # Verify installation
        if (-not $Silent) { Write-Host "Verifying installation..." -ForegroundColor Yellow }
        Write-Log "Verifying installation"
        
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq "Running") {
            Write-Log "Installation successful - Service is running" "SUCCESS"
            
            if (-not $Silent) {
                Write-Host ""
                Write-Host "========================================================================" -ForegroundColor Green
                Write-Host "INSTALLATION SUCCESSFUL!" -ForegroundColor Green
                Write-Host "========================================================================" -ForegroundColor Green
                Write-Host ""
                Write-Host "Service Details:" -ForegroundColor Cyan
                Write-Host "- Name: $ServiceName" -ForegroundColor White
                Write-Host "- Status: Running" -ForegroundColor Green
                Write-Host "- Privileges: SYSTEM (BitLocker access enabled)" -ForegroundColor White
                Write-Host "- Token: $Token" -ForegroundColor White
                Write-Host "- Version: $AgentVersion" -ForegroundColor White
                Write-Host ""
                Write-Host "Log Files:" -ForegroundColor Cyan
                Write-Host "- Installation: $LogFile" -ForegroundColor White
                Write-Host "- Service: $LogDir\service.log" -ForegroundColor White
                Write-Host ""
                Write-Host "The agent will automatically:" -ForegroundColor Yellow
                Write-Host "- Register with the helpdesk system" -ForegroundColor White
                Write-Host "- Collect hardware and software inventory" -ForegroundColor White
                Write-Host "- Collect BitLocker recovery keys" -ForegroundColor White
                Write-Host "- Send regular heartbeats" -ForegroundColor White
                Write-Host ""
                Write-Host "Installation completed successfully!" -ForegroundColor Green
            }
            exit 0
        } else {
            Write-Log "Installation failed - Service not running" "ERROR"
            if (-not $Silent) {
                Write-Host "ERROR: Service installation completed but service is not running" -ForegroundColor Red
                Write-Host "Check the log files:" -ForegroundColor Yellow
                Write-Host "- Installation: $LogFile" -ForegroundColor White
                Write-Host "- Service: $LogDir\service.log" -ForegroundColor White
                Read-Host "Press Enter to exit"
            }
            exit 1
        }
    } else {
        Write-Log "Failed to start service" "ERROR"
        if (-not $Silent) {
            Write-Host "ERROR: Failed to start service" -ForegroundColor Red
            Write-Host "Check the log file: $LogFile" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
        }
        exit 1
    }
} else {
    Write-Log "Failed to create service" "ERROR"
    if (-not $Silent) {
        Write-Host "ERROR: Failed to create Windows service" -ForegroundColor Red
        Write-Host "Check the log file: $LogFile" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
    }
    exit 1
}
