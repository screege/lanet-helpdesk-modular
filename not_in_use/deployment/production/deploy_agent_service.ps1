# LANET Agent Production Deployment Script
# Deploys LANET Agent as Windows Service with SYSTEM privileges for BitLocker access
# Suitable for mass deployment across 2000+ client computers via GPO, SCCM, or RMM tools

param(
    [Parameter(Mandatory=$true)]
    [string]$InstallationToken,
    
    [Parameter(Mandatory=$false)]
    [string]$ServerUrl = "https://helpdesk.lanet.mx/api",
    
    [Parameter(Mandatory=$false)]
    [string]$InstallPath = "C:\Program Files\LANET Agent",
    
    [Parameter(Mandatory=$false)]
    [switch]$Silent = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false
)

# Script configuration
$ErrorActionPreference = "Stop"
$ServiceName = "LANETAgent"
$ServiceDisplayName = "LANET Helpdesk Agent"
$LogFile = "$env:TEMP\lanet_agent_deploy.log"

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    
    if (-not $Silent) {
        switch ($Level) {
            "ERROR" { Write-Host $LogEntry -ForegroundColor Red }
            "WARN"  { Write-Host $LogEntry -ForegroundColor Yellow }
            "SUCCESS" { Write-Host $LogEntry -ForegroundColor Green }
            default { Write-Host $LogEntry }
        }
    }
    
    Add-Content -Path $LogFile -Value $LogEntry
}

# Check administrator privileges
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Download agent files
function Download-AgentFiles {
    param([string]$DestinationPath)
    
    Write-Log "Downloading LANET Agent files..."
    
    try {
        # Create destination directory
        if (-not (Test-Path $DestinationPath)) {
            New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
            Write-Log "Created directory: $DestinationPath"
        }
        
        # Download agent package (this would be from your distribution server)
        $AgentPackageUrl = "$ServerUrl/downloads/lanet-agent-windows.zip"
        $PackagePath = "$env:TEMP\lanet-agent-windows.zip"
        
        Write-Log "Downloading from: $AgentPackageUrl"
        
        # For now, we'll copy from local source since we don't have a distribution server
        # In production, this would download from your server
        $SourcePath = Split-Path -Parent $PSScriptRoot
        $SourcePath = Join-Path $SourcePath "lanet_agent"
        
        if (Test-Path $SourcePath) {
            Write-Log "Copying agent files from local source: $SourcePath"
            Copy-Item -Path "$SourcePath\*" -Destination $DestinationPath -Recurse -Force
            Write-Log "Agent files copied successfully" "SUCCESS"
        } else {
            throw "Source agent files not found at: $SourcePath"
        }
        
        return $true
    }
    catch {
        Write-Log "Failed to download agent files: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Install Python dependencies
function Install-Dependencies {
    param([string]$InstallPath)
    
    Write-Log "Installing Python dependencies..."
    
    try {
        # Check if Python is available
        $PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
        if (-not $PythonPath) {
            throw "Python not found. Please install Python 3.8+ first."
        }
        
        Write-Log "Found Python at: $PythonPath"
        
        # Install required packages
        $RequiredPackages = @("pywin32", "psutil", "requests", "wmi")
        
        foreach ($Package in $RequiredPackages) {
            Write-Log "Installing $Package..."
            $Result = & python -m pip install $Package 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Log "Successfully installed $Package" "SUCCESS"
            } else {
                throw "Failed to install $Package`: $Result"
            }
        }
        
        return $true
    }
    catch {
        Write-Log "Failed to install dependencies: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Create agent configuration
function Create-AgentConfiguration {
    param([string]$InstallPath, [string]$Token)
    
    Write-Log "Creating agent configuration..."
    
    try {
        $ConfigDir = Join-Path $InstallPath "config"
        if (-not (Test-Path $ConfigDir)) {
            New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
        }
        
        $ConfigFile = Join-Path $ConfigDir "agent_config.json"
        
        $Config = @{
            server = @{
                url = $ServerUrl
                timeout = 30
                retry_attempts = 3
            }
            agent = @{
                name = $env:COMPUTERNAME
                version = "3.0"
                log_level = "INFO"
                heartbeat_interval = 300
                inventory_interval = 3600
            }
            registration = @{
                installation_token = $Token
                auto_register = $true
            }
            bitlocker = @{
                enabled = $true
                collection_interval = 3600
                require_admin_privileges = $false
            }
            service = @{
                name = $ServiceName
                display_name = $ServiceDisplayName
                account = "LocalSystem"
                start_type = "auto"
                restart_on_failure = $true
            }
        } | ConvertTo-Json -Depth 3
        
        Set-Content -Path $ConfigFile -Value $Config -Encoding UTF8
        Write-Log "Configuration created: $ConfigFile" "SUCCESS"
        
        return $true
    }
    catch {
        Write-Log "Failed to create configuration: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Install Windows Service
function Install-WindowsService {
    param([string]$InstallPath)
    
    Write-Log "Installing Windows service..."
    
    try {
        # Check if service already exists
        $ExistingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($ExistingService) {
            if ($Force) {
                Write-Log "Service exists, removing..." "WARN"
                Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
                & sc.exe delete $ServiceName
                Start-Sleep -Seconds 2
            } else {
                throw "Service '$ServiceName' already exists. Use -Force to overwrite."
            }
        }
        
        # Install service using Python script
        $ServiceScript = Join-Path $InstallPath "service\windows_service.py"
        if (-not (Test-Path $ServiceScript)) {
            throw "Service script not found: $ServiceScript"
        }
        
        Write-Log "Installing service with script: $ServiceScript"
        $Result = & python $ServiceScript install 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Service installed successfully" "SUCCESS"
        } else {
            throw "Service installation failed: $Result"
        }
        
        # Configure service to run as LocalSystem
        Write-Log "Configuring service account..."
        & sc.exe config $ServiceName obj= LocalSystem start= auto
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Service configured to run as LocalSystem" "SUCCESS"
        } else {
            Write-Log "Warning: Could not configure service account" "WARN"
        }
        
        # Set service description
        & sc.exe description $ServiceName "LANET Helpdesk MSP Agent - Collects system information and BitLocker data with SYSTEM privileges"
        
        return $true
    }
    catch {
        Write-Log "Failed to install Windows service: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Test BitLocker access
function Test-BitLockerAccess {
    Write-Log "Testing BitLocker access..."
    
    try {
        $BitLockerVolumes = Get-BitLockerVolume -ErrorAction SilentlyContinue
        if ($BitLockerVolumes) {
            Write-Log "BitLocker access test successful - found $($BitLockerVolumes.Count) volumes" "SUCCESS"
            foreach ($Volume in $BitLockerVolumes) {
                Write-Log "  Volume $($Volume.MountPoint): $($Volume.ProtectionStatus)"
            }
            return $true
        } else {
            Write-Log "No BitLocker volumes found or access denied" "WARN"
            return $false
        }
    }
    catch {
        Write-Log "BitLocker access test failed: $($_.Exception.Message)" "WARN"
        return $false
    }
}

# Register agent with server
function Register-Agent {
    param([string]$InstallPath, [string]$Token)
    
    Write-Log "Registering agent with server..."
    
    try {
        $MainScript = Join-Path $InstallPath "main.py"
        if (-not (Test-Path $MainScript)) {
            throw "Main script not found: $MainScript"
        }
        
        Write-Log "Running registration with token: $Token"
        $Result = & python $MainScript --register $Token 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Agent registered successfully" "SUCCESS"
            return $true
        } else {
            Write-Log "Agent registration failed: $Result" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Failed to register agent: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main deployment function
function Deploy-LANETAgent {
    Write-Log "Starting LANET Agent deployment..." "SUCCESS"
    Write-Log "Installation Token: $InstallationToken"
    Write-Log "Server URL: $ServerUrl"
    Write-Log "Install Path: $InstallPath"
    
    # Check prerequisites
    if (-not (Test-Administrator)) {
        Write-Log "Administrator privileges required for deployment" "ERROR"
        return $false
    }
    
    # Deployment steps
    $Steps = @(
        @{ Name = "Download Agent Files"; Function = { Download-AgentFiles -DestinationPath $InstallPath } },
        @{ Name = "Install Dependencies"; Function = { Install-Dependencies -InstallPath $InstallPath } },
        @{ Name = "Create Configuration"; Function = { Create-AgentConfiguration -InstallPath $InstallPath -Token $InstallationToken } },
        @{ Name = "Install Windows Service"; Function = { Install-WindowsService -InstallPath $InstallPath } },
        @{ Name = "Test BitLocker Access"; Function = { Test-BitLockerAccess } },
        @{ Name = "Register Agent"; Function = { Register-Agent -InstallPath $InstallPath -Token $InstallationToken } }
    )
    
    foreach ($Step in $Steps) {
        Write-Log "Executing: $($Step.Name)..."
        $Result = & $Step.Function
        
        if (-not $Result) {
            Write-Log "Deployment failed at step: $($Step.Name)" "ERROR"
            return $false
        }
    }
    
    # Start the service
    Write-Log "Starting LANET Agent service..."
    try {
        Start-Service -Name $ServiceName
        Write-Log "Service started successfully" "SUCCESS"
    }
    catch {
        Write-Log "Failed to start service: $($_.Exception.Message)" "ERROR"
        return $false
    }
    
    Write-Log "LANET Agent deployment completed successfully!" "SUCCESS"
    return $true
}

# Script execution
try {
    Write-Log "LANET Agent Production Deployment Script" "SUCCESS"
    Write-Log "=========================================" "SUCCESS"
    
    $Success = Deploy-LANETAgent
    
    if ($Success) {
        Write-Log "Deployment Summary:" "SUCCESS"
        Write-Log "  Service Name: $ServiceName"
        Write-Log "  Install Path: $InstallPath"
        Write-Log "  Service Account: LocalSystem (SYSTEM privileges)"
        Write-Log "  BitLocker Access: Enabled"
        Write-Log "  Auto Start: Enabled"
        Write-Log "  Log File: $LogFile"
        
        if (-not $Silent) {
            Write-Host "`n✅ LANET Agent deployed successfully!" -ForegroundColor Green
            Write-Host "🔧 Service Management Commands:" -ForegroundColor Cyan
            Write-Host "   Start:   sc start $ServiceName" -ForegroundColor White
            Write-Host "   Stop:    sc stop $ServiceName" -ForegroundColor White
            Write-Host "   Status:  sc query $ServiceName" -ForegroundColor White
            Write-Host "   Logs:    $InstallPath\logs\" -ForegroundColor White
        }
        
        exit 0
    } else {
        Write-Log "Deployment failed. Check log file: $LogFile" "ERROR"
        exit 1
    }
}
catch {
    Write-Log "Deployment script failed: $($_.Exception.Message)" "ERROR"
    exit 1
}
