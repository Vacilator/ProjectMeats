@echo off
REM ProjectMeats AI Assistant Quick Setup for Windows
REM This script provides a simplified setup process for the AI Assistant

echo.
echo ========================================
echo  ProjectMeats AI Assistant Setup
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

echo.
echo Choose setup option:
echo 1. Full Setup (Backend + Frontend + AI Assistant)
echo 2. Backend Only
echo 3. Frontend Only
echo 4. AI Assistant Configuration Only
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Running full setup...
    python setup.py
    if errorlevel 1 goto error
    echo.
    echo Running AI Assistant configuration...
    python setup_ai_assistant.py
    if errorlevel 1 goto error
) else if "%choice%"=="2" (
    echo Running backend setup...
    python setup.py --backend
    if errorlevel 1 goto error
) else if "%choice%"=="3" (
    echo Running frontend setup...
    python setup.py --frontend
    if errorlevel 1 goto error
) else if "%choice%"=="4" (
    echo Running AI Assistant configuration...
    python setup_ai_assistant.py
    if errorlevel 1 goto error
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

goto success

:error
echo.
echo ========================================
echo  Setup encountered errors
echo ========================================
echo.
echo Please check the error messages above.
echo For troubleshooting, see docs/ai_assistant_setup.md
echo.
pause
exit /b 1

:success
echo.
echo ========================================
echo  Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Start the backend server:
echo    cd backend
echo    python manage.py runserver
echo.
echo 2. Start the frontend server (in a new terminal):
echo    cd frontend
echo    npm start
echo.
echo 3. Access the application:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000/api/v1
echo    Admin Panel: http://localhost:8000/admin
echo.
echo For more information, see docs/ai_assistant_setup.md
echo.
pause