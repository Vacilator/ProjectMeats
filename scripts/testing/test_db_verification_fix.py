#!/usr/bin/env python3
"""
Test script to validate the database verification fix for deployment issue

This test validates:
1. Database credential loading from JSON file  
2. Enhanced database connectivity testing
3. Environment variable validation
4. Fallback database testing
"""
import json
import os
import sys
from unittest.mock import MagicMock

# Add current directory to path to import our module
sys.path.insert(0, os.path.dirname(__file__))

try:
    from ai_deployment_orchestrator import AIDeploymentOrchestrator
except ImportError as e:
    print(f"Could not import AIDeploymentOrchestrator: {e}")
    sys.exit(1)

def test_database_credential_loading():
    """Test loading database credentials from JSON file"""
    print("Testing database credential loading...")
    
    # Create a mock orchestrator
    orchestrator = AIDeploymentOrchestrator()
    orchestrator.ssh_client = MagicMock()
    orchestrator.log = MagicMock()  # Mock the logging
    
    # Test 1: Valid credentials file
    valid_creds = {
        "deployment_time": "2024-01-01T00:00:00",
        "database_name": "projectmeats_prod_test123",
        "database_user": "pm_user_test456",
        "database_password": "secure_test_password",
        "database_host": "localhost",
        "database_port": 5432
    }
    
    # Mock the execute_command to return valid JSON
    orchestrator.execute_command = MagicMock(return_value=(0, json.dumps(valid_creds), ""))
    
    db_name, db_user, db_password = orchestrator._load_database_credentials()
    
    assert db_name == "projectmeats_prod_test123", f"Expected 'projectmeats_prod_test123', got '{db_name}'"
    assert db_user == "pm_user_test456", f"Expected 'pm_user_test456', got '{db_user}'"
    assert db_password == "secure_test_password", f"Expected 'secure_test_password', got '{db_password}'"
    print("✓ Valid credentials test passed")
    
    # Test 2: File not found
    orchestrator.execute_command = MagicMock(return_value=(1, "FILE_NOT_FOUND", "No such file"))
    
    db_name, db_user, db_password = orchestrator._load_database_credentials()
    
    assert db_name is None, f"Expected None, got '{db_name}'"
    assert db_user is None, f"Expected None, got '{db_user}'"
    assert db_password is None, f"Expected None, got '{db_password}'"
    print("✓ File not found test passed")
    
    # Test 3: Invalid JSON
    orchestrator.execute_command = MagicMock(return_value=(0, "invalid json {", ""))
    
    db_name, db_user, db_password = orchestrator._load_database_credentials()
    
    assert db_name is None, f"Expected None, got '{db_name}'"
    assert db_user is None, f"Expected None, got '{db_user}'"
    assert db_password is None, f"Expected None, got '{db_password}'"
    print("✓ Invalid JSON test passed")

def test_database_environment_validation():
    """Test database environment validation"""
    print("\nTesting database environment validation...")
    
    orchestrator = AIDeploymentOrchestrator()
    orchestrator.ssh_client = MagicMock()
    orchestrator.log = MagicMock()
    
    # Test matching DATABASE_URL
    test_db_name = "test_db"
    test_db_user = "test_user"
    test_db_password = "test_pass"
    
    expected_url = f"postgres://{test_db_user}:{test_db_password}@localhost:5432/{test_db_name}"
    orchestrator.execute_command = MagicMock(return_value=(0, f"DATABASE_URL={expected_url}", ""))
    
    result = orchestrator._validate_database_environment(test_db_name, test_db_user, test_db_password)
    assert result == True, "Environment validation should pass with matching URL"
    print("✓ Matching DATABASE_URL test passed")
    
    # Test non-matching DATABASE_URL
    orchestrator.execute_command = MagicMock(return_value=(0, "DATABASE_URL=postgres://wrong:wrong@localhost:5432/wrong", ""))
    
    result = orchestrator._validate_database_environment(test_db_name, test_db_user, test_db_password)
    assert result == False, "Environment validation should fail with non-matching URL"
    print("✓ Non-matching DATABASE_URL test passed")

def test_fallback_database_test():
    """Test fallback database connectivity test"""
    print("\nTesting fallback database connectivity...")
    
    orchestrator = AIDeploymentOrchestrator()
    orchestrator.ssh_client = MagicMock()
    orchestrator.log = MagicMock()
    
    # Test successful fallback
    orchestrator.execute_command = MagicMock(return_value=(0, "PostgreSQL 13.3", ""))
    
    result = orchestrator._fallback_database_test()
    assert result == True, "Fallback test should succeed"
    print("✓ Successful fallback test passed")
    
    # Test failed fallback
    orchestrator.execute_command = MagicMock(return_value=(1, "", "psql: could not connect"))
    
    result = orchestrator._fallback_database_test()
    assert result == False, "Fallback test should fail"
    print("✓ Failed fallback test passed")

def test_code_structure():
    """Test that the code structure is correct"""
    print("\nTesting code structure...")
    
    # Check that methods exist
    orchestrator = AIDeploymentOrchestrator()
    
    assert hasattr(orchestrator, '_load_database_credentials'), "Missing _load_database_credentials method"
    assert hasattr(orchestrator, '_validate_database_environment'), "Missing _validate_database_environment method"  
    assert hasattr(orchestrator, '_fallback_database_test'), "Missing _fallback_database_test method"
    assert hasattr(orchestrator, '_test_database_connectivity'), "Missing _test_database_connectivity method"
    assert hasattr(orchestrator, '_diagnose_database_connectivity_issues'), "Missing _diagnose_database_connectivity_issues method"
    
    print("✓ All required methods exist")

def main():
    """Run all tests"""
    print("Running database verification fix tests...\n")
    
    try:
        test_code_structure()
        test_database_credential_loading()
        test_database_environment_validation() 
        test_fallback_database_test()
        
        print("\n✅ All tests passed! Database verification fix is working correctly.")
        print("\nThe fix addresses the following issues:")
        print("- ✓ Loads actual database credentials instead of using hardcoded values")
        print("- ✓ Validates environment variables match actual configuration")
        print("- ✓ Provides multiple fallback testing methods")
        print("- ✓ Enhanced error logging and diagnostics")
        print("- ✓ Properly handles edge cases like missing files and invalid JSON")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())