# Quick Setup Guide - Socket Configuration Fix

## Problem Summary
MeatsCentral.com was inaccessible due to:
1. Nginx using default configuration instead of ProjectMeats config
2. Socket permission issues preventing nginx (www-data) from accessing Django backend
3. Inconsistent proxy configuration (TCP vs socket)

## Quick Fix Commands

### 1. Deploy with Fixed Configuration
```bash
# On the server, pull latest changes
cd ~/ProjectMeats
git pull origin main

# Run the updated deployment script
sudo ./production_deploy.sh
```

### 2. Manual Fix (if deployment script fails)
```bash
# Fix nginx configuration
sudo cp /opt/projectmeats/deployment/templates/meatscentral.conf /etc/nginx/sites-available/meatscentral
sudo ln -sf /etc/nginx/sites-available/meatscentral /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Fix socket permissions
sudo systemctl enable projectmeats.socket
sudo systemctl start projectmeats.socket
sudo chown projectmeats:www-data /run/projectmeats.sock
sudo chmod 660 /run/projectmeats.sock

# Start Django service
sudo systemctl enable projectmeats
sudo systemctl start projectmeats

# Restart nginx
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Verify the Fix
```bash
# Run verification script
cd ~/ProjectMeats
./verify_socket_fix.sh

# Test externally
curl http://meatscentral.com/health
```

## Expected Results After Fix
- ✅ `curl http://meatscentral.com/health` returns "healthy"
- ✅ No nginx upstream connection errors
- ✅ Socket permissions: `srw-rw---- projectmeats www-data /run/projectmeats.sock`
- ✅ All services active: `systemctl is-active projectmeats.socket projectmeats nginx`

## Troubleshooting

### If Health Endpoint Still Fails
1. Check socket accessibility: `curl --unix-socket /run/projectmeats.sock http://localhost/health`
2. Check Django service logs: `journalctl -u projectmeats -f`  
3. Check nginx error logs: `tail -f /var/log/nginx/error.log`

### If Socket Permissions Are Wrong
```bash
sudo systemctl stop projectmeats
sudo rm -f /run/projectmeats.sock
sudo systemctl restart projectmeats.socket
ls -la /run/projectmeats.sock  # Should show projectmeats:www-data
sudo systemctl start projectmeats
```

### If TCP Fallback Is Needed
The deployment script automatically falls back to TCP (port 8000) if socket configuration fails.

## Files Changed in This Fix
- `production_deploy.sh` - Socket-first deployment with TCP fallback
- `deployment/templates/meatscentral.conf` - Domain-specific nginx config
- `deployment/scripts/diagnose_service.sh` - Socket accessibility testing
- `deployment/nginx/projectmeats-socket.conf` - Health endpoint improvements
- `deploy_production.py` - Enhanced DNS verification

## Support
- Run diagnostics: `./deployment/scripts/diagnose_service.sh`
- Check verification: `./verify_socket_fix.sh`
- View logs: `tail -f /var/log/projectmeats/error.log`