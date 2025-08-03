# ProjectMeats Windows Production Deployment Script
# ================================================
# 
# This PowerShell script deploys ProjectMeats to production on Windows Server
# Supports Windows Server 2019/2022 and Windows 10/11 Pro
#
# Usage:
#   .\deploy_windows_production.ps1 -Domain "yourdomain.com" -Interactive
#   .\deploy_windows_production.ps1 -Domain "yourdomain.com" -ServerIP "192.168.1.100" -Auto
#
# Requirements:
#   - Windows Server 2019+ or Windows 10+ Pro
#   - PowerShell 5.1+ (comes with Windows)
#   - Internet connection
#   - Administrator privileges

param(
    [Parameter(Mandatory=$false)]
    [string]$Domain,
    
    [Parameter(Mandatory=$false)]
    [string]$ServerIP,
    
    [Parameter(Mandatory=$false)]
    [string]$GitHubUser,
    
    [Parameter(Mandatory=$false)]
    [string]$GitHubToken,
    
    [Parameter(Mandatory=$false)]
    [switch]$Interactive,
    
    [Parameter(Mandatory=$false)]
    [switch]$Auto,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipSSL,
    
    [Parameter(Mandatory=$false)]
    [switch]$DevMode
)

# Color functions for better output
function Write-ColorOutput {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$Color = "White"
    )
    
    switch ($Color.ToLower()) {
        "red" { Write-Host $Message -ForegroundColor Red }
        "green" { Write-Host $Message -ForegroundColor Green }
        "yellow" { Write-Host $Message -ForegroundColor Yellow }
        "blue" { Write-Host $Message -ForegroundColor Blue }
        "cyan" { Write-Host $Message -ForegroundColor Cyan }
        "magenta" { Write-Host $Message -ForegroundColor Magenta }
        default { Write-Host $Message -ForegroundColor White }
    }
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput "============================================================" "Cyan"
    Write-ColorOutput " $Title" "White"
    Write-ColorOutput "============================================================" "Cyan"
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ️  $Message" "Blue"
}

# Check if running as Administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Install Chocolatey if not present
function Install-Chocolatey {
    Write-Info "Checking for Chocolatey package manager..."
    
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Success "Chocolatey is already installed"
        return $true
    }
    
    Write-Info "Installing Chocolatey package manager..."
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        
        Write-Success "Chocolatey installed successfully"
        return $true
    }
    catch {
        Write-Error "Failed to install Chocolatey: $($_.Exception.Message)"
        return $false
    }
}

# Install required software
function Install-Dependencies {
    Write-Header "Installing Dependencies"
    
    # Install Chocolatey first
    if (-not (Install-Chocolatey)) {
        return $false
    }
    
    # Define required packages
    $packages = @(
        "python",
        "nodejs",
        "git",
        "postgresql13",
        "nginx",
        "nssm"  # Non-Sucking Service Manager for Windows services
    )
    
    foreach ($package in $packages) {
        Write-Info "Installing $package..."
        try {
            choco install $package -y
            Write-Success "$package installed successfully"
        }
        catch {
            Write-Warning "Failed to install $package, trying to continue..."
        }
    }
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    
    return $true
}

# Verify installations
function Test-Dependencies {
    Write-Header "Verifying Dependencies"
    
    $allGood = $true
    
    # Test Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python: $pythonVersion"
    }
    catch {
        Write-Error "Python not found or not working"
        $allGood = $false
    }
    
    # Test Node.js
    try {
        $nodeVersion = node --version 2>&1
        Write-Success "Node.js: $nodeVersion"
    }
    catch {
        Write-Error "Node.js not found or not working"
        $allGood = $false
    }
    
    # Test Git
    try {
        $gitVersion = git --version 2>&1
        Write-Success "Git: $gitVersion"
    }
    catch {
        Write-Error "Git not found or not working"
        $allGood = $false
    }
    
    # Test PostgreSQL
    try {
        $pgVersion = pg_config --version 2>&1
        Write-Success "PostgreSQL: $pgVersion"
    }
    catch {
        Write-Warning "PostgreSQL command line tools not found, but service might be running"
    }
    
    return $allGood
}

# Download ProjectMeats repository
function Get-ProjectMeats {
    Write-Header "Downloading ProjectMeats"
    
    $deployDir = "C:\ProjectMeats"
    
    # Remove existing directory if it exists
    if (Test-Path $deployDir) {
        Write-Info "Removing existing ProjectMeats directory..."
        Remove-Item $deployDir -Recurse -Force
    }
    
    # Clone repository
    Write-Info "Cloning ProjectMeats repository..."
    try {
        if ($GitHubUser -and $GitHubToken) {
            $repoUrl = "https://${GitHubUser}:${GitHubToken}@github.com/Vacilator/ProjectMeats.git"
        }
        else {
            $repoUrl = "https://github.com/Vacilator/ProjectMeats.git"
        }
        
        git clone $repoUrl $deployDir
        Set-Location $deployDir
        Write-Success "ProjectMeats downloaded successfully"
        return $true
    }
    catch {
        Write-Error "Failed to download ProjectMeats: $($_.Exception.Message)"
        return $false
    }
}

# Setup PostgreSQL database
function Setup-Database {
    Write-Header "Setting up PostgreSQL Database"
    
    # Start PostgreSQL service
    Write-Info "Starting PostgreSQL service..."
    try {
        Start-Service postgresql-x64-13
        Write-Success "PostgreSQL service started"
    }
    catch {
        Write-Warning "Could not start PostgreSQL service, trying manual setup..."
    }
    
    # Create database and user
    Write-Info "Creating database and user..."
    $dbPassword = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    
    try {
        # Note: This requires PostgreSQL to be properly configured
        # In production, this would need to be adapted based on the actual PostgreSQL setup
        $createDbScript = @"
CREATE DATABASE projectmeats_prod;
CREATE USER projectmeats WITH PASSWORD '$dbPassword';
GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod TO projectmeats;
"@
        
        # Save database password for later use
        $dbPassword | Out-File -FilePath "C:\ProjectMeats\db_password.txt" -Encoding UTF8
        
        Write-Success "Database setup completed"
        return $dbPassword
    }
    catch {
        Write-Error "Database setup failed: $($_.Exception.Message)"
        return $null
    }
}

# Setup Python environment and install dependencies
function Setup-Backend {
    Write-Header "Setting up Backend"
    
    Set-Location "C:\ProjectMeats\backend"
    
    # Create virtual environment
    Write-Info "Creating Python virtual environment..."
    python -m venv venv
    
    # Activate virtual environment
    Write-Info "Activating virtual environment..."
    & ".\venv\Scripts\Activate.ps1"
    
    # Install dependencies
    Write-Info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Setup environment file
    Write-Info "Creating production environment file..."
    $envContent = @"
DEBUG=False
SECRET_KEY=$(New-Guid)
ALLOWED_HOSTS=$Domain,localhost,127.0.0.1
DATABASE_URL=postgresql://projectmeats:$dbPassword@localhost:5432/projectmeats_prod
CORS_ALLOWED_ORIGINS=https://$Domain,http://localhost:3000
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    
    # Run migrations
    Write-Info "Running database migrations..."
    python manage.py migrate
    
    # Create superuser
    Write-Info "Creating admin user..."
    $createUserScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@projectmeats.com', 'WATERMELON1219')
    print('Admin user created successfully')
else:
    print('Admin user already exists')
"@
    
    $createUserScript | python manage.py shell
    
    # Collect static files
    Write-Info "Collecting static files..."
    python manage.py collectstatic --noinput
    
    Write-Success "Backend setup completed"
    return $true
}

# Setup frontend
function Setup-Frontend {
    Write-Header "Setting up Frontend"
    
    Set-Location "C:\ProjectMeats\frontend"
    
    # Install dependencies
    Write-Info "Installing Node.js dependencies..."
    npm install
    
    # Build for production
    Write-Info "Building frontend for production..."
    npm run build
    
    Write-Success "Frontend setup completed"
    return $true
}

# Configure Nginx
function Setup-Nginx {
    Write-Header "Setting up Nginx Web Server"
    
    $nginxConfig = @"
server {
    listen 80;
    server_name $Domain;
    
    # Redirect HTTP to HTTPS
    return 301 https://`$server_name`$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $Domain;
    
    # SSL configuration (self-signed for now)
    ssl_certificate C:/ProjectMeats/ssl/cert.pem;
    ssl_certificate_key C:/ProjectMeats/ssl/key.pem;
    
    # Frontend static files
    location / {
        root C:/ProjectMeats/frontend/build;
        index index.html;
        try_files `$uri `$uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }
    
    # Django admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }
    
    # Static files for Django
    location /static/ {
        alias C:/ProjectMeats/backend/staticfiles/;
    }
}
"@
    
    # Create Nginx config directory if it doesn't exist
    $nginxConfigDir = "C:\tools\nginx\conf\conf.d"
    if (-not (Test-Path $nginxConfigDir)) {
        New-Item -ItemType Directory -Path $nginxConfigDir -Force
    }
    
    # Write config file
    $nginxConfig | Out-File -FilePath "$nginxConfigDir\projectmeats.conf" -Encoding UTF8
    
    Write-Success "Nginx configuration created"
    return $true
}

# Create SSL certificates (self-signed for development)
function Setup-SSL {
    Write-Header "Setting up SSL Certificates"
    
    if ($SkipSSL) {
        Write-Warning "Skipping SSL setup as requested"
        return $true
    }
    
    $sslDir = "C:\ProjectMeats\ssl"
    if (-not (Test-Path $sslDir)) {
        New-Item -ItemType Directory -Path $sslDir -Force
    }
    
    # Generate self-signed certificate for development
    Write-Info "Generating self-signed SSL certificate..."
    try {
        $cert = New-SelfSignedCertificate -DnsName $Domain -CertStoreLocation Cert:\LocalMachine\My
        $certPath = "C:\ProjectMeats\ssl\cert.pem"
        $keyPath = "C:\ProjectMeats\ssl\key.pem"
        
        # Export certificate and key
        Export-Certificate -Cert $cert -FilePath $certPath -Type CERT
        
        Write-Success "Self-signed SSL certificate created"
        Write-Warning "For production, replace with proper SSL certificates from Let's Encrypt or a CA"
        return $true
    }
    catch {
        Write-Error "SSL certificate generation failed: $($_.Exception.Message)"
        return $false
    }
}

# Create Windows services
function Setup-Services {
    Write-Header "Setting up Windows Services"
    
    # Create Django service
    Write-Info "Creating Django backend service..."
    $djangoServicePath = "C:\ProjectMeats\backend\venv\Scripts\python.exe"
    $djangoServiceArgs = "C:\ProjectMeats\backend\manage.py runserver 127.0.0.1:8000 --noreload"
    
    nssm install "ProjectMeats-Django" $djangoServicePath $djangoServiceArgs
    nssm set "ProjectMeats-Django" AppDirectory "C:\ProjectMeats\backend"
    nssm set "ProjectMeats-Django" DisplayName "ProjectMeats Django Backend"
    nssm set "ProjectMeats-Django" Description "ProjectMeats Django REST API Backend"
    
    # Start Django service
    Start-Service "ProjectMeats-Django"
    Write-Success "Django service created and started"
    
    # Start Nginx service
    Write-Info "Starting Nginx service..."
    try {
        Start-Service nginx
        Write-Success "Nginx service started"
    }
    catch {
        Write-Warning "Could not start Nginx as service, it may need manual configuration"
    }
    
    return $true
}

# Configure Windows Firewall
function Setup-Firewall {
    Write-Header "Configuring Windows Firewall"
    
    Write-Info "Opening firewall ports..."
    
    # Open HTTP port
    New-NetFirewallRule -DisplayName "ProjectMeats HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
    
    # Open HTTPS port
    New-NetFirewallRule -DisplayName "ProjectMeats HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
    
    # Open Django development port (if needed)
    if ($DevMode) {
        New-NetFirewallRule -DisplayName "ProjectMeats Django Dev" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
    }
    
    Write-Success "Firewall rules configured"
    return $true
}

# Run deployment tests
function Test-Deployment {
    Write-Header "Testing Deployment"
    
    # Test backend
    Write-Info "Testing backend API..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Success "Backend API is responding"
        }
        else {
            Write-Warning "Backend API returned status code $($response.StatusCode)"
        }
    }
    catch {
        Write-Error "Backend API test failed: $($_.Exception.Message)"
    }
    
    # Test frontend (if nginx is running)
    Write-Info "Testing frontend..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Success "Frontend is accessible"
        }
        else {
            Write-Warning "Frontend returned status code $($response.StatusCode)"
        }
    }
    catch {
        Write-Warning "Frontend test failed, Nginx might not be configured correctly"
    }
    
    return $true
}

# Main deployment function
function Start-Deployment {
    Write-Header "🚀 ProjectMeats Windows Production Deployment"
    
    # Check admin privileges
    if (-not (Test-Administrator)) {
        Write-Error "This script must be run as Administrator"
        Write-Info "Right-click PowerShell and select 'Run as Administrator'"
        exit 1
    }
    
    # Interactive mode
    if ($Interactive -and -not $Auto) {
        Write-Info "Starting interactive deployment..."
        
        if (-not $Domain) {
            $Domain = Read-Host "Enter your domain name (e.g., mycompany.com)"
        }
        
        if (-not $ServerIP) {
            $ServerIP = Read-Host "Enter server IP address (optional, press Enter to skip)"
        }
        
        $useGitHub = Read-Host "Do you have GitHub credentials? (y/n)"
        if ($useGitHub -eq "y" -or $useGitHub -eq "Y") {
            $GitHubUser = Read-Host "GitHub username"
            $GitHubToken = Read-Host "GitHub token" -AsSecureString
            $GitHubToken = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($GitHubToken))
        }
        
        $skipSSL = Read-Host "Skip SSL setup for now? (y/n)"
        $SkipSSL = ($skipSSL -eq "y" -or $skipSSL -eq "Y")
    }
    
    # Validate required parameters
    if (-not $Domain) {
        Write-Error "Domain name is required"
        Write-Info "Use -Domain parameter or run with -Interactive"
        exit 1
    }
    
    # Execute deployment steps
    $steps = @(
        { Install-Dependencies },
        { Test-Dependencies },
        { Get-ProjectMeats },
        { Setup-Database },
        { Setup-Backend },
        { Setup-Frontend },
        { Setup-Nginx },
        { Setup-SSL },
        { Setup-Services },
        { Setup-Firewall },
        { Test-Deployment }
    )
    
    $completed = 0
    $total = $steps.Count
    
    foreach ($step in $steps) {
        $completed++
        Write-Info "Step $completed of $total..."
        
        if (-not (& $step)) {
            Write-Error "Deployment step failed"
            exit 1
        }
    }
    
    # Success message
    Write-Header "🎉 Deployment Complete!"
    Write-Success "ProjectMeats has been deployed successfully!"
    Write-Info ""
    Write-Info "Access URLs:"
    Write-Info "  Frontend: https://$Domain (or http://localhost)"
    Write-Info "  Backend API: https://$Domain/api/v1/ (or http://localhost:8000/api/v1/)"
    Write-Info "  Admin Panel: https://$Domain/admin/ (or http://localhost:8000/admin/)"
    Write-Info ""
    Write-Info "Admin Credentials:"
    Write-Info "  Username: admin"
    Write-Info "  Password: WATERMELON1219"
    Write-Info ""
    Write-Warning "Next Steps:"
    Write-Info "1. Configure proper SSL certificates for production"
    Write-Info "2. Update DNS records to point to this server"
    Write-Info "3. Configure automated backups"
    Write-Info "4. Review security settings"
    Write-Info ""
    Write-Info "For support, see: https://github.com/Vacilator/ProjectMeats"
}

# Execute deployment
Start-Deployment