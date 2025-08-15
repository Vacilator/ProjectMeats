#!/usr/bin/env python3
"""
Test script to verify logging fixes work correctly.
This script tests the deployment orchestrator logging improvements.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_logging_initialization():
    """Test that logging initialization only happens once"""
    print("🧪 Testing logging initialization fixes...")
    
    # Import after adding to path
    from ai_deployment_orchestrator import AIDeploymentOrchestrator
    
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            "logging": {"level": "INFO"},
            "deployment": {"max_retries": 1},
            "recovery": {"auto_recovery": False}
        }
        json.dump(config, f)
        config_file = f.name
    
    try:
        # Create orchestrator instance
        orchestrator = AIDeploymentOrchestrator(config_file)
        
        # Check that logging was initialized
        assert orchestrator._logging_initialized == True, "Logging should be initialized"
        
        # Try to initialize logging again - should be skipped
        initial_logger = orchestrator.logger
        orchestrator._setup_logging()
        
        # Logger should be the same instance
        assert orchestrator.logger is initial_logger, "Logger should not be recreated"
        
        print("✅ Logging initialization test passed")
        
    finally:
        os.unlink(config_file)

def test_error_detection_deduplication():
    """Test that error detection deduplication works"""
    print("🧪 Testing error detection deduplication...")
    
    from ai_deployment_orchestrator import AIDeploymentOrchestrator
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            "logging": {"level": "INFO"},
            "deployment": {"max_retries": 1},
            "recovery": {"auto_recovery": False}
        }
        json.dump(config, f)
        config_file = f.name
    
    try:
        orchestrator = AIDeploymentOrchestrator(config_file)
        
        # Test output that should NOT trigger false positives
        normal_output = """
        Reading package lists...
        Building dependency tree...
        The following NEW packages will be installed:
          python3 python3-pip nginx git curl
        0 upgraded, 5 newly installed, 0 to remove and 0 not upgraded.
        Need to get 2,342 kB of archives.
        After this operation, 9,876 kB of additional disk space will be used.
        """
        
        errors = orchestrator.detect_errors(normal_output)
        assert len(errors) == 0, f"Normal output should not trigger errors, but got: {[e.description for e in errors]}"
        
        # Test output that SHOULD trigger detection (but only once)
        error_output = "npm ERR! conflict: Cannot resolve dependency conflicts"
        
        errors1 = orchestrator.detect_errors(error_output)
        assert len(errors1) == 1, "Error output should trigger exactly one error"
        
        # Same error output should not trigger again due to deduplication
        errors2 = orchestrator.detect_errors(error_output)
        assert len(errors2) == 0, "Duplicate error should be deduplicated"
        
        print("✅ Error detection deduplication test passed")
        
    finally:
        os.unlink(config_file)

def test_improved_error_patterns():
    """Test that improved error patterns are more specific"""
    print("🧪 Testing improved error pattern specificity...")
    
    from ai_deployment_orchestrator import AIDeploymentOrchestrator
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            "logging": {"level": "INFO"},
            "deployment": {"max_retries": 1},
            "recovery": {"auto_recovery": False}
        }
        json.dump(config, f)
        config_file = f.name
    
    try:
        orchestrator = AIDeploymentOrchestrator(config_file)
        
        # Test cases that should NOT trigger false positives
        false_positive_cases = [
            "Setting up nodejs (18.17.1-1nodesource1) ...",  # Normal nodejs install
            "Building dependency tree...",  # Normal apt output
            "Permission granted for user projectmeats",  # Normal permission message
            "Listening on port 8000",  # Normal port usage
        ]
        
        for case in false_positive_cases:
            errors = orchestrator.detect_errors(case)
            assert len(errors) == 0, f"Should not trigger error for: {case}, but got: {[e.description for e in errors]}"
        
        # Test cases that SHOULD trigger detection
        true_positive_cases = [
            ("npm ERR! conflict: Cannot resolve dependencies", "Node.js package conflicts detected"),
            ("E: Unable to locate package fake-package\nPackage not found", "Package repository needs update"),
            ("Permission denied /opt/projectmeats", "Permission issues detected"),
            ("bind: Address already in use :80", "Port conflicts detected"),
        ]
        
        for case, expected_desc in true_positive_cases:
            # Reset reported errors for this test
            orchestrator._reported_errors.clear()
            errors = orchestrator.detect_errors(case)
            assert len(errors) >= 1, f"Should trigger error for: {case}"
            assert any(expected_desc in error.description for error in errors), f"Should detect '{expected_desc}' for: {case}"
        
        print("✅ Improved error pattern specificity test passed")
        
    finally:
        os.unlink(config_file)

def main():
    """Run all logging fix tests"""
    print("🚀 Running logging fixes tests...\n")
    
    try:
        test_logging_initialization()
        test_error_detection_deduplication()
        test_improved_error_patterns()
        
        print("\n🎉 All tests passed! Logging fixes are working correctly.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())