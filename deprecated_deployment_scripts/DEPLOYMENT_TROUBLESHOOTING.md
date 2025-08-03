# ProjectMeats Deployment Troubleshooting Guide

## Overview

This guide addresses the deployment issues reported in the error log and provides solutions implemented in PR #71.

## Error Summary

The deployment failures included:

1. **PostgreSQL Permission Denied**
   ```
   could not change directory to "/root/ProjectMeats_backup_CLOSE": Permission denied
   ```

2. **Git Clone Directory Conflicts**
   ```
   fatal: destination path '.' already exists and is not an empty directory
   ```

3. **Download Validation Failures**
   ```
   End-of-central-directory signature not found
   unzip: cannot find zipfile directory
   ```

## Solutions Implemented (PR #71)

### 1. PostgreSQL Permission Fix

**Problem**: PostgreSQL commands failed when run from directories the `postgres` user couldn't access.

**Solution**: All PostgreSQL commands now run with `cd /tmp &&` prefix:

```python
# Before (failing)
f"sudo -u postgres createdb projectmeats || true"

# After (working)
f"cd /tmp && sudo -u postgres createdb projectmeats || true"
```

### 2. Directory Conflict Handling

**Problem**: Git clone failed when target directory already contained files.

**Solution**: Detect existing content and create timestamped backups:

```python
# Check for existing content
result = self.run_command(f"ls -la {self.config['project_dir']}", capture_output=True)
if result and len(result.strip().split('\n')) > 3:
    # Create backup
    backup_dir = f"{self.config['project_dir']}_backup_{int(time.time())}"
    self.run_command(f"mv {self.config['project_dir']} {backup_dir}")
    self.run_command(f"mkdir -p {self.config['project_dir']}")
```

### 3. Download Validation

**Problem**: Failed downloads (404 responses) were treated as valid zip files.

**Solution**: Validate download size and file type before extraction:

```python
# Size validation
zip_size = self.run_command(f"stat -c%s {project_dir}/project.zip", capture_output=True)
if int(zip_size) < 1000:  # Less than 1KB indicates error response
    raise Exception(f"Download failed - file too small ({zip_size} bytes)")

# File type validation
file_result = self.run_command(f"file project.zip", capture_output=True)
if "zip" not in file_result.lower():
    raise Exception("Downloaded file is not a valid zip archive")
```

### 4. Additional Improvements

- Added tarball download as fallback method
- Enhanced error handling and logging
- Interactive confirmation for directory backups
- Better fallback mechanisms

## Verification Tools

### 1. Run Fix Verification

```bash
python3 verify_deployment_fixes.py
```

This script verifies that your `master_deploy.py` contains all PR #71 fixes.

### 2. Test Deployment Environment

```bash
sudo ./verify_deployment_readiness.sh
```

This script checks that your environment has all required dependencies.

### 3. Test Fix Logic

```bash
python3 test_specific_fixes.py
```

This script simulates the exact error scenarios and validates fixes.

## Troubleshooting Steps

If deployment is still failing:

1. **Verify Script Version**
   ```bash
   python3 verify_deployment_fixes.py
   ```

2. **Check Environment**
   ```bash
   sudo ./verify_deployment_readiness.sh
   ```

3. **Test Network Connectivity**
   ```bash
   curl -I https://github.com/Vacilator/ProjectMeats
   ```

4. **Clean Previous Attempts**
   ```bash
   # Remove any failed deployment directories
   sudo rm -rf /opt/projectmeats*
   ```

5. **Run Deployment in Clean Environment**
   ```bash
   cd /tmp
   sudo python3 /path/to/master_deploy.py
   ```

## Expected Behavior After Fixes

1. **PostgreSQL commands** will work from any directory by running from `/tmp`
2. **Existing directories** will be automatically backed up and cleaned
3. **Invalid downloads** will be detected and rejected before extraction
4. **Multiple fallback methods** will be attempted if primary download fails

## Testing Results

All validation tests pass:
- ✅ PostgreSQL permission fix validated
- ✅ Directory backup logic validated  
- ✅ Download validation logic validated
- ✅ All PR #71 fixes present in current script

The deployment script should now handle all the reported error scenarios correctly.