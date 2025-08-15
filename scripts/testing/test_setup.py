#!/usr/bin/env python3
"""
Test script for ProjectMeats AI Assistant setup validation.

This script tests the setup process and configuration without making changes.
"""

import os
import sys
from pathlib import Path


def test_setup_scripts():
    """Test that setup scripts exist and are valid Python"""
    project_root = Path(__file__).parent.absolute()
    
    scripts = [
        "setup.py",
        "setup_ai_assistant.py"
    ]
    
    print("🧪 Testing setup scripts...")
    
    for script in scripts:
        script_path = project_root / script
        if not script_path.exists():
            print(f"❌ Missing script: {script}")
            return False
        
        # Test compilation
        try:
            import py_compile
            py_compile.compile(script_path, doraise=True)
            print(f"✅ {script} - syntax valid")
        except py_compile.PyCompileError as e:
            print(f"❌ {script} - syntax error: {e}")
            return False
    
    return True


def test_backend_structure():
    """Test backend directory structure"""
    project_root = Path(__file__).parent.absolute()
    backend_dir = project_root / "backend"
    
    print("🔧 Testing backend structure...")
    
    required_files = [
        "manage.py",
        "requirements.txt",
        ".env.example",
        "projectmeats/settings.py"
    ]
    
    for file_path in required_files:
        full_path = backend_dir / file_path
        if not full_path.exists():
            print(f"❌ Missing backend file: {file_path}")
            return False
        else:
            print(f"✅ Found: {file_path}")
    
    # Test AI assistant app
    ai_app_dir = backend_dir / "apps" / "ai_assistant"
    if not ai_app_dir.exists():
        print("❌ Missing AI assistant app directory")
        return False
    
    ai_files = ["models.py", "views.py", "services/ai_service.py"]
    for file_path in ai_files:
        full_path = ai_app_dir / file_path
        if not full_path.exists():
            print(f"❌ Missing AI assistant file: {file_path}")
            return False
        else:
            print(f"✅ Found AI assistant: {file_path}")
    
    return True


def test_frontend_structure():
    """Test frontend directory structure"""
    project_root = Path(__file__).parent.absolute()
    frontend_dir = project_root / "frontend"
    
    print("🌐 Testing frontend structure...")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory missing")
        return False
    
    required_files = [
        "package.json",
        "src",
        ".env.production.template"
    ]
    
    for file_path in required_files:
        full_path = frontend_dir / file_path
        if not full_path.exists():
            print(f"❌ Missing frontend file/dir: {file_path}")
            return False
        else:
            print(f"✅ Found: {file_path}")
    
    return True


def test_environment_templates():
    """Test environment template files"""
    project_root = Path(__file__).parent.absolute()
    
    print("📝 Testing environment templates...")
    
    templates = [
        "backend/.env.example",
        "backend/.env.production.template",
        "frontend/.env.production.template"
    ]
    
    for template in templates:
        template_path = project_root / template
        if not template_path.exists():
            print(f"❌ Missing template: {template}")
            return False
        
        # Check if template has required variables
        with open(template_path, 'r') as f:
            content = f.read()
        
        if template.startswith("backend"):
            required_vars = ["SECRET_KEY", "DEBUG", "DATABASE_URL"]
            for var in required_vars:
                if var not in content:
                    print(f"❌ Missing variable in {template}: {var}")
                    return False
        
        print(f"✅ Template valid: {template}")
    
    return True


def test_documentation():
    """Test documentation exists"""
    project_root = Path(__file__).parent.absolute()
    docs_dir = project_root / "docs"
    
    print("📚 Testing documentation...")
    
    if not docs_dir.exists():
        print("❌ Documentation directory missing")
        return False
    
    required_docs = [
        "ai_assistant_setup.md",
        "setup-and-development.md"
    ]
    
    for doc in required_docs:
        doc_path = docs_dir / doc
        if not doc_path.exists():
            print(f"❌ Missing documentation: {doc}")
            return False
        else:
            print(f"✅ Found documentation: {doc}")
    
    return True


def test_setup_help():
    """Test setup script help output"""
    project_root = Path(__file__).parent.absolute()
    
    print("❓ Testing setup script help...")
    
    try:
        import subprocess
        
        # Test main setup help
        result = subprocess.run([
            sys.executable, "setup.py", "--help"
        ], cwd=project_root, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("❌ setup.py --help failed")
            return False
        
        if "ai assistant" not in result.stdout.lower():
            print("❌ setup.py help doesn't mention AI assistant")
            print(f"Help output preview: {result.stdout[:200]}...")
            return False
        
        print("✅ setup.py help output valid")
        
        # Test AI setup script exists
        ai_script = project_root / "setup_ai_assistant.py"
        if ai_script.exists():
            print("✅ AI assistant setup script exists")
        else:
            print("❌ AI assistant setup script missing")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Setup script help timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing setup help: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 ProjectMeats AI Assistant Setup Validation")
    print("=" * 50)
    
    tests = [
        ("Setup Scripts", test_setup_scripts),
        ("Backend Structure", test_backend_structure),
        ("Frontend Structure", test_frontend_structure),
        ("Environment Templates", test_environment_templates),
        ("Documentation", test_documentation),
        ("Setup Help", test_setup_help),
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
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Setup is ready to use.")
        print("\nNext steps:")
        print("1. Run: python setup_ai_assistant.py")
        print("2. Follow the interactive setup wizard")
        print("3. Start the development servers")
        return 0
    else:
        print("❌ Some tests failed. Please check the setup.")
        print("\nRecommended actions:")
        print("1. Ensure all required files are present")
        print("2. Check file permissions")
        print("3. Verify project structure")
        return 1


if __name__ == "__main__":
    sys.exit(main())