# ProjectMeats Production Deployment - Simplified Guide

🎯 **Objective**: Get ProjectMeats running in production with minimal steps and maximum reliability.

## ⚡ Quick Start (30 Minutes)

### 1. Server Requirements
- **Operating System**: Ubuntu 20.04+ LTS  
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 50GB SSD minimum
- **Network**: Domain name pointing to server IP

### 2. One-Command Deployment

For servers **without** existing Node.js/NVM conflicts:
```bash
# Download and run deployment script
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_server.sh | sudo bash
```

For servers **with** existing NVM/Node.js installations:
```bash
# Clone repository and run deployment
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats
sudo ./deploy_server.sh
```

### 3. Access Your Application
- **Website**: https://yourdomain.com
- **Admin Panel**: https://yourdomain.com/admin/
- **API Docs**: https://yourdomain.com/api/docs/

---

## 🔧 Production Infrastructure Setup

### Prerequisites Installation

Run this script to install all production requirements:

```bash
#!/bin/bash
# ProductionMeats Infrastructure Setup
set -e

echo "🚀 Setting up ProjectMeats production infrastructure..."

# Update system
apt update && apt upgrade -y

# Install core packages
apt install -y \
    python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx redis-server \
    git curl wget \
    ufw fail2ban \
    certbot python3-certbot-nginx

# Install Node.js 18 LTS (avoiding conflicts)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt install -y nodejs

echo "✅ Infrastructure setup complete!"
```

### PostgreSQL Production Setup

```bash
#!/bin/bash
# PostgreSQL Production Configuration

# Create database and user
sudo -u postgres createdb projectmeats_prod
sudo -u postgres createuser projectmeats_user
sudo -u postgres psql << EOF
ALTER USER projectmeats_user PASSWORD 'CHANGE_THIS_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod TO projectmeats_user;
ALTER USER projectmeats_user CREATEDB;
\q
EOF

# Production optimization
sudo tee -a /etc/postgresql/*/main/postgresql.conf << EOF
# Production Performance Settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
max_connections = 100
EOF

# Restart PostgreSQL
sudo systemctl restart postgresql
sudo systemctl enable postgresql

echo "✅ PostgreSQL configured for production"
```

### Redis Cache Setup

```bash
#!/bin/bash
# Redis Production Configuration

# Configure Redis for caching
sudo tee -a /etc/redis/redis.conf << EOF
# Memory optimization
maxmemory 256mb
maxmemory-policy allkeys-lru

# Security
bind 127.0.0.1
requirepass your_redis_password

# Persistence (disabled for cache-only usage)
save ""
appendonly no
EOF

sudo systemctl restart redis
sudo systemctl enable redis

echo "✅ Redis configured for production"
```

---

## 🔄 Post-Merge Update Process

### Clean Update Script

Create this script to handle clean updates after repository merges:

```bash
#!/bin/bash
# ProjectMeats Clean Update Script
# Use this after merging changes to get a clean deployment

set -e
echo "🔄 Starting clean update process..."

# Configuration
APP_DIR="/home/projectmeats/app"
BACKUP_DIR="/home/projectmeats/backups"
LOG_FILE="/home/projectmeats/logs/update.log"

# Create backup before update
echo "📦 Creating backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup database
sudo -u projectmeats pg_dump -h localhost -U projectmeats_user projectmeats_prod | gzip > "$BACKUP_DIR/pre_update_db_$timestamp.sql.gz"

# Backup current application
tar -czf "$BACKUP_DIR/pre_update_app_$timestamp.tar.gz" -C /home/projectmeats app

echo "✅ Backup created: $timestamp"

# Stop services during update
echo "⏸️ Stopping services..."
sudo systemctl stop projectmeats

# Clean update process
echo "🧹 Performing clean update..."
cd "$APP_DIR"

# Stash any local changes
sudo -u projectmeats git stash

# Force clean state
sudo -u projectmeats git reset --hard HEAD
sudo -u projectmeats git clean -fd

# Pull latest changes
sudo -u projectmeats git pull origin main

# Clean Python cache and dependencies
echo "🐍 Cleaning Python environment..."
cd backend
sudo -u projectmeats find . -name "*.pyc" -delete
sudo -u projectmeats find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
sudo -u projectmeats ./venv/bin/pip install --upgrade pip
sudo -u projectmeats ./venv/bin/pip install -r requirements.txt --force-reinstall

# Clean and rebuild frontend
echo "⚛️ Cleaning frontend environment..."
cd ../frontend
sudo -u projectmeats rm -rf node_modules package-lock.json
sudo -u projectmeats npm cache clean --force
sudo -u projectmeats npm install
sudo -u projectmeats npm run build

# Run database migrations
echo "🗄️ Applying database migrations..."
cd ../backend
sudo -u projectmeats ./venv/bin/python manage.py migrate

# Collect static files
sudo -u projectmeats ./venv/bin/python manage.py collectstatic --noinput --clear

# Fix permissions
echo "🔧 Fixing permissions..."
sudo chown -R projectmeats:projectmeats /home/projectmeats/
sudo chmod -R 755 /home/projectmeats/app
sudo chmod -R 755 /home/projectmeats/uploads

# Restart services
echo "🚀 Restarting services..."
sudo systemctl start projectmeats
sudo systemctl reload nginx

# Verify deployment
echo "✅ Verifying deployment..."
sleep 5

if systemctl is-active --quiet projectmeats; then
    echo "✅ ProjectMeats service is running"
else
    echo "❌ ProjectMeats service failed to start"
    echo "📋 Recent logs:"
    sudo journalctl -u projectmeats -n 20 --no-pager
    exit 1
fi

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx service is running"
else
    echo "❌ Nginx service failed"
    sudo systemctl status nginx --no-pager
    exit 1
fi

# Test application response
if curl -f -s http://localhost:8000/health/ >/dev/null; then
    echo "✅ Application responding correctly"
else
    echo "❌ Application not responding"
    echo "📋 Application logs:"
    tail -20 /home/projectmeats/logs/gunicorn_error.log
    exit 1
fi

echo ""
echo "🎉 Clean update completed successfully!"
echo "📊 Update summary:"
echo "   - Backup created: $timestamp"
echo "   - Git repository: $(cd $APP_DIR && sudo -u projectmeats git rev-parse --short HEAD)"
echo "   - Services: All running"
echo "   - Application: Responding"
echo ""
echo "🌐 Your application is available at:"
echo "   - Website: https://$(hostname -f || echo 'your-domain.com')"
echo "   - Admin: https://$(hostname -f || echo 'your-domain.com')/admin/"

# Log successful update
echo "$(date): Clean update completed successfully" >> "$LOG_FILE"
```

Save this as `/home/projectmeats/clean_update.sh` and make it executable:

```bash
sudo chmod +x /home/projectmeats/clean_update.sh
```

### Usage After Repository Merges

1. **SSH into your production server**
2. **Run the clean update script**:
   ```bash
   sudo /home/projectmeats/clean_update.sh
   ```
3. **Verify everything is working**:
   ```bash
   sudo /home/projectmeats/scripts/status.sh
   ```

---

## 🔒 Security & SSL Setup

### Automatic SSL Certificate

```bash
# Install SSL certificate with Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com \
    --agree-tos --email admin@yourdomain.com --non-interactive

# Setup automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Firewall Configuration

```bash
# Basic firewall setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

### Fail2Ban Protection

```bash
# Configure Fail2Ban for additional security
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
maxretry = 3

[nginx-req-limit]
enabled = true
filter = nginx-req-limit
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 600
bantime = 7200
EOF

sudo systemctl restart fail2ban
```

---

## 📊 Monitoring & Maintenance

### Daily Health Check

Add to crontab (`crontab -e`):
```bash
# Daily health check at 6 AM
0 6 * * * /home/projectmeats/scripts/status.sh > /home/projectmeats/logs/daily_status.log 2>&1

# Database backup every 6 hours
0 */6 * * * /home/projectmeats/backup_database.sh

# Log cleanup monthly
0 0 1 * * find /home/projectmeats/logs -name "*.log" -mtime +30 -delete
```

### Quick Troubleshooting Commands

```bash
# Check all services
sudo systemctl status projectmeats nginx postgresql redis

# View recent logs
sudo journalctl -u projectmeats -f
tail -f /home/projectmeats/logs/gunicorn_error.log

# Test database connection
sudo -u projectmeats psql -h localhost -U projectmeats_user -d projectmeats_prod -c "SELECT version();"

# Restart everything
sudo systemctl restart projectmeats nginx
```

---

## 🚨 Emergency Procedures

### Rollback to Previous Version

```bash
# If something goes wrong, rollback quickly
cd /home/projectmeats/app
sudo -u projectmeats git log --oneline -10  # Find previous commit
sudo -u projectmeats git checkout PREVIOUS_COMMIT_HASH
sudo systemctl restart projectmeats
```

### Restore from Backup

```bash
# Restore database from backup
sudo systemctl stop projectmeats
sudo -u projectmeats gunzip -c /home/projectmeats/backups/pre_update_db_TIMESTAMP.sql.gz | \
    sudo -u projectmeats psql -h localhost -U projectmeats_user -d projectmeats_prod
sudo systemctl start projectmeats
```

---

## 📋 Production Checklist

### Initial Deployment
- [ ] Server provisioned with Ubuntu 20.04+
- [ ] Domain DNS pointing to server IP
- [ ] Infrastructure packages installed
- [ ] PostgreSQL configured and secured
- [ ] SSL certificate installed and working
- [ ] Firewall configured and enabled
- [ ] Application deployed and running
- [ ] Backups configured and tested

### After Each Update
- [ ] Clean update script completed successfully
- [ ] All services running (`systemctl status`)
- [ ] Website accessible via HTTPS
- [ ] Admin panel working
- [ ] API endpoints responding
- [ ] Database migrations applied
- [ ] No error logs in recent entries

### Monthly Maintenance
- [ ] Update system packages (`apt update && apt upgrade`)
- [ ] Check disk space (`df -h`)
- [ ] Review security logs (`fail2ban-client status`)
- [ ] Test backup restoration procedure
- [ ] Review and clean old log files

---

## 🎯 Success Metrics

After deployment, you should have:
- ✅ **Response Time**: < 2 seconds page load
- ✅ **Uptime**: 99.9% availability 
- ✅ **Security**: A+ SSL rating
- ✅ **Backups**: Automated daily backups
- ✅ **Monitoring**: Health checks every 5 minutes
- ✅ **Updates**: Clean update process in < 10 minutes

---

**🎉 Congratulations! Your ProjectMeats production environment is ready for business.**

For support, check logs in `/home/projectmeats/logs/` or run the status script: `sudo /home/projectmeats/scripts/status.sh`