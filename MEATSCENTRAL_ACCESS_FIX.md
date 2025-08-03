# MeatsCentral.com Access Fix Guide

## Problem
You can't access meatscentral.com from your browser, getting "Unable to connect to the remote server" error.

## Quick Diagnosis

**Step 1: Check DNS (run from your computer)**
```bash
nslookup meatscentral.com
```
Expected result: Should show IP address 167.99.155.140

**Step 2: Test direct IP access**
```bash
curl http://167.99.155.140/health
```
If this works but the domain doesn't, it's a DNS or nginx configuration issue.

## Most Likely Issues & Fixes

### Issue 1: DNS Not Configured (Most Common)
Your domain registrar needs an A record pointing to your server.

**Fix:**
1. Log into your domain registrar (GoDaddy, Namecheap, etc.)
2. Find DNS settings for meatscentral.com
3. Add/Update A record:
   - **Name:** @ (or meatscentral.com)
   - **Type:** A
   - **Value:** 167.99.155.140
   - **TTL:** 300

**Note:** DNS changes can take up to 48 hours to propagate globally.

### Issue 2: Nginx Not Configured for Domain
Nginx might not be set up to serve your domain.

**Fix (run on server):**
```bash
# SSH into your server
ssh -i ~/.ssh/id_ed25519 root@167.99.155.140

# Download and run the fix tool
wget https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/fix_meatscentral_access.py
python3 fix_meatscentral_access.py --auto-fix
```

### Issue 3: Firewall Blocking Access
Server firewall might be blocking HTTP traffic.

**Fix (run on server):**
```bash
# Check firewall status
ufw status

# Open HTTP and HTTPS ports
ufw allow 80/tcp
ufw allow 443/tcp

# Restart nginx
systemctl restart nginx
```

### Issue 4: Services Not Running
Backend services might be stopped.

**Fix (run on server):**
```bash
# Check service status
systemctl status nginx
systemctl status projectmeats

# Start services if stopped
systemctl start nginx
systemctl start projectmeats
systemctl enable nginx
systemctl enable projectmeats
```

## Comprehensive Fix Tool

I've created a specialized tool for your exact issue. Here's how to use it:

### From Your Computer (Local Diagnostics)
```bash
# Download the tool
curl -O https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/fix_meatscentral_access.py

# Run local diagnostics
python3 fix_meatscentral_access.py --local-check
```

### On Your Server (Auto-Fix)
```bash
# SSH into server
ssh -i ~/.ssh/id_ed25519 root@167.99.155.140

# Download and run auto-fix
wget https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/fix_meatscentral_access.py
python3 fix_meatscentral_access.py --auto-fix
```

## Manual Nginx Configuration

If auto-fix doesn't work, manually configure nginx:

```bash
# Create nginx config for your domain
cat > /etc/nginx/sites-available/meatscentral.com << 'EOF'
server {
    listen 80;
    server_name meatscentral.com www.meatscentral.com;
    
    # Frontend static files
    location / {
        root /opt/projectmeats/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/meatscentral.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart nginx
nginx -t
systemctl restart nginx
```

## Verification Steps

After making changes, verify everything works:

```bash
# On server - test local access
curl http://localhost/health

# From your computer - test domain access  
curl http://meatscentral.com/health

# Check DNS propagation
nslookup meatscentral.com
```

## Common Commands for Troubleshooting

```bash
# Check what's listening on port 80
netstat -tlnp | grep :80

# View nginx logs
tail -f /var/log/nginx/error.log

# Check nginx configuration
nginx -T | grep -A 5 meatscentral.com

# Test nginx config syntax
nginx -t

# Check service status
systemctl status nginx projectmeats postgresql
```

## If Nothing Works

1. **Check DNS propagation**: Use https://dnschecker.org/ to see if DNS has propagated
2. **Test direct IP**: Try http://167.99.155.140/health directly
3. **Contact domain registrar**: Ensure DNS settings are correct
4. **Wait for propagation**: DNS changes can take 24-48 hours

## Getting Help

If you're still having issues:

1. Run the diagnostic tool: `python3 fix_meatscentral_access.py --local-check`
2. SSH into server and run: `python3 fix_meatscentral_access.py --server-check`
3. Share the output for further assistance

## Next Steps

Once meatscentral.com is accessible:
1. Set up SSL certificate with Let's Encrypt
2. Configure HTTPS redirect
3. Set up monitoring and backups