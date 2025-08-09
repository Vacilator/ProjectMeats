# ProjectMeats Production Deployment Configurations

This directory contains production-ready deployment configurations for ProjectMeats.

## 🚀 Quick Deployment

For the fastest deployment on your server:

```bash
# 1. Clone or upload the project to your server
cd /opt
sudo git clone https://github.com/Vacilator/ProjectMeats.git projectmeats
cd projectmeats

# 2. Run the setup script
sudo ./deployment/scripts/setup_production.sh
```

This will automatically:
- Install all dependencies (Python, Node.js, PostgreSQL, Nginx)
- Set up the database and virtual environment  
- Configure and start all services
- Build the frontend
- Create admin user

## 📁 Configuration Files

### Nginx Configuration (`nginx/projectmeats.conf`)
- Serves React frontend from `/opt/projectmeats/frontend/build`
- Proxies `/api/` and `/admin/` requests to Django backend
- Handles static files and media
- Includes security headers and gzip compression
- Ready for SSL/HTTPS setup

### SystemD Service (`systemd/projectmeats.service`)
- Runs Django backend with gunicorn
- Automatic restart on failure
- Security hardening settings
- Proper logging configuration

### PM2 Configuration (`pm2/ecosystem.config.js`)
- Alternative to systemd for process management
- Automatic restart and monitoring
- Clustering support
- Memory limits

### Environment Template (`env.production.template`)
- Production environment variables
- Database configuration
- Security settings
- Email configuration
- CORS settings

## 🛠️ Manual Setup

### 1. System Requirements
```bash
# Ubuntu 20.04+ with:
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv postgresql nginx nodejs npm
```

### 2. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres createdb projectmeats_db
sudo -u postgres createuser -s projectmeats_user
sudo -u postgres psql -c "ALTER USER projectmeats_user WITH ENCRYPTED PASSWORD 'your_password';"
```

### 3. Application Setup
```bash
# Set up project directory
sudo mkdir -p /opt/projectmeats
cd /opt/projectmeats

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Environment configuration
cp deployment/env.production.template .env.production
# Edit .env.production with your settings

# Django setup
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Frontend build
cd ../frontend
npm install --production
npm run build
```

### 4. Web Server Configuration
```bash
# Nginx
sudo cp deployment/nginx/projectmeats.conf /etc/nginx/sites-available/projectmeats
sudo ln -s /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# SystemD service
sudo cp deployment/systemd/projectmeats.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable projectmeats
sudo systemctl start projectmeats
```

## 🔧 Alternative: PM2 Setup

If you prefer PM2 over systemd:

```bash
# Install PM2 globally
sudo npm install -g pm2

# Start application
cd /opt/projectmeats
pm2 start deployment/pm2/ecosystem.config.js

# Save PM2 configuration
pm2 save
pm2 startup

# Monitor
pm2 status
pm2 logs projectmeats-django
```

## 🔒 SSL Setup

After basic deployment, set up SSL with Let's Encrypt:

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already set up by certbot)
sudo crontab -l | grep certbot
```

## 📊 Monitoring

### Service Status
```bash
# SystemD
sudo systemctl status projectmeats
sudo systemctl status nginx

# PM2
pm2 status
pm2 info projectmeats-django
```

### Logs
```bash
# SystemD
sudo journalctl -u projectmeats -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/projectmeats/error.log

# PM2
pm2 logs projectmeats-django
```

### Health Check
```bash
# Test application
curl http://localhost/health
curl http://localhost/api/docs/

# Check processes
ps aux | grep gunicorn
ss -tlnp | grep 8000
```

## 🔄 Updates

To update the application:

```bash
cd /opt/projectmeats

# Pull latest code
git pull origin main

# Update backend
source venv/bin/activate
pip install -r backend/requirements.txt
cd backend
python manage.py migrate
python manage.py collectstatic --noinput

# Update frontend
cd ../frontend
npm install --production
npm run build

# Restart services
sudo systemctl restart projectmeats
# or: pm2 restart projectmeats-django
```

## 🔧 Troubleshooting

### Common Issues

1. **403 Forbidden**: Check file permissions
   ```bash
   sudo chown -R www-data:www-data /opt/projectmeats
   ```

2. **502 Bad Gateway**: Backend not running
   ```bash
   sudo systemctl status projectmeats
   sudo journalctl -u projectmeats -n 20
   ```

3. **Static files not loading**: Run collectstatic
   ```bash
   cd /opt/projectmeats/backend
   python manage.py collectstatic --noinput
   ```

4. **Database connection**: Check environment variables
   ```bash
   cat /opt/projectmeats/.env.production | grep DATABASE
   ```

### Log Locations
- Nginx: `/var/log/nginx/`
- Django: `/var/log/projectmeats/`
- SystemD: `journalctl -u projectmeats`
- PM2: `pm2 logs`

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Verify all services are running
3. Test database connectivity
4. Check file permissions
5. Review environment variables

For more help, see the main project documentation or create an issue on GitHub.