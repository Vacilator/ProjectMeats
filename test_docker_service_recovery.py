#!/usr/bin/env python3
"""
Test Suite for Enhanced Docker Service Recovery
==============================================

This script tests the enhanced Docker service recovery functionality,
specifically focusing on handling Docker service startup failures.

Usage:
    python test_docker_service_recovery.py
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ai_deployment_orchestrator import AIDeploymentOrchestrator
except ImportError as e:
    print(f"Error importing AI deployment modules: {e}")
    sys.exit(1)


class TestDockerServiceRecovery(unittest.TestCase):
    """Test suite for Docker service recovery enhancements"""
    
    def setUp(self):
        """Setup test environment"""
        import tempfile
        import json
        
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
        test_config = {
            'server': 'test-server',
            'domain': 'test-domain.com',
            'ssh_key_path': '/dev/null'
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        self.orchestrator = AIDeploymentOrchestrator(self.config_file)
        
        # Mock the execute_command method
        self.orchestrator.execute_command = Mock()
        self.orchestrator.log = Mock()
    
    def tearDown(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_docker_service_startup_failure_diagnosis(self):
        """Test diagnosis of Docker service startup failures"""
        
        # Simulate service startup failure with "failed to start daemon" pattern
        error_message = "Job for docker.service failed because the control process exited with error code. failed to start daemon"
        
        # Mock systemctl status response
        status_output = """
        ● docker.service - Docker Application Container Engine
           Loaded: loaded (/lib/systemd/system/docker.service; enabled; vendor preset: enabled)
           Active: failed (Result: exit-code) since Sat 2025-08-31 06:47:25 UTC; 1min ago
        """
        
        # Mock journal output
        journal_output = """
        Aug 31 06:47:25 server systemd[1]: Starting Docker Application Container Engine...
        Aug 31 06:47:25 server dockerd[1234]: failed to start daemon: Error initializing network controller
        Aug 31 06:47:25 server systemd[1]: docker.service: Main process exited, code=exited, status=1/FAILURE
        """
        
        # Setup mock responses
        self.orchestrator.execute_command.side_effect = [
            (1, status_output, ""),  # systemctl status docker
            (0, journal_output, ""), # journalctl -u docker
            (0, "", ""),             # test -d /var/run
            (0, "", ""),             # rm -f /var/run/docker.pid
            (0, "", "")              # rm -f /var/run/docker.sock
        ]
        
        # Test the diagnosis function
        result = self.orchestrator._diagnose_docker_service_startup_failure(error_message)
        
        # Verify that recovery was attempted (due to "failed to start daemon" pattern)
        self.assertTrue(result)
        
        # Verify that diagnostic commands were called
        call_args = [call[0][0] for call in self.orchestrator.execute_command.call_args_list]
        self.assertIn("systemctl status docker", call_args)
        self.assertIn("journalctl -u docker --no-pager -n 10", call_args)
        
    def test_docker_installation_validation(self):
        """Test Docker installation validation"""
        
        # Mock successful Docker installation check
        self.orchestrator.execute_command.side_effect = [
            (0, "/usr/bin/docker", ""),              # which docker
            (0, "Docker version 20.10.21", ""),     # docker --version
            (0, "docker.service unit file", ""),    # systemctl cat docker
            (0, "", ""),                             # test -e /etc/docker/daemon.json
            (0, "", "")                              # test -e /var/lib/docker
        ]
        
        # Test the validation function
        result = self.orchestrator._validate_docker_installation()
        
        # Verify that validation passed
        self.assertTrue(result)
        
        # Verify that all checks were performed
        call_args = [call[0][0] for call in self.orchestrator.execute_command.call_args_list]
        self.assertIn("which docker", call_args)
        self.assertIn("docker --version", call_args)
        self.assertIn("systemctl cat docker", call_args)
    
    def test_docker_installation_validation_failure(self):
        """Test Docker installation validation failure scenarios"""
        
        # Mock Docker binary not found
        self.orchestrator.execute_command.side_effect = [
            (1, "", "which: no docker in PATH")  # which docker fails
        ]
        
        # Test the validation function
        result = self.orchestrator._validate_docker_installation()
        
        # Verify that validation failed
        self.assertFalse(result)
    
    def test_enhanced_docker_service_recovery(self):
        """Test enhanced Docker service recovery with startup failure handling"""
        
        # Mock initial service start failure, then successful restart
        self.orchestrator.execute_command.side_effect = [
            (1, "", "Job for docker.service failed"),      # systemctl start docker (fails)
            (1, "status output", ""),                       # systemctl status docker
            (0, "journal output", ""),                      # journalctl -u docker
            (0, "", ""),                                    # test -d /var/run
            (0, "", ""),                                    # systemctl restart docker (succeeds)
            (0, "active", ""),                              # systemctl is-active docker
            (0, "Docker info output", "")                   # docker info
        ]
        
        # Test the recovery function
        result = self.orchestrator._attempt_docker_service_recovery()
        
        # Verify that recovery was successful
        self.assertTrue(result)
        
        # Verify that restart was attempted after initial failure
        call_args = [call[0][0] for call in self.orchestrator.execute_command.call_args_list]
        self.assertIn("systemctl start docker", call_args)
        self.assertIn("systemctl restart docker", call_args)


if __name__ == '__main__':
    print("Running Enhanced Docker Service Recovery Tests...")
    print("=" * 60)
    
    # Run the tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDockerServiceRecovery)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed! Enhanced Docker service recovery is working correctly.")
    else:
        print("❌ Some tests failed. Please review the implementation.")
        sys.exit(1)