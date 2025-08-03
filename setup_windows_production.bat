@echo off
REM ProjectMeats Windows Production Deployment Launcher
REM This batch file provides easy access to the PowerShell deployment script

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  ProjectMeats Windows Production Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Choose deployment option:
echo.
echo 1. Interactive Setup (Recommended for first-time users)
echo 2. Quick Auto-Deploy (requires domain name)
echo 3. Development Setup (local development only)
echo 4. Just install dependencies
echo 5. Run diagnostics
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Starting interactive deployment...
    powershell -ExecutionPolicy Bypass -File "%~dp0deploy_windows_production.ps1" -Interactive
) else if "%choice%"=="2" (
    set /p domain="Enter your domain name (e.g., mycompany.com): "
    echo.
    echo Starting automatic deployment for !domain!...
    powershell -ExecutionPolicy Bypass -File "%~dp0deploy_windows_production.ps1" -Domain "!domain!" -Auto
) else if "%choice%"=="3" (
    echo.
    echo Setting up development environment...
    powershell -ExecutionPolicy Bypass -File "%~dp0deploy_windows_production.ps1" -Domain "localhost" -DevMode -SkipSSL -Auto
) else if "%choice%"=="4" (
    echo.
    echo Installing dependencies only...
    powershell -ExecutionPolicy Bypass -Command "& { . '%~dp0deploy_windows_production.ps1'; Install-Dependencies; Test-Dependencies }"
) else if "%choice%"=="5" (
    echo.
    echo Running deployment diagnostics...
    python "%~dp0unified_deployment_tool.py" --diagnose
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo  Deployment completed successfully!
    echo ========================================
    echo.
) else (
    echo.
    echo ========================================
    echo  Deployment encountered errors
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo For troubleshooting, see:
    echo - README.md
    echo - docs/production_deployment.md
    echo - https://github.com/Vacilator/ProjectMeats
    echo.
)

pause