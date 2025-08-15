# 🚨 URGENT: ProjectMeats Server Fix Instructions

Your server at `meatscentral.com` is currently showing a default Nginx page because the ProjectMeats application isn't running properly.

## 🔧 Quick Fix (5 minutes)

If you already have the ProjectMeats code on your server:

```bash
# SSH into your server
ssh root@167.99.155.140

# Navigate to project directory
cd /opt/projectmeats

# Run the quick fix script
sudo ./deployment/scripts/quick_server_fix.sh
```

This will:
- ✅ Set up the Django backend with gunicorn
- ✅ Build and configure the React frontend  
- ✅ Configure Nginx to serve the app properly
- ✅ Start all services automatically

## 📋 What Was Missing

Your server had:
- ✅ Nginx installed and running
- ✅ Domain pointing correctly
- ✅ PostgreSQL database running
- ✅ Firewall configured properly

But was missing:
- ❌ Application processes running (Django backend)
- ❌ Frontend built and configured  
- ❌ Nginx configured to serve the app (was serving default page)

## 🎯 Expected Result

After running the fix:
- **Main App**: http://meatscentral.com → React frontend
- **Admin**: http://meatscentral.com/admin → Django admin interface
- **API**: http://meatscentral.com/api → REST API endpoints

## 🔑 Admin Access

Default credentials:
- **Username**: admin
- **Password**: WATERMELON1219

⚠️ **Important**: Change this password after first login!

## 📊 Monitoring

Check if everything is running:
```bash
# Service status
sudo systemctl status projectmeats
sudo systemctl status nginx

# View logs
sudo journalctl -u projectmeats -f
sudo tail -f /var/log/nginx/access.log

# Test endpoints
curl http://localhost/health
curl http://localhost/api/docs/
```

## 🔄 If You Need a Fresh Install

If you don't have the project code on your server yet:

```bash
# Clone the project
cd /opt
sudo git clone https://github.com/Vacilator/ProjectMeats.git projectmeats
cd projectmeats

# Run full setup
sudo ./deployment/scripts/setup_production.sh
```

## 🆘 Troubleshooting

**Problem: 502 Bad Gateway**
```bash
sudo systemctl restart projectmeats
sudo journalctl -u projectmeats -n 20
```

**Problem: Static files not loading**
```bash
cd /opt/projectmeats/backend
source ../venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart projectmeats
```

**Problem: Frontend not building**
```bash
cd /opt/projectmeats/frontend
npm install
npm run build
sudo systemctl restart nginx
```

## 📞 Support

The deployment configurations are now in your project at:
- `deployment/nginx/` - Web server config
- `deployment/systemd/` - Service config  
- `deployment/scripts/` - Setup scripts
- `deployment/README.md` - Full documentation

After the quick fix, your ProjectMeats application should be live at meatscentral.com! 🎉