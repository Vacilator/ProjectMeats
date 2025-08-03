# ProjectMeats Deployment Scripts

This directory contains the **consolidated deployment system** for ProjectMeats. All previous fragmented documentation and scripts have been replaced with these three comprehensive tools:

## 🎯 Main Scripts

### 1. `one_click_deploy.sh` - Complete Automated Deployment
```bash
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/one_click_deploy.sh | sudo bash
```
- **What it does**: Complete production setup in one command
- **Requirements**: Ubuntu 20.04+, sudo access, domain name
- **Time**: 15-30 minutes
- **Handles**: Everything automatically including Node.js conflicts

### 2. `master_deploy.py` - Advanced Deployment Script  
```bash
python3 master_deploy.py --auto --domain=yourdomain.com
```
- **What it does**: Full-featured deployment with all options
- **Features**: Interactive setup, multiple database options, custom configurations
- **Use when**: You need more control over the deployment process

### 3. `fix_nodejs.sh` - Node.js Conflict Resolution
```bash
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/fix_nodejs.sh | sudo bash
```
- **What it does**: Specifically fixes Node.js/npm installation conflicts
- **Solves**: "nodejs : Conflicts: npm" errors
- **Use when**: You've been experiencing the Node.js package dependency issues

## 📚 Documentation

- **[PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)** - The ONLY deployment guide you need
- **[DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)** - Quick reference with links to main guide

## 🗑️ Removed Files

The following fragmented files have been **removed** to eliminate confusion:
- `docs/production_deployment.md` (1060 lines)
- `docs/production_setup_guide.md` (212 lines)  
- `docs/production_deployment_overview.md` (230 lines)

All content has been consolidated into the single `PRODUCTION_DEPLOYMENT.md` guide.

## 🎉 The Node.js Problem is SOLVED

**Previous Issue:**
```
The following packages have unmet dependencies:
 nodejs : Conflicts: npm
 npm : Depends: node-cacache but it is not going to be installed
E: Unable to correct problems, you have held broken packages.
```

**Solution:** Our scripts now automatically:
1. ✅ Stop all Node.js processes
2. ✅ Remove ALL conflicting packages (including newer Ubuntu 22.04 versions)
3. ✅ Clean package cache completely  
4. ✅ Try multiple installation methods with fallbacks
5. ✅ Verify installation before proceeding

## 🚀 Quick Start

**For most users:**
```bash
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/one_click_deploy.sh | sudo bash
```

**If you want to understand what's happening:**
1. Read `PRODUCTION_DEPLOYMENT.md`
2. Run `python3 master_deploy.py` for interactive setup

**If you just want to fix Node.js and continue manually:**
```bash
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/fix_nodejs.sh | sudo bash
```

Your deployment process is now **simple, reliable, and automated**! 🎯