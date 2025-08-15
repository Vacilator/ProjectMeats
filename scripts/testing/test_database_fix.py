#!/usr/bin/env python3
"""
Test script to verify database syntax fix in deployment orchestrator
"""

import sys
from pathlib import Path

def test_database_syntax_fix():
    """Test that the database setup script no longer has the \\echo syntax error"""
    print("Testing database syntax fix...")
    
    orchestrator_file = Path("/home/runner/work/ProjectMeats/ProjectMeats/ai_deployment_orchestrator.py")
    
    if not orchestrator_file.exists():
        print("✗ AI deployment orchestrator file not found")
        return False
    
    content = orchestrator_file.read_text()
    
    # Check that the problematic \\echo commands have been removed from DO $$ blocks
    if "\\echo" in content and "DO $$" in content:
        # Look for the problematic pattern more specifically
        lines = content.split('\n')
        in_do_block = False
        line_num = 0
        
        for line in lines:
            line_num += 1
            if "DO $$" in line:
                in_do_block = True
            elif "$$;" in line and in_do_block:
                in_do_block = False
            elif "\\echo" in line and in_do_block:
                print(f"✗ Found \\echo inside DO $$ block at line {line_num}")
                print(f"  Line: {line.strip()}")
                return False
    
    # Check that RAISE NOTICE is used instead
    if "RAISE NOTICE" in content:
        print("✓ Uses RAISE NOTICE instead of \\echo in PL/pgSQL blocks")
    else:
        print("? No RAISE NOTICE found - may not be using PL/pgSQL blocks")
    
    print("✓ Database syntax fix is correct")
    return True

def test_systemd_service_config():
    """Test systemd service configuration"""
    print("Testing systemd service configuration...")
    
    service_file = Path("/home/runner/work/ProjectMeats/ProjectMeats/deployment/systemd/projectmeats.service")
    
    if not service_file.exists():
        print("✗ Systemd service file not found")
        return False
    
    content = service_file.read_text()
    
    # Essential configuration checks
    required_configs = [
        ("WorkingDirectory=/opt/projectmeats/backend", "Working directory set to backend"),
        ("projectmeats.wsgi:application", "WSGI module path is correct"),
        ("User=www-data", "Service runs as www-data"),
        ("Group=www-data", "Service group is www-data")
    ]
    
    all_passed = True
    for config, description in required_configs:
        if config in content:
            print(f"✓ {description}")
        else:
            print(f"✗ Missing: {description}")
            all_passed = False
    
    return all_passed

def main():
    """Run the tests"""
    print("ProjectMeats Deployment Orchestrator Fix Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    if test_database_syntax_fix():
        tests_passed += 1
    
    if test_systemd_service_config():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ All fixes are correctly implemented!")
        return True
    else:
        print("✗ Some fixes need attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)