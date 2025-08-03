#!/usr/bin/env python3
"""
ProjectMeats Windows Deployment Testing Script
==============================================

This script tests the Windows deployment functionality of ProjectMeats
to ensure it works correctly for Windows users deploying to production.

It simulates Windows-specific scenarios and validates deployment scripts.
"""

import os
import sys
import subprocess
import platform
import tempfile
import shutil
from pathlib import Path
import json


class TestColors:
    """Colors for test output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_test_header(title):
    """Print test section header"""
    print(f"\n{TestColors.CYAN}{TestColors.BOLD}{'='*60}{TestColors.END}")
    print(f"{TestColors.CYAN}{TestColors.BOLD} {title}{TestColors.END}")
    print(f"{TestColors.CYAN}{TestColors.BOLD}{'='*60}{TestColors.END}")


def print_test_result(test_name, passed, details=""):
    """Print test result"""
    status = f"{TestColors.GREEN}✅ PASS" if passed else f"{TestColors.RED}❌ FAIL"
    print(f"{status}{TestColors.END} {test_name}")
    if details:
        print(f"    {TestColors.YELLOW}{details}{TestColors.END}")


def run_command_test(command, expected_success=True, timeout=30):
    """Run a command and test if it succeeds as expected"""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        success = result.returncode == 0
        return success == expected_success, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def test_unified_deployment_tool():
    """Test the unified deployment tool"""
    print_test_header("Testing Unified Deployment Tool")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Basic help command
    total_tests += 1
    passed, stdout, stderr = run_command_test("python3 unified_deployment_tool.py --help")
    print_test_result("Help command works", passed)
    if passed:
        tests_passed += 1
    
    # Test 2: Diagnose command
    total_tests += 1
    passed, stdout, stderr = run_command_test("python3 unified_deployment_tool.py --diagnose")
    print_test_result("Diagnose command works", passed)
    if passed:
        tests_passed += 1
    
    # Test 3: Status command
    total_tests += 1
    passed, stdout, stderr = run_command_test("python3 unified_deployment_tool.py --status")
    # Status might fail due to no deployment, but command should work
    command_worked = "Issues found" in stdout or "Systems appear healthy" in stdout
    print_test_result("Status command works", command_worked)
    if command_worked:
        tests_passed += 1
    
    # Test 4: Check for Windows compatibility code
    total_tests += 1
    try:
        with open("unified_deployment_tool.py", "r") as f:
            content = f.read()
            has_windows_code = "platform.system()" in content and "Windows" in content
        print_test_result("Contains Windows compatibility code", has_windows_code)
        if has_windows_code:
            tests_passed += 1
    except:
        print_test_result("Contains Windows compatibility code", False)
    
    return tests_passed, total_tests


def test_windows_deployment_scripts():
    """Test Windows-specific deployment scripts"""
    print_test_header("Testing Windows Deployment Scripts")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: PowerShell script exists
    total_tests += 1
    ps_script_exists = Path("deploy_windows_production.ps1").exists()
    print_test_result("PowerShell deployment script exists", ps_script_exists)
    if ps_script_exists:
        tests_passed += 1
    
    # Test 2: Batch launcher exists
    total_tests += 1
    bat_script_exists = Path("setup_windows_production.bat").exists()
    print_test_result("Batch launcher script exists", bat_script_exists)
    if bat_script_exists:
        tests_passed += 1
    
    # Test 3: Windows validation script exists
    total_tests += 1
    validation_script_exists = Path("validate_windows_production.py").exists()
    print_test_result("Windows validation script exists", validation_script_exists)
    if validation_script_exists:
        tests_passed += 1
    
    # Test 4: Test PowerShell script syntax (basic check)
    if ps_script_exists:
        total_tests += 1
        try:
            with open("deploy_windows_production.ps1", "r") as f:
                ps_content = f.read()
                # Check for key PowerShell elements
                has_params = "param(" in ps_content
                has_functions = "function " in ps_content
                has_chocolatey = "choco" in ps_content
                syntax_ok = has_params and has_functions and has_chocolatey
            print_test_result("PowerShell script has proper structure", syntax_ok)
            if syntax_ok:
                tests_passed += 1
        except:
            print_test_result("PowerShell script has proper structure", False)
    
    # Test 5: Test Windows validation script
    if validation_script_exists:
        total_tests += 1
        passed, stdout, stderr = run_command_test("python3 validate_windows_production.py")
        # Should fail because we're not on Windows, but script should execute
        script_works = "designed for Windows systems" in stderr or "Windows systems" in stdout
        print_test_result("Windows validation script executes", script_works)
        if script_works:
            tests_passed += 1
    
    return tests_passed, total_tests


def test_documentation():
    """Test Windows deployment documentation"""
    print_test_header("Testing Windows Documentation")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Windows deployment guide exists
    total_tests += 1
    windows_guide_exists = Path("docs/windows_production_deployment.md").exists()
    print_test_result("Windows deployment guide exists", windows_guide_exists)
    if windows_guide_exists:
        tests_passed += 1
    
    # Test 2: Main production deployment guide exists
    total_tests += 1
    prod_guide_exists = Path("docs/production_deployment.md").exists()
    print_test_result("Main production deployment guide exists", prod_guide_exists)
    if prod_guide_exists:
        tests_passed += 1
    
    # Test 3: Check Windows guide content
    if windows_guide_exists:
        total_tests += 1
        try:
            with open("docs/windows_production_deployment.md", "r") as f:
                content = f.read()
                has_powershell = "PowerShell" in content
                has_chocolatey = "Chocolatey" in content
                has_windows_paths = "C:\\" in content
                has_services = "Windows Services" in content
                content_complete = has_powershell and has_chocolatey and has_windows_paths and has_services
            print_test_result("Windows guide has comprehensive content", content_complete)
            if content_complete:
                tests_passed += 1
        except:
            print_test_result("Windows guide has comprehensive content", False)
    
    # Test 4: Check main guide references Windows
    if prod_guide_exists:
        total_tests += 1
        try:
            with open("docs/production_deployment.md", "r") as f:
                content = f.read()
                mentions_windows = "Windows" in content
                has_powershell_ref = "powershell" in content.lower()
                cross_platform = mentions_windows and has_powershell_ref
            print_test_result("Main guide includes Windows instructions", cross_platform)
            if cross_platform:
                tests_passed += 1
        except:
            print_test_result("Main guide includes Windows instructions", False)
    
    return tests_passed, total_tests


def test_cross_platform_compatibility():
    """Test cross-platform compatibility features"""
    print_test_header("Testing Cross-Platform Compatibility")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Setup script platform detection
    total_tests += 1
    try:
        with open("setup.py", "r") as f:
            setup_content = f.read()
            has_platform_detection = "platform.system()" in setup_content
        print_test_result("Setup script has platform detection", has_platform_detection)
        if has_platform_detection:
            tests_passed += 1
    except:
        print_test_result("Setup script has platform detection", False)
    
    # Test 2: Unified tool platform compatibility
    total_tests += 1
    try:
        with open("unified_deployment_tool.py", "r") as f:
            unified_content = f.read()
            has_windows_paths = '"C:\\\\' in unified_content or "'C:\\\\" in unified_content
            has_linux_paths = '"/opt/' in unified_content or "'/opt/" in unified_content
            cross_platform = has_windows_paths and has_linux_paths
        print_test_result("Unified tool supports both platforms", cross_platform)
        if cross_platform:
            tests_passed += 1
    except:
        print_test_result("Unified tool supports both platforms", False)
    
    # Test 3: Path handling compatibility
    total_tests += 1
    try:
        with open("unified_deployment_tool.py", "r") as f:
            content = f.read()
            uses_pathlib = "from pathlib import Path" in content
            platform_specific_paths = "platform.system()" in content and "Windows" in content
            proper_paths = uses_pathlib and platform_specific_paths
        print_test_result("Proper cross-platform path handling", proper_paths)
        if proper_paths:
            tests_passed += 1
    except:
        print_test_result("Proper cross-platform path handling", False)
    
    # Test 4: Service management compatibility
    total_tests += 1
    try:
        with open("unified_deployment_tool.py", "r") as f:
            content = f.read()
            has_systemctl = "systemctl" in content
            has_sc_query = "sc query" in content or '"sc"' in content
            service_compatibility = has_systemctl and has_sc_query
        print_test_result("Cross-platform service management", service_compatibility)
        if service_compatibility:
            tests_passed += 1
    except:
        print_test_result("Cross-platform service management", False)
    
    return tests_passed, total_tests


def test_production_readiness():
    """Test overall production readiness"""
    print_test_header("Testing Production Readiness")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Production validation script
    total_tests += 1
    passed, stdout, stderr = run_command_test("python3 validate_production.py")
    print_test_result("Production validation passes", passed)
    if passed:
        tests_passed += 1
    
    # Test 2: Backend tests
    total_tests += 1
    passed, stdout, stderr = run_command_test("cd backend && python3 manage.py test --keepdb -v 0", timeout=120)
    print_test_result("Backend tests pass", passed)
    if passed:
        tests_passed += 1
    
    # Test 3: Frontend build
    total_tests += 1
    passed, stdout, stderr = run_command_test("cd frontend && npm run build", timeout=180)
    print_test_result("Frontend builds successfully", passed)
    if passed:
        tests_passed += 1
    
    # Test 4: Required files exist
    total_tests += 1
    required_files = [
        "README.md",
        "production_checklist.md",
        "unified_deployment_tool.py",
        "backend/requirements.txt",
        "frontend/package.json"
    ]
    all_files_exist = all(Path(f).exists() for f in required_files)
    print_test_result("All required files exist", all_files_exist)
    if all_files_exist:
        tests_passed += 1
    
    return tests_passed, total_tests


def test_deployment_scripts_integration():
    """Test integration between different deployment scripts"""
    print_test_header("Testing Deployment Scripts Integration")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Unified tool can handle Windows scripts
    total_tests += 1
    try:
        with open("unified_deployment_tool.py", "r") as f:
            content = f.read()
            handles_powershell = ".ps1" in content
            handles_batch = ".bat" in content
            windows_integration = handles_powershell and handles_batch
        print_test_result("Unified tool integrates Windows scripts", windows_integration)
        if windows_integration:
            tests_passed += 1
    except:
        print_test_result("Unified tool integrates Windows scripts", False)
    
    # Test 2: Consistent configuration across platforms
    total_tests += 1
    try:
        # Check if Windows and Linux scripts use similar configuration
        linux_config_exists = Path("one_click_deploy.sh").exists()
        windows_config_exists = Path("deploy_windows_production.ps1").exists()
        both_exist = linux_config_exists and windows_config_exists
        print_test_result("Both platform deployment scripts exist", both_exist)
        if both_exist:
            tests_passed += 1
    except:
        print_test_result("Both platform deployment scripts exist", False)
    
    # Test 3: Environment variable compatibility
    total_tests += 1
    try:
        with open("unified_deployment_tool.py", "r") as f:
            content = f.read()
            sets_env_vars = "env[" in content and "DOMAIN" in content
            cross_platform_env = sets_env_vars
        print_test_result("Cross-platform environment variable handling", cross_platform_env)
        if cross_platform_env:
            tests_passed += 1
    except:
        print_test_result("Cross-platform environment variable handling", False)
    
    return tests_passed, total_tests


def main():
    """Run all tests"""
    print(f"{TestColors.BOLD}{TestColors.BLUE}")
    print("🧪 ProjectMeats Windows Deployment Testing Suite")
    print("=" * 60)
    print(f"{TestColors.END}")
    
    all_tests_passed = 0
    all_total_tests = 0
    
    # Run test suites
    test_suites = [
        ("Unified Deployment Tool", test_unified_deployment_tool),
        ("Windows Deployment Scripts", test_windows_deployment_scripts),
        ("Documentation", test_documentation),
        ("Cross-Platform Compatibility", test_cross_platform_compatibility),
        ("Production Readiness", test_production_readiness),
        ("Deployment Scripts Integration", test_deployment_scripts_integration),
    ]
    
    suite_results = []
    
    for suite_name, test_function in test_suites:
        try:
            passed, total = test_function()
            all_tests_passed += passed
            all_total_tests += total
            suite_results.append((suite_name, passed, total))
        except Exception as e:
            print(f"{TestColors.RED}❌ Test suite '{suite_name}' failed with error: {e}{TestColors.END}")
            suite_results.append((suite_name, 0, 1))
            all_total_tests += 1
    
    # Print final results
    print_test_header("🔍 Final Test Results")
    
    for suite_name, passed, total in suite_results:
        percentage = (passed / total * 100) if total > 0 else 0
        color = TestColors.GREEN if passed == total else TestColors.YELLOW if passed > 0 else TestColors.RED
        print(f"{color}{suite_name}: {passed}/{total} ({percentage:.1f}%){TestColors.END}")
    
    overall_percentage = (all_tests_passed / all_total_tests * 100) if all_total_tests > 0 else 0
    
    print(f"\n{TestColors.BOLD}Overall Results:{TestColors.END}")
    print(f"Tests Passed: {all_tests_passed}/{all_total_tests} ({overall_percentage:.1f}%)")
    
    if all_tests_passed == all_total_tests:
        print(f"\n{TestColors.GREEN}{TestColors.BOLD}🎉 All tests passed! Windows deployment is ready.{TestColors.END}")
        exit_code = 0
    elif overall_percentage >= 80:
        print(f"\n{TestColors.YELLOW}{TestColors.BOLD}⚠️ Most tests passed. Minor issues to address.{TestColors.END}")
        exit_code = 0
    else:
        print(f"\n{TestColors.RED}{TestColors.BOLD}❌ Significant issues found. Windows deployment needs work.{TestColors.END}")
        exit_code = 1
    
    print(f"\n{TestColors.CYAN}Windows deployment testing complete!{TestColors.END}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()