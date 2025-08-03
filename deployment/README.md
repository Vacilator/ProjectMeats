# Deployment Directory

This directory contains all deployment-related files organized for clarity and maintainability.

## Directory Structure

```
deployment/
├── configs/           # Configuration files
│   └── ai_deployment_config.json
├── docs/             # Deployment documentation
│   ├── DEPLOYMENT_AUTH_QUICKREF.md
│   ├── DEPLOYMENT_ISSUE_ANALYSIS.md
│   ├── DEPLOYMENT_TROUBLESHOOTING.md
│   └── GITHUB_PAT_USAGE_EXAMPLES.md
├── scripts/          # Deployment and utility scripts
│   ├── agent_orchestrator.py
│   ├── ai_deployment_examples.py
│   ├── auth_helper.sh
│   ├── check_dns_propagation.py
│   ├── diagnose_deployment_issue.py
│   ├── diagnose_domain_access.py
│   ├── fix_meatscentral_access.py
│   ├── fix_nodejs.sh
│   └── server_guide.py
└── deprecated/       # Deprecated files (for reference)
```

## Main Deployment Scripts

**In Root Directory:**
- `ai_deployment_orchestrator.py` - Main AI deployment orchestrator (enhanced in PR 93)
- `production_deploy.py` - Clean production deployment script
- `cleanup_redundancies.py` - Repository cleanup script

## Usage

### Production Deployment
```bash
# Clean production deployment
python production_deploy.py --full

# With custom config
python production_deploy.py --full --config deployment/configs/ai_deployment_config.json
```

### Repository Cleanup
```bash
# Analyze redundancies
python cleanup_redundancies.py --analyze

# Clean redundant files
python cleanup_redundancies.py --clean
```

### AI Deployment Orchestrator
```bash
# Use the enhanced orchestrator (from PR 93)
python ai_deployment_orchestrator.py
```

## Configuration

Main configuration file: `deployment/configs/ai_deployment_config.json`

Copy and customize for your environment:
```bash
cp deployment/configs/ai_deployment_config.json my_deployment_config.json
```