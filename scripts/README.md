# ProjectMeats Scripts Directory

This directory contains organized scripts and utilities for ProjectMeats development and operations.

## Directory Structure

### `/deployment/`
Contains deployment-related scripts, utilities, and diagnostic tools:
- **Legacy deployment scripts** - Older deployment methods (now deprecated)
- **Diagnostic tools** - Scripts for troubleshooting deployment issues
- **Utility scripts** - Helper scripts for specific deployment tasks
- **Fix scripts** - Tools for resolving specific deployment problems

### `/testing/`
Contains test scripts and validation tools:
- **Integration tests** - End-to-end deployment testing
- **Unit test helpers** - Scripts supporting automated testing
- **Validation scripts** - Tools for verifying system functionality

## Main Deployment Tools (in root directory)

The primary deployment tools remain in the root directory for easy access:

- **`ai_deployment_orchestrator.py`** - ⭐ **PRIMARY DEPLOYMENT TOOL** - AI-powered deployment with intelligent error recovery
- **`master_deploy.py`** - Alternative comprehensive deployment tool
- **`deploy_production.py`** - Interactive deployment wizard
- **`ai_deploy.sh`** - Wrapper script for AI deployment
- **`production_deploy.sh`** - Production deployment script

## Usage

For most deployment needs, use the primary tool:
```bash
python ai_deployment_orchestrator.py --interactive
```

Scripts in subdirectories are primarily for:
- Development and debugging
- Legacy system support  
- Specialized troubleshooting scenarios

## Note

The main production deployment process is handled by `ai_deployment_orchestrator.py` in the root directory. Scripts in this directory are supplementary tools and should not be used for primary deployment workflows unless specifically needed for troubleshooting.