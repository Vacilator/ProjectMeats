#!/bin/bash
# Deployment Verification Script
# Run this before attempting deployment to check if environment is ready

echo "🔍 ProjectMeats Deployment Verification"
echo "======================================="

# Check if we're running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Must run as root (use sudo)"
    exit 1
fi

echo "✅ Running as root"

# Check PostgreSQL
if command -v postgres >/dev/null 2>&1; then
    echo "✅ PostgreSQL available"
else
    echo "❌ PostgreSQL not found"
    exit 1
fi

# Check curl
if command -v curl >/dev/null 2>&1; then
    echo "✅ curl available"
else
    echo "❌ curl not found"
    exit 1
fi

# Check git
if command -v git >/dev/null 2>&1; then
    echo "✅ git available"
else
    echo "❌ git not found"
    exit 1
fi

# Check unzip
if command -v unzip >/dev/null 2>&1; then
    echo "✅ unzip available"
else
    echo "❌ unzip not found"
    exit 1
fi

# Check file command
if command -v file >/dev/null 2>&1; then
    echo "✅ file command available"
else
    echo "❌ file command not found"
    exit 1
fi

# Test /tmp access
if [ -w /tmp ]; then
    echo "✅ /tmp is writable"
else
    echo "❌ /tmp is not writable"
    exit 1
fi

# Test Django log directory access
LOG_DIR="/var/log/projectmeats"
DJANGO_LOG="$LOG_DIR/django.log"

if [ -d "$LOG_DIR" ]; then
    echo "✅ Log directory exists: $LOG_DIR"
    
    # Test if projectmeats user can write to the log file
    if [ -f "$DJANGO_LOG" ] && sudo -u projectmeats test -w "$DJANGO_LOG" 2>/dev/null; then
        echo "✅ Django log file is writable by projectmeats user"
    elif sudo -u projectmeats touch "$DJANGO_LOG" 2>/dev/null; then
        echo "✅ Django log file can be created by projectmeats user"
    else
        echo "❌ Django log file not writable by projectmeats user"
        echo "   Run: sudo ./deployment/scripts/fix_permissions.sh"
        exit 1
    fi
else
    echo "❌ Log directory does not exist: $LOG_DIR"
    echo "   Run: sudo ./deployment/scripts/fix_permissions.sh"
    exit 1
fi

echo ""
echo "🎉 Environment verification passed!"
echo "You can now run: python3 master_deploy.py"
