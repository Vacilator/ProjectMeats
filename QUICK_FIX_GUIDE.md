# Quick Fix Guide for DigitalOcean App Platform certificate_id Error

## Problem
```
parsing app spec: proto: (line 1:116): unknown field "certificate_id"
```

## Solution
✅ **Use the corrected `app.yaml` file** in the repository root

## Quick Steps
1. **Use the fixed configuration:**
   ```bash
   # The corrected app.yaml is ready to use
   # It contains no invalid certificate_id field
   ```

2. **Validate before deploying:**
   ```bash
   python validate_app_spec.py app.yaml
   ```

3. **Deploy with DigitalOcean CLI or Dashboard:**
   ```bash
   # If using doctl CLI
   doctl apps spec validate app.yaml
   doctl apps create app.yaml
   ```

## What Was Fixed
- ❌ Removed invalid `certificate_id` field
- ✅ Added proper DigitalOcean App Platform specification structure
- ✅ Included Django backend service configuration  
- ✅ Added React frontend as static site
- ✅ Configured PostgreSQL database
- ✅ Added pre-deployment jobs (migrations, static files)

## SSL/TLS Certificates
DigitalOcean App Platform automatically manages SSL certificates:
- No manual certificate configuration needed
- Let's Encrypt certificates are provisioned automatically
- Custom domains get automatic HTTPS

## Files
- `app.yaml` - Main configuration (use this)
- `app.minimal.yaml` - Minimal configuration (alternative)
- `validate_app_spec.py` - Validation tool
- `DIGITALOCEAN_APP_FIX.md` - Detailed documentation

## Need Help?
Run the validator to check for issues:
```bash
./validate_app_spec.py app.yaml
```