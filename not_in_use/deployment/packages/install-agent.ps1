# LANET Helpdesk V3 - Agent Installation Script
# PowerShell script para instalar el agente en Windows

param(
    [Parameter(Mandatory=$true)]
    [string]$InstallationToken,
    
    [Parameter(Mandatory=$false)]
    [string]$ServerUrl = "https://helpdesk.lanet.mx",
    
    [Parameter(Mandatory=$false)]
    [string]$InstallPath = "C:\Program Files\LANET Agent",
    
    [Parameter(Mandatory=$false)]
    [switch]$Silent = $false
)

# Verificar si se ejecuta como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "Este script debe ejecutarse como Administrador"
    exit 1
}

Write-Host "=== LANET Helpdesk V3 - Instalación del Agente ===" -ForegroundColor Green
Write-Host "Token de instalación: $InstallationToken"
Write-Host "Servidor: $ServerUrl"
Write-Host "Ruta de instalación: $InstallPath"
Write-Host ""

try {
    # Crear directorio de instalación
    Write-Host "Creando directorio de instalación..." -ForegroundColor Yellow
    if (!(Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    }
    
    # Crear subdirectorios
    $LogsPath = Join-Path $InstallPath "logs"
    if (!(Test-Path $LogsPath)) {
        New-Item -ItemType Directory -Path $LogsPath -Force | Out-Null
    }
    
    # Copiar archivo del agente
    Write-Host "Copiando archivos del agente..." -ForegroundColor Yellow
    $AgentSource = Join-Path $PSScriptRoot "lanet-agent-windows-v2.py"
    $AgentDest = Join-Path $InstallPath "lanet-agent.py"
    
    if (Test-Path $AgentSource) {
        Copy-Item $AgentSource $AgentDest -Force
    } else {
        Write-Error "No se encontró el archivo del agente: $AgentSource"
        exit 1
    }
    
    # Verificar Python
    Write-Host "Verificando instalación de Python..." -ForegroundColor Yellow
    try {
        $PythonVersion = python --version 2>&1
        Write-Host "Python encontrado: $PythonVersion" -ForegroundColor Green
    } catch {
        Write-Error "Python no está instalado o no está en el PATH"
        Write-Host "Por favor instale Python 3.8 o superior desde https://python.org"
        exit 1
    }
    
    # Instalar dependencias de Python
    Write-Host "Instalando dependencias de Python..." -ForegroundColor Yellow
    $RequiredPackages = @("psutil", "requests", "configparser")
    
    foreach ($Package in $RequiredPackages) {
        Write-Host "Instalando $Package..." -ForegroundColor Cyan
        python -m pip install $Package --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Error instalando $Package, pero continuando..."
        }
    }
    
    # Crear archivo de configuración inicial
    Write-Host "Creando configuración inicial..." -ForegroundColor Yellow
    $ConfigPath = Join-Path $InstallPath "config.ini"
    $ConfigContent = @"
[SERVER]
url = $ServerUrl
heartbeat_interval = 60
inventory_interval = 3600
metrics_interval = 300

[AGENT]
computer_name = $env:COMPUTERNAME
auto_create_tickets = true
version = 2.0.0

[ALERTS]
disk_threshold = 90
cpu_threshold = 85
ram_threshold = 95
temp_threshold = 80

[REGISTRATION]
installation_token = $InstallationToken
asset_id = 
agent_token = 
client_id = 
site_id = 
client_name = 
site_name = 
"@
    
    Set-Content -Path $ConfigPath -Value $ConfigContent -Encoding UTF8
    
    # Registrar agente
    Write-Host "Registrando agente con el servidor..." -ForegroundColor Yellow
    $RegisterCommand = "python `"$AgentDest`" --register `"$InstallationToken`""
    
    try {
        $RegisterResult = Invoke-Expression $RegisterCommand 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Agente registrado exitosamente!" -ForegroundColor Green
            Write-Host $RegisterResult
        } else {
            Write-Error "Error durante el registro del agente:"
            Write-Host $RegisterResult -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Error "Error ejecutando el registro: $_"
        exit 1
    }
    
    # Crear servicio de Windows
    Write-Host "Creando servicio de Windows..." -ForegroundColor Yellow
    
    # Crear script wrapper para el servicio
    $ServiceScript = Join-Path $InstallPath "service-wrapper.py"
    $ServiceScriptContent = @"
import sys
import os
import time
import subprocess
import logging
from pathlib import Path

# Configurar logging para el servicio
log_file = Path(r"$LogsPath\service.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_agent():
    agent_path = r"$AgentDest"
    while True:
        try:
            logger.info("Starting LANET Agent...")
            result = subprocess.run([sys.executable, agent_path], 
                                  capture_output=False, 
                                  cwd=r"$InstallPath")
            
            if result.returncode != 0:
                logger.error(f"Agent exited with code {result.returncode}")
            
            logger.info("Agent stopped, restarting in 30 seconds...")
            time.sleep(30)
            
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
            break
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_agent()
"@
    
    Set-Content -Path $ServiceScript -Value $ServiceScriptContent -Encoding UTF8
    
    # Crear servicio usando NSSM (Non-Sucking Service Manager) si está disponible
    # O usar sc.exe como alternativa
    $ServiceName = "LANETAgent"
    $ServiceDisplayName = "LANET Helpdesk Agent"
    $ServiceDescription = "Agente de monitoreo y gestión para LANET Helpdesk V3"
    
    # Intentar usar NSSM primero
    try {
        nssm install $ServiceName python $ServiceScript 2>$null
        if ($LASTEXITCODE -eq 0) {
            nssm set $ServiceName DisplayName $ServiceDisplayName
            nssm set $ServiceName Description $ServiceDescription
            nssm set $ServiceName Start SERVICE_AUTO_START
            Write-Host "Servicio creado con NSSM" -ForegroundColor Green
        } else {
            throw "NSSM no disponible"
        }
    } catch {
        # Usar sc.exe como alternativa
        Write-Host "NSSM no disponible, usando sc.exe..." -ForegroundColor Yellow
        $ServiceCommand = "python.exe `"$ServiceScript`""
        sc.exe create $ServiceName binPath= $ServiceCommand start= auto DisplayName= $ServiceDisplayName
        sc.exe description $ServiceName $ServiceDescription
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Servicio creado con sc.exe" -ForegroundColor Green
        } else {
            Write-Warning "Error creando servicio, pero la instalación continuó"
        }
    }
    
    # Iniciar servicio
    Write-Host "Iniciando servicio..." -ForegroundColor Yellow
    try {
        Start-Service -Name $ServiceName -ErrorAction Stop
        Write-Host "Servicio iniciado exitosamente!" -ForegroundColor Green
    } catch {
        Write-Warning "Error iniciando servicio: $_"
        Write-Host "Puede iniciar el servicio manualmente desde services.msc" -ForegroundColor Yellow
    }
    
    # Crear acceso directo en el escritorio (opcional)
    if (!$Silent) {
        $CreateShortcut = Read-Host "¿Crear acceso directo en el escritorio? (y/n)"
        if ($CreateShortcut -eq "y" -or $CreateShortcut -eq "Y") {
            $DesktopPath = [Environment]::GetFolderPath("Desktop")
            $ShortcutPath = Join-Path $DesktopPath "LANET Agent.lnk"
            
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
            $Shortcut.TargetPath = "python.exe"
            $Shortcut.Arguments = "`"$AgentDest`" --test"
            $Shortcut.WorkingDirectory = $InstallPath
            $Shortcut.IconLocation = "python.exe"
            $Shortcut.Description = "LANET Helpdesk Agent - Test"
            $Shortcut.Save()
            
            Write-Host "Acceso directo creado en el escritorio" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "=== Instalación Completada ===" -ForegroundColor Green
    Write-Host "El agente LANET ha sido instalado y configurado exitosamente." -ForegroundColor White
    Write-Host ""
    Write-Host "Ubicación: $InstallPath" -ForegroundColor Cyan
    Write-Host "Servicio: $ServiceName" -ForegroundColor Cyan
    Write-Host "Logs: $LogsPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Para verificar el estado del agente:" -ForegroundColor Yellow
    Write-Host "  Get-Service $ServiceName" -ForegroundColor White
    Write-Host ""
    Write-Host "Para probar el agente manualmente:" -ForegroundColor Yellow
    Write-Host "  python `"$AgentDest`" --test" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Error "Error durante la instalación: $_"
    Write-Host "Revise los logs para más detalles" -ForegroundColor Red
    exit 1
}

Write-Host "Presione cualquier tecla para continuar..." -ForegroundColor Gray
if (!$Silent) {
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
