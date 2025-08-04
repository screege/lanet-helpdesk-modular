# Apply Registration Fix NOW - Run as Administrator
Write-Host "APPLYING REGISTRATION FIX NOW" -ForegroundColor Green
Write-Host ""

# Stop service
Write-Host "1. Stopping service..." -ForegroundColor Yellow
sc.exe stop LANETAgent | Out-Null

# Take ownership and apply fix directly
Write-Host "2. Taking ownership and applying fix..." -ForegroundColor Yellow
takeown /f "C:\Program Files\LANET Agent\lanet_agent.py" /a | Out-Null
icacls "C:\Program Files\LANET Agent\lanet_agent.py" /grant Administrators:F | Out-Null

# Read current file and apply fix
$content = Get-Content "C:\Program Files\LANET Agent\lanet_agent.py" -Raw

# Apply the fix - replace the problematic line
$oldPattern = 'registration_data = response\.json\(\)'
$newReplacement = @'
response_data = response.json()
                
                # El backend devuelve los datos dentro de 'data'
                if 'data' in response_data:
                    registration_data = response_data['data']
                else:
                    registration_data = response_data
'@

$content = $content -replace $oldPattern, $newReplacement

# Write back the fixed content
$content | Out-File -FilePath "C:\Program Files\LANET Agent\lanet_agent.py" -Encoding UTF8 -Force

Write-Host "   ✅ Fix applied directly to installed file" -ForegroundColor Green

# Test the fix
Write-Host "3. Testing the fix..." -ForegroundColor Yellow
$testOutput = & "C:\Python310\python.exe" "C:\Program Files\LANET Agent\lanet_agent.py" 2>&1
Write-Host "Test output:" -ForegroundColor Cyan
$testOutput | Select-Object -First 10 | ForEach-Object {
    if ($_ -match "Successfully registered|Registration successful") {
        Write-Host "   $_" -ForegroundColor Green
    } elseif ($_ -match "Registration failed|ERROR") {
        Write-Host "   $_" -ForegroundColor Red
    } else {
        Write-Host "   $_" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "Fix applied! Now starting service..." -ForegroundColor Green

# Start service
sc.exe start LANETAgent

Write-Host "Service started. Check logs in a few seconds." -ForegroundColor Green
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
