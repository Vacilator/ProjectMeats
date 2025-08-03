#!/bin/bash
# Script to move deprecated deployment scripts to archive folder
# and update main documentation to point to unified tool

echo "🧹 Cleaning up redundant deployment scripts..."

# Create deprecated archive folder
mkdir -p deprecated_deployment_scripts

# Move redundant scripts to archive (keeping for reference)
echo "📦 Archiving old deployment scripts..."

# AI deployment scripts (replaced by unified tool)
mv ai_deployment_orchestrator.py deprecated_deployment_scripts/ 2>/dev/null || true
mv ai_deployment_examples.py deprecated_deployment_scripts/ 2>/dev/null || true
mv ai_deployment_config.*.json deprecated_deployment_scripts/ 2>/dev/null || true

# Master deploy scripts (replaced by unified tool)
mv master_deploy.py deprecated_deployment_scripts/ 2>/dev/null || true
mv deploy_production.py deprecated_deployment_scripts/ 2>/dev/null || true
mv enhanced_deployment.py deprecated_deployment_scripts/ 2>/dev/null || true

# Fix/diagnose/clean scripts (replaced by unified tool)
mv fix_meatscentral_access.py deprecated_deployment_scripts/ 2>/dev/null || true
mv diagnose_deployment_issue.py deprecated_deployment_scripts/ 2>/dev/null || true
mv diagnose_domain_access.py deprecated_deployment_scripts/ 2>/dev/null || true

# Partial deployment scripts (replaced by unified tool)
mv deploy_server.sh deprecated_deployment_scripts/ 2>/dev/null || true
mv deploy_no_auth.sh deprecated_deployment_scripts/ 2>/dev/null || true
mv complete_deployment.sh deprecated_deployment_scripts/ 2>/dev/null || true

# Configuration and helper scripts (replaced by unified tool)
mv production_config.json deprecated_deployment_scripts/ 2>/dev/null || true
mv setup_ai_deployment.py deprecated_deployment_scripts/ 2>/dev/null || true
mv setup_ai_assistant.py deprecated_deployment_scripts/ 2>/dev/null || true

# Test scripts for old deployment system
mv test_*deploy*.py deprecated_deployment_scripts/ 2>/dev/null || true
mv test_*deployment*.py deprecated_deployment_scripts/ 2>/dev/null || true
mv validate_deployment*.sh deprecated_deployment_scripts/ 2>/dev/null || true
mv verify_deployment*.py deprecated_deployment_scripts/ 2>/dev/null || true
mv verify_deployment*.sh deprecated_deployment_scripts/ 2>/dev/null || true

# Deployment documentation (consolidated into unified guide)
mv DEPLOYMENT_*.md deprecated_deployment_scripts/ 2>/dev/null || true
mv AI_DEPLOYMENT_*.md deprecated_deployment_scripts/ 2>/dev/null || true
mv PRODUCTION_DEPLOYMENT.md deprecated_deployment_scripts/ 2>/dev/null || true
mv QUICK_SETUP.md deprecated_deployment_scripts/ 2>/dev/null || true

echo "✅ Archived old deployment scripts to deprecated_deployment_scripts/"

# Create deprecation notice
cat > deprecated_deployment_scripts/README.md << 'EOF'
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
**Archived on:** $ARCHIVE_DATE
**Replaced by:** Unified Deployment Tool v1.0
EOF

echo "📚 Created deprecation notice in deprecated_deployment_scripts/README.md"

echo "🎉 Cleanup completed! Use the unified deployment tool going forward:"
echo "   python3 unified_deployment_tool.py --help"