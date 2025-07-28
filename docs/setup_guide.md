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
- **Python 3.9+** - [Download from python.org](https://python.org) (⚠️ **Python 3.13+ Windows users**: See [Python 3.13+ Setup Guide](../PYTHON_3_13_SETUP.md) for PostgreSQL compatibility issues)
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
venv\\Scripts\\activate
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
.\\setup.ps1
.\\setup.ps1 -Backend
.\\setup.ps1 -Frontend
.\\setup.ps1 -Help
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

## 🆘 Troubleshooting

### Common Issues and Solutions

#### Python 3.13+ Setup Issues (Windows)
```bash
# Error: Microsoft Visual C++ 14.0 or greater is required
# Solution 1: Use development requirements (recommended)
cd backend
pip install -r requirements-dev.txt

# Solution 2: Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Solution 3: Use SQLite for development (no PostgreSQL)
# Remove psycopg line from requirements.txt and run setup normally
```

See **[Python 3.13+ Setup Guide](../PYTHON_3_13_SETUP.md)** for detailed solutions.

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
# Use: venv\\Scripts\\activate.bat instead of venv\\Scripts\\activate
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

---

This comprehensive setup guide covers all scenarios for getting ProjectMeats running in your environment. For additional help, see the [API Reference](api_reference.md) or create an issue on GitHub.