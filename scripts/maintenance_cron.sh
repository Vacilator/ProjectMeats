#!/bin/bash
# ProjectMeats Maintenance Cron Jobs
# Automated maintenance tasks for production deployment

# This script should be added to root's crontab:
# 0 2 * * * /opt/projectmeats/scripts/maintenance_cron.sh
# 0 6 * * 0 /opt/projectmeats/scripts/maintenance_cron.sh --weekly

set -euo pipefail

# Configuration
PROJECT_DIR="/opt/projectmeats"
LOG_FILE="/var/log/projectmeats/maintenance.log"
SCRIPT_DIR="$PROJECT_DIR/scripts"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Redirect output to log file
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=== ProjectMeats Maintenance - $(date) ==="

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to run health check
run_health_check() {
    log "Running health check..."
    if [ -x "$SCRIPT_DIR/health_check.sh" ]; then
        bash "$SCRIPT_DIR/health_check.sh" --domain "${DOMAIN:-localhost}"
    else
        log "Health check script not found"
    fi
}

# Function to backup database
backup_database() {
    log "Running database backup..."
    if [ -x "$SCRIPT_DIR/backup_database.sh" ]; then
        bash "$SCRIPT_DIR/backup_database.sh"
    else
        log "Backup script not found"
    fi
}

# Function to renew SSL certificates
renew_ssl() {
    log "Checking SSL certificate renewal..."
    if [ -x "$SCRIPT_DIR/ssl_automation.sh" ]; then
        bash "$SCRIPT_DIR/ssl_automation.sh" --renew
    else
        log "SSL automation script not found"
    fi
}

# Function to clean up old logs
cleanup_logs() {
    log "Cleaning up old logs..."
    
    # Clean up application logs older than 30 days
    find /opt/projectmeats/logs -name "*.log" -mtime +30 -delete 2>/dev/null || true
    find /var/log/projectmeats -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    # Clean up Docker logs if they get too large
    docker system prune -f --filter "until=720h" 2>/dev/null || true
    
    log "Log cleanup completed"
}

# Function to update system packages
update_system() {
    log "Updating system packages..."
    
    # Update package lists
    apt update
    
    # Upgrade security packages only
    unattended-upgrade
    
    log "System update completed"
}

# Function to monitor disk space
monitor_disk_space() {
    log "Monitoring disk space..."
    
    local disk_usage=$(df /opt/projectmeats | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$disk_usage" -gt 85 ]; then
        log "WARNING: Disk space is high ($disk_usage%)"
        # Could send alert email here
    else
        log "Disk space is adequate ($disk_usage%)"
    fi
}

# Function to check Docker container health
check_container_health() {
    log "Checking Docker container health..."
    
    cd "$PROJECT_DIR"
    docker-compose ps
    
    # Restart unhealthy containers
    local unhealthy_containers=$(docker ps --filter health=unhealthy --format "{{.Names}}")
    if [ -n "$unhealthy_containers" ]; then
        log "Found unhealthy containers: $unhealthy_containers"
        log "Restarting unhealthy containers..."
        echo "$unhealthy_containers" | xargs -r docker restart
    fi
}

# Main execution
main() {
    local mode="${1:-daily}"
    
    case "$mode" in
        "--daily"|"daily")
            log "Running daily maintenance tasks..."
            run_health_check
            backup_database
            cleanup_logs
            monitor_disk_space
            check_container_health
            ;;
        "--weekly"|"weekly")
            log "Running weekly maintenance tasks..."
            run_health_check
            backup_database
            renew_ssl
            cleanup_logs
            update_system
            monitor_disk_space
            check_container_health
            ;;
        "--health"|"health")
            log "Running health check only..."
            run_health_check
            ;;
        *)
            echo "Usage: $0 [--daily|--weekly|--health]"
            exit 1
            ;;
    esac
    
    log "Maintenance completed successfully"
}

# Run with first argument or default to daily
main "${1:-daily}"