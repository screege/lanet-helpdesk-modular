# ========================================================================
# LANET HELPDESK AGENT - SILENT ENTERPRISE DEPLOYMENT
# Version: 3.0.0 Enterprise
# Purpose: Completely automated deployment for mass installation
# Usage: .\LANET_Agent_Silent_Enterprise.ps1 -Token "LANET-XXX-XXX-XXX" -ServerUrl "https://helpdesk.company.com/api"
# ========================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Token,
    
    [Parameter(Mandatory=$true)]
    [string]$ServerUrl,
    
    [switch]$Force,
    [switch]$Verify,
    [switch]$Uninstall
)

# Configuration
$AgentVersion = "3.0.0"
$ServiceName = "LANETAgent"
$InstallDir = "C:\Program Files\LANET Agent"
$LogDir = "C:\ProgramData\LANET Agent\Logs"
$LogFile = "$LogDir\silent_installation.log"

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $logEntry -ErrorAction SilentlyContinue
    Write-Host $logEntry
}

# Validate token function
function Test-TokenValidation {
    param([string]$Token, [string]$ServerUrl)
    
    try {
        Write-Log "Validating token with server: $ServerUrl"
        
        # Test server connectivity
        $healthUrl = $ServerUrl.Replace("/api", "") + "/api/health"
        $healthResponse = Invoke-WebRequest -Uri $healthUrl -Method GET -TimeoutSec 10 -ErrorAction Stop
        
        if ($healthResponse.StatusCode -ne 200) {
            throw "Server health check failed"
        }
        
        # Validate token
        $validateUrl = $ServerUrl + "/agents/register-with-token"
        $body = @{
            token = $Token
            hardware_info = @{
                validation_only = $true
                computer_name = $env:COMPUTERNAME
            }
        } | ConvertTo-Json -Depth 3
        
        $response = Invoke-WebRequest -Uri $validateUrl -Method POST -Body $body -ContentType "application/json" -TimeoutSec 15 -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            $responseData = $response.Content | ConvertFrom-Json
            
            if ($responseData.success -and $responseData.data) {
                Write-Log "Token validation successful - Client: $($responseData.data.client_name), Site: $($responseData.data.site_name)" "SUCCESS"
                return @{
                    Valid = $true
                    ClientName = $responseData.data.client_name
                    SiteName = $responseData.data.site_name
                }
            } else {
                throw "Invalid token response format"
            }
        } else {
            throw "Token validation failed with status $($response.StatusCode)"
        }
        
    } catch {
        Write-Log "Token validation failed: $($_.Exception.Message)" "ERROR"
        return @{ Valid = $false; Error = $_.Exception.Message }
    }
}

# Main installation function
function Install-LANETAgent {
    param([string]$Token, [string]$ServerUrl, [hashtable]$ValidationResult)
    
    try {
        Write-Log "Starting LANET Agent silent installation"
        Write-Log "Version: $AgentVersion"
        Write-Log "Token: $Token"
        Write-Log "Server: $ServerUrl"
        Write-Log "Client: $($ValidationResult.ClientName)"
        Write-Log "Site: $($ValidationResult.SiteName)"
        
        # Check administrator privileges
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
        if (-not $isAdmin) {
            throw "Administrator privileges required"
        }
        Write-Log "Administrator privileges confirmed"
        
        # Test BitLocker access
        try {
            $bitlockerVolumes = Get-BitLockerVolume -ErrorAction Stop
            $protectedCount = ($bitlockerVolumes | Where-Object { $_.ProtectionStatus -eq 'On' }).Count
            $totalCount = $bitlockerVolumes.Count
            Write-Log "BitLocker access confirmed - $protectedCount/$totalCount volumes protected"
        } catch {
            Write-Log "BitLocker access limited: $($_.Exception.Message)" "WARNING"
        }
        
        # Stop existing service
        Write-Log "Removing existing installation"
        try {
            Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
            sc.exe delete $ServiceName | Out-Null
            if (Test-Path $InstallDir) {
                Remove-Item $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
            }
        } catch {
            Write-Log "Error during cleanup: $($_.Exception.Message)" "WARNING"
        }
        
        # Create installation directories
        Write-Log "Creating installation directories"
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        New-Item -ItemType Directory -Path "$InstallDir\modules" -Force | Out-Null
        New-Item -ItemType Directory -Path "$InstallDir\core" -Force | Out-Null
        New-Item -ItemType Directory -Path "$InstallDir\config" -Force | Out-Null
        
        # Copy agent files
        Write-Log "Installing agent files"
        $scriptDir = Split-Path -Parent $PSCommandPath
        $sourceDir = Join-Path $scriptDir "..\production_installer\agent_files"
        
        if (-not (Test-Path "$sourceDir\main.py")) {
            throw "Agent source files not found at $sourceDir"
        }
        
        Copy-Item "$sourceDir\*" $InstallDir -Recurse -Force
        Write-Log "Agent files copied successfully"
        
        # Create service configuration
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
                client_name = $ValidationResult.ClientName
                site_name = $ValidationResult.SiteName
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
        Write-Log "Creating Windows service wrapper"
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
        logger.info('👤 Client: $($ValidationResult.ClientName)')
        logger.info('🏢 Site: $($ValidationResult.SiteName)')
        
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
        Write-Log "Installing Windows service"
        $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
        if (-not $pythonExe) {
            throw "Python not found in PATH. Please install Python 3.10+ and add to PATH."
        }
        
        Write-Log "Using Python: $pythonExe"
        
        $serviceCommand = "`"$pythonExe`" `"$InstallDir\service_wrapper.py`""
        $createResult = sc.exe create $ServiceName binPath= $serviceCommand obj= LocalSystem start= auto DisplayName= "LANET Helpdesk Agent"
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create Windows service (Exit code: $LASTEXITCODE)"
        }
        
        Write-Log "Windows service created successfully"
        
        # Set service description
        sc.exe description $ServiceName "LANET Helpdesk monitoring agent with BitLocker data collection (SYSTEM privileges)" | Out-Null
        
        # Start service
        Write-Log "Starting LANET Agent service"
        $startResult = sc.exe start $ServiceName
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Service start command failed (Exit code: $LASTEXITCODE)" "WARNING"
            # Try alternative start method
            Start-Sleep -Seconds 2
            try {
                Start-Service -Name $ServiceName -ErrorAction Stop
                Write-Log "Service started successfully using Start-Service"
            } catch {
                throw "Failed to start service: $($_.Exception.Message)"
            }
        } else {
            Write-Log "Service started successfully"
        }
        
        # Verify installation
        Write-Log "Verifying installation"
        Start-Sleep -Seconds 10
        
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq "Running") {
            Write-Log "Installation verification successful - Service is running" "SUCCESS"
            
            # Log final status
            Write-Log "=== INSTALLATION COMPLETED SUCCESSFULLY ===" "SUCCESS"
            Write-Log "Service Name: $ServiceName" "SUCCESS"
            Write-Log "Service Status: Running" "SUCCESS"
            Write-Log "Service Account: LocalSystem (SYSTEM privileges)" "SUCCESS"
            Write-Log "Client: $($ValidationResult.ClientName)" "SUCCESS"
            Write-Log "Site: $($ValidationResult.SiteName)" "SUCCESS"
            Write-Log "Installation Directory: $InstallDir" "SUCCESS"
            Write-Log "Log Directory: $LogDir" "SUCCESS"
            Write-Log "=========================================" "SUCCESS"
            
            return $true
        } else {
            $serviceStatus = if ($service) { $service.Status } else { "Not Found" }
            throw "Service verification failed - Status: $serviceStatus"
        }
        
    } catch {
        Write-Log "Installation failed: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Uninstall function
function Uninstall-LANETAgent {
    try {
        Write-Log "Starting LANET Agent uninstallation"
        
        # Stop and remove service
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        sc.exe delete $ServiceName | Out-Null
        
        # Remove installation directory
        if (Test-Path $InstallDir) {
            Remove-Item $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        Write-Log "Uninstallation completed successfully" "SUCCESS"
        return $true
        
    } catch {
        Write-Log "Uninstallation failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Verify function
function Test-Installation {
    try {
        Write-Log "Verifying LANET Agent installation"
        
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq "Running") {
            Write-Log "Verification successful - Service is running" "SUCCESS"
            Write-Log "Service Status: $($service.Status)" "SUCCESS"
            Write-Log "Installation Directory: $(Test-Path $InstallDir)" "SUCCESS"
            Write-Log "Log Directory: $(Test-Path $LogDir)" "SUCCESS"
            return $true
        } else {
            $serviceStatus = if ($service) { $service.Status } else { "Not Found" }
            Write-Log "Verification failed - Service status: $serviceStatus" "ERROR"
            return $false
        }
        
    } catch {
        Write-Log "Verification failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main execution
try {
    Write-Log "LANET Agent Silent Enterprise Deployment v$AgentVersion started"
    
    # Handle uninstall
    if ($Uninstall) {
        $result = Uninstall-LANETAgent
        exit $(if ($result) { 0 } else { 1 })
    }
    
    # Handle verification
    if ($Verify) {
        $result = Test-Installation
        exit $(if ($result) { 0 } else { 1 })
    }
    
    # Check if already installed and running (unless Force is specified)
    if (-not $Force) {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq "Running") {
            Write-Log "LANET Agent is already installed and running - use -Force to reinstall" "SUCCESS"
            exit 0
        }
    }
    
    # Validate token
    $validationResult = Test-TokenValidation -Token $Token -ServerUrl $ServerUrl
    if (-not $validationResult.Valid) {
        Write-Log "Token validation failed: $($validationResult.Error)" "ERROR"
        exit 1
    }
    
    # Install agent
    $installResult = Install-LANETAgent -Token $Token -ServerUrl $ServerUrl -ValidationResult $validationResult
    
    if ($installResult) {
        Write-Log "LANET Agent installation completed successfully" "SUCCESS"
        exit 0
    } else {
        Write-Log "LANET Agent installation failed" "ERROR"
        exit 1
    }
    
} catch {
    Write-Log "Fatal error: $($_.Exception.Message)" "ERROR"
    exit 1
}
