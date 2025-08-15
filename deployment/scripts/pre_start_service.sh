#!/bin/bash
# Pre-start script for ProjectMeats service
# Ensures proper permissions and setup before service starts

set -e

# Configuration
PROJECT_DIR="/opt/projectmeats"
LOG_DIR="/var/log/projectmeats"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Set proper ownership and permissions for log directory
chown projectmeats:www-data "$LOG_DIR"
chmod 775 "$LOG_DIR"

# Pre-create log files with proper permissions
touch "$LOG_DIR/error.log"
touch "$LOG_DIR/access.log"
touch "$LOG_DIR/post_failure.log"

# Set proper ownership and permissions for log files
chown projectmeats:www-data "$LOG_DIR/error.log"
chown projectmeats:www-data "$LOG_DIR/access.log"
chown projectmeats:www-data "$LOG_DIR/post_failure.log"

chmod 664 "$LOG_DIR/error.log"
chmod 664 "$LOG_DIR/access.log"
chmod 664 "$LOG_DIR/post_failure.log"

# Ensure socket directory has proper permissions
mkdir -p /var/run/projectmeats
chown projectmeats:www-data /var/run/projectmeats
chmod 775 /var/run/projectmeats

# Set permissions for socket file if it exists
if [ -f /run/projectmeats.sock ]; then
    chown projectmeats:www-data /run/projectmeats.sock
    chmod 660 /run/projectmeats.sock
fi

exit 0