#!/bin/bash
# Test script to validate the permission fixes for systemd issues
set -e

echo "=== Testing ProjectMeats Permission Fixes ==="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_info() { echo -e "${YELLOW}[INFO]${NC} $1"; }

# Test 1: Pre-start script no longer tries to run privileged operations
echo "=== Test 1: Pre-start Script Privilege Removal ==="
log_info "Checking that pre_start_service.sh no longer contains chown commands..."

if grep -q "^[^#]*chown" deployment/scripts/pre_start_service.sh; then
    log_error "✗ Pre-start script still contains chown commands"
    exit 1
else
    log_success "✓ Pre-start script no longer contains privileged chown operations"
fi

# Test 2: Deployment scripts handle log file creation
echo "=== Test 2: Log File Creation in Deployment Scripts ==="
log_info "Checking that deployment scripts create log files..."

scripts_to_check=(
    "production_deploy.sh"
    "deployment/scripts/quick_server_fix.sh"
    "deployment/scripts/fix_permissions.sh"
)

for script in "${scripts_to_check[@]}"; do
    if grep -q "touch.*log" "$script"; then
        log_success "✓ $script creates log files"
    else
        log_error "✗ $script does not create log files"
        exit 1
    fi
done

# Test 3: Systemd service files have improved ExecStopPost
echo "=== Test 3: Systemd Service ExecStopPost Improvements ==="
log_info "Checking that ExecStopPost uses safer approach..."

service_files=(
    "deployment/systemd/projectmeats.service"
    "deployment/systemd/projectmeats-socket.service"
)

for service_file in "${service_files[@]}"; do
    if grep -q "ExecStopPost.*tmp.*mv" "$service_file"; then
        log_success "✓ $service_file uses safer ExecStopPost with temp file"
    elif ! grep -q "ExecStopPost" "$service_file"; then
        log_info "⚠ $service_file has no ExecStopPost (acceptable)"
    else
        log_error "✗ $service_file has problematic ExecStopPost"
        exit 1
    fi
done

# Test 4: User and group consistency
echo "=== Test 4: User and Group Consistency ==="
log_info "Checking for consistent projectmeats:www-data usage..."

files_to_check=(
    "production_deploy.sh"
    "deployment/scripts/quick_server_fix.sh"
    "deployment/scripts/fix_permissions.sh"
)

for file in "${files_to_check[@]}"; do
    if grep -q "projectmeats:www-data" "$file" || grep -q "usermod.*www-data.*projectmeats" "$file"; then
        log_success "✓ $file uses consistent projectmeats:www-data ownership"
    else
        log_error "✗ $file does not use consistent ownership"
        exit 1
    fi
done

# Test 5: SuccessExitStatus includes hook failure tolerance
echo "=== Test 5: Service Hook Failure Tolerance ==="
log_info "Checking that services tolerate hook failures..."

for service_file in "${service_files[@]}"; do
    if grep -q "SuccessExitStatus=0 1 2" "$service_file"; then
        log_success "✓ $service_file tolerates hook failures"
    else
        log_error "✗ $service_file does not tolerate hook failures"
        exit 1
    fi
done

# Test 6: Directory creation in deployment scripts
echo "=== Test 6: Directory Creation in Deployment Scripts ==="
log_info "Checking that directories are created before service starts..."

required_dirs=(
    "/var/log/projectmeats"
    "/var/run/projectmeats"
)

for script in "${scripts_to_check[@]}"; do
    for dir in "${required_dirs[@]}"; do
        if grep -q "mkdir.*$dir" "$script"; then
            log_success "✓ $script creates directory $dir"
        fi
    done
done

# Test 7: Pre-start script now does verification only
echo "=== Test 7: Pre-start Script Verification Mode ==="
log_info "Checking that pre-start script only verifies permissions..."

if grep -q "does not exist" deployment/scripts/pre_start_service.sh && 
   grep -q "not writable" deployment/scripts/pre_start_service.sh; then
    log_success "✓ Pre-start script now performs verification checks"
else
    log_error "✗ Pre-start script does not perform proper verification"
    exit 1
fi

# Test 8: No more mkdir/chown in pre_start_service.sh
echo "=== Test 8: No Privileged Operations in Pre-start Script ==="
log_info "Verifying pre-start script contains no privileged operations..."

privileged_ops=("mkdir" "chown" "chmod")
for op in "${privileged_ops[@]}"; do
    if grep -q "^[^#]*$op" deployment/scripts/pre_start_service.sh; then
        log_error "✗ Pre-start script still contains privileged operation: $op"
        exit 1
    fi
done

log_success "✓ Pre-start script contains no privileged operations"

echo ""
echo "=== All Permission Fix Tests Passed! ==="
log_success "✅ Systemd permission issues have been properly addressed"

echo ""
echo "Summary of fixes implemented:"
echo "• Moved log directory/file creation to deployment scripts (before service starts)"
echo "• Removed privileged chown/mkdir operations from pre_start_service.sh"
echo "• Updated ExecStopPost to use safer temp file approach"
echo "• Added hook failure tolerance with SuccessExitStatus=0 1 2"
echo "• Ensured consistent projectmeats:www-data user/group usage"
echo "• Pre-start script now only verifies permissions instead of setting them"