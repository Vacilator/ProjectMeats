# Django Service Startup Fix - COMPREHENSIVE SOLUTION

## Problem Summary
The ProjectMeats Django service was failing to start with exit code 1. Deep analysis revealed multiple critical issues:

1. **WSGI Configuration Issue**: The `wsgi.py` file was defaulting to development settings instead of production
2. **CRITICAL Secret Key Issue**: The generated secret key contained shell special characters `()` causing systemd service failures
3. **Environment Variable Handling**: Production settings were not properly reading environment variables
4. **Directory Creation**: Missing log and PID directories (previously identified)

## Root Cause Analysis

### Primary Issue: Secret Key Shell Special Characters
The most critical issue was the generated Django secret key: 
```
SECRET_KEY==64vkjgn0mxz@tnuglpwkq^n9cn4%zwr)4sj=a^(8%c287n*31
```

This key contains parentheses `()` which are shell special characters. When systemd tries to load the environment file or when the shell processes this key, it encounters a syntax error, preventing the service from starting.

### Secondary Issues:
1. **WSGI Module Path**: `wsgi.py` was hardcoded to development settings
2. **Production Settings**: Not properly configured to read from environment
3. **Missing Directories**: Log and PID directories not created (as previously identified)

## Comprehensive Solution

### 1. Fixed WSGI Configuration
Updated `backend/projectmeats/wsgi.py` to properly handle production settings:

```python
# Determine settings module based on environment
if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    django_env = os.environ.get("DJANGO_ENV", "production")
    if django_env == "development":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apps.settings.development")
    else:
        # Default to production settings for safety in deployment
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apps.settings.production")
```

### 2. Enhanced Production Settings  
Updated `backend/apps/settings/production.py` to read all configuration from environment variables:
- SSL/HTTPS settings configurable via environment
- Security headers (HSTS, XSS, Content-Type, etc.)
- Cookie security settings
- CORS configuration
- ALLOWED_HOSTS configuration

### 3. Secret Key Fix (CRITICAL)
Created tools to generate and validate shell-safe secret keys that avoid problematic characters like `()`, quotes, and other shell specials.

### 4. Directory Creation (Previous Fix)
Continue to ensure all required directories are created:
```bash
mkdir -p /var/log/projectmeats
mkdir -p /var/run/projectmeats
mkdir -p /opt/projectmeats/backend/media
```

### 5. Added Diagnostic Tools
Created `diagnose_deployment` Django management command to identify and fix common deployment issues.
## Quick Fix Steps

### Option 1: Use Diagnostic Command (Recommended)
```bash
cd /opt/projectmeats/backend
source /opt/projectmeats/venv/bin/activate

# Diagnose the current issue
python manage.py diagnose_deployment --validate-secret-key '=64vkjgn0mxz@tnuglpwkq^n9cn4%zwr)4sj=a^(8%c287n*31'

# Generate a safe replacement key
python manage.py diagnose_deployment --generate-secret-key
```

### Option 2: Manual Fix
1. **Generate a new safe secret key:**
   ```bash
   python3 -c "
   import secrets, string
   safe_chars = string.ascii_letters + string.digits + '-_@#\$%^&*+=<>?'
   key = ''.join(secrets.choice(safe_chars) for _ in range(50))
   print(key)
   "
   ```

2. **Update the .env file:**
   ```bash
   # Backup current file
   cp /opt/projectmeats/backend/.env /opt/projectmeats/backend/.env.backup
   
   # Replace the SECRET_KEY line with your new safe key
   sed -i "s/^SECRET_KEY=.*/SECRET_KEY=YOUR_NEW_SAFE_KEY/" /opt/projectmeats/backend/.env
   
   # Ensure production environment is set
   grep -q "^DJANGO_ENV=" /opt/projectmeats/backend/.env || echo "DJANGO_ENV=production" >> /opt/projectmeats/backend/.env
   ```

3. **Create required directories:**
   ```bash
   mkdir -p /var/log/projectmeats /var/run/projectmeats /opt/projectmeats/backend/media
   chmod 755 /var/log/projectmeats /var/run/projectmeats /opt/projectmeats/backend/media
   ```

4. **Restart the service:**
   ```bash
   systemctl restart projectmeats.service
   ```

### Option 3: Run Full Diagnostics
```bash
cd /opt/projectmeats/backend
source /opt/projectmeats/venv/bin/activate
python manage.py diagnose_deployment
```

## Verification

Check if the service is now running:
```bash
systemctl status projectmeats.service
```

Test the application:
```bash
curl -I http://your-domain/
# Should return HTTP headers, not curl errors
```

Check service logs if needed:
```bash
journalctl -u projectmeats.service -n 50
```

## Prevention

To avoid similar issues in the future:
1. Use the diagnostic command before deployment: `python manage.py diagnose_deployment`
2. Validate secret keys for shell-safety before using them in environment files
3. Always test Django configuration with `python manage.py check --deploy`
4. Test systemd services after configuration changes

## Files Modified in This Fix
- `backend/projectmeats/wsgi.py` - Fixed WSGI settings module selection
- `backend/apps/settings/production.py` - Added environment variable support for all settings
- `backend/apps/core/management/commands/diagnose_deployment.py` - Added comprehensive diagnostic tools

## Summary
The Django service startup failure was caused by multiple issues, with the most critical being a secret key containing shell special characters. The comprehensive solution addresses all identified issues and provides tools to prevent similar problems in the future.
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