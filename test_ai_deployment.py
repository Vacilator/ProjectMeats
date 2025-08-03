#!/usr/bin/env python3
"""
Test Suite for AI Deployment Orchestrator
=========================================

This script tests the AI deployment system functionality including:
- Configuration loading and validation
- SSH connection handling
- Error detection and recovery
- State management
- Command execution monitoring

Usage:
    python test_ai_deployment.py
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ai_deployment_orchestrator import (
        AIDeploymentOrchestrator, 
        DeploymentState, 
        DeploymentStatus,
        ErrorPattern,
        ErrorSeverity
    )
except ImportError as e:
    print(f"Error importing AI deployment modules: {e}")
    print("Please install dependencies: pip install -r ai_deployment_requirements.txt")
    sys.exit(1)


class TestAIDeploymentOrchestrator(unittest.TestCase):
    """Test suite for AI Deployment Orchestrator"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
        # Create test configuration
        test_config = {
            "ssh": {
                "port": 22,
                "timeout": 30
            },
            "deployment": {
                "max_retries": 2,
                "retry_delay": 1,
                "command_timeout": 60,
                "auto_approve": True
            },
            "logging": {
                "level": "DEBUG"
            },
            "recovery": {
                "auto_recovery": True,
                "backup_on_failure": True
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        self.orchestrator = AIDeploymentOrchestrator(self.config_file)
    
    def tearDown(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_loading(self):
        """Test configuration loading"""
        self.assertIsNotNone(self.orchestrator.config)
        self.assertEqual(self.orchestrator.config['deployment']['max_retries'], 2)
        self.assertEqual(self.orchestrator.config['ssh']['port'], 22)
    
    def test_error_pattern_detection(self):
        """Test error pattern detection"""
        # Test Node.js conflict detection
        output = "nodejs : Conflicts: npm"
        errors = self.orchestrator.detect_errors(output)
        self.assertTrue(len(errors) > 0)
        
        # Find the Node.js error pattern
        nodejs_error = next((e for e in errors if "nodejs" in e.pattern), None)
        self.assertIsNotNone(nodejs_error)
        self.assertEqual(nodejs_error.severity, ErrorSeverity.HIGH)
    
    def test_deployment_state_creation(self):
        """Test deployment state management"""
        server_config = {
            'hostname': 'test.example.com',
            'username': 'test_user'
        }
        
        state = DeploymentState(
            deployment_id="test123",
            status=DeploymentStatus.PENDING,
            current_step=0,
            total_steps=10,
            server_info=server_config
        )
        
        self.assertEqual(state.deployment_id, "test123")
        self.assertEqual(state.status, DeploymentStatus.PENDING)
        self.assertEqual(state.current_step, 0)
    
    def test_state_persistence(self):
        """Test state save and load functionality"""
        # Create test state
        test_state = DeploymentState(
            deployment_id="test456",
            status=DeploymentStatus.RUNNING,
            current_step=3,
            total_steps=10,
            server_info={'hostname': 'test.com'}
        )
        
        self.orchestrator.state = test_state
        
        # Test state saving (mock file operations)
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            self.orchestrator.save_state()
            mock_open.assert_called_once()
    
    @patch('paramiko.SSHClient')
    def test_ssh_connection(self, mock_ssh_client):
        """Test SSH connection functionality"""
        # Mock SSH client
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        
        # Test successful connection
        result = self.orchestrator.connect_to_server(
            hostname="test.example.com",
            username="testuser"
        )
        
        # Verify connection attempt
        mock_client.connect.assert_called_once()
    
    def test_command_execution_simulation(self):
        """Test command execution simulation"""
        # Mock SSH client for command execution
        mock_ssh = Mock()
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        
        # Configure mock return values
        mock_stdout.readline.side_effect = ["Command output line 1\n", "Command output line 2\n", ""]
        mock_stderr.readline.side_effect = [""]
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        self.orchestrator.ssh_client = mock_ssh
        
        # Test command execution
        exit_code, stdout, stderr = self.orchestrator.execute_command("echo 'test'")
        
        # Verify command was executed
        mock_ssh.exec_command.assert_called_once_with("echo 'test'", timeout=60)
    
    def test_deployment_step_validation(self):
        """Test deployment step validation"""
        # Check that all deployment steps have corresponding functions
        for step_name, step_description in self.orchestrator.deployment_steps:
            function_name = f"deploy_{step_name}"
            self.assertTrue(
                hasattr(self.orchestrator, function_name),
                f"Missing deployment function: {function_name}"
            )
    
    def test_recovery_functions(self):
        """Test error recovery functions"""
        # Test that recovery functions exist
        recovery_functions = [
            'fix_nodejs_conflicts',
            'update_package_lists', 
            'fix_permissions',
            'restart_database_service',
            'kill_conflicting_processes',
            'restart_services',
            'cleanup_disk_space',
            'fix_dns_issues',
            'retry_ssl_setup',
            'fix_npm_permissions'
        ]
        
        for func_name in recovery_functions:
            self.assertTrue(
                hasattr(self.orchestrator, func_name),
                f"Missing recovery function: {func_name}"
            )
    
    def test_error_severity_classification(self):
        """Test error severity classification"""
        # Test different severity levels
        critical_pattern = ErrorPattern(
            pattern="disk space",
            severity=ErrorSeverity.CRITICAL,
            recovery_function="cleanup_disk_space",
            description="Disk space issue"
        )
        
        self.assertEqual(critical_pattern.severity, ErrorSeverity.CRITICAL)
        
        medium_pattern = ErrorPattern(
            pattern="Port.*already in use",
            severity=ErrorSeverity.MEDIUM,
            recovery_function="kill_conflicting_processes",
            description="Port conflict"
        )
        
        self.assertEqual(medium_pattern.severity, ErrorSeverity.MEDIUM)
    
    def test_logging_functionality(self):
        """Test logging functionality"""
        # Test different log levels
        with patch('builtins.print') as mock_print:
            self.orchestrator.log("Test message", "INFO")
            mock_print.assert_called()
            
            self.orchestrator.log("Success message", "SUCCESS")
            mock_print.assert_called()
            
            self.orchestrator.log("Error message", "ERROR")
            mock_print.assert_called()


class TestDeploymentIntegration(unittest.TestCase):
    """Integration tests for deployment functionality"""
    
    def setUp(self):
        """Setup integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Cleanup integration test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_deployment_template_generation(self):
        """Test deployment template generation"""
        from setup_ai_deployment import AIDeploymentSetup
        
        setup = AIDeploymentSetup()
        setup.project_root = Path(self.temp_dir)
        
        # Test template generation
        setup.generate_deployment_templates()
        
        templates_dir = Path(self.temp_dir) / "deployment_templates"
        self.assertTrue(templates_dir.exists())
        
        quick_template = templates_dir / "quick_deployment.json"
        full_template = templates_dir / "full_deployment.json"
        
        self.assertTrue(quick_template.exists())
        self.assertTrue(full_template.exists())
        
        # Validate template content
        with open(quick_template) as f:
            quick_data = json.load(f)
            self.assertIn("name", quick_data)
            self.assertIn("steps", quick_data)
            self.assertIn("config", quick_data)
    
    def test_configuration_validation(self):
        """Test configuration file validation"""
        # Create test configuration
        config_data = {
            "version": "1.0",
            "ssh": {
                "port": 22,
                "timeout": 30
            },
            "deployment": {
                "max_retries": 3,
                "auto_recovery": True
            }
        }
        
        config_file = os.path.join(self.temp_dir, "test_config.json")
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        # Test configuration loading
        orchestrator = AIDeploymentOrchestrator(config_file)
        self.assertIsNotNone(orchestrator.config)
        self.assertEqual(orchestrator.config['ssh']['port'], 22)


def run_integration_tests():
    """Run integration tests that require network access"""
    print("Running integration tests (requires network access)...")
    
    # Test GitHub connectivity
    try:
        import urllib.request
        response = urllib.request.urlopen("https://github.com/Vacilator/ProjectMeats", timeout=10)
        print("[OK] GitHub connectivity test passed")
    except Exception as e:
        print(f"[FAIL] GitHub connectivity test failed: {e}")
    
    # Test SSH key generation (if ssh-keygen is available)
    try:
        import subprocess
        result = subprocess.run(["ssh-keygen", "-t", "ed25519", "-f", "/tmp/test_key", "-N", ""], 
                               capture_output=True, timeout=10)
        if result.returncode == 0:
            print("[OK] SSH key generation test passed")
            # Cleanup
            os.remove("/tmp/test_key")
            os.remove("/tmp/test_key.pub")
        else:
            print("[FAIL] SSH key generation test failed")
    except Exception as e:
        print(f"[FAIL] SSH key generation test failed: {e}")


def main():
    """Main test runner"""
    print("[TEST] AI Deployment Orchestrator Test Suite")
    print("=" * 50)
    
    # Run unit tests
    print("\nRunning unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration tests
    print("\nRunning integration tests...")
    run_integration_tests()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
    
    # Provide usage examples
    print("\n[INFO] Usage Examples:")
    print("python ai_deployment_orchestrator.py --test-connection --server example.com")
    print("python setup_ai_deployment.py")
    print("./ai_deploy.sh --interactive")


if __name__ == "__main__":
    main()