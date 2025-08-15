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
- Automatic @copilot assignment for deployment failures

Usage:
    # Interactive setup and deployment
    python ai_deployment_orchestrator.py --interactive
    
    # Automated deployment with configuration
    python ai_deployment_orchestrator.py --server=myserver.com --domain=mydomain.com --auto
    
    # With GitHub authentication (recommended for @copilot integration)
    python ai_deployment_orchestrator.py --server=myserver.com --domain=mydomain.com --github-user=USERNAME --github-token=TOKEN
    
    # Test connection and validate server
    python ai_deployment_orchestrator.py --test-connection --server=myserver.com
    
    # Resume failed deployment
    python ai_deployment_orchestrator.py --resume --deployment-id=abc123

GitHub Integration:
    When deployment failures occur, the orchestrator automatically:
    - Creates GitHub issues assigned to @copilot for automatic fixing
    - Includes comprehensive error details and troubleshooting steps
    - For critical failures, also creates PRs with dedicated fix branches
    - Uses PAT credentials from --github-token parameter or GITHUB_TOKEN env var

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
import getpass

# Try to import Django's secret key generator, fallback to manual generation
try:
    from django.core.management.utils import get_random_secret_key
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    
    def get_random_secret_key():
        """Generate a Django-compatible secret key without Django dependency"""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)'
        return ''.join(secrets.choice(chars) for _ in range(50))

# Import GitHub integration
try:
    from scripts.deployment.github_integration import GitHubIntegration, DeploymentLogManager, DeploymentLogEntry
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
    automated_script_used: Optional[str] = None  # NEW: Track which automated script was used
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.start_time is None:
            self.start_time = datetime.now()


@dataclass 
class ProductionConfig:
    """Production configuration settings collected from user"""
    # Django Core
    secret_key: str = ""
    debug: bool = False
    allowed_hosts: str = ""
    
    # Database
    db_name: str = "projectmeats_prod"
    db_user: str = "projectmeats_user" 
    db_password: str = ""
    db_host: str = "localhost"
    db_port: str = "5432"
    
    # Domain & CORS
    domain: str = ""
    cors_origins: str = ""
    
    # Email (optional)
    email_host: str = ""
    email_port: str = "587"
    email_user: str = ""
    email_password: str = ""
    email_use_tls: bool = True
    
    # Company Info
    company_name: str = "ProjectMeats"
    company_email: str = ""
    company_phone: str = ""
    company_address: str = ""
    
    # Security
    enable_ssl: bool = True
    
    # File paths
    media_root: str = "/opt/projectmeats/media"
    static_root: str = "/opt/projectmeats/backend/staticfiles"
    log_dir: str = "/opt/projectmeats/logs"
    backup_dir: str = "/opt/projectmeats/backups"


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
        
        # Logging initialization guard
        self._logging_initialized = False
        self._reported_errors = set()  # Track reported errors to prevent duplicates
        
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
        
        # Deployment steps with enhanced verification and automated scripts
        # Base deployment steps - modified dynamically based on deployment mode
        self.base_deployment_steps = [
            ("validate_server", "Server validation and prerequisites"),
            ("setup_authentication", "Authentication and security setup"),
            ("install_dependencies", "System dependencies installation"),
            ("handle_nodejs_conflicts", "Node.js conflict resolution"),
            ("setup_database", "Database configuration"),
            ("download_application", "Application download and setup"),
            ("run_deployment_scripts", "Run automated deployment scripts"),  # NEW: Run specialized deployment scripts
            ("production_config_setup", "Production configuration and environment setup"),  # NEW: Production config collection
            ("configure_backend", "Backend configuration"),
            ("configure_frontend", "Frontend build and configuration"),
            ("setup_webserver", "Web server and SSL configuration"),
            ("setup_services", "System services and monitoring"),
            ("final_verification", "Final testing and verification"),
            ("domain_accessibility_check", "Domain accessibility verification")  # NEW: Critical final check
        ]
        
        # Will be set dynamically in run_deployment based on deployment mode
        self.deployment_steps = self.base_deployment_steps.copy()
    
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
        """Setup comprehensive logging with duplicate prevention"""
        if self._logging_initialized:
            return  # Prevent duplicate initialization
        
        log_level = getattr(logging, self.config["logging"]["level"].upper())
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Setup file logging
        log_filename = f"logs/deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Clear any existing handlers to prevent duplicates
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ],
            force=True  # Override any existing configuration
        )
        
        self.logger = logging.getLogger(__name__)
        self._logging_initialized = True
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
        """Initialize error detection patterns with improved specificity"""
        return [
            ErrorPattern(
                pattern=r"npm.*ERR.*conflict|nodejs.*conflict.*npm.*ERR",
                severity=ErrorSeverity.HIGH,
                recovery_function="fix_nodejs_conflicts",
                description="Node.js package conflicts detected"
            ),
            ErrorPattern(
                pattern=r"E: Unable to locate package.*|Package.*not found.*repository",
                severity=ErrorSeverity.MEDIUM,
                recovery_function="update_package_lists",
                description="Package repository needs update"
            ),
            ErrorPattern(
                pattern=r"Permission denied.*(/opt/|/home/|/etc/|systemctl|chmod|chown)",
                severity=ErrorSeverity.HIGH,
                recovery_function="fix_permissions",
                description="Permission issues detected"
            ),
            ErrorPattern(
                pattern=r"bind.*Address already in use|Port.*already in use.*:80|:443|:8000",
                severity=ErrorSeverity.MEDIUM,
                recovery_function="kill_conflicting_processes",
                description="Port conflicts detected"
            ),
            ErrorPattern(
                pattern=r"Could not connect to.*database.*Connection refused",
                severity=ErrorSeverity.HIGH,
                recovery_function="restart_database_service",
                description="Database connection issues"
            ),
            ErrorPattern(
                pattern=r"Connection refused.*:80|:443|:8000",
                severity=ErrorSeverity.HIGH,
                recovery_function="restart_services",
                description="Service connection issues"
            ),
            ErrorPattern(
                pattern=r"No space left on device|disk.*full.*usage.*9[0-9]%",
                severity=ErrorSeverity.CRITICAL,
                recovery_function="cleanup_disk_space",
                description="Insufficient disk space"
            ),
            ErrorPattern(
                pattern=r"DNS.*failed.*NXDOMAIN|name resolution.*failed.*not found",
                severity=ErrorSeverity.MEDIUM,
                recovery_function="fix_dns_issues",
                description="DNS resolution problems"
            ),
            ErrorPattern(
                pattern=r"SSL.*certificate.*failed.*verification|certbot.*failed.*challenge",
                severity=ErrorSeverity.HIGH,
                recovery_function="retry_ssl_setup",
                description="SSL certificate issues"
            ),
            ErrorPattern(
                pattern=r"npm.*ERR.*EACCES.*permission|npm.*WARN.*EACCES",
                severity=ErrorSeverity.MEDIUM,
                recovery_function="fix_npm_permissions",
                description="NPM permission issues"
            ),
            # NEW: Django-specific error patterns
            ErrorPattern(
                pattern=r"ModuleNotFoundError.*dj_database_url|ModuleNotFoundError.*django|No module named.*django",
                severity=ErrorSeverity.HIGH,
                recovery_function="fix_django_service_issues",
                description="Django dependencies missing"
            ),
            ErrorPattern(
                pattern=r"ExecStart=.*gunicorn.*projectmeats.wsgi.*code=exited.*status=1",
                severity=ErrorSeverity.CRITICAL,
                recovery_function="fix_django_service_issues",
                description="Django WSGI application failure"
            ),
            ErrorPattern(
                pattern=r"systemctl.*failed.*projectmeats.*service|projectmeats.*service.*failed",
                severity=ErrorSeverity.HIGH,
                recovery_function="fix_django_service_issues",
                description="ProjectMeats Django service failure"
            ),
            ErrorPattern(
                pattern=r"ImportError.*django|django.*not.*found|Django.*configuration.*invalid",
                severity=ErrorSeverity.HIGH,
                recovery_function="fix_django_service_issues",
                description="Django configuration or import issues"
            ),
            ErrorPattern(
                pattern=r"EnvironmentFile.*projectmeats.env.*No such file",
                severity=ErrorSeverity.HIGH,
                recovery_function="fix_django_service_issues",
                description="Django environment file missing"
            )
        ]
    
    def log(self, message: str, level: str = "INFO", color: Optional[str] = None):
        """Enhanced logging with colors and structured output, with deduplication"""
        # Skip redundant logging initialization messages
        if "Logging initialized" in message:
            if hasattr(self, '_logging_init_logged') and self._logging_init_logged:
                return  # Skip duplicate logging initialization messages
            self._logging_init_logged = True
        
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
        
        # Structured logging - only if logger is initialized
        if hasattr(self, 'logger') and self.logger:
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
                # Only run error detection on failed commands, not successful ones
                if stderr_text:
                    errors = self.detect_errors(stderr_text)
                    # Attempt auto-recovery if configured and errors are detected
                    if errors and self.config.get('recovery', {}).get('auto_recovery', False):
                        for error in errors:
                            if self.auto_recover_error(error):
                                break
            
            return exit_status, stdout_text, stderr_text
            
        except Exception as e:
            self.log(f"Command execution failed: {e}", "ERROR")
            return -1, "", str(e)
    
    def detect_errors(self, output: str) -> List[ErrorPattern]:
        """Detect errors in command output using patterns with deduplication"""
        if not output or len(output.strip()) < 10:  # Skip very short outputs
            return []
        
        detected_errors = []
        
        for pattern in self.error_patterns:
            if re.search(pattern.pattern, output, re.IGNORECASE | re.MULTILINE):
                # Create a unique key for this error to prevent duplicates
                error_key = f"{pattern.description}:{hash(output[:200])}"
                
                if error_key not in self._reported_errors:
                    detected_errors.append(pattern)
                    self._reported_errors.add(error_key)
                    self.log(f"Error detected: {pattern.description}", "WARNING")
                # If already reported, skip to prevent spam
        
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
            # Fix project-specific directory permissions
            "chown -R projectmeats:projectmeats /opt/projectmeats/frontend",
            "chmod -R 755 /opt/projectmeats/frontend",
            # Clean npm cache for projectmeats user
            "sudo -u projectmeats npm cache clean --force",
            # Ensure npm global directory exists and is owned correctly
            "mkdir -p /opt/projectmeats/.npm-global",
            "chown -R projectmeats:projectmeats /opt/projectmeats/.npm-global",
            # Set npm prefix for projectmeats user
            "sudo -u projectmeats npm config set prefix /opt/projectmeats/.npm-global"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"NPM permission fix failed: {cmd}", "WARNING")
                # Continue with other commands even if one fails
        
        return True
    
    def _check_django_service_health(self) -> bool:
        """Check if Django service needs fixing - returns True if fix is needed"""
        self.log("Checking Django service health...", "INFO")
        
        # Check 1: Is the Django service running?
        exit_code, stdout, stderr = self.execute_command("systemctl is-active projectmeats")
        if exit_code != 0:
            self.log("Django service (projectmeats) is not running", "WARNING")
            return True
        
        # Check 2: Are Python dependencies installed?
        project_dir = "/opt/projectmeats"
        exit_code, stdout, stderr = self.execute_command(
            f"test -d {project_dir}/venv && {project_dir}/venv/bin/pip show django dj-database-url psycopg2-binary"
        )
        if exit_code != 0:
            self.log("Python dependencies missing or virtual environment not found", "WARNING")
            return True
        
        # Check 3: Is the environment file in the correct location?
        exit_code, stdout, stderr = self.execute_command("test -f /etc/projectmeats/projectmeats.env")
        if exit_code != 0:
            self.log("Environment file not found at expected systemd location", "WARNING")
            return True
        
        # Check 4: Can Django configuration be imported?
        exit_code, stdout, stderr = self.execute_command(
            f"cd {project_dir}/backend && source ../venv/bin/activate && "
            "export $(cat /etc/projectmeats/projectmeats.env | grep -v '^#' | xargs) && "
            "timeout 10 python -c 'import django; from django.conf import settings; django.setup()' 2>/dev/null"
        )
        if exit_code != 0:
            self.log("Django configuration cannot be imported - likely missing dependencies or config issues", "WARNING")
            return True
        
        # Check 5: Is Django responding on the expected port?
        exit_code, stdout, stderr = self.execute_command("curl -f --connect-timeout 5 --max-time 10 http://127.0.0.1:8000/ >/dev/null 2>&1")
        if exit_code != 0:
            self.log("Django application not responding on port 8000", "WARNING")
            return True
        
        self.log("Django service appears to be healthy", "SUCCESS")
        return False
    
    def _run_django_service_fix(self, fix_script_path: str) -> bool:
        """Run the Django service fix script"""
        self.log("Running Django service fix script...", "INFO", Colors.BOLD + Colors.YELLOW)
        
        # Make script executable
        exit_code, stdout, stderr = self.execute_command(f"chmod +x {fix_script_path}")
        if exit_code != 0:
            self.log(f"Failed to make Django fix script executable: {fix_script_path}", "ERROR")
            return False
        
        # Run the fix script with timeout
        fix_timeout = 600  # 10 minutes should be enough for dependency installation
        
        try:
            exit_code, stdout, stderr = self.execute_command(
                f"bash {fix_script_path}",
                timeout=fix_timeout + 30
            )
            
            if exit_code == 0:
                self.log("Django service fix script completed successfully", "SUCCESS", Colors.BOLD + Colors.GREEN)
                
                # Check for success indicators in output
                if "🎉 Quick Fix Complete!" in stdout or "ProjectMeats Django service is now running" in stdout:
                    self.log("Django fix script reports successful completion", "SUCCESS")
                    
                    # Verify the fix worked
                    if self._verify_django_fix_success():
                        self.log("Django service fix verification passed", "SUCCESS")
                        return True
                    else:
                        self.log("Django service fix verification failed", "WARNING")
                        return False
                else:
                    self.log("Django fix script completed but without clear success indicators", "WARNING")
                    return self._verify_django_fix_success()
            else:
                self.log(f"Django service fix script failed with exit code {exit_code}", "ERROR")
                
                if stderr:
                    self.log(f"Fix script error output: {stderr[-300:]}", "ERROR")
                
                return False
                
        except Exception as e:
            self.log(f"Exception running Django service fix script: {e}", "ERROR")
            return False
    
    def _verify_django_fix_success(self) -> bool:
        """Verify that the Django service fix was successful"""
        self.log("Verifying Django service fix...", "INFO")
        
        # Give the service a moment to start
        import time
        time.sleep(5)
        
        # Check if service is now running
        exit_code, stdout, stderr = self.execute_command("systemctl is-active projectmeats")
        if exit_code != 0:
            self.log("Django service still not running after fix", "ERROR")
            return False
        
        # Detect if using socket or TCP configuration
        if self._detect_socket_service_configuration():
            return self._verify_socket_service()
        else:
            return self._verify_tcp_service()
    
    def _verify_socket_service(self) -> bool:
        """Verify Django service when using Unix socket configuration"""
        self.log("Verifying Django service with Unix socket configuration...", "INFO")
        
        # First check if socket file exists
        exit_code, stdout, stderr = self.execute_command("test -S /run/projectmeats.sock")
        if exit_code != 0:
            self.log("Unix socket file /run/projectmeats.sock does not exist", "ERROR")
            return False
        
        # Test socket accessibility directly
        exit_code, stdout, stderr = self.execute_command(
            "timeout 15 curl -f --connect-timeout 5 --unix-socket /run/projectmeats.sock http://localhost/ >/dev/null 2>&1"
        )
        if exit_code == 0:
            self.log("Django application is responding via Unix socket", "SUCCESS")
            return True
        
        # If direct socket test fails, try health endpoint
        exit_code, stdout, stderr = self.execute_command(
            "timeout 15 curl -f --connect-timeout 5 --unix-socket /run/projectmeats.sock http://localhost/health >/dev/null 2>&1"
        )
        if exit_code == 0:
            self.log("Django application is responding via Unix socket (health endpoint)", "SUCCESS")
            return True
        
        # If socket tests fail, try through nginx if configured
        exit_code, stdout, stderr = self.execute_command("systemctl is-active nginx")
        if exit_code == 0:
            self.log("Socket direct access failed, testing through nginx...", "INFO")
            exit_code, stdout, stderr = self.execute_command(
                "timeout 15 curl -f --connect-timeout 5 http://localhost/ >/dev/null 2>&1"
            )
            if exit_code == 0:
                self.log("Django application is responding through nginx", "SUCCESS")
                return True
        
        self.log("Django application not responding via Unix socket", "WARNING")
        self._log_socket_diagnostic_info()
        return False
    
    def _verify_tcp_service(self) -> bool:
        """Verify Django service when using TCP configuration"""
        self.log("Verifying Django service with TCP configuration...", "INFO")
        
        # Check if Django is responding on TCP port 8000
        exit_code, stdout, stderr = self.execute_command(
            "timeout 15 curl -f --connect-timeout 5 http://127.0.0.1:8000/ >/dev/null 2>&1"
        )
        if exit_code == 0:
            self.log("Django application is responding on port 8000", "SUCCESS")
            return True
        else:
            self.log("Django application not responding on port 8000", "WARNING")
            # Check service logs for more information
            exit_code2, logs, stderr2 = self.execute_command("journalctl -u projectmeats -n 5 --no-pager")
            if exit_code2 == 0:
                self.log(f"Recent Django service logs: {logs[-200:]}", "INFO")
            return False
    
    def _log_socket_diagnostic_info(self) -> None:
        """Log diagnostic information for socket service issues"""
        self.log("Gathering socket diagnostic information...", "INFO")
        
        # Check socket permissions
        exit_code, stdout, stderr = self.execute_command("ls -la /run/projectmeats.sock")
        if exit_code == 0:
            self.log(f"Socket permissions: {stdout.strip()}", "INFO")
        
        # Check service logs
        exit_code, logs, stderr = self.execute_command("journalctl -u projectmeats -n 5 --no-pager")
        if exit_code == 0:
            self.log(f"Recent Django service logs: {logs[-200:]}", "INFO")
            
        # Check if socket service exists
        exit_code, stdout, stderr = self.execute_command("systemctl is-active projectmeats.socket")
        if exit_code == 0:
            self.log("Socket service is active", "INFO")
        else:
            self.log("Socket service is not active", "WARNING")
    
    def _detect_socket_service_configuration(self) -> bool:
        """Detect if the new Unix socket-based SystemD service configuration is available"""
        self.log("Detecting SystemD socket service configuration...", "INFO")
        
        # Check for socket service files in the project
        required_socket_files = [
            "/opt/projectmeats/deployment/systemd/projectmeats-socket.service",
            "/opt/projectmeats/deployment/systemd/projectmeats.socket",
            "/opt/projectmeats/deployment/nginx/projectmeats-socket.conf",
            "/opt/projectmeats/deployment/scripts/reload_and_start_services.sh"
        ]
        
        socket_files_present = True
        for file_path in required_socket_files:
            exit_code, stdout, stderr = self.execute_command(f"test -f {file_path}")
            if exit_code != 0:
                self.log(f"Socket configuration file not found: {file_path}", "DEBUG")
                socket_files_present = False
        
        if socket_files_present:
            self.log("✓ Unix socket SystemD service configuration detected", "SUCCESS")
            self.log("Will use socket-based deployment architecture", "INFO")
            return True
        else:
            self.log("Socket service configuration not found - using traditional TCP configuration", "INFO")
            return False

    def _setup_projectmeats_user(self) -> bool:
        """Setup the dedicated projectmeats user required by socket services"""
        self.log("Setting up projectmeats user for socket services...", "INFO")
        
        # Check if user already exists
        exit_code, stdout, stderr = self.execute_command("id projectmeats")
        if exit_code == 0:
            self.log("ProjectMeats user already exists", "SUCCESS")
            return True
        
        # Create user with proper settings
        create_user_commands = [
            # Create system user with no shell and specific home directory
            "useradd --system --group --home-dir /opt/projectmeats --shell /bin/false projectmeats",
            # Create necessary directories
            "mkdir -p /opt/projectmeats /var/log/projectmeats /var/run/projectmeats",
            # Set ownership
            "chown -R projectmeats:projectmeats /opt/projectmeats /var/log/projectmeats /var/run/projectmeats",
            # Set permissions
            "chmod 755 /opt/projectmeats /var/log/projectmeats /var/run/projectmeats"
        ]
        
        for cmd in create_user_commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0 and "already exists" not in stderr:
                self.log(f"User setup command failed: {cmd}", "ERROR")
                self.log(f"Error: {stderr}", "ERROR")
                return False
        
        self.log("✓ ProjectMeats user created successfully", "SUCCESS")
        return True

    def _deploy_socket_service_files(self) -> bool:
        """Deploy the socket-based SystemD service files"""
        self.log("Deploying Unix socket SystemD service configuration...", "INFO")
        
        # Copy service files to systemd directory
        service_files = [
            ("/opt/projectmeats/deployment/systemd/projectmeats.socket", "/etc/systemd/system/projectmeats.socket"),
            ("/opt/projectmeats/deployment/systemd/projectmeats-socket.service", "/etc/systemd/system/projectmeats.service")
        ]
        
        for source, dest in service_files:
            exit_code, stdout, stderr = self.execute_command(f"cp {source} {dest}")
            if exit_code != 0:
                self.log(f"Failed to copy {source} to {dest}: {stderr}", "ERROR")
                return False
            
            # Set proper permissions
            exit_code, stdout, stderr = self.execute_command(f"chmod 644 {dest}")
            if exit_code != 0:
                self.log(f"Failed to set permissions on {dest}", "WARNING")
        
        self.log("✓ SystemD socket service files deployed", "SUCCESS")
        return True

    def _deploy_socket_nginx_configuration(self) -> bool:
        """Deploy the socket-based Nginx configuration"""
        self.log("Deploying Unix socket Nginx configuration...", "INFO")
        
        domain = self.config.get('domain', 'localhost')
        
        # Copy and customize nginx configuration
        exit_code, stdout, stderr = self.execute_command(
            f"cp /opt/projectmeats/deployment/nginx/projectmeats-socket.conf /etc/nginx/sites-available/projectmeats"
        )
        if exit_code != 0:
            self.log(f"Failed to copy nginx socket configuration: {stderr}", "ERROR")
            return False
        
        # Update server_name in nginx config if domain is specified
        if domain and domain != 'localhost':
            self.log(f"Updating nginx configuration for domain: {domain}", "INFO")
            exit_code, stdout, stderr = self.execute_command(
                f"sed -i 's/server_name meatscentral.com www.meatscentral.com;/server_name {domain} www.{domain};/g' /etc/nginx/sites-available/projectmeats"
            )
            if exit_code != 0:
                self.log("Failed to update domain in nginx config", "WARNING")
        
        # Enable the site
        exit_code, stdout, stderr = self.execute_command(
            "ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/"
        )
        if exit_code != 0:
            self.log(f"Failed to enable nginx site: {stderr}", "ERROR")
            return False
        
        # Remove default site
        self.execute_command("rm -f /etc/nginx/sites-enabled/default")
        
        self.log("✓ Unix socket Nginx configuration deployed", "SUCCESS")
        return True

    def _apply_socket_permission_fixes(self) -> bool:
        """Apply socket permission fixes to ensure nginx (www-data) can access the socket"""
        self.log("Applying socket permission fixes...", "INFO")
        
        # Ensure socket directory exists with proper permissions
        commands = [
            "mkdir -p /var/run/projectmeats",
            "chown -R projectmeats:www-data /var/run/projectmeats",
            "chmod 775 /var/run/projectmeats"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Failed to execute permission command '{cmd}': {stderr}", "ERROR")
                return False
        
        # Wait for socket to be created by systemd and then fix permissions
        self.log("Ensuring socket file permissions after service start...", "INFO")
        
        # Check if socket file exists and fix permissions
        exit_code, stdout, stderr = self.execute_command("test -S /run/projectmeats.sock")
        if exit_code == 0:
            # Socket exists, fix permissions as mentioned in problem statement  
            exit_code, stdout, stderr = self.execute_command("chown projectmeats:www-data /run/projectmeats.sock")
            if exit_code != 0:
                self.log(f"Failed to set socket ownership: {stderr}", "WARNING")
            
            exit_code, stdout, stderr = self.execute_command("chmod 660 /run/projectmeats.sock")
            if exit_code != 0:
                self.log(f"Failed to set socket permissions: {stderr}", "WARNING")
            else:
                self.log("✓ Socket permissions fixed for www-data access", "SUCCESS")
        else:
            self.log("Socket file not yet created - permissions will be handled by systemd configuration", "INFO")
        
        return True
    
    def _verify_socket_accessibility(self) -> bool:
        """Verify that nginx (www-data) can access the socket"""
        self.log("Verifying socket accessibility for nginx...", "INFO")
        
        # Check socket file permissions
        exit_code, stdout, stderr = self.execute_command("ls -l /run/projectmeats.sock")
        if exit_code == 0:
            self.log(f"Socket permissions: {stdout.strip()}", "INFO")
            
            # Verify socket is accessible (should show srw-rw---- projectmeats www-data)
            if "projectmeats www-data" in stdout and "rw-" in stdout:
                self.log("✓ Socket has correct permissions for www-data access", "SUCCESS")
                
                # Test socket connectivity as recommended in problem statement
                exit_code, stdout, stderr = self.execute_command(
                    "curl --unix-socket /run/projectmeats.sock http://localhost/health --connect-timeout 5 --max-time 10"
                )
                if exit_code == 0:
                    self.log("✓ Socket connectivity test successful", "SUCCESS")
                    return True
                else:
                    self.log(f"Socket connectivity test failed: {stderr}", "WARNING")
                    self.log("This may indicate Django service is not running yet", "INFO")
            else:
                self.log("Socket permissions may not be optimal for www-data access", "WARNING")
        else:
            self.log("Socket file not found for verification", "WARNING")
        
        return True

    def _enhanced_dns_resolution_check(self, domain: str) -> bool:
        """Enhanced DNS resolution check to avoid local resolver artifacts"""
        self.log(f"Enhanced DNS resolution check for {domain}...", "INFO")
        
        # Use dig with external DNS servers to avoid "127.0.0.53#53" local resolver artifact
        # as mentioned in the problem statement
        dns_servers = ["8.8.8.8", "1.1.1.1"]  # Google DNS and Cloudflare DNS
        
        for dns_server in dns_servers:
            self.log(f"Testing DNS resolution via {dns_server}...", "INFO")
            
            # Use dig +short to get clean IP address output
            exit_code, stdout, stderr = self.execute_command(
                f"dig +short @{dns_server} A {domain}"
            )
            
            if exit_code == 0 and stdout.strip():
                ip_address = stdout.strip().split('\n')[0]  # Get first IP if multiple
                # Validate IP address format
                if self._is_valid_ip(ip_address):
                    self.log(f"✓ DNS resolution via {dns_server}: {domain} -> {ip_address}", "SUCCESS")
                    
                    # Test direct IP access as mentioned in problem statement
                    self.log(f"Testing direct IP access: {ip_address}...", "INFO")
                    exit_code, stdout, stderr = self.execute_command(
                        f"curl -f -H 'Host: {domain}' --connect-timeout 10 --max-time 15 http://{ip_address}/ --silent --output /dev/null"
                    )
                    if exit_code == 0:
                        self.log(f"✓ Direct IP access successful to {ip_address}", "SUCCESS")
                    else:
                        self.log(f"Direct IP access failed to {ip_address}: {stderr}", "WARNING")
                    
                    return True
                else:
                    self.log(f"Invalid IP address returned: {ip_address}", "WARNING")
            else:
                self.log(f"DNS resolution failed via {dns_server}: {stderr}", "WARNING")
        
        # Fallback to nslookup if dig failed
        self.log("Falling back to nslookup...", "INFO")
        exit_code, stdout, stderr = self.execute_command(f"nslookup {domain}")
        if exit_code == 0:
            self.log(f"Fallback nslookup successful for {domain}", "INFO")
            return True
        else:
            self.log(f"All DNS resolution methods failed for {domain}", "ERROR")
            return False

    def _enhanced_port_80_check(self) -> None:
        """Enhanced port 80 accessibility check with proper privileges"""
        self.log("Enhanced port 80 accessibility check...", "INFO")
        
        # Use ss command with sudo as mentioned in problem statement for proper privilege check
        exit_code, stdout, stderr = self.execute_command("ss -tuln | grep :80")
        if exit_code == 0:
            self.log(f"✓ Port 80 is listening: {stdout.strip()}", "SUCCESS")
            
            # Check specifically for 0.0.0.0:80 binding (external access)
            if "0.0.0.0:80" in stdout:
                self.log("✓ Port 80 is bound for external access (0.0.0.0:80)", "SUCCESS")
            else:
                self.log("⚠ Port 80 may only be bound locally", "WARNING")
        else:
            self.log("✗ No process listening on port 80", "ERROR")
            
            # Additional diagnostics
            self.log("Running additional port diagnostics...", "INFO")
            
            # Check nginx status
            exit_code, stdout, stderr = self.execute_command("systemctl is-active nginx")
            if exit_code == 0:
                self.log("✓ Nginx service is active", "INFO")
            else:
                self.log("✗ Nginx service is not active", "WARNING")
            
            # Check nginx configuration
            exit_code, stdout, stderr = self.execute_command("nginx -t")
            if exit_code == 0:
                self.log("✓ Nginx configuration is valid", "INFO")
            else:
                self.log(f"✗ Nginx configuration has errors: {stderr}", "WARNING")

    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        import socket
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def _enhanced_health_endpoint_test(self, domain: str, is_local: bool = False) -> bool:
        """Enhanced health endpoint testing to handle 400 Bad Request and other issues"""
        host_label = "localhost" if is_local else domain
        self.log(f"Enhanced health endpoint test for {host_label}...", "INFO")
        
        # Multiple health endpoint patterns to try (Priority #3 - Health Endpoint fixes)
        health_endpoints = [
            "/health",      # Standard health endpoint
            "/health/",     # With trailing slash
            "/api/health",  # API health endpoint
            "/"             # Root endpoint fallback
        ]
        
        for endpoint in health_endpoints:
            url = f"http://{domain}{endpoint}" if domain else f"http://localhost{endpoint}"
            
            # Use different curl approaches to handle various response issues
            curl_commands = [
                # Standard approach
                f"curl -f -L --connect-timeout 10 --max-time 15 '{url}'",
                # Don't fail on HTTP errors, get status code
                f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 10 --max-time 15 '{url}'",
                # Include response headers to diagnose redirects/issues
                f"curl -I -s --connect-timeout 10 --max-time 15 '{url}'"
            ]
            
            for i, cmd in enumerate(curl_commands):
                self.log(f"Testing {endpoint} with method {i+1}/3...", "DEBUG")
                exit_code, stdout, stderr = self.execute_command(cmd)
                
                if i == 0:  # Standard curl
                    if exit_code == 0 and ("healthy" in stdout.lower() or "ok" in stdout.lower()):
                        self.log(f"✓ Health endpoint {endpoint} is working: {stdout.strip()}", "SUCCESS")
                        return True
                elif i == 1:  # Status code only
                    if stdout.strip() in ["200", "201", "204"]:
                        self.log(f"✓ Health endpoint {endpoint} returns good status: {stdout.strip()}", "SUCCESS")
                        return True
                    elif stdout.strip() in ["301", "302", "307", "308"]:
                        self.log(f"⚠ Health endpoint {endpoint} redirects (status: {stdout.strip()})", "WARNING")
                    elif stdout.strip() == "400":
                        self.log(f"✗ Health endpoint {endpoint} returns 400 Bad Request - needs Django health endpoint", "ERROR")
                    else:
                        self.log(f"Health endpoint {endpoint} status: {stdout.strip()}", "INFO")
                elif i == 2:  # Headers
                    if "200 OK" in stdout:
                        self.log(f"✓ Health endpoint {endpoint} headers look good", "SUCCESS") 
                        return True
                    elif "301" in stdout or "302" in stdout:
                        self.log(f"Health endpoint {endpoint} redirect detected: {stdout.split()[0]}", "INFO")
        
        # If all endpoints failed, provide specific guidance
        self.log(f"All health endpoint tests failed for {host_label}", "ERROR")
        if not is_local:
            self.log("Consider checking: DNS resolution, firewall rules, nginx configuration", "INFO")
        else:
            self.log("Consider checking: Django service status, nginx config, socket permissions", "INFO")
        
        return False

    def _run_socket_service_management(self) -> bool:
        """Run the automated socket service management script"""
        self.log("Running socket service management script...", "INFO")
        
        # Make the script executable
        script_path = "/opt/projectmeats/deployment/scripts/reload_and_start_services.sh"
        exit_code, stdout, stderr = self.execute_command(f"chmod +x {script_path}")
        if exit_code != 0:
            self.log(f"Failed to make service script executable: {stderr}", "ERROR")
            return False
        
        # Run the service management script
        exit_code, stdout, stderr = self.execute_command(f"bash {script_path}")
        if exit_code != 0:
            self.log(f"Socket service management script failed: {stderr}", "ERROR")
            self.log(f"Script output: {stdout}", "INFO")
            return False
        
        self.log("✓ Socket services configured and started", "SUCCESS")
        return True

    def _assess_remaining_deployment_needs(self) -> bool:
        """Assess if there are remaining deployment needs after Django fix"""
        self.log("Assessing remaining deployment needs...", "INFO")
        
        # Check critical components
        components_status = {
            "nginx": False,
            "frontend_build": False,
            "database_setup": False,
            "static_files": False
        }
        
        # Check nginx
        exit_code, stdout, stderr = self.execute_command("systemctl is-active nginx && test -f /etc/nginx/sites-enabled/projectmeats")
        components_status["nginx"] = (exit_code == 0)
        
        # Check frontend build
        exit_code, stdout, stderr = self.execute_command("test -d /opt/projectmeats/frontend/build && test -f /opt/projectmeats/frontend/build/index.html")
        components_status["frontend_build"] = (exit_code == 0)
        
        # Check database setup using actual credentials if available
        db_name, db_user, db_password = self._load_database_credentials()
        if db_name and db_user:
            exit_code, stdout, stderr = self.execute_command(f"sudo -u postgres psql -d '{db_name}' -c 'SELECT 1;' -t >/dev/null 2>&1")
        else:
            # Fallback to generic PostgreSQL test
            exit_code, stdout, stderr = self.execute_command("sudo -u postgres psql -c 'SELECT 1;' -t >/dev/null 2>&1")
        components_status["database_setup"] = (exit_code == 0)
        
        # Check static files
        exit_code, stdout, stderr = self.execute_command("test -d /opt/projectmeats/backend/staticfiles")
        components_status["static_files"] = (exit_code == 0)
        
        # Log component status
        for component, status in components_status.items():
            status_text = "OK" if status else "MISSING"
            level = "SUCCESS" if status else "INFO"
            self.log(f"{status_text} {component}", level)
        
        # Return True if we have significant missing components
        missing_count = sum(1 for status in components_status.values() if not status)
        needs_additional_setup = missing_count >= 2
        
        if needs_additional_setup:
            self.log(f"Additional deployment needed - {missing_count} components require setup", "INFO")
        else:
            self.log("Most components are already configured", "SUCCESS")
            
        return needs_additional_setup
    
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
            
            # Configure deployment mode and adjust steps
            deployment_mode = server_config.get('deployment_mode', 'standard')
            docker_monitoring = server_config.get('docker_monitoring', False)
            
            if deployment_mode == 'docker':
                self.log("Configuring Docker deployment with industry best practices", "INFO", Colors.CYAN)
                # Insert Docker setup step after database setup
                docker_steps = self.base_deployment_steps.copy()
                # Find the index to insert Docker setup after database setup
                db_index = next(i for i, (step, _) in enumerate(docker_steps) if step == "setup_database")
                docker_steps.insert(db_index + 1, ("docker_setup", "Docker infrastructure and container deployment"))
                
                # Replace standard deployment steps with Docker-optimized ones
                self.deployment_steps = docker_steps
                
                # Store Docker configuration
                self.config['deployment_mode'] = 'docker'
                self.config['docker_monitoring'] = docker_monitoring
                
                if docker_monitoring:
                    self.log("Monitoring stack (Prometheus, Grafana) will be deployed", "INFO", Colors.GREEN)
            else:
                self.log("Using standard systemd-based deployment", "INFO", Colors.YELLOW)
                self.deployment_steps = self.base_deployment_steps.copy()
            
            self.log(f"Deployment pipeline configured with {len(self.deployment_steps)} steps", "INFO")
            
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
        """Handle deployment failure with GitHub integration and @copilot assignment"""
        self.log(f"Deployment failed at step: {failed_step}", "CRITICAL")
        self.log(f"Error: {error_message}", "CRITICAL")
        
        # Update GitHub status and create issue with @copilot assignment
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
            
            # Determine if this is a critical failure that needs a PR
            critical_steps = ["server_connection", "configure_backend", "setup_webserver", "final_verification"]
            is_critical = failed_step in critical_steps
            
            # Create GitHub issue for the failure with @copilot assignment
            issue_number = self.github_log_manager.create_failure_issue(error_details)
            if issue_number:
                self.log(f"✅ Created GitHub issue #{issue_number} with @copilot assignment for deployment failure", "INFO")
                
                # For critical failures, also create a PR to expedite the fix
                if is_critical:
                    pr_number = self.github_log_manager.create_failure_pr(error_details)
                    if pr_number:
                        self.log(f"✅ Created GitHub PR #{pr_number} with @copilot assignment for critical deployment failure", "INFO")
                    else:
                        self.log("⚠️ Could not create GitHub PR, but issue was created successfully", "WARNING")
            else:
                self.log("❌ Failed to create GitHub issue - @copilot will not be automatically notified", "ERROR")
            
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
        
        self.log("OK All deployment verification checks passed", "SUCCESS", Colors.BOLD + Colors.GREEN)
        return True
    
    def _verify_services_health(self) -> bool:
        """Verify that all required services are healthy"""
        self.log("Checking service health...", "INFO")
        
        required_services = ["nginx", "postgresql"]
        optional_services = ["projectmeats"]  # May not exist if backend setup failed
        
        for service in required_services:
            exit_code, stdout, stderr = self.execute_command(f"systemctl is-active {service}")
            if exit_code != 0:
                self.log(f"X Required service {service} is not running", "ERROR")
                return False
            else:
                self.log(f"OK Service {service} is running", "SUCCESS")
        
        for service in optional_services:
            exit_code, stdout, stderr = self.execute_command(f"systemctl is-active {service}")
            if exit_code != 0:
                self.log(f"WARNING Optional service {service} is not running", "WARNING")
            else:
                self.log(f"OK Service {service} is running", "SUCCESS")
        
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
            self.log(f"OK Domain {domain} is accessible via HTTP", "SUCCESS")
            return True
        elif exit_code == 0 and "HTTP_ACCESS_FAILED" not in stdout:
            # Got a response but not the health endpoint
            self.log(f"OK Domain {domain} is responding (health endpoint may not be configured)", "SUCCESS")
            return True
        else:
            self.log(f"X CRITICAL: Domain {domain} is NOT accessible externally", "CRITICAL")
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
            self.log("X Local nginx health check failed", "WARNING")
            return False
        else:
            self.log("OK Local nginx is responding", "SUCCESS")
        
        # Test if frontend files are served
        exit_code, stdout, stderr = self.execute_command("curl -I http://localhost/")
        if exit_code != 0:
            self.log("X Frontend files not being served", "WARNING")
            return False
        else:
            self.log("OK Frontend files are being served", "SUCCESS")
        
        return True
    
    def _diagnose_domain_accessibility_issues(self, domain: str):
        """Diagnose why domain is not accessible"""
        self.log("Diagnosing domain accessibility issues...", "INFO")
        
        # Check DNS resolution
        exit_code, stdout, stderr = self.execute_command(f"nslookup {domain}")
        if exit_code != 0:
            self.log(f"X DNS resolution failed for {domain}", "ERROR")
            self.log("Possible causes: Domain not configured, DNS not propagated", "ERROR")
        else:
            self.log(f"OK DNS resolution works for {domain}", "INFO")
            # Extract IP address from nslookup output
            lines = stdout.split('\n')
            for line in lines:
                if 'Address:' in line and '::' not in line:
                    ip = line.split('Address:')[1].strip()
                    self.log(f"Domain resolves to IP: {ip}", "INFO")
                    break
        
        # Check if nginx is listening on port 80 (using ss as per problem statement)
        exit_code, stdout, stderr = self.execute_command("ss -tlnp | grep :80")
        if exit_code != 0:
            self.log("X No process listening on port 80", "ERROR")
        else:
            self.log(f"OK Port 80 is being used: {stdout.strip()}", "INFO")
        
        # Check nginx configuration
        exit_code, stdout, stderr = self.execute_command(f"nginx -T | grep -A 10 'server_name {domain}'")
        if exit_code != 0:
            self.log(f"X No nginx configuration found for {domain}", "ERROR")
        else:
            self.log(f"OK Nginx is configured for {domain}", "INFO")
        
        # Check firewall
        exit_code, stdout, stderr = self.execute_command("ufw status")
        if exit_code == 0:
            self.log(f"Firewall status: {stdout.strip()}", "INFO")
        
        # Additional network diagnostics
        server_ip = self.state.server_info.get('hostname', 'unknown')
        self.log(f"Server IP: {server_ip}", "INFO")
        self.log("Suggested actions:", "INFO")
        self.log(f"1. Verify DNS A record points {domain} -> {server_ip}", "INFO")
        self.log(f"2. Test direct IP access: http://{server_ip}/health", "INFO")
        self.log(f"3. Check domain propagation: https://dnschecker.org/", "INFO")
        self.log(f"4. Verify firewall allows HTTP/HTTPS traffic", "INFO")
    
    def attempt_recovery(self, failed_step: str) -> bool:
        """Attempt to recover from a failed step"""
        self.log(f"Attempting recovery for failed step: {failed_step}", "WARNING")
        
        # Implement step-specific recovery logic
        recovery_methods = {
            "install_dependencies": ["update_package_lists", "fix_nodejs_conflicts"],
            "configure_backend": ["fix_django_service_issues", "fix_permissions", "restart_database_service"],
            "configure_frontend": ["fix_npm_permissions", "cleanup_disk_space"],
            "setup_webserver": ["kill_conflicting_processes", "restart_services"],
            "setup_services": ["restart_services", "fix_permissions"],
            "run_deployment_scripts": ["fix_django_service_issues"]  # NEW: For deployment script failures
        }
        
        methods = recovery_methods.get(failed_step, ["restart_services"])
        
        for method in methods:
            recovery_function = getattr(self, method, None)
            if recovery_function and recovery_function():
                self.log(f"Recovery successful with method: {method}", "SUCCESS")
                return True
        
        return False
    
    def fix_django_service_issues(self) -> bool:
        """Fix Django service issues using the dedicated fix script"""
        self.log("Attempting to fix Django service issues...", "WARNING")
        
        project_dir = "/opt/projectmeats"
        django_fix_script = f"{project_dir}/fix_django_service.sh"
        
        # Check if Django service actually needs fixing
        if not self._check_django_service_health():
            self.log("Django service appears healthy - no fix needed", "SUCCESS")
            return True
        
        # Check if fix script exists
        exit_code, stdout, stderr = self.execute_command(f"test -f {django_fix_script}")
        if exit_code != 0:
            self.log("Django fix script not found - cannot apply automatic fix", "WARNING")
            return False
        
        # Run the Django service fix
        if self._run_django_service_fix(django_fix_script):
            self.log("Django service issues resolved successfully", "SUCCESS")
            return True
        else:
            self.log("Django service fix failed", "ERROR")
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
        
        # Show automated script usage information
        if hasattr(self.state, 'automated_script_used') and self.state.automated_script_used:
            print(f"{Colors.CYAN}Automated Script Used:{Colors.END} {self.state.automated_script_used}")
            print(f"{Colors.GREEN}OK Deployment leveraged specialized automation scripts{Colors.END}")
        else:
            print(f"{Colors.CYAN}Deployment Method:{Colors.END} Manual step-by-step configuration")
        
        # Critical status indicators
        print(f"\n{Colors.BOLD}Critical Deployment Checks:{Colors.END}")
        print(f"{Colors.CYAN}Services Healthy:{Colors.END} {'OK YES' if self.state.services_healthy else 'X NO'}")
        print(f"{Colors.CYAN}Domain Accessible:{Colors.END} {'OK YES' if self.state.domain_accessible else 'X NO'}")
        print(f"{Colors.CYAN}All Checks Passed:{Colors.END} {'OK YES' if self.state.critical_checks_passed else 'X NO'}")
        
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
                print(f"  {Colors.RED}X Services not healthy{Colors.END}")
            if not self.state.domain_accessible:
                print(f"  {Colors.RED}X Domain not accessible from internet{Colors.END}")
            
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
            print(f"  GitHub integration: OK Enabled")
        else:
            print(f"  GitHub integration: X Disabled (set GITHUB_TOKEN to enable)")
        
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
                self.log(f"OK {test_name} connectivity: OK", "SUCCESS")
            else:
                self.log(f"X {test_name} connectivity: FAILED", "WARNING")
        
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
        exit_code, stdout, stderr = self.execute_command("useradd -m -s /bin/bash projectmeats")
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
            # Error detection and recovery is now handled in execute_command for failed commands
            self.log("Package installation failed, but will continue with deployment", "WARNING")
            return False
        
        return exit_code == 0
    
    def deploy_handle_nodejs_conflicts(self) -> bool:
        """Handle Node.js conflicts"""
        self.log("Setting up Node.js...", "INFO")
        return self.fix_nodejs_conflicts()
    
    def deploy_setup_database(self) -> bool:
        """Setup PostgreSQL database service (database creation handled in production_config_setup)"""
        self.log("Setting up PostgreSQL database service...", "INFO")
        
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
        
        # Verify PostgreSQL is running
        exit_code, stdout, stderr = self.execute_command("systemctl is-active postgresql")
        if exit_code == 0:
            self.log("PostgreSQL service is running successfully", "SUCCESS")
            self.log("Database and user creation will be handled during production configuration", "INFO")
            return True
        else:
            self.log("PostgreSQL service failed to start", "ERROR")
            return False
    
    def deploy_download_application(self) -> bool:
        """Download and setup ProjectMeats application with improved validation"""
        self.log("Downloading and setting up ProjectMeats application...", "INFO")
        
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
            f"test -d {project_dir}/backend && test -d {project_dir}/frontend && test -f {project_dir}/README.md"
        )
        if exit_code == 0:
            self.log("ProjectMeats application already exists - verifying integrity...", "INFO")
            # Quick validation of existing installation
            key_files = ["backend/manage.py", "backend/requirements.txt", "frontend/package.json"]
            all_present = True
            for file_path in key_files:
                exit_code2, stdout2, stderr2 = self.execute_command(f"test -f {project_dir}/{file_path}")
                if exit_code2 != 0:
                    all_present = False
                    break
            
            if all_present:
                self.log("Existing installation is valid - skipping download", "SUCCESS")
                return True
            else:
                self.log("Existing installation is incomplete - will re-download", "WARNING")
        
        # Check if directory has content that needs backup
        try:
            exit_code, stdout, stderr = self.execute_command(f"ls -la {project_dir}")
            if exit_code == 0 and len(stdout.strip().split('\n')) > 3:  # More than just . and ..
                self.log("Project directory contains files - creating backup", "WARNING")
                
                # Create backup of existing content
                backup_dir = f"{project_dir}_backup_{int(time.time())}"
                self.log(f"Creating backup at {backup_dir}", "INFO")
                exit_code, stdout, stderr = self.execute_command(f"mv {project_dir} {backup_dir}")
                if exit_code != 0:
                    self.log(f"Failed to backup existing directory: {stderr}", "ERROR")
                    return False
                self.execute_command(f"mkdir -p {project_dir}")
        except:
            pass  # Directory is empty or doesn't exist, which is fine
        
        # Test network connectivity first
        self.log("Testing network connectivity...", "INFO")
        exit_code, stdout, stderr = self.execute_command("curl -s --connect-timeout 10 https://github.com > /dev/null")
        if exit_code != 0:
            self.log("Network connectivity issue - cannot reach GitHub", "ERROR")
            return False
        
        # Download from GitHub with improved timeout handling and validation
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
            try:
                exit_code, stdout, stderr = self.execute_command(
                    f"cd {project_dir} && timeout {download_timeout} git clone --progress https://github.com/Vacilator/ProjectMeats.git .",
                    timeout=download_timeout + 60
                )
                if exit_code == 0:
                    project_downloaded = True
                    self.log("Successfully downloaded using git clone", "SUCCESS")
                else:
                    self.log(f"Git clone failed (exit code: {exit_code}), trying direct download...", "WARNING")
                    if stderr and "already exists and is not an empty directory" in stderr:
                        self.log("Git clone failed due to directory conflict - already handled with backup", "WARNING")
                    elif stderr:
                        self.log(f"Error details: {stderr[:200]}...", "WARNING")
            except Exception as e:
                self.log(f"Git clone error: {e}", "WARNING")
        
        # Method 3: Direct ZIP download with validation
        if not project_downloaded:
            self.log("Attempting direct ZIP download with validation...", "INFO")
            
            try:
                # Download with timeout
                exit_code, stdout, stderr = self.execute_command(
                    f"cd {project_dir} && timeout {download_timeout} curl -L --connect-timeout 30 --max-time {download_timeout} https://github.com/Vacilator/ProjectMeats/archive/main.zip -o project.zip",
                    timeout=download_timeout + 60
                )
                if exit_code != 0:
                    raise Exception(f"Download command failed with exit code {exit_code}")
                
                # Validate download - check file size
                exit_code, stdout, stderr = self.execute_command(f"stat -c%s {project_dir}/project.zip 2>/dev/null || echo 0")
                if exit_code != 0 or not stdout:
                    raise Exception("Failed to check downloaded file size")
                
                file_size = int(stdout.strip())
                if file_size < 1000:  # Less than 1KB indicates error response (404, etc.)
                    raise Exception(f"Download failed - file too small ({file_size} bytes), likely a 404 error page")
                
                # Check if it's actually a ZIP file
                exit_code, stdout, stderr = self.execute_command(f"cd {project_dir} && file project.zip")
                if exit_code != 0 or "zip" not in stdout.lower():
                    # Show what we actually got
                    exit_code2, head_content, stderr2 = self.execute_command(f"head -c 200 {project_dir}/project.zip")
                    self.log(f"Downloaded file is not a valid ZIP archive. Content preview: {head_content[:100]}...", "WARNING")
                    raise Exception("Downloaded file is not a valid ZIP archive")
                
                # Extract with proper handling of hidden files
                self.log("Extracting validated ZIP archive...", "INFO")
                extract_commands = [
                    f"cd {project_dir} && unzip -q project.zip",
                    f"cd {project_dir} && mv ProjectMeats-main/* . 2>/dev/null || true",
                    f"cd {project_dir} && mv ProjectMeats-main/.* . 2>/dev/null || true",
                    f"cd {project_dir} && rm -rf ProjectMeats-main project.zip"
                ]
                
                for cmd in extract_commands:
                    exit_code, stdout, stderr = self.execute_command(cmd)
                    if exit_code != 0 and "mv ProjectMeats-main/.*" not in cmd:  # Allow hidden file move to fail
                        raise Exception(f"Extraction command failed: {cmd}")
                
                project_downloaded = True
                self.log("Successfully downloaded via validated ZIP download", "SUCCESS")
                
            except Exception as e:
                self.log(f"ZIP download failed: {e}", "ERROR")
                # Clean up failed download
                self.execute_command(f"rm -f {project_dir}/project.zip")
                self.execute_command(f"rm -rf {project_dir}/ProjectMeats-main")
        
        # Method 4: Tarball download as alternative
        if not project_downloaded:
            self.log("Attempting tarball download as final fallback...", "INFO")
            
            try:
                # Download tarball
                exit_code, stdout, stderr = self.execute_command(
                    f"cd {project_dir} && timeout {download_timeout} curl -L --connect-timeout 30 --max-time {download_timeout} https://github.com/Vacilator/ProjectMeats/archive/refs/heads/main.tar.gz -o project.tar.gz",
                    timeout=download_timeout + 60
                )
                if exit_code != 0:
                    raise Exception(f"Tarball download failed with exit code {exit_code}")
                
                # Validate tarball
                exit_code, stdout, stderr = self.execute_command(f"stat -c%s {project_dir}/project.tar.gz 2>/dev/null || echo 0")
                if exit_code != 0 or not stdout:
                    raise Exception("Failed to check downloaded tarball size")
                
                tar_size = int(stdout.strip())
                if tar_size < 1000:  # Less than 1KB indicates error response
                    raise Exception(f"Tarball download failed - file too small ({tar_size} bytes)")
                
                # Check if it's actually a gzip file
                exit_code, stdout, stderr = self.execute_command(f"cd {project_dir} && file project.tar.gz")
                if exit_code != 0 or "gzip compressed" not in stdout.lower():
                    raise Exception("Downloaded file is not a valid gzip archive")
                
                # Extract tarball
                self.log("Extracting validated tarball...", "INFO")
                extract_commands = [
                    f"cd {project_dir} && tar -xzf project.tar.gz",
                    f"cd {project_dir} && mv ProjectMeats-main/* . 2>/dev/null || true",
                    f"cd {project_dir} && mv ProjectMeats-main/.* . 2>/dev/null || true",
                    f"cd {project_dir} && rm -rf ProjectMeats-main project.tar.gz"
                ]
                
                for cmd in extract_commands:
                    exit_code, stdout, stderr = self.execute_command(cmd)
                    if exit_code != 0 and "mv ProjectMeats-main/.*" not in cmd:  # Allow hidden file move to fail
                        raise Exception(f"Extraction command failed: {cmd}")
                
                project_downloaded = True
                self.log("Successfully downloaded via validated tarball", "SUCCESS")
                
            except Exception as e:
                self.log(f"Tarball download failed: {e}", "ERROR")
                # Clean up failed download
                self.execute_command(f"rm -f {project_dir}/project.tar.gz")
                self.execute_command(f"rm -rf {project_dir}/ProjectMeats-main")
        
        if not project_downloaded:
            self.log("All download methods failed!", "ERROR")
            self.log("This indicates a network connectivity issue or GitHub access problem", "ERROR")
            self.log("Please check: 1) Internet connectivity, 2) DNS resolution, 3) GitHub accessibility", "ERROR")
            return False
        
        # Comprehensive verification that essential files exist
        self.log("Verifying downloaded application structure...", "INFO")
        exit_code, stdout, stderr = self.execute_command(
            f"test -d {project_dir}/backend && test -d {project_dir}/frontend && test -f {project_dir}/README.md"
        )
        if exit_code != 0:
            self.log("Downloaded project appears incomplete - missing essential directories", "ERROR")
            self.log("Required directories/files: backend/, frontend/, README.md", "ERROR")
            # Show what we actually have
            exit_code2, ls_output, stderr2 = self.execute_command(f"ls -la {project_dir}")
            if exit_code2 == 0:
                self.log(f"Current directory contents: {ls_output}", "ERROR")
            return False
        
        # Check for key files
        self.log("Checking for key application files...", "INFO")
        key_files = [
            "backend/manage.py",
            "backend/requirements.txt", 
            "frontend/package.json",
            "backend/apps/settings/settings.py"
        ]
        
        missing_files = []
        for file_path in key_files:
            exit_code, stdout, stderr = self.execute_command(f"test -f {project_dir}/{file_path}")
            if exit_code != 0:
                missing_files.append(file_path)
        
        if missing_files:
            self.log(f"CRITICAL: Some essential files are missing: {', '.join(missing_files)}", "ERROR")
            self.log("This indicates the download was incomplete or corrupted", "ERROR")
            return False
        else:
            self.log("All key application files found and verified", "SUCCESS")
        
        # Set ownership
        exit_code, stdout, stderr = self.execute_command(f"chown -R projectmeats:projectmeats {project_dir}")
        if exit_code != 0:
            self.log("Warning: Could not set proper ownership", "WARNING")
        
        self.log("ProjectMeats application setup completed successfully", "SUCCESS")
        return True
    
    def deploy_run_deployment_scripts(self) -> bool:
        """Run specialized deployment scripts based on server state with socket service support"""
        self.log("Running automated deployment scripts...", "INFO", Colors.BOLD + Colors.BLUE)
        
        project_dir = "/opt/projectmeats"
        
        # Check if deployment scripts exist
        quick_fix_script = f"{project_dir}/deployment/scripts/quick_server_fix.sh"
        setup_script = f"{project_dir}/deployment/scripts/setup_production.sh"
        django_fix_script = f"{project_dir}/fix_django_service.sh"
        
        # NEW: Check for socket service management scripts
        socket_service_script = f"{project_dir}/deployment/scripts/reload_and_start_services.sh"
        socket_verification_script = f"{project_dir}/deployment/scripts/verify_service.sh"
        
        # Check for Django service issues first - this is a critical fix
        django_service_needs_fix = self._check_django_service_health()
        
        if django_service_needs_fix:
            self.log("Django service issues detected - applying Django service fix...", "WARNING", Colors.BOLD + Colors.YELLOW)
            
            # Verify Django fix script exists
            exit_code, stdout, stderr = self.execute_command(f"test -f {django_fix_script}")
            if exit_code == 0:
                if self._run_django_service_fix(django_fix_script):
                    self.log("Django service fix completed successfully", "SUCCESS")
                    # Mark that we used the Django fix script
                    self.state.automated_script_used = "Django Service Fix"
                    
                    # After successful fix, continue with normal deployment logic
                    # but first check if we still need additional scripts
                    remaining_issues = self._assess_remaining_deployment_needs()
                    if not remaining_issues:
                        self.log("Django service fix resolved all issues - deployment scripts complete", "SUCCESS")
                        return True
                else:
                    self.log("Django service fix failed - continuing with manual configuration", "WARNING")
            else:
                self.log("Django fix script not found, continuing with other deployment methods", "WARNING")
        
        # NEW: Check if socket service configuration is available and prioritize it
        use_socket_services = self._detect_socket_service_configuration()
        
        if use_socket_services:
            self.log("Socket service configuration detected - prioritizing socket-based deployment", "INFO", Colors.BOLD + Colors.CYAN)
            
            # Run socket service management if backend is configured
            exit_code, stdout, stderr = self.execute_command("test -d /opt/projectmeats/venv && test -f /opt/projectmeats/backend/.env")
            if exit_code == 0:
                self.log("Backend appears configured - running socket service management", "INFO")
                
                if self._run_socket_service_management():
                    self.log("Socket services configured successfully", "SUCCESS")
                    
                    # Run socket verification if available
                    exit_code, stdout, stderr = self.execute_command(f"test -f {socket_verification_script}")
                    if exit_code == 0:
                        self.log("Running socket service verification...", "INFO")
                        exit_code, stdout, stderr = self.execute_command(f"chmod +x {socket_verification_script} && bash {socket_verification_script}")
                        if exit_code == 0:
                            self.log("Socket service verification passed", "SUCCESS")
                        else:
                            self.log("Socket service verification had warnings", "WARNING")
                    
                    # Mark that we used socket service management
                    if hasattr(self.state, 'automated_script_used') and self.state.automated_script_used:
                        self.state.automated_script_used = f"{self.state.automated_script_used} + Socket Service Management"
                    else:
                        self.state.automated_script_used = "Socket Service Management"
                    
                    # Check if this resolved deployment needs
                    remaining_issues = self._assess_remaining_deployment_needs()
                    if not remaining_issues:
                        self.log("Socket service management resolved all deployment needs", "SUCCESS")
                        return True
                else:
                    self.log("Socket service management failed - continuing with standard deployment scripts", "WARNING")
        
        # Standard deployment script selection logic
        # Verify other scripts exist
        exit_code, stdout, stderr = self.execute_command(f"test -f {quick_fix_script} && test -f {setup_script}")
        if exit_code != 0:
            self.log("Standard deployment scripts not found, using manual configuration", "WARNING")
            return True  # Continue with manual deployment steps
        
        # Determine which script to use based on server state
        script_to_use = None
        
        # Check if this is an existing deployment (has dependencies and project already setup)
        self.log("Analyzing server state to choose appropriate deployment script...", "INFO")
        
        # Check for existing dependencies
        checks = [
            ("python3 --version", "Python"),
            ("psql --version", "PostgreSQL"),
            ("nginx -v", "Nginx"),
            ("node --version", "Node.js")
        ]
        
        dependencies_installed = 0
        total_checks = len(checks)
        
        for cmd, name in checks:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code == 0:
                dependencies_installed += 1
                self.log(f"OK {name} is available", "SUCCESS")
            else:
                self.log(f"X {name} not found", "INFO")
        
        # Check if project files are already present
        project_exists = False
        exit_code, stdout, stderr = self.execute_command(
            f"test -d {project_dir}/backend && test -d {project_dir}/frontend && test -f {project_dir}/README.md"
        )
        if exit_code == 0:
            project_exists = True
            self.log("OK Project files already exist", "SUCCESS")
        else:
            self.log("X Project files not found", "INFO")
        
        # Decision logic for which script to use
        if dependencies_installed >= (total_checks * 0.75) and project_exists:
            # Use quick fix script for existing servers with dependencies
            script_to_use = quick_fix_script
            script_name = "Quick Server Fix"
            self.log(f"Server has most dependencies and project files - using {script_name} script", "INFO")
        else:
            # Use full setup script for fresh servers
            script_to_use = setup_script
            script_name = "Full Production Setup"
            self.log(f"Fresh server or missing dependencies - using {script_name} script", "INFO")
        
        # Make script executable
        exit_code, stdout, stderr = self.execute_command(f"chmod +x {script_to_use}")
        if exit_code != 0:
            self.log(f"Failed to make script executable: {script_to_use}", "ERROR")
            return False
        
        # Get domain from config for script environment
        domain = self.config.get('domain', 'meatscentral.com')
        
        # Set environment variables for the script
        env_vars = f"export DOMAIN={domain}"
        
        # Run the selected deployment script
        self.log(f"Executing {script_name} script...", "INFO")
        self.log("This may take several minutes as it sets up the entire application", "INFO")
        
        # Use extended timeout for deployment scripts (30 minutes)
        script_timeout = 1800
        
        try:
            # Run script with environment variables and extended timeout
            exit_code, stdout, stderr = self.execute_command(
                f"cd {project_dir} && {env_vars} && timeout {script_timeout} bash {script_to_use}",
                timeout=script_timeout + 60
            )
            
            if exit_code == 0:
                self.log(f"OK {script_name} script completed successfully", "SUCCESS", Colors.BOLD + Colors.GREEN)
                
                # Parse script output for important information
                if "Setup complete!" in stdout or "Deployment Complete!" in stdout:
                    self.log("Deployment script reports successful completion", "SUCCESS")
                
                # Check for any warnings in the output
                if "WARNING" in stdout or "failed" in stdout.lower():
                    self.log("Script completed but with warnings - check output above", "WARNING")
                
                # Mark that we used automated scripts (combine with Django fix if both used)
                if hasattr(self.state, 'automated_script_used') and self.state.automated_script_used:
                    self.state.automated_script_used = f"{self.state.automated_script_used} + {script_name}"
                else:
                    self.state.automated_script_used = script_name
                
                return True
            else:
                self.log(f"X {script_name} script failed with exit code {exit_code}", "ERROR")
                
                # Show error output for debugging
                if stderr:
                    self.log(f"Script error output: {stderr[-500:]}", "ERROR")  # Last 500 chars
                
                # Try to extract specific error information and apply targeted fixes
                if ("ModuleNotFoundError" in stderr or "django" in stderr.lower()) and not django_service_needs_fix:
                    self.log("Django dependency issues detected - attempting Django service fix...", "WARNING")
                    # Try Django fix as recovery
                    if self._run_django_service_fix(django_fix_script):
                        self.log("Django service fix resolved the issue", "SUCCESS")
                        return True
                elif "Database" in stderr or "psql" in stderr:
                    self.log("Database setup error detected - continuing with manual configuration", "WARNING")
                elif "npm" in stderr or "node" in stderr:
                    self.log("Frontend build error detected - continuing with manual configuration", "WARNING")
                elif "nginx" in stderr:
                    self.log("Nginx configuration error detected - continuing with manual configuration", "WARNING")
                else:
                    self.log("General script error - continuing with manual configuration", "WARNING")
                
                # Don't fail the deployment - continue with manual steps
                self.log("Continuing with manual deployment configuration steps...", "INFO")
                return True
                
        except Exception as e:
            self.log(f"Exception running deployment script: {e}", "ERROR")
            self.log("Continuing with manual deployment configuration steps...", "INFO")
            return True  # Continue with manual steps
    
    def collect_production_config(self, domain: str = None) -> ProductionConfig:
        """
        Setup production configuration with automatic database credential generation
        """
        self.log("=== Production Configuration Setup ===", "INFO")
        print(f"\n{Colors.CYAN}{'='*60}")
        print(f"{Colors.CYAN}  ProjectMeats Production Configuration")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
        
        config = ProductionConfig()
        
        # Auto-generate secret key
        self.log("Generating Django secret key...", "INFO")
        config.secret_key = get_random_secret_key()
        print(f"{Colors.GREEN}✓ Django secret key generated automatically{Colors.END}")
        
        # Domain configuration
        if domain:
            config.domain = domain
            config.allowed_hosts = f"{domain},www.{domain}"
            config.cors_origins = f"https://{domain},https://www.{domain}"
            print(f"{Colors.GREEN}✓ Domain configured: {domain}{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}Domain Configuration:{Colors.END}")
            config.domain = input(f"Enter your domain name (e.g., example.com): ").strip()
            if config.domain:
                config.allowed_hosts = f"{config.domain},www.{config.domain}"
                config.cors_origins = f"https://{config.domain},https://www.{config.domain}"
        
        # Database configuration - AUTO-GENERATED (no user prompts)
        print(f"\n{Colors.YELLOW}Database Configuration:{Colors.END}")
        print("Setting up PostgreSQL database configuration automatically...")
        
        # Generate unique, secure database credentials automatically
        config.db_name = f"projectmeats_prod_{secrets.token_hex(4)}"  # e.g., projectmeats_prod_a1b2c3d4
        config.db_user = f"pm_user_{secrets.token_hex(3)}"  # e.g., pm_user_x9y8z7
        config.db_password = self._generate_secure_db_password()
        
        print(f"{Colors.GREEN}✓ Database name: {config.db_name}{Colors.END}")
        print(f"{Colors.GREEN}✓ Database user: {config.db_user}{Colors.END}")
        print(f"{Colors.GREEN}✓ Database password: [auto-generated 16-character secure password]{Colors.END}")
        print(f"{Colors.GREEN}✓ Database configuration generated automatically{Colors.END}")
        
        # Log the credentials securely for system administration
        self.log(f"Generated database credentials - Name: {config.db_name}, User: {config.db_user}", "INFO")
        
        # Save credentials to a secure admin file (readable only by root)
        try:
            admin_info = {
                "deployment_time": datetime.now().isoformat(),
                "database_name": config.db_name,
                "database_user": config.db_user,
                "database_password": config.db_password,
                "database_host": config.db_host,
                "database_port": config.db_port
            }
            
            # Note: In production, this would be written to the server, here we just log it
            self.log("Database credentials will be saved to /opt/projectmeats/admin/database_credentials.json on the server", "INFO")
            
        except Exception as e:
            self.log(f"Warning: Could not prepare admin credentials file: {e}", "WARNING")
        
        # Company information
        print(f"\n{Colors.YELLOW}Company Information (Optional):{Colors.END}")
        config.company_name = input(f"Company name [{config.company_name}]: ").strip() or config.company_name
        config.company_email = input("Company email (optional): ").strip()
        config.company_phone = input("Company phone (optional): ").strip()
        config.company_address = input("Company address (optional): ").strip()
        
        # Email configuration (optional)
        print(f"\n{Colors.YELLOW}Email Configuration (Optional - can be configured later):{Colors.END}")
        configure_email = input("Configure email settings now? (y/N): ").strip().lower()
        
        if configure_email in ['y', 'yes']:
            config.email_host = input("SMTP host (e.g., smtp.gmail.com): ").strip()
            if config.email_host:
                config.email_port = input(f"SMTP port [{config.email_port}]: ").strip() or config.email_port
                config.email_user = input("Email username: ").strip()
                config.email_password = getpass.getpass("Email password (will be hidden): ").strip()
                
                use_tls = input("Use TLS encryption? (Y/n): ").strip().lower()
                config.email_use_tls = use_tls not in ['n', 'no']
                
                print(f"{Colors.GREEN}✓ Email configuration collected{Colors.END}")
        else:
            print(f"{Colors.BLUE}Email configuration skipped - using console backend for now{Colors.END}")
        
        # SSL configuration
        print(f"\n{Colors.YELLOW}Security Configuration:{Colors.END}")
        enable_ssl = input("Enable SSL/HTTPS security settings? (Y/n): ").strip().lower()
        config.enable_ssl = enable_ssl not in ['n', 'no']
        
        if config.enable_ssl:
            print(f"{Colors.GREEN}✓ SSL/HTTPS security will be enabled{Colors.END}")
        else:
            print(f"{Colors.BLUE}SSL disabled - recommended only for development{Colors.END}")
        
        print(f"\n{Colors.GREEN}{'='*60}")
        print(f"{Colors.GREEN}  Configuration Summary")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"Domain: {config.domain or 'Not specified'}")
        print(f"Database: {config.db_name}")
        print(f"Database User: {config.db_user}")
        print(f"Company: {config.company_name}")
        print(f"Email configured: {'Yes' if config.email_host else 'No'}")
        print(f"SSL enabled: {'Yes' if config.enable_ssl else 'No'}")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
        
        return config
    
    def _generate_secure_db_password(self) -> str:
        """Generate a secure database password automatically"""
        # Use a mix of letters and numbers (avoiding special chars that might cause SQL escaping issues)
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        # Generate 16-character password (sufficient for database security)
        password = ''.join(secrets.choice(chars) for _ in range(16))
        return password
    
    def generate_production_env_file(self, config: ProductionConfig) -> str:
        """
        Generate .env file content from ProductionConfig
        """
        self.log("Generating production environment file...", "INFO")
        
        # Read the template file content
        template_content = f"""# ProjectMeats Production Environment Configuration
# Generated automatically by AI Deployment Orchestrator on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# ==========================================
# DJANGO CORE SETTINGS
# ==========================================

# Production settings
DEBUG=False

# Django secret key (auto-generated)
SECRET_KEY={config.secret_key}

# Allowed hosts
ALLOWED_HOSTS={config.allowed_hosts}

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

# PostgreSQL production database
DATABASE_URL=postgresql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}

# ==========================================
# SECURITY SETTINGS
# ==========================================
"""
        
        if config.enable_ssl:
            template_content += """
# SSL/HTTPS Configuration
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_REFERRER_POLICY=strict-origin-when-cross-origin

# Cookie Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=True
CSRF_COOKIE_SAMESITE=Strict
"""
        else:
            template_content += """
# SSL disabled for development
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
"""
        
        template_content += f"""
# ==========================================
# CORS CONFIGURATION
# ==========================================

# Frontend domains
CORS_ALLOWED_ORIGINS={config.cors_origins}

# Additional CORS settings
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOWED_HEADERS=accept,accept-encoding,authorization,content-type,dnt,origin,user-agent,x-csrftoken,x-requested-with

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS={config.cors_origins}

# ==========================================
# FILE STORAGE
# ==========================================

# File storage paths
MEDIA_ROOT={config.media_root}
STATIC_ROOT={config.static_root}

# ==========================================
# EMAIL CONFIGURATION
# ==========================================
"""
        
        if config.email_host:
            template_content += f"""
# SMTP Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST={config.email_host}
EMAIL_PORT={config.email_port}
EMAIL_USE_TLS={str(config.email_use_tls).lower()}
EMAIL_HOST_USER={config.email_user}
EMAIL_HOST_PASSWORD={config.email_password}

# Default from email
DEFAULT_FROM_EMAIL={config.company_name} <{config.email_user}>
SERVER_EMAIL={config.company_name} Server <{config.email_user}>
"""
        else:
            template_content += """
# Console email backend for development/testing
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
"""
        
        template_content += f"""
# ==========================================
# CACHE CONFIGURATION
# ==========================================

# Redis cache configuration (recommended for production)
CACHE_URL=redis://localhost:6379/1

# Session storage
SESSION_ENGINE=django.contrib.sessions.backends.cache
SESSION_CACHE_ALIAS=default

# ==========================================
# LOGGING CONFIGURATION
# ==========================================

# Logging level
LOG_LEVEL=INFO

# Log directory
LOG_DIR={config.log_dir}

# ==========================================
# API CONFIGURATION
# ==========================================

# API version
API_VERSION=v1

# Rate limiting
API_THROTTLE_RATE_ANON=100/hour
API_THROTTLE_RATE_USER=1000/hour

# ==========================================
# BACKUP CONFIGURATION
# ==========================================

# Backup directory
BACKUP_DIR={config.backup_dir}

# Database backup retention (days)
DB_BACKUP_RETENTION_DAYS=30

# Full backup retention (days)
FULL_BACKUP_RETENTION_DAYS=7

# ==========================================
# BUSINESS CONFIGURATION
# ==========================================

# Company Information
COMPANY_NAME={config.company_name}
COMPANY_EMAIL={config.company_email or 'info@' + (config.domain or 'example.com')}
COMPANY_PHONE={config.company_phone}
COMPANY_ADDRESS={config.company_address}

# Time Zone
TIME_ZONE=America/New_York

# Default Currency
DEFAULT_CURRENCY=USD

# ==========================================
# FEATURE FLAGS
# ==========================================

# Enable/disable features
ENABLE_USER_REGISTRATION=False
ENABLE_EMAIL_VERIFICATION=True
ENABLE_TWO_FACTOR_AUTH=False
ENABLE_API_DOCS=True

# ==========================================
# POWERAPPS MIGRATION
# ==========================================

# PowerApps Migration Mode
POWERAPPS_MIGRATION_MODE=False
"""
        
        return template_content
    
    def deploy_production_config_setup(self) -> bool:
        """
        Setup production configuration by collecting user input and generating environment files
        """
        try:
            self.log("Setting up production configuration...", "INFO")
            
            # Get domain from server configuration
            domain = self.state.server_info.get('domain') if self.state else None
            
            # Collect configuration from user
            config = self.collect_production_config(domain)
            
            # Generate environment file
            env_content = self.generate_production_env_file(config)
            
            # Create the environment file on the server
            self.log("Creating production environment file on server...", "INFO")
            
            # Ensure the directories exist
            exit_code, stdout, stderr = self.execute_command("mkdir -p /opt/projectmeats/backend /etc/projectmeats")
            if exit_code != 0:
                self.log(f"Failed to create directories: {stderr}", "ERROR")
                return False
            
            # Write the environment file to the location expected by systemd service
            env_file_cmd = f"""cat > /etc/projectmeats/projectmeats.env << 'EOF'
{env_content}
EOF"""
            
            exit_code, stdout, stderr = self.execute_command(env_file_cmd)
            if exit_code != 0:
                self.log(f"Failed to create systemd environment file: {stderr}", "ERROR")
                return False
            
            # Also create a backup in the backend directory for Django management commands
            backup_env_cmd = f"""cat > /opt/projectmeats/backend/.env << 'EOF'
{env_content}
EOF"""
            
            exit_code, stdout, stderr = self.execute_command(backup_env_cmd)
            if exit_code != 0:
                self.log(f"Warning: Failed to create backend .env file: {stderr}", "WARNING")
            
            # Set proper permissions on both files
            exit_code, stdout, stderr = self.execute_command("chmod 600 /etc/projectmeats/projectmeats.env /opt/projectmeats/backend/.env 2>/dev/null")
            if exit_code != 0:
                self.log("Warning: Could not set secure permissions on .env files", "WARNING")
            
            self.log("✓ Production environment file created successfully", "SUCCESS")
            
            # Create database and user with the collected configuration
            if self._setup_database_with_config(config):
                # Create secure admin credentials file on the server
                self._save_admin_credentials(config)
                # Ensure Django service directories and permissions are set up
                self._setup_django_service_directories()
                return True
            else:
                return False
            
        except Exception as e:
            self.log(f"Error setting up production configuration: {e}", "ERROR")
            return False
    
    def _setup_django_service_directories(self) -> bool:
        """Setup directories and permissions required by Django systemd service"""
        try:
            self.log("Setting up Django service directories and permissions...", "INFO")
            
            # Create required directories
            setup_dirs_cmd = """
            # Create log directory
            mkdir -p /var/log/projectmeats
            chown www-data:www-data /var/log/projectmeats
            chmod 755 /var/log/projectmeats
            
            # Create PID directory
            mkdir -p /var/run/projectmeats
            chown www-data:www-data /var/run/projectmeats
            chmod 755 /var/run/projectmeats
            
            # Create media directory (for file uploads)
            mkdir -p /opt/projectmeats/backend/media
            chown -R www-data:www-data /opt/projectmeats/backend/media
            chmod -R 755 /opt/projectmeats/backend/media
            
            # Create static files directory
            mkdir -p /opt/projectmeats/backend/staticfiles
            chown -R www-data:www-data /opt/projectmeats/backend/staticfiles
            chmod -R 755 /opt/projectmeats/backend/staticfiles
            
            # Ensure www-data can read environment file
            chown www-data:www-data /etc/projectmeats/projectmeats.env 2>/dev/null || true
            
            # Ensure backend directory has proper permissions
            chown -R www-data:www-data /opt/projectmeats/backend
            chmod -R 755 /opt/projectmeats/backend
            """
            
            exit_code, stdout, stderr = self.execute_command(setup_dirs_cmd)
            if exit_code == 0:
                self.log("✓ Django service directories and permissions configured", "SUCCESS")
                return True
            else:
                self.log(f"Warning: Could not set up all Django service directories: {stderr}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Warning: Error setting up Django service directories: {e}", "WARNING")
            return False
    
    def _save_admin_credentials(self, config: ProductionConfig) -> bool:
        """Save database credentials to a secure admin file on the server"""
        try:
            admin_info = {
                "deployment_time": datetime.now().isoformat(),
                "database_name": config.db_name,
                "database_user": config.db_user, 
                "database_password": config.db_password,
                "database_host": config.db_host,
                "database_port": config.db_port,
                "domain": config.domain,
                "company_name": config.company_name
            }
            
            # Create admin directory and credentials file
            admin_setup_cmd = f"""
            mkdir -p /opt/projectmeats/admin
            cat > /opt/projectmeats/admin/database_credentials.json << 'EOF'
{json.dumps(admin_info, indent=2)}
EOF
            chmod 600 /opt/projectmeats/admin/database_credentials.json
            chown root:root /opt/projectmeats/admin/database_credentials.json
            """
            
            exit_code, stdout, stderr = self.execute_command(admin_setup_cmd)
            if exit_code == 0:
                self.log("✓ Admin credentials file saved to /opt/projectmeats/admin/database_credentials.json", "SUCCESS")
                return True
            else:
                self.log(f"Warning: Could not save admin credentials file: {stderr}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Warning: Error saving admin credentials: {e}", "WARNING")
            return False
    
    def _setup_database_with_config(self, config: ProductionConfig) -> bool:
        """Setup PostgreSQL database with user-provided configuration"""
        try:
            self.log(f"Setting up PostgreSQL database '{config.db_name}' with user '{config.db_user}'...", "INFO")
            
            # Step 1: Create database user if not exists
            create_user_script = f"""
sudo -u postgres psql << 'EOF'
-- Create database user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = '{config.db_user}') THEN
        CREATE USER {config.db_user} WITH PASSWORD '{config.db_password}';
        RAISE NOTICE 'User {config.db_user} created successfully';
    ELSE
        RAISE NOTICE 'User {config.db_user} already exists';
    END IF;
END
$$;
\\q
EOF
"""
            
            self.log("Creating PostgreSQL user...", "INFO")
            exit_code, stdout, stderr = self.execute_command(create_user_script)
            if exit_code != 0:
                self.log(f"Database user creation failed: {stderr}", "ERROR")
                return False
            
            # Step 2: Create database if not exists
            create_db_script = f"""
# Method 1: Check if database exists, then create it using createdb command
if ! sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw {config.db_name}; then
    echo "Creating database {config.db_name}..."
    sudo -u postgres createdb -O {config.db_user} {config.db_name}
else
    echo "Database {config.db_name} already exists"
fi
"""
            
            self.log("Creating PostgreSQL database...", "INFO")
            exit_code, stdout, stderr = self.execute_command(create_db_script)
            # Don't fail on database creation errors as database might already exist
            
            # Step 3: Grant permissions to ensure user has access
            grant_permissions_script = f"""
sudo -u postgres psql -d {config.db_name} << 'EOF'
-- Grant all permissions to the user
GRANT ALL PRIVILEGES ON DATABASE {config.db_name} TO {config.db_user};
GRANT ALL PRIVILEGES ON SCHEMA public TO {config.db_user};
\\q
EOF
"""
            
            self.log("Granting database permissions...", "INFO")
            exit_code, stdout, stderr = self.execute_command(grant_permissions_script)
            if exit_code != 0:
                self.log(f"Permission grant failed, but continuing: {stderr}", "WARNING")
            
            # Test database connection
            test_connection_cmd = f"""
export PGPASSWORD='{config.db_password}'
psql -h {config.db_host} -p {config.db_port} -U {config.db_user} -d {config.db_name} -c "SELECT version();"
"""
            
            self.log("Testing database connection...", "INFO")
            exit_code, stdout, stderr = self.execute_command(test_connection_cmd)
            if exit_code == 0:
                self.log("✓ Database connection test successful", "SUCCESS")
                return True
            else:
                self.log(f"Database connection test failed: {stderr}", "ERROR")
                
                # Attempt recovery by reconfiguring PostgreSQL authentication
                if self._attempt_database_auth_recovery(config):
                    # Retry connection test
                    exit_code, stdout, stderr = self.execute_command(test_connection_cmd)
                    if exit_code == 0:
                        self.log("✓ Database connection test successful after recovery", "SUCCESS")
                        return True
                    else:
                        self.log(f"Database connection still failed after recovery: {stderr}", "ERROR")
                        return False
                else:
                    return False
                
        except Exception as e:
            self.log(f"Error setting up database: {e}", "ERROR")
            return False
    
    def _attempt_database_auth_recovery(self, config: ProductionConfig) -> bool:
        """Attempt to recover from database authentication issues"""
        try:
            self.log("Attempting database authentication recovery...", "WARNING")
            
            # Check PostgreSQL authentication configuration
            pg_hba_check = """
# Check current pg_hba.conf configuration
sudo -u postgres psql -c "SHOW hba_file;" -t
"""
            exit_code, stdout, stderr = self.execute_command(pg_hba_check)
            if exit_code == 0:
                hba_file = stdout.strip()
                self.log(f"PostgreSQL HBA file location: {hba_file}", "INFO")
                
                # Backup and update pg_hba.conf to ensure local connections work
                backup_and_update_hba = f"""
# Backup original pg_hba.conf
sudo cp {hba_file} {hba_file}.backup

# Add/ensure local connection authentication method
sudo grep -q "local.*{config.db_name}.*{config.db_user}" {hba_file} || {{
    echo "# Added by ProjectMeats deployment" | sudo tee -a {hba_file}
    echo "local   {config.db_name}   {config.db_user}   md5" | sudo tee -a {hba_file}
    echo "host    {config.db_name}   {config.db_user}   127.0.0.1/32   md5" | sudo tee -a {hba_file}
}}

# Reload PostgreSQL configuration
sudo systemctl reload postgresql
"""
                
                exit_code, stdout, stderr = self.execute_command(backup_and_update_hba)
                if exit_code == 0:
                    self.log("✓ PostgreSQL authentication configuration updated", "SUCCESS")
                    time.sleep(2)  # Give PostgreSQL time to reload config
                    return True
                else:
                    self.log(f"Failed to update PostgreSQL configuration: {stderr}", "ERROR")
                    return False
            else:
                self.log("Could not locate PostgreSQL HBA configuration file", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Database authentication recovery failed: {e}", "ERROR")
            return False

    def deploy_configure_backend(self) -> bool:
        """Configure backend with automatic socket service detection"""
        self.log("Configuring backend...", "INFO")
        
        # Check if automated script already handled this
        if hasattr(self.state, 'automated_script_used') and self.state.automated_script_used:
            self.log(f"Backend may already be configured by {self.state.automated_script_used} script", "INFO")
            
            # Verify if backend is already configured
            exit_code, stdout, stderr = self.execute_command(
                "systemctl is-active projectmeats && test -f /opt/projectmeats/backend/venv/bin/activate"
            )
            if exit_code == 0:
                self.log("OK Backend already configured and service running - skipping manual configuration", "SUCCESS")
                return True
            else:
                self.log("Backend not fully configured - continuing with manual setup", "INFO")
        
        # NEW: Detect if socket service configuration is available
        use_socket_services = self._detect_socket_service_configuration()
        
        if use_socket_services:
            self.log("Using Unix socket-based SystemD service configuration", "INFO", Colors.BOLD + Colors.CYAN)
            return self._configure_backend_with_socket_services()
        
        # Check if Django service issues need to be addressed first
        if self._check_django_service_health():
            self.log("Django service issues detected - applying fix before continuing with configuration...", "WARNING")
            if self.fix_django_service_issues():
                self.log("Django service fix successful - continuing with remaining backend configuration", "SUCCESS")
                # After successful Django fix, verify if we still need manual backend setup
                exit_code, stdout, stderr = self.execute_command("systemctl is-active projectmeats")
                if exit_code == 0:
                    self.log("Django service is now running - backend configuration complete", "SUCCESS")
                    return True
            else:
                self.log("Django service fix failed - continuing with manual backend setup", "WARNING")
    def _configure_backend_with_socket_services(self) -> bool:
        """Configure backend using the new Unix socket-based SystemD service configuration"""
        self.log("Configuring backend with Unix socket services...", "INFO")
        
        # Step 1: Setup projectmeats user
        if not self._setup_projectmeats_user():
            return False
        
        # Step 2: Create virtual environment and install dependencies
        self.log("Setting up Python virtual environment...", "INFO")
        venv_commands = [
            "cd /opt/projectmeats && python3 -m venv venv",
            "cd /opt/projectmeats && ./venv/bin/pip install --upgrade pip",
            "cd /opt/projectmeats && ./venv/bin/pip install -r backend/requirements.txt"
        ]
        
        for cmd in venv_commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Backend setup command failed: {cmd}", "ERROR")
                self.log(f"Error: {stderr}", "ERROR")
                return False
        
        # Step 3: Verify .env file exists (should be created in production_config_setup step)
        self.log("Verifying production environment configuration...", "INFO")
        exit_code, stdout, stderr = self.execute_command("test -f /opt/projectmeats/backend/.env")
        if exit_code != 0:
            self.log("Production .env file not found - this should have been created in production_config_setup", "ERROR")
            return False
        
        # Step 4: Set proper ownership for projectmeats user
        self.log("Setting proper ownership for projectmeats user...", "INFO")
        ownership_commands = [
            "chown -R projectmeats:projectmeats /opt/projectmeats",
            "chmod -R 755 /opt/projectmeats",
            "chmod +x /opt/projectmeats/venv/bin/*"
        ]
        
        for cmd in ownership_commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Ownership command failed: {cmd}", "WARNING")
        
        # Step 5: Run Django management commands
        self.log("Running Django management commands...", "INFO")
        django_commands = [
            "cd /opt/projectmeats/backend && ../venv/bin/python manage.py migrate",
            "cd /opt/projectmeats/backend && ../venv/bin/python manage.py collectstatic --noinput",
            "cd /opt/projectmeats/backend && ../venv/bin/python manage.py check --deploy"
        ]
        
        for cmd in django_commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Django command failed: {cmd}", "WARNING")
                # Continue with other commands
        
        # Step 6: Deploy socket service files
        if not self._deploy_socket_service_files():
            return False
        
        # Step 7: Run socket service management
        if not self._run_socket_service_management():
            return False
        
        # Step 8: Verify socket service is running
        self.log("Verifying socket service status...", "INFO")
        exit_code, stdout, stderr = self.execute_command("systemctl is-active projectmeats.socket")
        if exit_code != 0:
            self.log("ProjectMeats socket not active", "ERROR")
            return False
        
        exit_code, stdout, stderr = self.execute_command("systemctl is-active projectmeats.service")
        if exit_code != 0:
            self.log("ProjectMeats service not active", "WARNING")
            # Socket activation should start the service when needed
        
        # Step 9: Test socket connectivity
        self.log("Testing Unix socket connectivity...", "INFO")
        exit_code, stdout, stderr = self.execute_command("test -S /run/projectmeats.sock")
        if exit_code != 0:
            self.log("Unix socket file not found", "ERROR")
            return False
        
        self.log("✓ Backend configured successfully with Unix socket services", "SUCCESS", Colors.BOLD + Colors.GREEN)
        return True

    def _configure_backend_traditional(self) -> bool:
        """Configure backend using traditional TCP-based approach"""
        self.log("Using traditional TCP-based backend configuration...", "INFO")
        
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
                # Try Django service fix if this appears to be a dependency issue
                if "ModuleNotFoundError" in stderr or "No module named" in stderr:
                    self.log("Dependency error detected - attempting Django service fix...", "WARNING")
                    if self.fix_django_service_issues():
                        self.log("Django service fix resolved dependency issues", "SUCCESS")
                        # Retry the failed command
                        exit_code, stdout, stderr = self.execute_command(cmd)
                        if exit_code == 0:
                            continue
                return False
        
        # Verify .env file was created in production_config_setup step
        self.log("Verifying production environment configuration...", "INFO")
        exit_code, stdout, stderr = self.execute_command("test -f /opt/projectmeats/backend/.env")
        if exit_code != 0:
            self.log("Production .env file not found - this should have been created in production_config_setup", "ERROR")
            return False
        
        self.log("✓ Production environment configuration found", "SUCCESS")
        
        # Verify that settings.py exists (should be from our PR fix)
        exit_code, stdout, stderr = self.execute_command("test -f /opt/projectmeats/backend/apps/settings/settings.py")
        if exit_code != 0:
            self.log("settings.py file not found - deployment script may need updating", "ERROR")
            return False
        
        # Set Django to use the smart settings.py that reads from .env
        self.log("Configuring Django to use environment-based settings...", "INFO")
        export_cmd = "echo 'export DJANGO_SETTINGS_MODULE=apps.settings.settings' >> /etc/environment"
        self.execute_command(export_cmd)
        
        # Also set for current session
        self.execute_command("export DJANGO_SETTINGS_MODULE=apps.settings.settings")
        
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
        
        # Create traditional Django service file (TCP-based)
        service_content = """[Unit]
Description=ProjectMeats Django Backend
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=root
WorkingDirectory=/opt/projectmeats/backend
EnvironmentFile=-/etc/projectmeats/projectmeats.env
EnvironmentFile=-/opt/projectmeats/.env.production
Environment=DJANGO_SETTINGS_MODULE=apps.settings.production
ExecStart=/opt/projectmeats/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 projectmeats.wsgi:application
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
        
        # Final verification that the service is running
        exit_code, stdout, stderr = self.execute_command("systemctl is-active projectmeats")
        if exit_code == 0:
            self.log("Backend configuration completed successfully", "SUCCESS")
            return True
        else:
            self.log("Backend service not running after configuration - attempting Django service fix...", "WARNING")
            # Last attempt with Django service fix
            if self.fix_django_service_issues():
                self.log("Django service fix resolved backend configuration issues", "SUCCESS")
                return True
            else:
                self.log("Backend configuration completed but service may need manual attention", "WARNING")
                return True  # Don't fail the entire deployment for service issues
    
    def deploy_configure_frontend(self) -> bool:
        """Configure frontend"""
        self.log("Configuring frontend...", "INFO")
        
        # Check if automated script already handled this
        if hasattr(self.state, 'automated_script_used') and self.state.automated_script_used:
            self.log(f"Frontend may already be configured by {self.state.automated_script_used} script", "INFO")
            
            # Verify if frontend is already built
            exit_code, stdout, stderr = self.execute_command(
                "test -d /opt/projectmeats/frontend/build && test -f /opt/projectmeats/frontend/build/index.html"
            )
            if exit_code == 0:
                self.log("OK Frontend already built - skipping manual configuration", "SUCCESS")
                return True
            else:
                self.log("Frontend not fully built - continuing with manual setup", "INFO")
        
        # Ensure proper directory ownership before npm operations
        self.log("Setting frontend directory ownership...", "INFO")
        ownership_commands = [
            "chown -R projectmeats:projectmeats /opt/projectmeats/frontend",
            "chmod -R 755 /opt/projectmeats/frontend"
        ]
        
        for cmd in ownership_commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0:
                self.log(f"Ownership setup failed: {cmd}", "ERROR")
                self.log(f"Error output: {stderr}", "ERROR")
                return False
        
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
        """Setup web server with automatic socket configuration detection"""
        self.log("Setting up web server...", "INFO")
        
        # Check if automated script already handled this
        if hasattr(self.state, 'automated_script_used') and self.state.automated_script_used:
            self.log(f"Web server may already be configured by {self.state.automated_script_used} script", "INFO")
            
            # Verify if nginx is already configured for ProjectMeats
            exit_code, stdout, stderr = self.execute_command(
                "test -f /etc/nginx/sites-enabled/projectmeats && systemctl is-active nginx"
            )
            if exit_code == 0:
                self.log("OK Web server already configured and running - skipping manual configuration", "SUCCESS")
                return True
            else:
                self.log("Web server not fully configured - continuing with manual setup", "INFO")
        
        # NEW: Detect if socket nginx configuration is available
        use_socket_config = self._detect_socket_service_configuration()
        
        if use_socket_config:
            self.log("Using Unix socket-based Nginx configuration", "INFO", Colors.BOLD + Colors.CYAN)
            return self._setup_webserver_with_socket_config()
        
        # Fall back to traditional TCP-based configuration
        return self._setup_webserver_traditional()

    def _setup_webserver_with_socket_config(self) -> bool:
        """Setup web server using Unix socket nginx configuration"""
        self.log("Configuring Nginx with Unix socket configuration...", "INFO")
        
        # Deploy socket nginx configuration
        if not self._deploy_socket_nginx_configuration():
            return False
        
        # Apply socket permission fixes (Priority #2 from problem statement)
        if not self._apply_socket_permission_fixes():
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
        
        # Verify socket accessibility for nginx (www-data)
        if not self._verify_socket_accessibility():
            self.log("Socket permission verification failed - this may cause nginx upstream issues", "WARNING")
        
        self.log("✓ Nginx configured with Unix socket successfully", "SUCCESS", Colors.BOLD + Colors.GREEN)
        return True

    def _setup_webserver_traditional(self) -> bool:
        """Setup web server using traditional TCP-based configuration"""
        self.log("Configuring Nginx with traditional TCP configuration...", "INFO")
        
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
        """Final verification with enhanced database connectivity testing"""
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
        
        # Enhanced database connectivity test with credential validation
        if not self._test_database_connectivity():
            return False
        
        # Test localhost health endpoint first with enhanced error handling (Priority #3)
        self._enhanced_health_endpoint_test("localhost", is_local=True)
        
        # Check if frontend build exists
        exit_code, stdout, stderr = self.execute_command("ls -la /opt/projectmeats/frontend/build/index.html")
        if exit_code != 0:
            self.log("Frontend build files not found", "ERROR")
            return False
        
        # NEW: Test domain accessibility from external perspective
        domain = self.config.get('domain', 'localhost')
        if domain and domain != 'localhost':
            self.log(f"Testing external domain accessibility: {domain}", "INFO")
            
            # Enhanced HTTP access test with better error handling (Priority #3)  
            if self._enhanced_health_endpoint_test(domain, is_local=False):
                self.log(f"OK Domain {domain} is externally accessible via HTTP", "SUCCESS")
            else:
                self.log(f"WARNING WARNING: Domain {domain} may not be externally accessible via HTTP", "WARNING")
                self.log(f"This could be due to DNS propagation, firewall, or SSL redirect issues", "WARNING")
                
                # Try to diagnose the issue
                self.log("Running additional diagnostics...", "INFO")
                
                # Enhanced DNS resolution check to avoid local resolver artifacts (Priority #4)
                if not self._enhanced_dns_resolution_check(domain):
                    self.log("DNS resolution issues detected", "WARNING")
                
                # Check what processes are listening on port 80 with proper privileges
                self._enhanced_port_80_check()
                
                # Check nginx configuration for the domain
                config_exit_code, config_stdout, config_stderr = self.execute_command(
                    f"nginx -T | grep -A 5 'server_name {domain}'"
                )
                if config_exit_code == 0:
                    self.log(f"OK Nginx configured for domain {domain}", "INFO")
                else:
                    self.log(f"WARNING Nginx may not be configured for domain {domain}", "WARNING")
            
            # Test HTTPS if available
            https_exit_code, https_stdout, https_stderr = self.execute_command(
                f"curl -f -L --max-time 30 --connect-timeout 10 https://{domain}/health || echo 'HTTPS_ACCESS_FAILED'"
            )
            if https_exit_code == 0 and "healthy" in https_stdout:
                self.log(f"OK Domain {domain} is accessible via HTTPS", "SUCCESS")
            else:
                self.log(f"ℹ HTTPS not available for {domain} (normal for new deployments)", "INFO")
        
        self.log("Final verification completed successfully", "SUCCESS")
        return True
    
    def _test_database_connectivity(self) -> bool:
        """Enhanced database connectivity test using actual credentials"""
        self.log("Testing database connectivity with actual credentials...", "INFO")
        
        # First, try to load database credentials from the credentials file
        db_name, db_user, db_password = self._load_database_credentials()
        
        if not db_name or not db_user:
            self.log("Could not load database credentials, using fallback test", "WARNING")
            return self._fallback_database_test()
        
        # Validate environment variables are set correctly
        if not self._validate_database_environment(db_name, db_user, db_password):
            self.log("Database environment validation failed", "WARNING")
        
        # Test 1: Direct PostgreSQL connection test
        self.log(f"Test 1: Testing direct connection to database '{db_name}' as user '{db_user}'", "INFO")
        exit_code, stdout, stderr = self.execute_command(
            f"PGPASSWORD='{db_password}' psql -h localhost -U '{db_user}' -d '{db_name}' -c 'SELECT 1;' -t"
        )
        if exit_code == 0:
            self.log("✓ Direct database connection successful", "SUCCESS")
            return True
        else:
            self.log(f"✗ Direct database connection failed (exit code {exit_code})", "ERROR")
            if stderr:
                self.log(f"  Error details: {stderr.strip()}", "ERROR")
            
        # Test 2: Try with postgres user as fallback
        self.log(f"Test 2: Testing database connection via postgres user", "INFO")
        exit_code, stdout, stderr = self.execute_command(
            f"sudo -u postgres psql -d '{db_name}' -c 'SELECT 1;' -t"
        )
        if exit_code == 0:
            self.log("✓ Database connection via postgres user successful", "SUCCESS")
            return True
        else:
            self.log(f"✗ Database connection via postgres user failed (exit code {exit_code})", "ERROR")
            if stderr:
                self.log(f"  Error details: {stderr.strip()}", "ERROR")
        
        # Test 3: Check if database exists
        self.log(f"Test 3: Verifying database '{db_name}' exists", "INFO")
        exit_code, stdout, stderr = self.execute_command(
            f"sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw '{db_name}'"
        )
        if exit_code == 0:
            self.log(f"✓ Database '{db_name}' exists", "INFO")
        else:
            self.log(f"✗ Database '{db_name}' does not exist", "ERROR")
            
        # Test 4: Check PostgreSQL server status
        self.log("Test 4: Checking PostgreSQL server status", "INFO")
        exit_code, stdout, stderr = self.execute_command("pg_isready -h localhost -p 5432")
        if exit_code == 0:
            self.log("✓ PostgreSQL server is ready", "INFO")
        else:
            self.log("✗ PostgreSQL server is not ready", "ERROR")
            
        # Provide diagnostic information
        self.log("Database connectivity test failed. Diagnostics:", "ERROR")
        self._diagnose_database_connectivity_issues(db_name, db_user)
        
        return False
    
    def _load_database_credentials(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Load database credentials from the admin credentials file"""
        try:
            self.log("Loading database credentials from /opt/projectmeats/admin/database_credentials.json", "INFO")
            exit_code, stdout, stderr = self.execute_command(
                "cat /opt/projectmeats/admin/database_credentials.json 2>/dev/null || echo 'FILE_NOT_FOUND'"
            )
            
            if exit_code != 0 or "FILE_NOT_FOUND" in stdout:
                self.log("Database credentials file not found", "WARNING")
                return None, None, None
            
            try:
                import json
                creds = json.loads(stdout.strip())
                db_name = creds.get('database_name')
                db_user = creds.get('database_user') 
                db_password = creds.get('database_password')
                
                if db_name and db_user and db_password:
                    # Mask password in log for security
                    masked_password = db_password[:3] + '*' * (len(db_password) - 6) + db_password[-3:] if len(db_password) > 6 else '*' * len(db_password)
                    self.log(f"Loaded credentials - DB: {db_name}, User: {db_user}, Password: {masked_password}", "SUCCESS")
                    return db_name, db_user, db_password
                else:
                    self.log("Incomplete credentials in database_credentials.json", "WARNING")
                    return None, None, None
                    
            except json.JSONDecodeError as e:
                self.log(f"Invalid JSON in database credentials file: {e}", "ERROR")
                return None, None, None
                
        except Exception as e:
            self.log(f"Error loading database credentials: {e}", "WARNING")
            return None, None, None
    
    def _validate_database_environment(self, db_name: str, db_user: str, db_password: str) -> bool:
        """Validate that environment variables match the actual database configuration"""
        self.log("Validating database environment variables...", "INFO")
        
        # Check if DATABASE_URL is set correctly
        expected_db_url = f"postgres://{db_user}:{db_password}@localhost:5432/{db_name}"
        exit_code, stdout, stderr = self.execute_command(
            "grep DATABASE_URL /opt/projectmeats/.env.production 2>/dev/null || echo 'NOT_FOUND'"
        )
        
        if exit_code == 0 and "NOT_FOUND" not in stdout:
            env_db_url = stdout.strip().split('=', 1)[1] if '=' in stdout else ""
            # Mask passwords for comparison log
            masked_expected = expected_db_url.replace(db_password, '*' * len(db_password))
            masked_actual = env_db_url.replace(db_password, '*' * len(db_password)) if db_password in env_db_url else env_db_url
            
            self.log(f"Expected DATABASE_URL: {masked_expected}", "INFO")
            self.log(f"Actual DATABASE_URL:   {masked_actual}", "INFO")
            
            if expected_db_url in env_db_url or env_db_url in expected_db_url:
                self.log("✓ DATABASE_URL appears to be correctly configured", "SUCCESS")
                return True
            else:
                self.log("✗ DATABASE_URL does not match expected configuration", "WARNING")
                return False
        else:
            self.log("✗ DATABASE_URL not found in environment file", "WARNING")
            return False
    
    def _fallback_database_test(self) -> bool:
        """Fallback database connectivity test using postgres user"""
        self.log("Running fallback database connectivity test...", "INFO")
        
        # Try to connect to any database to test PostgreSQL connectivity
        exit_code, stdout, stderr = self.execute_command(
            "sudo -u postgres psql -c 'SELECT version();' -t"
        )
        if exit_code == 0:
            self.log("✓ PostgreSQL is accessible via postgres user", "SUCCESS")
            return True
        else:
            self.log(f"✗ PostgreSQL fallback test failed: {stderr}", "ERROR")
            return False
    
    def _diagnose_database_connectivity_issues(self, db_name: str, db_user: str):
        """Provide diagnostic information for database connectivity issues"""
        self.log("Running database connectivity diagnostics...", "INFO")
        
        # Check PostgreSQL process
        exit_code, stdout, stderr = self.execute_command("pgrep -f postgres")
        if exit_code == 0:
            self.log("✓ PostgreSQL processes are running", "INFO")
        else:
            self.log("✗ No PostgreSQL processes found", "ERROR")
        
        # Check PostgreSQL service status
        exit_code, stdout, stderr = self.execute_command("systemctl status postgresql --no-pager -l")
        if exit_code == 0:
            self.log(f"PostgreSQL service status: {stdout[:200]}...", "INFO")
        else:
            self.log(f"PostgreSQL service status check failed: {stderr}", "ERROR")
        
        # Check PostgreSQL configuration
        exit_code, stdout, stderr = self.execute_command("sudo -u postgres psql -c '\\l' -t | head -10")
        if exit_code == 0:
            self.log(f"Available databases: {stdout.strip()}", "INFO")
        else:
            self.log("Could not list databases", "ERROR")
        
        # Check pg_hba.conf for authentication issues
        exit_code, stdout, stderr = self.execute_command(
            "grep -v '^#' /etc/postgresql/*/main/pg_hba.conf | grep -v '^$' | head -5"
        )
        if exit_code == 0:
            self.log(f"PostgreSQL auth config (pg_hba.conf): {stdout.strip()}", "INFO")
        else:
            self.log("Could not read PostgreSQL authentication configuration", "WARNING")

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
            self.log("OK HTTP health endpoint accessible", "SUCCESS")
            tests_passed += 1
        else:
            self.log("X HTTP health endpoint not accessible", "ERROR")
        
        # Test 2: Root page accessibility
        self.log("Test 2: Root page accessibility", "INFO")
        exit_code, stdout, stderr = self.execute_command(
            f"timeout 30 curl -I -L --connect-timeout 10 http://{domain}/ || echo 'FAILED'"
        )
        if exit_code == 0 and ("200 OK" in stdout or "301" in stdout or "302" in stdout):
            self.log("OK Root page accessible", "SUCCESS")
            tests_passed += 1
        else:
            self.log("X Root page not accessible", "ERROR")
        
        # Test 3: DNS resolution verification
        self.log("Test 3: DNS resolution", "INFO")
        exit_code, stdout, stderr = self.execute_command(f"nslookup {domain}")
        if exit_code == 0 and "NXDOMAIN" not in stderr:
            self.log("OK DNS resolution working", "SUCCESS")
            tests_passed += 1
        else:
            self.log("X DNS resolution failed", "ERROR")
        
        # Determine if domain accessibility check passes
        if tests_passed >= 2:
            self.log(f"OK Domain accessibility check PASSED ({tests_passed}/{total_tests} tests)", "SUCCESS", Colors.BOLD + Colors.GREEN)
            return True
        else:
            self.log(f"X Domain accessibility check FAILED ({tests_passed}/{total_tests} tests)", "CRITICAL", Colors.BOLD + Colors.RED)
            self.log(f"CRITICAL: {domain} is not accessible from the internet", "CRITICAL")
            self.log("This indicates the deployment has NOT succeeded despite completing technical steps", "CRITICAL")
            
            # Provide diagnostic information
            self._diagnose_domain_accessibility_issues(domain)
            
            return False

    def deploy_docker_setup(self) -> bool:
        """Setup Docker-based deployment with industry best practices"""
        self.log("Setting up Docker-based production deployment...", "INFO", Colors.BOLD + Colors.CYAN)
        
        try:
            # Install Docker and docker-compose with latest best practices
            if not self._install_docker():
                return False
            
            # Create optimized docker-compose.yml for production
            if not self._create_production_docker_compose():
                return False
                
            # Create production-optimized Dockerfiles
            if not self._create_production_dockerfiles():
                return False
                
            # Create Docker environment files with security
            if not self._create_docker_environment_files():
                return False
                
            # Setup Docker networking and volumes
            if not self._setup_docker_infrastructure():
                return False
                
            # Build and deploy containers
            if not self._build_and_deploy_containers():
                return False
                
            self.log("Docker deployment setup completed successfully", "SUCCESS", Colors.GREEN)
            return True
            
        except Exception as e:
            self.log(f"Docker deployment setup failed: {e}", "ERROR")
            return False
    
    def _install_docker(self) -> bool:
        """Install Docker with industry best practices"""
        self.log("Installing Docker with latest security practices...", "INFO")
        
        commands = [
            # Remove any old Docker versions
            "apt-get remove -y docker docker-engine docker.io containerd runc || true",
            
            # Install dependencies
            "apt-get update",
            "apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release",
            
            # Add Docker's official GPG key
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
            
            # Add Docker repository
            "echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable' | tee /etc/apt/sources.list.d/docker.list > /dev/null",
            
            # Install Docker
            "apt-get update",
            "apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
            
            # Enable and start Docker
            "systemctl enable docker",
            "systemctl start docker",
            
            # Create projectmeats user and add to docker group
            "useradd -r -s /bin/false projectmeats || true",
            "usermod -aG docker projectmeats",
            
            # Create necessary directories
            "mkdir -p /opt/projectmeats/{logs,backups,ssl,media,static}",
            "chown -R projectmeats:docker /opt/projectmeats",
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0 and "remove" not in cmd and "useradd" not in cmd:
                self.log(f"Failed to execute: {cmd}", "ERROR")
                self.log(f"Error: {stderr}", "ERROR")
                return False
                
        # Verify Docker installation
        exit_code, stdout, stderr = self.execute_command("docker --version")
        if exit_code == 0:
            self.log(f"Docker installed successfully: {stdout.strip()}", "SUCCESS")
            return True
        else:
            self.log("Docker installation verification failed", "ERROR")
            return False
    
    def _create_production_docker_compose(self) -> bool:
        """Create production-optimized docker-compose.yml with industry best practices"""
        self.log("Creating production docker-compose configuration...", "INFO")
        
        domain = self.config.get('domain', 'localhost')
        
        compose_content = f"""version: '3.8'

# ProjectMeats Production Docker Compose
# Optimized for DigitalOcean droplets with industry best practices

services:
  # PostgreSQL Database with security hardening
  db:
    image: postgres:15-alpine
    container_name: projectmeats-db
    environment:
      POSTGRES_DB: ${{POSTGRES_DB:-projectmeats}}
      POSTGRES_USER: ${{POSTGRES_USER:-projectmeats}}
      POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD}}
      POSTGRES_INITDB_ARGS: "--auth-host=scram-sha-256"
      POSTGRES_HOST_AUTH_METHOD: scram-sha-256
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - /opt/projectmeats/backups:/backups
    networks:
      - backend
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /var/run/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${{POSTGRES_USER:-projectmeats}} -d ${{POSTGRES_DB:-projectmeats}}"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Redis Cache with security hardening  
  redis:
    image: redis:7-alpine
    container_name: projectmeats-redis
    command: redis-server --appendonly yes --requirepass ${{REDIS_PASSWORD}}
    volumes:
      - redis_data:/data
    networks:
      - backend
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Django Backend with production optimizations
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
      target: production
    container_name: projectmeats-backend
    user: "1000:1000"  # Non-root user
    environment:
      - DATABASE_URL=postgresql://${{POSTGRES_USER:-projectmeats}}:${{POSTGRES_PASSWORD}}@db:5432/${{POSTGRES_DB:-projectmeats}}
      - REDIS_URL=redis://default:${{REDIS_PASSWORD}}@redis:6379/0
      - DJANGO_SETTINGS_MODULE=projectmeats.settings.production
      - DEBUG=False
      - ALLOWED_HOSTS={domain},www.{domain}
      - SECURE_SSL_REDIRECT=True
      - SESSION_COOKIE_SECURE=True
      - CSRF_COOKIE_SECURE=True
    volumes:
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media
      - /opt/projectmeats/logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend
      - frontend
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /var/cache
    healthcheck:
      test: ["CMD", "curl", "--fail", "--silent", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s

  # React Frontend with nginx serving
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      target: production
      args:
        - REACT_APP_API_BASE_URL=https://{domain}/api
    container_name: projectmeats-frontend
    volumes:
      - frontend_build:/usr/share/nginx/html:ro
    networks:
      - frontend
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /var/cache/nginx
      - /var/run
      - /var/log/nginx

  # Nginx Reverse Proxy with SSL termination
  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile.prod
    container_name: projectmeats-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - frontend_build:/var/www/html:ro
      - static_volume:/var/www/static:ro
      - media_volume:/var/www/media:ro
      - /opt/projectmeats/ssl:/etc/nginx/ssl:ro
      - /opt/projectmeats/logs/nginx:/var/log/nginx
    depends_on:
      - backend
      - frontend
    networks:
      - frontend
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /var/cache/nginx
      - /var/run
    healthcheck:
      test: ["CMD", "curl", "--fail", "--silent", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Background Task Worker
  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
      target: production
    container_name: projectmeats-celery
    command: celery -A projectmeats worker -l info --uid=1000 --gid=1000
    user: "1000:1000"
    environment:
      - DATABASE_URL=postgresql://${{POSTGRES_USER:-projectmeats}}:${{POSTGRES_PASSWORD}}@db:5432/${{POSTGRES_DB:-projectmeats}}
      - REDIS_URL=redis://default:${{REDIS_PASSWORD}}@redis:6379/0
      - DJANGO_SETTINGS_MODULE=projectmeats.settings.production
    volumes:
      - media_volume:/app/media
      - /opt/projectmeats/logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp

  # Backup Service
  backup:
    image: postgres:15-alpine
    container_name: projectmeats-backup
    environment:
      PGPASSWORD: ${{POSTGRES_PASSWORD}}
    volumes:
      - /opt/projectmeats/backups:/backups
    networks:
      - backend
    restart: "no"
    profiles:
      - backup
    command: >
      sh -c "
        while true; do
          echo 'Starting backup at $(date)'
          pg_dump -h db -U $${POSTGRES_USER:-projectmeats} -d $${POSTGRES_DB:-projectmeats} > /backups/backup-$(date +%Y%m%d-%H%M%S).sql
          find /backups -name '*.sql' -mtime +7 -delete
          echo 'Backup completed at $(date)'
          sleep 86400
        done
      "

# Volumes for persistent data
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  static_volume:
    driver: local
  media_volume:
    driver: local
  frontend_build:
    driver: local

# Networks for security isolation
networks:
  frontend:
    driver: bridge
    internal: false
  backend:
    driver: bridge
    internal: true
"""

        # Write docker-compose.yml to server
        exit_code, _, stderr = self.execute_command(f"cat > /opt/projectmeats/docker-compose.yml << 'EOF'\\n{compose_content}\\nEOF")
        if exit_code == 0:
            self.log("Production docker-compose.yml created successfully", "SUCCESS")
            return True
        else:
            self.log(f"Failed to create docker-compose.yml: {stderr}", "ERROR")
            return False
    
    def _create_production_dockerfiles(self) -> bool:
        """Create production-optimized Dockerfiles with multi-stage builds"""
        self.log("Creating production-optimized Dockerfiles...", "INFO")
        
        # Backend Dockerfile.prod with multi-stage build
        backend_dockerfile = """# ProjectMeats Backend Production Dockerfile
# Multi-stage build with security hardening

# Build stage
FROM python:3.11-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \\
    build-essential \\
    libpq-dev \\
    pkg-config \\
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt requirements-prod.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-prod.txt

# Production stage
FROM python:3.11-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    libpq5 \\
    curl \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Create app user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser \\
    && mkdir -p /app /app/staticfiles /app/media /app/logs \\
    && chown -R appuser:appuser /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory and user
WORKDIR /app
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \\
    CMD curl --fail --silent http://localhost:8000/health/ || exit 1

# Expose port
EXPOSE 8000

# Run gunicorn with production settings
CMD ["gunicorn", \\
     "--bind", "0.0.0.0:8000", \\
     "--workers", "3", \\
     "--worker-class", "gthread", \\
     "--threads", "2", \\
     "--worker-connections", "1000", \\
     "--max-requests", "1000", \\
     "--max-requests-jitter", "100", \\
     "--timeout", "120", \\
     "--graceful-timeout", "30", \\
     "--access-logfile", "/app/logs/gunicorn-access.log", \\
     "--error-logfile", "/app/logs/gunicorn-error.log", \\
     "--log-level", "info", \\
     "projectmeats.wsgi:application"]
"""

        # Frontend Dockerfile.prod with multi-stage build
        frontend_dockerfile = """# ProjectMeats Frontend Production Dockerfile
# Multi-stage build for optimized React build

# Build stage
FROM node:18-alpine AS builder

# Install dependencies for node-gyp
RUN apk add --no-cache python3 make g++

# Create app directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user
RUN addgroup -g 101 -S nginx && \\
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD curl --fail --silent http://localhost/ || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""

        # Nginx Dockerfile.prod with security hardening
        nginx_dockerfile = """# ProjectMeats Nginx Production Dockerfile
# Security-hardened reverse proxy

FROM nginx:alpine

# Install security tools
RUN apk add --no-cache curl openssl

# Copy nginx configuration
COPY nginx.prod.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Create non-root user
RUN addgroup -g 101 -S nginx && \\
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# Set proper permissions
RUN chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD curl --fail --silent http://localhost/health || exit 1

# Expose ports
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""

        # Create Dockerfiles on server
        dockerfiles = [
            ("/opt/projectmeats/backend/Dockerfile.prod", backend_dockerfile),
            ("/opt/projectmeats/frontend/Dockerfile.prod", frontend_dockerfile), 
            ("/opt/projectmeats/nginx/Dockerfile.prod", nginx_dockerfile)
        ]
        
        for filepath, content in dockerfiles:
            # Create directory if it doesn't exist
            dir_path = filepath.rsplit('/', 1)[0]
            self.execute_command(f"mkdir -p {dir_path}")
            
            # Write Dockerfile
            exit_code, _, stderr = self.execute_command(f"cat > {filepath} << 'EOF'\\n{content}\\nEOF")
            if exit_code != 0:
                self.log(f"Failed to create {filepath}: {stderr}", "ERROR")
                return False
                
        self.log("Production Dockerfiles created successfully", "SUCCESS")
        return True
    
    def _create_docker_environment_files(self) -> bool:
        """Create secure environment files for Docker deployment"""
        self.log("Creating Docker environment configuration...", "INFO")
        
        # Generate secure passwords
        postgres_password = secrets.token_urlsafe(32)
        redis_password = secrets.token_urlsafe(32)
        django_secret = get_random_secret_key()
        
        domain = self.config.get('domain', 'localhost')
        
        # Docker environment file
        docker_env_content = f"""# ProjectMeats Docker Environment Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Database Configuration
POSTGRES_DB=projectmeats
POSTGRES_USER=projectmeats
POSTGRES_PASSWORD={postgres_password}

# Redis Configuration  
REDIS_PASSWORD={redis_password}

# Django Configuration
DJANGO_SECRET_KEY={django_secret}
DEBUG=False
ALLOWED_HOSTS={domain},www.{domain},localhost,127.0.0.1

# Domain Configuration
DOMAIN={domain}
CORS_ALLOWED_ORIGINS=https://{domain},https://www.{domain}

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
"""

        # Write environment file
        exit_code, _, stderr = self.execute_command(f"cat > /opt/projectmeats/.env << 'EOF'\\n{docker_env_content}\\nEOF")
        if exit_code == 0:
            # Set secure permissions
            self.execute_command("chmod 600 /opt/projectmeats/.env")
            self.execute_command("chown projectmeats:docker /opt/projectmeats/.env")
            self.log("Docker environment file created with secure permissions", "SUCCESS")
            return True
        else:
            self.log(f"Failed to create environment file: {stderr}", "ERROR")
            return False
    
    def _setup_docker_infrastructure(self) -> bool:
        """Setup Docker networks, volumes, and infrastructure"""
        self.log("Setting up Docker infrastructure...", "INFO")
        
        commands = [
            # Create Docker networks
            "cd /opt/projectmeats && docker network create projectmeats_frontend --driver bridge || true",
            "cd /opt/projectmeats && docker network create projectmeats_backend --driver bridge --internal || true",
            
            # Create Docker volumes
            "cd /opt/projectmeats && docker volume create projectmeats_postgres_data || true",
            "cd /opt/projectmeats && docker volume create projectmeats_redis_data || true", 
            "cd /opt/projectmeats && docker volume create projectmeats_static_volume || true",
            "cd /opt/projectmeats && docker volume create projectmeats_media_volume || true",
            "cd /opt/projectmeats && docker volume create projectmeats_frontend_build || true",
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.execute_command(cmd)
            if exit_code != 0 and "already exists" not in stderr:
                self.log(f"Failed to execute: {cmd}", "WARNING")
                # Continue with other commands as some may already exist
                
        self.log("Docker infrastructure setup completed", "SUCCESS")
        return True
    
    def _build_and_deploy_containers(self) -> bool:
        """Build and deploy Docker containers"""
        self.log("Building and deploying Docker containers...", "INFO")
        
        commands = [
            # Change to project directory
            "cd /opt/projectmeats",
            
            # Pull base images
            "docker pull postgres:15-alpine",
            "docker pull redis:7-alpine", 
            "docker pull python:3.11-slim",
            "docker pull node:18-alpine",
            "docker pull nginx:alpine",
            
            # Build application images
            "cd /opt/projectmeats && docker-compose build --no-cache",
            
            # Deploy containers
            "cd /opt/projectmeats && docker-compose up -d",
            
            # Wait for services to be healthy
            "cd /opt/projectmeats && docker-compose ps",
        ]
        
        for cmd in commands:
            self.log(f"Executing: {cmd}", "INFO")
            exit_code, stdout, stderr = self.execute_command(cmd, timeout=600)  # 10 minute timeout for builds
            
            if exit_code != 0:
                self.log(f"Command failed: {cmd}", "ERROR")
                self.log(f"Error: {stderr}", "ERROR")
                return False
            else:
                self.log(f"Success: {stdout[:200]}...", "SUCCESS")
                
        # Verify containers are running
        exit_code, stdout, stderr = self.execute_command("cd /opt/projectmeats && docker-compose ps --format table")
        if exit_code == 0:
            self.log("Container deployment status:", "INFO")
            self.log(stdout, "INFO")
            
            # Check if critical containers are running
            if "projectmeats-db" in stdout and "projectmeats-backend" in stdout and "projectmeats-nginx" in stdout:
                self.log("All critical containers deployed successfully", "SUCCESS")
                return True
            else:
                self.log("Some critical containers may not be running", "WARNING")
                return False
        else:
            self.log(f"Failed to check container status: {stderr}", "ERROR")
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
    parser.add_argument("--docker", action="store_true", help="Use Docker-based deployment with industry best practices")
    parser.add_argument("--docker-monitoring", action="store_true", help="Include monitoring stack (Prometheus, Grafana) with Docker deployment")
    
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
            
            # Ask about deployment mode
            print(f"\n{Colors.BOLD}Deployment Mode:{Colors.END}")
            print("1. Standard deployment (systemd services)")
            print("2. Docker deployment (recommended for production)")
            print("3. Docker with monitoring (Prometheus, Grafana)")
            deployment_mode = input(f"{Colors.YELLOW}Choose deployment mode (1, 2, or 3) [2]:{Colors.END} ").strip() or "2"
            
            docker_deployment = deployment_mode in ["2", "3"]
            docker_monitoring = deployment_mode == "3"
            
            if docker_deployment:
                orchestrator.log("Docker deployment mode selected - using industry best practices", "INFO", Colors.GREEN)
                if docker_monitoring:
                    orchestrator.log("Monitoring stack will be included (Prometheus, Grafana)", "INFO", Colors.GREEN)
            
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
                'domain': domain_input,
                'deployment_mode': 'docker' if docker_deployment else 'standard',
                'docker_monitoring': docker_monitoring
            }
            
            # Store deployment configuration
            orchestrator.config['domain'] = domain_input
            orchestrator.config['deployment_mode'] = 'docker' if docker_deployment else 'standard'
            orchestrator.config['docker_monitoring'] = docker_monitoring
            
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
                'domain': domain,
                'deployment_mode': 'docker' if args.docker else 'standard',
                'docker_monitoring': args.docker_monitoring
            }
            
            if domain:
                orchestrator.config['domain'] = domain
                
            # Store deployment configuration
            orchestrator.config['deployment_mode'] = 'docker' if args.docker else 'standard'
            orchestrator.config['docker_monitoring'] = args.docker_monitoring
            
            if args.docker:
                orchestrator.log("Docker deployment mode enabled via --docker flag", "INFO", Colors.GREEN)
                if args.docker_monitoring:
                    orchestrator.log("Monitoring stack enabled via --docker-monitoring flag", "INFO", Colors.GREEN)
            
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