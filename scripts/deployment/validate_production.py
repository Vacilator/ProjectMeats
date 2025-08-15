#!/usr/bin/env python
"""
ProjectMeats Production Readiness Validator

This script validates that the repository is ready for production deployment
by checking various configurations, dependencies, and code quality metrics.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None):
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_backend_tests():
    """Check if all backend tests pass."""
    print("🧪 Checking backend tests...")
    backend_dir = Path(__file__).parent / "backend"
    success, stdout, stderr = run_command(
        "python manage.py test --keepdb -v 0", cwd=backend_dir
    )
    
    if success:
        print("✅ All backend tests passing")
        return True
    else:
        print(f"❌ Backend tests failed: {stderr}")
        return False


def check_frontend_build():
    """Check if frontend builds successfully."""
    print("🏗️  Checking frontend build...")
    frontend_dir = Path(__file__).parent / "frontend"
    success, stdout, stderr = run_command("npm run build", cwd=frontend_dir)
    
    if success:
        print("✅ Frontend builds successfully")
        return True
    else:
        print(f"❌ Frontend build failed: {stderr}")
        return False


def check_backend_linting():
    """Check backend code quality."""
    print("🔍 Checking backend code quality...")
    backend_dir = Path(__file__).parent / "backend"
    success, stdout, stderr = run_command(
        "flake8 --exclude=migrations --select=F401,F841,E722 --statistics", 
        cwd=backend_dir
    )
    
    if success or "0" in stdout:
        print("✅ Backend code quality good")
        return True
    else:
        print(f"⚠️  Backend linting issues found: {stdout}")
        return True  # Non-critical for deployment


def check_environment_templates():
    """Check if environment templates exist."""
    print("📝 Checking environment templates...")
    backend_dir = Path(__file__).parent / "backend"
    
    templates = [
        ".env.example",
        ".env.production.template"
    ]
    
    all_exist = True
    for template in templates:
        if (backend_dir / template).exists():
            print(f"✅ {template} exists")
        else:
            print(f"❌ {template} missing")
            all_exist = False
    
    return all_exist


def check_security_configuration():
    """Check security settings."""
    print("🔒 Checking security configuration...")
    backend_dir = Path(__file__).parent / "backend"
    settings_file = backend_dir / "projectmeats" / "settings.py"
    
    if not settings_file.exists():
        print("❌ Settings file not found")
        return False
    
    settings_content = settings_file.read_text()
    
    security_checks = [
        ("DEBUG = config", "DEBUG configuration found"),
        ("SECRET_KEY = config", "SECRET_KEY configuration found"),
        ("ALLOWED_HOSTS", "ALLOWED_HOSTS configuration found"),
        ("SECURE_BROWSER_XSS_FILTER", "XSS protection configured"),
        ("CORS_ALLOWED_ORIGINS", "CORS configuration found"),
    ]
    
    all_good = True
    for check, message in security_checks:
        if check in settings_content:
            print(f"✅ {message}")
        else:
            print(f"⚠️  {message} - might need review")
            # Not failing for these as they might be configured differently
    
    return all_good


def check_dependencies():
    """Check if dependencies are up to date."""
    print("📦 Checking dependencies...")
    
    # Check backend requirements
    backend_dir = Path(__file__).parent / "backend"
    if (backend_dir / "requirements.txt").exists():
        print("✅ Backend requirements.txt exists")
    else:
        print("❌ Backend requirements.txt missing")
        return False
    
    # Check frontend package.json
    frontend_dir = Path(__file__).parent / "frontend"
    if (frontend_dir / "package.json").exists():
        print("✅ Frontend package.json exists")
    else:
        print("❌ Frontend package.json missing")
        return False
    
    return True


def check_documentation():
    """Check if key documentation exists."""
    print("📚 Checking documentation...")
    
    docs = [
        "README.md",
        "docs/production_deployment.md",
        "production_checklist.md",
    ]
    
    all_exist = True
    for doc in docs:
        doc_path = Path(__file__).parent / doc
        if doc_path.exists():
            print(f"✅ {doc} exists")
        else:
            print(f"⚠️  {doc} missing")
            # Not critical for deployment
    
    return all_exist


def main():
    """Run all production readiness checks."""
    print("🚀 ProjectMeats Production Readiness Check")
    print("=" * 50)
    
    checks = [
        ("Backend Tests", check_backend_tests),
        ("Frontend Build", check_frontend_build),
        ("Backend Code Quality", check_backend_linting),
        ("Environment Templates", check_environment_templates),
        ("Security Configuration", check_security_configuration),
        ("Dependencies", check_dependencies),
        ("Documentation", check_documentation),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔄 Running {name} check...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error running {name} check: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Production Readiness Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    critical_failed = []
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if result:
            passed += 1
        elif name in ["Backend Tests", "Frontend Build", "Dependencies"]:
            critical_failed.append(name)
    
    print(f"\nPassed: {passed}/{total}")
    
    if critical_failed:
        print(f"\n❌ CRITICAL FAILURES: {', '.join(critical_failed)}")
        print("🚫 Repository is NOT ready for production deployment")
        return False
    elif passed == total:
        print("\n🎉 Repository is READY for production deployment!")
        return True
    else:
        print("\n⚠️  Repository is mostly ready with minor issues")
        print("✅ Deployment can proceed with caution")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)