# ========================================================================
# LANET HELPDESK AGENT - MASS DEPLOYMENT SCRIPT
# Version: 3.0.0 Enterprise
# Purpose: Deploy to multiple computers via PowerShell remoting, Group Policy, or SCCM
# Usage: Configure variables below and run as administrator
# ========================================================================

# DEPLOYMENT CONFIGURATION - MODIFY THESE VALUES
$DeploymentConfig = @{
    # Server configuration
    ServerUrl = "http://localhost:5001/api"  # Change to your helpdesk server URL
    
    # Default token (can be overridden per computer)
    DefaultToken = "LANET-75F6-EC23-85DC9D"  # Change to your deployment token
    
    # Deployment options
    MaxConcurrentJobs = 10
    TimeoutMinutes = 15
    RetryAttempts = 2
    
    # Logging
    LogDirectory = "C:\Temp\LANET_Deployment_Logs"
    
    # Computer list (modify as needed)
    TargetComputers = @(
        # Add your target computers here
        # Examples:
        # "COMPUTER01",
        # "COMPUTER02",
        # "192.168.1.100"
    )
    
    # Computer-specific tokens (optional)
    ComputerTokens = @{
        # Override tokens for specific computers if needed
        # "COMPUTER01" = "LANET-CLIENT1-SITE1-TOKEN"
        # "COMPUTER02" = "LANET-CLIENT2-SITE2-TOKEN"
    }
}

# Create log directory
if (-not (Test-Path $DeploymentConfig.LogDirectory)) {
    New-Item -ItemType Directory -Path $DeploymentConfig.LogDirectory -Force | Out-Null
}

$MasterLogFile = Join-Path $DeploymentConfig.LogDirectory "mass_deployment_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Logging function
function Write-DeploymentLog {
    param([string]$Message, [string]$Level = "INFO", [string]$Computer = "MASTER")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Computer] [$Level] $Message"
    Add-Content -Path $MasterLogFile -Value $logEntry
    
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host $logEntry -ForegroundColor $color
}

# Deploy to single computer function
function Deploy-ToComputer {
    param(
        [string]$ComputerName,
        [string]$Token,
        [string]$ServerUrl
    )
    
    $computerLogFile = Join-Path $DeploymentConfig.LogDirectory "deployment_$ComputerName.log"
    
    try {
        Write-DeploymentLog "Starting deployment to $ComputerName" "INFO" $ComputerName
        
        # Test connectivity
        if (-not (Test-Connection -ComputerName $ComputerName -Count 1 -Quiet)) {
            throw "Computer not reachable"
        }
        
        # Get script path
        $scriptPath = Join-Path $PSScriptRoot "LANET_Agent_Silent_Enterprise.ps1"
        if (-not (Test-Path $scriptPath)) {
            throw "Silent installer script not found: $scriptPath"
        }
        
        # Execute remote installation
        $scriptBlock = {
            param($Token, $ServerUrl, $ScriptContent)
            
            # Create temporary script file
            $tempScript = "$env:TEMP\LANET_Silent_Install.ps1"
            $ScriptContent | Out-File -FilePath $tempScript -Encoding UTF8
            
            # Execute installation
            try {
                & PowerShell -ExecutionPolicy Bypass -File $tempScript -Token $Token -ServerUrl $ServerUrl
                return @{ Success = $true; ExitCode = $LASTEXITCODE; Error = $null }
            } catch {
                return @{ Success = $false; ExitCode = -1; Error = $_.Exception.Message }
            } finally {
                # Cleanup
                Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
            }
        }
        
        # Read script content
        $scriptContent = Get-Content $scriptPath -Raw
        
        # Execute on remote computer
        $result = Invoke-Command -ComputerName $ComputerName -ScriptBlock $scriptBlock -ArgumentList $Token, $ServerUrl, $scriptContent -ErrorAction Stop
        
        if ($result.Success -and $result.ExitCode -eq 0) {
            Write-DeploymentLog "Deployment successful" "SUCCESS" $ComputerName
            return @{ Success = $true; Computer = $ComputerName; Error = $null }
        } else {
            $errorMsg = if ($result.Error) { $result.Error } else { "Exit code: $($result.ExitCode)" }
            throw "Installation failed: $errorMsg"
        }
        
    } catch {
        $errorMessage = $_.Exception.Message
        Write-DeploymentLog "Deployment failed: $errorMessage" "ERROR" $ComputerName
        return @{ Success = $false; Computer = $ComputerName; Error = $errorMessage }
    }
}

# Verify deployment function
function Test-Deployment {
    param([string]$ComputerName)
    
    try {
        $result = Invoke-Command -ComputerName $ComputerName -ScriptBlock {
            $service = Get-Service -Name "LANETAgent" -ErrorAction SilentlyContinue
            if ($service -and $service.Status -eq "Running") {
                return @{ Installed = $true; Status = $service.Status }
            } else {
                return @{ Installed = $false; Status = "Not Found" }
            }
        } -ErrorAction Stop
        
        return $result
        
    } catch {
        return @{ Installed = $false; Status = "Connection Failed"; Error = $_.Exception.Message }
    }
}

# Main deployment function
function Start-MassDeployment {
    Write-DeploymentLog "Starting LANET Agent mass deployment"
    Write-DeploymentLog "Target computers: $($DeploymentConfig.TargetComputers.Count)"
    Write-DeploymentLog "Server URL: $($DeploymentConfig.ServerUrl)"
    Write-DeploymentLog "Max concurrent jobs: $($DeploymentConfig.MaxConcurrentJobs)"
    
    if ($DeploymentConfig.TargetComputers.Count -eq 0) {
        Write-DeploymentLog "No target computers specified. Please update the TargetComputers array in the configuration." "ERROR"
        return
    }
    
    $jobs = @()
    $results = @()
    
    # Start deployment jobs
    foreach ($computer in $DeploymentConfig.TargetComputers) {
        # Get token for this computer
        $token = if ($DeploymentConfig.ComputerTokens.ContainsKey($computer)) {
            $DeploymentConfig.ComputerTokens[$computer]
        } else {
            $DeploymentConfig.DefaultToken
        }
        
        # Wait if we've reached max concurrent jobs
        while ((Get-Job -State Running).Count -ge $DeploymentConfig.MaxConcurrentJobs) {
            Start-Sleep -Seconds 5
        }
        
        # Start deployment job
        $job = Start-Job -ScriptBlock ${function:Deploy-ToComputer} -ArgumentList $computer, $token, $DeploymentConfig.ServerUrl
        $jobs += @{ Job = $job; Computer = $computer; StartTime = Get-Date }
        
        Write-DeploymentLog "Started deployment job for $computer" "INFO"
    }
    
    # Wait for all jobs to complete
    Write-DeploymentLog "Waiting for deployment jobs to complete..."
    
    while ($jobs | Where-Object { $_.Job.State -eq "Running" }) {
        Start-Sleep -Seconds 10
        
        # Check for completed jobs
        $completedJobs = $jobs | Where-Object { $_.Job.State -ne "Running" }
        foreach ($completedJob in $completedJobs) {
            if ($completedJob.Job.State -eq "Completed") {
                $result = Receive-Job -Job $completedJob.Job
                $results += $result
                
                if ($result.Success) {
                    Write-DeploymentLog "Deployment completed successfully" "SUCCESS" $completedJob.Computer
                } else {
                    Write-DeploymentLog "Deployment failed: $($result.Error)" "ERROR" $completedJob.Computer
                }
            } else {
                Write-DeploymentLog "Deployment job failed with state: $($completedJob.Job.State)" "ERROR" $completedJob.Computer
                $results += @{ Success = $false; Computer = $completedJob.Computer; Error = "Job failed" }
            }
            
            Remove-Job -Job $completedJob.Job -Force
        }
        
        # Remove completed jobs from tracking
        $jobs = $jobs | Where-Object { $_.Job.State -eq "Running" }
    }
    
    # Generate deployment report
    Write-DeploymentLog "=== DEPLOYMENT SUMMARY ==="
    $successCount = ($results | Where-Object { $_.Success }).Count
    $failureCount = ($results | Where-Object { -not $_.Success }).Count
    
    Write-DeploymentLog "Total computers: $($DeploymentConfig.TargetComputers.Count)"
    Write-DeploymentLog "Successful deployments: $successCount" "SUCCESS"
    Write-DeploymentLog "Failed deployments: $failureCount" $(if ($failureCount -gt 0) { "ERROR" } else { "INFO" })
    
    if ($failureCount -gt 0) {
        Write-DeploymentLog "Failed computers:"
        $results | Where-Object { -not $_.Success } | ForEach-Object {
            Write-DeploymentLog "  - $($_.Computer): $($_.Error)" "ERROR"
        }
    }
    
    Write-DeploymentLog "Deployment logs saved to: $($DeploymentConfig.LogDirectory)"
    Write-DeploymentLog "=== DEPLOYMENT COMPLETE ==="
    
    return $results
}

# Verification function
function Start-DeploymentVerification {
    Write-DeploymentLog "Starting deployment verification"
    
    $verificationResults = @()
    
    foreach ($computer in $DeploymentConfig.TargetComputers) {
        Write-DeploymentLog "Verifying $computer..." "INFO" $computer
        
        $result = Test-Deployment -ComputerName $computer
        $verificationResults += @{
            Computer = $computer
            Installed = $result.Installed
            Status = $result.Status
            Error = $result.Error
        }
        
        if ($result.Installed) {
            Write-DeploymentLog "Verification successful - Service running" "SUCCESS" $computer
        } else {
            Write-DeploymentLog "Verification failed - Status: $($result.Status)" "ERROR" $computer
        }
    }
    
    # Verification summary
    Write-DeploymentLog "=== VERIFICATION SUMMARY ==="
    $installedCount = ($verificationResults | Where-Object { $_.Installed }).Count
    $notInstalledCount = ($verificationResults | Where-Object { -not $_.Installed }).Count
    
    Write-DeploymentLog "Total computers: $($DeploymentConfig.TargetComputers.Count)"
    Write-DeploymentLog "Successfully installed: $installedCount" "SUCCESS"
    Write-DeploymentLog "Not installed: $notInstalledCount" $(if ($notInstalledCount -gt 0) { "ERROR" } else { "INFO" })
    
    return $verificationResults
}

# Main execution
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "LANET HELPDESK AGENT - MASS DEPLOYMENT TOOL" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Check administrator privileges
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Show configuration
Write-Host "Deployment Configuration:" -ForegroundColor Yellow
Write-Host "- Server URL: $($DeploymentConfig.ServerUrl)" -ForegroundColor White
Write-Host "- Default Token: $($DeploymentConfig.DefaultToken)" -ForegroundColor White
Write-Host "- Target Computers: $($DeploymentConfig.TargetComputers.Count)" -ForegroundColor White
Write-Host "- Log Directory: $($DeploymentConfig.LogDirectory)" -ForegroundColor White
Write-Host ""

# Menu
do {
    Write-Host "Select an option:" -ForegroundColor Yellow
    Write-Host "1. Start Mass Deployment" -ForegroundColor White
    Write-Host "2. Verify Existing Deployments" -ForegroundColor White
    Write-Host "3. View Configuration" -ForegroundColor White
    Write-Host "4. Exit" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Enter your choice (1-4)"
    
    switch ($choice) {
        "1" {
            Write-Host ""
            $results = Start-MassDeployment
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "2" {
            Write-Host ""
            $verificationResults = Start-DeploymentVerification
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "3" {
            Write-Host ""
            Write-Host "Current Configuration:" -ForegroundColor Cyan
            $DeploymentConfig | ConvertTo-Json -Depth 2 | Write-Host -ForegroundColor White
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "4" {
            Write-Host "Exiting..." -ForegroundColor Green
            break
        }
        default {
            Write-Host "Invalid choice. Please select 1-4." -ForegroundColor Red
        }
    }
    
    Write-Host ""
    
} while ($choice -ne "4")
