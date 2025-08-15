# ProjectMeats Production Deployment Guide

**🎯 One Guide, One Script, One Command - Everything You Need**

This is the **ONLY** deployment guide you need. All other deployment documents have been consolidated into this single, comprehensive guide.

---

## 🚀 Quick Start (3 Options)

### Option 1: AI-Driven Deployment (NEW - Recommended)
```bash
# On your local machine:
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Setup AI deployment system
python setup_ai_deployment.py

# Deploy with intelligent error handling and recovery
./ai_deploy.sh --interactive
```

**This AI-powered deployment provides:**
- **Intelligent Error Detection**: Automatically detects and recovers from deployment issues
- **Dynamic Terminal Session Management**: Handles interactive prompts and real-time monitoring
- **Autonomous Error Recovery**: Fixes common problems without human intervention
- **Resumable Deployments**: Continue from where you left off if something fails
- **Comprehensive Monitoring**: Real-time progress tracking and detailed logging

### Option 2: Fully Automated (Classic)
```bash
# On your production server (Ubuntu 20.04+):
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/one_click_deploy.sh | sudo bash
```

**This one command will:**
- Install all dependencies (Python, Node.js, Nginx, PostgreSQL)
- Handle all Node.js conflicts automatically
- Download and configure ProjectMeats
- Set up SSL certificates
- Configure security (firewall, fail2ban)
- Start all services
- Create admin user

### Option 3: Upload and Deploy
```bash
# 1. On your local machine:
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats
python3 master_deploy.py  # Generates all configs

# 2. Upload to server:
scp -r . user@yourdomain.com:/opt/projectmeats

# 3. On your server:
ssh user@yourdomain.com
cd /opt/projectmeats
sudo ./master_deploy.py --server
```

---

## 🏗️ What You Need

### Server Requirements
- **Ubuntu 20.04+ LTS** (recommended)
- **2+ vCPU, 4+ GB RAM, 20+ GB storage**
- **Root or sudo access**
- **Domain name** pointing to server IP

### Recommended Hosting Providers
| Provider | Cost/Month | Best For |
|----------|------------|----------|
| **DigitalOcean** | $20 | Easy setup, great docs |
| **Linode** | $20 | Performance, reliability |
| **Vultr** | $20 | Global locations |
| **Hetzner** | $15 | EU hosting, value |

---

## 🔧 The Node.js Problem (And How We Fix It)

**You're seeing this error?**
```
nodejs : Conflicts: npm
npm : Depends: node-cacache but it is not going to be installed
E: Unable to correct problems, you have held broken packages.
```

**Our solution handles this automatically by:**
1. **Complete cleanup** - Removes ALL Node.js packages and files
2. **Multiple fallback methods** - Tries 3 different installation approaches
3. **Smart detection** - Tests each method before proceeding
4. **User configuration** - Sets up npm properly for your user

---

## 📋 What Gets Deployed

After deployment, you'll have:

- **Frontend**: React app at `https://yourdomain.com`
- **Admin Panel**: Django admin at `https://yourdomain.com/admin/`
- **API Docs**: Swagger docs at `https://yourdomain.com/api/docs/`
- **SSL**: Let's Encrypt certificates (auto-renewing)
- **Security**: Firewall, Fail2Ban, security headers
- **Backups**: Daily automated database backups
- **Monitoring**: Service health checks

### Default Admin User
- **Username**: `admin`
- **Password**: `ProjectMeats2024!` (change after first login)
- **Email**: `admin@yourdomain.com`

---

## 🛠️ Detailed Steps (If You Want Manual Control)

### Step 1: Prepare Your Server

**Create a server with your preferred provider:**
1. Choose Ubuntu 20.04+ LTS
2. Select at least 2 vCPU, 4GB RAM
3. Set up SSH key authentication
4. Point your domain to the server IP

### Step 2: Run Master Deployment

```bash
# SSH into your server
ssh root@yourdomain.com  # or your sudo user

# Download and run master deployment
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/master_deploy.py | python3 - --domain=yourdomain.com
```

**Or for more control:**
```bash
# Clone repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Run interactive setup
python3 master_deploy.py
```

### Step 3: Verify Deployment

```bash
# Check all services
systemctl status projectmeats nginx postgresql

# Test the application
curl -k https://yourdomain.com
curl -k https://yourdomain.com/api/docs/

# View logs if needed
tail -f /opt/projectmeats/logs/application.log
```

---

## 🔍 Troubleshooting

### Issue: "Can't connect to domain"
**Cause**: DNS not propagated or firewall blocking
**Fix**: 
```bash
# Check DNS
nslookup yourdomain.com

# Check firewall
ufw status

# Check if services are running
systemctl status nginx projectmeats
```

### Issue: "SSL certificate failed"
**Cause**: Domain DNS not pointing to server
**Fix**:
```bash
# Wait for DNS propagation (up to 48 hours)
# Or run SSL setup manually:
certbot --nginx -d yourdomain.com
```

### Issue: "Node.js installation failed"
**Cause**: Package conflicts (the error you've been seeing)
**Fix**: Our script handles this automatically, but manually:
```bash
# Complete Node.js cleanup and reinstall
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/fix_nodejs.sh | sudo bash
```

### Issue: "Database connection failed"
**Cause**: PostgreSQL not configured properly
**Fix**:
```bash
# Reset database setup
sudo systemctl restart postgresql
sudo -u postgres createdb projectmeats
sudo systemctl restart projectmeats
```

### Issue: "Permission denied"
**Cause**: Incorrect file permissions
**Fix**:
```bash
# Fix permissions
chown -R projectmeats:projectmeats /opt/projectmeats
chmod +x /opt/projectmeats/scripts/*
```

---

## 🔒 Security Features

**Automatically configured:**
- **SSL/HTTPS**: Let's Encrypt certificates with auto-renewal
- **Firewall**: UFW configured (SSH, HTTP, HTTPS only)
- **Fail2Ban**: Prevents brute force attacks
- **Security Headers**: HSTS, XSS protection, etc.
- **Database Security**: Secure passwords, limited permissions
- **File Uploads**: Secure validation and storage

---

## 🚨 Emergency Commands

**If something goes wrong:**

```bash
# Restart everything
systemctl restart projectmeats nginx postgresql

# Check what's broken
systemctl status projectmeats
journalctl -u projectmeats -f

# Reset to clean state (CAREFUL - this removes data)
rm -rf /opt/projectmeats
# Then re-run deployment
```

**Get help:**
```bash
# Check deployment status
/opt/projectmeats/scripts/status.sh

# View all logs
/opt/projectmeats/scripts/show_logs.sh

# Test configuration
/opt/projectmeats/scripts/test_config.sh
```

---

## 🎯 Success Checklist

After deployment, verify these work:

- [ ] **Website loads**: `https://yourdomain.com` shows React app
- [ ] **Admin access**: `https://yourdomain.com/admin/` with admin credentials
- [ ] **API works**: `https://yourdomain.com/api/docs/` shows Swagger docs
- [ ] **SSL valid**: No browser warnings, green lock icon
- [ ] **Services running**: All systemctl status commands show "active"
- [ ] **Backups working**: Check `/opt/projectmeats/backups/` for files

---

## 📞 Support

**If you're still having issues:**

1. **Check logs**: `/opt/projectmeats/logs/deployment.log`
2. **Run diagnostics**: `/opt/projectmeats/scripts/diagnose.sh`
3. **View configuration**: `cat /opt/projectmeats/config/deployment.json`

**Common issues and solutions have been automated away**, but if you encounter something new, the scripts generate detailed logs for troubleshooting.

---

## 🎉 You're Done!

**Congratulations!** Your ProjectMeats application is now running in production with:

- ✅ **Professional UI** at your domain
- ✅ **Secure HTTPS** with auto-renewing certificates
- ✅ **Complete API** with documentation
- ✅ **Admin interface** for management
- ✅ **Automated backups** and monitoring
- ✅ **Enterprise security** configuration

**Time to deployment**: 15-30 minutes  
**Monthly cost**: $15-25 with recommended providers  
**Maintenance**: Automated - just check once per month  

Your business management application is ready to use! 🚀