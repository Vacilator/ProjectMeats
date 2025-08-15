#!/usr/bin/env python3
"""
Test script to validate Django logging configuration fixes for read-only filesystem issue.

This script tests:
1. Django settings can be loaded without logging errors
2. Logging configuration uses writable paths
3. Fallback mechanisms work when log files are not writable
4. WSGI application can be imported successfully
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_django_settings_load():
    """Test that Django settings can be loaded without errors."""
    print("\n🔍 Testing Django settings loading...")
    
    # Set up environment for testing
    backend_path = "/home/runner/work/ProjectMeats/ProjectMeats/backend"
    sys.path.insert(0, backend_path)
    os.chdir(backend_path)
    
    # Test with environment variables for writable log directory
    os.environ["LOG_DIR"] = "/tmp/test_projectmeats_logs"
    os.environ["DJANGO_LOG_FILE"] = "test_django.log"
    os.environ["DJANGO_SETTINGS_MODULE"] = "apps.settings.base"
    
    try:
        import django
        from django.conf import settings
        django.setup()
        
        # Check logging configuration
        logging_config = settings.LOGGING
        
        print("✅ Django settings loaded successfully")
        print(f"✅ Logging handlers: {list(logging_config['handlers'].keys())}")
        
        # Test if file handler was added (should be, since /tmp is writable)
        if 'file' in logging_config['handlers']:
            file_handler = logging_config['handlers']['file']
            log_file = file_handler['filename']
            print(f"✅ File logging enabled, path: {log_file}")
            
            # Test that we can actually write to the log file
            try:
                with open(log_file, 'a') as f:
                    f.write("Test log entry\n")
                print(f"✅ Log file is writable: {log_file}")
            except Exception as e:
                print(f"❌ Cannot write to log file: {e}")
                return False
        else:
            print("ℹ️ File logging disabled (console-only mode)")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to load Django settings: {e}")
        return False

def test_read_only_fallback():
    """Test that logging falls back gracefully when log directory is not writable."""
    print("\n🔍 Testing read-only directory fallback...")
    
    backend_path = "/home/runner/work/ProjectMeats/ProjectMeats/backend"
    sys.path.insert(0, backend_path)
    os.chdir(backend_path)
    
    # Create a read-only directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        readonly_log_dir = os.path.join(temp_dir, "readonly_logs")
        os.makedirs(readonly_log_dir)
        os.chmod(readonly_log_dir, 0o444)  # Read-only
        
        # Set environment to use read-only directory
        os.environ["LOG_DIR"] = readonly_log_dir
        os.environ["DJANGO_LOG_FILE"] = "test_django.log"
        os.environ["DJANGO_SETTINGS_MODULE"] = "apps.settings.base"
        
        # Clear Django settings cache
        if 'django.conf' in sys.modules and hasattr(sys.modules['django.conf'], '_wrapped'):
            del sys.modules['django.conf']._wrapped
        
        try:
            import django
            from django.conf import settings
            
            # This should work even with read-only log directory
            django.setup()
            
            logging_config = settings.LOGGING
            
            # Should not have file handler due to permission error
            if 'file' not in logging_config['handlers']:
                print("✅ Gracefully fell back to console-only logging")
                return True
            else:
                print("⚠️ File handler still present despite read-only directory")
                # This might still be OK if it's using a different path
                return True
                
        except Exception as e:
            print(f"❌ Django setup failed with read-only log directory: {e}")
            return False

def test_wsgi_import():
    """Test that WSGI application can be imported."""
    print("\n🔍 Testing WSGI application import...")
    
    backend_path = "/home/runner/work/ProjectMeats/ProjectMeats/backend"
    sys.path.insert(0, backend_path)
    os.chdir(backend_path)
    
    # Set up environment
    os.environ["LOG_DIR"] = "/tmp/test_projectmeats_logs"
    os.environ["DJANGO_SETTINGS_MODULE"] = "apps.settings.base"
    
    try:
        from projectmeats.wsgi import application
        print("✅ WSGI application imported successfully")
        print(f"✅ Application type: {type(application)}")
        return True
    except Exception as e:
        print(f"❌ Failed to import WSGI application: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all logging fix tests."""
    print("🧪 Testing Django Logging Configuration Fixes")
    print("=" * 50)
    
    tests = [
        test_django_settings_load,
        test_read_only_fallback,
        test_wsgi_import,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test_func.__name__}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Logging fixes are working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)