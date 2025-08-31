# Production Deployment Guide - ProjectMeats

> **🚨 PRIMARY DEPLOYMENT TOOL**: This guide covers the main production deployment method using `ai_deployment_orchestrator.py`. This is the **ONLY** tool you should use for production deployments.

## Quick Start

### 🚀 One-Command Production Deployment

```bash
# Automated production deployment
python ai_deployment_orchestrator.py --server=your-server.com --domain=your-domain.com --auto

# Interactive setup (recommended for first-time users)
python ai_deployment_orchestrator.py --interactive

# With GitHub integration for automated issue management
python ai_deployment_orchestrator.py --server=your-server.com --domain=your-domain.com --github-user=USERNAME --github-token=TOKEN --auto
```

### ✅ Prerequisites Checklist

- [ ] Ubuntu 20.04+ or Debian 10+ server with root access
- [ ] Domain name pointing to your server
- [ ] SSH access configured
- [ ] GitHub Personal Access Token (optional, for automated issue management)

## 🎯 When to Use What

| Scenario | Tool | Command |
|----------|------|---------|
| **Production Deployment** | AI Orchestrator | `python ai_deployment_orchestrator.py --auto` |
| **Development Setup** | Local Setup | `python setup.py` |
| **Testing Changes** | Docker Compose | `docker-compose up` |
| **CI/CD Pipeline** | AI Orchestrator | `python ai_deployment_orchestrator.py --ci-cd` |

> **⚠️ Important**: Do NOT use scripts in `legacy-deployment/` or most scripts in `scripts/deployment/`. These are deprecated and may cause conflicts.

## 🤖 AI Orchestrator Features

### Intelligent Error Detection & Recovery
- **Automatic Issue Detection**: Recognizes 50+ common deployment problems
- **Smart Recovery**: Automatically fixes issues like package conflicts, permission problems, and service failures
- **Learning System**: Improves recovery strategies based on previous deployments

### Real-time Monitoring & Management
- **Live Progress Tracking**: See exactly what's happening during deployment
- **Interactive Problem Solving**: Automatically handles prompts and confirmations
- **State Persistence**: Resume deployments from where they left off
- **Comprehensive Logging**: Detailed logs for troubleshooting and auditing

### GitHub Integration
- **Automated Issue Creation**: Creates GitHub issues for deployment failures with @copilot assignment
- **Detailed Error Reports**: Includes complete error context and suggested fixes
- **Pull Request Generation**: For critical issues, creates dedicated fix branches

## 📋 Deployment Scenarios

### 1. Fresh Server Setup

```bash
# Complete setup on new server
python ai_deployment_orchestrator.py \
  --server=your-server.com \
  --domain=your-domain.com \
  --github-user=your-username \
  --github-token=your-token \
  --auto
```

**What it does**:
- Installs all required system packages
- Sets up PostgreSQL database
- Configures web server (Nginx)
- Builds and deploys React frontend
- Sets up Django backend
- Configures SSL certificates
- Starts all services

### 2. Update Existing Deployment

```bash
# Update existing deployment with latest code
python ai_deployment_orchestrator.py \
  --server=your-server.com \
  --update-only \
  --auto
```

### 3. Database Migration

```bash
# Run database migrations only
python ai_deployment_orchestrator.py \
  --server=your-server.com \
  --migrate-only \
  --auto
```

### 4. SSL Certificate Renewal

```bash
# Renew SSL certificates
python ai_deployment_orchestrator.py \
  --server=your-server.com \
  --ssl-only \
  --auto
```

### 5. Health Check & Verification

```bash
# Test deployment health
python ai_deployment_orchestrator.py \
  --server=your-server.com \
  --verify-only
```

## ⚙️ Configuration

### Environment Configuration

Create `ai_deployment_config.json` for your environment:

```json
{
  "deployment": {
    "environment": "production",
    "domain": "your-domain.com",
    "ssl_enabled": true,
    "backup_enabled": true
  },
  "database": {
    "type": "postgresql",
    "name": "projectmeats",
    "user": "projectmeats",
    "backup_retention_days": 7
  },
  "server": {
    "hostname": "your-server.com",
    "username": "root",
    "project_dir": "/opt/projectmeats"
  },
  "github": {
    "enabled": true,
    "username": "your-github-username",
    "repository": "Vacilator/ProjectMeats"
  }
}
```

### Server Profiles

For multiple environments, create server-specific configs:

```bash
# Production
cp ai_deployment_config.json ai_deployment_config.production.json

# Staging  
cp ai_deployment_config.json ai_deployment_config.staging.json
```

Use with: `python ai_deployment_orchestrator.py --config=production`

## 🔧 Advanced Features

### Resumable Deployments

If a deployment fails or is interrupted:

```bash
# Resume from last checkpoint
python ai_deployment_orchestrator.py --resume --deployment-id=abc123
```

### Custom Recovery Strategies

Add custom error patterns:

```python
# In deployment config
"error_patterns": {
    "custom_pattern": {
        "pattern": "your-regex-pattern",
        "recovery": "your_recovery_function",
        "severity": "high"
    }
}
```

### Backup Management

```bash
# Create backup before deployment
python ai_deployment_orchestrator.py --backup-first --server=your-server.com

# Restore from backup
python ai_deployment_orchestrator.py --restore-backup=backup-2024-01-01 --server=your-server.com
```

## 🐛 Troubleshooting

### Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Connection Refused** | SSH connection fails | Check server IP, SSH key, firewall |
| **Database Connection Failed** | Django can't connect to DB | Verify PostgreSQL is running, check credentials |
| **Frontend Not Loading** | React app shows errors | Check build process, verify Nginx config |
| **SSL Certificate Failed** | HTTPS not working | Verify domain DNS, check Let's Encrypt rate limits |
| **Port Already in Use** | Service won't start | Check for conflicting services, restart server |

### Debug Mode

Enable detailed logging:

```bash
python ai_deployment_orchestrator.py --debug --verbose --server=your-server.com
```

### Manual Recovery

If automatic recovery fails:

```bash
# Get deployment state
python ai_deployment_orchestrator.py --status --deployment-id=abc123

# Skip failed step and continue
python ai_deployment_orchestrator.py --skip-step=database_setup --resume --deployment-id=abc123
```

## 📊 Monitoring & Maintenance

### Health Checks

The orchestrator automatically sets up health monitoring:

- **Service Status**: Monitors Django, Nginx, PostgreSQL
- **Resource Usage**: CPU, memory, disk space monitoring
- **Error Tracking**: Automatic error detection and alerting
- **Performance Metrics**: Response times and throughput tracking

### Automated Maintenance

Configure automatic maintenance tasks:

```json
{
  "maintenance": {
    "enabled": true,
    "backup_schedule": "daily",
    "ssl_renewal": "auto",
    "log_rotation": "weekly",
    "security_updates": "auto"
  }
}
```

### Update Procedures

```bash
# Update application code
python ai_deployment_orchestrator.py --update-code --server=your-server.com

# Update system packages
python ai_deployment_orchestrator.py --update-system --server=your-server.com

# Full system maintenance
python ai_deployment_orchestrator.py --maintenance --server=your-server.com
```

## 🔒 Security Best Practices

### Access Control
- Use SSH keys instead of passwords
- Configure firewall to allow only necessary ports
- Enable automatic security updates
- Regular security audits

### Data Protection
- Automated daily backups
- Encrypted database connections
- SSL/TLS for all web traffic
- Secure secret management

### Monitoring
- Log all deployment activities
- Monitor for unauthorized access attempts
- Alert on unusual system behavior
- Regular security patch updates

## 📚 Additional Resources

### Documentation Structure
```
docs/
├── PRODUCTION_DEPLOYMENT_GUIDE.md     # This file - primary guide
├── DEVELOPER_QUICK_START.md           # Fast onboarding
├── TROUBLESHOOTING_GUIDE.md           # Detailed troubleshooting
├── CONFIGURATION_REFERENCE.md         # All configuration options
└── ADVANCED_FEATURES.md               # Power user features
```

### Getting Help

1. **Check Logs**: `tail -f /opt/projectmeats/logs/deployment.log`
2. **Run Diagnostics**: `python ai_deployment_orchestrator.py --diagnose`
3. **GitHub Issues**: Automatic issue creation with @copilot assignment
4. **Documentation**: Check troubleshooting guide for common issues

---

## 🎯 Summary

**The `ai_deployment_orchestrator.py` is your one-stop solution for ProjectMeats production deployments.** It handles everything from initial server setup to ongoing maintenance, with intelligent error recovery and comprehensive monitoring.

**Key Benefits:**
- **One Command Deployment**: Get from zero to production in minutes
- **Intelligent Recovery**: Automatic handling of deployment issues
- **Complete Monitoring**: Full visibility into deployment and system health
- **GitHub Integration**: Automated issue management and troubleshooting
- **Enterprise Ready**: Backup, security, and compliance features built-in

For any deployment needs, start here with the AI orchestrator. Other tools and scripts in the repository are either legacy (deprecated) or specialized utilities that complement the main orchestrator.