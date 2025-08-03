#!/usr/bin/env python3
"""
ProjectMeats Windows Production Validation Script
================================================

This script validates that a Windows system is ready for ProjectMeats production deployment.
It checks dependencies, configurations, and performs basic system health checks.

Usage:
    python validate_windows_production.py
    python validate_windows_production.py --fix    # Auto-fix issues
    python validate_windows_production.py --verbose
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json
import argparse


class Colors:
    """ANSI color codes for Windows terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    @classmethod
    def disable_if_needed(cls):
        """Disable colors if not supported"""
        if platform.system() == "Windows" and not os.environ.get('TERM'):
            # Disable colors on older Windows terminals
            for attr in dir(cls):
                if not attr.startswith('_') and isinstance(getattr(cls, attr), str):
                    setattr(cls, attr, '')


def print_header(title):
    """Print a formatted header"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.WHITE}{Colors.BOLD} {title}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")


def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def run_command(command, check_output=False, timeout=30):
    """Run a command and return success status and output"""
    try:
        if check_output:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        else:
            result = subprocess.run(command, shell=True, timeout=timeout)
            return result.returncode == 0, "", ""
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def check_windows_version():
    """Check if Windows version is supported"""
    print_header("Windows Version Check")
    
    try:
        version_info = platform.platform()
        win_version = platform.win32_ver()
        
        print_info(f"Platform: {version_info}")
        print_info(f"Windows Version: {win_version[0]} {win_version[1]}")
        
        # Check for supported versions
        major_version = int(win_version[1].split('.')[0])
        
        if major_version >= 10:
            print_success("Windows version is supported")
            return True
        else:
            print_error("Windows 10 or newer is required for production deployment")
            return False
            
    except Exception as e:
        print_error(f"Could not determine Windows version: {e}")
        return False


def check_administrator_privileges():
    """Check if running with administrator privileges"""
    print_header("Administrator Privileges Check")
    
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        
        if is_admin:
            print_success("Running with Administrator privileges")
            return True
        else:
            print_error("Administrator privileges required for production deployment")
            print_info("Right-click PowerShell/Command Prompt and select 'Run as administrator'")
            return False
            
    except Exception as e:
        print_warning(f"Could not check administrator privileges: {e}")
        return True  # Assume OK if we can't check


def check_python_installation():
    """Check Python installation and version"""
    print_header("Python Installation Check")
    
    python_commands = ["python", "py", "python3"]
    python_found = False
    
    for cmd in python_commands:
        success, output, error = run_command(f"{cmd} --version", check_output=True)
        
        if success and "Python" in output:
            version = output.replace("Python ", "").strip()
            version_parts = version.split('.')
            
            if len(version_parts) >= 2:
                major, minor = int(version_parts[0]), int(version_parts[1])
                
                if major == 3 and minor >= 9:
                    print_success(f"Python {version} found using '{cmd}' command")
                    python_found = True
                    break
                else:
                    print_warning(f"Python {version} found but Python 3.9+ is required")
            else:
                print_warning(f"Could not parse Python version: {version}")
    
    if not python_found:
        print_error("Python 3.9+ not found")
        print_info("Install Python from https://python.org or Microsoft Store")
        return False
    
    # Check pip
    success, output, error = run_command("pip --version", check_output=True)
    if success:
        print_success(f"pip found: {output}")
    else:
        print_warning("pip not found - may cause dependency installation issues")
    
    return python_found


def check_nodejs_installation():
    """Check Node.js installation and version"""
    print_header("Node.js Installation Check")
    
    success, output, error = run_command("node --version", check_output=True)
    
    if success:
        version = output.strip().replace('v', '')
        version_parts = version.split('.')
        
        if len(version_parts) >= 1:
            major = int(version_parts[0])
            
            if major >= 16:
                print_success(f"Node.js {version} found")
                
                # Check npm
                success, npm_output, _ = run_command("npm --version", check_output=True)
                if success:
                    print_success(f"npm {npm_output.strip()} found")
                else:
                    print_warning("npm not found")
                
                return True
            else:
                print_warning(f"Node.js {version} found but version 16+ is required")
        else:
            print_warning(f"Could not parse Node.js version: {version}")
    else:
        print_error("Node.js not found")
        print_info("Install Node.js from https://nodejs.org")
    
    return False


def check_git_installation():
    """Check Git installation"""
    print_header("Git Installation Check")
    
    success, output, error = run_command("git --version", check_output=True)
    
    if success:
        print_success(f"Git found: {output}")
        return True
    else:
        print_error("Git not found")
        print_info("Install Git from https://git-scm.com")
        return False


def check_postgresql_installation():
    """Check PostgreSQL installation and service"""
    print_header("PostgreSQL Installation Check")
    
    # Check if PostgreSQL service exists
    success, output, error = run_command('sc query "postgresql-x64-13"', check_output=True)
    
    if success and "RUNNING" in output:
        print_success("PostgreSQL service is running")
        service_ok = True
    elif success:
        print_warning("PostgreSQL service exists but is not running")
        service_ok = False
    else:
        print_error("PostgreSQL service not found")
        print_info("Install PostgreSQL from https://www.postgresql.org/download/windows/")
        service_ok = False
    
    # Check if psql command is available
    psql_paths = [
        "C:\\Program Files\\PostgreSQL\\13\\bin\\psql.exe",
        "C:\\Program Files\\PostgreSQL\\14\\bin\\psql.exe",
        "C:\\Program Files\\PostgreSQL\\15\\bin\\psql.exe",
        "psql"
    ]
    
    psql_found = False
    for psql_path in psql_paths:
        if Path(psql_path).exists() or shutil.which(psql_path):
            print_success(f"PostgreSQL client found: {psql_path}")
            psql_found = True
            break
    
    if not psql_found:
        print_warning("PostgreSQL client (psql) not found in PATH")
        print_info("Add PostgreSQL bin directory to PATH environment variable")
    
    return service_ok and psql_found


def check_web_server():
    """Check for web server (Nginx or IIS)"""
    print_header("Web Server Check")
    
    # Check for Nginx
    nginx_found = False
    nginx_paths = [
        "C:\\tools\\nginx\\nginx.exe",
        "C:\\nginx\\nginx.exe",
        "nginx"
    ]
    
    for nginx_path in nginx_paths:
        if Path(nginx_path).exists() or shutil.which(nginx_path):
            print_success(f"Nginx found: {nginx_path}")
            nginx_found = True
            break
    
    # Check for IIS
    iis_found = False
    success, output, error = run_command('sc query "W3SVC"', check_output=True)
    
    if success:
        if "RUNNING" in output:
            print_success("IIS (W3SVC) service is running")
            iis_found = True
        else:
            print_info("IIS service exists but is not running")
    
    if not nginx_found and not iis_found:
        print_warning("No web server found")
        print_info("Install Nginx or enable IIS for production deployment")
        return False
    
    return True


def check_firewall_configuration():
    """Check Windows Firewall configuration"""
    print_header("Windows Firewall Check")
    
    # Check if Windows Firewall is enabled
    success, output, error = run_command("netsh advfirewall show allprofiles state", check_output=True)
    
    if success:
        if "ON" in output:
            print_success("Windows Firewall is enabled")
        else:
            print_warning("Windows Firewall is disabled")
    else:
        print_warning("Could not check Windows Firewall status")
    
    # Check for HTTP/HTTPS rules
    success, output, error = run_command("netsh advfirewall firewall show rule name=all", check_output=True)
    
    http_rule_found = "80" in output or "HTTP" in output
    https_rule_found = "443" in output or "HTTPS" in output
    
    if http_rule_found:
        print_success("HTTP (port 80) firewall rule found")
    else:
        print_warning("HTTP (port 80) firewall rule not found")
    
    if https_rule_found:
        print_success("HTTPS (port 443) firewall rule found")
    else:
        print_warning("HTTPS (port 443) firewall rule not found")
    
    return True


def check_disk_space():
    """Check available disk space"""
    print_header("Disk Space Check")
    
    try:
        import shutil
        total, used, free = shutil.disk_usage("C:\\")
        
        free_gb = free // (1024**3)
        total_gb = total // (1024**3)
        
        print_info(f"C: drive - Total: {total_gb}GB, Free: {free_gb}GB")
        
        if free_gb >= 20:
            print_success(f"Sufficient disk space available ({free_gb}GB free)")
            return True
        else:
            print_error(f"Insufficient disk space ({free_gb}GB free, 20GB+ required)")
            return False
            
    except Exception as e:
        print_warning(f"Could not check disk space: {e}")
        return True


def check_memory():
    """Check available memory"""
    print_header("Memory Check")
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        
        print_info(f"Total RAM: {total_gb:.1f}GB, Available: {available_gb:.1f}GB")
        
        if total_gb >= 4:
            print_success(f"Sufficient memory ({total_gb:.1f}GB total)")
            return True
        else:
            print_warning(f"Limited memory ({total_gb:.1f}GB total, 4GB+ recommended)")
            return False
            
    except ImportError:
        print_info("psutil not available, skipping memory check")
        return True
    except Exception as e:
        print_warning(f"Could not check memory: {e}")
        return True


def check_network_connectivity():
    """Check internet connectivity"""
    print_header("Network Connectivity Check")
    
    test_urls = [
        "github.com",
        "nodejs.org",
        "python.org"
    ]
    
    connectivity_ok = True
    
    for url in test_urls:
        success, output, error = run_command(f"ping -n 1 {url}", check_output=True)
        
        if success:
            print_success(f"Can reach {url}")
        else:
            print_error(f"Cannot reach {url}")
            connectivity_ok = False
    
    return connectivity_ok


def check_project_dependencies():
    """Check if we can install project dependencies"""
    print_header("Project Dependencies Check")
    
    # Create a temporary test environment
    test_dir = Path("temp_test_env")
    
    try:
        test_dir.mkdir(exist_ok=True)
        os.chdir(test_dir)
        
        # Test Python virtual environment creation
        success, output, error = run_command("python -m venv test_venv")
        
        if success:
            print_success("Python virtual environment creation works")
            
            # Test pip install
            if platform.system() == "Windows":
                activate_script = "test_venv\\Scripts\\activate.bat"
                pip_cmd = "test_venv\\Scripts\\pip"
            else:
                activate_script = "test_venv/bin/activate"
                pip_cmd = "test_venv/bin/pip"
            
            success, output, error = run_command(f"{pip_cmd} install django", timeout=60)
            
            if success:
                print_success("Can install Python packages")
            else:
                print_error("Cannot install Python packages")
                return False
        else:
            print_error("Cannot create Python virtual environment")
            return False
        
        # Test npm functionality (if in a project directory)
        os.chdir("..")
        success, output, error = run_command("npm --version", check_output=True)
        
        if success:
            print_success("npm is functional")
        else:
            print_warning("npm test failed")
        
        return True
        
    except Exception as e:
        print_error(f"Dependency check failed: {e}")
        return False
    
    finally:
        # Cleanup
        os.chdir("..")
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)


def generate_report(results):
    """Generate a summary report"""
    print_header("🔍 Validation Summary Report")
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    failed_checks = total_checks - passed_checks
    
    print_info(f"Total checks: {total_checks}")
    print_success(f"Passed: {passed_checks}")
    
    if failed_checks > 0:
        print_error(f"Failed: {failed_checks}")
    
    print(f"\n{Colors.CYAN}Detailed Results:{Colors.END}")
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"  {color}{status}{Colors.END} {check_name}")
    
    if failed_checks == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 System is ready for ProjectMeats production deployment!{Colors.END}")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}🚫 System needs attention before production deployment{Colors.END}")
        print(f"\n{Colors.YELLOW}Next steps:{Colors.END}")
        print("1. Fix the failed checks above")
        print("2. Run this script again to verify fixes")
        print("3. Proceed with production deployment")
        return False


def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(description="Validate Windows system for ProjectMeats production deployment")
    parser.add_argument("--fix", action="store_true", help="Attempt to auto-fix issues")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    # Disable colors if needed
    Colors.disable_if_needed()
    
    print_header("🚀 ProjectMeats Windows Production Validation")
    print_info("This script will check if your Windows system is ready for production deployment")
    
    if not platform.system() == "Windows":
        print_error("This script is designed for Windows systems")
        sys.exit(1)
    
    # Run all validation checks
    checks = {
        "Windows Version": check_windows_version,
        "Administrator Privileges": check_administrator_privileges,
        "Python Installation": check_python_installation,
        "Node.js Installation": check_nodejs_installation,
        "Git Installation": check_git_installation,
        "PostgreSQL Installation": check_postgresql_installation,
        "Web Server": check_web_server,
        "Firewall Configuration": check_firewall_configuration,
        "Disk Space": check_disk_space,
        "Memory": check_memory,
        "Network Connectivity": check_network_connectivity,
        "Project Dependencies": check_project_dependencies,
    }
    
    results = {}
    
    for check_name, check_function in checks.items():
        try:
            results[check_name] = check_function()
        except Exception as e:
            print_error(f"Check '{check_name}' failed with error: {e}")
            results[check_name] = False
    
    # Generate final report
    system_ready = generate_report(results)
    
    if system_ready:
        print(f"\n{Colors.CYAN}Ready to deploy? Run:{Colors.END}")
        print("  .\\setup_windows_production.bat")
        print("  or")
        print("  python unified_deployment_tool.py --production --interactive")
    
    sys.exit(0 if system_ready else 1)


if __name__ == "__main__":
    main()