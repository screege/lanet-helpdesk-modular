# LANET Agent - Instalador PowerShell
Write-Host "🚀 LANET Agent - Instalador Automatico" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

$InstallDir = "$env:USERPROFILE\LANET_Agent"

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    Write-Host "Descarga Python desde: https://www.python.org/downloads/"
    Read-Host "Presiona Enter para continuar"
    exit 1
}

# Crear directorio
Write-Host "📁 Creando directorio: $InstallDir" -ForegroundColor Yellow
if (Test-Path $InstallDir) {
    Remove-Item $InstallDir -Recurse -Force
}
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\logs" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\data" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\config" -Force | Out-Null

# Copiar archivos
Write-Host "📋 Copiando archivos..." -ForegroundColor Yellow
Copy-Item -Path "agent" -Destination "$InstallDir\agent" -Recurse -Force
Copy-Item -Path "requirements.txt" -Destination "$InstallDir\requirements.txt" -Force

# Instalar dependencias
Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
Set-Location $InstallDir
pip install -r requirements.txt

# Crear scripts
Write-Host "📝 Creando scripts..." -ForegroundColor Yellow

# Script de registro
$registerScript = @"
@echo off
cd /d "$InstallDir"
set /p TOKEN="Ingresa el token de instalacion: "
python agent\main.py --register %TOKEN%
pause
"@
Set-Content -Path "$InstallDir\register_agent.bat" -Value $registerScript

# Script de inicio
$startScript = @"
@echo off
cd /d "$InstallDir"
python agent\main.py
pause
"@
Set-Content -Path "$InstallDir\start_agent.bat" -Value $startScript

# Crear acceso directo
Write-Host "📎 Creando acceso directo..." -ForegroundColor Yellow
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\LANET Agent.lnk")
$Shortcut.TargetPath = "$InstallDir\start_agent.bat"
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Save()

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✅ INSTALACION COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Directorio: $InstallDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "PASOS SIGUIENTES:" -ForegroundColor Yellow
Write-Host "1. Ejecutar: $InstallDir\register_agent.bat" -ForegroundColor White
Write-Host "2. Ingresar tu token de instalacion" -ForegroundColor White
Write-Host "3. Ejecutar: $InstallDir\start_agent.bat" -ForegroundColor White
Write-Host ""
Write-Host "O usar el acceso directo del escritorio" -ForegroundColor White
Write-Host ""
Read-Host "Presiona Enter para continuar"
