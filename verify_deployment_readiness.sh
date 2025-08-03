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

echo ""
echo "🎉 Environment verification passed!"
echo "You can now run: python3 master_deploy.py"
