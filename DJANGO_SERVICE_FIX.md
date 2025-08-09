# Django Service Fix Documentation

## Problem Summary

The ProjectMeats Django service was failing to start with the following error:
```
Process: 61482 ExecStart=/opt/projectmeats/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 3 --worker-class gthread --threads 2 --worker-connections 1000 --max-requests 1000 --max-requests-jitter 100 --preload --access-logfile /var/log/projectmeats/access.log --error-logfile /var/log/projectmeats/error.log --log-level info --pid /var/run/projectmeats/gunicorn.pid projectmeats.wsgi:application (code=exited, status=1/FAILURE)
```

## Root Cause Analysis

The service failure was caused by two main issues:

1. **Missing Python Dependencies**: The production server was missing required Python packages like `dj_database_url`, `django`, and other dependencies required by the Django application.

2. **Environment File Path Mismatch**: The systemd service was looking for the environment file at `/etc/projectmeats/projectmeats.env` but the deployment scripts were creating it at `/opt/projectmeats/.env.production`.

## Fix Implementation

### 1. Quick Fix Script (`fix_django_service.sh`)

Created an immediate fix script that:
- Installs missing Python dependencies in the virtual environment
- Creates the environment file in the correct location (`/etc/projectmeats/projectmeats.env`)
- Sets proper permissions
- Tests Django configuration
- Restarts the service

**Usage**: 
```bash
sudo ./fix_django_service.sh
```

### 2. Systemd Service Configuration Update

Updated `deployment/systemd/projectmeats.service` to:
- Use multiple environment file paths with fallback: `/etc/projectmeats/projectmeats.env` (primary) and `/opt/projectmeats/.env.production` (fallback)
- Added the `-` prefix to make environment files optional (non-fatal if missing)

### 3. Production Setup Script Improvements

Updated `deployment/scripts/setup_production.sh` to:
- Create environment file in the systemd-expected location (`/etc/projectmeats/projectmeats.env`)
- Add dependency verification steps
- Test Django configuration during setup
- Set proper file permissions
- Create backup copy in project directory

### 4. Dependency Verification Script (`verify_dependencies.sh`)

Created a standalone verification script that:
- Checks virtual environment setup
- Verifies all critical Python packages are installed
- Tests Django configuration and WSGI application
- Provides detailed error reporting

## Prevention Measures

The fixes implement the following prevention measures:

1. **Multiple Environment File Paths**: The systemd service now checks multiple locations for environment files
2. **Dependency Verification**: Setup scripts now verify dependencies are properly installed
3. **Configuration Testing**: Django configuration is tested during deployment
4. **Better Error Handling**: Scripts provide better error messages and diagnostics

## Usage Instructions

### For Immediate Fix (Production Server)
```bash
sudo ./fix_django_service.sh
```

### For New Deployments
The updated setup script will handle everything correctly:
```bash
sudo ./deployment/scripts/setup_production.sh
```

### For Dependency Verification
```bash
./verify_dependencies.sh [project_directory]
```

## Service Management Commands

After the fix, use these commands to manage the service:

```bash
# Check service status
sudo systemctl status projectmeats

# View service logs
sudo journalctl -u projectmeats -f

# Restart service
sudo systemctl restart projectmeats

# Check if service is running
sudo systemctl is-active projectmeats
```

## Environment File Location

The service now supports environment files in these locations (in order of preference):
1. `/etc/projectmeats/projectmeats.env` (primary, created by deployment scripts)
2. `/opt/projectmeats/.env.production` (fallback, for backward compatibility)

## Files Modified

- `deployment/systemd/projectmeats.service` - Updated environment file paths
- `deployment/scripts/setup_production.sh` - Enhanced with dependency verification and correct environment file creation
- `fix_django_service.sh` - New quick fix script
- `verify_dependencies.sh` - New dependency verification script
- `DJANGO_SERVICE_FIX.md` - This documentation

This fix resolves the immediate service failure while implementing robust prevention measures for future deployments.