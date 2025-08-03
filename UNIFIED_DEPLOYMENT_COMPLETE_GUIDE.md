# ProjectMeats Unified Deployment Tool - Complete Guide

## 🚀 THE ONLY DEPLOYMENT TOOL YOU NEED

The **Unified Deployment Tool** (`unified_deployment_tool.py`) consolidates ALL ProjectMeats deployment, diagnostic, fix, and management functionality into a single, powerful, and reliable tool.

### ✅ CONSOLIDATED FUNCTIONALITY

This tool **replaces and enhances** all of the following scripts:

- `ai_deployment_orchestrator.py` → AI-driven deployment with error recovery
- `master_deploy.py` → Comprehensive deployment system
- `deploy_production.py` → Interactive production setup
- `enhanced_deployment.py` → Enhanced deployment with fixes
- `fix_meatscentral_access.py` → Domain access diagnostics and fixes
- `diagnose_deployment_issue.py` → Deployment issue diagnosis
- `diagnose_domain_access.py` → Domain access diagnostics
- All configuration and management scripts

### 🆕 NEW ENHANCED FEATURES

✅ **Server cleanup and folder structure validation**  
✅ **Automatic credential and file overlap cleaning**  
✅ **Clean repository cloning with proper folder recreation**  
✅ **Comprehensive pre-deployment server preparation**  
✅ **Real-time deployment monitoring and AI-driven error recovery**  
✅ **Domain accessibility verification and auto-fixing**  
✅ **Consolidated configuration management**  
✅ **One-command deployment for production**

## 🎯 QUICK START

### Production Deployment (Most Common)

```bash
# One-command production deployment
sudo python3 unified_deployment_tool.py --production --domain=yourdomain.com --auto

# Interactive setup wizard for first-time users
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

## 🔧 ADVANCED CONFIGURATION

### Custom Project Directory

```bash
python3 unified_deployment_tool.py --production \
  --project-dir=/custom/path \
  --domain=mycompany.com \
  --auto
```

### Custom Database Configuration

```bash
# Use SQLite instead of PostgreSQL
python3 unified_deployment_tool.py --production \
  --database=sqlite \
  --domain=mycompany.com \
  --auto
```

### Custom Admin User

```bash
python3 unified_deployment_tool.py --production \
  --admin-user=myuser \
  --admin-email=admin@mycompany.com \
  --domain=mycompany.com \
  --auto
```

### Disable SSL for Testing

```bash
python3 unified_deployment_tool.py --production \
  --no-ssl \
  --domain=test.mycompany.com \
  --auto
```

## 🚨 TROUBLESHOOTING

### Common Issues and Solutions

#### 1. "Domain not accessible" Error

```bash
# Diagnose the specific issue
python3 unified_deployment_tool.py --diagnose --domain=yourdomain.com

# Common fixes:
# - Check DNS A record points to your server IP
# - Verify firewall allows HTTP/HTTPS traffic
# - Ensure nginx is running and configured correctly

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

# Manual service restart
sudo systemctl restart nginx
sudo systemctl restart projectmeats
sudo systemctl restart postgresql
```

#### 4. Permission Errors

```bash
# Fix permissions
sudo python3 unified_deployment_tool.py --fix

# Manual permission fix
sudo chown -R projectmeats:projectmeats /opt/projectmeats
sudo chmod -R 755 /opt/projectmeats
```

#### 5. Database Connection Issues

```bash
# For PostgreSQL issues
sudo systemctl restart postgresql
sudo -u postgres psql -c "SELECT version();"

# Re-run database setup
sudo python3 unified_deployment_tool.py --fix
```

### Getting Detailed Logs

```bash
# Verbose output for debugging
python3 unified_deployment_tool.py --diagnose --verbose

# Check system logs
sudo journalctl -u nginx
sudo journalctl -u projectmeats
sudo journalctl -u postgresql
```

## 📁 FILE STRUCTURE

After successful deployment, your server will have:

```
/opt/projectmeats/
├── backend/
│   ├── venv/
│   ├── manage.py
│   ├── requirements.txt
│   └── staticfiles/
├── frontend/
│   ├── build/
│   ├── package.json
│   └── node_modules/
├── logs/
├── backups/
└── uploads/

/etc/nginx/sites-available/
└── yourdomain.com

/etc/systemd/system/
└── projectmeats.service
```

## 🔒 SECURITY FEATURES

The unified tool automatically configures:

- **Firewall**: UFW with minimal required ports
- **SSL/TLS**: Let's Encrypt certificates
- **Security Headers**: HSTS, XSS protection, content type nosniff
- **Rate Limiting**: API endpoint protection
- **Secure Passwords**: Auto-generated secure credentials
- **File Permissions**: Proper ownership and permissions
- **Database Security**: Secured PostgreSQL configuration

## 🎯 PERFORMANCE OPTIMIZATION

Automatic optimizations include:

- **Static File Caching**: Long-term caching for assets
- **Gzip Compression**: Compressed responses
- **Database Indexing**: Optimized database queries
- **CDN Ready**: Cache-friendly headers
- **Resource Limits**: Proper memory and CPU limits
- **Connection Pooling**: Efficient database connections

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

### GitHub Issues

For bugs, feature requests, or detailed support:
<GITHUB_REPO_URL>/issues

> **Note:** Replace `<GITHUB_REPO_URL>` with your project's actual GitHub repository URL (e.g., `https://github.com/YourOrg/YourRepo`).
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

**Generated on:** 2024-12-19  
**Tool Version:** 1.0 - Unified Deployment System  
**Author:** ProjectMeats AI Assistant

> This tool consolidates all previous deployment scripts into one reliable, comprehensive solution for ProjectMeats deployment, management, and troubleshooting.