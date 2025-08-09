#!/bin/bash
# Test script to validate the Django service fix
# This simulates what the fixed deployment script would do

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🧪 ProjectMeats Django Service Fix Validation"
echo "============================================="

# Get the current directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="/tmp/projectmeats_test"

log_info "Creating test environment..."
mkdir -p $TEST_DIR/log
mkdir -p $TEST_DIR/run
mkdir -p $TEST_DIR/media

# Test 1: Verify Django configuration
log_info "Test 1: Verifying Django configuration..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate

export DJANGO_SETTINGS_MODULE=apps.settings.production
export DEBUG=False
export SECRET_KEY="test-key-for-validation"
export ALLOWED_HOSTS="localhost,127.0.0.1"

if python manage.py check --settings=apps.settings.production > /dev/null 2>&1; then
    log_success "✅ Django configuration is valid"
else
    log_error "❌ Django configuration has issues"
    exit 1
fi

# Test 2: Verify WSGI module loads
log_info "Test 2: Verifying WSGI module loads..."
if python -c "import projectmeats.wsgi; print('WSGI loaded successfully')" > /dev/null 2>&1; then
    log_success "✅ WSGI module loads successfully"
else
    log_error "❌ WSGI module failed to load"
    exit 1
fi

# Test 3: Test Gunicorn startup with log directories
log_info "Test 3: Testing Gunicorn startup with proper directories..."
timeout 5 gunicorn \
    --bind 127.0.0.1:8003 \
    --workers 1 \
    --worker-class gthread \
    --threads 2 \
    --preload \
    --access-logfile $TEST_DIR/log/access.log \
    --error-logfile $TEST_DIR/log/error.log \
    --pid $TEST_DIR/run/gunicorn.pid \
    projectmeats.wsgi:application \
    --daemon

sleep 2

if [ -f "$TEST_DIR/run/gunicorn.pid" ]; then
    PID=$(cat $TEST_DIR/run/gunicorn.pid)
    if kill -0 $PID 2>/dev/null; then
        log_success "✅ Gunicorn started successfully with PID: $PID"
        kill $PID 2>/dev/null || true
        wait $PID 2>/dev/null || true
    else
        log_error "❌ Gunicorn PID file exists but process not running"
        exit 1
    fi
else
    log_error "❌ Gunicorn PID file not created"
    exit 1
fi

# Test 4: Verify log files were created
log_info "Test 4: Verifying log files..."
if [ -f "$TEST_DIR/log/access.log" ] && [ -f "$TEST_DIR/log/error.log" ]; then
    log_success "✅ Log files created successfully"
    log_info "Access log: $(ls -la $TEST_DIR/log/access.log)"
    log_info "Error log: $(ls -la $TEST_DIR/log/error.log)"
    
    # Check error log for any startup issues
    if grep -q "ERROR" $TEST_DIR/log/error.log; then
        log_warning "⚠️  Errors found in log file:"
        grep "ERROR" $TEST_DIR/log/error.log
    else
        log_success "✅ No errors in log file"
    fi
else
    log_error "❌ Log files not created"
    exit 1
fi

# Test 5: Simulate systemd environment requirements
log_info "Test 5: Simulating systemd environment requirements..."

# Check if the service file exists
if [ -f "$PROJECT_DIR/deployment/systemd/projectmeats.service" ]; then
    log_success "✅ Systemd service file exists"
    
    # Validate service file syntax (basic check)
    if grep -q "ExecStart.*gunicorn" "$PROJECT_DIR/deployment/systemd/projectmeats.service"; then
        log_success "✅ Service file contains gunicorn command"
    else
        log_error "❌ Service file missing gunicorn command"
        exit 1
    fi
    
    # Check ReadWritePaths includes required directories
    if grep -q "ReadWritePaths=.*\/var\/log\/projectmeats.*\/var\/run\/projectmeats" "$PROJECT_DIR/deployment/systemd/projectmeats.service"; then
        log_success "✅ Service file allows writes to required directories"
    else
        log_error "❌ Service file missing required ReadWritePaths"
        exit 1
    fi
else
    log_error "❌ Systemd service file not found"
    exit 1
fi

# Test 6: Verify fix_django_service.sh has directory creation
log_info "Test 6: Verifying fix script creates required directories..."
if grep -q "mkdir -p /var/log/projectmeats" "$PROJECT_DIR/fix_django_service.sh"; then
    log_success "✅ Fix script creates log directory"
else
    log_error "❌ Fix script missing log directory creation"
    exit 1
fi

if grep -q "mkdir -p /var/run/projectmeats" "$PROJECT_DIR/fix_django_service.sh"; then
    log_success "✅ Fix script creates run directory" 
else
    log_error "❌ Fix script missing run directory creation"
    exit 1
fi

if grep -q "chown www-data:www-data /var/log/projectmeats" "$PROJECT_DIR/fix_django_service.sh"; then
    log_success "✅ Fix script sets proper ownership"
else
    log_error "❌ Fix script missing ownership setup"
    exit 1
fi

# Cleanup
log_info "Cleaning up test environment..."
rm -rf $TEST_DIR

echo ""
echo "🎉 All Tests Passed!"
echo "===================="
echo ""
log_success "The Django service fix has been validated successfully."
echo ""
log_info "Summary of fixes:"
echo "  • Django configuration works with production settings"
echo "  • WSGI module loads correctly"
echo "  • Gunicorn starts successfully with proper log/pid directories"
echo "  • Log files are created as expected"
echo "  • Systemd service configuration is valid"
echo "  • Deployment script creates required directories with proper permissions"
echo ""
log_info "The service startup issue should now be resolved."