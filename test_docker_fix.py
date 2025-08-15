#!/usr/bin/env python3
"""
Test script to validate the Docker installation fix
"""

import re
import sys
import subprocess

def test_docker_command_fix():
    """Test that the Docker repository command is properly formatted"""
    print("Testing Docker installation fix...")
    
    # Test the problematic pattern - this should NOT be present anymore
    with open('ai_deployment_orchestrator.py', 'r') as f:
        orchestrator_content = f.read()
    
    # Check for the problematic pattern
    problematic_pattern = r'\$\(lsb_release -cs\)'
    if re.search(problematic_pattern, orchestrator_content):
        print("❌ FAIL: Found problematic $(lsb_release -cs) pattern in ai_deployment_orchestrator.py")
        return False
    else:
        print("✅ PASS: No problematic $(lsb_release -cs) pattern found in ai_deployment_orchestrator.py")
    
    # Check for the fixed pattern
    fixed_pattern = r'ubuntu_codename = codename_output\.strip\(\)'
    if re.search(fixed_pattern, orchestrator_content):
        print("✅ PASS: Found proper Ubuntu codename handling in ai_deployment_orchestrator.py")
    else:
        print("❌ FAIL: Fixed pattern not found in ai_deployment_orchestrator.py")
        return False
    
    # Test legacy script
    with open('legacy-deployment/master_deploy.py', 'r') as f:
        legacy_content = f.read()
    
    if re.search(problematic_pattern, legacy_content):
        print("❌ FAIL: Found problematic $(lsb_release -cs) pattern in legacy master_deploy.py")
        return False
    else:
        print("✅ PASS: No problematic $(lsb_release -cs) pattern found in legacy master_deploy.py")
    
    # Check for the fixed pattern in legacy
    legacy_fixed_pattern = r'ubuntu_codename = self\.run_command\("lsb_release -cs", capture_output=True\)'
    if re.search(legacy_fixed_pattern, legacy_content):
        print("✅ PASS: Found proper Ubuntu codename handling in legacy master_deploy.py")
    else:
        print("❌ FAIL: Fixed pattern not found in legacy master_deploy.py")
        return False
    
    print("\n🎉 All tests passed! Docker installation fix appears to be working correctly.")
    return True

def test_syntax_validation():
    """Test that Python syntax is still valid after the changes"""
    print("\nTesting Python syntax validation...")
    
    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', 'ai_deployment_orchestrator.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PASS: ai_deployment_orchestrator.py syntax is valid")
        else:
            print(f"❌ FAIL: ai_deployment_orchestrator.py syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Could not validate ai_deployment_orchestrator.py: {e}")
        return False
    
    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', 'legacy-deployment/master_deploy.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PASS: legacy-deployment/master_deploy.py syntax is valid")
        else:
            print(f"❌ FAIL: legacy-deployment/master_deploy.py syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Could not validate legacy-deployment/master_deploy.py: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Docker Installation Fix Validation")
    print("=" * 50)
    
    success = test_docker_command_fix() and test_syntax_validation()
    
    if success:
        print("\n✅ SUCCESS: All validations passed!")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Some validations failed!")
        sys.exit(1)