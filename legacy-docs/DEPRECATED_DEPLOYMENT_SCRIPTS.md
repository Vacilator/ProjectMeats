# 🗂️ Deployment Scripts Cleanup Notice

**IMPORTANT: This directory contains deprecated deployment scripts.**

All deployment functionality has been consolidated into the unified deployment system:

## ✅ Use This Instead
```bash
# The ONLY deployment script you need:
python3 master_deploy.py --help
```

## 🚫 Deprecated Files (To Be Removed)

These files have been replaced by the unified system and will be removed in future versions:

### Replaced Scripts
- `one_click_deploy.sh` → Use `python3 master_deploy.py --auto`
- `deploy_production.py` → Use `python3 master_deploy.py --wizard`
- `quick_deploy.sh` → Use `python3 master_deploy.py --auto`
- `deploy_server.sh` → Use `python3 master_deploy.py --prepare-server`
- `complete_deployment.sh` → Use `python3 master_deploy.py --auto`
- `deploy_no_auth.sh` → Use `python3 master_deploy.py --auto`
- `ai_deployment_*.py` → Functionality integrated into master_deploy.py

### Replaced Documentation
- `DEPLOYMENT_*.md` → See `UNIFIED_DEPLOYMENT_GUIDE.md`
- `PRODUCTION_DEPLOYMENT.md` → See `UNIFIED_DEPLOYMENT_GUIDE.md`
- Multiple deployment READMEs → See `UNIFIED_DEPLOYMENT_GUIDE.md`

### Replaced Verification Scripts
- `verify_deployment*.py` → Built into master_deploy.py
- `test_*_deploy*.py` → Built into master_deploy.py

## 📚 Migration Guide

| Old Command | New Command |
|-------------|-------------|
| `./one_click_deploy.sh` | `python3 master_deploy.py --auto --domain=yourdomain.com` |
| `python3 deploy_production.py` | `python3 master_deploy.py --wizard` |
| `./quick_deploy.sh` | `python3 master_deploy.py --auto` |
| `./deploy_server.sh` | `python3 master_deploy.py --prepare-server` |

## 🎯 Benefits of Unified System

- **Single Source of Truth**: One script for all deployment needs
- **Interactive PostgreSQL Setup**: Step-by-step database configuration
- **Docker Support**: Modern container-based deployment
- **CI/CD Integration**: Automated deployment pipelines
- **Enhanced Monitoring**: Built-in health checks and alerts
- **Better Error Handling**: Comprehensive error recovery
- **Consistent Experience**: Same interface for all deployment types

## 🔄 Cleanup Timeline

1. **Phase 1** (Current): Deprecated files marked with this notice
2. **Phase 2** (Next Release): Deprecated files moved to `deprecated/` folder
3. **Phase 3** (Future Release): Deprecated files removed completely

**For the latest deployment instructions, always refer to `UNIFIED_DEPLOYMENT_GUIDE.md`**