#!/usr/bin/env python3
"""
Frontend Setup Validation Script

This script validates that the frontend environment is properly configured
for CI/CD pipeline execution.
"""

import os
import subprocess
import sys
import json
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def validate_frontend_structure():
    """Validate frontend directory structure."""
    print("🔍 Validating frontend directory structure...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    required_files = [
        "package.json",
        "package-lock.json",
        "tsconfig.json",
        "src/App.tsx",
        "src/App.test.tsx",
        "public/index.html"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (frontend_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ Frontend directory structure is valid")
    return True


def validate_package_json():
    """Validate package.json configuration."""
    print("📦 Validating package.json configuration...")
    
    try:
        with open("frontend/package.json") as f:
            package_data = json.load(f)
        
        required_scripts = ["start", "build", "test", "type-check", "lint"]
        missing_scripts = []
        
        scripts = package_data.get("scripts", {})
        for script in required_scripts:
            if script not in scripts:
                missing_scripts.append(script)
        
        if missing_scripts:
            print(f"❌ Missing scripts: {', '.join(missing_scripts)}")
            return False
        
        print("✅ Package.json configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading package.json: {e}")
        return False


def test_npm_commands():
    """Test basic npm commands."""
    print("🧪 Testing npm commands...")
    
    # Test npm ci
    success, stdout, stderr = run_command("npm ci", cwd="frontend", check=False)
    if not success:
        print(f"❌ npm ci failed: {stderr}")
        return False
    print("✅ npm ci completed successfully")
    
    # Test type checking
    success, stdout, stderr = run_command("npm run type-check", cwd="frontend", check=False)
    if not success:
        print(f"⚠️  Type checking issues found: {stderr}")
        # Don't fail on type errors, just warn
    else:
        print("✅ Type checking passed")
    
    # Test linting
    success, stdout, stderr = run_command("npm run lint", cwd="frontend", check=False)
    if not success:
        print(f"⚠️  Linting issues found: {stderr}")
        # Don't fail on lint errors, just warn
    else:
        print("✅ Linting passed")
    
    # Test build
    success, stdout, stderr = run_command("npm run build", cwd="frontend", check=False)
    if not success:
        print(f"❌ Build failed: {stderr}")
        return False
    print("✅ Build completed successfully")
    
    return True


def main():
    """Main validation function."""
    print("🚀 Starting frontend setup validation...")
    print("=" * 50)
    
    # Change to project root
    os.chdir(Path(__file__).parent)
    
    validations = [
        validate_frontend_structure,
        validate_package_json,
        test_npm_commands,
    ]
    
    all_passed = True
    for validation in validations:
        try:
            if not validation():
                all_passed = False
        except Exception as e:
            print(f"❌ Validation error: {e}")
            all_passed = False
        print("-" * 30)
    
    if all_passed:
        print("🎉 All frontend validations passed!")
        print("✅ Frontend is ready for CI/CD pipeline")
        return 0
    else:
        print("❌ Some validations failed")
        print("🔧 Please fix the issues above before running CI/CD")
        return 1


if __name__ == "__main__":
    sys.exit(main())