#!/bin/bash
# Test script to verify the fixes for settings.py and systemd service issues

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🧪 ProjectMeats Fixes Verification Test"
echo "======================================"
echo

# Test 1: Settings.py file existence (original failing check)
log_info "Test 1: Verifying settings.py file exists where deployment script expects it..."
if test -f backend/apps/settings/settings.py; then
    log_success "✅ settings.py file found at backend/apps/settings/settings.py"
else
    log_error "❌ settings.py file missing - deployment will fail"
    exit 1
fi

# Test 2: Django configuration validation
log_info "Test 2: Testing Django configuration with new settings file..."
cd backend
if python manage.py check --settings=apps.settings.settings >/dev/null 2>&1; then
    log_success "✅ Django configuration valid with apps.settings.settings"
else
    log_error "❌ Django configuration failed with new settings file"
    exit 1
fi

# Test 3: Production settings work via new settings file
log_info "Test 3: Testing production settings selection..."
if DJANGO_ENV=production python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings.settings'); import django; django.setup(); from django.conf import settings; assert not settings.DEBUG, 'Production mode should have DEBUG=False'" >/dev/null 2>&1; then
    log_success "✅ Production settings correctly selected (DEBUG=False)"
else
    log_error "❌ Production settings not working correctly"
    exit 1
fi

# Test 4: Development settings work via new settings file
log_info "Test 4: Testing development settings selection..."
if DJANGO_ENV=development python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings.settings'); import django; django.setup(); from django.conf import settings; assert settings.DEBUG, 'Development mode should have DEBUG=True'" >/dev/null 2>&1; then
    log_success "✅ Development settings correctly selected (DEBUG=True)"
else
    log_error "❌ Development settings not working correctly"
    exit 1
fi

# Test 5: Original modular settings still work
log_info "Test 5: Verifying original modular settings still function..."
if python manage.py check --settings=apps.settings.production >/dev/null 2>&1; then
    log_success "✅ Original modular production settings still work"
else
    log_error "❌ Original modular settings broken"
    exit 1
fi

# Test 6: SystemD service file exists
log_info "Test 6: Verifying systemd service file exists..."
cd ..
if test -f deployment/systemd/projectmeats.service; then
    log_success "✅ SystemD service file found at deployment/systemd/projectmeats.service"
else
    log_error "❌ SystemD service file missing"
    exit 1
fi

# Test 7: SystemD service installation script exists
log_info "Test 7: Verifying systemd installation script exists..."
if test -f install_systemd_service.sh; then
    log_success "✅ SystemD installation script found"
else
    log_error "❌ SystemD installation script missing"
    exit 1
fi

# Test 8: Simulate all deployment script checks
log_info "Test 8: Simulating original deployment script file checks..."
checks_passed=0
total_checks=4

if test -f backend/manage.py; then
    echo "  - manage.py exists: ✅"
    ((checks_passed++))
else
    echo "  - manage.py exists: ❌"
fi

if test -f backend/requirements.txt; then
    echo "  - requirements.txt exists: ✅"
    ((checks_passed++))
else
    echo "  - requirements.txt exists: ❌"
fi

if test -f frontend/package.json; then
    echo "  - package.json exists: ✅"
    ((checks_passed++))
else
    echo "  - package.json exists: ❌"
fi

if test -f backend/apps/settings/settings.py; then
    echo "  - settings.py exists: ✅"
    ((checks_passed++))
else
    echo "  - settings.py exists: ❌"
fi

if [ $checks_passed -eq $total_checks ]; then
    log_success "✅ All deployment script file checks pass ($checks_passed/$total_checks)"
else
    log_error "❌ Some deployment checks failed ($checks_passed/$total_checks)"
    exit 1
fi

echo
echo "🎉 All Tests Passed!"
echo "==================="
echo
log_success "The fixes have been successfully verified:"
echo "  • settings.py file created and working correctly"
echo "  • Environment-based settings selection functional"
echo "  • Original modular settings preserved"
echo "  • SystemD service files ready for deployment"
echo "  • All deployment script checks now pass"
echo
log_info "The original deployment errors should now be resolved:"
echo "  ❌ 'backend/apps/settings/settings.py' missing → ✅ Fixed"
echo "  ❌ 'Unit projectmeats.service not found' → ✅ Installation script ready"