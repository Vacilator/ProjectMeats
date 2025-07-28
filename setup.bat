@echo off
REM ProjectMeats Windows Batch Setup Script
REM Alternative to PowerShell for Windows users

echo ============================================
echo  ProjectMeats Windows Setup Script
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.9+ from https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js 16+ from https://nodejs.org
    echo.
    pause
    exit /b 1
)

echo [INFO] Prerequisites check passed!
echo.

REM Ask user what to setup
echo What would you like to setup?
echo 1. Full setup (Backend + Frontend)
echo 2. Backend only
echo 3. Frontend only
echo 4. Use Python script (recommended)
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto full_setup
if "%choice%"=="2" goto backend_setup
if "%choice%"=="3" goto frontend_setup
if "%choice%"=="4" goto python_setup
echo Invalid choice. Using full setup...

:full_setup
echo [INFO] Starting full setup...
call :backend_setup
if %errorlevel% neq 0 exit /b 1
call :frontend_setup
if %errorlevel% neq 0 exit /b 1
goto success

:backend_setup
echo [INFO] Setting up Django backend...
if not exist "backend" (
    echo [ERROR] Backend directory not found
    exit /b 1
)

cd backend

REM Copy environment file
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [SUCCESS] Created .env file
    ) else (
        echo [ERROR] .env.example not found
        exit /b 1
    )
) else (
    echo [INFO] .env file already exists
)

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    exit /b 1
)

REM Run migrations
echo [INFO] Running database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to run migrations
    exit /b 1
)

echo [SUCCESS] Backend setup complete!
cd ..
exit /b 0

:frontend_setup
echo [INFO] Setting up React frontend...
if not exist "frontend" (
    echo [ERROR] Frontend directory not found
    exit /b 1
)

cd frontend

REM Install Node.js dependencies
echo [INFO] Installing Node.js dependencies...
npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Node.js dependencies
    exit /b 1
)

REM Create environment file if needed
if not exist ".env.local" (
    if exist ".env.example" (
        copy ".env.example" ".env.local" >nul
        echo [SUCCESS] Created .env.local from example
    ) else (
        echo # React Environment Variables > .env.local
        echo REACT_APP_API_BASE_URL=http://localhost:8000/api/v1 >> .env.local
        echo REACT_APP_ENVIRONMENT=development >> .env.local
        echo [SUCCESS] Created basic .env.local
    )
) else (
    echo [INFO] .env.local already exists
)

echo [SUCCESS] Frontend setup complete!
cd ..
exit /b 0

:python_setup
echo [INFO] Using Python setup script (recommended)...
python setup.py
if %errorlevel% neq 0 (
    echo [ERROR] Python setup script failed
    pause
    exit /b 1
)
goto success

:success
echo.
echo ============================================
echo  Setup completed successfully!
echo ============================================
echo.
echo Next Steps:
echo 1. Start the backend server:
echo    cd backend ^&^& python manage.py runserver
echo.
echo 2. Start the frontend server (in another terminal):
echo    cd frontend ^&^& npm start
echo.
echo 3. Access the application:
echo    Backend API: http://localhost:8000
echo    Frontend:    http://localhost:3000
echo    API Docs:    http://localhost:8000/api/docs/
echo.
echo For best experience, consider using:
echo    python setup.py
echo.
pause
exit /b 0