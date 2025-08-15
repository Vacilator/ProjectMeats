# Nginx Socket Health Fix - Troubleshooting Guide

This guide helps troubleshoot deployment issues related to nginx socket configuration, health endpoints, and verification failures.

## Quick Health Check Commands

### 1. Test Health Endpoint Directly
```bash
# Test Django health endpoint via socket (if service is running)
curl --unix-socket /run/projectmeats.sock http://localhost/health

# Test health endpoint via HTTP (external access)
curl -I http://meatscentral.com/health
curl -I http://meatscentral.com/health/
```

### 2. Check Socket Status and Permissions
```bash
# Check if socket exists and permissions
ls -la /run/projectmeats.sock

# Should show: srw-rw---- 1 projectmeats www-data 0 DATE /run/projectmeats.sock

# Check socket accessibility for www-data
sudo -u www-data curl --unix-socket /run/projectmeats.sock http://localhost/health
```

### 3. Verify Port 80 Listening
```bash
# Modern way (preferred)
ss -tlnp | grep :80

# Fallback method
netstat -tlnp | grep :80
```

### 4. Check Service Status
```bash
# Check Django service
systemctl status projectmeats.service
systemctl status projectmeats.socket

# Check nginx
systemctl status nginx
nginx -t
```

## Common Issues and Solutions

### Issue: 404 on /health endpoint

**Symptoms:**
- `curl http://domain/health` returns 404
- Health endpoint works locally but not externally

**Diagnosis:**
```bash
# Check if Django URLs include health endpoints
grep -n "health" /opt/projectmeats/backend/projectmeats/urls.py

# Check nginx configuration
nginx -T | grep -A 10 -B 5 "location.*health"
```

**Solutions:**
1. Ensure both `/health` and `/health/` paths are in Django urls.py
2. Verify nginx configuration routes health requests to Django backend
3. Check nginx configuration syntax: `nginx -t`

### Issue: Upstream connect errors

**Symptoms:**
- nginx error: "connect() to unix:/run/projectmeats.sock failed"
- 502 Bad Gateway errors

**Diagnosis:**
```bash
# Check socket exists
test -S /run/projectmeats.sock && echo "Socket exists" || echo "Socket missing"

# Check socket permissions
stat -c "%U:%G %a" /run/projectmeats.sock

# Check nginx can access socket
sudo -u www-data test -r /run/projectmeats.sock && echo "Readable" || echo "Not readable"
sudo -u www-data test -w /run/projectmeats.sock && echo "Writable" || echo "Not writable"
```

**Solutions:**
1. Fix socket permissions:
   ```bash
   sudo chown projectmeats:www-data /run/projectmeats.sock
   sudo chmod 660 /run/projectmeats.sock
   ```
2. Restart services in correct order:
   ```bash
   sudo systemctl stop nginx
   sudo systemctl restart projectmeats.socket
   sudo systemctl restart projectmeats.service
   sudo systemctl start nginx
   ```

### Issue: DNS parsing issues

**Symptoms:**
- Domain resolution fails in deployment scripts
- External health checks fail

**Diagnosis:**
```bash
# Test DNS resolution (modern method)
dig +short A meatscentral.com

# Test external connectivity
curl -m 10 -I http://meatscentral.com/health

# Test with DNS bypass
curl --resolve "meatscentral.com:80:ACTUAL_IP" -I http://meatscentral.com/health
```

**Solutions:**
1. Verify DNS configuration at domain registrar
2. Check external DNS propagation: https://dnschecker.org/#A/meatscentral.com
3. Use IP-based testing during DNS propagation delays

### Issue: Port checks failing

**Symptoms:**
- Scripts report "Port 80 not listening"
- Cannot access website externally

**Diagnosis:**
```bash
# Check what's listening on port 80
sudo ss -tlnp | grep :80

# Check nginx configuration
sudo nginx -t

# Check nginx processes
ps aux | grep nginx

# Check firewall
sudo ufw status verbose
```

**Solutions:**
1. Restart nginx: `sudo systemctl restart nginx`
2. Check nginx configuration: `sudo nginx -t`
3. Ensure firewall allows port 80: `sudo ufw allow 'Nginx Full'`
4. Check for port conflicts with other services

## Diagnostic Script Usage

Run the comprehensive diagnostic script:
```bash
sudo /opt/projectmeats/deployment/scripts/diagnose_service.sh
```

This script automatically tests:
- Service status and configuration
- Socket accessibility and permissions  
- Network connectivity and port binding
- Django backend functionality
- Nginx configuration and routing

## Deployment Verification Commands

After deployment, run these commands to verify everything is working:

```bash
# 1. Health endpoint tests
curl http://localhost/health          # Should return 200 OK
curl http://meatscentral.com/health   # Should work externally

# 2. Socket tests
ls -l /run/projectmeats.sock         # Check socket exists with correct permissions
curl --unix-socket /run/projectmeats.sock http://localhost/health

# 3. Service status
systemctl is-active projectmeats.service projectmeats.socket nginx

# 4. Port binding
sudo ss -tlnp | grep :80             # Should show nginx listening

# 5. Configuration syntax
nginx -t                             # Should show "syntax is ok"
```

## When to Use This Guide

Use this troubleshooting guide when encountering:
- 404 errors on health endpoints
- 502 Bad Gateway errors  
- "upstream connect" errors in nginx logs
- Socket permission denied errors
- External connectivity failures
- DNS resolution problems
- Port binding issues

The fixes implemented address these common deployment failure patterns by ensuring proper nginx-socket integration and robust health monitoring.