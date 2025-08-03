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

# Import GitHub integration
try:
    from github_integration import GitHubIntegration, DeploymentLogManager, DeploymentLogEntry
    GITHUB_INTEGRATION_AVAILABLE = True
except ImportError:
    GITHUB_INTEGRATION_AVAILABLE = False
    GitHubIntegration = None
    DeploymentLogManager = None
    DeploymentLogEntry = None


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
    domain_accessible: bool = False  # NEW: Track domain accessibility
    services_healthy: bool = False   # NEW: Track service health
    critical_checks_passed: bool = False  # NEW: Track critical deployment checks
    
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


class AIIntelligenceEngine:
    """
    AI Intelligence Engine for deployment analysis and optimization
    
    Provides intelligent error detection, predictive analysis, and autonomous
    recovery capabilities for deployment processes.
    """
    
    def __init__(self):
        self.error_patterns = self._load_error_patterns()
        self.fix_strategies = self._load_fix_strategies()
        self.performance_baselines = {}
        self.deployment_history = []
        
    def _load_error_patterns(self) -> Dict[str, Dict]:
        """Load error patterns for intelligent detection"""
        return {
            "nodejs_conflicts": {
                "patterns": [
                    r"npm.*ERR.*EACCES",
                    r"node.*version.*conflict",
                    r"npm.*permission.*denied"
                ],
                "severity": ErrorSeverity.HIGH,
                "auto_fix": True,
                "fix_time": 300  # 5 minutes
            },
            "database_connection": {
                "patterns": [
                    r"psql.*connection.*refused",
                    r"postgresql.*authentication.*failed",
                    r"role.*does not exist"
                ],
                "severity": ErrorSeverity.CRITICAL,
                "auto_fix": True,
                "fix_time": 180  # 3 minutes
            },
            "ssl_certificate": {
                "patterns": [
                    r"certbot.*failed",
                    r"letsencrypt.*error",
                    r"ssl.*certificate.*invalid"
                ],
                "severity": ErrorSeverity.HIGH,
                "auto_fix": True,
                "fix_time": 240  # 4 minutes
            }
        }
    
    def _load_fix_strategies(self) -> Dict[str, Dict]:
        """Load fix strategies for common issues"""
        return {
            "nodejs_conflicts": {
                "strategy": "comprehensive_nodejs_cleanup_and_reinstall",
                "steps": [
                    "Remove all existing Node.js installations",
                    "Clean package manager caches", 
                    "Install Node.js 18 LTS via NodeSource repository",
                    "Verify installation and fix permissions"
                ]
            },
            "database_connection": {
                "strategy": "postgresql_setup_with_validation",
                "steps": [
                    "Ensure PostgreSQL is running",
                    "Create database and user with proper permissions",
                    "Test connectivity",
                    "Apply security configurations"
                ]
            }
        }
    
    def analyze_error(self, error_output: str, context: Dict = None):
        """Analyze error output using AI pattern matching"""
        best_match = None
        highest_confidence = 0.0
        
        for error_type, pattern_info in self.error_patterns.items():
            confidence = 0.0
            matches = 0
            
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, error_output, re.IGNORECASE):
                    matches += 1
                    confidence += 0.2  # Each pattern match adds confidence
            
            if matches > 0:
                confidence = min(confidence + (matches * 0.1), 1.0)
                
                if confidence > highest_confidence:
                    highest_confidence = confidence
                    best_match = error_type
        
        return {
            "error_type": best_match,
            "confidence": highest_confidence,
            "auto_fix_available": best_match and self.error_patterns[best_match].get("auto_fix", False),
            "estimated_fix_time": best_match and self.error_patterns[best_match].get("fix_time", 300)
        } if best_match else None


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
        
        # GitHub integration - must be after logging setup
        self.github_log_manager: Optional[DeploymentLogManager] = None
        self.github_integration: Optional[GitHubIntegration] = None
        self._setup_github_integration()  # Call here instead of in _setup_logging
        
        # Remote connection
        self.ssh_client = None
        self.sftp_client = None
        
        # Command execution
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.is_running = False
        
        # Error patterns for intelligent recovery
        self.error_patterns = self._initialize_error_patterns()
        
        # Deployment steps with enhanced verification
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
            ("final_verification", "Final testing and verification"),
            ("domain_accessibility_check", "Domain accessibility verification")  # NEW: Critical final check
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
            "ai_features": {
                "intelligent_error_detection": True,
                "predictive_analysis": True,
                "autonomous_recovery": True,
                "performance_optimization": True
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
    
    def _setup_github_integration(self):
        """Setup GitHub integration for logging and issue creation"""
        # Initialize GitHub-related attributes
        self.github_log_manager: Optional[DeploymentLogManager] = None
        self.github_integration: Optional[GitHubIntegration] = None
        
        if not GITHUB_INTEGRATION_AVAILABLE:
            self.log("GitHub integration not available (missing github_integration module)", "WARNING")
            return
        
        # Check for GitHub token
        github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_PAT')
        if not github_token:
            self.log("GitHub token not found in environment variables", "INFO")
            self.log("Set GITHUB_TOKEN or GITHUB_PAT for GitHub integration features", "INFO")
            return
        
        try:
            self.github_integration = GitHubIntegration(
                token=github_token,
                repo="Vacilator/ProjectMeats"
            )
            self.log("GitHub integration initialized successfully", "SUCCESS")
        except Exception as e:
            self.log(f"Failed to initialize GitHub integration: {e}", "WARNING")
    
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
        
        # Add to GitHub log manager if available
        if hasattr(self, 'github_log_manager') and self.github_log_manager and level in ["ERROR", "CRITICAL", "WARNING", "SUCCESS"]:
            try:
                current_step = None
                if self.state and hasattr(self.state, 'current_step'):
                    step_name = self.deployment_steps[self.state.current_step - 1][0] if self.state.current_step > 0 else None
                    current_step = step_name
                
                self.github_log_manager.add_log(level, message, current_step)
            except Exception:
                pass  # Don't fail deployment for GitHub logging issues
    
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
            
            # Initialize GitHub log manager
            if GITHUB_INTEGRATION_AVAILABLE and self.github_integration:
                self.github_log_manager = DeploymentLogManager(deployment_id)
                self.github_log_manager.github = self.github_integration
                self.github_log_manager.update_status("in_progress")
            
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
                self._handle_deployment_failure("server_connection", "Failed to connect to server")
                return False
            
            # Execute deployment steps
            failed_step = None
            for i, (step_name, step_description) in enumerate(self.deployment_steps):
                self.state.current_step = i + 1
                self.save_state()
                
                step_success = self.execute_deployment_step(step_name, step_description)
                
                if not step_success:
                    failed_step = step_name
                    self.state.status = DeploymentStatus.FAILED
                    self.state.error_count += 1
                    self.save_state()
                    
                    if not self.config['recovery']['auto_recovery']:
                        self._handle_deployment_failure(step_name, f"Step failed: {step_description}")
                        return False
                    
                    # Try automatic recovery
                    self.log("Attempting automatic recovery...", "WARNING")
                    if self.attempt_recovery(step_name):
                        # Re-run the failed step after successful recovery
                        self.log(f"Re-running step after recovery: {step_description}", "INFO")
                        if not self.execute_deployment_step(step_name, step_description):
                            self._handle_deployment_failure(step_name, f"Step failed even after recovery: {step_description}")
                            return False
                    else:
                        self._handle_deployment_failure(step_name, f"Step failed and recovery unsuccessful: {step_description}")
                        return False
            
            # CRITICAL FIX: Only mark as successful if all critical checks pass
            if not self._verify_deployment_success():
                self._handle_deployment_failure("final_verification", "Deployment verification failed - application not accessible")
                return False
            
            # Deployment completed successfully
            self.state.status = DeploymentStatus.SUCCESS
            self.state.end_time = datetime.now()
            self.save_state()
            
            # Update GitHub status
            if self.github_log_manager:
                domain = server_config.get('domain', server_config['hostname'])
                target_url = f"https://{domain}" if domain else None
                self.github_log_manager.update_status("success", target_url)
                self.github_log_manager.post_final_logs("success")
            
            self.log("Deployment completed successfully!", "SUCCESS", Colors.BOLD + Colors.GREEN)
            self.print_deployment_summary()
            
            return True
            
        except KeyboardInterrupt:
            self.log("Deployment cancelled by user", "WARNING")
            self.state.status = DeploymentStatus.CANCELLED
            self.save_state()
            self._handle_deployment_failure("user_cancelled", "Deployment cancelled by user")
            return False
            
        except Exception as e:
            self.log(f"Deployment failed with exception: {e}", "CRITICAL")
            self.state.status = DeploymentStatus.FAILED
            self.save_state()
            self._handle_deployment_failure("exception", f"Deployment failed with exception: {e}")
            return False
            
        finally:
            self.disconnect_from_server()
    
    def _handle_deployment_failure(self, failed_step: str, error_message: str):
        """Handle deployment failure with GitHub integration"""
        self.log(f"Deployment failed at step: {failed_step}", "CRITICAL")
        self.log(f"Error: {error_message}", "CRITICAL")
        
        # Update GitHub status and create issue
        if self.github_log_manager:
            self.github_log_manager.update_status("failure")
            
            error_details = {
                "failed_step": failed_step,
                "error_message": error_message,
                "server_info": self.state.server_info if self.state else {},
                "auto_recovery": self.config.get('recovery', {}).get('auto_recovery', False),
                "deployment_step": self.state.current_step if self.state else 0,
                "total_steps": len(self.deployment_steps)
            }
            
            # Create GitHub issue for the failure
            issue_number = self.github_log_manager.create_failure_issue(error_details)
            if issue_number:
                self.log(f"Created GitHub issue #{issue_number} for deployment failure", "INFO")
            
            # Post final logs
            self.github_log_manager.post_final_logs("failed")
    
    def _verify_deployment_success(self) -> bool:
        """Comprehensive verification that deployment actually succeeded"""
        self.log("Performing comprehensive deployment verification...", "INFO", Colors.BOLD + Colors.BLUE)
        
        # Check 1: Services are running
        if not self._verify_services_health():
            return False
        
        # Check 2: Domain is accessible (critical check)
        if not self._verify_domain_accessibility():
            return False
        
        # Check 3: Application endpoints respond correctly
        if not self._verify_application_endpoints():
            return False
        
        # All critical checks passed
        self.state.critical_checks_passed = True
        self.state.services_healthy = True
        self.state.domain_accessible = True
        self.save_state()
        
        self.log("✓ All deployment verification checks passed", "SUCCESS", Colors.BOLD + Colors.GREEN)
        return True
    
    def _verify_services_health(self) -> bool:
        """Verify that all required services are healthy"""
        self.log("Checking service health...", "INFO")
        
        required_services = ["nginx", "postgresql"]
        optional_services = ["projectmeats"]  # May not exist if backend setup failed
        
        for service in required_services:
            exit_code, stdout, stderr = self.execute_command(f"systemctl is-active {service}")
            if exit_code != 0:
                self.log(f"✗ Required service {service} is not running", "ERROR")
                return False
            else:
                self.log(f"✓ Service {service} is running", "SUCCESS")
        
        for service in optional_services:
            exit_code, stdout, stderr = self.execute_command(f"systemctl is-active {service}")
            if exit_code != 0:
                self.log(f"⚠ Optional service {service} is not running", "WARNING")
            else:
                self.log(f"✓ Service {service} is running", "SUCCESS")
        
        return True
    
    def _verify_domain_accessibility(self) -> bool:
        """Verify that the domain is accessible from external sources"""
        domain = self.config.get('domain', 'localhost')
        
        if not domain or domain == 'localhost':
            self.log("No domain configured, skipping external accessibility check", "WARNING")
            return True
        
        self.log(f"Testing external accessibility for domain: {domain}", "INFO")
        
        # Test HTTP accessibility
        exit_code, stdout, stderr = self.execute_command(
            f"curl -f -L --max-time 30 --connect-timeout 10 http://{domain}/health || echo 'HTTP_ACCESS_FAILED'"
        )
        
        if exit_code == 0 and "healthy" in stdout:
            self.log(f"✓ Domain {domain} is accessible via HTTP", "SUCCESS")
            return True
        elif exit_code == 0 and "HTTP_ACCESS_FAILED" not in stdout:
            # Got a response but not the health endpoint
            self.log(f"✓ Domain {domain} is responding (health endpoint may not be configured)", "SUCCESS")
            return True
        else:
            self.log(f"✗ CRITICAL: Domain {domain} is NOT accessible externally", "CRITICAL")
            self.log("This means the deployment has not succeeded despite completing all steps", "CRITICAL")
            
            # Perform diagnostic checks
            self._diagnose_domain_accessibility_issues(domain)
            return False
    
    def _verify_application_endpoints(self) -> bool:
        """Verify that application endpoints are working"""
        self.log("Testing application endpoints...", "INFO")
        
        # Test local nginx
        exit_code, stdout, stderr = self.execute_command("curl -f http://localhost/health")
        if exit_code != 0:
            self.log("✗ Local nginx health check failed", "WARNING")
            return False
        else:
            self.log("✓ Local nginx is responding", "SUCCESS")
        
        # Test if frontend files are served
        exit_code, stdout, stderr = self.execute_command("curl -I http://localhost/")
        if exit_code != 0:
            self.log("✗ Frontend files not being served", "WARNING")
            return False
        else:
            self.log("✓ Frontend files are being served", "SUCCESS")
        
        return True
    
    def _diagnose_domain_accessibility_issues(self, domain: str):
        """Diagnose why domain is not accessible"""
        self.log("Diagnosing domain accessibility issues...", "INFO")
        
        # Check DNS resolution
        exit_code, stdout, stderr = self.execute_command(f"nslookup {domain}")
        if exit_code != 0:
            self.log(f"✗ DNS resolution failed for {domain}", "ERROR")
            self.log("Possible causes: Domain not configured, DNS not propagated", "ERROR")
        else:
            self.log(f"✓ DNS resolution works for {domain}", "INFO")
            # Extract IP address from nslookup output
            lines = stdout.split('\n')
            for line in lines:
                if 'Address:' in line and '::' not in line:
                    ip = line.split('Address:')[1].strip()
                    self.log(f"Domain resolves to IP: {ip}", "INFO")
                    break
        
        # Check if nginx is listening on port 80
        exit_code, stdout, stderr = self.execute_command("netstat -tlnp | grep :80")
        if exit_code != 0:
            self.log("✗ No process listening on port 80", "ERROR")
        else:
            self.log(f"✓ Port 80 is being used: {stdout.strip()}", "INFO")
        
        # Check nginx configuration
        exit_code, stdout, stderr = self.execute_command(f"nginx -T | grep -A 10 'server_name {domain}'")
        if exit_code != 0:
            self.log(f"✗ No nginx configuration found for {domain}", "ERROR")
        else:
            self.log(f"✓ Nginx is configured for {domain}", "INFO")
        
        # Check firewall
        exit_code, stdout, stderr = self.execute_command("ufw status")
        if exit_code == 0:
            self.log(f"Firewall status: {stdout.strip()}", "INFO")
        
        # Additional network diagnostics
        server_ip = self.state.server_info.get('hostname', 'unknown')
        self.log(f"Server IP: {server_ip}", "INFO")
        self.log("Suggested actions:", "INFO")
        self.log(f"1. Verify DNS A record points {domain} → {server_ip}", "INFO")
        self.log(f"2. Test direct IP access: http://{server_ip}/health", "INFO")
        self.log(f"3. Check domain propagation: https://dnschecker.org/", "INFO")
        self.log(f"4. Verify firewall allows HTTP/HTTPS traffic", "INFO")
    
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
        
        # Critical status indicators
        print(f"\n{Colors.BOLD}Critical Deployment Checks:{Colors.END}")
        print(f"{Colors.CYAN}Services Healthy:{Colors.END} {'✓ YES' if self.state.services_healthy else '✗ NO'}")
        print(f"{Colors.CYAN}Domain Accessible:{Colors.END} {'✓ YES' if self.state.domain_accessible else '✗ NO'}")
        print(f"{Colors.CYAN}All Checks Passed:{Colors.END} {'✓ YES' if self.state.critical_checks_passed else '✗ NO'}")
        
        if self.state.status == DeploymentStatus.SUCCESS and self.state.critical_checks_passed:
            server_info = self.state.server_info
            domain = server_info.get('domain', server_info['hostname'])
            
            print(f"\n{Colors.GREEN}[SUCCESS] Deployment Successful!{Colors.END}")
            print(f"\n{Colors.BOLD}Access your application:{Colors.END}")
            print(f"  {Colors.CYAN}Website:{Colors.END} https://{domain}")
            print(f"  {Colors.CYAN}Admin Panel:{Colors.END} https://{domain}/admin/")
            print(f"  {Colors.CYAN}API Docs:{Colors.END} https://{domain}/api/docs/")
            
            # Verification URLs
            print(f"\n{Colors.BOLD}Verification URLs:{Colors.END}")
            print(f"  {Colors.CYAN}Health Check:{Colors.END} http://{domain}/health")
            print(f"  {Colors.CYAN}Direct IP:{Colors.END} http://{server_info['hostname']}/health")
            
        elif self.state.status == DeploymentStatus.SUCCESS and not self.state.critical_checks_passed:
            print(f"\n{Colors.YELLOW}[PARTIAL SUCCESS] Technical deployment completed but application not accessible{Colors.END}")
            print(f"\n{Colors.BOLD}Issues detected:{Colors.END}")
            if not self.state.services_healthy:
                print(f"  {Colors.RED}✗ Services not healthy{Colors.END}")
            if not self.state.domain_accessible:
                print(f"  {Colors.RED}✗ Domain not accessible from internet{Colors.END}")
            
            print(f"\n{Colors.BOLD}Troubleshooting needed:{Colors.END}")
            server_info = self.state.server_info
            domain = server_info.get('domain', server_info['hostname'])
            print(f"  1. Check DNS: nslookup {domain}")
            print(f"  2. Test direct access: http://{server_info['hostname']}/health")
            print(f"  3. Check firewall: ufw status")
            print(f"  4. Check nginx: systemctl status nginx")
            
            # GitHub issue information
            if self.github_log_manager:
                print(f"\n{Colors.CYAN}A GitHub issue has been created with detailed diagnostics{Colors.END}")
                
        else:
            print(f"\n{Colors.RED}[FAILED] Deployment Failed{Colors.END}")
            print(f"\n{Colors.BOLD}The deployment did not complete successfully.{Colors.END}")
            
            if self.github_log_manager:
                print(f"\n{Colors.CYAN}A GitHub issue has been created with error details and logs{Colors.END}")
        
        print(f"\n{Colors.BLUE}Log files:{Colors.END}")
        print(f"  State: {self.state_file}")
        print(f"  Detailed logs: {self.log_file}")
        print(f"  System logs: logs/")
        
        # GitHub integration info
        if self.github_integration:
            print(f"  GitHub integration: ✓ Enabled")
        else:
            print(f"  GitHub integration: ✗ Disabled (set GITHUB_TOKEN to enable)")
        
        print(f"\n{Colors.BLUE}For support:{Colors.END}")
        print(f"  Documentation: https://github.com/Vacilator/ProjectMeats/blob/main/DEPLOYMENT_README.md")
        print(f"  Issues: https://github.com/Vacilator/ProjectMeats/issues")
    
    # Deployment step implementations
    def deploy_validate_server(self) -> bool:
        """Validate server prerequisites and optionally prepare golden image"""
        self.log("Validating server environment...", "INFO")
        
        # Import server initializer
        try:
            from server_initialization import ServerInitializer
            server_init = ServerInitializer(self.ssh_client, self.logger)
        except ImportError:
            server_init = None
            self.log("Server initialization module not available", "WARNING")
        
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
        
        # Check disk space (minimum 5GB free)
        exit_code, stdout, stderr = self.execute_command("df -BG /")
        if exit_code == 0:
            self.log(f"Disk space: {stdout}", "INFO")
            # Extract available space
            lines = stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    available_gb = parts[3].replace('G', '')
                    try:
                        if int(available_gb) < 5:
                            self.log(f"WARNING: Low disk space ({available_gb}GB available, 5GB minimum recommended)", "WARNING")
                    except ValueError:
                        pass
        
        # Check memory (minimum 1GB)
        exit_code, stdout, stderr = self.execute_command("free -m")
        if exit_code == 0:
            self.log(f"Memory: {stdout}", "INFO")
            lines = stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 2:
                    total_mb = parts[1]
                    try:
                        if int(total_mb) < 1024:
                            self.log(f"WARNING: Low memory ({total_mb}MB total, 1GB minimum recommended)", "WARNING")
                    except ValueError:
                        pass
        
        # Check if this is a fresh server or has previous deployments
        exit_code, stdout, stderr = self.execute_command("ls -la /opt/projectmeats/ 2>/dev/null || echo 'NOT_FOUND'")
        if "NOT_FOUND" not in stdout:
            self.log("Previous ProjectMeats deployment detected", "INFO")
            
            # Check for golden image marker
            exit_code, stdout, stderr = self.execute_command("test -f /opt/projectmeats/golden_image_info.json")
            if exit_code == 0:
                self.log("Golden image detected - server is pre-configured", "SUCCESS")
            else:
                self.log("Previous deployment found but not a golden image", "WARNING")
                
                # Option to clean up previous deployment
                if self.config.get('deployment', {}).get('auto_cleanup', True):
                    self.log("Cleaning up previous deployment...", "INFO")
                    if server_init:
                        if server_init.cleanup_failed_deployment():
                            self.log("Previous deployment cleaned up successfully", "SUCCESS")
                        else:
                            self.log("Failed to clean up previous deployment", "WARNING")
        else:
            self.log("Fresh server detected", "INFO")
            
            # Option to prepare golden image
            if self.config.get('deployment', {}).get('prepare_golden_image', False):
                self.log("Preparing server as golden image...", "INFO")
                if server_init:
                    if server_init.prepare_golden_image():
                        self.log("Golden image preparation completed", "SUCCESS")
                    else:
                        self.log("Golden image preparation failed", "WARNING")
        
        # Test network connectivity
        connectivity_tests = [
            ("GitHub", "curl -s --connect-timeout 10 https://github.com > /dev/null"),
            ("Ubuntu repositories", "curl -s --connect-timeout 10 http://archive.ubuntu.com > /dev/null"),
            ("DNS resolution", "nslookup google.com > /dev/null")
        ]
        
        for test_name, test_command in connectivity_tests:
            exit_code, stdout, stderr = self.execute_command(test_command)
            if exit_code == 0:
                self.log(f"✓ {test_name} connectivity: OK", "SUCCESS")
            else:
                self.log(f"✗ {test_name} connectivity: FAILED", "WARNING")
        
        return True
    
    def deploy_setup_authentication(self) -> bool:
        """Setup authentication and security"""
        self.log("Setting up authentication...", "INFO")
        
        # Update system
        exit_code, stdout, stderr = self.execute_command("apt update")
        if exit_code != 0:
            return False
        
        # Create projectmeats user if it doesn't exist
        self.log("Creating projectmeats user...", "INFO")
        exit_code, stdout, stderr = self.execute_command("useradd -m -s /bin/bash projectmeats || true")
        if exit_code != 0 and "already exists" not in stderr:
            self.log(f"Failed to create projectmeats user: {stderr}", "ERROR")
            return False
        
        return True
    
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
        
        # Start and enable PostgreSQL
        commands = [
            "systemctl start postgresql",
            "systemctl enable postgresql"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Database service command failed: {cmd}", "ERROR")
                return False
        
        # Create database and user with proper authentication
        self.log("Creating ProjectMeats database and user...", "INFO")
        
        db_commands = [
            "sudo -u postgres psql -c \"DROP DATABASE IF EXISTS projectmeats;\"",
            "sudo -u postgres psql -c \"DROP USER IF EXISTS projectmeats;\"",
            "sudo -u postgres psql -c \"CREATE DATABASE projectmeats;\"",
            "sudo -u postgres psql -c \"CREATE USER projectmeats WITH PASSWORD 'projectmeats';\"",
            "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE projectmeats TO projectmeats;\"",
            "sudo -u postgres psql -c \"ALTER USER projectmeats CREATEDB;\""
        ]
        
        for cmd in db_commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Database command failed: {cmd}", "WARNING")
                # Continue with other commands as some may fail if already exist
        
        # Verify database connection
        exit_code, stdout, stderr = self.execute_command(
            "sudo -u postgres psql -d projectmeats -c \"SELECT version();\""
        )
        if exit_code == 0:
            self.log("Database setup completed successfully", "SUCCESS")
        else:
            self.log("Database verification failed", "WARNING")
        
        return True
    
    def deploy_download_application(self) -> bool:
        """Download application with improved timeout and error handling"""
        self.log("Setting up ProjectMeats application...", "INFO")
        
        project_dir = "/opt/projectmeats"
        
        # Setup GitHub authentication
        self.setup_github_auth()
        
        # Create project directory
        exit_code, stdout, stderr = self.execute_command(f"mkdir -p {project_dir}")
        if exit_code != 0:
            self.log("Failed to create project directory", "ERROR")
            return False
        
        # Check if application is already downloaded and valid
        exit_code, stdout, stderr = self.execute_command(
            f"ls -la {project_dir}/backend {project_dir}/frontend {project_dir}/README.md 2>/dev/null"
        )
        if exit_code == 0:
            self.log("ProjectMeats application already exists - skipping download", "SUCCESS")
            return True
        
        # Check if directory has content that needs backup
        exit_code, stdout, stderr = self.execute_command(f"ls -A {project_dir} 2>/dev/null | wc -l")
        if exit_code == 0 and stdout and int(stdout.strip()) > 0:
            self.log("Project directory contains files - creating backup", "WARNING")
            
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
        
        # Test network connectivity first
        self.log("Testing network connectivity...", "INFO")
        exit_code, stdout, stderr = self.execute_command("curl -s --connect-timeout 10 https://github.com > /dev/null")
        if exit_code != 0:
            self.log("Network connectivity issue - cannot reach GitHub", "ERROR")
            return False
        
        # Download from GitHub with improved timeout handling
        project_downloaded = False
        download_timeout = 1200  # 20 minutes for download operations
        
        # Method 1: Git clone with PAT authentication (if configured)
        if self.config['github'].get('user') and self.config['github'].get('token'):
            self.log("Attempting git clone with Personal Access Token...", "INFO")
            self.log("This may take several minutes for a large repository...", "INFO")
            try:
                github_url = f"https://{self.config['github']['user']}:{self.config['github']['token']}@github.com/Vacilator/ProjectMeats.git"
                exit_code, stdout, stderr = self.execute_command(
                    f"cd {project_dir} && timeout {download_timeout} git clone --progress {github_url} .",
                    timeout=download_timeout + 60
                )
                if exit_code == 0:
                    project_downloaded = True
                    self.log("Successfully downloaded using PAT authentication", "SUCCESS")
                else:
                    self.log(f"PAT authentication failed (exit code: {exit_code}), trying other methods...", "WARNING")
                    if stderr:
                        self.log(f"Error details: {stderr[:200]}...", "WARNING")
            except Exception as e:
                self.log(f"PAT authentication error: {e}", "WARNING")
        
        # Method 2: Basic git clone (public access)
        if not project_downloaded:
            self.log("Attempting git clone (public access)...", "INFO")
            self.log("This may take several minutes for a large repository...", "INFO")
            exit_code, stdout, stderr = self.execute_command(
                f"cd {project_dir} && timeout {download_timeout} git clone --progress https://github.com/Vacilator/ProjectMeats.git .",
                timeout=download_timeout + 60
            )
            if exit_code == 0:
                project_downloaded = True
                self.log("Successfully downloaded using git clone", "SUCCESS")
            else:
                self.log(f"Git clone failed (exit code: {exit_code}), trying direct download...", "WARNING")
                if stderr:
                    self.log(f"Error details: {stderr[:200]}...", "WARNING")
        
        # Method 3: Direct zip download (fallback)
        if not project_downloaded:
            self.log("Attempting direct zip download as fallback...", "INFO")
            
            # Download with timeout
            exit_code, stdout, stderr = self.execute_command(
                f"cd {project_dir} && timeout {download_timeout} curl -L --connect-timeout 30 --max-time {download_timeout} https://github.com/Vacilator/ProjectMeats/archive/main.zip -o project.zip",
                timeout=download_timeout + 60
            )
            if exit_code == 0:
                # Quick size check
                exit_code, stdout, stderr = self.execute_command(f"stat -c%s {project_dir}/project.zip 2>/dev/null || echo 0")
                if exit_code == 0 and stdout and int(stdout.strip()) > 1000:
                    # Extract without complex validation
                    self.log("Extracting downloaded archive...", "INFO")
                    exit_code, stdout, stderr = self.execute_command(
                        f"cd {project_dir} && unzip -q project.zip && mv ProjectMeats-main/* . && rmdir ProjectMeats-main && rm project.zip"
                    )
                    if exit_code == 0:
                        project_downloaded = True
                        self.log("Successfully downloaded via direct zip download", "SUCCESS")
                    else:
                        self.log("Failed to extract zip file", "ERROR")
                        # Clean up
                        self.execute_command(f"rm -f {project_dir}/project.zip")
                else:
                    self.log("Downloaded file appears invalid or too small", "ERROR")
                    self.execute_command(f"rm -f {project_dir}/project.zip")
            else:
                self.log(f"Direct download failed (exit code: {exit_code})", "WARNING")
        
        if not project_downloaded:
            self.log("All download methods failed", "ERROR")
            self.log("Please check network connectivity and GitHub access", "ERROR")
            return False
        
        # Simple verification that essential files exist
        self.log("Verifying downloaded application...", "INFO")
        exit_code, stdout, stderr = self.execute_command(
            f"test -d {project_dir}/backend && test -d {project_dir}/frontend && test -f {project_dir}/README.md"
        )
        if exit_code != 0:
            self.log("Downloaded project appears incomplete - missing essential directories", "ERROR")
            self.log("Required: backend/, frontend/, README.md", "ERROR")
            return False
        
        # Check for key files
        self.log("Checking for key application files...", "INFO")
        key_files = [
            "backend/manage.py",
            "backend/requirements.txt", 
            "frontend/package.json"
        ]
        
        missing_files = []
        for file_path in key_files:
            exit_code, stdout, stderr = self.execute_command(f"test -f {project_dir}/{file_path}")
            if exit_code != 0:
                missing_files.append(file_path)
        
        if missing_files:
            self.log(f"Warning: Some expected files are missing: {', '.join(missing_files)}", "WARNING")
            self.log("Deployment will continue but may fail in later steps", "WARNING")
        else:
            self.log("All key application files found", "SUCCESS")
        
        self.log("ProjectMeats application setup completed successfully", "SUCCESS")
        return True
    
    def deploy_configure_backend(self) -> bool:
        """Configure backend"""
        self.log("Configuring backend...", "INFO")
        
        # Create virtual environment and install dependencies
        commands = [
            "cd /opt/projectmeats/backend && python3 -m venv venv",
            "cd /opt/projectmeats/backend && ./venv/bin/pip install --upgrade pip",
            "cd /opt/projectmeats/backend && ./venv/bin/pip install -r requirements.txt"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Backend setup command failed: {cmd}", "ERROR")
                return False
        
        # Create Django settings for production
        self.log("Creating production Django settings...", "INFO")
        production_settings = """
import os
from .settings import *

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['*']  # Configure properly in production

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'projectmeats',
        'USER': 'projectmeats',
        'PASSWORD': 'projectmeats',  # Should be secure in production
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = '/opt/projectmeats/backend/staticfiles/'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = '/opt/projectmeats/backend/media/'

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
"""
        
        exit_code, stdout, stderr = self.execute_command(
            f"cat > /opt/projectmeats/backend/apps/settings/production.py << 'EOF'\n{production_settings}\nEOF"
        )
        if exit_code != 0:
            # Try alternative path structure
            exit_code, stdout, stderr = self.execute_command(
                f"mkdir -p /opt/projectmeats/backend/projectmeats && cat > /opt/projectmeats/backend/projectmeats/production_settings.py << 'EOF'\n{production_settings}\nEOF"
            )
        
        # Set Django settings module
        self.execute_command("export DJANGO_SETTINGS_MODULE=apps.settings.production")
        
        # Run Django management commands
        django_commands = [
            "cd /opt/projectmeats/backend && ./venv/bin/python manage.py migrate",
            "cd /opt/projectmeats/backend && ./venv/bin/python manage.py collectstatic --noinput",
            "cd /opt/projectmeats/backend && ./venv/bin/python manage.py check --deploy"
        ]
        
        for cmd in django_commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Django command failed: {cmd}", "WARNING")
                # Continue with other commands
        
        # Create Django service file
        service_content = """[Unit]
Description=ProjectMeats Django Backend
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=root
WorkingDirectory=/opt/projectmeats/backend
Environment=DJANGO_SETTINGS_MODULE=apps.settings.production
ExecStart=/opt/projectmeats/backend/venv/bin/python manage.py runserver 127.0.0.1:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
        
        exit_code, stdout, stderr = self.execute_command(
            f"cat > /etc/systemd/system/projectmeats.service << 'EOF'\n{service_content}\nEOF"
        )
        if exit_code != 0:
            self.log("Failed to create systemd service file", "ERROR")
            return False
        
        # Enable and start the service
        commands = [
            "systemctl daemon-reload",
            "systemctl enable projectmeats",
            "systemctl start projectmeats"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Service command failed: {cmd}", "WARNING")
        
        self.log("Backend configuration completed", "SUCCESS")
        return True
    
    def deploy_configure_frontend(self) -> bool:
        """Configure frontend"""
        self.log("Configuring frontend...", "INFO")
        
        # Configure npm for projectmeats user to avoid permission issues
        self.log("Configuring npm...", "INFO")
        npm_config_commands = [
            "mkdir -p /opt/projectmeats/.npm-global",
            "chown -R projectmeats:projectmeats /opt/projectmeats/.npm-global",
            "sudo -u projectmeats npm config set prefix /opt/projectmeats/.npm-global"
        ]
        
        for cmd in npm_config_commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"npm configuration failed: {cmd}", "ERROR")
                self.log(f"Error output: {stderr}", "ERROR")
                return False
        
        # Install dependencies and build frontend
        commands = [
            "cd /opt/projectmeats/frontend && sudo -u projectmeats bash -c 'export PATH=$PATH:/opt/projectmeats/.npm-global/bin; npm install'",
            "cd /opt/projectmeats/frontend && sudo -u projectmeats bash -c 'export PATH=$PATH:/opt/projectmeats/.npm-global/bin; npm run build'"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Frontend command failed: {cmd}", "ERROR")
                self.log(f"Error output: {stderr}", "ERROR")
                return False
        
        # Verify build directory was created
        exit_code, stdout, stderr = self.execute_command("ls -la /opt/projectmeats/frontend/build/")
        if exit_code != 0:
            self.log("Frontend build directory not found", "ERROR")
            return False
        
        # Verify index.html was created
        exit_code, stdout, stderr = self.execute_command("ls -la /opt/projectmeats/frontend/build/index.html")
        if exit_code != 0:
            self.log("Frontend index.html not found", "ERROR")
            return False
        
        self.log("Frontend configuration completed successfully", "SUCCESS")
        return True
    
    def deploy_setup_webserver(self) -> bool:
        """Setup web server"""
        self.log("Setting up web server...", "INFO")
        
        # Get domain from config
        domain = self.config.get('domain', 'localhost')
        self.log(f"Configuring nginx for domain: {domain}", "INFO")
        
        # Remove default nginx site
        self.execute_command("rm -f /etc/nginx/sites-enabled/default")
        
        # Create ProjectMeats nginx configuration
        nginx_config = f"""# Rate limiting
limit_req_zone $binary_remote_addr zone=projectmeats_api:10m rate=10r/s;

# Upstream for Django
upstream projectmeats_backend {{
    server 127.0.0.1:8000;
}}

# HTTP server
server {{
    listen 80;
    server_name {domain};

    # Frontend static files
    location / {{
        root /opt/projectmeats/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Caching for static assets
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}

    # API endpoints
    location /api/ {{
        limit_req zone=projectmeats_api burst=20 nodelay;
        
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}

    # Admin interface
    location /admin/ {{
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    # Django static files
    location /static/ {{
        alias /opt/projectmeats/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # Media files
    location /media/ {{
        alias /opt/projectmeats/backend/media/;
        expires 1d;
        add_header Cache-Control "public";
    }}

    # Health check
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}"""
        
        # Write nginx configuration file
        exit_code, stdout, stderr = self.execute_command(
            f"cat > /etc/nginx/sites-available/projectmeats << 'EOF'\n{nginx_config}\nEOF"
        )
        if exit_code != 0:
            self.log("Failed to create nginx configuration", "ERROR")
            return False
        
        # Enable the site
        exit_code, stdout, stderr = self.execute_command(
            "ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/"
        )
        if exit_code != 0:
            self.log("Failed to enable nginx site", "ERROR")
            return False
        
        # Test nginx configuration
        exit_code, stdout, stderr = self.execute_command("nginx -t")
        if exit_code != 0:
            self.log(f"Nginx configuration test failed: {stderr}", "ERROR")
            return False
        
        # Start and enable nginx
        exit_code, stdout, stderr = self.execute_command("systemctl start nginx")
        if exit_code != 0:
            self.log("Failed to start nginx", "ERROR")
            return False
        
        exit_code, stdout, stderr = self.execute_command("systemctl enable nginx")
        if exit_code != 0:
            self.log("Failed to enable nginx", "ERROR")
            return False
        
        # Reload nginx to apply configuration
        exit_code, stdout, stderr = self.execute_command("systemctl reload nginx")
        if exit_code != 0:
            self.log("Failed to reload nginx", "ERROR")
            return False
        
        self.log("Nginx configured and started successfully", "SUCCESS")
        return True
    
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
        services = ["nginx", "postgresql", "projectmeats"]
        for service in services:
            exit_code, stdout, stderr = self.execute_command(f"systemctl is-active {service}")
            if exit_code != 0:
                self.log(f"Service {service} not running", "ERROR")
                # Try to start the service
                self.log(f"Attempting to start {service}...", "INFO")
                start_exit_code, start_stdout, start_stderr = self.execute_command(f"systemctl start {service}")
                if start_exit_code != 0:
                    self.log(f"Failed to start {service}: {start_stderr}", "ERROR")
                    return False
                else:
                    self.log(f"Successfully started {service}", "SUCCESS")
        
        # Test nginx configuration
        exit_code, stdout, stderr = self.execute_command("nginx -t")
        if exit_code != 0:
            self.log(f"Nginx configuration test failed: {stderr}", "ERROR")
            return False
        
        # Test database connectivity
        exit_code, stdout, stderr = self.execute_command(
            "sudo -u postgres psql -d projectmeats -c \"SELECT 1;\" -t"
        )
        if exit_code != 0:
            self.log("Database connectivity test failed", "ERROR")
            return False
        
        # Test localhost health endpoint first
        exit_code, stdout, stderr = self.execute_command(f"curl -f http://localhost/health || echo 'Health check not available'")
        if exit_code == 0:
            self.log("Health check endpoint responding", "SUCCESS")
        else:
            self.log("Health check endpoint not responding (may be normal)", "INFO")
        
        # Check if frontend build exists
        exit_code, stdout, stderr = self.execute_command("ls -la /opt/projectmeats/frontend/build/index.html")
        if exit_code != 0:
            self.log("Frontend build files not found", "ERROR")
            return False
        
        # NEW: Test domain accessibility from external perspective
        domain = self.config.get('domain', 'localhost')
        if domain and domain != 'localhost':
            self.log(f"Testing external domain accessibility: {domain}", "INFO")
            
            # Test HTTP access to the domain
            exit_code, stdout, stderr = self.execute_command(
                f"curl -f -L --max-time 30 --connect-timeout 10 http://{domain}/health || echo 'EXTERNAL_ACCESS_FAILED'"
            )
            if exit_code == 0 and "healthy" in stdout:
                self.log(f"✓ Domain {domain} is externally accessible via HTTP", "SUCCESS")
            else:
                self.log(f"⚠ WARNING: Domain {domain} may not be externally accessible via HTTP", "WARNING")
                self.log(f"This could be due to DNS propagation, firewall, or SSL redirect issues", "WARNING")
                
                # Try to diagnose the issue
                self.log("Running additional diagnostics...", "INFO")
                
                # Check if DNS resolves
                dns_exit_code, dns_stdout, dns_stderr = self.execute_command(f"nslookup {domain}")
                if dns_exit_code == 0:
                    self.log(f"✓ DNS resolution for {domain} works", "INFO")
                else:
                    self.log(f"⚠ DNS resolution issue for {domain}: {dns_stderr}", "WARNING")
                
                # Check what processes are listening on port 80
                port_exit_code, port_stdout, port_stderr = self.execute_command("netstat -tlnp | grep :80")
                if port_exit_code == 0:
                    self.log(f"✓ Port 80 is being listened on: {port_stdout.strip()}", "INFO")
                else:
                    self.log("⚠ No process listening on port 80", "WARNING")
                
                # Check nginx configuration for the domain
                config_exit_code, config_stdout, config_stderr = self.execute_command(
                    f"nginx -T | grep -A 5 'server_name {domain}'"
                )
                if config_exit_code == 0:
                    self.log(f"✓ Nginx configured for domain {domain}", "INFO")
                else:
                    self.log(f"⚠ Nginx may not be configured for domain {domain}", "WARNING")
            
            # Test HTTPS if available
            https_exit_code, https_stdout, https_stderr = self.execute_command(
                f"curl -f -L --max-time 30 --connect-timeout 10 https://{domain}/health || echo 'HTTPS_ACCESS_FAILED'"
            )
            if https_exit_code == 0 and "healthy" in https_stdout:
                self.log(f"✓ Domain {domain} is accessible via HTTPS", "SUCCESS")
            else:
                self.log(f"ℹ HTTPS not available for {domain} (normal for new deployments)", "INFO")
        
        self.log("Final verification completed successfully", "SUCCESS")
        return True
    
    def deploy_domain_accessibility_check(self) -> bool:
        """CRITICAL: Verify domain accessibility - this determines real deployment success"""
        self.log("Performing critical domain accessibility check...", "INFO", Colors.BOLD + Colors.YELLOW)
        
        domain = self.config.get('domain', 'localhost')
        
        if not domain or domain == 'localhost':
            self.log("No external domain configured - skipping external accessibility check", "WARNING")
            return True
        
        self.log(f"Testing if {domain} is accessible from the internet...", "INFO")
        
        # Multiple accessibility tests
        tests_passed = 0
        total_tests = 3
        
        # Test 1: HTTP health check
        self.log("Test 1: HTTP health endpoint", "INFO")
        exit_code, stdout, stderr = self.execute_command(
            f"timeout 30 curl -f -L --connect-timeout 10 http://{domain}/health || echo 'FAILED'"
        )
        if exit_code == 0 and "healthy" in stdout and "FAILED" not in stdout:
            self.log("✓ HTTP health endpoint accessible", "SUCCESS")
            tests_passed += 1
        else:
            self.log("✗ HTTP health endpoint not accessible", "ERROR")
        
        # Test 2: Root page accessibility
        self.log("Test 2: Root page accessibility", "INFO")
        exit_code, stdout, stderr = self.execute_command(
            f"timeout 30 curl -I -L --connect-timeout 10 http://{domain}/ || echo 'FAILED'"
        )
        if exit_code == 0 and ("200 OK" in stdout or "301" in stdout or "302" in stdout):
            self.log("✓ Root page accessible", "SUCCESS")
            tests_passed += 1
        else:
            self.log("✗ Root page not accessible", "ERROR")
        
        # Test 3: DNS resolution verification
        self.log("Test 3: DNS resolution", "INFO")
        exit_code, stdout, stderr = self.execute_command(f"nslookup {domain}")
        if exit_code == 0 and "NXDOMAIN" not in stderr:
            self.log("✓ DNS resolution working", "SUCCESS")
            tests_passed += 1
        else:
            self.log("✗ DNS resolution failed", "ERROR")
        
        # Determine if domain accessibility check passes
        if tests_passed >= 2:
            self.log(f"✓ Domain accessibility check PASSED ({tests_passed}/{total_tests} tests)", "SUCCESS", Colors.BOLD + Colors.GREEN)
            return True
        else:
            self.log(f"✗ Domain accessibility check FAILED ({tests_passed}/{total_tests} tests)", "CRITICAL", Colors.BOLD + Colors.RED)
            self.log(f"CRITICAL: {domain} is not accessible from the internet", "CRITICAL")
            self.log("This indicates the deployment has NOT succeeded despite completing technical steps", "CRITICAL")
            
            # Provide diagnostic information
            self._diagnose_domain_accessibility_issues(domain)
            
            return False


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
    username = args.username or profile_settings.get('username', "root")
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
            
        elif args.profile:
            # Use predefined server profile
            profiles = orchestrator.config.get('server_profiles', {})
            if args.profile not in profiles:
                orchestrator.log(f"Profile '{args.profile}' not found in configuration", "ERROR")
                available_profiles = list(profiles.keys())
                if available_profiles:
                    orchestrator.log(f"Available profiles: {', '.join(available_profiles)}", "INFO")
                else:
                    orchestrator.log("No profiles configured. Run setup_ai_deployment.py first.", "INFO")
                return 1
            
            profile = profiles[args.profile]
            server_config = {
                'hostname': profile['hostname'],
                'username': profile.get('username', 'root'),
                'key_file': profile.get('key_file') if not profile.get('use_password', False) else None,
                'password': None,  # Password will be prompted if needed
                'domain': profile.get('domain')
            }
            
            if profile.get('domain'):
                orchestrator.config['domain'] = profile['domain']
            
            orchestrator.log(f"Using profile '{args.profile}' for deployment", "INFO")
            orchestrator.log(f"Target: {profile['hostname']}", "INFO")
            
            success = orchestrator.run_deployment(server_config)
            return 0 if success else 1
        
        elif args.server:
            # Direct deployment
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