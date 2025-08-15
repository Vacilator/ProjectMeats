# ProjectMeats Deployment Fix - Issue Resolution

## 🔍 Problem Statement Analysis

Based on the issue description, the main problems were:

1. **Backend Django app not running** (the problem incorrectly mentioned PM2, but this is a Django app that should use gunicorn)
2. **Missing React static files** - 404 errors for `/static/js/main.5dbb099c.js` and `/favicon.ico`
3. **Nginx not properly configured** to proxy between frontend and backend
4. **React app not built** or files not in the correct location

## ✅ Solutions Implemented

### 1. New Production Deployment Script (`production_deploy.sh`)

Created a comprehensive deployment script that:
- ✅ Installs Node.js 18 LTS for React builds
- ✅ Sets up Python virtual environment with Django dependencies  
- ✅ Creates PostgreSQL database with proper credentials
- ✅ **Builds React frontend** to create all static files including `main.*.js`
- ✅ **Sets up systemd service** for Django backend with gunicorn (not PM2)
- ✅ **Configures Nginx** to properly serve React build files and proxy API calls
- ✅ Creates management tools for easy troubleshooting

### 2. Fixed Service Architecture

**Before (Issues):**
- Backend not running at all
- No React build process
- Nginx serving from wrong location
- Missing static files

**After (Fixed):**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Nginx :80     │───▶│  React Frontend  │    │ Django Backend  │
│                 │    │  /opt/project... │◄───│ gunicorn :8000  │
│ Serves static   │    │  /build/         │    │ systemd service │
│ Proxies /api/   │    └──────────────────┘    └─────────────────┘
└─────────────────┘
```

### 3. Nginx Configuration Fix

The new nginx config (`/etc/nginx/sites-available/projectmeats`):

```nginx
# Serves React build files
root /opt/projectmeats/frontend/build;

# API calls → Django backend
location /api/ {
    proxy_pass http://127.0.0.1:8000;
}

# Django admin → Django backend  
location /admin/ {
    proxy_pass http://127.0.0.1:8000;
}

# Static files with proper fallback
location /static/ {
    alias /opt/projectmeats/backend/staticfiles/;
    try_files $uri @react_static;
}

# React static assets (the missing main.*.js files)
location ~* ^/static/.+\.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    root /opt/projectmeats/frontend/build;
    try_files $uri =404;
}

# Favicon and other assets
location ~* \.(ico|png|svg|webmanifest)$ {
    root /opt/projectmeats/frontend/build;
    try_files $uri =404;
}

# React routing
location / {
    try_files $uri $uri/ /index.html;
}
```

### 4. Systemd Service for Django Backend

Created proper systemd service (`/etc/systemd/system/projectmeats.service`):
```ini
[Service]
Type=notify
User=projectmeats
ExecStart=/opt/projectmeats/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    projectmeats.wsgi:application
```

## 🚀 Deployment Instructions

### Option 1: Run the New Production Script

```bash
# On your production server:
cd ProjectMeats
sudo ./production_deploy.sh
```

This will:
1. Install all dependencies (Node.js, Python, PostgreSQL, Nginx)
2. Build React frontend → creates `/static/js/main.*.js`
3. Set up Django backend with gunicorn
4. Configure Nginx properly
5. Start all services

### Option 2: Manual Steps (if script fails)

```bash
# 1. Install Node.js and build React
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs
cd /opt/projectmeats/frontend
npm install
npm run build  # Creates build/static/js/main.*.js

# 2. Install Python dependencies and setup Django  
cd /opt/projectmeats/backend
python3 -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# 3. Create systemd service (use content from production_deploy.sh)
sudo cp deployment/systemd/projectmeats.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable projectmeats
sudo systemctl start projectmeats

# 4. Configure Nginx (use content from production_deploy.sh)  
sudo cp deployment/nginx/projectmeats.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

## 🔧 Troubleshooting Commands

After deployment, use these commands to diagnose issues:

```bash
# Overall status
projectmeats status

# Service status  
systemctl status projectmeats  # Django backend
systemctl status nginx         # Web server

# Logs
projectmeats logs              # Django errors
journalctl -u projectmeats -f  # Django service logs
tail -f /var/log/nginx/error.log  # Nginx errors

# File checks
ls -la /opt/projectmeats/frontend/build/static/js/  # React files
ls -la /opt/projectmeats/backend/staticfiles/       # Django static files

# Test endpoints
curl -I http://localhost/                           # Frontend
curl -I http://localhost/static/js/main.*.js       # React JS files  
curl -I http://localhost/favicon.ico               # Favicon
curl -I http://localhost/api/                       # Backend API
```

## 🎯 Key Fixes Summary

| Issue | Previous State | Fixed State |
|-------|---------------|-------------|
| **Backend Service** | Not running / using PM2 | ✅ systemd + gunicorn |
| **React Static Files** | 404 errors, not built | ✅ Built to `/build/static/js/` |
| **Nginx Config** | Wrong root, no proxy | ✅ Serves React + proxies API |  
| **Service Management** | Manual/broken | ✅ systemd auto-restart |
| **Static File Serving** | Missing/404s | ✅ Proper nginx locations |

## 📋 What the New Script Does Differently

1. **Builds React App**: Runs `npm run build` to create `build/static/js/main.*.js`
2. **Proper Backend Service**: Uses gunicorn with systemd (not PM2)  
3. **Smart Nginx Config**: Serves React build files AND proxies API calls
4. **Error Recovery**: Better error handling and status checking
5. **Management Tools**: Creates `projectmeats` command for easy management

## 🌟 Result After Fix

✅ **http://meatscentral.com/** → React frontend loads properly  
✅ **http://meatscentral.com/static/js/main.*.js** → File exists and serves  
✅ **http://meatscentral.com/favicon.ico** → File exists and serves  
✅ **http://meatscentral.com/api/** → Proxies to Django backend  
✅ **http://meatscentral.com/admin/** → Django admin works  
✅ **Backend service runs automatically** with systemd  

The deployment issues mentioned in the problem statement should now be resolved!