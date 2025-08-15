#!/usr/bin/env python3
"""
Test script for DNS and domain verification functionality.
Tests the new DNS and domain verification methods without requiring user input.
"""

import sys
import os
import subprocess
from unittest.mock import patch, MagicMock
import time

# Add the project root to Python path
sys.path.insert(0, '/home/runner/work/ProjectMeats/ProjectMeats')

# Import the deployment class
from deploy_production import ProductionDeployment

def test_dns_configuration():
    """Test DNS configuration checking"""
    print("🧪 Testing DNS configuration checking...")
    
    # Create deployment instance
    deployment = ProductionDeployment()
    deployment.config = {'domain': 'example.com'}
    deployment.is_local_setup = False
    
    # Mock subprocess to simulate DNS responses
    with patch('subprocess.run') as mock_run:
        # Test case 1: DNS resolves correctly
        mock_run.side_effect = [
            # dig --version check
            MagicMock(returncode=0),
            # DNS query with correct IP
            MagicMock(returncode=0, stdout="167.99.155.140\n")
        ]
        
        result = deployment.check_dns_configuration("167.99.155.140")
        assert result == True, "Should return True when DNS resolves correctly"
        print("✅ Test 1 passed: DNS resolves correctly")
        
        # Test case 2: DNS doesn't resolve
        mock_run.side_effect = [
            # dig --version check  
            MagicMock(returncode=0),
            # DNS query with no result
            MagicMock(returncode=0, stdout="\n")
        ]
        
        # Mock user input to continue anyway and mock time.sleep
        with patch.object(deployment, 'confirm', return_value=True), \
             patch('time.sleep'):  # Mock sleep to avoid waiting
            result = deployment.check_dns_configuration("167.99.155.140")
            assert result == True, "Should return True when user chooses to continue"
            print("✅ Test 2 passed: Handles no DNS resolution with user confirmation")

def test_domain_verification():
    """Test domain accessibility verification"""
    print("\n🧪 Testing domain verification...")
    
    deployment = ProductionDeployment()
    deployment.config = {'domain': 'example.com'}
    deployment.is_local_setup = False
    
    with patch('subprocess.run') as mock_run:
        # Mock successful DNS and HTTP response
        mock_run.side_effect = [
            # DNS query
            MagicMock(returncode=0, stdout="167.99.155.140\n"),
            # HTTP connectivity test
            MagicMock(returncode=0, stdout="HTTP/1.1 200 OK\n"),
        ]
        
        result = deployment.verify_domain_accessibility("167.99.155.140")
        assert result == True, "Should return True when both DNS and HTTP work"
        print("✅ Test 3 passed: Domain verification successful")

def test_localhost_skip():
    """Test that localhost deployments skip DNS checks"""
    print("\n🧪 Testing localhost deployment skip...")
    
    deployment = ProductionDeployment()
    deployment.config = {'domain': 'localhost'}
    deployment.is_local_setup = True
    
    # Should skip without any subprocess calls
    result1 = deployment.check_dns_configuration()
    result2 = deployment.verify_domain_accessibility()
    
    assert result1 == True, "Should skip DNS check for localhost"
    assert result2 == True, "Should skip domain verification for localhost"
    print("✅ Test 4 passed: Localhost deployments skip DNS checks")

def test_dig_not_available():
    """Test behavior when dig command is not available"""
    print("\n🧪 Testing behavior when dig is not available...")
    
    deployment = ProductionDeployment()
    deployment.config = {'domain': 'example.com'}
    deployment.is_local_setup = False
    
    with patch('subprocess.run') as mock_run:
        # Simulate dig command not found
        mock_run.side_effect = FileNotFoundError("dig not found")
        
        result = deployment.check_dns_configuration("167.99.155.140")
        assert result == True, "Should continue when dig is not available"
        print("✅ Test 5 passed: Handles missing dig command gracefully")

def main():
    """Run all tests"""
    print("🚀 Running DNS and Domain Verification Tests")
    print("=" * 50)
    
    try:
        test_localhost_skip()
        test_dig_not_available()
        test_dns_configuration()
        test_domain_verification()
        
        print("\n🎉 All tests passed!")
        print("\nNote: These tests validate the logic with mocked network calls.")
        print("For real network testing, run the deployment script in a test environment.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())