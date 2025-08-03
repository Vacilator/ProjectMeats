# 🚀 ProjectMeats Unified Deployment Guide

**THE ONLY DEPLOYMENT GUIDE YOU NEED**

This guide consolidates ALL deployment methods, documentation, and instructions into one comprehensive resource. All other deployment files have been streamlined into the unified `master_deploy.py` system.

---

## 📋 Quick Reference

| Deployment Type | Command | Use Case |
|----------------|---------|----------|
| **🎯 Production** | `sudo python3 master_deploy.py --auto --domain=yourdomain.com` | Complete production deployment |
| **🧙‍♂️ Interactive Wizard** | `sudo python3 master_deploy.py --wizard` | Step-by-step guided setup |
| **🐳 Docker** | `sudo python3 master_deploy.py --docker --domain=yourdomain.com` | Container-based deployment |
| **🐘 PostgreSQL Setup** | `sudo python3 master_deploy.py --setup-postgres --interactive` | Database configuration only |
| **📊 Monitoring Only** | `sudo python3 master_deploy.py --monitoring --domain=yourdomain.com` | Health checks and alerts |

---

## 🎯 Deployment Options

### 1. 🚀 Full Production Deployment (Recommended)

Complete automated production deployment with all features:

```bash
# Basic production deployment
sudo python3 master_deploy.py --auto --domain=yourdomain.com

# With GitHub authentication
sudo python3 master_deploy.py --auto \
  --domain=yourdomain.com \
  --github-user=your-username \
  --github-token=your-token

# Custom configuration
sudo python3 master_deploy.py --auto \
  --domain=yourdomain.com \
  --env=production \
  --database=postgresql \
  --project-dir=/opt/projectmeats
```

**What this includes:**
- ✅ System dependencies (Python, Node.js, PostgreSQL, Nginx)
- ✅ Automatic Node.js conflict resolution
- ✅ SSL certificates via Let's Encrypt
- ✅ Security hardening (firewall, fail2ban)
- ✅ PostgreSQL database with secure configuration
- ✅ Admin user creation
- ✅ Monitoring and health checks
- ✅ Automated backups
- ✅ Production optimizations

### 2. 🧙‍♂️ Interactive Deployment Wizard

Step-by-step guided deployment with explanations:

```bash
sudo python3 master_deploy.py --wizard
```

**The wizard will guide you through:**
1. 📋 Environment selection (Production/Staging/Development)
2. 🔧 Deployment method (Standard/Docker/Cloud)
3. 🐘 Database configuration with PostgreSQL setup guide
4. 🌐 Domain and SSL configuration
5. 🔒 Security settings
6. 📊 Final review and deployment

### 3. 🐳 Docker Deployment

Modern container-based deployment with docker-compose:

```bash
# Docker deployment
sudo python3 master_deploy.py --docker --domain=yourdomain.com

# Docker with monitoring
sudo python3 master_deploy.py --docker --domain=yourdomain.com --monitoring
```

**Docker deployment includes:**
- 🐳 Multi-container setup (Django, React, PostgreSQL, Redis, Nginx)
- 📊 Built-in monitoring (Prometheus, Grafana)
- 🔄 Auto-restart and health checks
- 📦 Optimized for scalability
- 🔒 Security best practices

### 4. 🔄 CI/CD Pipeline Integration

Automated deployment with GitHub Actions integration:

```bash
# Setup CI/CD hooks
sudo python3 master_deploy.py --ci-cd --domain=yourdomain.com

# Combined with standard deployment
sudo python3 master_deploy.py --auto --ci-cd --domain=yourdomain.com
```

**CI/CD features:**
- 🔗 GitHub webhook integration
- 🔄 Automatic deployment on push to main
- 📊 Health checks after deployment
- 🛡️ Rollback capabilities
- 📧 Alert notifications

---

## 🐘 PostgreSQL Configuration Guide

### Interactive PostgreSQL Setup

For detailed PostgreSQL configuration with step-by-step guidance:

```bash
sudo python3 master_deploy.py --setup-postgres --interactive
```

### What the PostgreSQL Setup Includes:

1. **🔧 Installation & Configuration**
   - PostgreSQL 13+ installation
   - Service configuration and startup
   - Security hardening

2. **🗄️ Database Setup**
   - Creates `projectmeats` database
   - Configures application user with proper permissions
   - Generates secure random password
   - Tests connectivity

3. **🔒 Security Configuration**
   - Proper authentication setup
   - Connection restrictions
   - Backup user configuration

4. **✅ Validation**
   - Connection testing
   - Permission verification
   - Performance optimization

### Manual PostgreSQL Setup

If you need to configure PostgreSQL manually:

```bash
# Install PostgreSQL
sudo apt update && sudo apt install -y postgresql postgresql-contrib

# Access PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE projectmeats;
CREATE USER projectmeats_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE projectmeats TO projectmeats_user;
ALTER USER projectmeats_user CREATEDB;
\q

# Test connection
PGPASSWORD='secure_password' psql -h localhost -U projectmeats_user -d projectmeats -c 'SELECT version();'
```

---

## 🔧 Environment Configuration

### Production Environment
```bash
# Full production setup
sudo python3 master_deploy.py --auto --env=production --domain=yourdomain.com

# Features: SSL, security hardening, monitoring, backups
```

### Staging Environment
```bash
# Staging environment
sudo python3 master_deploy.py --auto --env=staging --domain=staging.yourdomain.com

# Features: Similar to production but with debug logging
```

### Development Environment
```bash
# Development setup
sudo python3 master_deploy.py --auto --env=development --domain=dev.yourdomain.com

# Features: Debug mode, SQLite option, development tools
```

---

## 📊 Monitoring & Health Checks

### Setup Monitoring System

```bash
# Monitoring and alerts only
sudo python3 master_deploy.py --monitoring --domain=yourdomain.com

# Combined with deployment
sudo python3 master_deploy.py --auto --monitoring --domain=yourdomain.com
```

### Health Check Endpoints

After deployment, these endpoints are available:

- **System Health**: `https://yourdomain.com/health`
- **API Health**: `https://yourdomain.com/api/health/`
- **Database Health**: `https://yourdomain.com/api/health/db/`

### Manual Health Checks

```bash
# System status
/opt/projectmeats/scripts/status.sh

# Detailed health check
/opt/projectmeats/scripts/health_check.py

# Service status
systemctl status projectmeats nginx postgresql
```

---

## 🔒 Security Features

All deployments include comprehensive security:

### 🛡️ Firewall Configuration
- UFW firewall with minimal open ports
- Only HTTP (80), HTTPS (443), and SSH (22) allowed
- Rate limiting on API endpoints

### 🔐 SSL/TLS Configuration
- Automatic Let's Encrypt certificates
- HTTPS enforcement
- Security headers (HSTS, CSP, etc.)
- Auto-renewal setup

### 🚨 Intrusion Prevention
- Fail2Ban for SSH and web attacks
- Rate limiting on API endpoints
- Security monitoring and alerts

### 🔑 Access Control
- Application user with minimal privileges
- Secure database authentication
- Regular security updates

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Node.js Conflicts
```bash
# The deployment script automatically handles Node.js conflicts
# Manual fix if needed:
sudo apt remove -y nodejs npm
sudo python3 master_deploy.py --prepare-server
```

#### 2. PostgreSQL Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Reset PostgreSQL setup
sudo python3 master_deploy.py --setup-postgres --interactive
```

#### 3. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew --dry-run
```

#### 4. Service Issues
```bash
# Check all services
/opt/projectmeats/scripts/status.sh

# Restart services
sudo systemctl restart projectmeats nginx

# Check logs
sudo journalctl -u projectmeats -f
```

### 📊 Logs and Diagnostics

**Important log locations:**
- Application logs: `/opt/projectmeats/logs/`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u projectmeats`
- Deployment logs: `/opt/projectmeats/logs/deployment.log`

**Diagnostic commands:**
```bash
# Health check
/opt/projectmeats/scripts/health_check.py

# System status
/opt/projectmeats/scripts/status.sh

# Service logs
sudo journalctl -u projectmeats -n 50

# Database connectivity
sudo -u projectmeats psql -h localhost -U projectmeats -d projectmeats -c 'SELECT version();'
```

---

## 🔄 Backup and Recovery

### Automated Backups
- Daily database backups to `/opt/projectmeats/backups/`
- 7-day retention policy
- Automated cleanup of old backups

### Manual Backup
```bash
# Create backup
/opt/projectmeats/scripts/backup.sh

# Restore from backup
sudo -u postgres psql projectmeats < /opt/projectmeats/backups/backup_YYYYMMDD_HHMMSS.sql
```

---

## 🚀 Advanced Features

### 🐳 Docker Deployment with Monitoring

```bash
sudo python3 master_deploy.py --docker --monitoring --domain=yourdomain.com
```

**Includes:**
- Prometheus metrics collection
- Grafana dashboards
- Container health monitoring
- Resource usage tracking

### 🔄 CI/CD Integration

```bash
sudo python3 master_deploy.py --ci-cd --domain=yourdomain.com
```

**Features:**
- GitHub webhook handler
- Automatic deployment on push
- Health checks after deployment
- Rollback capabilities

---

## 📞 Support and Documentation

### 🆘 Getting Help

1. **Check this guide first** - Most issues are covered here
2. **Run health checks** - Use built-in diagnostic tools
3. **Check logs** - Review application and system logs
4. **GitHub Issues** - Report bugs or request features

### 📚 Additional Resources

- **API Documentation**: `https://yourdomain.com/api/docs/`
- **Admin Interface**: `https://yourdomain.com/admin/`
- **GitHub Repository**: https://github.com/Vacilator/ProjectMeats
- **Development Guide**: See `docs/dev_environment_setup.md`

---

## 📝 Migration from Old Scripts

If you were using any of these old scripts, they have been replaced by the unified system:

| Old Script | New Command |
|------------|-------------|
| `one_click_deploy.sh` | `python3 master_deploy.py --auto` |
| `deploy_production.py` | `python3 master_deploy.py --wizard` |
| `quick_deploy.sh` | `python3 master_deploy.py --auto` |
| `deploy_server.sh` | `python3 master_deploy.py --prepare-server` |
| All verification scripts | Built into `master_deploy.py` |

**Old scripts are deprecated and will be removed in future versions.**

---

## ✅ Deployment Checklist

Before deployment:
- [ ] Domain name configured and pointing to server
- [ ] Server has Ubuntu 20.04+ with sudo access
- [ ] GitHub authentication configured (if private repo)
- [ ] Email configured for alerts (optional)

After deployment:
- [ ] Visit `https://yourdomain.com` - frontend loads
- [ ] Visit `https://yourdomain.com/admin/` - admin interface works
- [ ] Visit `https://yourdomain.com/api/docs/` - API documentation loads
- [ ] Run `/opt/projectmeats/scripts/health_check.py` - all services healthy
- [ ] Check SSL certificate - shows valid and secure
- [ ] Test admin login with provided credentials

---

**🎉 Congratulations! Your ProjectMeats application is now running in production with enterprise-grade security, monitoring, and reliability.**