@echo off
REM ========================================================================
REM LANET HELPDESK AGENT - ONE-CLICK ENTERPRISE INSTALLER
REM Version: 3.0.0 Enterprise
REM Purpose: Single double-click installation for technicians
REM Automatically elevates to administrator and launches GUI installer
REM ========================================================================

title LANET Agent Enterprise Installer

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ========================================================================
    echo LANET HELPDESK AGENT - ENTERPRISE INSTALLER
    echo ========================================================================
    echo.
    echo This installer requires Administrator privileges to install the Windows service.
    echo.
    echo Requesting administrator elevation...
    echo.
    
    REM Request administrator elevation and run PowerShell installer
    powershell -Command "Start-Process PowerShell -Verb RunAs -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0LANET_Agent_Professional_Installer.ps1\"'"
    
    if %errorLevel% equ 0 (
        echo Administrator elevation successful - GUI installer launched
        echo.
        echo Please complete the installation in the new window that opened.
        echo.
    ) else (
        echo.
        echo ERROR: Administrator elevation failed or was cancelled.
        echo.
        echo To install manually:
        echo 1. Right-click this file and select "Run as administrator"
        echo 2. Or run PowerShell as administrator and execute:
        echo    .\LANET_Agent_Professional_Installer.ps1
        echo.
    )
    
    pause
    exit /b %errorLevel%
)

REM If already running as administrator, launch directly
echo Running with administrator privileges - launching installer...
powershell -ExecutionPolicy Bypass -File "%~dp0LANET_Agent_Professional_Installer.ps1"

if %errorLevel% equ 0 (
    echo.
    echo Installation process completed.
) else (
    echo.
    echo Installation process encountered an error.
    echo Check the installation logs for details.
)

pause
