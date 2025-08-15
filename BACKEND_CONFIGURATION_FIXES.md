# ProjectMeats Backend Configuration Fixes

This document describes the fixes applied to resolve persistent backend configuration failures, including:

- Permission denied errors when Gunicorn attempts to write to `/var/log/projectmeats/error.log`
- Syntax errors in `/etc/projectmeats/projectmeats.env` (e.g., `SECRET_KEY==...` with an extra '=')
- Faulty dependency checks in diagnostics reporting packages as missing when they're installed
- Suboptimal systemd service configuration

## Applied Fixes

### 1. Environment File Generation Fix

**Problem**: Environment files were generated with syntax errors due to improper quoting and special characters in SECRET_KEY values.

**Solution**: 
- Added proper quoting around SECRET_KEY values: `SECRET_KEY='$SECRET_KEY'`
- Added environment file syntax validation using `bash -n`
- Enhanced error handling for special characters in sed replacements

**Files Modified**:
- `enhanced_django_service_fix.sh`
- `production_deploy.sh` 
- `deployment/scripts/setup_production.sh`

### 2. Log File Permissions Fix

**Problem**: Gunicorn service failed because the `projectmeats` user couldn't write to log files owned by `www-data`.

**Solution**:
- Changed log directory ownership from `www-data:www-data` to `projectmeats:www-data`
- Pre-create log files with proper permissions before service starts
- Added pre-start script (`pre_start_service.sh`) to ensure permissions are set
- Set directory permissions to 775 and file permissions to 664

**Files Modified**:
- `enhanced_django_service_fix.sh`
- `deployment/scripts/fix_permissions.sh`
- Created: `deployment/scripts/pre_start_service.sh`

### 3. Package Detection Fix

**Problem**: Diagnostic script incorrectly reported `djangorestframework` as missing due to import name mismatch.

**Solution**:
- Fixed package import mappings: `djangorestframework` → `rest_framework`
- Added double-checking with `pip show` command for accuracy
- Enhanced logging with full pip list, gunicorn version, and Python site info

**Files Modified**:
- `deployment/scripts/diagnose_service.sh`

### 4. Systemd Service Optimization

**Problem**: Service configuration was suboptimal for error handling and debugging.

**Solution**:
- Added `ExecStartPre` to run permission fixes before service starts
- Added `ExecStopPost` to capture failure logs to `/var/log/projectmeats/post_failure.log`
- Reduced `RestartSec` from 10s to 5s for faster recovery
- Added `SuccessExitStatus=0 1` for graceful exit handling
- Enhanced journalctl capture in diagnostic scripts

**Files Modified**:
- `deployment/systemd/projectmeats.service`
- `deployment/systemd/projectmeats-socket.service`

## Quick Application

### Apply All Fixes
```bash
sudo ./apply_deployment_fixes.sh
```

### Test Fixes
```bash
./test_deployment_fixes.sh
```

### Run Enhanced Deployment
```bash
sudo ./enhanced_django_service_fix.sh
```

## Docker Alternative (Recommended Fallback)

If bare-metal deployment issues persist, use the enhanced Docker Compose setup:

### Setup Docker Production
```bash
# Copy environment template
cp .env.prod.example .env.prod

# Edit with your values
nano .env.prod

# Deploy with Docker
docker compose -f docker-compose.prod.yml up -d
```

### Docker Enhancements Made
- Added proper gunicorn configuration with logging
- Volume-mounted log paths for persistence
- User-specific execution context
- Enhanced healthcheck with `--fail` flag
- Environment file support (`.env.prod`)

## Validation Commands

### Check Service Status
```bash
systemctl status projectmeats
journalctl -fu projectmeats
```

### Validate Environment File
```bash
bash -n /etc/projectmeats/projectmeats.env
```

### Check Log Permissions
```bash
ls -la /var/log/projectmeats/
```

### Run Diagnostics
```bash
sudo ./deployment/scripts/diagnose_service.sh
```

## Migration Path

1. **First Priority**: Apply bare-metal fixes using `apply_deployment_fixes.sh`
2. **If Issues Persist**: Migrate to Docker using `docker-compose.prod.yml`
3. **For New Deployments**: Consider Docker-first approach

## Files Created/Modified

### New Files
- `deployment/scripts/pre_start_service.sh` - Pre-start permission setup
- `apply_deployment_fixes.sh` - Comprehensive fix application
- `test_deployment_fixes.sh` - Validation testing
- `.env.prod.example` - Docker environment template
- `BACKEND_CONFIGURATION_FIXES.md` - This documentation

### Modified Files
- `enhanced_django_service_fix.sh` - Environment and permissions fixes
- `production_deploy.sh` - Environment generation fixes
- `deployment/scripts/setup_production.sh` - Sed escaping and validation
- `deployment/scripts/diagnose_service.sh` - Package detection and logging
- `deployment/systemd/projectmeats.service` - Service optimization
- `deployment/systemd/projectmeats-socket.service` - Service optimization
- `docker-compose.prod.yml` - Enhanced Docker configuration

## Risk Mitigation

- All scripts include dry-run validation modes
- Automatic backup of existing `.env` files before modification
- Comprehensive syntax validation before deployment
- Enhanced error logging for better debugging
- Fallback Docker option if bare-metal fails

## Testing

The fixes have been validated through:
- Environment file syntax validation
- Package detection logic testing
- Systemd service file validation
- Pre-start script syntax checking
- Comprehensive integration testing

For support or questions, reference the deployment logs in `/var/log/projectmeats/` and run the diagnostic script for detailed analysis.