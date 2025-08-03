# Deprecated Deployment Scripts

⚠️ **THESE SCRIPTS ARE DEPRECATED** ⚠️

All functionality from these scripts has been consolidated into the new **Unified Deployment Tool**.

## Use This Instead

**NEW:** `unified_deployment_tool.py` - THE ONLY DEPLOYMENT TOOL YOU NEED

```bash
# One-command production deployment
sudo python3 unified_deployment_tool.py --production --domain=yourdomain.com --auto

# Diagnose issues
python3 unified_deployment_tool.py --diagnose --domain=yourdomain.com

# Auto-fix problems
sudo python3 unified_deployment_tool.py --fix

# Check system health
python3 unified_deployment_tool.py --status
```

## What Was Replaced

### AI Deployment Scripts
- `ai_deployment_orchestrator.py` → `unified_deployment_tool.py --production`
- `ai_deployment_examples.py` → Built into unified tool
- Configuration files → `unified_deployment_tool.py --config`

### Master Deploy Scripts  
- `master_deploy.py` → `unified_deployment_tool.py --production`
- `deploy_production.py` → `unified_deployment_tool.py --production --interactive`
- `enhanced_deployment.py` → Enhanced features built into unified tool

### Fix/Diagnose Scripts
- `fix_meatscentral_access.py` → `unified_deployment_tool.py --fix`
- `diagnose_deployment_issue.py` → `unified_deployment_tool.py --diagnose`
- `diagnose_domain_access.py` → `unified_deployment_tool.py --diagnose`

### Partial Deploy Scripts
- `deploy_server.sh` → `unified_deployment_tool.py --production`
- `deploy_no_auth.sh` → `unified_deployment_tool.py --production` (with built-in auth handling)
- `complete_deployment.sh` → `unified_deployment_tool.py --production --auto`

## Documentation

See `UNIFIED_DEPLOYMENT_COMPLETE_GUIDE.md` for comprehensive documentation.

---
**Archived on:** 2024-06-01
**Replaced by:** Unified Deployment Tool v1.0