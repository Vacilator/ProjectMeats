# ProjectMeats Django Service - Immediate Fix Instructions

🚨 **URGENT FIX FOR PRODUCTION SERVER** 🚨

## Problem
The ProjectMeats Django service is failing to start due to missing Python dependencies and environment configuration issues.

## Quick Fix (Run on Production Server)

### Step 1: Pull Latest Fixes
```bash
cd /opt/projectmeats
sudo git pull origin main
```

### Step 2: Run the Fix Script
```bash
sudo ./fix_django_service.sh
```

This script will:
- ✅ Install all missing Python dependencies
- ✅ Create environment file in correct location
- ✅ Set proper permissions
- ✅ Test Django configuration
- ✅ Restart the service

### Expected Output
```
🔧 ProjectMeats Django Service Quick Fix
========================================
[INFO] Step 1: Installing Python dependencies...
[SUCCESS] Dependencies installed successfully
[INFO] Step 2: Setting up environment configuration...
[SUCCESS] Environment file created at /etc/projectmeats/projectmeats.env
[INFO] Step 3: Testing Django configuration...
[SUCCESS] Django configuration is valid
[INFO] Step 4: Restarting ProjectMeats service...
[INFO] Step 5: Checking service status...
[SUCCESS] ✅ ProjectMeats Django service is now running!
[INFO] Step 6: Testing HTTP response...
[SUCCESS] ✅ Django application is responding on port 8000

🎉 Quick Fix Complete!
======================
```

## Verification Commands

### Check Service Status
```bash
sudo systemctl status projectmeats
```
Should show: `Active: active (running)`

### Check Application Response
```bash
curl -I http://127.0.0.1:8000/
```
Should return HTTP 200, 302, or 404 (not connection refused)

### View Service Logs
```bash
sudo journalctl -u projectmeats -f
```

## If Fix Script Fails

### Manual Dependency Installation
```bash
cd /opt/projectmeats
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Manual Environment Setup
```bash
sudo mkdir -p /etc/projectmeats
sudo cp deployment/env.production.template /etc/projectmeats/projectmeats.env
sudo chown www-data:www-data /etc/projectmeats/projectmeats.env
sudo chmod 640 /etc/projectmeats/projectmeats.env
```

### Manual Service Restart
```bash
sudo systemctl daemon-reload
sudo systemctl restart projectmeats
```

## Alternative: Use Enhanced Quick Setup
If the fix script doesn't work, try the updated quick setup script:

```bash
sudo ./deployment/scripts/quick_server_fix.sh
```

## Root Cause
The original issue was:
1. Missing Python dependencies (`dj_database_url`, `django`, etc.)
2. Environment file in wrong location (systemd expected `/etc/projectmeats/projectmeats.env`)
3. No dependency verification during deployment

## Prevention
Future deployments will automatically:
- ✅ Install all dependencies with verification
- ✅ Create environment files in correct locations
- ✅ Test Django configuration before starting service
- ✅ Use multiple fallback paths for environment files

## Support
If issues persist:
1. Run the dependency verification script: `./verify_dependencies.sh`
2. Check the comprehensive documentation: `DJANGO_SERVICE_FIX.md`
3. Review service logs: `sudo journalctl -u projectmeats -n 50`

---
**This fix resolves the immediate production issue. The service should be running within 2-3 minutes of running the fix script.**