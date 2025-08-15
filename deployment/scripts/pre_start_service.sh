#!/bin/bash
# Pre-start script for ProjectMeats service
# Ensures proper permissions and setup before service starts

set -e

# Configuration
PROJECT_DIR="/opt/projectmeats"
LOG_DIR="/var/log/projectmeats"

# Create log directory if it doesn't exist - use full path
/bin/mkdir -p "$LOG_DIR"

# Set proper ownership and permissions for log directory - use full paths
/bin/chown projectmeats:www-data "$LOG_DIR"
/bin/chmod 775 "$LOG_DIR"

# Pre-create log files with proper permissions - use full path
/bin/touch "$LOG_DIR/error.log"
/bin/touch "$LOG_DIR/access.log"
/bin/touch "$LOG_DIR/post_failure.log"

# Set proper ownership and permissions for log files - use full paths
/bin/chown projectmeats:www-data "$LOG_DIR/error.log"
/bin/chown projectmeats:www-data "$LOG_DIR/access.log"
/bin/chown projectmeats:www-data "$LOG_DIR/post_failure.log"

/bin/chmod 664 "$LOG_DIR/error.log"
/bin/chmod 664 "$LOG_DIR/access.log"
/bin/chmod 664 "$LOG_DIR/post_failure.log"

# Ensure socket directory has proper permissions - use full paths
/bin/mkdir -p /var/run/projectmeats
/bin/chown projectmeats:www-data /var/run/projectmeats
/bin/chmod 775 /var/run/projectmeats

# Set permissions for socket file if it exists - use full paths
if [ -f /run/projectmeats.sock ]; then
    /bin/chown projectmeats:www-data /run/projectmeats.sock
    /bin/chmod 660 /run/projectmeats.sock
fi

exit 0