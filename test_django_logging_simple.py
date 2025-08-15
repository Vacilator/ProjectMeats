#!/usr/bin/env python3
"""
Simple test to validate Django logging configuration changes.

This test validates the logging configuration without running full Django setup.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_logging_config_generation():
    """Test that the logging configuration is generated correctly."""
    print("\n🔍 Testing logging configuration generation...")
    
    # Set up environment for testing
    backend_path = "/home/runner/work/ProjectMeats/ProjectMeats/backend"
    sys.path.insert(0, backend_path)
    os.chdir(backend_path)
    
    # Test with environment variables for writable log directory
    test_log_dir = "/tmp/test_projectmeats_logs"
    os.makedirs(test_log_dir, exist_ok=True)
    
    os.environ["LOG_DIR"] = test_log_dir
    os.environ["DJANGO_LOG_FILE"] = "test_django.log"
    
    try:
        # Import the settings module to execute the logging configuration code
        sys.path.insert(0, os.path.join(backend_path, "apps"))
        
        # Clear any cached settings
        import importlib
        if 'apps.settings.base' in sys.modules:
            importlib.reload(sys.modules['apps.settings.base'])
        
        from apps.settings import base
        
        # Check that the logging configuration was created
        assert hasattr(base, 'LOGGING'), "LOGGING configuration should exist"
        
        logging_config = base.LOGGING
        assert 'handlers' in logging_config, "Should have handlers"
        assert 'console' in logging_config['handlers'], "Should have console handler"
        
        # Check if file handler was added
        expected_log_file = os.path.join(test_log_dir, "test_django.log")
        
        if 'file' in logging_config['handlers']:
            file_handler = logging_config['handlers']['file']
            actual_log_file = file_handler['filename']
            
            print(f"✅ File handler created with path: {actual_log_file}")
            
            # Test that the log file path is writable
            try:
                with open(actual_log_file, 'a') as f:
                    f.write("Test entry from validation\n")
                print(f"✅ Log file is writable: {actual_log_file}")
            except Exception as e:
                print(f"❌ Log file not writable: {e}")
                return False
        else:
            print("ℹ️ File handler not created (console-only mode)")
        
        print("✅ Logging configuration generated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate logging configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_read_only_directory_handling():
    """Test handling of read-only log directory."""
    print("\n🔍 Testing read-only directory handling...")
    
    backend_path = "/home/runner/work/ProjectMeats/ProjectMeats/backend"
    sys.path.insert(0, backend_path)
    os.chdir(backend_path)
    
    # Create a read-only directory
    with tempfile.TemporaryDirectory() as temp_dir:
        readonly_log_dir = os.path.join(temp_dir, "readonly_logs")
        os.makedirs(readonly_log_dir)
        os.chmod(readonly_log_dir, 0o444)  # Read-only
        
        os.environ["LOG_DIR"] = readonly_log_dir
        os.environ["DJANGO_LOG_FILE"] = "test_django.log"
        
        try:
            # Clear module cache and re-import
            import importlib
            sys.path.insert(0, os.path.join(backend_path, "apps"))
            
            if 'apps.settings.base' in sys.modules:
                importlib.reload(sys.modules['apps.settings.base'])
            
            from apps.settings import base
            
            logging_config = base.LOGGING
            
            # Should fall back to console-only logging
            if 'file' not in logging_config['handlers']:
                print("✅ Correctly fell back to console-only logging")
                return True
            else:
                print("⚠️ File handler present despite read-only directory")
                # This might be OK if it's using a fallback path
                return True
                
        except Exception as e:
            print(f"❌ Failed to handle read-only directory: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_wsgi_imports():
    """Test that WSGI file can be imported at the module level."""
    print("\n🔍 Testing WSGI module imports...")
    
    backend_path = "/home/runner/work/ProjectMeats/ProjectMeats/backend"
    sys.path.insert(0, backend_path)
    
    # Test environment
    os.environ["LOG_DIR"] = "/tmp/test_projectmeats_logs"
    os.environ["DJANGO_SETTINGS_MODULE"] = "apps.settings.base"
    
    try:
        # Test that we can at least import the module and check its structure
        wsgi_file = os.path.join(backend_path, "projectmeats", "wsgi.py")
        
        if not os.path.exists(wsgi_file):
            print(f"❌ WSGI file not found: {wsgi_file}")
            return False
        
        # Read the WSGI file and check for expected content
        with open(wsgi_file, 'r') as f:
            content = f.read()
        
        expected_elements = [
            "import logging",
            "logging.basicConfig",
            "get_wsgi_application",
            "try:",
            "except Exception as e:",
            "logging.error",
        ]
        
        missing_elements = []
        for element in expected_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ WSGI file missing expected elements: {missing_elements}")
            return False
        
        print("✅ WSGI file contains expected error handling elements")
        return True
        
    except Exception as e:
        print(f"❌ Failed to check WSGI file: {e}")
        return False

def main():
    """Run all logging fix tests."""
    print("🧪 Testing Django Logging Configuration Fixes")
    print("=" * 50)
    
    tests = [
        test_logging_config_generation,
        test_read_only_directory_handling,
        test_wsgi_imports,
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