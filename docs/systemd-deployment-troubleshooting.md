# SystemD Deployment Troubleshooting Guide

## Common SystemD Deployment Errors

### Error: Exit Code 127 (Command Not Found)
**Symptom**: `mkdir: command not found` in pre_start_service.sh line 12

**Root Cause**: SystemD has a limited PATH environment that may not include `/bin` or `/usr/bin`

**Solution Applied**:
- Updated `deployment/scripts/pre_start_service.sh` to use full paths:
  - `mkdir` → `/bin/mkdir`
  - `chown` → `/bin/chown` 
  - `chmod` → `/bin/chmod`
  - `touch` → `/bin/touch`

**Verification**:
```bash
bash -n deployment/scripts/pre_start_service.sh
```

### Error: Exit Code 2 (Invalid Argument) 
**Symptom**: Permission denied in ExecStopPost for `/var/log/projectmeats/post_failure.log`

**Root Cause**: ExecStopPost tries to write to log file without checking permissions

**Solution Applied**:
- Updated `deployment/systemd/projectmeats.service` ExecStopPost to check permissions:
```ini
ExecStopPost=/bin/sh -c 'if [ -w /var/log/projectmeats/post_failure.log ]; then journalctl -u projectmeats.service -n 50 >> /var/log/projectmeats/post_failure.log; fi'
```

### Error: Bash Syntax Error in Environment File
**Symptom**: `SECRET_KEY with unescaped special characters like parentheses, breaking bash sourcing`

**Root Cause**: Django's `get_random_secret_key()` generates characters like `()$` that break bash parsing

**Solutions Applied**:
1. **Updated SECRET_KEY generation** to use only safe characters:
   ```python
   ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#%^&*-_=+'))
   ```

2. **Added proper quoting** in environment templates:
   ```bash
   SECRET_KEY="value"
   DATABASE_URL="postgres://user:pass@host/db"
   ```

3. **Enhanced sed replacement** to handle quoted values:
   ```bash
   sed -i 's|"temp-key-change-me"|"'"$SECRET_KEY"'"|' /etc/projectmeats/projectmeats.env
   ```

**Verification**:
```bash
bash -n /etc/projectmeats/projectmeats.env
```

### Error: PATH Not Found in SystemD
**Symptom**: Commands fail in systemd context even with full paths

**Root Cause**: SystemD service had incomplete PATH environment

**Solution Applied**:
- Updated `deployment/systemd/projectmeats.service`:
```ini
Environment=PATH=/usr/bin:/bin:/usr/sbin:/sbin:/opt/projectmeats/venv/bin
```

## Validation Commands

### Test Environment File Generation
```bash
# Generate test environment file
SECRET_KEY=$(python3 -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#%^&*-_=+') for _ in range(50)))")
cat > /tmp/test.env << EOF
SECRET_KEY="$SECRET_KEY"
DEBUG=False
EOF

# Validate syntax and sourcing
bash -n /tmp/test.env && echo "Valid"
source /tmp/test.env && echo "Sources correctly"
```

### Test Pre-Start Script
```bash
# Verify script syntax
bash -n deployment/scripts/pre_start_service.sh

# Test commands exist
/bin/mkdir --version
/bin/chown --version  
/bin/chmod --version
/bin/touch --version
```

### Test SystemD Service Configuration  
```bash
# Check service file
systemd-analyze verify deployment/systemd/projectmeats.service

# Verify PATH setting
grep "Environment=PATH=" deployment/systemd/projectmeats.service

# Verify permission check
grep "if \[ -w.*post_failure.log \]" deployment/systemd/projectmeats.service
```

## Files Modified
- `deploy_production.py` - Safe SECRET_KEY generation
- `deployment/scripts/pre_start_service.sh` - Full command paths
- `deployment/systemd/projectmeats.service` - Enhanced PATH and ExecStopPost
- `deployment/scripts/setup_production.sh` - Safe key generation and quoting
- `deployment/scripts/quick_server_fix.sh` - Same improvements
- `deployment/config/projectmeats.env.template` - Proper value quoting
- `apply_deployment_fixes.sh` - Improved key generation

## Prevention
- Always quote environment variable values
- Use full command paths in SystemD scripts
- Test environment files with `bash -n` before deployment
- Use character sets that don't require escaping in shell contexts
- Include comprehensive PATH in SystemD service files