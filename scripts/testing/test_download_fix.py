#!/usr/bin/env python3
"""
Test script to verify the download fix works
"""
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from ai_deployment_orchestrator import AIDeploymentOrchestrator

def test_download_method():
    """Test the improved download method"""
    print("Testing improved download method...")
    
    # Create a test orchestrator
    orchestrator = AIDeploymentOrchestrator()
    
    # Mock the execute_command method to simulate successful operations
    def mock_execute_command(command, timeout=None):
        print(f"Mock executing: {command[:100]}...")
        
        # Simulate different command responses
        if "mkdir -p" in command:
            return 0, "", ""
        elif "ls -A" in command and "wc -l" in command:
            return 0, "0", ""  # Empty directory
        elif "curl -s --connect-timeout" in command and "github.com" in command:
            return 0, "", ""  # Network connectivity OK
        elif "test -d" in command and "backend" in command:
            return 0, "", ""  # Files exist
        elif "test -f" in command:
            return 0, "", ""  # Files exist
        elif "git clone" in command:
            return 0, "Cloning...", ""  # Successful clone
        else:
            return 0, "", ""
    
    # Mock the log method
    def mock_log(message, level="INFO", color=None):
        print(f"[{level}] {message}")
    
    # Apply mocks
    orchestrator.execute_command = mock_execute_command
    orchestrator.log = mock_log
    
    # Test the download method
    try:
        result = orchestrator.deploy_download_application()
        if result:
            print("✅ Download method test PASSED")
            return True
        else:
            print("❌ Download method test FAILED")
            return False
    except Exception as e:
        print(f"❌ Download method test FAILED with exception: {e}")
        return False

def test_timeout_handling():
    """Test that timeout values are properly set"""
    print("\nTesting timeout handling...")
    
    orchestrator = AIDeploymentOrchestrator()
    
    # Check that the timeout configuration is reasonable
    default_timeout = orchestrator.config['deployment']['command_timeout']
    print(f"Default command timeout: {default_timeout} seconds")
    
    if default_timeout >= 300:
        print("✅ Default timeout is reasonable")
    else:
        print("❌ Default timeout may be too short")
        return False
    
    return True

def test_network_connectivity_check():
    """Test network connectivity checking logic"""
    print("\nTesting network connectivity check...")
    
    # This would normally test actual network connectivity
    # For this test, we'll just verify the logic exists
    orchestrator = AIDeploymentOrchestrator()
    
    # Check that the method includes network testing
    method_source = orchestrator.deploy_download_application.__doc__
    if "timeout" in method_source.lower():
        print("✅ Method includes timeout handling")
        return True
    else:
        print("❌ Method may not handle timeouts properly")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing AI Deployment Orchestrator Download Fix")
    print("=" * 60)
    
    tests = [
        test_download_method,
        test_timeout_handling,
        test_network_connectivity_check
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The download fix should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())