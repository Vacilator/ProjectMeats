#!/usr/bin/env python3
"""
Verification script to ensure the user is running the updated master_deploy.py
with all PR 71 fixes applied.
"""

import os
import sys
import hashlib
import subprocess

def check_script_version():
    """Check if the master_deploy.py script has the PR 71 fixes"""
    print("🔍 Verifying master_deploy.py Version")
    print("=" * 40)
    
    script_path = "master_deploy.py"
    if not os.path.exists(script_path):
        print("❌ master_deploy.py not found in current directory")
        return False
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Check for specific PR 71 fix signatures
    required_fixes = {
        "PostgreSQL /tmp fix": {
            "signature": "cd /tmp && sudo -u postgres createdb",
            "description": "PostgreSQL commands run from /tmp to avoid permission issues"
        },
        "Directory backup logic": {
            "signature": "backup_choice = input(\"Backup existing files and proceed? [Y/n]: \")",
            "description": "Interactive backup of existing directory content"
        },
        "Download size validation": {
            "signature": "if int(zip_size) < 1000:",
            "description": "Validates download size to detect error responses"
        },
        "File type validation": {
            "signature": "if \"zip\" not in file_result.lower():",
            "description": "Validates downloaded file is actually a zip archive"
        },
        "Tarball fallback": {
            "signature": "tar -xzf project.tar.gz",
            "description": "Alternative tarball download method"
        },
        "Backup directory creation": {
            "signature": "backup_dir = f\"{self.config['project_dir']}_backup_{int(time.time())}\"",
            "description": "Creates timestamped backup directories"
        }
    }
    
    print("Checking for PR 71 fixes:")
    all_present = True
    
    for fix_name, fix_info in required_fixes.items():
        present = fix_info["signature"] in content
        status = "✅" if present else "❌"
        print(f"   {status} {fix_name}")
        print(f"      {fix_info['description']}")
        
        if not present:
            all_present = False
            print(f"      Missing signature: {fix_info['signature']}")
        print()
    
    return all_present

def generate_fix_summary():
    """Generate a summary of what PR 71 fixes"""
    print("📋 PR 71 Fix Summary")
    print("=" * 20)
    print()
    print("The following issues from your error log are addressed:")
    print()
    print("1. PostgreSQL Permission Denied:")
    print("   Error: 'could not change directory to \"/root/ProjectMeats_backup_CLOSE\"'")
    print("   Fix: All PostgreSQL commands now run with 'cd /tmp &&' prefix")
    print("   Code: cd /tmp && sudo -u postgres createdb projectmeats")
    print()
    print("2. Git Clone Directory Conflict:")
    print("   Error: 'destination path already exists and is not an empty directory'")
    print("   Fix: Detect existing content and create backup before git clone")
    print("   Code: Creates backup_TIMESTAMP directories and cleans target")
    print()
    print("3. Download Validation Failures:")
    print("   Error: 'End-of-central-directory signature not found'")
    print("   Fix: Validate download size and file type before extraction")
    print("   Code: Check file size > 1KB and verify with 'file' command")
    print()
    print("4. Additional Robustness:")
    print("   - Added tarball download as fallback method")
    print("   - Better error messages and logging")
    print("   - Graceful handling of edge cases")

def create_deployment_verification():
    """Create a script to verify deployment will work"""
    verification_script = """#!/bin/bash
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
"""
    
    with open("verify_deployment_readiness.sh", 'w') as f:
        f.write(verification_script)
    
    os.chmod("verify_deployment_readiness.sh", 0o755)
    print("📝 Created verify_deployment_readiness.sh")
    print("   Run: sudo ./verify_deployment_readiness.sh")

def main():
    """Main verification function"""
    print("🛠️  ProjectMeats Deployment Fix Verification")
    print("=" * 50)
    print()
    
    # Check if script has the fixes
    script_ok = check_script_version()
    
    print()
    generate_fix_summary()
    
    print()
    create_deployment_verification()
    
    print()
    print("=" * 50)
    
    if script_ok:
        print("✅ Your master_deploy.py has all PR 71 fixes!")
        print()
        print("If deployment is still failing:")
        print("1. Ensure you're using the updated script")
        print("2. Run: sudo ./verify_deployment_readiness.sh")
        print("3. Check that you're running from the correct directory")
        print("4. Verify network connectivity to GitHub")
        print()
        print("The errors in your log should no longer occur with this version.")
    else:
        print("❌ Your master_deploy.py is missing some PR 71 fixes")
        print()
        print("To fix this:")
        print("1. Ensure you're using the latest version from the repository")
        print("2. Check that PR 71 was properly merged")
        print("3. Re-download the master_deploy.py script")
    
    return script_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)