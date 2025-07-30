#!/bin/bash
# Production Build Verification Script for ProjectMeats
# This script validates both backend and frontend are ready for production

set -e  # Exit on any error

echo "🚀 ProjectMeats Production Build Verification"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "info")
            echo -e "ℹ️  $message"
            ;;
    esac
}

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_status "error" "Must be run from ProjectMeats root directory"
    exit 1
fi

print_status "info" "Starting production build verification..."

# Backend checks
echo ""
echo "🐍 Backend Verification"
echo "----------------------"

cd backend

# Check if virtual environment should be activated
if [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    print_status "warning" "Virtual environment detected but not activated"
    print_status "info" "Consider running: source backend/venv/bin/activate"
fi

# Install/check dependencies
print_status "info" "Checking backend dependencies..."
if pip install -r requirements.txt > /dev/null 2>&1; then
    print_status "success" "Backend dependencies verified"
else
    print_status "error" "Failed to install backend dependencies"
    exit 1
fi

# Run tests
print_status "info" "Running backend tests..."
if python manage.py test --keepdb -v 0 > /dev/null 2>&1; then
    print_status "success" "All backend tests passing"
else
    print_status "error" "Backend tests failed"
    exit 1
fi

# Check migrations
print_status "info" "Checking for unapplied migrations..."
if python manage.py showmigrations --plan | grep -q "\[ \]"; then
    print_status "warning" "Unapplied migrations detected - run 'python manage.py migrate'"
else
    print_status "success" "All migrations applied"
fi

# Collect static files test
print_status "info" "Testing static file collection..."
if python manage.py collectstatic --noinput --dry-run > /dev/null 2>&1; then
    print_status "success" "Static file collection ready"
else
    print_status "warning" "Static file collection may have issues"
fi

cd ..

# Frontend checks
echo ""
echo "⚛️  Frontend Verification"
echo "-----------------------"

cd frontend

# Check Node.js version
NODE_VERSION=$(node --version 2>/dev/null || echo "not found")
if [ "$NODE_VERSION" != "not found" ]; then
    print_status "success" "Node.js version: $NODE_VERSION"
else
    print_status "error" "Node.js not found"
    exit 1
fi

# Install dependencies
print_status "info" "Installing frontend dependencies..."
if npm install > /dev/null 2>&1; then
    print_status "success" "Frontend dependencies installed"
else
    print_status "error" "Failed to install frontend dependencies"
    exit 1
fi

# Type checking
print_status "info" "Running TypeScript type checking..."
if npm run type-check > /dev/null 2>&1; then
    print_status "success" "TypeScript types are valid"
else
    print_status "warning" "TypeScript type checking failed"
fi

# Production build
print_status "info" "Building production frontend..."
if npm run build > /dev/null 2>&1; then
    print_status "success" "Frontend production build successful"
    
    # Check build size
    BUILD_SIZE=$(du -sh build 2>/dev/null | cut -f1 || echo "unknown")
    print_status "info" "Build size: $BUILD_SIZE"
    
    # Check if build directory has expected files
    if [ -f "build/index.html" ] && [ -d "build/static" ]; then
        print_status "success" "Build artifacts verified"
    else
        print_status "warning" "Build artifacts may be incomplete"
    fi
else
    print_status "error" "Frontend production build failed"
    exit 1
fi

cd ..

# Final checks
echo ""
echo "🔍 Final Production Readiness Checks"
echo "===================================="

# Check environment templates
if [ -f "backend/.env.production.template" ]; then
    print_status "success" "Production environment template exists"
else
    print_status "warning" "Production environment template missing"
fi

# Check documentation
if [ -f "docs/production_deployment.md" ]; then
    print_status "success" "Production deployment documentation exists"
else
    print_status "warning" "Production deployment documentation missing"
fi

# Check for sensitive files
if [ -f "backend/.env" ]; then
    print_status "warning" "Local .env file detected - ensure it's not committed"
fi

if [ -f "backend/db.sqlite3" ]; then
    print_status "info" "SQLite database detected (development)"
fi

# Security check
if grep -q "DEBUG.*True" backend/projectmeats/settings.py 2>/dev/null; then
    print_status "warning" "DEBUG may be enabled - verify production settings"
fi

echo ""
echo "✨ Production Build Verification Complete!"
echo "========================================"

print_status "success" "Repository is ready for production deployment"
print_status "info" "Next steps:"
echo "   1. Review production_checklist.md"
echo "   2. Configure production environment variables"
echo "   3. Set up production database"
echo "   4. Deploy to production server"

exit 0