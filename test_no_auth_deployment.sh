#!/bin/bash
# Test script for no-authentication deployment
# This tests the download functionality without requiring root access

set -e

echo "🧪 Testing ProjectMeats No-Auth Deployment Download Methods"
echo "==========================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

TEMP_DIR="/tmp/projectmeats_test_$(date +%s)"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

echo "📂 Test directory: $TEMP_DIR"
echo ""

# Test 1: GitHub API release download
echo "🧪 Test 1: GitHub Release API"
if curl -L -o "release_info.json" "https://api.github.com/repos/Vacilator/ProjectMeats/releases/latest" 2>/dev/null; then
    if python3 -c "
import json
try:
    with open('release_info.json', 'r') as f:
        data = json.load(f)
    print('✅ Release API accessible')
    print('📦 Latest release:', data.get('tag_name', 'No tag'))
    print('🌐 Download URL:', data.get('zipball_url', 'No URL'))
except Exception as e:
    print('❌ Release API failed:', e)
"; then
        echo -e "${GREEN}✅ Test 1 PASSED${NC}"
    else
        echo -e "${RED}❌ Test 1 FAILED${NC}"
    fi
else
    echo -e "${RED}❌ Test 1 FAILED - API not accessible${NC}"
fi
echo ""

# Test 2: Direct tarball download
echo "🧪 Test 2: Direct Tarball Download"
if curl -L -o "projectmeats.tar.gz" "https://github.com/Vacilator/ProjectMeats/archive/refs/heads/main.tar.gz" 2>/dev/null; then
    if tar -tzf projectmeats.tar.gz | head -5 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Test 2 PASSED - Tarball downloaded and is valid${NC}"
        echo "📦 Tarball size: $(du -h projectmeats.tar.gz | cut -f1)"
    else
        echo -e "${RED}❌ Test 2 FAILED - Invalid tarball${NC}"
    fi
else
    echo -e "${RED}❌ Test 2 FAILED - Download failed${NC}"
fi
echo ""

# Test 3: Individual file download
echo "🧪 Test 3: Individual File Download"
base_url="https://raw.githubusercontent.com/Vacilator/ProjectMeats/main"
test_files=(
    "README.md"
    "deploy_production.py"
    "docs/deployment_authentication_guide.md"
    "backend/requirements.txt"
)

success_count=0
for file in "${test_files[@]}"; do
    if curl -L -o "test_$success_count.txt" "$base_url/$file" 2>/dev/null; then
        if [ -s "test_$success_count.txt" ]; then
            ((success_count++))
        fi
    fi
done

if [ $success_count -eq ${#test_files[@]} ]; then
    echo -e "${GREEN}✅ Test 3 PASSED - All $success_count files downloaded${NC}"
else
    echo -e "${YELLOW}⚠️  Test 3 PARTIAL - $success_count/${#test_files[@]} files downloaded${NC}"
fi
echo ""

# Test 4: Command availability
echo "🧪 Test 4: Required Commands"
commands=("curl" "tar" "python3" "unzip")
available_commands=0

for cmd in "${commands[@]}"; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "✅ $cmd available"
        ((available_commands++))
    else
        echo "❌ $cmd not available"
    fi
done

if [ $available_commands -eq ${#commands[@]} ]; then
    echo -e "${GREEN}✅ Test 4 PASSED - All required commands available${NC}"
else
    echo -e "${YELLOW}⚠️  Test 4 PARTIAL - $available_commands/${#commands[@]} commands available${NC}"
fi
echo ""

# Summary
echo "📊 Test Summary"
echo "==============="
echo "• GitHub Release API: $([ -f release_info.json ] && echo "✅" || echo "❌")"
echo "• Direct Tarball Download: $([ -f projectmeats.tar.gz ] && echo "✅" || echo "❌")"
echo "• Individual File Downloads: $success_count/${#test_files[@]} files"
echo "• Required Commands: $available_commands/${#commands[@]} available"
echo ""

if [ -f projectmeats.tar.gz ] && [ $success_count -gt 2 ]; then
    echo -e "${GREEN}🎉 OVERALL: Authentication-free deployment should work!${NC}"
    exit_code=0
else
    echo -e "${YELLOW}⚠️  OVERALL: Some issues detected, manual steps may be needed${NC}"
    exit_code=1
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"
echo "🧹 Cleaned up test files"

exit $exit_code