# ProjectMeats Production Setup Guide
## Simplified Deployment Process

This guide provides a streamlined approach to deploying ProjectMeats to production with interactive setup and server provider recommendations.

## 🚀 Quick Start (5-Minute Setup)

### Option 1: Interactive Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Run interactive production setup
python deploy_production.py
```

The interactive script will:
- Guide you through server provider selection
- Collect all configuration values via prompts
- Generate all necessary configuration files
- Create deployment scripts
- Provide step-by-step deployment instructions

### Option 2: One-Command Server Deployment
```bash
# On your production server (Ubuntu 20.04+)
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_production.py | python3
```

## 📋 Server Provider Recommendations

### Best Value Options (Small-Medium Business)

| Provider | Cost/Month | Specs | Best For |
|----------|------------|-------|----------|
| **DigitalOcean** | $20-40 | 2-4 vCPU, 4-8GB RAM | Easy setup, great docs |
| **Linode** | $18-36 | 2-4 vCPU, 4-8GB RAM | Performance focused |
| **Vultr** | $20-40 | 2-4 vCPU, 4-8GB RAM | Global reach |
| **AWS Lightsail** | $20-40 | 2-4 vCPU, 4-8GB RAM | AWS ecosystem |

### Quick Server Setup Steps:
1. **Create server** with Ubuntu 20.04+ LTS
2. **Point domain** DNS to server IP
3. **SSH into server** as root or sudo user
4. **Run deployment script**

## 🔧 Interactive Configuration

The `deploy_production.py` script will prompt you for:

### Basic Configuration
- **Deployment Type**: Production server, local server, or development
- **Domain Name**: Your website domain (e.g., mycompany.com)
- **SSL/HTTPS**: Automatic Let's Encrypt setup
- **Database**: PostgreSQL (recommended) or SQLite

### Security Settings
- **Admin Credentials**: Username, email, and password
- **Secret Keys**: Automatically generated secure keys
- **Security Headers**: HTTPS redirects, HSTS, XSS protection

### Email Configuration
- **SMTP Settings**: Email provider configuration
- **Email Templates**: Automated notification setup

### Advanced Options
- **Time Zone**: Company location settings
- **Caching**: Redis configuration for performance
- **File Storage**: Upload directory configuration
- **Backup Settings**: Automated backup schedule

## 🛠️ Generated Files

After running the interactive setup, you'll have:

```
ProjectMeats/
├── backend/.env                    # Production environment variables
├── frontend/.env.production        # Frontend production config
├── deploy_server.sh               # Complete server deployment script
├── production_config.json         # Configuration backup
└── scripts/
    ├── update.sh                  # Application update script
    └── status.sh                  # System status checker
```

## 🚀 Deployment Process

### For Production Servers:

1. **Upload to Server**:
```bash
# From your local machine
scp -r . user@your-domain.com:/home/projectmeats/setup
```

2. **SSH and Deploy**:
```bash
# On the server
ssh user@your-domain.com
cd /home/projectmeats/setup
sudo ./deploy_server.sh
```

3. **Access Application**:
- Website: `https://your-domain.com`
- Admin Panel: `https://your-domain.com/admin/`
- API Documentation: `https://your-domain.com/api/docs/`

### For Local Development:

1. **Run Setup**:
```bash
python deploy_production.py
# Select "Local Server" or "Development Testing"
```

2. **Start Services**:
```bash
cd backend && python manage.py runserver &
cd frontend && npm start
```

3. **Access Application**:
- Website: `http://localhost:3000`
- Admin Panel: `http://localhost:8000/admin/`

## 🔒 Security Features

The automated setup includes:

- **SSL/HTTPS**: Let's Encrypt certificates with auto-renewal
- **Firewall**: UFW configured with essential ports only
- **Fail2Ban**: Intrusion prevention for SSH and web attacks
- **Security Headers**: HSTS, XSS protection, content type sniffing
- **Database Security**: Secure passwords and user permissions
- **File Uploads**: Secure file handling and validation

## 📊 Monitoring & Maintenance

### Automated Features:
- **Daily Backups**: Database and application files
- **Log Rotation**: Automatic cleanup of old logs
- **Health Monitoring**: Service status checks
- **Update Scripts**: Easy application updates

### Manual Commands:
```bash
# Check system status
./scripts/status.sh

# Update application
./scripts/update.sh

# View logs
tail -f /home/projectmeats/logs/gunicorn_error.log

# Restart services
sudo systemctl restart projectmeats nginx
```

## 🆘 Troubleshooting

### Common Issues:

1. **DNS Not Pointing**: Ensure domain DNS points to server IP
2. **SSL Certificate Fails**: Check domain DNS propagation (24-48 hours)
3. **Database Connection**: Verify PostgreSQL service status
4. **Permission Errors**: Check file ownership (`chown -R projectmeats:projectmeats /home/projectmeats/`)

### Quick Fixes:
```bash
# Restart all services
sudo systemctl restart projectmeats nginx postgresql

# Check service status
sudo systemctl status projectmeats

# View detailed logs
journalctl -u projectmeats -f

# Test database connection
sudo -u projectmeats psql -h localhost -U projectmeats_user -d projectmeats_prod
```

## 📞 Support

- **Documentation**: Check `docs/` folder for detailed guides
- **Logs**: System logs in `/home/projectmeats/logs/`
- **Configuration**: Backup saved in `production_config.json`
- **Updates**: Use `./scripts/update.sh` for application updates

## 🎯 Success Metrics

After successful deployment:
- ✅ Website loads at your domain
- ✅ Admin panel accessible with your credentials
- ✅ API documentation available
- ✅ SSL certificate valid and auto-renewing
- ✅ Automated backups running
- ✅ All services start on boot
- ✅ Performance: < 2 second page load times
- ✅ Security: All security headers active

---

**Total Setup Time**: 30-60 minutes (including DNS propagation)  
**Ongoing Maintenance**: < 1 hour/month with automated scripts

🎉 **Your ProjectMeats production environment is ready!**