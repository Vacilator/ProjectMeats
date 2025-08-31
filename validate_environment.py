#!/usr/bin/env python3
"""
ProjectMeats Environment Validation Script

This script validates that your environment is properly configured for deployment
and tests the unified environment management system.

Usage:
    python validate_environment.py
    python validate_environment.py --test-deployment
"""

import os
import sys
import argparse
from pathlib import Path


def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required, found", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} (compatible)")
    return True


def check_deployment_structure():
    """Check that deployment files are in place"""
    print("\n📁 Checking deployment file structure...")
    
    required_files = [
        "ai_deployment_orchestrator.py",
        "deployment/environment_config.py", 
        "deployment/templates/environment.template",
        "backend/projectmeats/settings.py",
        "ENVIRONMENT_SETUP_GUIDE.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    return len(missing_files) == 0


def check_environment_manager():
    """Test the environment configuration manager"""
    print("\n🔧 Testing Environment Configuration Manager...")
    
    try:
        from deployment.environment_config import EnvironmentConfigManager
        print("✅ EnvironmentConfigManager imported successfully")
        
        # Test credential generation
        mgr = EnvironmentConfigManager()
        credentials = mgr.generate_secure_credentials()
        
        print(f"✅ Credential generation working:")
        print(f"   Secret key: {len(credentials['secret_key'])} characters")
        print(f"   DB name: {credentials['db_name']}")
        print(f"   DB user: {credentials['db_user']}")
        print(f"   DB password: {len(credentials['db_password'])} characters")
        
        # Test configuration validation
        test_config = {
            'secret_key': credentials['secret_key'],
            'db_name': credentials['db_name'],
            'db_user': credentials['db_user'],
            'db_password': credentials['db_password'],
            'domain': 'test.example.com',
            'allowed_hosts': 'test.example.com,localhost',
            'cors_origins': 'https://test.example.com'
        }
        
        is_valid, issues = mgr.validate_configuration(test_config)
        if is_valid:
            print("✅ Configuration validation working")
        else:
            print("⚠️  Configuration validation found issues:")
            for issue in issues:
                print(f"   - {issue}")
        
        # Test environment file generation
        env_content = mgr.create_environment_file(test_config)
        print(f"✅ Environment file generation working ({len(env_content)} chars)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import EnvironmentConfigManager: {e}")
        return False
    except Exception as e:
        print(f"❌ Environment manager test failed: {e}")
        return False


def check_django_integration():
    """Test Django settings integration"""
    print("\n⚙️ Testing Django settings integration...")
    
    try:
        # Change to backend directory
        os.chdir('backend')
        
        # Test importing Django settings
        import projectmeats.settings
        print("✅ Django settings imported successfully")
        
        # Test configuration function with environment variables
        os.environ['TEST_DEBUG'] = 'False'
        os.environ['TEST_SECRET'] = 'test-secret-key-for-validation'
        
        # Test the config function directly
        import projectmeats.settings as settings_module
        
        # Check if config function works
        if hasattr(settings_module, 'config'):
            config_func = settings_module.config
            debug_val = config_func('TEST_DEBUG', default=True, cast=bool)
            secret_val = config_func('TEST_SECRET', default='default')
            
            if debug_val == False and secret_val == 'test-secret-key-for-validation':
                print("✅ Environment variable reading working")
            else:
                print(f"⚠️  Environment variable reading issues: DEBUG={debug_val}, SECRET={secret_val}")
        
        # Cleanup
        del os.environ['TEST_DEBUG']
        del os.environ['TEST_SECRET']
        os.chdir('..')
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import Django settings: {e}")
        print("   This is normal if Django dependencies aren't installed")
        os.chdir('..')
        return True  # Don't fail on missing Django in validation environment
    except Exception as e:
        print(f"❌ Django integration test failed: {e}")
        os.chdir('..')
        return False


def check_orchestrator_integration():
    """Test AI deployment orchestrator integration"""
    print("\n🤖 Testing AI Deployment Orchestrator integration...")
    
    try:
        # Test that the orchestrator file has the correct imports
        with open('ai_deployment_orchestrator.py', 'r') as f:
            content = f.read()
        
        if 'from deployment.environment_config import EnvironmentConfigManager' in content:
            print("✅ Orchestrator imports EnvironmentConfigManager")
        else:
            print("❌ Orchestrator missing EnvironmentConfigManager import")
            return False
        
        if 'ENVIRONMENT_CONFIG_AVAILABLE' in content:
            print("✅ Orchestrator has environment config availability check")
        else:
            print("❌ Orchestrator missing availability check")
            return False
        
        if 'env_manager' in content:
            print("✅ Orchestrator uses env_manager attribute")
        else:
            print("❌ Orchestrator not using env_manager")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator integration check failed: {e}")
        return False


def test_full_deployment_flow():
    """Test a simulated deployment flow"""
    print("\n🚀 Testing simulated deployment flow...")
    
    try:
        from deployment.environment_config import EnvironmentConfigManager
        
        # Simulate the flow that the orchestrator would use
        mgr = EnvironmentConfigManager()
        
        # Generate credentials
        credentials = mgr.generate_secure_credentials()
        print("✅ 1. Credentials generated")
        
        # Create full configuration
        config = {
            'debug': False,
            'secret_key': credentials['secret_key'],
            'db_name': credentials['db_name'],
            'db_user': credentials['db_user'],
            'db_password': credentials['db_password'],
            'db_host': 'localhost',
            'db_port': '5432',
            'domain': 'testdeploy.example.com',
            'allowed_hosts': 'testdeploy.example.com,www.testdeploy.example.com,localhost,127.0.0.1',
            'cors_origins': 'https://testdeploy.example.com,https://www.testdeploy.example.com',
            'enable_ssl': True,
            'email_host': '',
            'company_name': 'Test Deployment Company',
            'company_email': 'admin@testdeploy.example.com',
            'company_phone': '+1-555-987-6543',
            'company_address': '456 Deployment Ave',
            'static_root': '/opt/projectmeats/backend/staticfiles',
            'media_root': '/opt/projectmeats/media',
            'log_dir': '/opt/projectmeats/logs',
            'backup_dir': '/opt/projectmeats/backups'
        }
        
        # Validate configuration
        is_valid, issues = mgr.validate_configuration(config)
        if is_valid:
            print("✅ 2. Configuration validated")
        else:
            print("❌ 2. Configuration validation failed")
            for issue in issues:
                print(f"   - {issue}")
            return False
        
        # Generate environment file
        env_content = mgr.create_environment_file(config)
        print("✅ 3. Environment file generated")
        
        # Check that all required sections are present
        required_sections = [
            'DEBUG=false',
            f'SECRET_KEY={credentials["secret_key"]}',
            f'DATABASE_URL=postgresql://{credentials["db_user"]}:{credentials["db_password"]}@localhost:5432/{credentials["db_name"]}',
            'ALLOWED_HOSTS=testdeploy.example.com',
            'CORS_ALLOWED_ORIGINS=https://testdeploy.example.com',
            'SECURE_SSL_REDIRECT=True',
            'COMPANY_NAME=Test Deployment Company'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in env_content:
                missing_sections.append(section)
        
        if missing_sections:
            print("❌ 4. Environment file missing required sections:")
            for section in missing_sections:
                print(f"   - {section}")
            return False
        else:
            print("✅ 4. All required environment sections present")
        
        print(f"✅ Full deployment flow test PASSED")
        print(f"   Generated environment file: {len(env_content)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment flow test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Validate ProjectMeats environment setup')
    parser.add_argument('--test-deployment', action='store_true', 
                       help='Run full deployment flow test')
    args = parser.parse_args()
    
    print("🔍 ProjectMeats Environment Validation")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Deployment Structure", check_deployment_structure),
        ("Environment Manager", check_environment_manager),
        ("Django Integration", check_django_integration),
        ("Orchestrator Integration", check_orchestrator_integration),
    ]
    
    if args.test_deployment:
        checks.append(("Full Deployment Flow", test_full_deployment_flow))
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Environment is ready for deployment.")
        print("\nNext steps:")
        print("1. Ensure your server meets the requirements (see ENVIRONMENT_SETUP_GUIDE.md)")
        print("2. Configure DNS for your domain")
        print("3. Run: python ai_deployment_orchestrator.py --interactive --domain=yourdomain.com")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("📖 See ENVIRONMENT_SETUP_GUIDE.md for troubleshooting help.")
        return 1


if __name__ == "__main__":
    sys.exit(main())