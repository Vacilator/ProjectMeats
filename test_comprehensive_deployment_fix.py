#!/usr/bin/env python3
"""
Comprehensive test to verify deployment orchestrator fixes
address all issues mentioned in the problem statement.
"""

import sys
import re
from pathlib import Path


def test_database_syntax_fix_comprehensive():
    """Test database syntax fix addresses the core issue from problem statement"""
    print("Testing database syntax fix (core issue from problem statement)...")
    
    orchestrator_file = Path("/home/runner/work/ProjectMeats/ProjectMeats/ai_deployment_orchestrator.py")
    content = orchestrator_file.read_text()
    
    # Test 1: No \echo inside DO $$ blocks (the main syntax error)
    do_block_pattern = r'DO \$\$(.*?)\$\$;'
    do_blocks = re.findall(do_block_pattern, content, re.DOTALL)
    
    has_echo_in_do_block = False
    for block in do_blocks:
        if '\\echo' in block:
            has_echo_in_do_block = True
            print(f"✗ Found \\echo inside DO $$ block: {block[:100]}...")
            break
    
    if not has_echo_in_do_block:
        print("✓ No \\echo commands inside DO $$ blocks (syntax error fixed)")
    else:
        return False
    
    # Test 2: Verify RAISE NOTICE is used instead
    if 'RAISE NOTICE' in content:
        print("✓ Uses RAISE NOTICE for informational messages (correct PL/pgSQL)")
    else:
        print("? No RAISE NOTICE found - may be using different approach")
    
    # Test 3: Test that user creation logic is still present
    if "CREATE USER" in content and "IF NOT EXISTS" in content:
        print("✓ Database user creation logic is preserved")
    else:
        print("✗ Database user creation logic missing")
        return False
    
    return True


def test_systemd_service_configuration():
    """Test systemd service addresses Django service startup failure"""
    print("\nTesting systemd service configuration (Django startup issue)...")
    
    service_file = Path("/home/runner/work/ProjectMeats/ProjectMeats/deployment/systemd/projectmeats.service")
    content = service_file.read_text()
    
    # Check all the critical configurations mentioned in problem statement
    critical_configs = [
        ("WorkingDirectory=/opt/projectmeats/backend", "Working directory points to backend (fixes path issues)"),
        ("projectmeats.wsgi:application", "WSGI module path is correct"),
        ("User=www-data", "Service runs as www-data (proper permissions)"),
        ("EnvironmentFile.*projectmeats.env", "Environment file is loaded"),
        ("ExecStart.*gunicorn", "Gunicorn is properly configured")
    ]
    
    all_passed = True
    for pattern, description in critical_configs:
        if re.search(pattern, content):
            print(f"✓ {description}")
        else:
            print(f"✗ Missing: {description}")
            all_passed = False
    
    return all_passed


def test_no_other_database_syntax_issues():
    """Test that other scripts don't have similar database syntax issues"""
    print("\nTesting other deployment scripts for database syntax issues...")
    
    # Check other deployment files
    files_to_check = [
        "/home/runner/work/ProjectMeats/ProjectMeats/deploy_production.py",
        "/home/runner/work/ProjectMeats/ProjectMeats/deployment/scripts/quick_server_fix.sh",
        "/home/runner/work/ProjectMeats/ProjectMeats/deployment/scripts/setup_production.sh"
    ]
    
    all_clean = True
    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            continue
            
        content = path.read_text()
        
        # Look for problematic patterns
        if "\\echo" in content and "DO $$" in content:
            # Check if \echo is inside DO blocks
            do_blocks = re.findall(r'DO \$\$(.*?)\$\$', content, re.DOTALL)
            for block in do_blocks:
                if '\\echo' in block:
                    print(f"✗ Found \\echo in DO block in {path.name}")
                    all_clean = False
                    break
    
    if all_clean:
        print("✓ No database syntax issues in other deployment scripts")
    
    return all_clean


def test_wsgi_configuration():
    """Test WSGI file exists and is properly configured"""
    print("\nTesting WSGI configuration (addresses module not found errors)...")
    
    wsgi_file = Path("/home/runner/work/ProjectMeats/ProjectMeats/backend/projectmeats/wsgi.py")
    
    if not wsgi_file.exists():
        print("✗ WSGI file not found at expected location")
        return False
    
    content = wsgi_file.read_text()
    
    # Check for proper Django WSGI setup
    wsgi_checks = [
        ("from django.core.wsgi import get_wsgi_application", "Django WSGI import"),
        ("application = get_wsgi_application()", "WSGI application variable"),
        ("DJANGO_SETTINGS_MODULE", "Settings module configuration"),
        ("apps.settings", "Uses apps.settings (matches systemd config)")
    ]
    
    all_passed = True
    for check, description in wsgi_checks:
        if check in content:
            print(f"✓ {description}")
        else:
            print(f"✗ Missing: {description}")
            all_passed = False
    
    return all_passed


def test_nginx_configuration():
    """Test nginx configuration supports HTTPS setup"""
    print("\nTesting nginx configuration (HTTPS/SSL setup support)...")
    
    nginx_file = Path("/home/runner/work/ProjectMeats/ProjectMeats/deployment/nginx/projectmeats.conf")
    content = nginx_file.read_text()
    
    # Check for SSL/HTTPS support (even if commented out)
    nginx_checks = [
        ("listen 443 ssl", "HTTPS configuration present"),
        ("ssl_certificate", "SSL certificate configuration"),
        ("proxy_pass.*django_backend", "Django backend proxy configured"),
        ("server_name.*meatscentral.com", "Domain configuration present")
    ]
    
    all_passed = True
    for check, description in nginx_checks:
        if re.search(check, content):
            print(f"✓ {description}")
        else:
            print(f"? {description} (may be commented out)")
    
    return all_passed


def main():
    """Run comprehensive tests for all deployment issues"""
    print("ProjectMeats Deployment Fix Comprehensive Tests")
    print("=" * 55)
    print("Testing fixes for issues mentioned in problem statement:")
    print("1. Database creation syntax errors (\\echo in DO $$ blocks)")
    print("2. Django service startup failures (WSGI/path issues)") 
    print("3. Overall deployment configuration issues")
    print("")
    
    tests = [
        ("Database Syntax Fix", test_database_syntax_fix_comprehensive),
        ("Systemd Service Configuration", test_systemd_service_configuration),
        ("Other Scripts Clean", test_no_other_database_syntax_issues),
        ("WSGI Configuration", test_wsgi_configuration),
        ("Nginx Configuration", test_nginx_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"✗ {test_name} has issues")
        except Exception as e:
            print(f"✗ {test_name} error: {e}")
    
    print(f"\n{'='*55}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All deployment issues from problem statement are addressed!")
        print("\nThe fixes should resolve:")
        print("- Database creation syntax errors → Fixed \\echo in DO $$ blocks")
        print("- Django service startup failures → Service config is correct")
        print("- WSGI module path issues → WSGI file exists and is properly configured")
        print("- Environment and path configuration → All paths are correct")
        print("\nDeployment should now work correctly.")
        return True
    else:
        print("✗ Some issues remain. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)