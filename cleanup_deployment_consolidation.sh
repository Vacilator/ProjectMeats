#!/bin/bash
# ProjectMeats Deployment Consolidation Cleanup Script
# ====================================================
# 
# This script organizes deprecated deployment files based on the consolidation
# guide, moving legacy scripts and documentation to archived locations while
# preserving the enhanced AI deployment orchestrator as the primary system.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Logging functions
log_header() { echo -e "\n${PURPLE}${BOLD}$1${NC}"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_header "🤖 ProjectMeats Deployment Consolidation Cleanup"
echo -e "${CYAN}Organizing deployment files based on AI orchestrator consolidation${NC}"
echo "=================================================================="

# Create deprecated directory structure
log_info "Creating archive directory structure..."
mkdir -p deprecated/scripts
mkdir -p deprecated/docs
mkdir -p deprecated/configs
mkdir -p deprecated/tests

log_success "Archive directories created"

# Archive deprecated deployment scripts
log_header "📦 Archiving Deprecated Deployment Scripts"

DEPRECATED_SCRIPTS=(
    "one_click_deploy.sh"
    "quick_deploy.sh"
    "deploy_production.py"
    "deploy_server.sh"
    "complete_deployment.sh"
    "deploy_no_auth.sh"
    "verify_deployment.sh"
    "verify_deployment_fixes.py"
    "verify_deployment_readiness.sh"
    "verify_production.sh"
    "validate_deployment_fixes.sh"
    "test_deployment_fixes.py"
    "test_deployment_integration.py"
    "test_deployment_simulation.py"
    "test_no_auth_deployment.sh"
    "test_specific_fixes.py"
    "test_master_deploy_fixes.py"
    "diagnose_deployment_issue.py"
    "fix_nodejs.sh"
    "auth_helper.sh"
)

for script in "${DEPRECATED_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        log_info "Archiving $script..."
        mv "$script" deprecated/scripts/
        log_success "✅ $script archived"
    else
        log_warning "⚠️ $script not found (may already be archived)"
    fi
done

# Archive deprecated documentation
log_header "📚 Archiving Deprecated Documentation"

DEPRECATED_DOCS=(
    "DEPLOYMENT_README.md"
    "PRODUCTION_DEPLOYMENT.md"
    "DEPLOYMENT_INSTRUCTIONS.md"
    "DEPLOYMENT_TROUBLESHOOTING.md"
    "DEPLOYMENT_AUTH_QUICKREF.md"
    "DEPLOYMENT_ISSUE_ANALYSIS.md"
    "DEPLOYMENT_FIXES_SUMMARY.md"
    "DEPLOYMENT_FIX_SUMMARY.md"
    "AI_DEPLOYMENT_FIX_SUMMARY.md"
    "FRONTEND_CICD_FIX.md"
    "GITHUB_PAT_USAGE_EXAMPLES.md"
    "OPTIMIZATION_REPORT.md"
    "PR71_REVIEW_SUMMARY.md"
    "SOLUTION_SUMMARY.md"
    "QUICK_SETUP.md"
)

for doc in "${DEPRECATED_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        log_info "Archiving $doc..."
        mv "$doc" deprecated/docs/
        log_success "✅ $doc archived"
    else
        log_warning "⚠️ $doc not found (may already be archived)"
    fi
done

# Archive deprecated configuration files
log_header "⚙️ Archiving Deprecated Configuration Files"

DEPRECATED_CONFIGS=(
    "ai_deployment_config.example.json"
    "production_config.json"
    "deployment_state.json"
    "cookies.txt"
)

for config in "${DEPRECATED_CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        log_info "Archiving $config..."
        mv "$config" deprecated/configs/
        log_success "✅ $config archived"
    else
        log_warning "⚠️ $config not found (may already be archived)"
    fi
done

# Archive deprecated test files  
log_header "🧪 Archiving Deprecated Test Files"

DEPRECATED_TESTS=(
    "test_download_fix.py"
    "test_github_auth_enhancement.sh"
    "verify_deployment_fix.py"
)

for test in "${DEPRECATED_TESTS[@]}"; do
    if [ -f "$test" ]; then
        log_info "Archiving $test..."
        mv "$test" deprecated/tests/
        log_success "✅ $test archived"
    else
        log_warning "⚠️ $test not found (may already be archived)"
    fi
done

# Create archive README
log_header "📄 Creating Archive Documentation"

cat > deprecated/README.md << 'EOF'
# Deprecated ProjectMeats Deployment Files

## ⚠️ IMPORTANT NOTICE

These files have been **DEPRECATED** as part of the ProjectMeats deployment consolidation effort. 

**DO NOT USE** these files for new deployments. They are preserved here for:
- Historical reference
- Emergency fallback (if needed)
- Migration assistance

## 🤖 Use This Instead

**PRIMARY DEPLOYMENT SYSTEM:**
```bash
# AI-powered intelligent deployment (RECOMMENDED)
python3 ai_deployment_orchestrator.py --interactive
```

**SECONDARY DEPLOYMENT SYSTEM:**
```bash
# Traditional unified deployment
python3 master_deploy.py --auto --domain=yourdomain.com
```

## 📚 Current Documentation

- **DEPLOYMENT_MASTER_GUIDE.md** - Complete deployment reference
- **AI_DEPLOYMENT_README.md** - AI orchestrator guide
- **DEPLOYMENT_CONSOLIDATION_GUIDE.md** - Consolidation overview

## 🗂️ Archive Contents

- **scripts/** - Legacy deployment scripts
- **docs/** - Deprecated documentation
- **configs/** - Old configuration files
- **tests/** - Deprecated test files

## ⚡ Migration Path

If you were using any deprecated scripts:

| Old Script | New Command |
|------------|-------------|
| `one_click_deploy.sh` | `python3 ai_deployment_orchestrator.py --interactive` |
| `quick_deploy.sh` | `python3 ai_deployment_orchestrator.py --auto-deploy` |
| `deploy_production.py` | `python3 ai_deployment_orchestrator.py --profile=production` |
| All others | See DEPLOYMENT_MASTER_GUIDE.md for equivalents |

## 🚀 Enhanced Features

The new AI deployment orchestrator provides:
- 🧠 Intelligent error detection and recovery
- 🔮 Predictive deployment analysis
- 📊 Performance optimization
- 🔄 Self-healing deployment processes
- 📈 Real-time monitoring and alerting

---

*For support with migration, see the main deployment documentation or raise an issue on GitHub.*
EOF

log_success "Archive README created"

# Update main README with consolidation notice
log_header "📝 Updating Main Documentation"

# Check if we should update existing files
if [ -f "README.md" ]; then
    log_info "Adding consolidation notice to main README..."
    
    # Add notice if not already present
    if ! grep -q "DEPLOYMENT CONSOLIDATION" README.md; then
        cat >> README.md << 'EOF'

## 🚀 Deployment System (Consolidated)

**IMPORTANT**: The ProjectMeats deployment system has been consolidated around the **AI Deployment Orchestrator** as the primary intelligent deployment solution.

### Quick Start
```bash
# AI-powered deployment (recommended)
python3 ai_deployment_orchestrator.py --interactive

# Traditional deployment
python3 master_deploy.py --auto --domain=yourdomain.com
```

### Complete Guide
See **DEPLOYMENT_MASTER_GUIDE.md** for comprehensive deployment instructions.

### Legacy Files
Legacy deployment scripts have been moved to `deprecated/` directory. Use the AI orchestrator for all new deployments.

EOF
        log_success "Consolidation notice added to README"
    else
        log_info "Consolidation notice already present in README"
    fi
fi

# Create .gitignore entry for deprecated files
log_header "🔧 Updating Git Configuration"

if [ -f ".gitignore" ]; then
    if ! grep -q "deprecated/" .gitignore; then
        echo "" >> .gitignore
        echo "# Deprecated deployment files (archived)" >> .gitignore
        echo "# Use ai_deployment_orchestrator.py for new deployments" >> .gitignore
        echo "deprecated/" >> .gitignore
        log_success "Added deprecated/ to .gitignore"
    else
        log_info ".gitignore already configured for deprecated files"
    fi
fi

# Show final status
log_header "📊 Consolidation Summary"

echo -e "${BOLD}Files Organized:${NC}"
echo -e "  ${GREEN}✅ Core Deployment Files:${NC}"
echo -e "     • ai_deployment_orchestrator.py (PRIMARY)"
echo -e "     • master_deploy.py (SECONDARY)"
echo -e "     • setup_ai_deployment.py (SETUP)"
echo -e "     • DEPLOYMENT_MASTER_GUIDE.md (DOCS)"

echo -e "  ${YELLOW}📦 Archived Files:${NC}"
echo -e "     • $(ls deprecated/scripts/ 2>/dev/null | wc -l) deployment scripts"
echo -e "     • $(ls deprecated/docs/ 2>/dev/null | wc -l) documentation files"
echo -e "     • $(ls deprecated/configs/ 2>/dev/null | wc -l) configuration files"
echo -e "     • $(ls deprecated/tests/ 2>/dev/null | wc -l) test files"

echo ""
log_success "🎉 Deployment consolidation cleanup completed!"
echo ""
log_info "Next steps:"
echo -e "  ${CYAN}1.${NC} Review DEPLOYMENT_MASTER_GUIDE.md for deployment instructions"
echo -e "  ${CYAN}2.${NC} Set up AI deployment: python3 setup_ai_deployment.py"
echo -e "  ${CYAN}3.${NC} Deploy with AI: python3 ai_deployment_orchestrator.py --interactive"
echo -e "  ${CYAN}4.${NC} Commit changes: git add . && git commit -m 'Deployment consolidation cleanup'"

echo ""
log_warning "Legacy files are in deprecated/ directory for reference only"
log_info "Use the AI deployment orchestrator for all new deployments"