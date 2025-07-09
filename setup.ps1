# ProjectMeats Windows Setup Script
# PowerShell equivalent of Makefile commands

Write-Host "🔧 Setting up Django backend..." -ForegroundColor Blue
Set-Location backend

# Copy .env.example to .env if it doesn't exist
if (!(Test-Path .env)) { 
    Copy-Item .env.example .env 
    Write-Host "✅ Created .env file" -ForegroundColor Green
} else {
    Write-Host "ℹ️  .env file already exists" -ForegroundColor Yellow
}

# Install Python dependencies (if venv exists)
if (Test-Path venv) {
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python manage.py migrate
    Write-Host "✅ Backend setup complete!" -ForegroundColor Green
}

Set-Location ..

Write-Host "🔧 Setting up React frontend..." -ForegroundColor Blue
Set-Location frontend

# Install Node dependencies
npm install
Write-Host "✅ Frontend setup complete!" -ForegroundColor Green

Set-Location ..
Write-Host "✅ Complete setup finished! Run the development servers manually." -ForegroundColor Green
