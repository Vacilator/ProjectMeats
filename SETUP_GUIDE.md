# ProjectMeats Server Setup Guide

## 🚀 Simple Two-Step Setup

### Step 1: Fix Common Server Issues
```bash
sudo ./fix_server.sh
```

**This fixes:**
- Missing directories
- Node.js conflicts  
- Permission issues
- File location problems

### Step 2: Deploy the Application
```bash
cd /home/projectmeats/setup
sudo ./deploy.sh
```

**This sets up:**
- Database (PostgreSQL)
- Web server (Nginx)
- SSL certificates
- Django backend
- React frontend

## ✅ After Setup

Your application will be available at:
- **Website**: https://meatscentral.com
- **Admin**: https://meatscentral.com/admin/
- **Login**: admin / WATERMELON1219

## 🆘 Troubleshooting

**If setup fails:**
1. Run the fix script again: `sudo ./fix_server.sh`
2. Check logs: `tail -f /home/projectmeats/logs/django.log`
3. Restart services: `systemctl restart nginx`

**Common issues:**
- **"Permission denied"** → Run with `sudo`
- **"Files not found"** → Run from ProjectMeats directory
- **"Port already in use"** → Stop other services first

## 📞 Need Help?

1. Check the main [README.md](README.md)
2. Review error logs in `/home/projectmeats/logs/`
3. Ensure you're running commands as root/sudo