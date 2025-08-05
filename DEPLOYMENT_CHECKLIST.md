# 🚀 ProjectMeats Deployment Checklist & Quick Commands

## 📋 Pre-Deployment Checklist

### ✅ Server Requirements
- [ ] **Server**: Ubuntu 20.04+ with root access
- [ ] **Resources**: 2 CPU, 4GB RAM, 80GB SSD minimum
- [ ] **Network**: Public IP address
- [ ] **Domain**: Domain name pointing to server IP

### ✅ Domain Configuration
```bash
# Add these DNS records:
A     yourdomain.com      → SERVER_IP_ADDRESS
A     www.yourdomain.com  → SERVER_IP_ADDRESS
```

---

## 🎯 Quick Deployment Commands

### **Option 1: One-Command Deployment (RECOMMENDED)**
```bash
# Download and run the quick deployment script
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/quick_production_deploy.sh -o deploy.sh
sudo bash deploy.sh yourdomain.com
```

### **Option 2: Use Unified Deployment Tool**
```bash
# Download the unified tool
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/unified_deployment_tool.py -o deploy.py

# Interactive deployment
sudo python3 deploy.py --production --interactive

# Automated deployment
sudo python3 deploy.py --production --domain=yourdomain.com --auto
```

### **Option 3: Manual Git Clone Method**
```bash
# Clone repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Run deployment
sudo python3 unified_deployment_tool.py --production --domain=yourdomain.com --auto
```

---

## 🐘 PostgreSQL Database Setup

### Automated (Included in deployment scripts)
The deployment scripts automatically:
- ✅ Install PostgreSQL 13+
- ✅ Create `projectmeats` database
- ✅ Create application user with secure password  
- ✅ Configure authentication and permissions
- ✅ Test connectivity
- ✅ Run Django migrations

### Manual PostgreSQL Setup (if needed)
```bash
# Install PostgreSQL
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE projectmeats;
CREATE USER projectmeats_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE projectmeats TO projectmeats_user;
ALTER USER projectmeats_user CREATEDB;
\q
EOF

# Test connection
PGPASSWORD='your_secure_password' psql -h localhost -U projectmeats_user -d projectmeats -c 'SELECT version();'
```

---

## ✅ Post-Deployment Verification

### Check URLs
```bash
# These should all work after deployment:
curl -k https://yourdomain.com                 # Frontend
curl -k https://yourdomain.com/admin/          # Django admin  
curl -k https://yourdomain.com/api/docs/       # API documentation
curl -k https://yourdomain.com/api/health/     # Health check
```

### Check Services
```bash
# Verify all services are running:
sudo systemctl status projectmeats
sudo systemctl status nginx
sudo systemctl status postgresql

# Check logs if needed:
sudo journalctl -u projectmeats -f
sudo tail -f /var/log/nginx/error.log
```

### Default Admin Access
```
URL: https://yourdomain.com/admin/
Username: admin
Password: WATERMELON1219

⚠️ CHANGE THIS PASSWORD IMMEDIATELY AFTER LOGIN!
```

---

## 🛠️ Troubleshooting Commands

### Service Management
```bash
# Restart services
sudo systemctl restart projectmeats
sudo systemctl restart nginx
sudo systemctl restart postgresql

# Check service status
sudo systemctl status projectmeats nginx postgresql

# View logs
sudo journalctl -u projectmeats -n 50
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Troubleshooting
```bash
# Check database connection
sudo -u postgres psql -c "SELECT version();"

# Check if projectmeats database exists
sudo -u postgres psql -l | grep projectmeats

# Connect to database
sudo -u postgres psql projectmeats
```

### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/projectmeats

# Fix permissions
sudo chmod +x /opt/projectmeats/ProjectMeats/backend/manage.py
```

---

## 📊 Health Check Script

Create this script to monitor your deployment:

```bash
# Create health check script
cat > /opt/health_check.sh << 'EOF'
#!/bin/bash
echo "=== ProjectMeats Health Check ==="
echo "Date: $(date)"
echo ""

# Check services
echo "🔧 Services:"
systemctl is-active --quiet projectmeats && echo "✅ ProjectMeats: Running" || echo "❌ ProjectMeats: Stopped"
systemctl is-active --quiet nginx && echo "✅ Nginx: Running" || echo "❌ Nginx: Stopped"  
systemctl is-active --quiet postgresql && echo "✅ PostgreSQL: Running" || echo "❌ PostgreSQL: Stopped"
echo ""

# Check website
echo "🌐 Website:"
curl -f -s -o /dev/null https://yourdomain.com && echo "✅ Frontend: Accessible" || echo "❌ Frontend: Not accessible"
curl -f -s -o /dev/null https://yourdomain.com/admin/ && echo "✅ Admin: Accessible" || echo "❌ Admin: Not accessible"
curl -f -s -o /dev/null https://yourdomain.com/api/docs/ && echo "✅ API Docs: Accessible" || echo "❌ API Docs: Not accessible"
echo ""

# Check disk space
echo "💾 Disk Usage:"
df -h /opt/projectmeats | tail -1
echo ""

# Check memory
echo "🧠 Memory Usage:"
free -h | grep Mem
EOF

sudo chmod +x /opt/health_check.sh
```

Run health check:
```bash
sudo /opt/health_check.sh
```

---

## 🎉 Success Indicators

After successful deployment, you should have:

- ✅ **Website accessible** at `https://yourdomain.com`
- ✅ **SSL certificate** working (green lock in browser)
- ✅ **Admin interface** at `https://yourdomain.com/admin/`
- ✅ **API documentation** at `https://yourdomain.com/api/docs/`
- ✅ **PostgreSQL database** running and configured
- ✅ **Automated backups** configured
- ✅ **Security hardening** applied (firewall, fail2ban)
- ✅ **Monitoring** and health checks active

---

## 📞 Support

If you encounter issues:

1. **Run health check**: `sudo /opt/health_check.sh`
2. **Check logs**: `sudo journalctl -u projectmeats -n 50`
3. **Verify services**: `sudo systemctl status projectmeats nginx postgresql`
4. **Review this checklist** for missed steps
5. **Check deployment logs**: Look in `/opt/projectmeats/logs/`

**Remember: Your codebase is production-ready. Any issues are infrastructure-related and can be resolved with proper server setup.**