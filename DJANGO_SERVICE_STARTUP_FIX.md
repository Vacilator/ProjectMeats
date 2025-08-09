# Django Service Startup Fix

## Problem
The ProjectMeats Django service was failing to start via systemd with the following error:
```
Active: activating (auto-restart) (Result: exit-code) since Sat 2025-08-09 12:58:09 UTC; 2s ago
Process: 65250 ExecStart=/opt/projectmeats/venv/bin/gunicorn ... (code=exited, status=1/FAILURE)
```

## Root Cause
The systemd service was configured to write log files and PID files to specific directories:
- `/var/log/projectmeats/access.log` - Access log file
- `/var/log/projectmeats/error.log` - Error log file  
- `/var/run/projectmeats/gunicorn.pid` - PID file

However, these directories were not being created by the `fix_django_service.sh` script, causing Gunicorn to fail during startup when trying to create these files.

## Solution
Updated the `fix_django_service.sh` script to:

1. **Create required directories:**
   ```bash
   mkdir -p /var/log/projectmeats
   mkdir -p /var/run/projectmeats
   mkdir -p /opt/projectmeats/backend/media
   ```

2. **Set proper ownership:**
   ```bash
   chown www-data:www-data /var/log/projectmeats
   chown www-data:www-data /var/run/projectmeats
   chown www-data:www-data /opt/projectmeats/backend/media
   ```

3. **Set appropriate permissions:**
   ```bash
   chmod 755 /var/log/projectmeats
   chmod 755 /var/run/projectmeats
   chmod 755 /opt/projectmeats/backend/media
   ```

## Files Modified
- `fix_django_service.sh` - Added Step 4 to create directories and set permissions

## Validation
The fix has been validated with a comprehensive test script (`test_django_service_fix.sh`) that verifies:
- Django configuration works with production settings
- WSGI module loads correctly
- Gunicorn starts successfully with proper log/PID directories
- Log files are created as expected
- Systemd service configuration is valid
- Deployment script creates required directories with proper permissions

## Consistency
This fix makes the `fix_django_service.sh` script consistent with the main `deployment/scripts/quick_server_fix.sh` script, which already included directory creation and permission setup.

## Testing
Run the validation test to confirm the fix works:
```bash
chmod +x test_django_service_fix.sh
./test_django_service_fix.sh
```

All tests should pass, confirming the Django service startup issue is resolved.