# ProjectMeats Windows Setup Script
# PowerShell equivalent of Makefile commands with enhanced error handling

param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$SkipPrereqs,
    [switch]$Help
)

# Color functions for better output
function Write-Info { 
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue 
}

function Write-Success { 
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green 
}

function Write-Warning { 
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow 
}

function Write-Error { 
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red 
}

function Write-Step { 
    param($Message)
    Write-Host "[STEP] $Message" -ForegroundColor Magenta 
}

function Show-Help {
    Write-Host "ProjectMeats Windows Setup Script" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\setup.ps1                    # Full setup (backend + frontend)"
    Write-Host "  .\setup.ps1 -Backend           # Backend only"
    Write-Host "  .\setup.ps1 -Frontend          # Frontend only"
    Write-Host "  .\setup.ps1 -SkipPrereqs       # Skip prerequisite checks"
    Write-Host "  .\setup.ps1 -Help              # Show this help"
    Write-Host ""
    Write-Host "Alternative (recommended):"
    Write-Host "  python setup.py                # Cross-platform Python script"
    Write-Host ""
    Write-Host "For more information, see docs/setup_guide.md"
}

function Test-Command {
    param($Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Test-Prerequisites {
    Write-Step "🔍 Checking system prerequisites..."
    $allGood = $true
    
    # Check Python
    if (Test-Command "python") {
        $pythonVersion = python --version 2>&1
        Write-Success "✓ Python found: $pythonVersion"
    } elseif (Test-Command "python3") {
        $pythonVersion = python3 --version 2>&1
        Write-Success "✓ Python3 found: $pythonVersion"
    } else {
        Write-Error "✗ Python not found. Please install Python 3.9+ from https://python.org"
        $allGood = $false
    }
    
    # Check Node.js
    if (Test-Command "node") {
        $nodeVersion = node --version 2>&1
        Write-Success "✓ Node.js found: $nodeVersion"
    } else {
        Write-Error "✗ Node.js not found. Please install Node.js 16+ from https://nodejs.org"
        $allGood = $false
    }
    
    # Check npm
    if (Test-Command "npm") {
        $npmVersion = npm --version 2>&1
        Write-Success "✓ npm found: $npmVersion"
    } else {
        Write-Error "✗ npm not found. Should come with Node.js installation"
        $allGood = $false
    }
    
    # Check pip
    if (Test-Command "pip") {
        $pipVersion = pip --version 2>&1
        Write-Success "✓ pip found: $($pipVersion.Split(' ')[1])"
    } elseif (Test-Command "pip3") {
        $pipVersion = pip3 --version 2>&1
        Write-Success "✓ pip3 found: $($pipVersion.Split(' ')[1])"
    } else {
        Write-Error "✗ pip not found. Should come with Python installation"
        $allGood = $false
    }
    
    # Check git (optional)
    if (Test-Command "git") {
        Write-Success "✓ Git available for version control"
    } else {
        Write-Warning "ℹ️  Git not found - version control won't be available"
    }
    
    if ($allGood) {
        Write-Success "✅ Prerequisites check completed"
    } else {
        Write-Error "❌ Prerequisites not met"
    }
    
    return $allGood
}

function Setup-Backend {
    Write-Step "🔧 Setting up Django backend..."
    
    # Check if backend directory exists
    if (!(Test-Path "backend")) {
        Write-Error "Backend directory not found"
        return $false
    }
    
    Set-Location backend
    
    try {
        # Copy .env.example to .env if it doesn't exist
        if (!(Test-Path .env)) { 
            if (Test-Path .env.example) {
                Copy-Item .env.example .env 
                Write-Success "✓ Created .env file"
            } else {
                Write-Error "✗ .env.example not found"
                return $false
            }
        } else {
            Write-Warning "ℹ️  .env file already exists"
        }
        
        # Install Python dependencies
        Write-Info "📦 Installing Python dependencies..."
        
        # Check if requirements.txt exists
        if (!(Test-Path requirements.txt)) {
            Write-Error "✗ requirements.txt not found"
            return $false
        }
        
        # Determine pip command
        $pipCmd = if (Test-Command "pip3") { "pip3" } else { "pip" }
        
        # Install requirements
        $result = & $pipCmd install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Error "✗ Failed to install Python dependencies"
            return $false
        }
        
        # Run migrations
        Write-Info "🗃️  Running database migrations..."
        $pythonCmd = if (Test-Command "python3") { "python3" } else { "python" }
        
        $result = & $pythonCmd manage.py migrate
        if ($LASTEXITCODE -ne 0) {
            Write-Error "✗ Failed to run migrations"
            return $false
        }
        
        Write-Success "✅ Backend setup complete!"
        return $true
    }
    catch {
        Write-Error "✗ Backend setup failed: $($_.Exception.Message)"
        return $false
    }
    finally {
        Set-Location ..
    }
}

function Setup-Frontend {
    Write-Step "🔧 Setting up React frontend..."
    
    # Check if frontend directory exists
    if (!(Test-Path "frontend")) {
        Write-Error "Frontend directory not found"
        return $false
    }
    
    Set-Location frontend
    
    try {
        # Check package.json exists
        if (!(Test-Path package.json)) {
            Write-Error "✗ package.json not found"
            return $false
        }
        
        # Install Node.js dependencies
        Write-Info "📦 Installing Node.js dependencies..."
        
        $result = npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Error "✗ Failed to install Node.js dependencies"
            return $false
        }
        
        # Create environment file if needed
        if (!(Test-Path .env.local)) {
            if (Test-Path .env.example) {
                Copy-Item .env.example .env.local
                Write-Success "✓ Created .env.local from example"
            } else {
                # Create basic environment file
                @"
# React Environment Variables
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
"@ | Out-File -FilePath .env.local -Encoding utf8
                Write-Success "✓ Created basic .env.local"
            }
        } else {
            Write-Warning "ℹ️  .env.local already exists"
        }
        
        Write-Success "✅ Frontend setup complete!"
        return $true
    }
    catch {
        Write-Error "✗ Frontend setup failed: $($_.Exception.Message)"
        return $false
    }
    finally {
        Set-Location ..
    }
}

function Show-NextSteps {
    Write-Success "`n🎉 Setup completed successfully!"
    
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "1. Start the backend server:"
    Write-Host "   cd backend && python manage.py runserver" -ForegroundColor Cyan
    
    Write-Host "`n2. Start the frontend server:"
    Write-Host "   cd frontend && npm start" -ForegroundColor Cyan
    
    Write-Host "`n3. Access the application:"
    Write-Host "   Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor Cyan
    Write-Host "   API Docs:    http://localhost:8000/api/docs/" -ForegroundColor Cyan
    
    Write-Host "`nPowerShell Aliases (optional):" -ForegroundColor Yellow
    Write-Host "   Set-Alias pm-backend 'cd backend && python manage.py runserver'" -ForegroundColor Cyan
    Write-Host "   Set-Alias pm-frontend 'cd frontend && npm start'" -ForegroundColor Cyan
    
    Write-Host "`nDocumentation:" -ForegroundColor Yellow
    Write-Host "   README.md           - Project overview" -ForegroundColor Cyan
    Write-Host "   docs/setup_guide.md  - Comprehensive setup guide" -ForegroundColor Cyan
    Write-Host "   docs/               - Complete documentation" -ForegroundColor Cyan
}

# Main execution
function Main {
    if ($Help) {
        Show-Help
        exit 0
    }
    
    Write-Step "🚀 ProjectMeats Windows Setup Script"
    Write-Info "Platform: Windows $([Environment]::OSVersion.Version)"
    Write-Info "PowerShell: $($PSVersionTable.PSVersion)"
    Write-Info "Working directory: $(Get-Location)"
    
    # Check prerequisites
    if (!$SkipPrereqs) {
        if (!(Test-Prerequisites)) {
            Write-Error "Prerequisites not met. Please install required dependencies."
            Write-Info "Run with -SkipPrereqs to bypass checks (not recommended)"
            exit 1
        }
    }
    
    # Determine what to setup
    $setupBackend = $Backend -or !$Frontend
    $setupFrontend = $Frontend -or !$Backend
    
    $success = $true
    
    # Setup backend
    if ($setupBackend) {
        if (!(Setup-Backend)) {
            $success = $false
        }
    }
    
    # Setup frontend  
    if ($setupFrontend) {
        if (!(Setup-Frontend)) {
            $success = $false
        }
    }
    
    if ($success) {
        Show-NextSteps
        exit 0
    } else {
        Write-Error "Setup completed with errors. Please check the messages above."
        Write-Info "Consider using the cross-platform Python script: python setup.py"
        exit 1
    }
}

# Run main function
Main
