# ProjectMeats Environment Files - Deprecation Notice

**⚠️ DEPRECATED FILES - DO NOT USE ⚠️**

The following environment files have been replaced by the unified environment management system:

## Replaced Files
- `.env.prod` → Use AI Deployment Orchestrator auto-generation
- `.env.prod.example` → See ENVIRONMENT_SETUP_GUIDE.md
- `.env.prod.template` → Replaced by deployment/templates/environment.template
- `.env.production.enhanced` → Replaced by deployment/templates/environment.template
- `deployment/config/projectmeats.env.template` → Replaced by deployment/templates/environment.template

## Current System
The ProjectMeats deployment now uses:
- **Unified Template**: `deployment/templates/environment.template`
- **Configuration Manager**: `deployment/environment_config.py`
- **Auto-Generation**: Environment files are created automatically by the AI Deployment Orchestrator

## Migration Guide
1. **For Production**: Use `python ai_deployment_orchestrator.py --interactive`
2. **For Development**: Use `backend/.env.example` as a starting point
3. **For Reference**: See `ENVIRONMENT_SETUP_GUIDE.md` for complete documentation

## Why This Change?
- **Security**: Auto-generated credentials reduce human error
- **Consistency**: Single template ensures all deployments use the same format
- **Maintainability**: One source of truth for environment configuration
- **User Experience**: Simplified setup process with validation

These files will be removed in a future release. Please update your deployment processes to use the new unified system.