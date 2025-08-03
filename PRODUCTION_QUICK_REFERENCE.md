# ProjectMeats Production Deployment - Quick Reference

## 🚀 One-Command Setup

### Fresh Server Deployment
```bash
# Download and run automated setup
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/setup_production_infrastructure.sh | sudo bash -s yourdomain.com

# Then deploy the application
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_server.sh | sudo bash
```

### With Existing Repository
```bash
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Setup infrastructure first
sudo ./setup_production_infrastructure.sh yourdomain.com

# Deploy application
sudo ./deploy_server.sh
```

## 🔄 Post-Merge Updates

### After Repository Merges (Recommended)
```bash
# Clean update that handles conflicts and ensures clean state
sudo /home/projectmeats/clean_update.sh
```

### Regular Updates
```bash
# Standard update for minor changes
sudo /home/projectmeats/scripts/update.sh

# Or use clean update option
sudo /home/projectmeats/scripts/update.sh --clean
```

## 📋 Key Documentation

| Guide | Purpose |
|-------|---------|
| **PRODUCTION_DEPLOYMENT_SIMPLIFIED.md** | Main deployment guide with all steps |
| **PRODUCTION_REQUIREMENTS.md** | Complete infrastructure setup (PostgreSQL, Redis, etc.) |
| **clean_update.sh** | Script for clean post-merge updates |
| **setup_production_infrastructure.sh** | Automated infrastructure setup |

## 🛠️ Infrastructure Components

### Automated Setup Includes:
- ✅ **PostgreSQL** - Production database with optimizations
- ✅ **Redis** - Caching server with security
- ✅ **Nginx** - Web server with SSL and performance tuning
- ✅ **SSL Certificates** - Let's Encrypt with auto-renewal
- ✅ **Security** - UFW firewall + Fail2Ban protection
- ✅ **Monitoring** - Health checks and automated backups
- ✅ **Log Management** - Rotation and cleanup

### Manual Verification Commands:
```bash
# Check all services
sudo systemctl status projectmeats nginx postgresql redis

# Check application
curl -I https://yourdomain.com

# Check SSL
sudo certbot certificates

# View system status
sudo /home/projectmeats/scripts/status.sh
```

## 🚨 Emergency Procedures

### Quick Service Restart
```bash
sudo systemctl restart projectmeats nginx postgresql redis
```

### Rollback Application
```bash
cd /home/projectmeats/app
sudo -u projectmeats git log --oneline -5  # Find previous commit
sudo -u projectmeats git checkout COMMIT_HASH
sudo systemctl restart projectmeats
```

### Restore Database
```bash
# Find backup
ls /home/projectmeats/backups/

# Restore (replace TIMESTAMP with actual backup timestamp)
sudo systemctl stop projectmeats
gunzip -c /home/projectmeats/backups/database_TIMESTAMP.sql.gz | \
sudo -u projectmeats psql -h localhost -U projectmeats_user -d projectmeats_prod
sudo systemctl start projectmeats
```

## 📊 Monitoring & Logs

### Log Locations
- **Application**: `/home/projectmeats/logs/gunicorn_error.log`
- **Nginx**: `/var/log/nginx/error.log`
- **PostgreSQL**: `/var/log/postgresql/`
- **System**: `journalctl -u projectmeats -f`

### Monitoring Commands
```bash
# System status
sudo /home/projectmeats/scripts/status.sh

# Real-time logs
tail -f /home/projectmeats/logs/gunicorn_error.log

# Service logs
sudo journalctl -u projectmeats -f

# Database status
sudo -u postgres psql -c "SELECT version();"
```

## 🔧 Configuration Files

### Environment Variables
- **Backend**: `/home/projectmeats/app/backend/.env`
- **Frontend**: `/home/projectmeats/app/frontend/.env.production`
- **Database**: `/home/projectmeats/config/database.env`
- **Redis**: `/home/projectmeats/config/redis.env`

### Service Files
- **Application Service**: `/etc/systemd/system/projectmeats.service`
- **Nginx Config**: `/etc/nginx/sites-available/projectmeats`
- **Gunicorn Config**: `/home/projectmeats/app/backend/gunicorn.conf.py`

## 🎯 Success Checklist

After deployment, verify:
- [ ] Website loads: `https://yourdomain.com`
- [ ] Admin panel works: `https://yourdomain.com/admin/`
- [ ] API docs available: `https://yourdomain.com/api/docs/`
- [ ] SSL certificate valid (A+ rating)
- [ ] All services running: `sudo systemctl status projectmeats nginx postgresql redis`
- [ ] Backups configured: `ls /home/projectmeats/backups/`
- [ ] Monitoring active: `sudo /home/projectmeats/scripts/status.sh`

## 💡 Best Practices

### Regular Maintenance
- Use `clean_update.sh` after merging repository changes
- Check logs weekly: `tail -f /home/projectmeats/logs/gunicorn_error.log`
- Monitor disk space: `df -h`
- Test backups monthly
- Update system packages: `sudo apt update && sudo apt upgrade`

### Performance Optimization
- Monitor database connections: `sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"`
- Check Redis memory: `redis-cli info memory`
- Review Nginx logs for slow requests
- Use the monitoring script: `/home/projectmeats/system_monitor.sh`

### Security
- Review Fail2Ban logs: `sudo fail2ban-client status`
- Check SSL expiration: `sudo certbot certificates`
- Monitor unauthorized access attempts in `/var/log/auth.log`
- Keep system packages updated

---

## 📞 Support

- **Documentation**: All guides in repository root and `/docs` folder
- **Logs**: Check `/home/projectmeats/logs/` for application logs
- **Status**: Run `sudo /home/projectmeats/scripts/status.sh` for system overview
- **Configuration**: Infrastructure summary at `/home/projectmeats/INFRASTRUCTURE_SUMMARY.md`

**🎉 Your ProjectMeats production environment is ready for business!**