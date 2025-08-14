# ProjectMeats SystemD Configuration Guide

This directory contains the complete SystemD service configuration for ProjectMeats Django application using Unix socket communication with Gunicorn and Nginx.

## Files Overview

### SystemD Service Files

1. **`projectmeats-socket.service`** - Main service file for socket-based deployment
   - Uses `projectmeats` user/group instead of `www-data`
   - Binds to Unix socket `/run/projectmeats.sock`
   - Configured for socket activation with `Requires=projectmeats.socket`

2. **`projectmeats.socket`** - SystemD socket file for Gunicorn
   - Listens on `/run/projectmeats.sock`
   - Proper permissions for `projectmeats` user/group
   - Enables socket-based activation

3. **`projectmeats.service`** - Original TCP-based service file (preserved for compatibility)

### Management Scripts

Located in `deployment/scripts/`:

1. **`reload_and_start_services.sh`** - Service management script
   - Reloads systemd daemon
   - Enables and starts `projectmeats.socket`
   - Enables and starts `projectmeats.service`
   - Usage: `sudo ./reload_and_start_services.sh`

2. **`verify_service.sh`** - Service verification and monitoring
   - Checks `projectmeats.service` status
   - Views recent logs with `journalctl`
   - Displays useful management commands
   - Usage: `sudo ./verify_service.sh`

3. **`rerun_deployment.sh`** - Quick deployment restart
   - Single command to rerun `/opt/projectmeats/one_click_deploy.sh`
   - Automatically handles permissions
   - Usage: `sudo ./rerun_deployment.sh`

### Nginx Configuration

1. **`projectmeats-socket.conf`** - Updated Nginx configuration for Unix socket
   - Proxies to `unix:/run/projectmeats.sock`
   - Includes required security headers
   - Proper proxy headers for Django

2. **`projectmeats.conf`** - Original TCP-based configuration (preserved)

## Key Differences from TCP Configuration

| Feature | TCP Version | Socket Version |
|---------|-------------|----------------|
| User/Group | `www-data` | `projectmeats` |
| Binding | `127.0.0.1:8000` | `unix:/run/projectmeats.sock` |
| Nginx Upstream | `server 127.0.0.1:8000;` | `server unix:/run/projectmeats.sock;` |
| Service Type | `Type=simple` | `Type=notify` with socket |
| Restart Policy | `on-failure` | `always` |

## Installation Instructions

### 1. Deploy Socket-Based Configuration

```bash
# Copy service files
sudo cp deployment/systemd/projectmeats-socket.service /etc/systemd/system/projectmeats.service
sudo cp deployment/systemd/projectmeats.socket /etc/systemd/system/

# Copy Nginx configuration
sudo cp deployment/nginx/projectmeats-socket.conf /etc/nginx/sites-available/projectmeats
sudo ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/

# Run setup script
sudo ./deployment/scripts/reload_and_start_services.sh
```

### 2. Verify Installation

```bash
# Check service status
sudo ./deployment/scripts/verify_service.sh

# Or manually check
sudo systemctl status projectmeats.service
sudo systemctl status projectmeats.socket
```

### 3. Troubleshooting

```bash
# View service logs
sudo journalctl -u projectmeats.service -f

# View socket logs
sudo journalctl -u projectmeats.socket -f

# Test socket connection
sudo -u projectmeats curl --unix-socket /run/projectmeats.sock http://localhost/

# Restart services
sudo systemctl restart projectmeats.service
sudo systemctl restart nginx
```

## Service Management Commands

### Quick Commands Reference

```bash
# Status checks
sudo systemctl status projectmeats.service
sudo systemctl status projectmeats.socket

# Start/Stop/Restart
sudo systemctl start projectmeats.service
sudo systemctl stop projectmeats.service
sudo systemctl restart projectmeats.service

# Enable/Disable (auto-start)
sudo systemctl enable projectmeats.service
sudo systemctl enable projectmeats.socket
sudo systemctl disable projectmeats.service

# Logs
sudo journalctl -u projectmeats.service -f          # Follow logs
sudo journalctl -u projectmeats.service -n 50      # Last 50 lines
sudo journalctl -u projectmeats.service --since "1 hour ago"
```

## Automated Deployment Enhancement

The `one_click_deploy.sh` script has been enhanced to:

1. **Check for existing service**: Automatically detects if `projectmeats.service` exists
2. **Auto-create service**: If missing, creates both service and socket files
3. **Configure SystemD**: Runs `daemon-reload`, enables services
4. **Continue deployment**: Proceeds with normal deployment process

This ensures the service is always properly configured during deployment.

## Security Features

The socket-based configuration includes enhanced security:

- **User isolation**: Runs as `projectmeats` user instead of `www-data`
- **Filesystem protection**: `ProtectSystem=strict`, `ProtectHome=true`
- **Process isolation**: `NoNewPrivileges=true`
- **Socket permissions**: Restricted to `projectmeats` user/group (mode 0660)
- **Read-only paths**: Only specific directories are writable

## Performance Benefits

Socket-based communication offers:

- **Lower latency**: Direct Unix socket communication vs TCP loopback
- **Reduced overhead**: No TCP/IP stack involvement
- **Better security**: No network exposure of application port
- **Resource efficiency**: Less memory and CPU usage for IPC

## Migration from TCP to Socket

To migrate from the existing TCP configuration:

1. **Backup current config**: `sudo cp /etc/systemd/system/projectmeats.service /etc/systemd/system/projectmeats.service.backup`
2. **Install socket version**: Follow installation instructions above
3. **Test thoroughly**: Verify application functionality
4. **Update monitoring**: Adjust any monitoring tools to check socket instead of TCP port

## File Permissions

Ensure proper permissions are set:

```bash
# Service files
sudo chown root:root /etc/systemd/system/projectmeats.service
sudo chown root:root /etc/systemd/system/projectmeats.socket
sudo chmod 644 /etc/systemd/system/projectmeats.service
sudo chmod 644 /etc/systemd/system/projectmeats.socket

# Runtime directories
sudo mkdir -p /var/log/projectmeats /var/run/projectmeats
sudo chown projectmeats:projectmeats /var/log/projectmeats /var/run/projectmeats
sudo chmod 755 /var/log/projectmeats /var/run/projectmeats

# Socket file (created automatically by systemd)
# /run/projectmeats.sock will be owned by projectmeats:projectmeats with mode 0660
```