# ProjectMeats Service Startup Fix - Enhanced Diagnostics and Fallback Implementation

## Overview

This document describes the enhanced fixes implemented to resolve the persistent ProjectMeats Django service startup failures. The solution addresses root causes through systematic diagnostics, service configuration refinements, and robust fallback mechanisms.

## Problem Summary

The ProjectMeats Django service was experiencing persistent startup failures with "control process exited with error code" despite successful completion of prior deployment steps (venv setup, migrations, collectstatic). Analysis revealed multiple contributing factors:

1. **Inadequate Error Diagnostics**: Scripts didn't capture detailed Gunicorn startup errors
2. **Service Configuration Inconsistencies**: Multiple systemd configurations with conflicting user/group settings
3. **Environment File Path Confusion**: Inconsistent environment file locations across services
4. **Permission Issues**: Mixed user/group ownership causing access failures
5. **Dependency Version Problems**: Potentially incompatible Gunicorn version

## Implemented Solutions

### 1. Enhanced Diagnostic Agent ✅ (High Priority)

#### New Diagnostic Script: `deployment/scripts/diagnose_service.sh`

**Features:**
- **Comprehensive Service Status**: Captures systemctl status and journalctl output automatically
- **Direct Gunicorn Testing**: Tests Gunicorn execution outside systemd for isolation
- **Dependency Verification**: Checks for missing Python packages and installs them
- **Permission Validation**: Verifies file/directory access rights
- **Error Analysis**: Parses common error patterns with suggested solutions
- **Detailed Logging**: All output saved to `/var/log/projectmeats/deployment_errors.log`

**Usage:**
```bash
sudo deployment/scripts/diagnose_service.sh [project_directory]
sudo deployment/scripts/diagnose_service.sh --fix  # Future: auto-fix mode
```

#### Integration with Existing Scripts

**Updated `deployment/scripts/quick_server_fix.sh`:**
- Automatically runs diagnostics on service start failure
- Captures detailed error logs for troubleshooting
- Enhanced error reporting with specific file checks

### 2. Systemd Service Refinement ✅ (High Priority)

#### Standardized Service Configuration

**Unified User/Group Model:**
- **User**: `projectmeats` (dedicated service user)
- **Group**: `www-data` (for web server compatibility)
- **Consistent across all service variants**

**Fixed Service Files:**

1. **`projectmeats.service`** (TCP-based, primary)
   - Added `RuntimeDirectory=projectmeats`
   - Multiple environment file fallbacks
   - Enhanced security settings

2. **`projectmeats-socket.service`** (Socket-based)
   - Consistent user/group with TCP variant
   - Fixed environment file paths

3. **`projectmeats-port.service`** (NEW: Fallback service)
   - Direct port binding without socket activation
   - Used when socket activation fails

#### Environment File Standardization

**Priority Order:**
1. `/etc/projectmeats/projectmeats.env` (Primary - created by deployment scripts)
2. `/opt/projectmeats/.env.production` (Fallback - backward compatibility)
3. `/opt/projectmeats/backend/.env` (Additional fallback)

### 3. Dependency and Version Control ✅ (Medium Priority)

#### Fixed Gunicorn Version

**Changed in `backend/requirements.txt`:**
```
# Before
gunicorn==23.0.0

# After  
gunicorn==20.0.4
```

**Benefits:**
- Resolves compatibility issues with Python 3.12+
- More stable service startup behavior
- Proven compatibility with Django 4.2.7

#### Enhanced Dependency Management

**Features:**
- Automatic missing package detection and installation
- Pre-deployment dependency verification
- Error checking during pip install operations

### 4. Permission and Ownership Fix ✅ (Medium Priority)

#### New Permission Management Script: `deployment/scripts/fix_permissions.sh`

**Key Features:**
- **User Creation**: Creates `projectmeats` system user if needed
- **Consistent Ownership**: `projectmeats:www-data` across all components
- **Proper Directory Permissions**: 755 for directories, 775 for writable areas
- **Secure Environment Files**: 640 permissions for sensitive configuration
- **Verification Testing**: Validates permissions work correctly

**Directories Managed:**
- `/opt/projectmeats` (project files)
- `/var/log/projectmeats` (logs)
- `/var/run/projectmeats` (runtime files)
- `/etc/projectmeats` (configuration)

### 5. Fallback and Manual Setup ✅ (Medium Priority)

#### Multi-Stage Fallback Logic in `production_deploy.sh`

**Fallback Sequence:**
1. **Primary Service**: Try standard TCP-based service
2. **Socket Activation**: Attempt socket-based service if available
3. **Port-Based Fallback**: Use direct port binding service
4. **Manual Intervention**: Detailed troubleshooting guidance

**Manual Recovery Instructions:**

```bash
# Check service status
sudo systemctl status projectmeats
sudo journalctl -xeu projectmeats -n 50

# Run diagnostics
sudo deployment/scripts/diagnose_service.sh

# Fix permissions
sudo deployment/scripts/fix_permissions.sh

# Test manual Gunicorn start
cd /opt/projectmeats/backend
source ../venv/bin/activate
./venv/bin/gunicorn --bind 127.0.0.1:8000 projectmeats.wsgi:application
```

### 6. Testing and Validation ✅ (Low Priority)

#### New Test Suite: `deployment/scripts/test_service_start.sh`

**Test Coverage:**
- Django configuration validation
- WSGI application import testing
- Gunicorn startup simulation (both socket and TCP)
- Systemd service file syntax validation
- Permission simulation
- Dependency verification

**Usage:**
```bash
./deployment/scripts/test_service_start.sh [project_directory]
```

## Usage Instructions

### For Immediate Production Fix

1. **Run Enhanced Diagnostics:**
   ```bash
   sudo deployment/scripts/diagnose_service.sh
   ```

2. **Fix Permissions:**
   ```bash
   sudo deployment/scripts/fix_permissions.sh
   ```

3. **Deploy with Fallback:**
   ```bash
   sudo ./production_deploy.sh
   ```

### For New Deployments

The enhanced `production_deploy.sh` automatically:
- Tests primary service configuration
- Attempts socket activation if primary fails
- Falls back to port-based service if needed
- Captures detailed error logs throughout

### For Development Testing

```bash
# Test configuration before deployment
./deployment/scripts/test_service_start.sh

# Check specific aspects
sudo deployment/scripts/diagnose_service.sh --fix
```

## Files Modified/Created

### New Files:
- `deployment/scripts/diagnose_service.sh` - Enhanced diagnostic capabilities
- `deployment/scripts/fix_permissions.sh` - Permission management
- `deployment/scripts/test_service_start.sh` - Service startup testing
- `deployment/systemd/projectmeats-port.service` - Fallback service configuration

### Modified Files:
- `backend/requirements.txt` - Fixed Gunicorn version
- `deployment/systemd/projectmeats.service` - Enhanced configuration
- `deployment/systemd/projectmeats-socket.service` - Standardized user/group
- `deployment/systemd/projectmeats.socket` - Fixed permissions
- `deployment/scripts/quick_server_fix.sh` - Integrated diagnostics
- `production_deploy.sh` - Added fallback logic

## Expected Outcomes

1. **Improved Diagnosis**: Detailed error logs capture exact failure reasons
2. **Consistent Service Configuration**: Standardized user/group and paths
3. **Automatic Fallbacks**: Multiple service variants tried automatically
4. **Enhanced Reliability**: Better error handling and recovery mechanisms
5. **Easy Troubleshooting**: Clear diagnostic output and manual intervention steps

## Monitoring and Maintenance

### Log Files:
- `/var/log/projectmeats/deployment_errors.log` - Deployment and diagnostic logs
- `/var/log/projectmeats/error.log` - Gunicorn error logs
- `/var/log/projectmeats/access.log` - Gunicorn access logs

### Status Commands:
```bash
# Service status
sudo systemctl status projectmeats

# Recent logs
sudo journalctl -xeu projectmeats -f

# Run diagnostics
sudo deployment/scripts/diagnose_service.sh

# Fix permissions if needed
sudo deployment/scripts/fix_permissions.sh
```

This implementation provides a systematic approach to resolving service startup failures while maintaining backward compatibility and providing robust fallback mechanisms.