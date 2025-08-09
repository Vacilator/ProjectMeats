# ProjectMeats Deployment Scripts

This directory contains deployment scripts for ProjectMeats application.

## Quick Server Fix Script

The `quick_server_fix.sh` script is designed for rapid deployment on existing servers.

### Recent Fixes Applied

**Issue**: SystemD service failed with "unavailable resources or another system error"

**Root Causes Identified:**
1. Environment file created in wrong location (`.env.production` vs `/etc/projectmeats/projectmeats.env`)
2. Missing `/etc/projectmeats/` directory
3. Insufficient error handling when systemd service fails
4. Missing permission settings for environment file

**Fixes Applied:**
1. **Environment File Location**: Script now creates environment file at `/etc/projectmeats/projectmeats.env` as expected by systemd service
2. **Directory Creation**: Added creation of `/etc/projectmeats/` directory
3. **Permission Management**: Set proper permissions on environment file (640, root:www-data)
4. **Enhanced Error Handling**: Added detailed diagnostics when systemd service fails to start
5. **File Verification**: Added checks for critical files (gunicorn, wsgi.py, environment file)
6. **WSGI Configuration**: Updated `wsgi.py` to properly respect `DJANGO_SETTINGS_MODULE` environment variable

### Usage

```bash
# Run as root on the target server
sudo bash /opt/projectmeats/deployment/scripts/quick_server_fix.sh
```

### Verification

After running the deployment script, use the verification script to check status:

```bash
sudo bash /opt/projectmeats/deployment/scripts/verify_deployment.sh
```

### Troubleshooting

If services fail to start:

1. **Check SystemD service status:**
   ```bash
   sudo systemctl status projectmeats
   sudo journalctl -u projectmeats -n 20
   ```

2. **Verify critical files exist:**
   ```bash
   ls -la /etc/projectmeats/projectmeats.env
   ls -la /opt/projectmeats/venv/bin/gunicorn
   ls -la /opt/projectmeats/backend/projectmeats/wsgi.py
   ```

3. **Check permissions:**
   ```bash
   sudo chown -R www-data:www-data /var/log/projectmeats /var/run/projectmeats
   sudo chown -R www-data:www-data /opt/projectmeats
   sudo chown root:www-data /etc/projectmeats/projectmeats.env
   sudo chmod 640 /etc/projectmeats/projectmeats.env
   ```

4. **Restart services manually:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart projectmeats
   sudo systemctl restart nginx
   ```

### Files Modified

- `quick_server_fix.sh`: Enhanced with better error handling and correct file paths
- `verify_deployment.sh`: New verification script for post-deployment validation
- `../systemd/projectmeats.service`: SystemD service configuration (unchanged but validated)
- `../../backend/projectmeats/wsgi.py`: Updated to respect environment settings properly

## Other Scripts

- `setup_production.sh`: Full production setup script
- `deploy.sh`: General deployment script
- `verify.sh`: General verification script

All scripts have been updated to align with the fixes applied to the quick server fix script.