# LANET Agent Production Installer - PowerShell Launcher
# Automatically requests administrator privileges and launches the installer

Write-Host "LANET Agent Production Installer" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "This installer will:" -ForegroundColor Yellow
Write-Host "- Install LANET Agent as a Windows service" -ForegroundColor White
Write-Host "- Configure SYSTEM privileges for BitLocker access" -ForegroundColor White
Write-Host "- Enable automatic startup on system boot" -ForegroundColor White
Write-Host "- Validate installation token in real-time" -ForegroundColor White
Write-Host ""

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallerPath = Join-Path $ScriptDir "LANET_Agent_Production_Installer.py"

# Check if installer exists
if (-not (Test-Path $InstallerPath)) {
    Write-Host "ERROR: Installer not found at $InstallerPath" -ForegroundColor Red
    Write-Host "Please ensure all installer files are in the same directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    Write-Host "Running with administrator privileges..." -ForegroundColor Green
    Write-Host "Starting GUI installer..." -ForegroundColor Green
    Write-Host ""
    
    # Launch the Python installer
    try {
        & python $InstallerPath
    }
    catch {
        Write-Host "ERROR: Failed to launch installer: $_" -ForegroundColor Red
        Write-Host "Please ensure Python is installed and in your PATH." -ForegroundColor Red
    }
} else {
    Write-Host "Requesting administrator privileges..." -ForegroundColor Yellow
    Write-Host ""
    
    # Restart as administrator
    try {
        Start-Process python -ArgumentList "`"$InstallerPath`"" -Verb RunAs
    }
    catch {
        Write-Host "ERROR: Failed to request administrator privileges: $_" -ForegroundColor Red
        Write-Host "Please manually run as administrator." -ForegroundColor Red
        Read-Host "Press Enter to exit"
    }
}

Write-Host ""
Write-Host "Installer launched. Check the GUI window for installation progress." -ForegroundColor Green
