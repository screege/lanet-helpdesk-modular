@echo off
REM LANET Agent Standalone Installer Build Script
REM Creates a single executable file for technician deployment

echo ========================================
echo LANET Agent Standalone Installer Build
echo ========================================
echo.
echo This script will create a standalone executable installer that:
echo - Requires no Python installation on target computers
echo - Includes all dependencies and agent files
echo - Provides one-click installation experience
echo - Works across 2000+ computers with enterprise reliability
echo.

REM Check if we're in the correct directory
if not exist "agent_files" (
    echo ERROR: agent_files directory not found!
    echo Please run this script from the production_installer directory.
    pause
    exit /b 1
)

if not exist "standalone_installer.py" (
    echo ERROR: standalone_installer.py not found!
    echo Please ensure all installer files are present.
    pause
    exit /b 1
)

echo Starting build process...
echo.

REM Run the build script
python build_standalone_installer.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo BUILD COMPLETED SUCCESSFULLY!
    echo ========================================
    echo.
    echo The standalone installer has been created:
    echo - Executable: dist\LANET_Agent_Installer.exe
    echo - Deployment package: deployment\
    echo.
    echo The installer is ready for technician deployment!
    echo.
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo.
    echo Please check the error messages above and try again.
    echo.
)

pause
