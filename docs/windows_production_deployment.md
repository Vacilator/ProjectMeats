# ProjectMeats Windows Production Deployment Guide

## 🚀 Complete Windows Production Deployment

This guide covers deploying ProjectMeats to production on Windows Server or Windows 10/11 Pro systems.

### 📋 Prerequisites

#### System Requirements
- **Windows Server 2019/2022** or **Windows 10/11 Pro**
- **4GB RAM minimum** (8GB+ recommended)
- **20GB free disk space** minimum
- **Administrator privileges**
- **Internet connection**

#### Required Software
The deployment script will automatically install these, but you can install manually if preferred:
- **Python 3.9+** 
- **Node.js 16+**
- **Git**
- **PostgreSQL 13+**
- **Nginx** (or IIS as alternative)

## ⚡ Quick Deployment Options

### Option 1: Automated PowerShell Deployment (Recommended)

**Download and run the Windows production deployment script:**

```powershell
# Download the deployment script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_windows_production.ps1" -OutFile "deploy_windows_production.ps1"

# Run interactive deployment
.\deploy_windows_production.ps1 -Interactive

# Or for automatic deployment with your domain
.\deploy_windows_production.ps1 -Domain "yourdomain.com" -Auto
```

### Option 2: Batch File Launcher

**Download and run the simple batch launcher:**

```cmd
# Download the batch launcher
curl -o setup_windows_production.bat https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/setup_windows_production.bat

# Run as Administrator (right-click → "Run as administrator")
setup_windows_production.bat
```

### Option 3: Unified Deployment Tool

**Use the cross-platform unified tool:**

```powershell
# Clone the repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Run the unified deployment tool
python unified_deployment_tool.py --production --interactive
```

## 🔧 Manual Step-by-Step Deployment

If you prefer manual control or need to troubleshoot:

### Step 1: Install Dependencies

#### Using Chocolatey (Recommended)
```powershell
# Install Chocolatey package manager
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install required packages
choco install python nodejs git postgresql13 nginx nssm -y
```

#### Manual Installation
1. **Python**: Download from [python.org](https://www.python.org/downloads/)
2. **Node.js**: Download from [nodejs.org](https://nodejs.org/)
3. **Git**: Download from [git-scm.com](https://git-scm.com/)
4. **PostgreSQL**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
5. **Nginx**: Download from [nginx.org](http://nginx.org/en/download.html)

### Step 2: Clone and Setup ProjectMeats

```powershell
# Create deployment directory
New-Item -ItemType Directory -Path "C:\ProjectMeats" -Force
Set-Location "C:\ProjectMeats"

# Clone repository
git clone https://github.com/Vacilator/ProjectMeats.git .

# Setup backend
Set-Location "backend"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Setup frontend
Set-Location "..\frontend"
npm install
npm run build
```

### Step 3: Configure Database

```powershell
# Start PostgreSQL service
Start-Service postgresql-x64-13

# Create database (adjust path as needed)
& "C:\Program Files\PostgreSQL\13\bin\psql.exe" -U postgres -c "CREATE DATABASE projectmeats_prod;"
& "C:\Program Files\PostgreSQL\13\bin\psql.exe" -U postgres -c "CREATE USER projectmeats WITH PASSWORD 'your_secure_password';"
& "C:\Program Files\PostgreSQL\13\bin\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod TO projectmeats;"
```

### Step 4: Configure Environment

Create `backend\.env` file:
```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1
DATABASE_URL=postgresql://projectmeats:your_secure_password@localhost:5432/projectmeats_prod
CORS_ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:3000
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Step 5: Run Migrations and Create Admin User

```powershell
Set-Location "C:\ProjectMeats\backend"
.\venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Step 6: Configure Nginx

Create `C:\tools\nginx\conf\conf.d\projectmeats.conf`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate C:/ProjectMeats/ssl/cert.pem;
    ssl_certificate_key C:/ProjectMeats/ssl/key.pem;
    
    location / {
        root C:/ProjectMeats/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias C:/ProjectMeats/backend/staticfiles/;
    }
}
```

### Step 7: Create Windows Services

```powershell
# Install NSSM (Non-Sucking Service Manager)
choco install nssm -y

# Create Django service
nssm install "ProjectMeats-Django" "C:\ProjectMeats\backend\venv\Scripts\python.exe" "C:\ProjectMeats\backend\manage.py runserver 127.0.0.1:8000 --noreload"
nssm set "ProjectMeats-Django" AppDirectory "C:\ProjectMeats\backend"
nssm set "ProjectMeats-Django" DisplayName "ProjectMeats Django Backend"
nssm set "ProjectMeats-Django" Description "ProjectMeats Django REST API Backend"

# Start services
Start-Service "ProjectMeats-Django"
Start-Service nginx
```

### Step 8: Configure Firewall

```powershell
# Open firewall ports
New-NetFirewallRule -DisplayName "ProjectMeats HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "ProjectMeats HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

## 🔒 SSL Certificate Configuration

### For Development/Testing
The deployment script creates self-signed certificates automatically.

### For Production
Replace self-signed certificates with proper SSL certificates:

1. **Using Let's Encrypt** (recommended for production):
   ```powershell
   # Install win-acme for Let's Encrypt on Windows
   choco install win-acme -y
   
   # Run Let's Encrypt certificate generation
   wacs.exe --target manual --host yourdomain.com --store certificatestore --installation iis
   ```

2. **Using purchased SSL certificates**:
   - Place your certificate files in `C:\ProjectMeats\ssl\`
   - Update Nginx configuration to point to your certificate files
   - Restart Nginx service

## 🔍 Troubleshooting

### Common Issues and Solutions

#### Python not found
```powershell
# Add Python to PATH
$env:Path += ";C:\Python39;C:\Python39\Scripts"
```

#### Node.js not found
```powershell
# Add Node.js to PATH
$env:Path += ";C:\Program Files\nodejs"
```

#### PostgreSQL connection issues
```powershell
# Check if PostgreSQL is running
Get-Service postgresql*
Start-Service postgresql-x64-13

# Check PostgreSQL logs
Get-Content "C:\Program Files\PostgreSQL\13\data\log\postgresql-*.log" -Tail 50
```

#### Nginx configuration errors
```powershell
# Test Nginx configuration
& "C:\tools\nginx\nginx.exe" -t

# Check Nginx error logs
Get-Content "C:\tools\nginx\logs\error.log" -Tail 50
```

#### Service startup issues
```powershell
# Check service status
Get-Service "ProjectMeats-Django"

# View service logs
Get-EventLog -LogName Application -Source "ProjectMeats-Django" -Newest 10
```

### Getting Help

1. **Check the logs**:
   - Django: `C:\ProjectMeats\backend\django.log`
   - Nginx: `C:\tools\nginx\logs\error.log`
   - PostgreSQL: `C:\Program Files\PostgreSQL\13\data\log\`

2. **Run diagnostics**:
   ```powershell
   python C:\ProjectMeats\unified_deployment_tool.py --diagnose
   ```

3. **Community support**:
   - GitHub Issues: https://github.com/Vacilator/ProjectMeats/issues
   - Documentation: https://github.com/Vacilator/ProjectMeats/docs

## 📊 Post-Deployment Verification

### Test Your Deployment

1. **Backend API**: https://yourdomain.com/api/v1/
2. **Frontend**: https://yourdomain.com/
3. **Admin Panel**: https://yourdomain.com/admin/
4. **Health Check**: https://yourdomain.com/api/v1/health/

### Default Credentials
- **Username**: admin
- **Password**: WATERMELON1219

**⚠️ Important**: Change the default password immediately after first login!

## 🔧 Maintenance and Updates

### Regular Maintenance Tasks

```powershell
# Update dependencies
Set-Location "C:\ProjectMeats\backend"
.\venv\Scripts\Activate.ps1
pip install --upgrade -r requirements.txt

Set-Location "..\frontend"
npm update

# Backup database
pg_dump -U projectmeats -h localhost projectmeats_prod > backup_$(Get-Date -Format "yyyy-MM-dd").sql

# Update application
git pull origin main
python manage.py migrate
python manage.py collectstatic --noinput
npm run build

# Restart services
Restart-Service "ProjectMeats-Django"
Restart-Service nginx
```

## 📚 Additional Resources

- **[Main README](../README.md)** - Project overview and development setup
- **[Production Checklist](../production_checklist.md)** - Pre-deployment checklist
- **[API Documentation](../docs/api_reference.md)** - Complete API reference
- **[Architecture Guide](../docs/architecture.md)** - System architecture details

---

**Need help?** Create an issue at https://github.com/Vacilator/ProjectMeats/issues