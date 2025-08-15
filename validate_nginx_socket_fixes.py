#!/usr/bin/env python3
"""
Validation script for nginx socket health fixes.
Tests key components that were modified to address deployment issues.
"""

import re
import sys
from pathlib import Path

def test_django_health_endpoints():
    """Test that Django URLs include both health paths"""
    print("🔍 Testing Django health endpoint configuration...")
    
    urls_file = Path("backend/projectmeats/urls.py")
    if not urls_file.exists():
        print("❌ URLs file not found")
        return False
    
    content = urls_file.read_text()
    
    # Check for both health paths
    health_with_slash = 'path("health/"' in content
    health_without_slash = 'path("health"' in content and 'path("health/"' not in content.replace('path("health/"', 'X')
    
    if health_with_slash and health_without_slash:
        print("✅ Both /health and /health/ endpoints configured")
        return True
    elif health_with_slash:
        print("⚠️  Only /health/ endpoint found, missing /health")
        return False
    else:
        print("❌ Health endpoints not found")
        return False

def test_nginx_socket_configuration():
    """Test nginx configurations use socket upstream"""
    print("\n🔍 Testing nginx socket configuration...")
    
    configs = [
        "deployment/templates/meatscentral.conf",
        "deployment/nginx/projectmeats-socket.conf"
    ]
    
    all_good = True
    for config_path in configs:
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"⚠️  Config file not found: {config_path}")
            continue
        
        content = config_file.read_text()
        
        # Check for socket upstream
        has_socket_upstream = "server unix:/run/projectmeats.sock" in content
        has_health_location = "location /health" in content
        has_fallback_health = "@health_fallback" in content
        
        print(f"Testing {config_path}:")
        print(f"  Socket upstream: {'✅' if has_socket_upstream else '❌'}")
        print(f"  Health location: {'✅' if has_health_location else '❌'}")
        print(f"  Health fallback: {'✅' if has_fallback_health else '❌'}")
        
        if not (has_socket_upstream and has_health_location and has_fallback_health):
            all_good = False
    
    return all_good

def test_systemd_socket_permissions():
    """Test systemd socket configuration has proper permissions"""
    print("\n🔍 Testing systemd socket permissions...")
    
    socket_file = Path("deployment/systemd/projectmeats.socket")
    if not socket_file.exists():
        print("❌ Socket configuration file not found")
        return False
    
    content = socket_file.read_text()
    
    has_socket_group = "SocketGroup=www-data" in content
    has_socket_mode = "SocketMode=0660" in content
    
    print(f"  SocketGroup=www-data: {'✅' if has_socket_group else '❌'}")
    print(f"  SocketMode=0660: {'✅' if has_socket_mode else '❌'}")
    
    return has_socket_group and has_socket_mode

def test_port_checking_modernization():
    """Test that scripts use ss instead of netstat where appropriate"""
    print("\n🔍 Testing port checking modernization...")
    
    files_to_check = [
        "ai_deployment_orchestrator.py",
        "production_deploy.sh"
    ]
    
    all_good = True
    for file_path in files_to_check:
        file_obj = Path(file_path)
        if not file_obj.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        content = file_obj.read_text()
        
        # Count occurrences
        ss_port80_count = len(re.findall(r'ss.*:80', content))
        netstat_port80_count = len(re.findall(r'netstat.*:80', content))
        
        print(f"Testing {file_path}:")
        print(f"  ss commands for port 80: {ss_port80_count}")
        print(f"  netstat commands for port 80: {netstat_port80_count}")
        
        if file_path == "ai_deployment_orchestrator.py":
            # Should have ss, not netstat for port 80
            if ss_port80_count > 0 and netstat_port80_count == 0:
                print("  ✅ Properly modernized to ss")
            else:
                print("  ❌ Still using netstat or missing ss")
                all_good = False
        elif file_path == "production_deploy.sh":
            # Should primarily use ss, netstat only as fallback
            if ss_port80_count >= netstat_port80_count:
                print("  ✅ Primarily uses ss with netstat fallback")
            else:
                print("  ❌ Too much netstat usage")
                all_good = False
    
    return all_good

def test_deployment_script_socket_fixes():
    """Test that deployment scripts handle socket permissions"""
    print("\n🔍 Testing deployment socket permission fixes...")
    
    script_file = Path("production_deploy.sh")
    if not script_file.exists():
        print("❌ production_deploy.sh not found")
        return False
    
    content = script_file.read_text()
    
    has_chown = "chown projectmeats:www-data /run/projectmeats.sock" in content
    has_chmod = "chmod 660 /run/projectmeats.sock" in content
    
    print(f"  Socket chown command: {'✅' if has_chown else '❌'}")
    print(f"  Socket chmod command: {'✅' if has_chmod else '❌'}")
    
    return has_chown and has_chmod

def main():
    """Run all validation tests"""
    print("🧪 ProjectMeats Nginx Socket Health Fix Validation")
    print("=" * 50)
    
    tests = [
        ("Django Health Endpoints", test_django_health_endpoints),
        ("Nginx Socket Configuration", test_nginx_socket_configuration),
        ("SystemD Socket Permissions", test_systemd_socket_permissions),
        ("Port Checking Modernization", test_port_checking_modernization),
        ("Deployment Socket Fixes", test_deployment_script_socket_fixes),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n📊 Validation Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All validation tests passed! Fixes are ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())