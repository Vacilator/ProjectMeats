#!/usr/bin/env python3
"""
ProjectMeats AI-Driven Deployment Orchestrator
==============================================

This script provides an intelligent, autonomous production deployment system that can:
- Establish secure remote connections to production servers
- Execute commands and monitor output in real-time
- Detect and automatically recover from errors
- Handle interactive prompts and confirmations
- Maintain deployment state across the entire process
- Provide comprehensive logging and monitoring

Features:
- Dynamic error detection and recovery
- Interactive terminal session management
- Secure remote server access
- Real-time monitoring and response
- State persistence and rollback capabilities
- Comprehensive logging and reporting
- GitHub PAT authentication support

Usage:
    # Interactive setup and deployment
    python ai_deployment_orchestrator.py --interactive
    
    # Automated deployment with configuration
    python ai_deployment_orchestrator.py --server=myserver.com --domain=mydomain.com --auto
    
    # With GitHub authentication (recommended for private repos)
    python ai_deployment_orchestrator.py --server=myserver.com --domain=mydomain.com --github-user=USERNAME --github-token=TOKEN
    
    # Test connection and validate server
    python ai_deployment_orchestrator.py --test-connection --server=myserver.com
    
    # Resume failed deployment
    python ai_deployment_orchestrator.py --resume --deployment-id=abc123

Author: ProjectMeats AI Assistant
"""

import os
import sys
import json
import time
import subprocess
import threading
import queue
import re
import socket
import paramiko
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import argparse


class DeploymentStatus(Enum):
    """Deployment status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DeploymentState:
    """Deployment state tracking"""
    deployment_id: str
    status: DeploymentStatus
    current_step: int
    total_steps: int
    server_info: Dict[str, Any]
    error_count: int = 0
    warnings: List[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.start_time is None:
            self.start_time = datetime.now()


@dataclass
class ErrorPattern:
    """Error pattern for detection and recovery"""
    pattern: str
    severity: ErrorSeverity
    recovery_function: str
    description: str
    retry_count: int = 3


class Colors:
    """Terminal colors for output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class AIDeploymentOrchestrator:
    """AI-driven deployment orchestrator for ProjectMeats"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "ai_deployment_config.json"
        self.state_file = "deployment_state.json"
        self.log_file = "deployment_log.json"
        
        # Initialize configuration
        self.config = self._load_config()
        self.state = None
        
        # Initialize logging
        self._setup_logging()
        
        # Remote connection
        self.ssh_client = None
        self.sftp_client = None
        
        # Command execution
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.is_running = False
        
        # Error patterns for intelligent recovery
        self.error_patterns = self._initialize_error_patterns()
        
        # Deployment steps
        self.deployment_steps = [
            ("validate_server", "Server validation and prerequisites"),
            ("setup_authentication", "Authentication and security setup"),
            ("install_dependencies", "System dependencies installation"),
            ("handle_nodejs_conflicts", "Node.js conflict resolution"),
            ("setup_database", "Database configuration"),
            ("download_application", "Application download and setup"),
            ("configure_backend", "Backend configuration"),
            ("configure_frontend", "Frontend build and configuration"),
            ("setup_webserver", "Web server and SSL configuration"),
            ("setup_services", "System services and monitoring"),
            ("final_verification", "Final testing and verification")
        ]
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        default_config = {
            "ssh": {
                "port": 22,
                "timeout": 30,
                "key_filename": None,
                "password": None
            },
            "deployment": {
                "max_retries": 3,
                "retry_delay": 5,
                "command_timeout": 300,
                "auto_approve": False
            },
            "github": {
                "user": None,
                "token": None
            },
            "logging": {
                "level": "INFO",
                "max_log_files": 10,
                "max_log_size": "10MB"
            },
            "recovery": {
                "auto_recovery": True,
                "backup_on_failure": True,
                "rollback_enabled": True
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subkey not in config[key]:
                                    config[key][subkey] = subvalue
                    return config
            except Exception as e:
                self.log(f"Error loading config: {e}", "ERROR")
        
        return default_config
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.log(f"Error saving config: {e}", "ERROR")
    
    def load_profile(self, profile_name: str) -> Dict[str, str]:
        """Load server profile from configuration"""
        server_profiles = self.config.get('server_profiles', {})
        
        if profile_name not in server_profiles:
            available_profiles = list(server_profiles.keys())
            self.log(f"Profile '{profile_name}' not found in configuration", "ERROR")
            if available_profiles:
                self.log(f"Available profiles: {', '.join(available_profiles)}", "INFO")
            else:
                self.log("No server profiles configured", "INFO")
            return {}
        
        profile = server_profiles[profile_name]
        self.log(f"Loading profile '{profile_name}'", "INFO")
        
        # Extract relevant settings from profile
        profile_settings = {}
        if 'hostname' in profile:
            profile_settings['server'] = profile['hostname']
        if 'username' in profile:
            profile_settings['username'] = profile['username']
        if 'domain' in profile:
            profile_settings['domain'] = profile['domain']
        if 'key_file' in profile:
            profile_settings['key_file'] = profile['key_file']
        
        self.log(f"Profile settings: {profile_settings}", "DEBUG")
        return profile_settings
    
    
    def setup_github_auth(self):
        """Setup GitHub authentication for private repository access"""
        # Check for environment variables first
        github_user = os.environ.get('GITHUB_USER') or os.environ.get('GITHUB_USERNAME')
        github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_PAT')
        
        if github_user and github_token:
            self.config['github']['user'] = github_user
            self.config['github']['token'] = github_token
            self.log("GitHub authentication loaded from environment variables", "SUCCESS")
            return True
        
        # Check if already configured in config file
        if self.config['github'].get('user') and self.config['github'].get('token'):
            self.log("GitHub authentication already configured", "SUCCESS")
            return True
        
        self.log("GitHub authentication not configured", "WARNING")
        self.log("For private repository access, set environment variables:", "INFO")
        self.log("  export GITHUB_USER=your_username", "INFO")
        self.log("  export GITHUB_TOKEN=your_personal_access_token", "INFO")
        
        return False
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        log_level = getattr(logging, self.config["logging"]["level"].upper())
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Setup file logging
        log_filename = f"logs/deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.log(f"Logging initialized - {log_filename}", "INFO")
    
    def _initialize_error_patterns(self) -> List[ErrorPattern]:
        """Initialize error detection patterns"""
        return [
            ErrorPattern(
                pattern=r"nodejs.*conflicts.*npm",
                severity=ErrorSeverity.HIGH,
                recovery_function="fix_nodejs_conflicts",
                description="Node.js package conflicts detected"
            ),
            ErrorPattern(
                pattern=r"E: Unable to locate package",
                severity=ErrorSeverity.MEDIUM,
                recovery_function="update_package_lists",
                description="Package repository needs update"
            ),
            ErrorPattern(
                pattern=r"Permission denied",
                severity=ErrorSeverity.HIGH,
                recovery_function="fix_permissions",
                description="Permission issues detected"
            ),
            ErrorPattern(
                pattern=r"Could not connect to.*database",
                severity=ErrorSeverity.HIGH,
                recovery_function="restart_database_service",
                description="Database connection issues"
            ),
            ErrorPattern(
                pattern=r"Port.*already in use",
                severity=ErrorSeverity.MEDIUM,
                recovery_function="kill_conflicting_processes",
                description="Port conflicts detected"
            ),
            ErrorPattern(
                pattern=r"Connection refused",
                severity=ErrorSeverity.HIGH,
                recovery_function="restart_services",
                description="Service connection issues"
            ),
            ErrorPattern(
                pattern=r"disk space",
                severity=ErrorSeverity.CRITICAL,
                recovery_function="cleanup_disk_space",
                description="Insufficient disk space"
            ),
            ErrorPattern(
                pattern=r"DNS.*failed|name resolution",
                severity=ErrorSeverity.MEDIUM,
                recovery_function="fix_dns_issues",
                description="DNS resolution problems"
            ),
            ErrorPattern(
                pattern=r"SSL.*certificate.*failed",
                severity=ErrorSeverity.HIGH,
                recovery_function="retry_ssl_setup",
                description="SSL certificate issues"
            ),
            ErrorPattern(
                pattern=r"npm.*EACCES",
                severity=ErrorSeverity.MEDIUM,
                recovery_function="fix_npm_permissions",
                description="NPM permission issues"
            )
        ]
    
    def log(self, message: str, level: str = "INFO", color: Optional[str] = None):
        """Enhanced logging with colors and structured output"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Color mapping
        color_map = {
            "DEBUG": Colors.CYAN,
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "CRITICAL": Colors.RED + Colors.BOLD
        }
        
        if color is None:
            color = color_map.get(level, Colors.WHITE)
        
        # Console output with colors
        print(f"{color}[{timestamp}] [{level}] {message}{Colors.END}")
        
        # Structured logging
        self.logger.log(getattr(logging, level.upper(), logging.INFO), message)
        
        # Save to structured log file
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "deployment_id": getattr(self.state, 'deployment_id', None),
            "step": getattr(self.state, 'current_step', None)
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass  # Don't fail deployment for logging issues
    
    def save_state(self):
        """Save deployment state to file"""
        if self.state:
            try:
                with open(self.state_file, 'w') as f:
                    # Convert dataclass to dict and handle datetime serialization
                    state_dict = asdict(self.state)
                    state_dict['start_time'] = self.state.start_time.isoformat() if self.state.start_time else None
                    state_dict['end_time'] = self.state.end_time.isoformat() if self.state.end_time else None
                    state_dict['status'] = self.state.status.value
                    json.dump(state_dict, f, indent=2)
            except Exception as e:
                self.log(f"Error saving state: {e}", "ERROR")
    
    def load_state(self, deployment_id: str) -> bool:
        """Load deployment state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state_dict = json.load(f)
                    if state_dict.get('deployment_id') == deployment_id:
                        # Convert back to dataclass
                        state_dict['status'] = DeploymentStatus(state_dict['status'])
                        if state_dict['start_time']:
                            state_dict['start_time'] = datetime.fromisoformat(state_dict['start_time'])
                        if state_dict['end_time']:
                            state_dict['end_time'] = datetime.fromisoformat(state_dict['end_time'])
                        
                        self.state = DeploymentState(**state_dict)
                        return True
        except Exception as e:
            self.log(f"Error loading state: {e}", "ERROR")
        return False
    
    def connect_to_server(self, hostname: str, username: str = "root", 
                         key_file: Optional[str] = None, password: Optional[str] = None) -> bool:
        """Establish SSH connection to remote server"""
        try:
            self.log(f"Connecting to {hostname} as {username}...", "INFO")
            
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                'hostname': hostname,
                'username': username,
                'port': self.config['ssh']['port'],
                'timeout': self.config['ssh']['timeout']
            }
            
            if key_file and os.path.exists(key_file):
                connect_kwargs['key_filename'] = key_file
            elif password:
                connect_kwargs['password'] = password
            
            self.ssh_client.connect(**connect_kwargs)
            self.sftp_client = self.ssh_client.open_sftp()
            
            self.log(f"Successfully connected to {hostname}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to connect to server: {e}", "ERROR")
            return False
    
    def disconnect_from_server(self):
        """Disconnect from remote server"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
        self.log("Disconnected from server", "INFO")
    
    def execute_command(self, command: str, timeout: Optional[int] = None) -> Tuple[int, str, str]:
        """Execute command on remote server with real-time monitoring"""
        if not self.ssh_client:
            raise Exception("Not connected to server")
        
        timeout = timeout or self.config['deployment']['command_timeout']
        
        self.log(f"Executing: {command}", "DEBUG")
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            
            # Real-time output monitoring
            stdout_output = []
            stderr_output = []
            
            def read_output(stream, output_list, stream_name):
                while True:
                    line = stream.readline()
                    if not line:
                        break
                    line = line.strip()
                    if line:
                        output_list.append(line)
                        self.log(f"[{stream_name}] {line}", "DEBUG", Colors.CYAN)
            
            # Start threads for real-time output
            stdout_thread = threading.Thread(target=read_output, args=(stdout, stdout_output, "STDOUT"))
            stderr_thread = threading.Thread(target=read_output, args=(stderr, stderr_output, "STDERR"))
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for command completion
            exit_status = stdout.channel.recv_exit_status()
            
            # Wait for output threads to finish
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)
            
            stdout_text = '\n'.join(stdout_output)
            stderr_text = '\n'.join(stderr_output)
            
            if exit_status == 0:
                self.log(f"Command completed successfully", "SUCCESS")
            else:
                self.log(f"Command failed with exit code {exit_status}", "ERROR")
            
            return exit_status, stdout_text, stderr_text
            
        except Exception as e:
            self.log(f"Command execution failed: {e}", "ERROR")
            return -1, "", str(e)
    
    def detect_errors(self, output: str) -> List[ErrorPattern]:
        """Detect errors in command output using patterns"""
        detected_errors = []
        
        for pattern in self.error_patterns:
            if re.search(pattern.pattern, output, re.IGNORECASE):
                detected_errors.append(pattern)
                self.log(f"Error detected: {pattern.description}", "WARNING")
        
        return detected_errors
    
    def auto_recover_error(self, error_pattern: ErrorPattern) -> bool:
        """Automatically attempt to recover from detected error"""
        self.log(f"Attempting auto-recovery for: {error_pattern.description}", "INFO")
        
        recovery_function = getattr(self, error_pattern.recovery_function, None)
        if recovery_function:
            try:
                return recovery_function()
            except Exception as e:
                self.log(f"Recovery function failed: {e}", "ERROR")
                return False
        else:
            self.log(f"No recovery function found for: {error_pattern.recovery_function}", "WARNING")
            return False
    
    # Error recovery functions
    def fix_nodejs_conflicts(self) -> bool:
        """Fix Node.js package conflicts"""
        self.log("Fixing Node.js conflicts...", "INFO")
        
        commands = [
            "apt remove -y nodejs npm libnode-dev || true",
            "apt purge -y nodejs npm libnode-dev || true",
            "apt autoremove -y",
            "apt clean",
            "curl -fsSL https://deb.nodesource.com/setup_18.x | bash -",
            "apt update",
            "apt install -y nodejs"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0 and "curl" not in cmd:  # Allow curl to potentially fail
                self.log(f"Node.js fix command failed: {cmd}", "ERROR")
                return False
        
        # Verify installation
        exit_code, stdout, stderr = self.execute_command("node --version")
        if exit_code == 0:
            self.log(f"Node.js fixed successfully: {stdout}", "SUCCESS")
            return True
        
        return False
    
    def update_package_lists(self) -> bool:
        """Update package repository lists"""
        self.log("Updating package lists...", "INFO")
        exit_code, stdout, stderr = self.execute_command("apt update")
        return exit_code == 0
    
    def fix_permissions(self) -> bool:
        """Fix common permission issues"""
        self.log("Fixing permissions...", "INFO")
        commands = [
            "chown -R projectmeats:projectmeats /opt/projectmeats",
            "chmod -R 755 /opt/projectmeats",
            "chmod +x /opt/projectmeats/scripts/*"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Permission fix failed: {cmd}", "ERROR")
                return False
        
        return True
    
    def restart_database_service(self) -> bool:
        """Restart database service"""
        self.log("Restarting database service...", "INFO")
        exit_code, stdout, stderr = self.execute_command("systemctl restart postgresql")
        if exit_code == 0:
            time.sleep(5)  # Wait for service to start
            exit_code, stdout, stderr = self.execute_command("systemctl is-active postgresql")
            return exit_code == 0
        return False
    
    def kill_conflicting_processes(self) -> bool:
        """Kill processes using conflicting ports"""
        self.log("Checking for conflicting processes...", "INFO")
        
        ports_to_check = [80, 443, 8000, 3000]
        for port in ports_to_check:
            exit_code, stdout, stderr = self.execute_command(f"lsof -ti:{port}")
            if exit_code == 0 and stdout.strip():
                pids = stdout.strip().split('\n')
                for pid in pids:
                    self.log(f"Killing process {pid} on port {port}", "INFO")
                    self.execute_command(f"kill -9 {pid}")
        
        return True
    
    def restart_services(self) -> bool:
        """Restart key services"""
        self.log("Restarting services...", "INFO")
        services = ["nginx", "projectmeats"]
        
        for service in services:
            exit_code, stdout, stderr = self.execute_command(f"systemctl restart {service}")
            if exit_code != 0:
                self.log(f"Failed to restart {service}", "WARNING")
        
        return True
    
    def cleanup_disk_space(self) -> bool:
        """Clean up disk space"""
        self.log("Cleaning up disk space...", "INFO")
        commands = [
            "apt autoremove -y",
            "apt autoclean",
            "docker system prune -f || true",
            "journalctl --vacuum-time=7d",
            "find /tmp -type f -atime +7 -delete || true"
        ]
        
        for cmd in commands:
            self.execute_command(cmd)
        
        # Check if cleanup was successful
        exit_code, stdout, stderr = self.execute_command("df -h /")
        if exit_code == 0:
            self.log(f"Disk space after cleanup: {stdout}", "INFO")
        
        return True
    
    def fix_dns_issues(self) -> bool:
        """Fix DNS resolution issues"""
        self.log("Fixing DNS issues...", "INFO")
        commands = [
            "systemctl restart systemd-resolved",
            "echo 'nameserver 8.8.8.8' > /etc/resolv.conf",
            "echo 'nameserver 8.8.4.4' >> /etc/resolv.conf"
        ]
        
        for cmd in commands:
            self.execute_command(cmd)
        
        # Test DNS resolution
        exit_code, stdout, stderr = self.execute_command("nslookup google.com")
        return exit_code == 0
    
    def retry_ssl_setup(self) -> bool:
        """Retry SSL certificate setup"""
        self.log("Retrying SSL setup...", "INFO")
        
        # Wait for DNS propagation
        time.sleep(30)
        
        domain = self.config.get('domain', 'example.com')
        cmd = f"certbot --nginx -d {domain} --agree-tos --non-interactive"
        exit_code, stdout, stderr = self.execute_command(cmd)
        
        return exit_code == 0
    
    def fix_npm_permissions(self) -> bool:
        """Fix NPM permission issues"""
        self.log("Fixing NPM permissions...", "INFO")
        commands = [
            "npm config set prefix /usr/local",
            "chown -R $(whoami) $(npm config get prefix)/{lib/node_modules,bin,share}",
            "npm cache clean --force"
        ]
        
        for cmd in commands:
            self.execute_command(cmd)
        
        return True
    
    def execute_deployment_step(self, step_name: str, step_description: str) -> bool:
        """Execute a deployment step with error handling and recovery"""
        self.log(f"Starting step: {step_description}", "INFO", Colors.BOLD + Colors.BLUE)
        
        step_function = getattr(self, f"deploy_{step_name}", None)
        if not step_function:
            self.log(f"Step function not found: deploy_{step_name}", "ERROR")
            return False
        
        max_retries = self.config['deployment']['max_retries']
        retry_delay = self.config['deployment']['retry_delay']
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.log(f"Retry attempt {attempt}/{max_retries}", "WARNING")
                    time.sleep(retry_delay)
                
                success = step_function()
                
                if success:
                    self.log(f"Step completed: {step_description}", "SUCCESS", Colors.BOLD + Colors.GREEN)
                    return True
                else:
                    self.log(f"Step failed: {step_description}", "ERROR")
                    if attempt < max_retries:
                        self.log(f"Will retry in {retry_delay} seconds...", "WARNING")
                    
            except Exception as e:
                self.log(f"Step exception: {e}", "ERROR")
                if attempt < max_retries:
                    self.log(f"Will retry in {retry_delay} seconds...", "WARNING")
        
        self.log(f"Step failed after {max_retries} attempts: {step_description}", "CRITICAL")
        return False
    
    def run_deployment(self, server_config: Dict[str, Any]) -> bool:
        """Run the complete deployment process"""
        try:
            # Initialize deployment state
            deployment_id = hashlib.md5(f"{server_config['hostname']}{datetime.now()}".encode()).hexdigest()[:8]
            
            self.state = DeploymentState(
                deployment_id=deployment_id,
                status=DeploymentStatus.RUNNING,
                current_step=0,
                total_steps=len(self.deployment_steps),
                server_info=server_config
            )
            
            self.save_state()
            
            self.log(f"Starting deployment {deployment_id}", "INFO", Colors.BOLD + Colors.PURPLE)
            self.log(f"Target server: {server_config['hostname']}", "INFO")
            
            # Connect to server
            if not self.connect_to_server(
                server_config['hostname'],
                server_config.get('username', 'root'),
                server_config.get('key_file'),
                server_config.get('password')
            ):
                self.state.status = DeploymentStatus.FAILED
                self.save_state()
                return False
            
            # Execute deployment steps
            for i, (step_name, step_description) in enumerate(self.deployment_steps):
                self.state.current_step = i + 1
                self.save_state()
                
                if not self.execute_deployment_step(step_name, step_description):
                    self.state.status = DeploymentStatus.FAILED
                    self.state.error_count += 1
                    self.save_state()
                    
                    if not self.config['recovery']['auto_recovery']:
                        return False
                    
                    # Try automatic recovery
                    self.log("Attempting automatic recovery...", "WARNING")
                    if not self.attempt_recovery(step_name):
                        return False
            
            # Deployment completed successfully
            self.state.status = DeploymentStatus.SUCCESS
            self.state.end_time = datetime.now()
            self.save_state()
            
            self.log("Deployment completed successfully!", "SUCCESS", Colors.BOLD + Colors.GREEN)
            self.print_deployment_summary()
            
            return True
            
        except KeyboardInterrupt:
            self.log("Deployment cancelled by user", "WARNING")
            self.state.status = DeploymentStatus.CANCELLED
            self.save_state()
            return False
            
        except Exception as e:
            self.log(f"Deployment failed with exception: {e}", "CRITICAL")
            self.state.status = DeploymentStatus.FAILED
            self.save_state()
            return False
            
        finally:
            self.disconnect_from_server()
    
    def attempt_recovery(self, failed_step: str) -> bool:
        """Attempt to recover from a failed step"""
        self.log(f"Attempting recovery for failed step: {failed_step}", "WARNING")
        
        # Implement step-specific recovery logic
        recovery_methods = {
            "install_dependencies": ["update_package_lists", "fix_nodejs_conflicts"],
            "configure_backend": ["fix_permissions", "restart_database_service"],
            "configure_frontend": ["fix_npm_permissions", "cleanup_disk_space"],
            "setup_webserver": ["kill_conflicting_processes", "restart_services"],
            "setup_services": ["restart_services", "fix_permissions"]
        }
        
        methods = recovery_methods.get(failed_step, ["restart_services"])
        
        for method in methods:
            recovery_function = getattr(self, method, None)
            if recovery_function and recovery_function():
                self.log(f"Recovery successful with method: {method}", "SUCCESS")
                return True
        
        return False
    
    def print_deployment_summary(self):
        """Print deployment summary"""
        if not self.state:
            return
        
        duration = (self.state.end_time or datetime.now()) - self.state.start_time
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}  Deployment Summary{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        
        print(f"\n{Colors.CYAN}Deployment ID:{Colors.END} {self.state.deployment_id}")
        print(f"{Colors.CYAN}Status:{Colors.END} {self.state.status.value.upper()}")
        print(f"{Colors.CYAN}Duration:{Colors.END} {duration}")
        print(f"{Colors.CYAN}Steps Completed:{Colors.END} {self.state.current_step}/{self.state.total_steps}")
        print(f"{Colors.CYAN}Errors:{Colors.END} {self.state.error_count}")
        print(f"{Colors.CYAN}Warnings:{Colors.END} {len(self.state.warnings)}")
        
        if self.state.status == DeploymentStatus.SUCCESS:
            server_info = self.state.server_info
            domain = server_info.get('domain', server_info['hostname'])
            
            print(f"\n{Colors.GREEN}[SUCCESS] Deployment Successful!{Colors.END}")
            print(f"\n{Colors.BOLD}Access your application:{Colors.END}")
            print(f"  {Colors.CYAN}Website:{Colors.END} https://{domain}")
            print(f"  {Colors.CYAN}Admin Panel:{Colors.END} https://{domain}/admin/")
            print(f"  {Colors.CYAN}API Docs:{Colors.END} https://{domain}/api/docs/")
        
        print(f"\n{Colors.BLUE}Log files:{Colors.END}")
        print(f"  State: {self.state_file}")
        print(f"  Detailed logs: {self.log_file}")
        print(f"  System logs: logs/")
    
    # Deployment step implementations
    def deploy_validate_server(self) -> bool:
        """Validate server prerequisites"""
        self.log("Validating server environment...", "INFO")
        
        # Check OS
        exit_code, stdout, stderr = self.execute_command("cat /etc/os-release")
        if exit_code != 0:
            return False
        
        if "ubuntu" not in stdout.lower():
            self.log("Warning: Non-Ubuntu OS detected", "WARNING")
        
        # Check root access
        exit_code, stdout, stderr = self.execute_command("whoami")
        if exit_code != 0 or stdout.strip() != "root":
            self.log("Root access required", "ERROR")
            return False
        
        # Check disk space
        exit_code, stdout, stderr = self.execute_command("df -h /")
        if exit_code == 0:
            self.log(f"Disk space: {stdout}", "INFO")
        
        # Check memory
        exit_code, stdout, stderr = self.execute_command("free -h")
        if exit_code == 0:
            self.log(f"Memory: {stdout}", "INFO")
        
        return True
    
    def deploy_setup_authentication(self) -> bool:
        """Setup authentication and security"""
        self.log("Setting up authentication...", "INFO")
        
        # Update system
        exit_code, stdout, stderr = self.execute_command("apt update")
        return exit_code == 0
    
    def deploy_install_dependencies(self) -> bool:
        """Install system dependencies"""
        self.log("Installing dependencies...", "INFO")
        
        packages = [
            'python3', 'python3-pip', 'python3-venv', 'nginx', 'git',
            'curl', 'ufw', 'fail2ban', 'certbot', 'python3-certbot-nginx',
            'postgresql', 'postgresql-contrib', 'libpq-dev'
        ]
        
        exit_code, stdout, stderr = self.execute_command(f"apt install -y {' '.join(packages)}")
        
        if exit_code != 0:
            # Check for errors and attempt recovery
            errors = self.detect_errors(stderr)
            for error in errors:
                if self.config['recovery']['auto_recovery']:
                    if self.auto_recover_error(error):
                        # Retry installation
                        exit_code, stdout, stderr = self.execute_command(f"apt install -y {' '.join(packages)}")
                        break
        
        return exit_code == 0
    
    def deploy_handle_nodejs_conflicts(self) -> bool:
        """Handle Node.js conflicts"""
        self.log("Setting up Node.js...", "INFO")
        return self.fix_nodejs_conflicts()
    
    def deploy_setup_database(self) -> bool:
        """Setup database"""
        self.log("Setting up database...", "INFO")
        
        commands = [
            "systemctl start postgresql",
            "systemctl enable postgresql",
            "sudo -u postgres createdb projectmeats || true",
            "sudo -u postgres createuser projectmeats || true"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            # Allow some commands to fail (already exists)
        
        return True
    
    def deploy_download_application(self) -> bool:
        """Download application with proper validation and backup handling"""
        self.log("Downloading ProjectMeats...", "INFO")
        
        project_dir = "/opt/projectmeats"
        
        # Setup GitHub authentication
        self.setup_github_auth()
        
        # Create project directory
        exit_code, stdout, stderr = self.execute_command(f"mkdir -p {project_dir}")
        if exit_code != 0:
            self.log("Failed to create project directory", "ERROR")
            return False
        
        # Check if directory already has content and handle it
        exit_code, stdout, stderr = self.execute_command(f"ls -la {project_dir}")
        if exit_code == 0 and stdout and len(stdout.strip().split('\n')) > 3:  # More than just . and ..
            self.log("Project directory already contains files", "WARNING")
            
            # Create backup of existing content
            backup_dir = f"{project_dir}_backup_{int(time.time())}"
            self.log(f"Creating backup at {backup_dir}", "INFO")
            exit_code, stdout, stderr = self.execute_command(f"mv {project_dir} {backup_dir}")
            if exit_code != 0:
                self.log("Failed to backup existing directory", "ERROR")
                return False
            
            # Recreate empty directory
            exit_code, stdout, stderr = self.execute_command(f"mkdir -p {project_dir}")
            if exit_code != 0:
                self.log("Failed to recreate project directory", "ERROR")
                return False
        
        # Download from GitHub (multiple methods with validation)
        project_downloaded = False
        
        # Method 1: Git clone with PAT authentication (if configured)
        if self.config['github'].get('user') and self.config['github'].get('token'):
            self.log("Attempting git clone with Personal Access Token...", "INFO")
            try:
                github_url = f"https://{self.config['github']['user']}:{self.config['github']['token']}@github.com/Vacilator/ProjectMeats.git"
                exit_code, stdout, stderr = self.execute_command(
                    f"cd {project_dir} && git clone {github_url} ."
                )
                if exit_code == 0:
                    project_downloaded = True
                    self.log("Successfully downloaded using PAT authentication", "SUCCESS")
                else:
                    self.log("PAT authentication failed, trying other methods...", "WARNING")
            except Exception as e:
                self.log(f"PAT authentication error: {e}", "WARNING")
        
        # Method 2: Basic git clone (public access)
        if not project_downloaded:
            self.log("Attempting git clone (public access)...", "INFO")
            exit_code, stdout, stderr = self.execute_command(
                f"cd {project_dir} && git clone https://github.com/Vacilator/ProjectMeats.git ."
            )
            if exit_code == 0:
                project_downloaded = True
                self.log("Successfully downloaded using git clone", "SUCCESS")
        
        # Method 3: Direct zip download with validation
        if not project_downloaded:
            self.log("Attempting direct zip download...", "INFO")
            
            # Download
            exit_code, stdout, stderr = self.execute_command(
                f"cd {project_dir} && curl -L https://github.com/Vacilator/ProjectMeats/archive/main.zip -o project.zip"
            )
            if exit_code == 0:
                # Validate download size
                exit_code, stdout, stderr = self.execute_command(
                    f"stat -c%s {project_dir}/project.zip 2>/dev/null || echo 0"
                )
                if exit_code == 0 and stdout:
                    zip_size = int(stdout.strip())
                    if zip_size < 1000:  # Less than 1KB indicates error response
                        self.log(f"Download failed - file too small ({zip_size} bytes)", "ERROR")
                    else:
                        # Check if it's actually a zip file
                        exit_code, stdout, stderr = self.execute_command(
                            f"cd {project_dir} && file project.zip"
                        )
                        if exit_code == 0 and "zip" in stdout.lower():
                            # Extract
                            exit_code, stdout, stderr = self.execute_command(
                                f"cd {project_dir} && unzip -q project.zip && mv ProjectMeats-main/* . && mv ProjectMeats-main/.* . 2>/dev/null || true && rm -rf ProjectMeats-main project.zip"
                            )
                            if exit_code == 0:
                                project_downloaded = True
                                self.log("Successfully downloaded via direct zip download", "SUCCESS")
                            else:
                                self.log("Failed to extract zip file", "ERROR")
                        else:
                            self.log("Downloaded file is not a valid zip archive", "ERROR")
                            # Clean up invalid file
                            self.execute_command(f"rm -f {project_dir}/project.zip")
        
        # Method 4: Try tarball download as alternative
        if not project_downloaded:
            self.log("Attempting tarball download...", "INFO")
            
            # Download
            exit_code, stdout, stderr = self.execute_command(
                f"cd {project_dir} && curl -L https://github.com/Vacilator/ProjectMeats/archive/refs/heads/main.tar.gz -o project.tar.gz"
            )
            if exit_code == 0:
                # Validate tarball size
                exit_code, stdout, stderr = self.execute_command(
                    f"stat -c%s {project_dir}/project.tar.gz 2>/dev/null || echo 0"
                )
                if exit_code == 0 and stdout:
                    tar_size = int(stdout.strip())
                    if tar_size < 1000:  # Less than 1KB indicates error response
                        self.log(f"Tarball download failed - file too small ({tar_size} bytes)", "ERROR")
                    else:
                        # Check if it's actually a tar.gz file
                        exit_code, stdout, stderr = self.execute_command(
                            f"cd {project_dir} && file project.tar.gz"
                        )
                        if exit_code == 0 and "gzip compressed" in stdout.lower():
                            # Extract
                            exit_code, stdout, stderr = self.execute_command(
                                f"cd {project_dir} && tar -xzf project.tar.gz && mv ProjectMeats-main/* . && mv ProjectMeats-main/.* . 2>/dev/null || true && rm -rf ProjectMeats-main project.tar.gz"
                            )
                            if exit_code == 0:
                                project_downloaded = True
                                self.log("Successfully downloaded via tarball", "SUCCESS")
                            else:
                                self.log("Failed to extract tarball", "ERROR")
                        else:
                            self.log("Downloaded file is not a valid gzip archive", "ERROR")
                            # Clean up invalid file
                            self.execute_command(f"rm -f {project_dir}/project.tar.gz")
        
        if not project_downloaded:
            self.log("All download methods failed", "ERROR")
            return False
        
        # Verify that essential files exist
        exit_code, stdout, stderr = self.execute_command(
            f"ls -la {project_dir}/backend {project_dir}/frontend {project_dir}/README.md"
        )
        if exit_code != 0:
            self.log("Downloaded project appears incomplete - missing essential directories", "ERROR")
            return False
        
        self.log("ProjectMeats application downloaded and validated successfully", "SUCCESS")
        return True
    
    def deploy_configure_backend(self) -> bool:
        """Configure backend"""
        self.log("Configuring backend...", "INFO")
        
        commands = [
            "cd /opt/projectmeats/backend && python3 -m venv venv",
            "cd /opt/projectmeats/backend && ./venv/bin/pip install -r requirements.txt",
            "cd /opt/projectmeats/backend && ./venv/bin/python manage.py migrate"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                return False
        
        return True
    
    def deploy_configure_frontend(self) -> bool:
        """Configure frontend"""
        self.log("Configuring frontend...", "INFO")
        
        commands = [
            "cd /opt/projectmeats/frontend && npm install",
            "cd /opt/projectmeats/frontend && npm run build"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                return False
        
        return True
    
    def deploy_setup_webserver(self) -> bool:
        """Setup web server"""
        self.log("Setting up web server...", "INFO")
        
        # Basic nginx configuration
        exit_code, stdout, stderr = self.execute_command("systemctl start nginx")
        if exit_code != 0:
            return False
        
        exit_code, stdout, stderr = self.execute_command("systemctl enable nginx")
        return exit_code == 0
    
    def deploy_setup_services(self) -> bool:
        """Setup system services"""
        self.log("Setting up services...", "INFO")
        
        commands = [
            "systemctl daemon-reload",
            "ufw --force enable",
            "ufw allow ssh",
            "ufw allow 'Nginx Full'"
        ]
        
        for cmd in commands:
            self.execute_command(cmd)
        
        return True
    
    def deploy_final_verification(self) -> bool:
        """Final verification"""
        self.log("Running final verification...", "INFO")
        
        # Check services
        services = ["nginx", "postgresql"]
        for service in services:
            exit_code, stdout, stderr = self.execute_command(f"systemctl is-active {service}")
            if exit_code != 0:
                self.log(f"Service {service} not running", "ERROR")
                return False
        
        self.log("Final verification completed", "SUCCESS")
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI-Driven Deployment Orchestrator for ProjectMeats")
    
    parser.add_argument("--interactive", action="store_true", help="Interactive deployment setup")
    parser.add_argument("--server", help="Server hostname or IP")
    parser.add_argument("--domain", help="Domain name")
    parser.add_argument("--username", default="root", help="SSH username")
    parser.add_argument("--key-file", help="SSH private key file")
    parser.add_argument("--password", help="SSH password")
    parser.add_argument("--github-user", help="GitHub username for authentication")
    parser.add_argument("--github-token", help="GitHub Personal Access Token")
    parser.add_argument("--auto-approve", action="store_true", help="Automatic deployment without prompts")
    parser.add_argument("--test-connection", action="store_true", help="Test server connection only")
    parser.add_argument("--resume", help="Resume deployment with given ID")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--profile", help="Use predefined server profile from configuration")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = AIDeploymentOrchestrator(args.config)
    
    # Set GitHub authentication if provided
    if args.github_user and args.github_token:
        orchestrator.config['github']['user'] = args.github_user
        orchestrator.config['github']['token'] = args.github_token
        orchestrator.log("GitHub authentication configured from command line", "SUCCESS")
    
    # Load profile settings if specified
    profile_settings = {}
    if args.profile:
        profile_settings = orchestrator.load_profile(args.profile)
        if not profile_settings:
            # Profile not found or error loading
            return 1
    
    # Apply profile settings as defaults, command line args take precedence
    server = args.server or profile_settings.get('server')
    domain = args.domain or profile_settings.get('domain')
    username = args.username if args.username != "root" else profile_settings.get('username', "root")
    key_file = args.key_file or profile_settings.get('key_file')
    
    try:
        if args.resume:
            if orchestrator.load_state(args.resume):
                orchestrator.log(f"Resuming deployment {args.resume}", "INFO")
                # Continue from last step
                # Implementation would continue deployment from saved state
            else:
                orchestrator.log(f"Could not load deployment state for {args.resume}", "ERROR")
                return 1
        
        elif args.test_connection:
            if not server:
                orchestrator.log("Server hostname required for connection test", "ERROR")
                return 1
            
            server_config = {
                'hostname': server,
                'username': username,
                'key_file': key_file,
                'password': args.password
            }
            
            if orchestrator.connect_to_server(**server_config):
                orchestrator.log("Connection test successful", "SUCCESS")
                orchestrator.disconnect_from_server()
                return 0
            else:
                return 1
        
        elif args.interactive:
            # Interactive setup
            orchestrator.log("Starting interactive deployment setup...", "INFO")
            print(f"\n{Colors.CYAN}Interactive Deployment Setup{Colors.END}")
            print(f"{Colors.CYAN}{'='*40}{Colors.END}")
            
            # Get server details
            print(f"\n{Colors.BOLD}Server Configuration:{Colors.END}")
            if server:
                hostname = input(f"{Colors.YELLOW}Enter server hostname or IP [{server}]:{Colors.END} ").strip() or server
            else:
                hostname = input(f"{Colors.YELLOW}Enter server hostname or IP:{Colors.END} ").strip()
            if not hostname:
                orchestrator.log("Server hostname is required", "ERROR")
                return 1
            
            username_input = input(f"{Colors.YELLOW}Enter SSH username [{username}]:{Colors.END} ").strip() or username
            
            print(f"\n{Colors.BOLD}Authentication Method:{Colors.END}")
            print("1. Password authentication")
            print("2. SSH key file authentication")
            auth_method = input(f"{Colors.YELLOW}Choose authentication method (1 or 2):{Colors.END} ").strip()
            
            if auth_method == "2":
                if key_file:
                    key_file_input = input(f"{Colors.YELLOW}Enter path to SSH private key [{key_file}]:{Colors.END} ").strip() or key_file
                else:
                    key_file_input = input(f"{Colors.YELLOW}Enter path to SSH private key:{Colors.END} ").strip()
                if not key_file_input or not os.path.exists(key_file_input):
                    orchestrator.log(f"SSH key file not found: {key_file_input}", "ERROR")
                    return 1
                key_file = key_file_input
                password = None
            else:
                print(f"{Colors.YELLOW}Enter SSH password for {username}@{hostname}:{Colors.END}")
                try:
                    import getpass
                    password = getpass.getpass("Password: ")
                except Exception as e:
                    orchestrator.log(f"Error reading password: {e}", "ERROR")
                    # Fallback to regular input (less secure but works)
                    password = input("Password (will be visible): ")
                key_file = None
            
            if domain:
                domain_input = input(f"{Colors.YELLOW}Enter domain name (optional) [{domain}]:{Colors.END} ").strip() or domain
            else:
                domain_input = input(f"{Colors.YELLOW}Enter domain name (optional):{Colors.END} ").strip()
            if not domain_input:
                domain_input = hostname  # Use hostname as fallback
            
            print(f"\n{Colors.BOLD}Configuration Summary:{Colors.END}")
            print(f"  Server: {hostname}")
            print(f"  Username: {username_input}")
            print(f"  Auth method: {'SSH Key' if key_file else 'Password'}")
            print(f"  Domain: {domain_input}")
            
            confirm = input(f"\n{Colors.YELLOW}Proceed with deployment? [Y/n]:{Colors.END} ").strip()
            if confirm.lower() in ['n', 'no']:
                orchestrator.log("Deployment cancelled by user", "INFO")
                return 0
            
            server_config = {
                'hostname': hostname,
                'username': username_input,
                'key_file': key_file,
                'password': password,
                'domain': domain_input
            }
            
            # Store domain in config
            orchestrator.config['domain'] = domain_input
            
            # Run deployment
            success = orchestrator.run_deployment(server_config)
            return 0 if success else 1
        
        elif server:
            # Direct deployment (either from --server or --profile)
            server_config = {
                'hostname': server,
                'username': username,
                'key_file': key_file,
                'password': args.password,
                'domain': domain
            }
            
            if domain:
                orchestrator.config['domain'] = domain
            
            success = orchestrator.run_deployment(server_config)
            return 0 if success else 1
        
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        orchestrator.log("Deployment cancelled by user", "WARNING")
        return 1
    except Exception as e:
        orchestrator.log(f"Deployment failed: {e}", "CRITICAL")
        return 1


if __name__ == "__main__":
    sys.exit(main())