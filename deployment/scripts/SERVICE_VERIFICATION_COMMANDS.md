# ProjectMeats Service Verification Commands

## Check service status
sudo systemctl status projectmeats.service

## View recent logs  
sudo journalctl -u projectmeats.service -f

## Additional useful commands

### Service Management
```bash
# Check if service is running
sudo systemctl is-active projectmeats.service

# Check if service is enabled (auto-start)
sudo systemctl is-enabled projectmeats.service

# Restart the service
sudo systemctl restart projectmeats.service

# Stop the service
sudo systemctl stop projectmeats.service

# Start the service
sudo systemctl start projectmeats.service
```

### Log Viewing Options
```bash
# View all logs for the service
sudo journalctl -u projectmeats.service

# View logs and follow new entries
sudo journalctl -u projectmeats.service -f

# View last 50 log entries
sudo journalctl -u projectmeats.service -n 50

# View logs since boot
sudo journalctl -u projectmeats.service -b

# View logs from last hour
sudo journalctl -u projectmeats.service --since "1 hour ago"

# View logs with full timestamps
sudo journalctl -u projectmeats.service -o short-iso
```

### Socket-specific Commands
```bash
# Check socket status
sudo systemctl status projectmeats.socket

# View socket logs
sudo journalctl -u projectmeats.socket -f

# List active sockets
sudo systemctl list-sockets | grep projectmeats

# Test socket connectivity (if projectmeats user exists)
sudo -u projectmeats curl --unix-socket /run/projectmeats.sock http://localhost/health/
```