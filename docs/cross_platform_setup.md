# ProjectMeats Cross-Platform Setup Guide

This guide provides comprehensive setup instructions for ProjectMeats on Windows, macOS, and Linux systems with troubleshooting for common CLI errors.

## 🚀 Quick Start (Recommended)

### Universal Setup - Works on All Platforms

The easiest way to set up ProjectMeats is using our cross-platform Python script:

```bash
# Full setup (backend + frontend)
python setup.py

# Backend only
python setup.py --backend

# Frontend only
python setup.py --frontend

# Show help
python setup.py --help
```

This script automatically:
- ✅ Detects your operating system
- ✅ Checks for required dependencies
- ✅ Provides clear error messages
- ✅ Handles file operations correctly across platforms
- ✅ Creates environment files
- ✅ Installs dependencies
- ✅ Runs database migrations

## 📋 Prerequisites

Before running any setup, ensure you have:

### Required
- **Python 3.9+** - [Download from python.org](https://python.org)
- **Node.js 16+** - [Download from nodejs.org](https://nodejs.org)
- **npm** (comes with Node.js)
- **pip** (comes with Python)

### Optional
- **Git** - For version control
- **PostgreSQL 12+** - For production (SQLite used for development)

## 🖥️ Platform-Specific Instructions

### Windows Setup

#### Option 1: Python Script (Recommended)
```powershell
python setup.py
```

#### Option 2: PowerShell Script
```powershell
.\setup.ps1
```

#### Option 3: Manual Setup
```powershell
# Backend
cd backend
copy .env.example .env
pip install -r requirements.txt
python manage.py migrate
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### macOS/Linux Setup

#### Option 1: Python Script (Recommended)
```bash
python setup.py
```

#### Option 2: Make Commands
```bash
make setup
# or
make setup-python
```

#### Option 3: Manual Setup
```bash
# Backend
cd backend
cp .env.example .env
pip install -r requirements.txt
python manage.py migrate
cd ..

# Frontend
cd frontend
npm install
cd ..
```

## 🔧 Development Commands

### Starting the Application

#### All Platforms (Python script)
```bash
# Backend (in one terminal)
cd backend && python manage.py runserver

# Frontend (in another terminal)  
cd frontend && npm start
```

#### Unix/Linux/macOS (Make commands)
```bash
# Start both servers simultaneously
make dev

# Or start individually
make backend    # Start Django server
make frontend   # Start React server
```

#### Windows (PowerShell aliases - optional)
```powershell
# Set up aliases for convenience
Set-Alias pm-backend "cd backend && python manage.py runserver"
Set-Alias pm-frontend "cd frontend && npm start"

# Use the aliases
pm-backend
pm-frontend
```

### Other Development Commands

#### Unix/Linux/macOS
```bash
make test           # Run all tests
make migrate        # Run database migrations
make migrations     # Create new migrations
make shell          # Open Django shell
make docs           # Generate API documentation
make clean          # Clean build artifacts
make lint           # Lint code
make format         # Format code
```

#### All Platforms (Direct commands)
```bash
# Backend tests
cd backend && python manage.py test

# Frontend tests
cd frontend && npm test

# Database migrations
cd backend && python manage.py migrate

# Create migrations
cd backend && python manage.py makemigrations

# Django shell
cd backend && python manage.py shell

# Generate API docs
cd backend && python manage.py spectacular --file ../docs/api_schema.yml
```

## 🐛 Troubleshooting Common CLI Errors

### Windows-Specific Issues

#### Error: "'true' is not recognized as an internal or external command"
**Problem**: Using Unix commands on Windows
```
cd backend && cp -n .env.example .env 2>/dev/null || true
The system cannot find the path specified.
'true' is not recognized as an internal or external command
```

**Solutions**:
1. Use the Python setup script: `python setup.py`
2. Use the PowerShell script: `.\setup.ps1`
3. Avoid using `make` commands on Windows

#### Error: "cp: command not found"
**Problem**: `cp` is a Unix command, not available on Windows CMD/PowerShell

**Solutions**:
1. Use `copy` instead of `cp` in PowerShell
2. Use the cross-platform Python script
3. Install Git Bash or WSL for Unix-like commands

#### Error: "make: command not found"
**Problem**: Make is not installed on Windows by default

**Solutions**:
1. Install make via Chocolatey: `choco install make`
2. Use the Python setup script instead
3. Use the PowerShell script
4. Run commands manually

### Cross-Platform Issues

#### Error: "python: command not found"
**Problem**: Python not installed or not in PATH

**Solutions**:
1. Install Python from [python.org](https://python.org)
2. Try `python3` instead of `python`
3. Add Python to your system PATH
4. Use the full path to Python executable

#### Error: "node: command not found" or "npm: command not found"
**Problem**: Node.js not installed or not in PATH

**Solutions**:
1. Install Node.js from [nodejs.org](https://nodejs.org)
2. Restart your terminal after installation
3. Add Node.js to your system PATH

#### Error: "pip: command not found"
**Problem**: pip not installed or not in PATH

**Solutions**:
1. Reinstall Python with pip included
2. Try `pip3` instead of `pip`
3. Install pip manually: `python -m ensurepip --upgrade`

#### Error: Permission denied or Access denied
**Problem**: Insufficient permissions

**Solutions**:
1. Run terminal as administrator (Windows) or use `sudo` (Unix)
2. Change file/directory permissions
3. Use virtual environments for Python packages

### Database Issues

#### Error: "django.db.utils.OperationalError: no such table"
**Problem**: Database not migrated

**Solution**:
```bash
cd backend
python manage.py migrate
```

#### Error: "psycopg2: command not found" or PostgreSQL connection issues
**Problem**: PostgreSQL not installed or configured

**Solutions**:
1. Use SQLite for development (default in .env.example)
2. Install PostgreSQL for production
3. Update DATABASE_URL in .env file

### Frontend Issues

#### Error: "Module not found" or React app won't start
**Problem**: Node modules not installed

**Solutions**:
```bash
cd frontend
rm -rf node_modules package-lock.json  # Clean install
npm install
```

#### Error: "Port 3000 is already in use"
**Problem**: Port conflict

**Solutions**:
1. Kill the process using port 3000
2. Use a different port: `PORT=3001 npm start`
3. Restart your computer

## 🌐 Environment Configuration

### Backend Environment (.env)
```bash
# Development settings
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend Environment (.env.local)
```bash
# React environment variables
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
```

## 🔍 Verification Steps

After setup, verify everything works:

1. **Backend API**: Visit http://localhost:8000/api/docs/
2. **Frontend**: Visit http://localhost:3000
3. **Admin**: Visit http://localhost:8000/admin/ (create superuser first)

### Create Django Superuser
```bash
cd backend
python manage.py createsuperuser
```

## 📚 Additional Resources

- **[README.md](../README.md)** - Project overview
- **[SETUP_OVERVIEW.md](../SETUP_OVERVIEW.md)** - Detailed setup guide
- **[docs/backend_setup.md](backend_setup.md)** - Backend development guide
- **[docs/frontend_setup.md](frontend_setup.md)** - Frontend development guide
- **[docs/api_reference.md](api_reference.md)** - API documentation

## 🆘 Getting Help

If you're still having issues:

1. Check this troubleshooting guide
2. Review the error message carefully
3. Try the alternative setup methods
4. Check your system PATH and permissions
5. Restart your terminal/command prompt
6. Create an issue in the project repository

## 🚀 Quick Commands Summary

| Task | Windows | macOS/Linux |
|------|---------|-------------|
| Full Setup | `python setup.py` | `python setup.py` or `make setup` |
| Backend Only | `python setup.py --backend` | `python setup.py --backend` or `make setup-backend` |
| Frontend Only | `python setup.py --frontend` | `python setup.py --frontend` or `make setup-frontend` |
| Start Backend | `cd backend && python manage.py runserver` | `make backend` |
| Start Frontend | `cd frontend && npm start` | `make frontend` |
| Both Servers | Manual (2 terminals) | `make dev` |
| Run Tests | `cd backend && python manage.py test` | `make test` |

Remember: When in doubt, use `python setup.py` - it works everywhere!