# ProjectMeats Unified Deployment Tool - Complete Guide

## 🚀 THE AUTONOMOUS DEPLOYMENT SOLUTION

The **Unified Deployment Tool** (`unified_deployment_tool.py`) is now a truly intelligent, autonomous deployment solution that consolidates ALL ProjectMeats deployment, diagnostic, fix, and management functionality.

## ✅ MAJOR ENHANCEMENT COMPLETED

**Version 2.0 - Autonomous & Intuitive** brings significant improvements:

### 🎯 **Autonomous Intelligence**
- ✅ **Smart System Analysis**: Automatically detects what needs to be done
- ✅ **Intelligent Recommendations**: Provides targeted suggestions based on system state
- ✅ **Self-Healing Capabilities**: Automatically fixes common issues without user intervention
- ✅ **Adaptive Decision Making**: Chooses the best course of action based on environment

### 🧙‍♂️ **Intuitive User Experience**
- ✅ **Interactive Setup Wizard**: Guides users through configuration step-by-step
- ✅ **Context-Aware Help**: Shows relevant help based on current situation
- ✅ **Simplified Commands**: Reduced complexity while maintaining full functionality
- ✅ **Smart Defaults**: Automatically chooses sensible defaults when possible

### 🛠️ **Enhanced Functionality**
- ✅ **Modular Architecture**: Clean, maintainable code structure
- ✅ **Robust Error Handling**: Better error recovery and user guidance
- ✅ **Streamlined Operations**: Faster execution with intelligent optimization
- ✅ **Comprehensive Diagnostics**: Advanced system analysis and reporting

## ✅ CONSOLIDATED FUNCTIONALITY

This tool **replaces and enhances** all of the following scripts with intelligent automation:

- `ai_deployment_orchestrator.py` → **Autonomous deployment with intelligent decision making**
- `master_deploy.py` → **Smart deployment system with auto-configuration**
- `deploy_production.py` → **Interactive production setup with guided wizard**
- `enhanced_deployment.py` → **Enhanced deployment with automatic issue resolution**
- `fix_meatscentral_access.py` → **Intelligent domain access diagnostics and fixes**
- `diagnose_deployment_issue.py` → **Smart deployment issue diagnosis**
- `diagnose_domain_access.py` → **Advanced domain access diagnostics**
- All configuration and management scripts → **Unified configuration management**

### 🆕 NEW AUTONOMOUS FEATURES

✅ **Smart System Detection**: Automatically identifies system state and requirements  
✅ **Intelligent Auto-Fix**: Applies targeted fixes based on detected issues  
✅ **Adaptive Configuration**: Automatically configures based on environment  
✅ **Interactive Guidance**: Step-by-step wizard for any skill level  
✅ **Context-Aware Help**: Shows relevant information based on current situation  
✅ **Autonomous Decision Making**: Makes intelligent choices to minimize user input  
✅ **Self-Healing Operations**: Automatically recovers from common errors  
✅ **Streamlined Interface**: Simplified commands with maximum functionality

## 🎯 QUICK START - AUTONOMOUS MODE

### 🧙‍♂️ Interactive Mode (Recommended for All Users)

```bash
# Start the interactive setup wizard - works for any skill level
sudo python3 unified_deployment_tool.py

# This will:
# 1. Analyze your system automatically
# 2. Guide you through configuration step-by-step
# 3. Fix any issues automatically
# 4. Deploy with optimal settings
```

### ⚡ Fully Automatic Mode

```bash
# One-command autonomous deployment
sudo python3 unified_deployment_tool.py --auto --domain=yourdomain.com

# The tool will:
# - Detect what needs to be done
# - Fix any issues automatically  
# - Deploy with intelligent defaults
# - Provide status updates throughout
```

### 🔍 Smart Diagnostics

```bash
# Intelligent system analysis
python3 unified_deployment_tool.py --diagnose

# This provides:
# - Comprehensive system health check
# - Targeted recommendations
# - Priority-based issue identification
# - Automatic fix suggestions
```
sudo python3 unified_deployment_tool.py --production --interactive
```

### Fixing MeatsCentral.com Issues

```bash
# Diagnose why meatscentral.com isn't working
python3 unified_deployment_tool.py --diagnose --domain=meatscentral.com --server=167.99.155.140

# Auto-fix domain access issues
sudo python3 unified_deployment_tool.py --fix --domain=meatscentral.com
```

### System Monitoring and Management

```bash
# Check system status and health
python3 unified_deployment_tool.py --status

# Update existing deployment
sudo python3 unified_deployment_tool.py --update

# Create backup
sudo python3 unified_deployment_tool.py --backup

# Clean server environment before fresh deployment
sudo python3 unified_deployment_tool.py --clean --auto
```

## 📋 DEPLOYMENT MODES

### 🎯 `--production`
Full production deployment with all security features:
- SSL certificates via Let's Encrypt
- Firewall configuration
- PostgreSQL database setup
- Security headers and HTTPS enforcement
- Automatic backups
- Service monitoring

### 🧪 `--staging`
Staging environment for testing:
- Similar to production but with relaxed security
- Uses staging database
- No SSL requirement
- Debug logging enabled

### 💻 `--development`
Development environment setup:
- Local development optimizations
- SQLite database (faster setup)
- Debug mode enabled
- Development server configuration

### 🔧 `--local`
Local development setup on your machine:
- No server configuration
- Local database setup
- Development tools integration

### 🐳 `--docker`
Container-based deployment:
- Docker and docker-compose setup
- Containerized services
- Easy scaling and management
- Production-ready containers

### ☁️ `--cloud`
Cloud provider deployment:
- Cloud-optimized configuration
- Auto-scaling setup
- Cloud database integration
- CDN configuration

## 🛠️ OPERATION MODES

### 🔍 `--diagnose`
Comprehensive system diagnostics:
- Server health check
- Network connectivity testing
- Service status verification
- Application integrity check
- Domain accessibility testing
- Security configuration review

### 🛠️ `--fix`
Automatic issue resolution:
- Service restart and configuration fixing
- Permission corrections
- Firewall rule adjustment
- Database connectivity fixes
- Domain access resolution
- SSL certificate renewal

### 🧹 `--clean`
Server cleanup and preparation:
- Remove overlapping files and credentials
- Clean conflicting installations
- Validate folder structure
- Prepare clean environment for deployment

### 📊 `--status`
System health and status check:
- Service status overview
- Resource usage monitoring
- Application health verification
- Performance metrics
- Security status check

### 🔄 `--update`
Update existing deployment:
- Pull latest code from repository
- Update dependencies
- Run database migrations
- Rebuild frontend assets
- Restart services

### ⚙️ `--config`
Configuration management:
- View current configuration
- Interactive configuration setup
- Save/load configuration profiles
- Environment variable management

### 📚 `--docs`
Documentation generation:
- Generate comprehensive documentation
- Create deployment guides
- Export configuration references
- API documentation

### 💾 `--backup`
Create system backup:
- Application files backup
- Database backup
- Configuration backup
- Service definitions backup

### ↩️ `--rollback`
Rollback to previous version:
- Restore from backup
- Revert to previous deployment
- Database rollback
- Service restoration

## 🔐 AUTHENTICATION SETUP

### SSH Key Authentication (Recommended)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@YOUR_SERVER_IP

# Use with deployment
python3 unified_deployment_tool.py --production --server=YOUR_SERVER_IP --key-file=~/.ssh/id_ed25519
```

### GitHub Authentication

For reliable repository downloading, especially for private repos:

```bash
# Method 1: Environment variables (recommended)
export GITHUB_USER=your_username
export GITHUB_TOKEN=your_personal_access_token

# Method 2: Command line options
python3 unified_deployment_tool.py --production --github-user=USERNAME --github-token=TOKEN
```

**To create a GitHub Personal Access Token:**
1. Go to GitHub.com → Settings → Developer settings → Personal access tokens
2. Generate new token with 'repo' scope
3. Copy the token (you won't see it again)

## 📝 COMMON USE CASES

### First-Time Production Deployment

```bash
# Interactive wizard for beginners
sudo python3 unified_deployment_tool.py --production --interactive

# Advanced users with all parameters
sudo python3 unified_deployment_tool.py --production \
  --domain=mycompany.com \
  --server=192.168.1.100 \
  --github-user=myusername \
  --github-token=ghp_xxxxxxxxxxxx \
  --auto
```

### Fixing a Broken Deployment

```bash
# Step 1: Diagnose the problem
python3 unified_deployment_tool.py --diagnose --domain=mycompany.com --server=192.168.1.100

# Step 2: Auto-fix common issues
sudo python3 unified_deployment_tool.py --fix

# Step 3: Clean deployment if needed
sudo python3 unified_deployment_tool.py --clean --auto

# Step 4: Fresh deployment
sudo python3 unified_deployment_tool.py --production --domain=mycompany.com --auto
```

### Updating an Existing Deployment

```bash
# Regular update
sudo python3 unified_deployment_tool.py --update

# Update with backup first
sudo python3 unified_deployment_tool.py --backup
sudo python3 unified_deployment_tool.py --update
```

### Docker-Based Deployment

```bash
# Docker production deployment
sudo python3 unified_deployment_tool.py --docker --production --domain=mycompany.com --auto

# Docker with custom configuration
sudo python3 unified_deployment_tool.py --docker --production \
  --domain=mycompany.com \
  --database=postgresql \
  --auto
```

### Monitoring and Maintenance

```bash
# Daily health check
python3 unified_deployment_tool.py --status

# Weekly backup
sudo python3 unified_deployment_tool.py --backup

# Monthly updates
sudo python3 unified_deployment_tool.py --backup
sudo python3 unified_deployment_tool.py --update
```

## 🚨 TROUBLESHOOTING

### Common Issues and Solutions

#### 1. "Domain not accessible" Error

```bash
# Diagnose the specific issue
python3 unified_deployment_tool.py --diagnose --domain=yourdomain.com

# Auto-fix attempt:
sudo python3 unified_deployment_tool.py --fix --domain=yourdomain.com
```

#### 2. Repository Download Fails

```bash
# Setup GitHub authentication
export GITHUB_USER=your_username
export GITHUB_TOKEN=your_token

# Clean and retry
sudo python3 unified_deployment_tool.py --clean --auto
sudo python3 unified_deployment_tool.py --production --domain=yourdomain.com --auto
```

#### 3. Service Failures

```bash
# Check what's wrong
python3 unified_deployment_tool.py --status

# Auto-fix services
sudo python3 unified_deployment_tool.py --fix
```

## 📞 SUPPORT AND HELP

### Command Line Help

```bash
# Show all available options
python3 unified_deployment_tool.py --help

# Show current configuration
python3 unified_deployment_tool.py --config

# Generate fresh documentation
python3 unified_deployment_tool.py --docs
```

### Quick Reference

```bash
# The most important commands to remember:

# 🎯 Deploy to production
sudo python3 unified_deployment_tool.py --production --domain=yourdomain.com --auto

# 🔍 Diagnose any issues
python3 unified_deployment_tool.py --diagnose --domain=yourdomain.com

# 🛠️ Fix any problems
sudo python3 unified_deployment_tool.py --fix

# 📊 Check system health
python3 unified_deployment_tool.py --status
```

---

**Generated on:** {GENERATION_DATE}  
**Tool Version:** 1.0 - Unified Deployment System  
**Author:** ProjectMeats AI Assistant

> This tool consolidates all previous deployment scripts into one reliable, comprehensive solution for ProjectMeats deployment, management, and troubleshooting.