# ProjectMeats Production Deployment Guide

## 🚀 Complete Production Deployment Instructions

This guide covers deploying ProjectMeats to production on both Linux and Windows systems.

### 📋 Quick Start Options

#### Option 1: Unified Deployment Tool (Recommended)

```bash
# Download and run the unified deployment tool
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/unified_deployment_tool.py -o unified_deployment_tool.py

# Interactive deployment
sudo python3 unified_deployment_tool.py --production --interactive

# Automatic deployment
sudo python3 unified_deployment_tool.py --production --domain=yourdomain.com --auto
```

#### Option 2: Platform-Specific Scripts

**Linux/Unix:**
```bash
# One-click deployment
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/one_click_deploy.sh | sudo bash

# Or clone and deploy
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats
sudo ./one_click_deploy.sh
```

**Windows:**
```powershell
# Download and run Windows deployment
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_windows_production.ps1" -OutFile "deploy_windows_production.ps1"
.\deploy_windows_production.ps1 -Interactive

# Or use the batch launcher
curl -o setup_windows_production.bat https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/setup_windows_production.bat
# Run as Administrator
setup_windows_production.bat
```

### 🔍 Pre-Deployment Validation

Before deploying, validate your system:

**Linux/Unix:**
```bash
./verify_production.sh
python3 validate_production.py
```

**Windows:**
```powershell
python validate_windows_production.py
```

### 📚 Platform-Specific Guides

- **[Windows Production Deployment](windows_production_deployment.md)** - Complete Windows deployment guide
- **[Linux Production Setup](../production_checklist.md)** - Linux deployment checklist

### 🏗️ System Requirements

#### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB (8GB+ recommended)
- **Storage**: 20GB free space
- **OS**: 
  - Linux: Ubuntu 18.04+, CentOS 7+, Debian 9+
  - Windows: Windows Server 2019+, Windows 10+ Pro

#### Required Software
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Web server (Nginx/Apache/IIS)
- Git

### 🔒 Security Configuration

#### SSL/TLS Setup
- **Linux**: Automatic Let's Encrypt via certbot
- **Windows**: Let's Encrypt via win-acme or manual certificate installation

#### Firewall Configuration
- **Linux**: UFW/iptables rules for ports 80, 443
- **Windows**: Windows Firewall rules for HTTP/HTTPS

#### Database Security
- Dedicated PostgreSQL user with limited privileges
- Strong passwords and connection encryption
- Regular security updates

### 🔧 Post-Deployment

#### Verification Steps
1. **Frontend**: https://yourdomain.com/
2. **Backend API**: https://yourdomain.com/api/v1/
3. **Admin Panel**: https://yourdomain.com/admin/
4. **Health Check**: https://yourdomain.com/api/v1/health/

#### Default Credentials
- **Username**: admin
- **Password**: WATERMELON1219

**⚠️ Important**: Change the default password immediately!

### 📊 Monitoring and Maintenance

#### Regular Tasks
- Database backups (automated)
- Security updates
- Log monitoring
- Performance monitoring
- SSL certificate renewal

#### Troubleshooting
- Check service logs
- Verify firewall rules
- Test database connectivity
- Validate SSL certificates

### 🆘 Support

- **Documentation**: [Project docs](../docs/)
- **Issues**: [GitHub Issues](https://github.com/Vacilator/ProjectMeats/issues)
- **Community**: [Discussions](https://github.com/Vacilator/ProjectMeats/discussions)

---

**Need platform-specific help?**
- Windows users: See [Windows Production Deployment Guide](windows_production_deployment.md)
- Linux users: See [Production Checklist](../production_checklist.md)