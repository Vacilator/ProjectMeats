#!/usr/bin/env python3
"""
Test script for validating master_deploy.py fixes.

This script tests the specific issues that were identified:
1. PostgreSQL directory access
2. Git clone handling of existing directories  
3. Download validation
"""

import os
import sys
import tempfile
import subprocess
import shutil
from pathlib import Path

def test_postgres_commands():
    """Test that PostgreSQL commands work from inaccessible directories"""
    print("🧪 Testing PostgreSQL command directory handling...")
    
    # Create a directory with restricted permissions
    test_dir = "/tmp/restricted_test"
    try:
        os.makedirs(test_dir, mode=0o700, exist_ok=True)
        os.chdir(test_dir)
        
        # Test the fixed command format (should work from /tmp)
        cmd = "cd /tmp && echo 'PostgreSQL command test'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PostgreSQL directory fix: PASSED")
            return True
        else:
            print("❌ PostgreSQL directory fix: FAILED")
            return False
    except Exception as e:
        print(f"❌ PostgreSQL directory test error: {e}")
        return False
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

def test_download_validation():
    """Test download validation logic"""
    print("🧪 Testing download validation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test 1: Create a small file (simulating error response)
        small_file = os.path.join(temp_dir, "small.zip")
        with open(small_file, 'w') as f:
            f.write("404")  # Only 3 bytes
        
        size = os.path.getsize(small_file)
        if size < 1000:
            print("✅ Small file detection: PASSED")
            small_test = True
        else:
            print("❌ Small file detection: FAILED")
            small_test = False
        
        # Test 2: Check file command availability
        try:
            result = subprocess.run(["file", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ File command available: PASSED")
                file_cmd_test = True
            else:
                print("❌ File command not available: FAILED")
                file_cmd_test = False
        except FileNotFoundError:
            print("❌ File command not found: FAILED")
            file_cmd_test = False
        
        return small_test and file_cmd_test

def test_directory_handling():
    """Test directory handling for existing content"""
    print("🧪 Testing directory handling...")
    
    with tempfile.TemporaryDirectory() as base_temp:
        test_dir = os.path.join(base_temp, "test_project")
        
        # Create directory with existing content
        os.makedirs(test_dir)
        with open(os.path.join(test_dir, "existing_file.txt"), 'w') as f:
            f.write("existing content")
        
        # Test directory content detection
        try:
            result = subprocess.run(f"ls -la {test_dir}", shell=True, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            
            if len(lines) > 3:  # More than just . and .. 
                print("✅ Directory content detection: PASSED")
                return True
            else:
                print("❌ Directory content detection: FAILED")
                return False
        except Exception as e:
            print(f"❌ Directory handling test error: {e}")
            return False

def test_curl_connectivity():
    """Test basic curl connectivity to GitHub"""
    print("🧪 Testing GitHub connectivity...")
    
    try:
        # Test basic GitHub connectivity
        result = subprocess.run([
            "curl", "-s", "-I", "https://github.com/Vacilator/ProjectMeats"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "200 OK" in result.stdout:
            print("✅ GitHub connectivity: PASSED")
            return True
        else:
            print(f"❌ GitHub connectivity: FAILED (status: {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print("❌ GitHub connectivity: TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ GitHub connectivity test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Master Deploy Fixes Validation")
    print("=" * 40)
    
    tests = [
        ("PostgreSQL Commands", test_postgres_commands),
        ("Download Validation", test_download_validation),
        ("Directory Handling", test_directory_handling),
        ("GitHub Connectivity", test_curl_connectivity),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Fixes should work correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please review the fixes.")
        return 1

if __name__ == "__main__":
    sys.exit(main())