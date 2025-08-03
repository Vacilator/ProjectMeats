# Node.js Deployment Conflict Fix

## Problem
The ProjectMeats deployment script was failing with Node.js package conflicts when trying to deploy on servers that already had Node.js installed via NVM (Node Version Manager).

**Error Message:**
```
The following packages have unmet dependencies:
 nodejs : Conflicts: npm
 npm : Depends: node-cacache but it is not going to be installed
       ...
E: Unable to correct problems, you have held broken packages.
```

## Root Cause
The deployment script attempted to install Node.js via Ubuntu apt packages while NVM-managed Node.js was already present on the system. This created package dependency conflicts because:

1. NVM installs Node.js in user space (`/root/.nvm/versions/node/`)
2. apt packages try to install Node.js in system space (`/usr/bin/`)
3. The package manager detected conflicts between these installations

## Solution
Modified `deploy_server.sh` to intelligently detect existing Node.js installations before attempting package installation.

### Changes Made

#### 1. Node.js Detection Logic (lines 55-90)
```bash
# Check if Node.js is already available and adequate
NODE_VERSION=""
NODE_AVAILABLE=false

if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node -v 2>/dev/null || echo "")
    if [[ "$NODE_VERSION" =~ ^v([0-9]+) ]]; then
        NODE_MAJOR=${BASH_REMATCH[1]}
        if [ "$NODE_MAJOR" -ge 16 ]; then
            NODE_AVAILABLE=true
            log_info "Found adequate Node.js version: $NODE_VERSION"
        fi
    fi
fi

if [ "$NODE_AVAILABLE" = false ]; then
    # Install Node.js via apt (original behavior)
else
    # Use existing installation
    log_info "Using existing Node.js installation: $NODE_VERSION"
fi
```

#### 2. User Access Verification (lines 174-196)
Added logic to ensure the `projectmeats` user can access Node.js/npm with proper PATH configuration.

### Benefits
- ✅ **Prevents package conflicts** when Node.js is already installed
- ✅ **Maintains compatibility** with fresh server deployments
- ✅ **Supports multiple Node.js sources** (NVM, system packages, manual installs)
- ✅ **Version validation** ensures adequate Node.js version (>=16)
- ✅ **Graceful fallbacks** when dependencies are missing

## Usage
The fix is automatically applied when running the deployment script. No manual intervention required.

### For NVM-managed Node.js:
```bash
# The script will detect existing Node.js and skip apt installation
sudo ./deploy_server.sh
```

### For fresh servers:
```bash
# The script will install Node.js via apt packages as before
sudo ./deploy_server.sh
```

## Testing
The fix has been tested with:
- ✅ NVM-managed Node.js v18.20.8 and v20.19.4
- ✅ Frontend build process (React with TypeScript)
- ✅ Backend setup (Django with Python dependencies)
- ✅ Path accessibility for application users

## Compatibility
- **Backward Compatible**: Works with existing deployment workflows
- **Forward Compatible**: Supports future Node.js versions (>=16)
- **Multi-platform**: Works with Ubuntu 20.04+ and similar distributions

## Files Modified
- `deploy_server.sh`: Enhanced Node.js detection and installation logic
- `.gitignore`: Added patterns to exclude test artifacts

## Verification
To verify the fix works correctly:
1. Ensure Node.js is available: `node -v && npm -v`
2. Run deployment: `sudo ./deploy_server.sh`
3. Check logs for "Using existing Node.js installation" message