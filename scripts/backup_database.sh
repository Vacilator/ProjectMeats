#!/bin/bash
# ProjectMeats Backup Automation Script
# Handles automated database backups with rotation and compression

set -euo pipefail

# Configuration
BACKUP_DIR="/opt/projectmeats/backups"
POSTGRES_CONTAINER="projectmeats-db"
DATABASE_NAME="projectmeats"
DATABASE_USER="projectmeats"
RETENTION_DAYS=30
COMPRESSION_ENABLED=true
BACKUP_PREFIX="projectmeats-backup"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILENAME="${BACKUP_PREFIX}-${TIMESTAMP}.sql"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILENAME}"

log "Starting database backup..."
log "Backup file: ${BACKUP_FILENAME}"

# Perform database backup
if docker exec "$POSTGRES_CONTAINER" pg_dump -U "$DATABASE_USER" -d "$DATABASE_NAME" --verbose > "$BACKUP_PATH"; then
    success "Database backup completed successfully"
    
    # Get backup file size
    BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
    success "Backup size: $BACKUP_SIZE"
    
    # Compress backup if enabled
    if [ "$COMPRESSION_ENABLED" = true ]; then
        log "Compressing backup..."
        if gzip "$BACKUP_PATH"; then
            COMPRESSED_SIZE=$(du -h "${BACKUP_PATH}.gz" | cut -f1)
            success "Backup compressed successfully (${COMPRESSED_SIZE})"
            BACKUP_PATH="${BACKUP_PATH}.gz"
        else
            warning "Backup compression failed, keeping uncompressed version"
        fi
    fi
    
    # Cleanup old backups
    log "Cleaning up old backups (keeping last ${RETENTION_DAYS} days)..."
    find "$BACKUP_DIR" -name "${BACKUP_PREFIX}-*.sql*" -mtime +$RETENTION_DAYS -delete
    
    # Count remaining backups
    BACKUP_COUNT=$(find "$BACKUP_DIR" -name "${BACKUP_PREFIX}-*.sql*" | wc -l)
    success "Backup cleanup completed. $BACKUP_COUNT backup(s) retained."
    
    # Verify backup integrity
    log "Verifying backup integrity..."
    if [ "$COMPRESSION_ENABLED" = true ]; then
        if gzip -t "$BACKUP_PATH" 2>/dev/null; then
            success "Backup integrity verified"
        else
            error "Backup integrity check failed!"
            exit 1
        fi
    else
        if [ -s "$BACKUP_PATH" ]; then
            success "Backup integrity verified"
        else
            error "Backup file is empty or corrupted!"
            exit 1
        fi
    fi
    
    # Send backup status to monitoring (optional)
    # curl -X POST http://localhost:9090/metrics/backup/success || true
    
    success "Backup process completed successfully"
    
else
    error "Database backup failed!"
    exit 1
fi