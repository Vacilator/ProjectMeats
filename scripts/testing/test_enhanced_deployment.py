#!/usr/bin/env python3
"""
Test suite for enhanced AI Deployment Orchestrator
==================================================

This test suite validates the major enhancements made to the AI deployment
orchestrator, including GitHub integration, domain accessibility checks,
and deployment verification logic.

Run with: python test_enhanced_deployment.py
"""

import os
import sys
import json
import time
import unittest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ai_deployment_orchestrator import AIDeploymentOrchestrator, DeploymentStatus, DeploymentState
    from github_integration import GitHubIntegration, DeploymentLogManager
    from server_initialization import ServerInitializer
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required modules are in the same directory")
    sys.exit(1)


class TestEnhancedDeploymentOrchestrator(unittest.TestCase):
    """Test enhanced deployment orchestrator functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create test config
        self.test_config = {
            "ssh": {"port": 22, "timeout": 30},
            "deployment": {
                "max_retries": 2,
                "retry_delay": 1,
                "command_timeout": 10,
                "auto_approve": True,
                "prepare_golden_image": False,
                "auto_cleanup": True
            },
            "github": {"user": "test_user", "token": "test_token"},
            "recovery": {"auto_recovery": True},
            "logging": {"level": "INFO"},
            "domain": "test-domain.com"
        }
        
        with open("ai_deployment_config.json", 'w') as f:
            json.dump(self.test_config, f)
        
        self.orchestrator = AIDeploymentOrchestrator()
        
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_initialization_with_github_integration(self):
        """Test that GitHub integration is properly initialized"""
        # Mock environment variables
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('ai_deployment_orchestrator.GitHubIntegration') as mock_github:
                orchestrator = AIDeploymentOrchestrator()
                
                # Should attempt to initialize GitHub integration
                self.assertIsNotNone(orchestrator.github_integration)
    
    def test_deployment_state_tracking(self):
        """Test enhanced deployment state tracking"""
        deployment_id = "test123"
        server_info = {"hostname": "test.com", "domain": "test-domain.com"}
        
        state = DeploymentState(
            deployment_id=deployment_id,
            status=DeploymentStatus.RUNNING,
            current_step=1,
            total_steps=12,  # Updated for new step count
            server_info=server_info
        )
        
        # Test new state fields
        self.assertFalse(state.domain_accessible)
        self.assertFalse(state.services_healthy)
        self.assertFalse(state.critical_checks_passed)
        
        # Test state update
        state.domain_accessible = True
        state.services_healthy = True
        state.critical_checks_passed = True
        
        self.assertTrue(state.domain_accessible)
        self.assertTrue(state.services_healthy)
        self.assertTrue(state.critical_checks_passed)
    
    @patch('ai_deployment_orchestrator.paramiko.SSHClient')
    def test_deployment_verification_logic(self, mock_ssh):
        """Test the enhanced deployment verification logic"""
        # Mock SSH client
        mock_ssh_instance = Mock()
        mock_ssh.return_value = mock_ssh_instance
        
        # Mock successful command execution
        def mock_execute_command(cmd):
            if "systemctl is-active" in cmd:
                return (0, "active", "")
            elif "curl" in cmd and "health" in cmd:
                return (0, "healthy", "")
            elif "nslookup" in cmd:
                return (0, "Address: 1.2.3.4", "")
            elif "nginx -T" in cmd:
                return (0, "server_name test-domain.com", "")
            else:
                return (0, "success", "")
        
        self.orchestrator.ssh_client = mock_ssh_instance
        self.orchestrator.execute_command = mock_execute_command
        
        # Test verification methods
        self.assertTrue(self.orchestrator._verify_services_health())
        self.assertTrue(self.orchestrator._verify_domain_accessibility())
        self.assertTrue(self.orchestrator._verify_application_endpoints())
        self.assertTrue(self.orchestrator._verify_deployment_success())
    
    @patch('ai_deployment_orchestrator.paramiko.SSHClient')
    def test_deployment_failure_detection(self, mock_ssh):
        """Test that deployment failures are properly detected"""
        # Mock SSH client
        mock_ssh_instance = Mock()
        mock_ssh.return_value = mock_ssh_instance
        
        # Mock failed command execution for domain accessibility
        def mock_execute_command_failed(cmd):
            if "curl" in cmd and "health" in cmd:
                return (1, "EXTERNAL_ACCESS_FAILED", "Connection refused")
            elif "systemctl is-active" in cmd:
                return (0, "active", "")
            else:
                return (0, "success", "")
        
        self.orchestrator.ssh_client = mock_ssh_instance
        self.orchestrator.execute_command = mock_execute_command_failed
        
        # Domain accessibility should fail
        self.assertFalse(self.orchestrator._verify_domain_accessibility())
        
        # Overall verification should fail
        self.assertFalse(self.orchestrator._verify_deployment_success())
    
    def test_github_log_manager_initialization(self):
        """Test GitHub log manager initialization"""
        with patch('ai_deployment_orchestrator.DeploymentLogManager') as mock_log_manager:
            deployment_id = "test123"
            server_config = {"hostname": "test.com", "domain": "test-domain.com"}
            
            # Mock the deployment state creation
            with patch.object(self.orchestrator, 'save_state'):
                with patch.object(self.orchestrator, 'connect_to_server', return_value=False):
                    # This should initialize GitHub log manager
                    self.orchestrator.run_deployment(server_config)
                    
                    # Should have attempted to create log manager
                    self.assertIsNotNone(self.orchestrator.github_log_manager)
    
    def test_enhanced_logging(self):
        """Test enhanced logging with GitHub integration"""
        # Create a mock GitHub log manager
        mock_github_manager = Mock()
        self.orchestrator.github_log_manager = mock_github_manager
        
        # Create deployment state
        self.orchestrator.state = DeploymentState(
            deployment_id="test123",
            status=DeploymentStatus.RUNNING,
            current_step=1,
            total_steps=12,
            server_info={"hostname": "test.com"}
        )
        
        # Test logging
        self.orchestrator.log("Test error message", "ERROR")
        
        # Should have called add_log on GitHub manager
        mock_github_manager.add_log.assert_called_once()
    
    def test_domain_accessibility_check_step(self):
        """Test the new domain accessibility check deployment step"""
        # Mock SSH connection
        mock_ssh_instance = Mock()
        self.orchestrator.ssh_client = mock_ssh_instance
        
        # Mock successful domain accessibility
        def mock_execute_command_success(cmd):
            if "curl" in cmd and "health" in cmd:
                return (0, "healthy", "")
            elif "curl -I" in cmd:
                return (0, "200 OK", "")
            elif "nslookup" in cmd:
                return (0, "Address: 1.2.3.4", "")
            else:
                return (0, "success", "")
        
        self.orchestrator.execute_command = mock_execute_command_success
        
        # Test the domain accessibility check step
        result = self.orchestrator.deploy_domain_accessibility_check()
        self.assertTrue(result)
        
        # Test with failed domain accessibility
        def mock_execute_command_failed(cmd):
            if "curl" in cmd and "health" in cmd:
                return (1, "FAILED", "Connection refused")
            elif "curl -I" in cmd:
                return (1, "", "Connection refused")
            elif "nslookup" in cmd:
                return (1, "", "NXDOMAIN")
            else:
                return (0, "success", "")
        
        self.orchestrator.execute_command = mock_execute_command_failed
        
        result = self.orchestrator.deploy_domain_accessibility_check()
        self.assertFalse(result)
    
    def test_deployment_step_count(self):
        """Test that deployment step count is updated correctly"""
        # Should have 12 steps now (added domain_accessibility_check)
        self.assertEqual(len(self.orchestrator.deployment_steps), 12)
        
        # Last step should be domain accessibility check
        last_step = self.orchestrator.deployment_steps[-1]
        self.assertEqual(last_step[0], "domain_accessibility_check")
    
    def test_failure_handling_with_github_integration(self):
        """Test deployment failure handling with GitHub integration"""
        # Mock GitHub log manager
        mock_github_manager = Mock()
        self.orchestrator.github_log_manager = mock_github_manager
        
        # Mock deployment state
        self.orchestrator.state = DeploymentState(
            deployment_id="test123",
            status=DeploymentStatus.FAILED,
            current_step=5,
            total_steps=12,
            server_info={"hostname": "test.com", "domain": "test-domain.com"}
        )
        
        # Test failure handling
        self.orchestrator._handle_deployment_failure("test_step", "Test error message")
        
        # Should have updated GitHub status
        mock_github_manager.update_status.assert_called_with("failure")
        
        # Should have created failure issue
        mock_github_manager.create_failure_issue.assert_called_once()
        
        # Should have posted final logs
        mock_github_manager.post_final_logs.assert_called_with("failed")


class TestGitHubIntegration(unittest.TestCase):
    """Test GitHub integration functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('github_integration.requests.Session')
    def test_github_integration_initialization(self, mock_session):
        """Test GitHub integration initialization"""
        # Mock successful authentication
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "test_user"}
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        github = GitHubIntegration(token="test_token", repo="test/repo")
        
        self.assertEqual(github.owner, "test")
        self.assertEqual(github.repo, "repo")
        self.assertEqual(github.token, "test_token")
    
    @patch('github_integration.requests.Session')
    def test_create_deployment_issue(self, mock_session):
        """Test creating deployment failure issues"""
        # Mock successful issue creation
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"number": 123, "html_url": "https://github.com/test/repo/issues/123"}
        
        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session_instance.get.return_value = Mock(status_code=200, json=lambda: {"login": "test"})
        mock_session.return_value = mock_session_instance
        
        github = GitHubIntegration(token="test_token", repo="test/repo")
        
        error_details = {
            "failed_step": "test_step",
            "error_message": "Test error",
            "server_info": {"hostname": "test.com", "domain": "test-domain.com"},
            "auto_recovery": True
        }
        
        issue_number = github.create_deployment_issue("test123", error_details)
        
        self.assertEqual(issue_number, 123)
        mock_session_instance.post.assert_called_once()
    
    @patch('github_integration.requests.Session')
    def test_deployment_log_manager(self, mock_session):
        """Test deployment log manager functionality"""
        # Mock GitHub session
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = Mock(status_code=200, json=lambda: {"login": "test"})
        mock_session_instance.post.return_value = Mock(status_code=201, json=lambda: {"html_url": "test_gist"})
        mock_session.return_value = mock_session_instance
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            log_manager = DeploymentLogManager("test123")
            
            # Add some logs
            log_manager.add_log("INFO", "Test info message")
            log_manager.add_log("ERROR", "Test error message")
            
            self.assertEqual(len(log_manager.logs), 2)
            
            # Test posting logs
            result = log_manager.post_final_logs("success")
            self.assertTrue(result)


class TestServerInitializer(unittest.TestCase):
    """Test server initialization functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_ssh = Mock()
        self.mock_logger = Mock()
        self.initializer = ServerInitializer(self.mock_ssh, self.mock_logger)
    
    def test_initialization(self):
        """Test server initializer initialization"""
        self.assertEqual(self.initializer.ssh_client, self.mock_ssh)
        self.assertEqual(self.initializer.logger, self.mock_logger)
        self.assertEqual(self.initializer.installed_packages, [])
        self.assertEqual(self.initializer.created_services, [])
    
    def test_execute_command(self):
        """Test command execution through SSH"""
        # Mock SSH command execution
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stdout.read.return_value = b"success output"
        mock_stderr.read.return_value = b""
        
        self.mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        exit_code, stdout, stderr = self.initializer.execute_command("test command")
        
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "success output")
        self.assertEqual(stderr, "")
    
    def test_golden_image_preparation_steps(self):
        """Test that golden image preparation includes all required steps"""
        # Mock successful command execution
        def mock_execute_command(cmd):
            return (0, "success", "")
        
        self.initializer.execute_command = mock_execute_command
        
        # Test individual preparation steps
        self.assertTrue(self.initializer._system_cleanup_and_update())
        self.assertTrue(self.initializer._remove_conflicting_software())
        self.assertTrue(self.initializer._security_hardening())
        self.assertTrue(self.initializer._performance_optimization())
        self.assertTrue(self.initializer._install_base_dependencies())
        self.assertTrue(self.initializer._configure_base_services())
        self.assertTrue(self.initializer._setup_deployment_environment())
    
    def test_cleanup_failed_deployment(self):
        """Test cleanup of failed deployments"""
        # Mock successful command execution
        def mock_execute_command(cmd):
            if "curl" in cmd and "health" in cmd:
                return (0, "healthy", "")
            return (0, "success", "")
        
        self.initializer.execute_command = mock_execute_command
        
        result = self.initializer.cleanup_failed_deployment()
        self.assertTrue(result)


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios between components"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create test config
        test_config = {
            "ssh": {"port": 22, "timeout": 30},
            "deployment": {
                "max_retries": 1,
                "retry_delay": 1,
                "auto_cleanup": True,
                "prepare_golden_image": False
            },
            "recovery": {"auto_recovery": True},
            "logging": {"level": "INFO"},
            "domain": "test-domain.com"
        }
        
        with open("ai_deployment_config.json", 'w') as f:
            json.dump(test_config, f)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('ai_deployment_orchestrator.paramiko.SSHClient')
    @patch('ai_deployment_orchestrator.DeploymentLogManager')
    def test_end_to_end_success_scenario(self, mock_log_manager, mock_ssh):
        """Test end-to-end successful deployment scenario"""
        # Setup mocks
        mock_ssh_instance = Mock()
        mock_ssh.return_value = mock_ssh_instance
        
        mock_log_manager_instance = Mock()
        mock_log_manager.return_value = mock_log_manager_instance
        
        # Mock all commands to succeed
        def mock_execute_command(cmd):
            if "systemctl is-active" in cmd:
                return (0, "active", "")
            elif "curl" in cmd and "health" in cmd:
                return (0, "healthy", "")
            elif "nslookup" in cmd:
                return (0, "Address: 1.2.3.4", "")
            elif "nginx -T" in cmd:
                return (0, "server_name test-domain.com", "")
            else:
                return (0, "success", "")
        
        orchestrator = AIDeploymentOrchestrator()
        orchestrator.execute_command = mock_execute_command
        
        # Mock all deployment steps to succeed
        for step_name, _ in orchestrator.deployment_steps:
            setattr(orchestrator, f"deploy_{step_name}", lambda: True)
        
        server_config = {
            "hostname": "test.com",
            "domain": "test-domain.com",
            "username": "root"
        }
        
        # Mock connection
        with patch.object(orchestrator, 'connect_to_server', return_value=True):
            with patch.object(orchestrator, 'disconnect_from_server'):
                result = orchestrator.run_deployment(server_config)
        
        self.assertTrue(result)
        self.assertEqual(orchestrator.state.status, DeploymentStatus.SUCCESS)
        self.assertTrue(orchestrator.state.critical_checks_passed)
    
    @patch('ai_deployment_orchestrator.paramiko.SSHClient')
    @patch('ai_deployment_orchestrator.DeploymentLogManager')
    def test_end_to_end_failure_scenario(self, mock_log_manager, mock_ssh):
        """Test end-to-end deployment failure scenario"""
        # Setup mocks
        mock_ssh_instance = Mock()
        mock_ssh.return_value = mock_ssh_instance
        
        mock_log_manager_instance = Mock()
        mock_log_manager.return_value = mock_log_manager_instance
        
        # Mock domain accessibility to fail
        def mock_execute_command(cmd):
            if "curl" in cmd and "health" in cmd:
                return (1, "EXTERNAL_ACCESS_FAILED", "Connection refused")
            elif "systemctl is-active" in cmd:
                return (0, "active", "")
            else:
                return (0, "success", "")
        
        orchestrator = AIDeploymentOrchestrator()
        orchestrator.execute_command = mock_execute_command
        
        # Mock most deployment steps to succeed, but domain check to fail
        for step_name, _ in orchestrator.deployment_steps[:-1]:  # All except last step
            setattr(orchestrator, f"deploy_{step_name}", lambda: True)
        
        server_config = {
            "hostname": "test.com", 
            "domain": "test-domain.com",
            "username": "root"
        }
        
        # Mock connection
        with patch.object(orchestrator, 'connect_to_server', return_value=True):
            with patch.object(orchestrator, 'disconnect_from_server'):
                result = orchestrator.run_deployment(server_config)
        
        self.assertFalse(result)
        self.assertEqual(orchestrator.state.status, DeploymentStatus.FAILED)
        
        # Should have called failure handling
        mock_log_manager_instance.update_status.assert_called_with("failure")


if __name__ == '__main__':
    # Run tests
    print("Running Enhanced AI Deployment Orchestrator Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEnhancedDeploymentOrchestrator,
        TestGitHubIntegration,
        TestServerInitializer,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestClass(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)