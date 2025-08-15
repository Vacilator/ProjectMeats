# 🚀 ProjectMeats Unified Deployment Guide

**IMPORTANT**: This guide has been consolidated and enhanced. The AI Deployment Orchestrator (`ai_deployment_orchestrator.py`) is now the PRIMARY and ONLY deployment tool needed.

## 🎯 Quick Start (Recommended)

### 1. 🐳 Docker Deployment (Industry Best Practices)

**One-line deployment:**
```bash
python3 ai_deployment_orchestrator.py --server=yourdomain.com --domain=yourdomain.com --docker --auto
```

**Interactive deployment:**
```bash
python3 ai_deployment_orchestrator.py --interactive
```

### 2. 📝 Using the Launcher Script

```bash
# Simple launcher with Docker
./deploy.py --server myserver.com --domain mydomain.com --docker

# With monitoring stack
./deploy.py --server myserver.com --domain mydomain.com --docker --monitoring

# Interactive setup
./deploy.py --interactive
```

## 🏗️ What's Included (Industry Standards)

### ✅ Docker Infrastructure
- **Multi-stage builds** for optimal image sizes
- **Security hardening** with non-root users
- **Health checks** for all services
- **Resource limits** and restart policies
- **Network isolation** between frontend/backend

### ✅ Production Services
- **PostgreSQL 15** with connection pooling and security hardening
- **Redis 7** for caching and session management
- **nginx** reverse proxy with SSL termination
- **Celery** for background task processing
- **Prometheus + Grafana** monitoring (optional)

### ✅ Security & Performance
- **SSL/HTTPS** automatic configuration
- **Security headers** and hardening
- **Rate limiting** and DDoS protection
- **Automated backups** with retention policies
- **Log aggregation** and monitoring

### ✅ DigitalOcean Optimization
- **Droplet-specific** performance tuning
- **Resource optimization** for cost efficiency
- **Network configuration** for optimal performance
- **Auto-scaling preparation**

# With GitHub authentication
sudo python3 master_deploy.py --auto \
  --domain=yourdomain.com \
  --github-user=your-username \
  --github-token=your-token

## 🔧 Configuration Examples

### Production Environment
```bash
# Full production with monitoring
python3 ai_deployment_orchestrator.py \
  --server=production.mycompany.com \
  --domain=myapp.com \
  --docker \
  --docker-monitoring \
  --github-user=myuser \
  --github-token=mytoken
```

### Staging Environment
```bash
# Staging deployment
python3 ai_deployment_orchestrator.py \
  --server=staging.mycompany.com \
  --domain=staging.myapp.com \
  --docker
```

## 📋 Deployment Process

The AI orchestrator executes these optimized steps:

1. **Server Validation** - Checks server requirements and connectivity
2. **Authentication Setup** - Configures secure access
3. **Docker Installation** - Installs latest Docker with security best practices
4. **Database Setup** - PostgreSQL with production configuration
5. **Application Download** - Secure code deployment
6. **Docker Infrastructure** - Creates optimized containers and networks
7. **SSL Configuration** - Automatic HTTPS setup
8. **Health Verification** - Comprehensive service testing
9. **Domain Accessibility** - External connectivity validation

## 🐳 Docker Architecture

```yaml
Services:
  - db (PostgreSQL 15 with security hardening)
  - redis (Redis 7 with authentication)
  - backend (Django + gunicorn, non-root user)
  - frontend (React + nginx, optimized builds)
  - nginx (SSL termination, security headers)
  - celery (Background tasks)
  - prometheus (Metrics collection - optional)
  - grafana (Monitoring dashboard - optional) 
  - backup (Automated database backups)
```

## 🔒 Security Features

- **Container Security**: Non-root users, read-only filesystems, security options
- **Network Security**: Isolated networks, encrypted communication
- **Application Security**: HTTPS, security headers, rate limiting
- **Data Security**: Encrypted databases, secure secret management
- **Access Security**: SSH key authentication, fail2ban protection

## 📊 Monitoring & Maintenance

### Health Endpoints
- `http://yourdomain.com/health` - Application health
- `http://yourdomain.com:9090` - Prometheus metrics (if enabled)
- `http://yourdomain.com:3001` - Grafana dashboard (if enabled)

### Log Locations
```
/opt/projectmeats/logs/
├── nginx/          # nginx access/error logs
├── gunicorn/       # Django application logs
└── celery/         # Background task logs
```

### Backup Management
```bash
# Backups are automatically created daily
ls /opt/projectmeats/backups/

# Manual backup
docker-compose exec db pg_dump -U projectmeats projectmeats > backup.sql
```

## 🚨 Troubleshooting

### Check Services
```bash
# Check all container status
docker-compose ps

# View service logs  
docker-compose logs backend
docker-compose logs nginx

# Check health
curl http://yourdomain.com/health
```

### Common Issues
1. **Domain not accessible**: Check DNS configuration
2. **SSL issues**: Verify domain points to server IP
3. **Database connection**: Check PostgreSQL container logs
4. **Performance issues**: Monitor resource usage

## 🎛️ Advanced Configuration

### Custom Environment Variables
Create `.env.prod` from `.env.prod.template` and customize:

```bash
# Copy and edit template
cp .env.prod.template .env.prod
nano .env.prod
```

### Scaling Services
```bash
# Scale backend workers
docker-compose up -d --scale backend=3

# Scale celery workers  
docker-compose up -d --scale celery=2
```

## 📚 Legacy Information

Previous deployment scripts have been archived in `legacy-deployment/`:
- `master_deploy.py` - Previous unified deployer
- `production_deploy.sh` - Shell-based deployment
- `deploy_production.py` - Python deployment script

**These are no longer needed** - use the AI orchestrator for all deployments.

---

## 🆘 Support

For deployment issues:
1. Check logs: `docker-compose logs [service]`
2. Review health endpoints
3. Consult troubleshooting section
4. Create GitHub issue with deployment logs

**The AI orchestrator provides comprehensive error handling and recovery - most issues are automatically resolved.**

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