# ========================================================================
# LANET HELPDESK AGENT - PROFESSIONAL ENTERPRISE INSTALLER
# Version: 3.0.0 Enterprise
# Purpose: GUI-based installer with token validation and automatic service deployment
# Comparable to: NinjaOne, GLPI, Zabbix enterprise installers
# ========================================================================

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Global variables
$global:ValidatedToken = $null
$global:ClientInfo = $null
$global:SiteInfo = $null
$global:ServerUrl = $null

# Configuration
$AgentVersion = "3.0.0"
$ServiceName = "LANETAgent"
$InstallDir = "C:\Program Files\LANET Agent"
$LogDir = "C:\ProgramData\LANET Agent\Logs"

# Create main form
function Create-MainForm {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "LANET Helpdesk Agent - Enterprise Installer v$AgentVersion"
    $form.Size = New-Object System.Drawing.Size(600, 500)
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false
    $form.Icon = [System.Drawing.SystemIcons]::Shield
    
    # Header
    $headerLabel = New-Object System.Windows.Forms.Label
    $headerLabel.Text = "LANET Helpdesk Agent Professional Installer"
    $headerLabel.Font = New-Object System.Drawing.Font("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
    $headerLabel.ForeColor = [System.Drawing.Color]::DarkBlue
    $headerLabel.Location = New-Object System.Drawing.Point(20, 20)
    $headerLabel.Size = New-Object System.Drawing.Size(550, 30)
    $headerLabel.TextAlign = "MiddleCenter"
    $form.Controls.Add($headerLabel)
    
    # Description
    $descLabel = New-Object System.Windows.Forms.Label
    $descLabel.Text = "This installer will deploy the LANET agent as a Windows service with SYSTEM privileges for complete system monitoring including BitLocker data collection."
    $descLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $descLabel.Location = New-Object System.Drawing.Point(20, 60)
    $descLabel.Size = New-Object System.Drawing.Size(550, 40)
    $form.Controls.Add($descLabel)
    
    # Server URL section
    $serverLabel = New-Object System.Windows.Forms.Label
    $serverLabel.Text = "Helpdesk Server URL:"
    $serverLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $serverLabel.Location = New-Object System.Drawing.Point(20, 120)
    $serverLabel.Size = New-Object System.Drawing.Size(200, 25)
    $form.Controls.Add($serverLabel)
    
    $global:serverTextBox = New-Object System.Windows.Forms.TextBox
    $global:serverTextBox.Text = "http://localhost:5001/api"
    $global:serverTextBox.Font = New-Object System.Drawing.Font("Segoe UI", 10)
    $global:serverTextBox.Location = New-Object System.Drawing.Point(20, 145)
    $global:serverTextBox.Size = New-Object System.Drawing.Size(450, 25)
    $form.Controls.Add($global:serverTextBox)
    
    # Token section
    $tokenLabel = New-Object System.Windows.Forms.Label
    $tokenLabel.Text = "Installation Token:"
    $tokenLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $tokenLabel.Location = New-Object System.Drawing.Point(20, 185)
    $tokenLabel.Size = New-Object System.Drawing.Size(200, 25)
    $form.Controls.Add($tokenLabel)
    
    $global:tokenTextBox = New-Object System.Windows.Forms.TextBox
    $global:tokenTextBox.Text = "LANET-75F6-EC23-85DC9D"
    $global:tokenTextBox.Font = New-Object System.Drawing.Font("Segoe UI", 10)
    $global:tokenTextBox.Location = New-Object System.Drawing.Point(20, 210)
    $global:tokenTextBox.Size = New-Object System.Drawing.Size(350, 25)
    $form.Controls.Add($global:tokenTextBox)
    
    # Validate button
    $validateButton = New-Object System.Windows.Forms.Button
    $validateButton.Text = "Validate Token"
    $validateButton.Font = New-Object System.Drawing.Font("Segoe UI", 10)
    $validateButton.Location = New-Object System.Drawing.Point(380, 208)
    $validateButton.Size = New-Object System.Drawing.Size(120, 30)
    $validateButton.BackColor = [System.Drawing.Color]::LightBlue
    $validateButton.Add_Click({ Validate-Token })
    $form.Controls.Add($validateButton)
    
    # Validation result section
    $global:validationLabel = New-Object System.Windows.Forms.Label
    $global:validationLabel.Text = "Please validate your token to continue"
    $global:validationLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $global:validationLabel.ForeColor = [System.Drawing.Color]::Gray
    $global:validationLabel.Location = New-Object System.Drawing.Point(20, 250)
    $global:validationLabel.Size = New-Object System.Drawing.Size(550, 60)
    $form.Controls.Add($global:validationLabel)
    
    # Progress bar
    $global:progressBar = New-Object System.Windows.Forms.ProgressBar
    $global:progressBar.Location = New-Object System.Drawing.Point(20, 320)
    $global:progressBar.Size = New-Object System.Drawing.Size(550, 25)
    $global:progressBar.Visible = $false
    $form.Controls.Add($global:progressBar)
    
    # Status label
    $global:statusLabel = New-Object System.Windows.Forms.Label
    $global:statusLabel.Text = ""
    $global:statusLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $global:statusLabel.Location = New-Object System.Drawing.Point(20, 355)
    $global:statusLabel.Size = New-Object System.Drawing.Size(550, 25)
    $form.Controls.Add($global:statusLabel)
    
    # Install button
    $global:installButton = New-Object System.Windows.Forms.Button
    $global:installButton.Text = "Install LANET Agent Service"
    $global:installButton.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
    $global:installButton.Location = New-Object System.Drawing.Point(150, 400)
    $global:installButton.Size = New-Object System.Drawing.Size(300, 40)
    $global:installButton.BackColor = [System.Drawing.Color]::Green
    $global:installButton.ForeColor = [System.Drawing.Color]::White
    $global:installButton.Enabled = $false
    $global:installButton.Add_Click({ Start-Installation })
    $form.Controls.Add($global:installButton)
    
    # Close button
    $closeButton = New-Object System.Windows.Forms.Button
    $closeButton.Text = "Close"
    $closeButton.Font = New-Object System.Drawing.Font("Segoe UI", 10)
    $closeButton.Location = New-Object System.Drawing.Point(500, 400)
    $closeButton.Size = New-Object System.Drawing.Size(70, 40)
    $closeButton.Add_Click({ $form.Close() })
    $form.Controls.Add($closeButton)
    
    return $form
}

# Token validation function
function Validate-Token {
    $token = $global:tokenTextBox.Text.Trim()
    $serverUrl = $global:serverTextBox.Text.Trim()
    
    if ([string]::IsNullOrEmpty($token) -or [string]::IsNullOrEmpty($serverUrl)) {
        $global:validationLabel.Text = "❌ Please enter both server URL and token"
        $global:validationLabel.ForeColor = [System.Drawing.Color]::Red
        return
    }
    
    $global:validationLabel.Text = "🔍 Validating token with server..."
    $global:validationLabel.ForeColor = [System.Drawing.Color]::Blue
    $global:validationLabel.Refresh()
    
    try {
        # Test server connectivity first
        $healthUrl = $serverUrl.Replace("/api", "") + "/api/health"
        $healthResponse = Invoke-WebRequest -Uri $healthUrl -Method GET -TimeoutSec 10 -ErrorAction Stop
        
        if ($healthResponse.StatusCode -ne 200) {
            throw "Server health check failed"
        }
        
        # Validate token
        $validateUrl = $serverUrl + "/agents/register-with-token"
        $body = @{
            token = $token
            hardware_info = @{
                validation_only = $true
                computer_name = $env:COMPUTERNAME
            }
        } | ConvertTo-Json -Depth 3
        
        $response = Invoke-WebRequest -Uri $validateUrl -Method POST -Body $body -ContentType "application/json" -TimeoutSec 15 -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            $responseData = $response.Content | ConvertFrom-Json
            
            if ($responseData.success -and $responseData.data) {
                $global:ValidatedToken = $token
                $global:ServerUrl = $serverUrl
                $global:ClientInfo = $responseData.data.client_name
                $global:SiteInfo = $responseData.data.site_name
                
                $global:validationLabel.Text = "✅ Token validated successfully!`nClient: $($global:ClientInfo)`nSite: $($global:SiteInfo)"
                $global:validationLabel.ForeColor = [System.Drawing.Color]::Green
                $global:installButton.Enabled = $true
                $global:installButton.BackColor = [System.Drawing.Color]::DarkGreen
            } else {
                throw "Invalid token response format"
            }
        } else {
            throw "Token validation failed with status $($response.StatusCode)"
        }
        
    } catch {
        $errorMessage = $_.Exception.Message
        if ($errorMessage -like "*timeout*") {
            $global:validationLabel.Text = "❌ Connection timeout - check server URL and network connectivity"
        } elseif ($errorMessage -like "*404*") {
            $global:validationLabel.Text = "❌ Server endpoint not found - verify server URL"
        } elseif ($errorMessage -like "*401*" -or $errorMessage -like "*403*") {
            $global:validationLabel.Text = "❌ Invalid token - please check your installation token"
        } else {
            $global:validationLabel.Text = "❌ Validation failed: $errorMessage"
        }
        $global:validationLabel.ForeColor = [System.Drawing.Color]::Red
        $global:installButton.Enabled = $false
        $global:installButton.BackColor = [System.Drawing.Color]::Gray
    }
}

# Installation function
function Start-Installation {
    $global:progressBar.Visible = $true
    $global:progressBar.Value = 0
    $global:installButton.Enabled = $false
    $global:statusLabel.Text = "Starting installation..."
    
    try {
        # Step 1: Check privileges
        Update-Progress 10 "Checking administrator privileges..."
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
        if (-not $isAdmin) {
            throw "Administrator privileges required. Please run as administrator."
        }
        
        # Step 2: Test BitLocker access
        Update-Progress 20 "Testing BitLocker access..."
        try {
            $bitlockerVolumes = Get-BitLockerVolume -ErrorAction Stop
            $protectedCount = ($bitlockerVolumes | Where-Object { $_.ProtectionStatus -eq 'On' }).Count
            Update-Progress 25 "BitLocker access confirmed - $protectedCount protected volumes found"
        } catch {
            Update-Progress 25 "BitLocker access limited - continuing installation"
        }
        
        # Step 3: Stop existing service
        Update-Progress 30 "Removing existing installation..."
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        sc.exe delete $ServiceName | Out-Null
        if (Test-Path $InstallDir) {
            Remove-Item $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        # Step 4: Create directories
        Update-Progress 40 "Creating installation directories..."
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        New-Item -ItemType Directory -Path "$InstallDir\modules" -Force | Out-Null
        New-Item -ItemType Directory -Path "$InstallDir\core" -Force | Out-Null
        New-Item -ItemType Directory -Path "$InstallDir\config" -Force | Out-Null
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
        
        # Step 5: Copy agent files
        Update-Progress 50 "Installing agent files..."
        $scriptDir = Split-Path -Parent $PSCommandPath
        $sourceDir = Join-Path $scriptDir "..\production_installer\agent_files"
        
        if (-not (Test-Path "$sourceDir\main.py")) {
            throw "Agent source files not found at $sourceDir"
        }
        
        Copy-Item "$sourceDir\*" $InstallDir -Recurse -Force
        
        # Step 6: Create service configuration
        Update-Progress 60 "Creating service configuration..."
        $config = @{
            server = @{
                url = $global:ServerUrl
                heartbeat_interval = 300
                inventory_interval = 3600
                metrics_interval = 300
            }
            agent = @{
                name = "LANET Helpdesk Agent"
                version = $AgentVersion
                installation_token = $global:ValidatedToken
                log_level = "INFO"
                client_name = $global:ClientInfo
                site_name = $global:SiteInfo
            }
            service = @{
                name = $ServiceName
                display_name = "LANET Helpdesk Agent"
                description = "LANET Helpdesk monitoring agent with BitLocker support"
                start_type = "auto"
            }
        }
        
        $config | ConvertTo-Json -Depth 3 | Out-File "$InstallDir\config\agent_config.json" -Encoding UTF8
        
        # Step 7: Create service wrapper
        Update-Progress 70 "Creating Windows service..."
        Create-ServiceWrapper
        
        # Step 8: Install service
        Update-Progress 80 "Installing Windows service..."
        $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
        if (-not $pythonExe) {
            throw "Python not found in PATH. Please install Python 3.10+ and add to PATH."
        }
        
        $serviceCommand = "`"$pythonExe`" `"$InstallDir\service_wrapper.py`""
        $createResult = sc.exe create $ServiceName binPath= $serviceCommand obj= LocalSystem start= auto DisplayName= "LANET Helpdesk Agent"
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create Windows service"
        }
        
        sc.exe description $ServiceName "LANET Helpdesk monitoring agent with BitLocker data collection (SYSTEM privileges)" | Out-Null
        
        # Step 9: Start service
        Update-Progress 90 "Starting service..."
        $startResult = sc.exe start $ServiceName
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to start service"
        }
        
        # Step 10: Verify installation
        Update-Progress 95 "Verifying installation..."
        Start-Sleep -Seconds 5
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if (-not $service -or $service.Status -ne "Running") {
            throw "Service verification failed"
        }
        
        Update-Progress 100 "Installation completed successfully!"
        
        # Show success message
        $successMessage = @"
✅ LANET Agent installed successfully!

Service Details:
• Name: $ServiceName
• Status: Running
• Privileges: SYSTEM (BitLocker enabled)
• Client: $($global:ClientInfo)
• Site: $($global:SiteInfo)

The agent will automatically:
• Register with the helpdesk system
• Collect hardware and software inventory
• Collect BitLocker recovery keys
• Send regular heartbeats

Installation completed successfully!
"@
        
        [System.Windows.Forms.MessageBox]::Show($successMessage, "Installation Successful", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
        
    } catch {
        $global:statusLabel.Text = "❌ Installation failed: $($_.Exception.Message)"
        $global:statusLabel.ForeColor = [System.Drawing.Color]::Red
        [System.Windows.Forms.MessageBox]::Show("Installation failed: $($_.Exception.Message)", "Installation Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        $global:installButton.Enabled = $true
    }
    
    $global:progressBar.Visible = $false
}

# Helper functions
function Update-Progress($value, $status) {
    $global:progressBar.Value = $value
    $global:statusLabel.Text = $status
    $global:statusLabel.ForeColor = [System.Drawing.Color]::Blue
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 500
}

function Create-ServiceWrapper {
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
        logger.info('👤 Client: $($global:ClientInfo)')
        logger.info('🏢 Site: $($global:SiteInfo)')
        
        # Change to agent directory
        os.chdir(str(agent_dir))
        
        # Import and run agent
        from main import main as agent_main
        
        # Set registration token
        sys.argv = ['main.py', '--register', '$($global:ValidatedToken)']
        
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
}

# Main execution
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    [System.Windows.Forms.MessageBox]::Show("This installer must be run as Administrator.`n`nPlease right-click and select 'Run as administrator'", "Administrator Required", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
    exit 1
}

# Create and show the form
$form = Create-MainForm
[System.Windows.Forms.Application]::Run($form)
