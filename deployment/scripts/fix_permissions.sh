#!/bin/bash
# ProjectMeats Permission Fix Script
# Ensures consistent ownership and permissions across all deployment components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

PROJECT_DIR="${1:-/opt/projectmeats}"

# Check if running as root
if [ $EUID -ne 0 ]; then
    log_error "This script must be run as root"
    exit 1
fi

log_info "Fixing permissions and ownership for ProjectMeats deployment"
log_info "Project directory: $PROJECT_DIR"

# Create projectmeats user if it doesn't exist
if ! id "projectmeats" &>/dev/null; then
    log_info "Creating projectmeats user..."
    useradd --system --home-dir "$PROJECT_DIR" --shell /bin/bash --group www-data projectmeats
    log_success "Created projectmeats user"
else
    log_info "projectmeats user already exists"
fi

# Create required directories
log_info "Creating and setting permissions on directories..."

directories=(
    "/var/log/projectmeats"
    "/var/run/projectmeats"
    "/run"
    "/etc/projectmeats"
    "$PROJECT_DIR"
    "$PROJECT_DIR/backend"
    "$PROJECT_DIR/frontend"
    "$PROJECT_DIR/backend/media"
    "$PROJECT_DIR/backend/staticfiles"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log_success "Created directory: $dir"
    fi
done

# Set ownership - projectmeats user with www-data group for web server access
log_info "Setting ownership..."
chown -R projectmeats:www-data "$PROJECT_DIR"
chown -R projectmeats:www-data "/var/log/projectmeats"
chown -R projectmeats:www-data "/var/run/projectmeats"
chown projectmeats:www-data "/etc/projectmeats" 2>/dev/null || true

# Set directory permissions
log_info "Setting directory permissions..."
chmod 755 "$PROJECT_DIR"
chmod 755 "$PROJECT_DIR/backend"
chmod 755 "$PROJECT_DIR/frontend" 2>/dev/null || true
chmod 775 "$PROJECT_DIR/backend/media"
chmod 775 "$PROJECT_DIR/backend/staticfiles"
chmod 775 "/var/log/projectmeats"
chmod 775 "/var/run/projectmeats"
chmod 755 "/etc/projectmeats" 2>/dev/null || true

# Set file permissions for critical files
log_info "Setting file permissions..."

# Make gunicorn executable
if [ -f "$PROJECT_DIR/venv/bin/gunicorn" ]; then
    chmod 755 "$PROJECT_DIR/venv/bin/gunicorn"
    log_success "Set gunicorn executable permissions"
fi

# Secure environment files
env_files=(
    "/etc/projectmeats/projectmeats.env"
    "$PROJECT_DIR/.env.production" 
    "$PROJECT_DIR/backend/.env"
)

for env_file in "${env_files[@]}"; do
    if [ -f "$env_file" ]; then
        chown projectmeats:www-data "$env_file"
        chmod 640 "$env_file"
        log_success "Secured $env_file"
    fi
done

# Set permissions for socket directory
if [ -d "/run" ]; then
    # Ensure /run/projectmeats.sock can be created
    chmod 755 "/run"
    log_success "Set /run directory permissions"
fi

# Make management scripts executable
if [ -d "$PROJECT_DIR/scripts" ]; then
    chmod 755 "$PROJECT_DIR/scripts"/*.sh 2>/dev/null || true
    log_success "Set management scripts executable"
fi

# Set systemd service files permissions  
systemd_files=(
    "/etc/systemd/system/projectmeats.service"
    "/etc/systemd/system/projectmeats.socket"
    "/etc/systemd/system/projectmeats-socket.service"
)

for service_file in "${systemd_files[@]}"; do
    if [ -f "$service_file" ]; then
        chmod 644 "$service_file"
        log_success "Set permissions for $service_file"
    fi
done

# Verification
log_info "Verifying permissions..."

# Check critical paths
critical_paths=(
    "$PROJECT_DIR/backend/manage.py"
    "$PROJECT_DIR/venv/bin/gunicorn"
    "/var/log/projectmeats"
    "/var/run/projectmeats"
)

for path in "${critical_paths[@]}"; do
    if [ -e "$path" ]; then
        owner=$(stat -c '%U:%G' "$path")
        perms=$(stat -c '%a' "$path")
        log_info "$path - Owner: $owner, Permissions: $perms"
    else
        log_warning "$path does not exist"
    fi
done

log_success "✅ Permission fix completed successfully"

# Test permissions by trying to create a test file as projectmeats user
log_info "Testing permissions..."
if sudo -u projectmeats touch "$PROJECT_DIR/permission_test" 2>/dev/null; then
    rm "$PROJECT_DIR/permission_test"
    log_success "✅ projectmeats user can write to project directory"
else
    log_error "❌ projectmeats user cannot write to project directory"
    exit 1
fi

if sudo -u projectmeats touch "/var/log/projectmeats/permission_test" 2>/dev/null; then
    rm "/var/log/projectmeats/permission_test"
    log_success "✅ projectmeats user can write to log directory"
else
    log_error "❌ projectmeats user cannot write to log directory"
    exit 1
fi

log_success "🎉 All permission checks passed!"