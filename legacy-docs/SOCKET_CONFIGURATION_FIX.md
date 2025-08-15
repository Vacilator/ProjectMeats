# Socket Configuration Fix for MeatsCentral.com

This document explains the fixes implemented to resolve the deployment issues where nginx could not access the Django backend via Unix socket.

## Issues Fixed

### 1. Nginx Configuration Mismatch
**Problem**: Deployment was using default nginx config instead of ProjectMeats-specific configuration.
**Solution**: Updated `production_deploy.sh` to:
- Use `deployment/templates/meatscentral.conf` for domain-specific configuration
- Remove default nginx site (`/etc/nginx/sites-enabled/default`)
- Create proper symlinks for meatscentral.com

### 2. Socket Permission Issues  
**Problem**: Socket existed but had permissions `srw-rw----` - nginx (www-data) couldn't access it.
**Solution**: 
- Updated systemd socket configuration with `SocketGroup=www-data` and `SocketMode=0660`
- Added automatic permission fixing in deployment script: `chown projectmeats:www-data /run/projectmeats.sock && chmod 660`
- Added socket accessibility testing in diagnostics

### 3. Upstream Configuration Mismatch
**Problem**: Nginx was proxying to TCP (`127.0.0.1:8000`) but Django was running on socket (`unix:/run/projectmeats.sock`).  
**Solution**:
- Prioritized socket-based configuration in deployment
- Created fallback logic to TCP if socket fails
- Fixed nginx upstream to use `unix:/run/projectmeats.sock`

### 4. Health Endpoint Issues
**Problem**: Health endpoint failed causing 502 errors, wrong error page paths.
**Solution**:
- Added health endpoint fallback served directly by nginx
- Handle both `/health` and `/health/` (with/without trailing slash)
- Fixed error page root path to `/opt/projectmeats/frontend/build`

## Files Modified

### Primary Configuration Files
- `deployment/templates/meatscentral.conf` - New domain-specific nginx config
- `production_deploy.sh` - Socket-first deployment with TCP fallback
- `deployment/nginx/projectmeats-socket.conf` - Fixed health endpoints  
- `deployment/systemd/projectmeats.socket` - Socket permissions (SocketGroup=www-data)

### Diagnostic and Verification
- `deployment/scripts/diagnose_service.sh` - Added socket accessibility testing
- `deploy_production.py` - Enhanced DNS parsing and external connectivity tests

## Testing Socket Configuration

### Manual Testing Commands
```bash
# Check socket exists and permissions
ls -la /run/projectmeats.sock

# Test socket accessibility 
curl --unix-socket /run/projectmeats.sock http://localhost/health

# Check nginx configuration
nginx -t

# Check service status
systemctl status projectmeats.socket
systemctl status projectmeats
```

### Diagnostic Script
```bash
# Run comprehensive diagnostics
/opt/projectmeats/deployment/scripts/diagnose_service.sh
```

## Socket vs TCP Configuration

### Socket Configuration (Preferred)
- **Advantages**: Lower latency, better security, no network exposure
- **Service**: Uses `projectmeats-socket.service` with `Requires=projectmeats.socket`
- **Nginx upstream**: `server unix:/run/projectmeats.sock;`
- **Gunicorn bind**: `--bind unix:/run/projectmeats.sock`

### TCP Configuration (Fallback)  
- **Advantages**: Simpler troubleshooting, more familiar
- **Service**: Uses `projectmeats.service` (original)
- **Nginx upstream**: `server 127.0.0.1:8000;`
- **Gunicorn bind**: `--bind 127.0.0.1:8000`

## Expected Deployment Flow

1. **Service Setup**: Copy socket-based systemd files
2. **Socket Start**: Enable and start `projectmeats.socket`
3. **Permission Fix**: Set socket ownership to `projectmeats:www-data` with mode `660`
4. **Service Start**: Start `projectmeats.service` (depends on socket)
5. **Nginx Config**: Use `meatscentral.conf` with socket upstream
6. **Verification**: Test socket accessibility and health endpoints

## Troubleshooting

### If Socket Configuration Fails
The deployment script automatically falls back to TCP configuration:
1. Stops socket services
2. Copies TCP-based service file  
3. Restarts with TCP binding
4. Logs indicate fallback is active

### Common Socket Issues
- **Permission denied**: Check socket ownership and mode
- **No such file**: Socket service may not be running
- **Connection refused**: Django service may not be bound to socket

### Log Locations
- Django service: `journalctl -u projectmeats -f`
- Nginx errors: `tail -f /var/log/nginx/error.log`
- Deployment logs: `/var/log/projectmeats/deployment_errors.log`

## Success Indicators

After applying these fixes, you should see:
- ✅ `curl http://meatscentral.com/health` returns "healthy" 
- ✅ No "upstream connect failed" errors in nginx logs
- ✅ Socket file exists with proper permissions: `srw-rw---- projectmeats www-data`
- ✅ Services running: `systemctl is-active projectmeats.socket projectmeats nginx`