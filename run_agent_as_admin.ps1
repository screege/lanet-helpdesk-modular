# Run LANET Agent with Administrator Privileges for BitLocker Access
Write-Host "🔐 LANET Agent - Administrator Mode for BitLocker Collection" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator for BitLocker access!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Test BitLocker access first
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
    Write-Host ""
} catch {
    Write-Host "❌ BitLocker access failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "The agent will not be able to collect BitLocker data." -ForegroundColor Yellow
    Write-Host ""
}

# Change to agent directory
Set-Location "C:\lanet-helpdesk-v3\production_installer\agent_files"

Write-Host "🚀 Starting LANET Agent with BitLocker support..." -ForegroundColor Green
Write-Host "Token: LANET-75F6-EC23-85DC9D" -ForegroundColor Cyan
Write-Host ""
Write-Host "Expected results:" -ForegroundColor Yellow
Write-Host "- BitLocker collection should show: $protectedCount/$totalCount volumes protected" -ForegroundColor White
Write-Host "- Hardware and software inventory should be collected" -ForegroundColor White
Write-Host "- Heartbeat should be sent successfully (status 200)" -ForegroundColor White
Write-Host ""

# Run the agent
python main.py --register LANET-75F6-EC23-85DC9D

Write-Host ""
Write-Host "Agent execution completed." -ForegroundColor Green
Read-Host "Press Enter to exit"
