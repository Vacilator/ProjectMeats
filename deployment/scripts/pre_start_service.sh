#!/bin/bash
# Pre-start script for ProjectMeats service
# Performs non-privileged checks before service starts
# NOTE: Privileged operations moved to deployment scripts

set -e

# Configuration
PROJECT_DIR="/opt/projectmeats"
LOG_DIR="/var/log/projectmeats"

# Verify log directory and files exist (but don't try to create/chown them)
if [ ! -d "$LOG_DIR" ]; then
    echo "ERROR: Log directory $LOG_DIR does not exist"
    echo "Run deployment/scripts/fix_permissions.sh to create it"
    exit 1
fi

# Verify log files exist and are writable by current user
for log_file in "error.log" "access.log" "post_failure.log"; do
    if [ ! -f "$LOG_DIR/$log_file" ]; then
        echo "ERROR: Log file $LOG_DIR/$log_file does not exist"
        echo "Run deployment scripts to create log files with proper permissions"
        exit 1
    fi
    
    if [ ! -w "$LOG_DIR/$log_file" ]; then
        echo "ERROR: Log file $LOG_DIR/$log_file is not writable by projectmeats user"
        echo "Run deployment/scripts/fix_permissions.sh to fix permissions"
        exit 1
    fi
done

# Verify socket directory exists (but don't try to create/chown it)
if [ ! -d "/var/run/projectmeats" ]; then
    echo "ERROR: Socket directory /var/run/projectmeats does not exist"
    echo "Run deployment scripts to create it with proper permissions"
    exit 1
fi

echo "Pre-start checks passed - all directories and files exist with proper permissions"
exit 0