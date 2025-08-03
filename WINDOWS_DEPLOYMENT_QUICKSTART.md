# Windows Production Deployment - Quick Start

## 🚀 For Windows Users Deploying to Production

### Option 1: One-Click Batch Deployment (Easiest)

1. **Download the batch launcher:**
   ```cmd
   curl -o setup_windows_production.bat https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/setup_windows_production.bat
   ```

2. **Run as Administrator:**
   - Right-click `setup_windows_production.bat`
   - Select "Run as administrator"
   - Follow the interactive prompts

### Option 2: PowerShell Direct Deployment

1. **Download and run:**
   ```powershell
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_windows_production.ps1" -OutFile "deploy_windows_production.ps1"
   .\deploy_windows_production.ps1 -Interactive
   ```

### Option 3: Using Unified Tool

1. **Clone repository:**
   ```cmd
   git clone https://github.com/Vacilator/ProjectMeats.git
   cd ProjectMeats
   ```

2. **Run unified deployment:**
   ```cmd
   python unified_deployment_tool.py --production --interactive
   ```

### Validation Before Deployment

**Check if your system is ready:**
```cmd
python validate_windows_production.py
```

### What Gets Installed Automatically

- ✅ Python 3.9+ (via Chocolatey)
- ✅ Node.js 16+ (via Chocolatey)
- ✅ Git (via Chocolatey)
- ✅ PostgreSQL 13+ (via Chocolatey)
- ✅ Nginx web server (via Chocolatey)
- ✅ NSSM service manager (via Chocolatey)
- ✅ ProjectMeats application
- ✅ Windows services configuration
- ✅ Firewall rules for HTTP/HTTPS
- ✅ SSL certificates (self-signed for dev, Let's Encrypt for prod)

### Access Your Deployment

After successful deployment:
- **Frontend:** https://yourdomain.com/
- **API:** https://yourdomain.com/api/v1/
- **Admin:** https://yourdomain.com/admin/

**Default login:** admin / WATERMELON1219

### Need Help?

- **Full Guide:** [Windows Production Deployment Guide](docs/windows_production_deployment.md)
- **Issues:** [GitHub Issues](https://github.com/Vacilator/ProjectMeats/issues)
- **General Info:** [Main README](README.md)

---

**✨ That's it! Windows production deployment is now as easy as Linux deployment.**