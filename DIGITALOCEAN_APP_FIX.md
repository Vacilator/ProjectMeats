# DigitalOcean App Platform Configuration Fix

## Problem
When trying to save the app specification to DigitalOcean App Platform, you may encounter:
```
parsing app spec: proto: (line 1:116): unknown field "certificate_id"
```

## Solution
The error occurs because `certificate_id` is not a valid field in the DigitalOcean App Platform specification. This field may have been deprecated or never existed in the official spec.

## Fixed Configuration
The `app.yaml` file has been updated to use the correct DigitalOcean App Platform specification format:

### Key Changes Made:
1. **Removed invalid `certificate_id` field** - This field doesn't exist in the current App Platform specification
2. **Updated to current spec format** - Using the latest DigitalOcean App Platform YAML structure
3. **Simplified configuration** - Removed unnecessary complex routing that might cause issues
4. **Added proper service definitions** - Backend service and frontend static site
5. **Included essential jobs** - Database migration and static file collection

### Valid Fields Used:
- `name`: Application name
- `region`: Deployment region
- `services`: Backend API services with Docker
- `static_sites`: Frontend React application 
- `databases`: PostgreSQL database
- `jobs`: Pre-deployment tasks (migrations, static files)

### SSL/TLS Configuration
For SSL certificates in DigitalOcean App Platform:
- Certificates are automatically managed by the platform
- No manual certificate configuration is needed
- Custom domains automatically get Let's Encrypt certificates
- Use the domain management in the DigitalOcean control panel instead

## Usage
1. Use the corrected `app.yaml` file in your repository root
2. Deploy using DigitalOcean App Platform dashboard or CLI
3. The app will automatically provision SSL certificates for your domains

## Alternative: Minimal Configuration
If you need a simpler setup, use `app.minimal.yaml` which contains only essential components.

## Validation
To validate your app specification before deploying:
```bash
# Install doctl if you haven't already
# Then validate the spec
doctl apps spec validate app.yaml
```

## Files
- `app.yaml` - Main DigitalOcean App Platform specification (corrected)
- `app.minimal.yaml` - Minimal working configuration
- This documentation file

## Common Issues Resolved
- ✅ Removed invalid `certificate_id` field
- ✅ Using current App Platform YAML format
- ✅ Proper service and static site definitions
- ✅ Correct environment variable format
- ✅ Valid health check configuration
- ✅ Proper job definitions for Django migrations