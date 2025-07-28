# ProjectMeats Complete Setup Guide

This comprehensive guide covers all setup scenarios for ProjectMeats, from quick development setup to production deployment.

## 📋 Table of Contents

1. [Quick Setup](#-quick-setup) - Get running in minutes
2. [Development Setup](#-development-setup) - Complete development environment
3. [Production Setup](#-production-setup) - Deploy to production
4. [Platform-Specific Setup](#-platform-specific-setup) - Windows, macOS, Linux
5. [Troubleshooting](#-troubleshooting) - Common issues and solutions
6. [Advanced Configuration](#-advanced-configuration) - Custom configurations

## 🚀 Quick Setup

### Prerequisites
Before starting, ensure you have:
- **Python 3.9+** - [Download from python.org](https://python.org)
- **Node.js 16+** - [Download from nodejs.org](https://nodejs.org)
- **Git** - For cloning the repository

### One-Command Setup (Recommended)
The fastest way to get ProjectMeats running:

```bash
# Clone repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Full setup (backend + frontend) - Works on all platforms
python setup.py

# Backend only
python setup.py --backend

# Frontend only  
python setup.py --frontend

# Show help and options
python setup.py --help
```

**What this does:**
- ✅ Checks for required dependencies
- ✅ Creates Python virtual environment
- ✅ Installs all dependencies
- ✅ Creates environment configuration files
- ✅ Runs database migrations
- ✅ Provides clear next steps

### Access Your Application
After setup completes:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

## 🔧 Development Setup

### Backend Development Environment

#### Step-by-Step Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your settings (optional for development)
# Uses SQLite by default, no database setup required

# Run database migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

#### Backend Environment Configuration
The `.env` file controls backend settings:

```env
# Development settings (default)
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Optional: PostgreSQL for development
# DATABASE_URL=postgresql://user:pass@localhost:5432/projectmeats_dev

# User Profile Settings
MAX_UPLOAD_SIZE=5242880  # 5MB for profile images
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,gif
DEFAULT_USER_TIMEZONE=UTC
```

#### Backend Development Commands
```bash
# Database management
python manage.py makemigrations    # Create migrations
python manage.py migrate           # Apply migrations
python manage.py showmigrations    # Show migration status

# User management
python manage.py createsuperuser   # Create admin user
python manage.py shell             # Django shell

# Testing
python manage.py test              # Run all tests
python manage.py test apps.accounts_receivables  # Test specific app

# Code quality
black .                           # Format code
flake8 .                         # Check code style
```

### Frontend Development Environment

#### Step-by-Step Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file for API connection
echo "REACT_APP_API_BASE_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm start
```

#### Frontend Environment Configuration
The `.env.local` file controls frontend settings:

```env
# Development API connection
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development

# Optional: Enable additional debugging
REACT_APP_DEBUG=true
```

#### Frontend Development Commands
```bash
# Development
npm start                         # Start development server
npm run build                     # Build for production
npm test                         # Run tests
npm run test:coverage            # Run tests with coverage

# Code quality
npm run lint                     # ESLint checking
npm run lint:fix                 # Auto-fix ESLint issues
npm run format                   # Prettier formatting
```

### AI-Enhanced Development (GitHub Copilot)

ProjectMeats includes comprehensive GitHub Copilot integration:

```bash
# Verify Copilot configuration
python verify_copilot_setup.py

# Open with enhanced VS Code workspace
code ProjectMeats.code-workspace
```

**Features:**
- Custom Copilot instructions for Django/React patterns
- MCP (Model Context Protocol) server integration
- Optimized VS Code configuration with debugging
- PowerApps migration context for AI suggestions

See [GitHub Copilot Usage Guide](copilot_usage_guide.md) for complete setup.

## 🚀 Production Setup

### Infrastructure Requirements

**Minimum Production Environment:**
- **Server**: 2 vCPU, 4GB RAM, 50GB SSD
- **Operating System**: Ubuntu 20.04+ LTS
- **Database**: PostgreSQL 12+
- **Web Server**: Nginx
- **SSL**: Let's Encrypt or commercial certificate

**Recommended Production Environment:**
- **Server**: 4 vCPU, 8GB RAM, 100GB SSD
- **Load Balancer**: For high availability
- **Cache**: Redis for session storage and caching
- **CDN**: For global performance
- **Monitoring**: Health checks and alerting

### Automated Production Deployment

```bash
# Clone repository to server
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Run automated production deployment
sudo ./deploy_production.sh
```

**What the deployment script does:**
- ✅ Installs system dependencies (Python, Node.js, PostgreSQL, Nginx)
- ✅ Creates application user and directories
- ✅ Sets up PostgreSQL database and user
- ✅ Deploys backend with Gunicorn
- ✅ Builds and deploys frontend
- ✅ Configures Nginx with SSL
- ✅ Sets up security (firewall, Fail2Ban)
- ✅ Configures monitoring and backups
- ✅ Creates systemd services

### Manual Production Setup

If you prefer manual setup or need custom configuration:

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql nginx git curl

# Create application user
sudo useradd -m -s /bin/bash projectmeats
```

#### 2. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres createdb projectmeats_prod
sudo -u postgres createuser projectmeats_user
sudo -u postgres psql -c "ALTER USER projectmeats_user PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod TO projectmeats_user;"
```

#### 3. Application Deployment
```bash
# Deploy as application user
sudo su - projectmeats
git clone https://github.com/Vacilator/ProjectMeats.git app
cd app

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create production environment
cat > .env << EOF
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://projectmeats_user:secure_password@localhost:5432/projectmeats_prod
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
CORS_ALLOWED_ORIGINS=https://yourdomain.com
EOF

# Run migrations and collect static files
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# Frontend setup
cd ../frontend
npm install
echo "REACT_APP_API_BASE_URL=https://yourdomain.com/api/v1" > .env.production
npm run build
```

#### 4. Web Server Configuration
```nginx
# /etc/nginx/sites-available/projectmeats
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        root /home/projectmeats/app/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/projectmeats/app/backend/staticfiles/;
    }
}
```

See [Production Deployment Guide](production_deployment.md) for complete production setup instructions.

## 🖥️ Platform-Specific Setup

### Windows Setup

#### Option 1: Python Script (Recommended)
```cmd
# Use Command Prompt or PowerShell
python setup.py
```

#### Option 2: PowerShell Script
```powershell
# Enhanced PowerShell script with parameters
.\setup.ps1
.\setup.ps1 -Backend
.\setup.ps1 -Frontend
.\setup.ps1 -Help
```

#### Option 3: Manual Windows Setup
```cmd
# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver

# Frontend setup (new command prompt)
cd frontend
npm install
echo REACT_APP_API_BASE_URL=http://localhost:8000/api/v1 > .env.local
npm start
```

### macOS Setup

#### Option 1: Python Script (Recommended)
```bash
python setup.py
```

#### Option 2: Make Commands
```bash
# Full setup
make setup

# Individual components
make setup-backend
make setup-frontend

# Development servers
make dev           # Start both servers
make backend       # Backend only
make frontend      # Frontend only
```

#### macOS-Specific Prerequisites
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python node postgresql
```

### Linux Setup

#### Option 1: Python Script (Recommended)
```bash
python3 setup.py
```

#### Option 2: Make Commands
```bash
make setup
make dev
```

#### Linux-Specific Prerequisites
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip nodejs npm postgresql-client

# CentOS/RHEL/Fedora
sudo yum install python3 python3-pip nodejs npm postgresql

# Arch Linux
sudo pacman -S python nodejs npm postgresql
```

## 🆘 Troubleshooting

### Common Issues and Solutions

#### Python/pip Issues
```bash
# "python: command not found"
# Try python3 instead
python3 setup.py

# "pip: command not found"
python -m pip install -r requirements.txt

# Permission errors on Windows
# Run Command Prompt as Administrator

# Virtual environment activation issues on Windows
# Use: venv\Scripts\activate.bat instead of venv\Scripts\activate
```

#### Node.js/npm Issues
```bash
# "node: command not found"
# Install from nodejs.org or use package manager

# npm permission errors
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH

# Clear npm cache
npm cache clean --force
```

#### Database Issues
```bash
# SQLite permission errors
# Ensure directory is writable
chmod 755 backend/

# PostgreSQL connection errors
# Check service is running
sudo systemctl status postgresql

# Database migration errors
# Reset migrations (development only)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

#### Frontend Issues
```bash
# React startup errors
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# CORS errors
# Ensure backend CORS_ALLOWED_ORIGINS includes frontend URL
# Check .env file: CORS_ALLOWED_ORIGINS=http://localhost:3000

# API connection errors
# Verify backend is running on port 8000
curl http://localhost:8000/api/v1/accounts-receivables/
```

#### Windows-Specific Issues
```cmd
# "true is not recognized" error
# Use python setup.py instead of make commands

# Path length limitations
# Enable long paths in Windows 10/11
# Or use shorter directory paths

# PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Getting Help

1. **Check Documentation**: Review this guide and [API Reference](api_reference.md)
2. **Verify Prerequisites**: Ensure Python, Node.js are installed correctly
3. **Check Logs**: Look for error messages in terminal output
4. **Test Components**: Verify backend and frontend work independently
5. **Review Issues**: Check GitHub issues for similar problems

## ⚙️ Advanced Configuration

### Custom Database Configuration

#### PostgreSQL for Development
```bash
# Install PostgreSQL
# Ubuntu: sudo apt install postgresql postgresql-contrib
# macOS: brew install postgresql
# Windows: Download from postgresql.org

# Create development database
sudo -u postgres createdb projectmeats_dev
sudo -u postgres createuser projectmeats_dev_user
sudo -u postgres psql -c "ALTER USER projectmeats_dev_user PASSWORD 'dev_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_dev TO projectmeats_dev_user;"

# Update backend/.env
DATABASE_URL=postgresql://projectmeats_dev_user:dev_password@localhost:5432/projectmeats_dev
```

#### Redis for Caching (Optional)
```bash
# Install Redis
# Ubuntu: sudo apt install redis-server
# macOS: brew install redis
# Windows: Use Docker or WSL

# Add to backend settings
pip install django-redis

# Update backend/.env
REDIS_URL=redis://localhost:6379/1
```

### Custom Frontend Configuration

#### Environment-Specific Settings
```env
# .env.local (development)
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
REACT_APP_DEBUG=true

# .env.staging (staging)
REACT_APP_API_BASE_URL=https://staging-api.yourdomain.com/api/v1
REACT_APP_ENVIRONMENT=staging

# .env.production (production)
REACT_APP_API_BASE_URL=https://api.yourdomain.com/api/v1
REACT_APP_ENVIRONMENT=production
```

#### Performance Optimization
```json
// package.json - build optimization
{
  "scripts": {
    "build": "react-scripts build",
    "build:analyze": "npm run build && npx webpack-bundle-analyzer build/static/js/*.js"
  }
}
```

### Development Tools Configuration

#### VS Code Settings
The project includes optimized VS Code configuration:
- Open `ProjectMeats.code-workspace` for best experience
- Automatic Python/Django extension setup
- Integrated debugging configurations
- Code formatting on save

#### Git Hooks (Optional)
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Runs code formatting and tests before commits
```

### Performance Tuning

#### Backend Performance
```python
# settings.py optimizations
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'conn_max_age': 60,
        },
    }
}

# Enable query optimization
DEBUG_TOOLBAR = True  # Development only
```

#### Frontend Performance
```javascript
// Lazy loading components
const AccountsReceivablesScreen = lazy(() => import('./screens/AccountsReceivablesScreen'));

// API client optimization
axios.defaults.timeout = 10000;
axios.interceptors.response.use(response => response, error => {
  // Global error handling
});
```

---

This comprehensive setup guide covers all scenarios for getting ProjectMeats running in your environment. For additional help, see the [API Reference](api_reference.md) or create an issue on GitHub.