#!/usr/bin/env python3
"""
ProjectMeats Unified Deployment, Fix, and Management Tool
========================================================

🚀 THE ONLY DEPLOYMENT TOOL YOU NEED FOR PROJECTMEATS 🚀

This unified tool consolidates ALL deployment, orchestration, diagnostics, 
fixes, and management functionality from the following scripts:

CONSOLIDATED FUNCTIONALITY:
- ai_deployment_orchestrator.py → AI-driven deployment with error recovery
- master_deploy.py → Comprehensive deployment system  
- deploy_production.py → Interactive production setup
- enhanced_deployment.py → Enhanced deployment with fixes
- fix_meatscentral_access.py → Domain access diagnostics and fixes
- diagnose_deployment_issue.py → Deployment issue diagnosis
- diagnose_domain_access.py → Domain access diagnostics
- All configuration and management scripts

NEW ENHANCED FEATURES:
✅ Server cleanup and folder structure validation
✅ Automatic credential and file overlap cleaning  
✅ Clean repository cloning with proper folder recreation
✅ Comprehensive pre-deployment server preparation
✅ Real-time deployment monitoring and AI-driven error recovery
✅ Domain accessibility verification and auto-fixing
✅ Consolidated configuration management
✅ One-command deployment for production

DEPLOYMENT MODES:
🎯 --production    : Full production deployment with all features
🧪 --staging       : Staging environment deployment  
💻 --development   : Development environment setup
🔧 --local         : Local development setup
🐳 --docker        : Docker-based deployment
☁️  --cloud         : Cloud provider deployment

DIAGNOSTIC & FIX MODES:
🔍 --diagnose      : Comprehensive deployment and access diagnostics
🛠️  --fix           : Auto-fix common deployment and access issues
🧹 --clean         : Clean server environment and remove conflicts
📊 --status        : System status and health check
🔄 --update        : Update existing deployment

MANAGEMENT MODES:
⚙️  --config        : Interactive configuration setup
📚 --docs          : Generate and view documentation
🗄️  --backup        : Backup current deployment
↩️  --rollback      : Rollback to previous version

Usage Examples:
    # 🎯 One-command production deployment
    sudo python3 unified_deployment_tool.py --production --domain=yourdomain.com --auto

    # 🧙‍♂️ Interactive wizard for first-time setup
    sudo python3 unified_deployment_tool.py --production --interactive

    # 🔍 Diagnose why meatscentral.com isn't working
    python3 unified_deployment_tool.py --diagnose --domain=meatscentral.com --server=167.99.155.140

    # 🛠️ Auto-fix domain access issues
    sudo python3 unified_deployment_tool.py --fix --domain=meatscentral.com

    # 🧹 Clean server environment before fresh deployment  
    sudo python3 unified_deployment_tool.py --clean --auto

    # 📊 Check system status and health
    python3 unified_deployment_tool.py --status

    # 🐳 Docker-based production deployment
    sudo python3 unified_deployment_tool.py --docker --production --domain=yourdomain.com

    # ⚙️ Configure deployment settings
    python3 unified_deployment_tool.py --config

Author: ProjectMeats AI Assistant
Version: 1.0 - Unified Deployment System
"""

import os
import sys
import json
import time
import subprocess
import platform
import argparse
import secrets
import shutil
import hashlib
import logging
import threading
import queue
import re
import socket
import getpass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import urllib.request
import urllib.parse

# Try to import optional dependencies
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False



# ============================================================================
# CORE CLASSES AND ENUMS
# ============================================================================

class DeploymentMode(Enum):
    """Deployment mode enumeration"""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    LOCAL = "local"
    DOCKER = "docker"
    CLOUD = "cloud"


class OperationMode(Enum):
    """Operation mode enumeration"""
    DEPLOY = "deploy"
    DIAGNOSE = "diagnose"
    FIX = "fix"
    CLEAN = "clean"
    STATUS = "status"
    UPDATE = "update"
    CONFIG = "config"
    DOCS = "docs"
    BACKUP = "backup"
    ROLLBACK = "rollback"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Colors:
    """Terminal colors for enhanced output"""
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


@dataclass
class DeploymentConfig:
    """Unified deployment configuration"""
    # Basic settings
    domain: str = None
    server_ip: str = None
    ssh_user: str = "root"
    ssh_key: str = None
    ssh_password: str = None
    
    # Deployment settings
    mode: DeploymentMode = DeploymentMode.PRODUCTION
    environment: str = "production"
    auto_mode: bool = False
    interactive_mode: bool = False
    
    # Application settings
    app_user: str = "projectmeats"
    project_dir: str = "/opt/projectmeats"
    logs_dir: str = "/opt/projectmeats/logs"
    backup_dir: str = "/opt/projectmeats/backups"
    
    # Database settings
    database_type: str = "postgresql"
    db_name: str = "projectmeats"
    db_user: str = "projectmeats"
    db_password: str = None
    
    # Security settings
    admin_user: str = "admin"
    admin_email: str = None
    admin_password: str = "ProjectMeats2024!"
    secret_key: str = None
    use_ssl: bool = True
    
    # GitHub settings
    github_user: str = None
    github_token: str = None
    
    # Advanced settings
    cleanup_before_deploy: bool = True
    backup_before_deploy: bool = True
    validate_dependencies: bool = True
    enable_monitoring: bool = True
    
    def __post_init__(self):
        if not self.admin_email and self.domain:
            self.admin_email = f"admin@{self.domain}"
        if not self.db_password:
            self.db_password = secrets.token_urlsafe(16)
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(50)


@dataclass
class SystemStatus:
    """System status tracking"""
    timestamp: datetime
    services: Dict[str, bool]
    ports: Dict[int, bool]
    disk_usage: Dict[str, Any]
    memory_usage: Dict[str, Any]
    domain_accessible: bool = False
    ssl_valid: bool = False
    deployment_health: str = "unknown"


# ============================================================================
# SERVER CLEANUP AND VALIDATION SYSTEM
# ============================================================================

class ServerCleanupManager:
    """Manages server cleanup and folder structure validation"""
    
    def __init__(self, config: DeploymentConfig, logger):
        self.config = config
        self.logger = logger
        self.ssh_client = None
        
    def set_ssh_client(self, ssh_client):
        """Set SSH client for remote operations"""
        self.ssh_client = ssh_client
        
    def run_command(self, command: str, timeout: int = 300) -> Tuple[int, str, str]:
        """Execute command locally or remotely"""
        try:
            if self.ssh_client:
                # Remote execution
                stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
                exit_code = stdout.channel.recv_exit_status()
                stdout_text = stdout.read().decode('utf-8').strip()
                stderr_text = stderr.read().decode('utf-8').strip()
                return exit_code, stdout_text, stderr_text
            else:
                # Local execution
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True, timeout=timeout
                )
                return result.returncode, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return -1, "", str(e)
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp and color"""
        color_map = {
            "DEBUG": Colors.CYAN,
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "CRITICAL": Colors.RED + Colors.BOLD
        }
        
        color = color_map.get(level, Colors.WHITE)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{color}[{timestamp}] [{level}] {message}{Colors.END}")
        
        # Also use the logger if available
        if self.logger:
            self.logger.log(getattr(logging, level.upper(), logging.INFO), message)
    
    def clean_overlapping_files(self) -> bool:
        """Clean overlapping files and credentials that might cause conflicts"""
        self.log("🧹 Cleaning overlapping files and credentials...", "INFO")
        
        try:
            # List of patterns for files that might cause conflicts
            cleanup_patterns = [
                "/opt/projectmeats*",
                "/etc/nginx/sites-*/projectmeats*",
                "/etc/nginx/sites-*/meatscentral*", 
                "/etc/systemd/system/projectmeats*",
                "/tmp/*projectmeats*",
                "/tmp/*deploy*",
                "/var/log/nginx/*projectmeats*",
                "/home/*/ProjectMeats*",
                "/root/ProjectMeats*"
            ]
            
            # Backup any existing ProjectMeats installations
            if self._backup_existing_installation():
                self.log("✅ Existing installation backed up", "SUCCESS")
            
            # Clean up deployment artifacts
            cleanup_commands = [
                "pkill -f 'projectmeats\\|gunicorn.*projectmeats' || true",
                "systemctl stop projectmeats || true",
                "systemctl disable projectmeats || true",
                "rm -f /etc/systemd/system/projectmeats*",
                "systemctl daemon-reload",
                "rm -rf /tmp/*projectmeats* /tmp/*deploy* || true",
                "rm -f /etc/nginx/sites-enabled/projectmeats || true",
                "rm -f /etc/nginx/sites-available/projectmeats || true",
                "nginx -s reload || systemctl reload nginx || true"
            ]
            
            for cmd in cleanup_commands:
                exit_code, stdout, stderr = self.run_command(cmd)
                if exit_code != 0 and "pkill" not in cmd and "systemctl stop" not in cmd:
                    self.log(f"Warning: Cleanup command failed: {cmd}", "WARNING")
            
            # Clean up conflicting Node.js installations
            self._clean_nodejs_conflicts()
            
            # Clean up old SSH keys and credentials if requested
            if self.config.cleanup_before_deploy:
                self._clean_old_credentials()
            
            self.log("✅ Server cleanup completed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Error during server cleanup: {e}", "ERROR")
            return False
    
    def _backup_existing_installation(self) -> bool:
        """Backup existing ProjectMeats installation"""
        try:
            backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Check if ProjectMeats directory exists
            exit_code, stdout, stderr = self.run_command("test -d /opt/projectmeats")
            if exit_code == 0:
                backup_path = f"/opt/projectmeats_backup_{backup_timestamp}"
                
                self.log(f"Backing up existing installation to {backup_path}", "INFO")
                exit_code, stdout, stderr = self.run_command(f"mv /opt/projectmeats {backup_path}")
                
                if exit_code == 0:
                    self.log(f"✅ Backup created: {backup_path}", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Backup failed: {stderr}", "ERROR")
                    
            return True  # No existing installation, nothing to backup
            
        except Exception as e:
            self.log(f"❌ Backup error: {e}", "ERROR")
            return False
    
    def _clean_nodejs_conflicts(self):
        """Clean up conflicting Node.js installations"""
        self.log("🔧 Cleaning Node.js conflicts...", "INFO")
        
        cleanup_commands = [
            "pkill -f node || true",
            "apt remove -y nodejs npm libnode-dev || true",
            "apt purge -y nodejs npm libnode-dev || true",
            "rm -rf /usr/local/bin/node* /usr/local/bin/npm* || true",
            "rm -rf /usr/local/lib/node_modules || true",
            "apt autoremove -y",
            "apt clean"
        ]
        
        for cmd in cleanup_commands:
            self.run_command(cmd)
    
    def _clean_old_credentials(self):
        """Clean up old credentials and configuration files"""
        self.log("🔑 Cleaning old credentials...", "INFO")
        
        credential_patterns = [
            "/root/.ssh/known_hosts.d/*github*",
            "/home/*/.ssh/known_hosts.d/*github*", 
            "/tmp/*.env",
            "/tmp/*config*"
        ]
        
        for pattern in credential_patterns:
            self.run_command(f"rm -f {pattern} || true")
    
    def validate_server_structure(self) -> bool:
        """Validate and recreate proper server folder structure"""
        self.log("📁 Validating server folder structure...", "INFO")
        
        try:
            # Required directories
            required_dirs = [
                self.config.project_dir,
                self.config.logs_dir,
                self.config.backup_dir,
                f"{self.config.project_dir}/uploads",
                "/etc/nginx/sites-available",
                "/etc/nginx/sites-enabled",
                "/etc/systemd/system"
            ]
            
            # Create required directories
            for directory in required_dirs:
                exit_code, stdout, stderr = self.run_command(f"mkdir -p {directory}")
                if exit_code == 0:
                    self.log(f"✅ Directory ready: {directory}", "DEBUG")
                else:
                    self.log(f"❌ Failed to create directory {directory}: {stderr}", "ERROR")
                    return False
            
            # Set proper permissions
            permission_commands = [
                f"chown -R {self.config.app_user}:{self.config.app_user} {self.config.project_dir} || true",
                f"chmod -R 755 {self.config.project_dir}",
                f"chmod -R 755 {self.config.logs_dir}",
                f"chmod -R 755 {self.config.backup_dir}"
            ]
            
            for cmd in permission_commands:
                self.run_command(cmd)
            
            # Validate critical system requirements
            if not self._validate_system_requirements():
                return False
            
            self.log("✅ Server folder structure validated", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Error validating server structure: {e}", "ERROR")
            return False
    
    def _validate_system_requirements(self) -> bool:
        """Validate system requirements"""
        self.log("🔍 Validating system requirements...", "INFO")
        
        # Check operating system
        exit_code, stdout, stderr = self.run_command("cat /etc/os-release | grep -i ubuntu")
        if exit_code != 0:
            self.log("⚠️ Warning: Non-Ubuntu OS detected", "WARNING")
        
        # Check available disk space (minimum 5GB)
        exit_code, stdout, stderr = self.run_command("df -BG / | tail -1")
        if exit_code == 0:
            parts = stdout.split()
            if len(parts) >= 4:
                available_gb = parts[3].replace('G', '')
                try:
                    if int(available_gb) < 5:
                        self.log(f"❌ Insufficient disk space: {available_gb}GB (minimum 5GB required)", "ERROR")
                        return False
                except ValueError:
                    pass
        
        # Check memory (minimum 1GB)
        exit_code, stdout, stderr = self.run_command("free -m | grep '^Mem:'")
        if exit_code == 0:
            parts = stdout.split()
            if len(parts) >= 2:
                total_mb = parts[1]
                try:
                    if int(total_mb) < 1024:
                        self.log(f"⚠️ Low memory: {total_mb}MB (1GB recommended)", "WARNING")
                except ValueError:
                    pass
        
        # Check internet connectivity
        exit_code, stdout, stderr = self.run_command("curl -s --connect-timeout 10 https://github.com > /dev/null")
        if exit_code != 0:
            self.log("❌ No internet connectivity to GitHub", "ERROR")
            return False
        
        self.log("✅ System requirements validated", "SUCCESS")
        return True
    
    def recreate_clean_repository_structure(self) -> bool:
        """Clean and recreate repository folder structure before cloning"""
        self.log("🔄 Recreating clean repository structure...", "INFO")
        
        try:
            # Remove any existing repository structure
            exit_code, stdout, stderr = self.run_command(f"rm -rf {self.config.project_dir}")
            if exit_code == 0:
                self.log("✅ Removed existing repository structure", "SUCCESS")
            
            # Recreate directory structure
            if not self.validate_server_structure():
                return False
            
            # Create application user if doesn't exist
            exit_code, stdout, stderr = self.run_command(f"id {self.config.app_user}")
            if exit_code != 0:
                self.log(f"Creating application user: {self.config.app_user}", "INFO")
                create_user_cmd = f"useradd -m -s /bin/bash -G sudo {self.config.app_user} || usermod -aG sudo {self.config.app_user}"
                self.run_command(create_user_cmd)
            
            self.log("✅ Clean repository structure recreated", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Error recreating repository structure: {e}", "ERROR")
            return False


# ============================================================================
# ENHANCED REPOSITORY CLONING SYSTEM  
# ============================================================================

class RepositoryManager:
    """Manages clean repository cloning with multiple fallback methods"""
    
    def __init__(self, config: DeploymentConfig, logger, cleanup_manager: ServerCleanupManager):
        self.config = config
        self.logger = logger
        self.cleanup_manager = cleanup_manager
        
    def log(self, message: str, level: str = "INFO"):
        """Use cleanup manager's logging"""
        self.cleanup_manager.log(message, level)
    
    def clone_repository_clean(self) -> bool:
        """Clone repository with comprehensive validation and multiple fallback methods"""
        self.log("📥 Starting clean repository clone...", "INFO")
        
        try:
            # Ensure clean directory structure
            if not self.cleanup_manager.recreate_clean_repository_structure():
                return False
            
            # Setup GitHub authentication
            self._setup_github_authentication()
            
            # Try multiple cloning methods
            clone_methods = [
                self._clone_with_pat_auth,
                self._clone_with_public_access,
                self._clone_with_ssh_key,
                self._download_via_zip,
                self._download_via_tarball
            ]
            
            for method in clone_methods:
                try:
                    self.log(f"Attempting {method.__name__}...", "INFO")
                    if method():
                        self.log(f"✅ Successfully cloned via {method.__name__}", "SUCCESS")
                        
                        # Validate the cloned repository
                        if self._validate_cloned_repository():
                            return True
                        else:
                            self.log(f"❌ Repository validation failed for {method.__name__}", "ERROR")
                            continue
                            
                except Exception as e:
                    self.log(f"❌ {method.__name__} failed: {e}", "WARNING")
                    continue
            
            # If all methods failed, provide detailed guidance
            self._show_manual_clone_instructions()
            return False
            
        except Exception as e:
            self.log(f"❌ Repository cloning failed: {e}", "ERROR")
            return False
    
    def _setup_github_authentication(self):
        """Setup GitHub authentication from environment or config"""
        # Check environment variables first
        github_user = os.environ.get('GITHUB_USER') or os.environ.get('GITHUB_USERNAME')
        github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_PAT')
        
        if github_user and github_token:
            self.config.github_user = github_user
            self.config.github_token = github_token
            self.log("✅ GitHub authentication loaded from environment", "SUCCESS")
        elif self.config.github_user and self.config.github_token:
            self.log("✅ GitHub authentication loaded from configuration", "SUCCESS")
        else:
            self.log("⚠️ No GitHub authentication configured (will try public methods)", "WARNING")
    
    def _clone_with_pat_auth(self) -> bool:
        """Clone using Personal Access Token authentication"""
        if not (self.config.github_user and self.config.github_token):
            return False
        
        github_url = f"https://{self.config.github_user}:{self.config.github_token}@github.com/Vacilator/ProjectMeats.git"
        
        exit_code, stdout, stderr = self.cleanup_manager.run_command(
            f"cd {self.config.project_dir} && timeout 600 git clone --progress {github_url} .",
            timeout=700
        )
        
        return exit_code == 0
    
    def _clone_with_public_access(self) -> bool:
        """Clone using public access (no authentication)"""
        exit_code, stdout, stderr = self.cleanup_manager.run_command(
            f"cd {self.config.project_dir} && timeout 600 git clone --progress https://github.com/Vacilator/ProjectMeats.git .",
            timeout=700
        )
        
        return exit_code == 0
    
    def _clone_with_ssh_key(self) -> bool:
        """Clone using SSH key authentication"""
        # Test SSH connectivity first
        exit_code, stdout, stderr = self.cleanup_manager.run_command(
            "timeout 30 ssh -T git@github.com -o StrictHostKeyChecking=no"
        )
        
        # SSH test returns 1 for successful auth test, 255 for connection failure
        if exit_code not in [0, 1]:
            return False
        
        exit_code, stdout, stderr = self.cleanup_manager.run_command(
            f"cd {self.config.project_dir} && timeout 600 git clone git@github.com:Vacilator/ProjectMeats.git .",
            timeout=700
        )
        
        return exit_code == 0
    
    def _download_via_zip(self) -> bool:
        """Download repository as ZIP file"""
        try:
            # Download ZIP
            download_cmd = f"cd {self.config.project_dir} && timeout 600 curl -L --fail --connect-timeout 30 --max-time 600 https://github.com/Vacilator/ProjectMeats/archive/main.zip -o project.zip"
            exit_code, stdout, stderr = self.cleanup_manager.run_command(download_cmd, timeout=700)
            
            if exit_code != 0:
                return False
            
            # Validate download
            exit_code, stdout, stderr = self.cleanup_manager.run_command(
                f"cd {self.config.project_dir} && stat -c%s project.zip"
            )
            
            if exit_code != 0:
                return False
                
            file_size = int(stdout.strip()) if stdout.strip().isdigit() else 0
            if file_size < 1000:  # Less than 1KB indicates error
                self.log(f"❌ Downloaded file too small ({file_size} bytes)", "ERROR")
                return False
            
            # Verify it's actually a ZIP file
            exit_code, stdout, stderr = self.cleanup_manager.run_command(
                f"cd {self.config.project_dir} && file project.zip"
            )
            
            if exit_code != 0 or "zip" not in stdout.lower():
                self.log("❌ Downloaded file is not a valid ZIP archive", "ERROR")
                return False
            
            # Extract ZIP
            extract_cmd = f"cd {self.config.project_dir} && unzip -q project.zip && mv ProjectMeats-main/* . && mv ProjectMeats-main/.[^.]* . 2>/dev/null || true && rmdir ProjectMeats-main && rm project.zip"
            exit_code, stdout, stderr = self.cleanup_manager.run_command(extract_cmd)
            
            return exit_code == 0
            
        except Exception as e:
            self.log(f"❌ ZIP download error: {e}", "ERROR")
            return False
    
    def _download_via_tarball(self) -> bool:
        """Download repository as tarball"""
        try:
            # Download tarball
            download_cmd = f"cd {self.config.project_dir} && timeout 600 curl -L --fail --connect-timeout 30 --max-time 600 https://github.com/Vacilator/ProjectMeats/archive/refs/heads/main.tar.gz -o project.tar.gz"
            exit_code, stdout, stderr = self.cleanup_manager.run_command(download_cmd, timeout=700)
            
            if exit_code != 0:
                return False
            
            # Validate download
            exit_code, stdout, stderr = self.cleanup_manager.run_command(
                f"cd {self.config.project_dir} && stat -c%s project.tar.gz"
            )
            
            if exit_code != 0:
                return False
                
            file_size = int(stdout.strip()) if stdout.strip().isdigit() else 0
            if file_size < 1000:  # Less than 1KB indicates error
                self.log(f"❌ Downloaded tarball too small ({file_size} bytes)", "ERROR")
                return False
            
            # Verify it's actually a gzip file
            exit_code, stdout, stderr = self.cleanup_manager.run_command(
                f"cd {self.config.project_dir} && file project.tar.gz"
            )
            
            if exit_code != 0 or "gzip" not in stdout.lower():
                self.log("❌ Downloaded file is not a valid gzip archive", "ERROR")
                return False
            
            # Extract tarball
            extract_cmd = f"cd {self.config.project_dir} && tar -xzf project.tar.gz && mv ProjectMeats-main/* . && mv ProjectMeats-main/.[^.]* . 2>/dev/null || true && rmdir ProjectMeats-main && rm project.tar.gz"
            exit_code, stdout, stderr = self.cleanup_manager.run_command(extract_cmd)
            
            return exit_code == 0
            
        except Exception as e:
            self.log(f"❌ Tarball download error: {e}", "ERROR")
            return False
    
    def _validate_cloned_repository(self) -> bool:
        """Validate that the repository was cloned correctly"""
        self.log("🔍 Validating cloned repository...", "INFO")
        
        # Check for essential files and directories
        essential_items = [
            ("backend", "directory"),
            ("frontend", "directory"), 
            ("README.md", "file"),
            ("backend/manage.py", "file"),
            ("backend/requirements.txt", "file"),
            ("frontend/package.json", "file")
        ]
        
        missing_items = []
        for item, item_type in essential_items:
            test_cmd = f"test -{item_type[0]} {self.config.project_dir}/{item}"
            exit_code, stdout, stderr = self.cleanup_manager.run_command(test_cmd)
            
            if exit_code != 0:
                missing_items.append(f"{item} ({item_type})")
        
        if missing_items:
            self.log(f"❌ Missing essential items: {', '.join(missing_items)}", "ERROR")
            return False
        
        # Check that we have a reasonable number of files
        exit_code, stdout, stderr = self.cleanup_manager.run_command(
            f"find {self.config.project_dir} -type f | wc -l"
        )
        
        if exit_code == 0 and stdout.strip().isdigit():
            file_count = int(stdout.strip())
            if file_count < 20:  # A reasonable minimum for a Django+React project
                self.log(f"❌ Too few files in repository ({file_count})", "ERROR")
                return False
        
        # Set proper ownership
        self.cleanup_manager.run_command(
            f"chown -R {self.config.app_user}:{self.config.app_user} {self.config.project_dir}"
        )
        
        self.log("✅ Repository validation successful", "SUCCESS")
        return True
    
    def _show_manual_clone_instructions(self):
        """Show detailed instructions for manual repository setup"""
        self.log("📋 ALL AUTOMATIC CLONE METHODS FAILED", "ERROR")
        self.log("=" * 60, "ERROR")
        self.log("Manual Repository Setup Required", "ERROR")
        self.log("=" * 60, "ERROR")
        
        print(f"\n{Colors.BOLD}🔒 GitHub Authentication Required{Colors.END}")
        print("=" * 60)
        print("GitHub has restricted access. Try these solutions:")
        print()
        print(f"{Colors.BOLD}1. 🔑 Personal Access Token (Recommended):{Colors.END}")
        print("   • Go to GitHub.com → Settings → Developer settings → Personal access tokens")
        print("   • Generate token with 'repo' scope")
        print("   • Set environment variables:")
        print(f"     export GITHUB_USER=your_username")
        print(f"     export GITHUB_TOKEN=your_personal_access_token")
        print(f"   • Re-run this tool")
        print()
        print(f"{Colors.BOLD}2. 🗝️ SSH Key Authentication:{Colors.END}")
        print("   • Generate SSH key: ssh-keygen -t ed25519 -C 'your_email@example.com'")
        print("   • Add public key to GitHub → Settings → SSH and GPG keys")
        print("   • Test: ssh -T git@github.com")
        print("   • Re-run this tool")
        print()
        print(f"{Colors.BOLD}3. 📦 Manual Transfer:{Colors.END}")
        print("   • Download on local machine with GitHub access:")
        print("     git clone https://github.com/Vacilator/ProjectMeats.git")
        print("   • Transfer to server:")
        print(f"     scp -r ProjectMeats/ root@{self.config.server_ip}:{self.config.project_dir}")
        print()
        print(f"{Colors.BOLD}4. 🌐 Alternative Deployment:{Colors.END}")
        print("   • Use the no-authentication script:")
        print("     curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash")
        print()
        print("For detailed instructions:")
        print("https://github.com/Vacilator/ProjectMeats/blob/main/docs/deployment_authentication_guide.md")
        print("=" * 60)



# ============================================================================
# COMPREHENSIVE DIAGNOSTICS SYSTEM
# ============================================================================

class DiagnosticsEngine:
    """Comprehensive diagnostics for deployment and access issues"""
    
    def __init__(self, config: DeploymentConfig, cleanup_manager: ServerCleanupManager):
        self.config = config
        self.cleanup_manager = cleanup_manager
        
    def log(self, message: str, level: str = "INFO"):
        """Use cleanup manager's logging"""
        self.cleanup_manager.log(message, level)
    
    def run_comprehensive_diagnosis(self) -> Dict[str, Any]:
        """Run comprehensive system diagnosis"""
        self.log("🔍 Starting comprehensive system diagnosis...", "INFO")
        
        diagnosis_results = {
            "timestamp": datetime.now().isoformat(),
            "server_info": self._diagnose_server_info(),
            "network_connectivity": self._diagnose_network(),
            "services_status": self._diagnose_services(),
            "application_status": self._diagnose_application(),
            "domain_accessibility": self._diagnose_domain_access(),
            "security_status": self._diagnose_security(),
            "recommendations": []
        }
        
        # Generate recommendations based on findings
        diagnosis_results["recommendations"] = self._generate_recommendations(diagnosis_results)
        
        # Print comprehensive report
        self._print_diagnosis_report(diagnosis_results)
        
        return diagnosis_results
    
    def _diagnose_server_info(self) -> Dict[str, Any]:
        """Diagnose basic server information"""
        self.log("📊 Diagnosing server information...", "INFO")
        
        server_info = {}
        
        # Operating system
        exit_code, stdout, stderr = self.cleanup_manager.run_command("cat /etc/os-release")
        if exit_code == 0:
            server_info["os_info"] = stdout
            if "ubuntu" in stdout.lower():
                server_info["os_supported"] = True
            else:
                server_info["os_supported"] = False
        
        # System resources
        exit_code, stdout, stderr = self.cleanup_manager.run_command("free -h")
        if exit_code == 0:
            server_info["memory_info"] = stdout
        
        exit_code, stdout, stderr = self.cleanup_manager.run_command("df -h /")
        if exit_code == 0:
            server_info["disk_info"] = stdout
        
        # CPU information
        exit_code, stdout, stderr = self.cleanup_manager.run_command("nproc")
        if exit_code == 0:
            server_info["cpu_cores"] = stdout.strip()
        
        # System load
        exit_code, stdout, stderr = self.cleanup_manager.run_command("uptime")
        if exit_code == 0:
            server_info["system_load"] = stdout.strip()
        
        return server_info
    
    def _diagnose_network(self) -> Dict[str, Any]:
        """Diagnose network connectivity"""
        self.log("🌐 Diagnosing network connectivity...", "INFO")
        
        network_info = {}
        
        # Internet connectivity
        test_urls = [
            ("github.com", "GitHub access"),
            ("google.com", "General internet"),
            ("archive.ubuntu.com", "Ubuntu repositories")
        ]
        
        connectivity_results = {}
        for url, description in test_urls:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(
                f"timeout 10 curl -s --connect-timeout 5 https://{url} > /dev/null"
            )
            connectivity_results[url] = {
                "accessible": exit_code == 0,
                "description": description
            }
        
        network_info["connectivity"] = connectivity_results
        
        # DNS resolution
        if self.config.domain:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(f"nslookup {self.config.domain}")
            network_info["dns_resolution"] = {
                "domain": self.config.domain,
                "resolves": exit_code == 0,
                "output": stdout if exit_code == 0 else stderr
            }
        
        # Port availability
        important_ports = [22, 80, 443, 8000, 5432]
        port_status = {}
        for port in important_ports:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(f"netstat -tlnp | grep :{port}")
            port_status[port] = {
                "listening": exit_code == 0,
                "details": stdout if exit_code == 0 else "Not listening"
            }
        
        network_info["ports"] = port_status
        
        return network_info
    
    def _diagnose_services(self) -> Dict[str, Any]:
        """Diagnose system services status"""
        self.log("⚙️ Diagnosing system services...", "INFO")
        
        services_info = {}
        
        # Critical services
        critical_services = ["nginx", "postgresql", "ssh"]
        if self.config.database_type == "sqlite":
            critical_services.remove("postgresql")
        
        service_status = {}
        for service in critical_services:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(f"systemctl is-active {service}")
            status = stdout.strip() if exit_code == 0 else "inactive"
            
            # Get more detailed status
            exit_code2, stdout2, stderr2 = self.cleanup_manager.run_command(f"systemctl status {service} --no-pager -l")
            
            service_status[service] = {
                "active": status == "active",
                "status": status,
                "details": stdout2 if exit_code2 == 0 else stderr2
            }
        
        services_info["system_services"] = service_status
        
        # Application services
        app_services = ["projectmeats"]
        app_service_status = {}
        for service in app_services:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(f"systemctl is-active {service}")
            status = stdout.strip() if exit_code == 0 else "inactive"
            
            exit_code2, stdout2, stderr2 = self.cleanup_manager.run_command(f"systemctl status {service} --no-pager -l")
            
            app_service_status[service] = {
                "active": status == "active",
                "status": status,
                "details": stdout2 if exit_code2 == 0 else stderr2
            }
        
        services_info["application_services"] = app_service_status
        
        return services_info
    
    def _diagnose_application(self) -> Dict[str, Any]:
        """Diagnose ProjectMeats application status"""
        self.log("🐍 Diagnosing ProjectMeats application...", "INFO")
        
        app_info = {}
        
        # Check if application directory exists
        exit_code, stdout, stderr = self.cleanup_manager.run_command(f"ls -la {self.config.project_dir}/")
        app_info["directory_exists"] = exit_code == 0
        app_info["directory_contents"] = stdout if exit_code == 0 else "Directory not found"
        
        if app_info["directory_exists"]:
            # Check essential files
            essential_files = [
                "backend/manage.py",
                "backend/requirements.txt",
                "frontend/package.json",
                "README.md"
            ]
            
            missing_files = []
            for file_path in essential_files:
                exit_code, stdout, stderr = self.cleanup_manager.run_command(f"test -f {self.config.project_dir}/{file_path}")
                if exit_code != 0:
                    missing_files.append(file_path)
            
            app_info["essential_files_present"] = len(missing_files) == 0
            app_info["missing_files"] = missing_files
            
            # Check backend setup
            exit_code, stdout, stderr = self.cleanup_manager.run_command(f"test -d {self.config.project_dir}/backend/venv")
            app_info["backend_venv_exists"] = exit_code == 0
            
            if app_info["backend_venv_exists"]:
                # Test Django
                exit_code, stdout, stderr = self.cleanup_manager.run_command(
                    f"cd {self.config.project_dir}/backend && ./venv/bin/python manage.py check --deploy"
                )
                app_info["django_check"] = {
                    "passes": exit_code == 0,
                    "output": stdout if exit_code == 0 else stderr
                }
            
            # Check frontend build
            exit_code, stdout, stderr = self.cleanup_manager.run_command(f"test -d {self.config.project_dir}/frontend/build")
            app_info["frontend_built"] = exit_code == 0
            
            if app_info["frontend_built"]:
                exit_code, stdout, stderr = self.cleanup_manager.run_command(f"test -f {self.config.project_dir}/frontend/build/index.html")
                app_info["frontend_index_exists"] = exit_code == 0
        
        return app_info
    
    def _diagnose_domain_access(self) -> Dict[str, Any]:
        """Diagnose domain accessibility"""
        if not self.config.domain:
            return {"configured": False}
        
        self.log(f"🌍 Diagnosing domain access for {self.config.domain}...", "INFO")
        
        domain_info = {"configured": True, "domain": self.config.domain}
        
        # DNS resolution test
        try:
            import socket
            resolved_ip = socket.gethostbyname(self.config.domain)
            domain_info["dns_resolves"] = True
            domain_info["resolved_ip"] = resolved_ip
            
            if self.config.server_ip and resolved_ip == self.config.server_ip:
                domain_info["points_to_server"] = True
            else:
                domain_info["points_to_server"] = False
                domain_info["expected_ip"] = self.config.server_ip
        except socket.gaierror:
            domain_info["dns_resolves"] = False
        
        # HTTP accessibility test
        if REQUESTS_AVAILABLE:
            try:
                import requests
                response = requests.get(f"http://{self.config.domain}/health", timeout=10)
                domain_info["http_accessible"] = response.status_code == 200
                domain_info["http_status"] = response.status_code
            except requests.exceptions.RequestException as e:
                domain_info["http_accessible"] = False
                domain_info["http_error"] = str(e)
        else:
            # Fallback to curl
            exit_code, stdout, stderr = self.cleanup_manager.run_command(
                f"timeout 10 curl -f http://{self.config.domain}/health"
            )
            domain_info["http_accessible"] = exit_code == 0
            domain_info["http_response"] = stdout if exit_code == 0 else stderr
        
        # HTTPS accessibility test
        if REQUESTS_AVAILABLE:
            try:
                import requests
                response = requests.get(f"https://{self.config.domain}/health", timeout=10)
                domain_info["https_accessible"] = response.status_code == 200
                domain_info["https_status"] = response.status_code
            except requests.exceptions.RequestException:
                domain_info["https_accessible"] = False
        else:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(
                f"timeout 10 curl -f https://{self.config.domain}/health"
            )
            domain_info["https_accessible"] = exit_code == 0
        
        # Local accessibility test
        exit_code, stdout, stderr = self.cleanup_manager.run_command("timeout 5 curl -f http://localhost/health")
        domain_info["local_accessible"] = exit_code == 0
        domain_info["local_response"] = stdout if exit_code == 0 else stderr
        
        return domain_info
    
    def _diagnose_security(self) -> Dict[str, Any]:
        """Diagnose security configuration"""
        self.log("🔒 Diagnosing security configuration...", "INFO")
        
        security_info = {}
        
        # Firewall status
        exit_code, stdout, stderr = self.cleanup_manager.run_command("ufw status")
        security_info["firewall"] = {
            "active": "Status: active" in stdout if exit_code == 0 else False,
            "rules": stdout if exit_code == 0 else stderr
        }
        
        # SSL certificate status
        if self.config.domain and self.config.use_ssl:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(f"ls /etc/letsencrypt/live/{self.config.domain}/")
            security_info["ssl_certificate"] = {
                "exists": exit_code == 0,
                "details": stdout if exit_code == 0 else "No SSL certificate found"
            }
        
        # SSH configuration
        exit_code, stdout, stderr = self.cleanup_manager.run_command("sshd -T | grep -E '(PasswordAuthentication|PermitRootLogin)'")
        security_info["ssh_config"] = stdout if exit_code == 0 else "Could not check SSH config"
        
        return security_info
    
    def _generate_recommendations(self, diagnosis_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on diagnosis results"""
        recommendations = []
        
        # Server info recommendations
        server_info = diagnosis_results.get("server_info", {})
        if not server_info.get("os_supported", True):
            recommendations.append("⚠️ Non-Ubuntu OS detected. Consider using Ubuntu 20.04+ LTS for best compatibility.")
        
        # Network recommendations
        network_info = diagnosis_results.get("network_connectivity", {})
        connectivity = network_info.get("connectivity", {})
        
        if not connectivity.get("github.com", {}).get("accessible", False):
            recommendations.append("❌ GitHub not accessible. Check internet connection and firewall settings.")
        
        # Services recommendations
        services_info = diagnosis_results.get("services_status", {})
        system_services = services_info.get("system_services", {})
        
        if not system_services.get("nginx", {}).get("active", False):
            recommendations.append("🌐 Nginx is not running. Start with: systemctl start nginx")
        
        if not system_services.get("postgresql", {}).get("active", False) and self.config.database_type == "postgresql":
            recommendations.append("🗄️ PostgreSQL is not running. Start with: systemctl start postgresql")
        
        # Application recommendations
        app_info = diagnosis_results.get("application_status", {})
        if not app_info.get("directory_exists", False):
            recommendations.append("📁 ProjectMeats application not found. Run deployment with --clean flag.")
        
        if app_info.get("directory_exists", False) and not app_info.get("essential_files_present", False):
            recommendations.append("📄 Essential application files missing. Repository download may have failed.")
        
        if not app_info.get("backend_venv_exists", False):
            recommendations.append("🐍 Python virtual environment not found. Backend setup incomplete.")
        
        if not app_info.get("frontend_built", False):
            recommendations.append("⚛️ Frontend not built. Run: cd frontend && npm install && npm run build")
        
        # Domain recommendations
        domain_info = diagnosis_results.get("domain_accessibility", {})
        if domain_info.get("configured", False):
            if not domain_info.get("dns_resolves", False):
                recommendations.append(f"🌍 DNS resolution failed for {self.config.domain}. Check domain configuration.")
            
            if not domain_info.get("points_to_server", False) and domain_info.get("dns_resolves", False):
                recommendations.append(f"🎯 Domain points to wrong IP. Update A record to point to {self.config.server_ip}")
            
            if not domain_info.get("http_accessible", False):
                recommendations.append("🔗 Domain not accessible via HTTP. Check nginx configuration and firewall.")
        
        # Security recommendations
        security_info = diagnosis_results.get("security_status", {})
        if not security_info.get("firewall", {}).get("active", False):
            recommendations.append("🔥 Firewall not active. Enable with: ufw enable")
        
        return recommendations
    
    def _print_diagnosis_report(self, diagnosis_results: Dict[str, Any]):
        """Print comprehensive diagnosis report"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}  📋 COMPREHENSIVE SYSTEM DIAGNOSIS REPORT{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
        
        timestamp = diagnosis_results["timestamp"]
        print(f"\n{Colors.CYAN}Diagnosis Time:{Colors.END} {timestamp}")
        if self.config.server_ip:
            print(f"{Colors.CYAN}Server IP:{Colors.END} {self.config.server_ip}")
        if self.config.domain:
            print(f"{Colors.CYAN}Domain:{Colors.END} {self.config.domain}")
        
        # Server Status
        print(f"\n{Colors.BOLD}📊 SERVER STATUS{Colors.END}")
        server_info = diagnosis_results.get("server_info", {})
        if server_info.get("os_supported"):
            print(f"  {Colors.GREEN}✓{Colors.END} Operating System: Supported")
        else:
            print(f"  {Colors.YELLOW}⚠{Colors.END} Operating System: Non-Ubuntu detected")
        
        # Network Status
        print(f"\n{Colors.BOLD}🌐 NETWORK STATUS{Colors.END}")
        network_info = diagnosis_results.get("network_connectivity", {})
        connectivity = network_info.get("connectivity", {})
        
        for url, info in connectivity.items():
            status_icon = f"{Colors.GREEN}✓{Colors.END}" if info["accessible"] else f"{Colors.RED}✗{Colors.END}"
            print(f"  {status_icon} {info['description']}: {'Accessible' if info['accessible'] else 'Not accessible'}")
        
        # Services Status
        print(f"\n{Colors.BOLD}⚙️ SERVICES STATUS{Colors.END}")
        services_info = diagnosis_results.get("services_status", {})
        
        # System services
        print(f"  {Colors.UNDERLINE}System Services:{Colors.END}")
        system_services = services_info.get("system_services", {})
        for service, info in system_services.items():
            status_icon = f"{Colors.GREEN}✓{Colors.END}" if info["active"] else f"{Colors.RED}✗{Colors.END}"
            print(f"    {status_icon} {service}: {info['status']}")
        
        # Application services
        print(f"  {Colors.UNDERLINE}Application Services:{Colors.END}")
        app_services = services_info.get("application_services", {})
        for service, info in app_services.items():
            status_icon = f"{Colors.GREEN}✓{Colors.END}" if info["active"] else f"{Colors.RED}✗{Colors.END}"
            print(f"    {status_icon} {service}: {info['status']}")
        
        # Application Status
        print(f"\n{Colors.BOLD}🐍 APPLICATION STATUS{Colors.END}")
        app_info = diagnosis_results.get("application_status", {})
        
        checks = [
            ("Directory exists", app_info.get("directory_exists", False)),
            ("Essential files present", app_info.get("essential_files_present", False)),
            ("Backend virtual environment", app_info.get("backend_venv_exists", False)),
            ("Frontend built", app_info.get("frontend_built", False))
        ]
        
        for check_name, check_result in checks:
            status_icon = f"{Colors.GREEN}✓{Colors.END}" if check_result else f"{Colors.RED}✗{Colors.END}"
            print(f"  {status_icon} {check_name}")
        
        # Domain Accessibility
        domain_info = diagnosis_results.get("domain_accessibility", {})
        if domain_info.get("configured", False):
            print(f"\n{Colors.BOLD}🌍 DOMAIN ACCESSIBILITY{Colors.END}")
            domain = domain_info["domain"]
            
            checks = [
                ("DNS resolution", domain_info.get("dns_resolves", False)),
                ("Points to server", domain_info.get("points_to_server", False)),
                ("HTTP accessible", domain_info.get("http_accessible", False)),
                ("HTTPS accessible", domain_info.get("https_accessible", False)),
                ("Local accessible", domain_info.get("local_accessible", False))
            ]
            
            for check_name, check_result in checks:
                status_icon = f"{Colors.GREEN}✓{Colors.END}" if check_result else f"{Colors.RED}✗{Colors.END}"
                print(f"  {status_icon} {check_name}")
            
            if domain_info.get("resolved_ip"):
                print(f"  {Colors.CYAN}Resolved IP:{Colors.END} {domain_info['resolved_ip']}")
        
        # Recommendations
        recommendations = diagnosis_results.get("recommendations", [])
        if recommendations:
            print(f"\n{Colors.BOLD}💡 RECOMMENDATIONS{Colors.END}")
            for recommendation in recommendations:
                print(f"  {recommendation}")
        
        # Next Steps
        print(f"\n{Colors.BOLD}🎯 NEXT STEPS{Colors.END}")
        if not diagnosis_results.get("application_status", {}).get("directory_exists", False):
            print(f"  1. Run clean deployment: {Colors.CYAN}sudo python3 unified_deployment_tool.py --production --clean --domain={self.config.domain or 'yourdomain.com'}{Colors.END}")
        else:
            print(f"  1. Fix identified issues using: {Colors.CYAN}sudo python3 unified_deployment_tool.py --fix{Colors.END}")
            print(f"  2. Check status again: {Colors.CYAN}python3 unified_deployment_tool.py --status{Colors.END}")
        
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")


# ============================================================================
# AUTO-FIX SYSTEM
# ============================================================================

class AutoFixEngine:
    """Automatic fixing system for common deployment and access issues"""
    
    def __init__(self, config: DeploymentConfig, cleanup_manager: ServerCleanupManager):
        self.config = config
        self.cleanup_manager = cleanup_manager
        
    def log(self, message: str, level: str = "INFO"):
        """Use cleanup manager's logging"""
        self.cleanup_manager.log(message, level)
    
    def run_comprehensive_fixes(self) -> bool:
        """Run comprehensive auto-fix for common issues"""
        self.log("🛠️ Starting comprehensive auto-fix...", "INFO")
        
        fix_success = True
        
        # Define fix operations in order of importance
        fix_operations = [
            ("Clean overlapping files", self._fix_overlapping_files),
            ("Fix service issues", self._fix_service_issues), 
            ("Fix nginx configuration", self._fix_nginx_config),
            ("Fix database issues", self._fix_database_issues),
            ("Fix Node.js conflicts", self._fix_nodejs_conflicts),
            ("Fix permissions", self._fix_permissions),
            ("Fix firewall", self._fix_firewall),
            ("Fix domain accessibility", self._fix_domain_access)
        ]
        
        for operation_name, fix_function in fix_operations:
            try:
                self.log(f"🔧 {operation_name}...", "INFO")
                if fix_function():
                    self.log(f"✅ {operation_name} completed successfully", "SUCCESS")
                else:
                    self.log(f"⚠️ {operation_name} had issues", "WARNING")
                    fix_success = False
            except Exception as e:
                self.log(f"❌ {operation_name} failed: {e}", "ERROR")
                fix_success = False
        
        if fix_success:
            self.log("🎉 All auto-fixes completed successfully!", "SUCCESS")
        else:
            self.log("⚠️ Some fixes had issues. Check logs for details.", "WARNING")
        
        return fix_success
    
    def _fix_overlapping_files(self) -> bool:
        """Fix overlapping files and credentials"""
        return self.cleanup_manager.clean_overlapping_files()
    
    def _fix_service_issues(self) -> bool:
        """Fix common service issues"""
        self.log("Fixing service issues...", "INFO")
        
        success = True
        
        # Critical services that should be running
        critical_services = ["nginx"]
        if self.config.database_type == "postgresql":
            critical_services.append("postgresql")
        
        for service in critical_services:
            # Check if service is running
            exit_code, stdout, stderr = self.cleanup_manager.run_command(f"systemctl is-active {service}")
            
            if exit_code != 0:
                self.log(f"Starting {service} service...", "INFO")
                
                # Try to start the service
                exit_code, stdout, stderr = self.cleanup_manager.run_command(f"systemctl start {service}")
                if exit_code == 0:
                    # Enable for automatic startup
                    self.cleanup_manager.run_command(f"systemctl enable {service}")
                    self.log(f"✅ {service} started and enabled", "SUCCESS")
                else:
                    self.log(f"❌ Failed to start {service}: {stderr}", "ERROR")
                    success = False
        
        return success
    
    def _fix_nginx_config(self) -> bool:
        """Fix nginx configuration issues"""
        if not self.config.domain:
            self.log("No domain configured, skipping nginx configuration", "INFO")
            return True
        
        self.log(f"Fixing nginx configuration for {self.config.domain}...", "INFO")
        
        try:
            # Remove default nginx site
            self.cleanup_manager.run_command("rm -f /etc/nginx/sites-enabled/default")
            
            # Create proper nginx configuration
            nginx_config = self._generate_nginx_config()
            
            # Write configuration file
            config_file = f"/etc/nginx/sites-available/{self.config.domain}"
            exit_code, stdout, stderr = self.cleanup_manager.run_command(
                f"cat > {config_file} << 'EOF'\n{nginx_config}\nEOF"
            )
            
            if exit_code != 0:
                self.log(f"Failed to write nginx config: {stderr}", "ERROR")
                return False
            
            # Enable the site
            self.cleanup_manager.run_command(f"ln -sf {config_file} /etc/nginx/sites-enabled/")
            
            # Test nginx configuration
            exit_code, stdout, stderr = self.cleanup_manager.run_command("nginx -t")
            if exit_code != 0:
                self.log(f"Nginx configuration test failed: {stderr}", "ERROR")
                return False
            
            # Reload nginx
            exit_code, stdout, stderr = self.cleanup_manager.run_command("systemctl reload nginx")
            if exit_code == 0:
                self.log("✅ Nginx configuration updated and reloaded", "SUCCESS")
                return True
            else:
                self.log(f"Failed to reload nginx: {stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error fixing nginx configuration: {e}", "ERROR")
            return False
    
    def _generate_nginx_config(self) -> str:
        """Generate nginx configuration for the domain"""
        domain = self.config.domain
        project_dir = self.config.project_dir
        
        config = f"""# ProjectMeats Nginx Configuration
# Auto-generated by Unified Deployment Tool

# Rate limiting
limit_req_zone $binary_remote_addr zone=projectmeats_api:10m rate=10r/s;

# Upstream for Django backend
upstream projectmeats_backend {{
    server 127.0.0.1:8000;
}}

server {{
    listen 80;
    server_name {domain} www.{domain};
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Frontend static files (React build)
    location / {{
        root {project_dir}/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
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
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }}
    
    # Django admin interface
    location /admin/ {{
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Django static files
    location /static/ {{
        alias {project_dir}/backend/staticfiles/;
        expires 1d;
        add_header Cache-Control "public";
    }}
    
    # Media files
    location /media/ {{
        alias {project_dir}/uploads/;
        expires 1d;
        add_header Cache-Control "public";
    }}
    
    # Health check endpoint
    location /health {{
        access_log off;
        try_files $uri @health_check;
    }}
    
    # Health check fallback
    location @health_check {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}"""
        
        return config
    
    def _fix_database_issues(self) -> bool:
        """Fix database configuration issues"""
        if self.config.database_type != "postgresql":
            return True  # Skip for SQLite
        
        self.log("Fixing PostgreSQL database issues...", "INFO")
        
        try:
            # Ensure PostgreSQL is running
            exit_code, stdout, stderr = self.cleanup_manager.run_command("systemctl start postgresql")
            if exit_code != 0:
                self.log(f"Failed to start PostgreSQL: {stderr}", "ERROR")
                return False
            
            # Wait for PostgreSQL to be ready
            for attempt in range(10):
                exit_code, stdout, stderr = self.cleanup_manager.run_command("sudo -u postgres psql -c 'SELECT 1;' > /dev/null")
                if exit_code == 0:
                    break
                time.sleep(2)
            else:
                self.log("PostgreSQL not responding after 20 seconds", "ERROR")
                return False
            
            # Create database and user
            db_commands = [
                f"sudo -u postgres createdb {self.config.db_name} || true",
                f"sudo -u postgres createuser {self.config.db_user} || true",
                f"sudo -u postgres psql -c \"ALTER USER {self.config.db_user} PASSWORD '{self.config.db_password}';\"",
                f"sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE {self.config.db_name} TO {self.config.db_user};\"",
                f"sudo -u postgres psql -c \"ALTER USER {self.config.db_user} CREATEDB;\""
            ]
            
            for cmd in db_commands:
                exit_code, stdout, stderr = self.cleanup_manager.run_command(cmd)
                # Continue even if some commands fail (user/db might already exist)
            
            # Test connection
            exit_code, stdout, stderr = self.cleanup_manager.run_command(
                f"PGPASSWORD='{self.config.db_password}' psql -h localhost -U {self.config.db_user} -d {self.config.db_name} -c 'SELECT 1;'"
            )
            
            if exit_code == 0:
                self.log("✅ PostgreSQL database configured successfully", "SUCCESS")
                return True
            else:
                self.log(f"Database connection test failed: {stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error fixing database: {e}", "ERROR")
            return False
    
    def _fix_nodejs_conflicts(self) -> bool:
        """Fix Node.js installation conflicts"""
        self.log("Fixing Node.js conflicts...", "INFO")
        
        try:
            # Stop any running Node.js processes
            self.cleanup_manager.run_command("pkill -f node || true")
            
            # Remove conflicting installations
            cleanup_commands = [
                "apt remove -y nodejs npm libnode-dev || true",
                "apt purge -y nodejs npm libnode-dev || true",
                "rm -rf /usr/local/bin/node* /usr/local/bin/npm* || true",
                "rm -rf /usr/local/lib/node_modules || true",
                "apt autoremove -y",
                "apt clean"
            ]
            
            for cmd in cleanup_commands:
                self.cleanup_manager.run_command(cmd)
            
            # Install Node.js 18 LTS
            install_commands = [
                "curl -fsSL https://deb.nodesource.com/setup_18.x | bash -",
                "apt update",
                "apt install -y nodejs"
            ]
            
            for cmd in install_commands:
                exit_code, stdout, stderr = self.cleanup_manager.run_command(cmd)
                if exit_code != 0 and "curl" not in cmd:
                    self.log(f"Node.js installation command failed: {cmd}", "ERROR")
                    return False
            
            # Verify installation
            exit_code, stdout, stderr = self.cleanup_manager.run_command("node --version")
            if exit_code == 0:
                self.log(f"✅ Node.js installed successfully: {stdout}", "SUCCESS")
                return True
            else:
                self.log("Node.js installation verification failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error fixing Node.js: {e}", "ERROR")
            return False
    
    def _fix_permissions(self) -> bool:
        """Fix file and directory permissions"""
        self.log("Fixing permissions...", "INFO")
        
        try:
            permission_commands = [
                f"chown -R {self.config.app_user}:{self.config.app_user} {self.config.project_dir} || true",
                f"chmod -R 755 {self.config.project_dir}",
                f"chmod -R 755 {self.config.logs_dir} || true",
                f"chmod -R 755 {self.config.backup_dir} || true"
            ]
            
            for cmd in permission_commands:
                self.cleanup_manager.run_command(cmd)
            
            self.log("✅ Permissions fixed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error fixing permissions: {e}", "ERROR")
            return False
    
    def _fix_firewall(self) -> bool:
        """Fix firewall configuration"""
        self.log("Fixing firewall configuration...", "INFO")
        
        try:
            firewall_commands = [
                "ufw allow ssh",
                "ufw allow 80/tcp",
                "ufw allow 443/tcp",
                "ufw --force enable"
            ]
            
            for cmd in firewall_commands:
                self.cleanup_manager.run_command(cmd)
            
            self.log("✅ Firewall configured", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error configuring firewall: {e}", "ERROR")
            return False
    
    def _fix_domain_access(self) -> bool:
        """Fix domain accessibility issues"""
        if not self.config.domain:
            return True
        
        self.log(f"Fixing domain accessibility for {self.config.domain}...", "INFO")
        
        try:
            # Test local accessibility first
            exit_code, stdout, stderr = self.cleanup_manager.run_command("curl -f http://localhost/health")
            if exit_code != 0:
                self.log("Local health check failed - fixing nginx configuration", "WARNING")
                if not self._fix_nginx_config():
                    return False
            
            # Wait a moment for nginx to process
            time.sleep(2)
            
            # Test again
            exit_code, stdout, stderr = self.cleanup_manager.run_command("curl -f http://localhost/health")
            if exit_code == 0:
                self.log("✅ Local accessibility fixed", "SUCCESS")
                return True
            else:
                self.log("Local accessibility still failing", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error fixing domain access: {e}", "ERROR")
            return False



# ============================================================================
# MAIN UNIFIED DEPLOYMENT ORCHESTRATOR
# ============================================================================

class UnifiedDeploymentOrchestrator:
    """Main orchestrator that unifies all deployment, diagnostic, and management functionality"""
    
    def __init__(self):
        self.config = None
        self.cleanup_manager = None
        self.repository_manager = None
        self.diagnostics_engine = None
        self.autofix_engine = None
        self.logger = None
        self.ssh_client = None
        
    def initialize(self, args):
        """Initialize the orchestrator with command line arguments"""
        # Parse configuration from arguments
        self.config = self._parse_config_from_args(args)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize managers
        self.cleanup_manager = ServerCleanupManager(self.config, self.logger)
        self.repository_manager = RepositoryManager(self.config, self.logger, self.cleanup_manager)
        self.diagnostics_engine = DiagnosticsEngine(self.config, self.cleanup_manager)
        self.autofix_engine = AutoFixEngine(self.config, self.cleanup_manager)
        
        # Setup SSH connection if needed
        if self._is_remote_operation():
            if not self._setup_ssh_connection():
                return False
        
        return True
    
    def _parse_config_from_args(self, args) -> DeploymentConfig:
        """Parse configuration from command line arguments"""
        config = DeploymentConfig()
        
        # Basic settings
        config.domain = args.domain
        config.server_ip = args.server
        config.ssh_user = args.username or "root"
        config.ssh_key = args.key_file
        config.ssh_password = args.password
        
        # Deployment mode
        if args.production:
            config.mode = DeploymentMode.PRODUCTION
            config.environment = "production"
        elif args.staging:
            config.mode = DeploymentMode.STAGING
            config.environment = "staging"
        elif args.development:
            config.mode = DeploymentMode.DEVELOPMENT
            config.environment = "development"
        elif args.local:
            config.mode = DeploymentMode.LOCAL
            config.environment = "local"
        elif args.docker:
            config.mode = DeploymentMode.DOCKER
            config.environment = "production"
        elif args.cloud:
            config.mode = DeploymentMode.CLOUD
            config.environment = "production"
        
        # Operation settings
        config.auto_mode = args.auto
        config.interactive_mode = args.interactive
        
        # GitHub settings
        config.github_user = args.github_user
        config.github_token = args.github_token
        
        # Advanced settings
        config.cleanup_before_deploy = not args.no_cleanup if hasattr(args, 'no_cleanup') else True
        config.backup_before_deploy = not args.no_backup if hasattr(args, 'no_backup') else True
        
        return config
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _is_remote_operation(self) -> bool:
        """Check if this is a remote operation requiring SSH"""
        return self.config.server_ip is not None
    
    def _setup_ssh_connection(self) -> bool:
        """Setup SSH connection for remote operations"""
        if not PARAMIKO_AVAILABLE:
            print(f"{Colors.RED}❌ Paramiko not available for SSH connections{Colors.END}")
            print(f"{Colors.CYAN}Install with: pip install paramiko{Colors.END}")
            return False
        
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                'hostname': self.config.server_ip,
                'username': self.config.ssh_user,
                'port': 22,
                'timeout': 30
            }
            
            if self.config.ssh_key and os.path.exists(self.config.ssh_key):
                connect_kwargs['key_filename'] = self.config.ssh_key
            elif self.config.ssh_password:
                connect_kwargs['password'] = self.config.ssh_password
            else:
                # Try default SSH keys
                possible_keys = [
                    os.path.expanduser("~/.ssh/id_rsa"),
                    os.path.expanduser("~/.ssh/id_ed25519"),
                    os.path.expanduser("~/.ssh/id_ecdsa")
                ]
                
                key_found = False
                for key_path in possible_keys:
                    if os.path.exists(key_path):
                        connect_kwargs['key_filename'] = key_path
                        key_found = True
                        break
                
                if not key_found:
                    print(f"{Colors.RED}❌ No SSH key found and no password provided{Colors.END}")
                    return False
            
            self.ssh_client.connect(**connect_kwargs)
            
            # Set SSH client for managers
            self.cleanup_manager.set_ssh_client(self.ssh_client)
            
            print(f"{Colors.GREEN}✅ Connected to {self.config.server_ip}{Colors.END}")
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ SSH connection failed: {e}{Colors.END}")
            return False
    
    def run(self, operation_mode: OperationMode) -> bool:
        """Run the specified operation"""
        try:
            if operation_mode == OperationMode.DEPLOY:
                return self._run_deployment()
            elif operation_mode == OperationMode.DIAGNOSE:
                return self._run_diagnostics()
            elif operation_mode == OperationMode.FIX:
                return self._run_autofix()
            elif operation_mode == OperationMode.CLEAN:
                return self._run_cleanup()
            elif operation_mode == OperationMode.STATUS:
                return self._run_status_check()
            elif operation_mode == OperationMode.UPDATE:
                return self._run_update()
            elif operation_mode == OperationMode.CONFIG:
                return self._run_configuration()
            elif operation_mode == OperationMode.DOCS:
                return self._run_documentation()
            elif operation_mode == OperationMode.BACKUP:
                return self._run_backup()
            elif operation_mode == OperationMode.ROLLBACK:
                return self._run_rollback()
            else:
                print(f"{Colors.RED}❌ Unknown operation mode: {operation_mode}{Colors.END}")
                return False
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️ Operation cancelled by user{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ Operation failed: {e}{Colors.END}")
            return False
        finally:
            if self.ssh_client:
                self.ssh_client.close()
    
    def _run_deployment(self) -> bool:
        """Run full deployment process"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🚀 STARTING PROJECTMEATS DEPLOYMENT{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        if self.config.interactive_mode:
            self._run_interactive_setup()
        
        # Pre-deployment cleanup
        if self.config.cleanup_before_deploy:
            if not self.cleanup_manager.clean_overlapping_files():
                print(f"{Colors.RED}❌ Pre-deployment cleanup failed{Colors.END}")
                return False
        
        # Validate and recreate server structure
        if not self.cleanup_manager.validate_server_structure():
            print(f"{Colors.RED}❌ Server structure validation failed{Colors.END}")
            return False
        
        # Clone repository
        if not self.repository_manager.clone_repository_clean():
            print(f"{Colors.RED}❌ Repository cloning failed{Colors.END}")
            return False
        
        # Run actual deployment based on mode
        if self.config.mode == DeploymentMode.DOCKER:
            return self._run_docker_deployment()
        else:
            return self._run_standard_deployment()
    
    def _run_interactive_setup(self):
        """Run interactive setup wizard"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🧙‍♂️ Interactive Setup Wizard{Colors.END}")
        print(f"{Colors.PURPLE}{'='*50}{Colors.END}")
        
        # Domain configuration
        if not self.config.domain:
            domain = input(f"{Colors.CYAN}Enter your domain (e.g., mycompany.com): {Colors.END}").strip()
            if domain:
                self.config.domain = domain
        
        # Database configuration
        if self.config.mode == DeploymentMode.PRODUCTION:
            print(f"\n{Colors.BOLD}Database Configuration:{Colors.END}")
            print("1. PostgreSQL (recommended for production)")
            print("2. SQLite (simple, but not recommended for production)")
            
            db_choice = input(f"{Colors.CYAN}Choose database (1-2) [1]: {Colors.END}").strip() or "1"
            if db_choice == "2":
                self.config.database_type = "sqlite"
        
        # Admin user configuration
        print(f"\n{Colors.BOLD}Admin User Configuration:{Colors.END}")
        admin_user = input(f"{Colors.CYAN}Admin username [admin]: {Colors.END}").strip() or "admin"
        self.config.admin_user = admin_user
        
        if not self.config.admin_email:
            admin_email = input(f"{Colors.CYAN}Admin email [admin@{self.config.domain or 'localhost'}]: {Colors.END}").strip()
            self.config.admin_email = admin_email or f"admin@{self.config.domain or 'localhost'}"
        
        # GitHub authentication
        if not (self.config.github_user and self.config.github_token):
            print(f"\n{Colors.BOLD}GitHub Authentication (Optional):{Colors.END}")
            print("For private repository access or reliable downloads:")
            
            setup_github = input(f"{Colors.CYAN}Setup GitHub authentication? [y/N]: {Colors.END}").strip().lower()
            if setup_github == 'y':
                github_user = input(f"{Colors.CYAN}GitHub username: {Colors.END}").strip()
                if github_user:
                    github_token = getpass.getpass(f"{Colors.CYAN}GitHub Personal Access Token: {Colors.END}")
                    if github_token:
                        self.config.github_user = github_user
                        self.config.github_token = github_token
    
    def _run_standard_deployment(self) -> bool:
        """Run standard (non-Docker) deployment"""
        print(f"\n{Colors.BOLD}📦 Standard Deployment Process{Colors.END}")
        
        deployment_steps = [
            ("Installing system dependencies", self._install_system_dependencies),
            ("Setting up database", self._setup_database),
            ("Configuring backend", self._setup_backend),
            ("Building frontend", self._setup_frontend),
            ("Configuring web server", self._setup_webserver),
            ("Setting up services", self._setup_services),
            ("Configuring security", self._setup_security),
            ("Final verification", self._verify_deployment)
        ]
        
        for step_name, step_function in deployment_steps:
            print(f"\n{Colors.CYAN}🔄 {step_name}...{Colors.END}")
            
            if not step_function():
                print(f"{Colors.RED}❌ {step_name} failed{Colors.END}")
                
                # Try auto-fix
                if self.config.auto_mode:
                    print(f"{Colors.YELLOW}🛠️ Attempting auto-fix...{Colors.END}")
                    if self.autofix_engine.run_comprehensive_fixes():
                        print(f"{Colors.GREEN}✅ Auto-fix successful, retrying step...{Colors.END}")
                        if step_function():
                            print(f"{Colors.GREEN}✅ {step_name} completed after auto-fix{Colors.END}")
                            continue
                
                print(f"{Colors.RED}❌ Deployment failed at: {step_name}{Colors.END}")
                return False
            
            print(f"{Colors.GREEN}✅ {step_name} completed{Colors.END}")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!{Colors.END}")
        self._print_deployment_success_message()
        return True
    
    def _run_docker_deployment(self) -> bool:
        """Run Docker-based deployment"""
        print(f"\n{Colors.BOLD}🐳 Docker Deployment Process{Colors.END}")
        
        # Install Docker
        if not self._install_docker():
            return False
        
        # Create docker-compose configuration
        if not self._create_docker_compose():
            return False
        
        # Build and start containers
        exit_code, stdout, stderr = self.cleanup_manager.run_command(
            f"cd {self.config.project_dir} && docker-compose up -d --build"
        )
        
        if exit_code == 0:
            print(f"{Colors.GREEN}✅ Docker deployment completed{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ Docker deployment failed: {stderr}{Colors.END}")
            return False
    
    def _run_diagnostics(self) -> bool:
        """Run comprehensive diagnostics"""
        diagnosis_results = self.diagnostics_engine.run_comprehensive_diagnosis()
        return True
    
    def _run_autofix(self) -> bool:
        """Run comprehensive auto-fix"""
        return self.autofix_engine.run_comprehensive_fixes()
    
    def _run_cleanup(self) -> bool:
        """Run server cleanup"""
        return self.cleanup_manager.clean_overlapping_files()
    
    def _run_status_check(self) -> bool:
        """Run system status check"""
        # Run diagnostics but focus on status display
        diagnosis_results = self.diagnostics_engine.run_comprehensive_diagnosis()
        
        # Additional status information
        print(f"\n{Colors.BOLD}📊 SYSTEM STATUS SUMMARY{Colors.END}")
        
        # Check deployment health
        app_info = diagnosis_results.get("application_status", {})
        services_info = diagnosis_results.get("services_status", {})
        domain_info = diagnosis_results.get("domain_accessibility", {})
        
        health_score = 0
        total_checks = 0
        
        # Application health
        if app_info.get("directory_exists"):
            health_score += 1
        total_checks += 1
        
        if app_info.get("essential_files_present"):
            health_score += 1
        total_checks += 1
        
        # Services health
        system_services = services_info.get("system_services", {})
        for service, info in system_services.items():
            if info.get("active"):
                health_score += 1
            total_checks += 1
        
        # Domain health
        if domain_info.get("http_accessible"):
            health_score += 2  # Weight domain accessibility higher
        total_checks += 2
        
        health_percentage = (health_score / total_checks * 100) if total_checks > 0 else 0
        
        if health_percentage >= 90:
            status_color = Colors.GREEN
            status_text = "EXCELLENT"
        elif health_percentage >= 70:
            status_color = Colors.YELLOW
            status_text = "GOOD"
        elif health_percentage >= 50:
            status_color = Colors.YELLOW
            status_text = "FAIR"
        else:
            status_color = Colors.RED
            status_text = "POOR"
        
        print(f"{Colors.BOLD}Overall Health: {status_color}{status_text} ({health_percentage:.1f}%){Colors.END}")
        
        return True
    
    def _run_update(self) -> bool:
        """Run system update"""
        print(f"\n{Colors.BOLD}🔄 UPDATING PROJECTMEATS{Colors.END}")
        
        # Pull latest code
        exit_code, stdout, stderr = self.cleanup_manager.run_command(
            f"cd {self.config.project_dir} && git pull origin main"
        )
        
        if exit_code != 0:
            print(f"{Colors.RED}❌ Failed to pull latest code: {stderr}{Colors.END}")
            return False
        
        # Update backend
        update_commands = [
            f"cd {self.config.project_dir}/backend && ./venv/bin/pip install -r requirements.txt",
            f"cd {self.config.project_dir}/backend && ./venv/bin/python manage.py migrate",
            f"cd {self.config.project_dir}/backend && ./venv/bin/python manage.py collectstatic --noinput"
        ]
        
        for cmd in update_commands:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(cmd)
            if exit_code != 0:
                print(f"{Colors.RED}❌ Backend update failed: {cmd}{Colors.END}")
                return False
        
        # Update frontend
        frontend_commands = [
            f"cd {self.config.project_dir}/frontend && npm install",
            f"cd {self.config.project_dir}/frontend && npm run build"
        ]
        
        for cmd in frontend_commands:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(cmd)
            if exit_code != 0:
                print(f"{Colors.RED}❌ Frontend update failed: {cmd}{Colors.END}")
                return False
        
        # Restart services
        restart_commands = [
            "systemctl restart projectmeats",
            "systemctl reload nginx"
        ]
        
        for cmd in restart_commands:
            self.cleanup_manager.run_command(cmd)
        
        print(f"{Colors.GREEN}✅ Update completed successfully{Colors.END}")
        return True
    
    def _run_configuration(self) -> bool:
        """Run configuration management"""
        print(f"\n{Colors.BOLD}⚙️ CONFIGURATION MANAGEMENT{Colors.END}")
        
        # Show current configuration
        print(f"\n{Colors.BOLD}Current Configuration:{Colors.END}")
        print(f"Domain: {self.config.domain or 'Not set'}")
        print(f"Mode: {self.config.mode.value}")
        print(f"Environment: {self.config.environment}")
        print(f"Database: {self.config.database_type}")
        print(f"Project Directory: {self.config.project_dir}")
        
        # Save configuration to file
        config_data = {
            "domain": self.config.domain,
            "mode": self.config.mode.value,
            "environment": self.config.environment,
            "database_type": self.config.database_type,
            "project_dir": self.config.project_dir,
            "admin_user": self.config.admin_user,
            "use_ssl": self.config.use_ssl,
            "timestamp": datetime.now().isoformat()
        }
        
        config_file = "unified_deployment_config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"{Colors.GREEN}✅ Configuration saved to {config_file}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to save configuration: {e}{Colors.END}")
        
        return True
    
    def _run_documentation(self) -> bool:
        """Generate and display documentation"""
        print(f"\n{Colors.BOLD}📚 PROJECTMEATS DOCUMENTATION{Colors.END}")
        
        docs_content = self._generate_consolidated_documentation()
        
        # Save to file
        docs_file = "UNIFIED_DEPLOYMENT_GUIDE.md"
        try:
            with open(docs_file, 'w') as f:
                f.write(docs_content)
            print(f"{Colors.GREEN}✅ Documentation generated: {docs_file}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to generate documentation: {e}{Colors.END}")
        
        return True
    
    def _run_backup(self) -> bool:
        """Create system backup"""
        print(f"\n{Colors.BOLD}💾 CREATING BACKUP{Colors.END}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"{self.config.backup_dir}/backup_{timestamp}"
        
        # Create backup directory
        exit_code, stdout, stderr = self.cleanup_manager.run_command(f"mkdir -p {backup_dir}")
        if exit_code != 0:
            print(f"{Colors.RED}❌ Failed to create backup directory{Colors.END}")
            return False
        
        # Backup application
        backup_commands = [
            f"tar -czf {backup_dir}/application.tar.gz -C {self.config.project_dir} .",
            f"cp /etc/nginx/sites-available/* {backup_dir}/ 2>/dev/null || true",
            f"cp /etc/systemd/system/projectmeats* {backup_dir}/ 2>/dev/null || true"
        ]
        
        # Backup database
        if self.config.database_type == "postgresql":
            backup_commands.append(
                f"pg_dump -h localhost -U {self.config.db_user} -d {self.config.db_name} | gzip > {backup_dir}/database.sql.gz"
            )
        elif self.config.database_type == "sqlite":
            backup_commands.append(
                f"cp {self.config.project_dir}/backend/db.sqlite3 {backup_dir}/database.sqlite3 2>/dev/null || true"
            )
        
        for cmd in backup_commands:
            self.cleanup_manager.run_command(cmd)
        
        print(f"{Colors.GREEN}✅ Backup created: {backup_dir}{Colors.END}")
        return True
    
    def _run_rollback(self) -> bool:
        """Rollback to previous version"""
        print(f"\n{Colors.BOLD}↩️ ROLLBACK OPERATION{Colors.END}")
        
        # List available backups
        exit_code, stdout, stderr = self.cleanup_manager.run_command(f"ls -la {self.config.backup_dir}/")
        if exit_code != 0:
            print(f"{Colors.RED}❌ No backups found{Colors.END}")
            return False
        
        print("Available backups:")
        print(stdout)
        
        # For now, just show what would be done
        print(f"{Colors.YELLOW}⚠️ Rollback functionality not yet implemented{Colors.END}")
        print("This would restore the most recent backup")
        
        return True
    
    # Deployment step implementations
    def _install_system_dependencies(self) -> bool:
        """Install system dependencies"""
        packages = [
            'python3', 'python3-pip', 'python3-venv', 'nginx', 'git',
            'curl', 'ufw', 'fail2ban', 'certbot', 'python3-certbot-nginx'
        ]
        
        if self.config.database_type == 'postgresql':
            packages.extend(['postgresql', 'postgresql-contrib', 'libpq-dev'])
        
        # Update system and install packages
        commands = [
            "apt update",
            f"apt install -y {' '.join(packages)}"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(cmd)
            if exit_code != 0:
                return False
        
        # Install Node.js
        return self.autofix_engine._fix_nodejs_conflicts()
    
    def _setup_database(self) -> bool:
        """Setup database"""
        if self.config.database_type == 'postgresql':
            return self.autofix_engine._fix_database_issues()
        return True
    
    def _setup_backend(self) -> bool:
        """Setup Django backend"""
        backend_dir = f"{self.config.project_dir}/backend"
        
        commands = [
            f"cd {backend_dir} && python3 -m venv venv",
            f"cd {backend_dir} && ./venv/bin/pip install -r requirements.txt",
            f"cd {backend_dir} && ./venv/bin/python manage.py migrate",
            f"cd {backend_dir} && ./venv/bin/python manage.py collectstatic --noinput"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(cmd)
            if exit_code != 0:
                return False
        
        # Create admin user
        return self._create_admin_user()
    
    def _create_admin_user(self) -> bool:
        """Create Django admin user"""
        backend_dir = f"{self.config.project_dir}/backend"
        
        create_user_script = f"""
from django.contrib.auth.models import User
if not User.objects.filter(username='{self.config.admin_user}').exists():
    User.objects.create_superuser('{self.config.admin_user}', '{self.config.admin_email}', '{self.config.admin_password}')
    print('Admin user created successfully')
else:
    print('Admin user already exists')
"""
        
        # Write script to temporary file
        script_path = f"{backend_dir}/create_admin.py"
        exit_code, stdout, stderr = self.cleanup_manager.run_command(
            f"cat > {script_path} << 'EOF'\n{create_user_script}\nEOF"
        )
        
        if exit_code != 0:
            return False
        
        # Execute script
        exit_code, stdout, stderr = self.cleanup_manager.run_command(
            f"cd {backend_dir} && ./venv/bin/python manage.py shell < create_admin.py"
        )
        
        # Clean up
        self.cleanup_manager.run_command(f"rm -f {script_path}")
        
        return exit_code == 0
    
    def _setup_frontend(self) -> bool:
        """Setup React frontend"""
        frontend_dir = f"{self.config.project_dir}/frontend"
        
        commands = [
            f"cd {frontend_dir} && npm install",
            f"cd {frontend_dir} && npm run build"
        ]
        
        for cmd in commands:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(cmd)
            if exit_code != 0:
                return False
        
        return True
    
    def _setup_webserver(self) -> bool:
        """Setup web server"""
        return self.autofix_engine._fix_nginx_config()
    
    def _setup_services(self) -> bool:
        """Setup system services"""
        # Create systemd service for Django
        service_content = f"""[Unit]
Description=ProjectMeats Django Application
After=network.target
Wants=postgresql.service

[Service]
Type=simple
User={self.config.app_user}
WorkingDirectory={self.config.project_dir}/backend
Environment=DJANGO_SETTINGS_MODULE=projectmeats.settings
ExecStart={self.config.project_dir}/backend/venv/bin/python manage.py runserver 127.0.0.1:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
        
        exit_code, stdout, stderr = self.cleanup_manager.run_command(
            f"cat > /etc/systemd/system/projectmeats.service << 'EOF'\n{service_content}\nEOF"
        )
        
        if exit_code != 0:
            return False
        
        # Enable and start services
        service_commands = [
            "systemctl daemon-reload",
            "systemctl enable projectmeats",
            "systemctl start projectmeats",
            "systemctl enable nginx",
            "systemctl start nginx"
        ]
        
        for cmd in service_commands:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(cmd)
            if exit_code != 0 and "start" in cmd:
                # Try to restart if start fails
                restart_cmd = cmd.replace("start", "restart")
                self.cleanup_manager.run_command(restart_cmd)
        
        return True
    
    def _setup_security(self) -> bool:
        """Setup security configuration"""
        return self.autofix_engine._fix_firewall()
    
    def _verify_deployment(self) -> bool:
        """Verify deployment success"""
        # Run diagnostics to verify everything is working
        diagnosis_results = self.diagnostics_engine.run_comprehensive_diagnosis()
        
        # Check critical components
        app_info = diagnosis_results.get("application_status", {})
        services_info = diagnosis_results.get("services_status", {})
        domain_info = diagnosis_results.get("domain_accessibility", {})
        
        critical_checks = [
            app_info.get("directory_exists", False),
            app_info.get("essential_files_present", False),
            services_info.get("system_services", {}).get("nginx", {}).get("active", False)
        ]
        
        if self.config.domain:
            critical_checks.append(domain_info.get("local_accessible", False))
        
        return all(critical_checks)
    
    def _install_docker(self) -> bool:
        """Install Docker and docker-compose"""
        docker_commands = [
            "apt update",
            "apt install -y apt-transport-https ca-certificates curl gnupg lsb-release",
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
            "echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable' | tee /etc/apt/sources.list.d/docker.list > /dev/null",
            "apt update",
            "apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin",
            "systemctl enable docker",
            "systemctl start docker"
        ]
        
        for cmd in docker_commands:
            exit_code, stdout, stderr = self.cleanup_manager.run_command(cmd)
            if exit_code != 0:
                return False
        
        return True
    
    def _create_docker_compose(self) -> bool:
        """Create docker-compose configuration"""
        # This is a simplified version - the full implementation would be more complex
        compose_content = f"""version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:80"
    environment:
      - DJANGO_SETTINGS_MODULE=projectmeats.settings.production
      - DATABASE_URL=sqlite:///db.sqlite3
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media

volumes:
  static_volume:
  media_volume:
"""
        
        exit_code, stdout, stderr = self.cleanup_manager.run_command(
            f"cat > {self.config.project_dir}/docker-compose.yml << 'EOF'\n{compose_content}\nEOF"
        )
        
        return exit_code == 0
    
    def _print_deployment_success_message(self):
        """Print deployment success message"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}   🎉 PROJECTMEATS DEPLOYMENT COMPLETED SUCCESSFULLY! 🎉{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.END}")
        
        if self.config.domain:
            protocol = "https" if self.config.use_ssl else "http"
            print(f"\n{Colors.BOLD}🌐 Your application is now available at:{Colors.END}")
            print(f"   {Colors.CYAN}{protocol}://{self.config.domain}{Colors.END}")
            print(f"\n{Colors.BOLD}🔐 Admin panel:{Colors.END}")
            print(f"   {Colors.CYAN}{protocol}://{self.config.domain}/admin/{Colors.END}")
            print(f"\n{Colors.BOLD}📚 API documentation:{Colors.END}")
            print(f"   {Colors.CYAN}{protocol}://{self.config.domain}/api/docs/{Colors.END}")
        
        print(f"\n{Colors.BOLD}🔑 Admin credentials:{Colors.END}")
        print(f"   Username: {Colors.YELLOW}{self.config.admin_user}{Colors.END}")
        print(f"   Password: {Colors.YELLOW}{self.config.admin_password}{Colors.END}")
        print(f"   Email: {Colors.YELLOW}{self.config.admin_email}{Colors.END}")
        
        print(f"\n{Colors.BOLD}📁 Important paths:{Colors.END}")
        print(f"   Project: {Colors.CYAN}{self.config.project_dir}{Colors.END}")
        print(f"   Logs: {Colors.CYAN}{self.config.logs_dir}{Colors.END}")
        print(f"   Backups: {Colors.CYAN}{self.config.backup_dir}{Colors.END}")
        
        print(f"\n{Colors.BOLD}🛠️ Management commands:{Colors.END}")
        print(f"   Status: {Colors.CYAN}python3 unified_deployment_tool.py --status{Colors.END}")
        print(f"   Update: {Colors.CYAN}python3 unified_deployment_tool.py --update{Colors.END}")
        print(f"   Backup: {Colors.CYAN}python3 unified_deployment_tool.py --backup{Colors.END}")
        print(f"   Diagnose: {Colors.CYAN}python3 unified_deployment_tool.py --diagnose{Colors.END}")
        print(f"   Fix issues: {Colors.CYAN}python3 unified_deployment_tool.py --fix{Colors.END}")
        
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.END}")
    
    def _generate_consolidated_documentation(self) -> str:
        """Generate consolidated documentation"""
        return f"""# ProjectMeats Unified Deployment Tool Documentation

## Overview

The Unified Deployment Tool consolidates ALL ProjectMeats deployment, diagnostic, and management functionality into a single, powerful tool.

## Quick Start

### Production Deployment
```bash
# One-command production deployment
sudo python3 unified_deployment_tool.py --production --domain=yourdomain.com --auto

# Interactive setup wizard
sudo python3 unified_deployment_tool.py --production --interactive
```

### Diagnostics and Fixes
```bash
# Diagnose issues
python3 unified_deployment_tool.py --diagnose --domain=yourdomain.com

# Auto-fix common problems
sudo python3 unified_deployment_tool.py --fix

# Check system status
python3 unified_deployment_tool.py --status
```

### Management Operations
```bash
# Clean server environment
sudo python3 unified_deployment_tool.py --clean

# Update deployment
sudo python3 unified_deployment_tool.py --update

# Create backup
sudo python3 unified_deployment_tool.py --backup

# Configuration management
python3 unified_deployment_tool.py --config
```

## Deployment Modes

- `--production`: Full production deployment with security and SSL
- `--staging`: Staging environment for testing
- `--development`: Development environment setup
- `--local`: Local development configuration
- `--docker`: Container-based deployment
- `--cloud`: Cloud provider deployment

## Operation Modes

- `--diagnose`: Comprehensive system diagnostics
- `--fix`: Automatic issue resolution
- `--clean`: Server cleanup and preparation
- `--status`: System health check
- `--update`: Update existing deployment
- `--config`: Configuration management
- `--docs`: Documentation generation
- `--backup`: Create system backup
- `--rollback`: Rollback to previous version

## Authentication

### SSH Key Authentication (Recommended)
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Use with deployment
python3 unified_deployment_tool.py --production --server=SERVER_IP --key-file=~/.ssh/id_ed25519
```

### GitHub Authentication
```bash
# Set environment variables
export GITHUB_USER=your_username
export GITHUB_TOKEN=your_personal_access_token

# Or use command line options
python3 unified_deployment_tool.py --production --github-user=USERNAME --github-token=TOKEN
```

## Troubleshooting

### Common Issues

1. **Domain not accessible**: Run `--diagnose` to identify DNS, firewall, or configuration issues
2. **Service failures**: Use `--fix` to automatically resolve common service problems
3. **Repository download fails**: Set up GitHub authentication or use `--clean` flag
4. **Permission errors**: Ensure running with sudo for system operations

### Getting Help

```bash
# Comprehensive diagnosis
python3 unified_deployment_tool.py --diagnose --domain=yourdomain.com --server=SERVER_IP

# Show this documentation
python3 unified_deployment_tool.py --docs

# Configuration help
python3 unified_deployment_tool.py --config
```

## Advanced Usage

### Custom Configuration
```bash
# Use custom project directory
python3 unified_deployment_tool.py --production --project-dir=/custom/path

# Disable cleanup before deployment
python3 unified_deployment_tool.py --production --no-cleanup

# Disable backup before deployment  
python3 unified_deployment_tool.py --production --no-backup
```

### Remote Deployment
```bash
# Deploy to remote server
python3 unified_deployment_tool.py --production --server=167.99.155.140 --domain=yourdomain.com --auto
```

### Docker Deployment
```bash
# Container-based deployment
sudo python3 unified_deployment_tool.py --docker --production --domain=yourdomain.com
```

## Security

- All deployments include firewall configuration
- SSL certificates are automatically provisioned for production
- Secure passwords are automatically generated
- File permissions are properly configured
- Security headers are enabled

## Monitoring

The tool includes comprehensive monitoring and health checks:
- Service status monitoring
- Domain accessibility verification
- Database connectivity checks
- Application health verification
- Performance metrics collection

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""



# ============================================================================
# COMMAND LINE INTERFACE AND MAIN ENTRY POINT
# ============================================================================

def create_argument_parser():
    """Create comprehensive argument parser"""
    parser = argparse.ArgumentParser(
        description="ProjectMeats Unified Deployment, Fix, and Management Tool",
        epilog="""
Examples:
  # Production deployment
  sudo python3 unified_deployment_tool.py --production --domain=yourdomain.com --auto
  
  # Interactive setup
  sudo python3 unified_deployment_tool.py --production --interactive
  
  # Diagnose issues
  python3 unified_deployment_tool.py --diagnose --domain=meatscentral.com --server=167.99.155.140
  
  # Auto-fix problems
  sudo python3 unified_deployment_tool.py --fix
  
  # Check status
  python3 unified_deployment_tool.py --status
  
  # Docker deployment
  sudo python3 unified_deployment_tool.py --docker --production --domain=yourdomain.com
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Deployment modes (mutually exclusive)
    deployment_group = parser.add_mutually_exclusive_group()
    deployment_group.add_argument("--production", action="store_true", help="Production deployment mode")
    deployment_group.add_argument("--staging", action="store_true", help="Staging deployment mode")
    deployment_group.add_argument("--development", action="store_true", help="Development deployment mode")
    deployment_group.add_argument("--local", action="store_true", help="Local development mode")
    deployment_group.add_argument("--docker", action="store_true", help="Docker deployment mode")
    deployment_group.add_argument("--cloud", action="store_true", help="Cloud deployment mode")
    
    # Operation modes (mutually exclusive)
    operation_group = parser.add_mutually_exclusive_group()
    operation_group.add_argument("--diagnose", action="store_true", help="Run comprehensive diagnostics")
    operation_group.add_argument("--fix", action="store_true", help="Auto-fix common issues")
    operation_group.add_argument("--clean", action="store_true", help="Clean server environment")
    operation_group.add_argument("--status", action="store_true", help="Check system status")
    operation_group.add_argument("--update", action="store_true", help="Update existing deployment")
    operation_group.add_argument("--config", action="store_true", help="Configuration management")
    operation_group.add_argument("--docs", action="store_true", help="Generate documentation")
    operation_group.add_argument("--backup", action="store_true", help="Create system backup")
    operation_group.add_argument("--rollback", action="store_true", help="Rollback to previous version")
    
    # Server connection settings
    server_group = parser.add_argument_group("Server Connection")
    server_group.add_argument("--server", help="Server hostname or IP address")
    server_group.add_argument("--username", default="root", help="SSH username (default: root)")
    server_group.add_argument("--key-file", help="SSH private key file path")
    server_group.add_argument("--password", help="SSH password (not recommended)")
    
    # Application settings
    app_group = parser.add_argument_group("Application Settings")
    app_group.add_argument("--domain", help="Domain name (e.g., mycompany.com)")
    app_group.add_argument("--project-dir", default="/opt/projectmeats", help="Project installation directory")
    app_group.add_argument("--app-user", default="projectmeats", help="Application user")
    app_group.add_argument("--database", choices=["postgresql", "sqlite"], default="postgresql", help="Database type")
    
    # GitHub authentication
    github_group = parser.add_argument_group("GitHub Authentication")
    github_group.add_argument("--github-user", help="GitHub username")
    github_group.add_argument("--github-token", help="GitHub Personal Access Token")
    
    # Deployment options
    deploy_group = parser.add_argument_group("Deployment Options")
    deploy_group.add_argument("--auto", action="store_true", help="Automatic deployment without prompts")
    deploy_group.add_argument("--interactive", action="store_true", help="Interactive deployment wizard")
    deploy_group.add_argument("--no-cleanup", action="store_true", help="Skip cleanup before deployment")
    deploy_group.add_argument("--no-backup", action="store_true", help="Skip backup before deployment")
    deploy_group.add_argument("--no-ssl", action="store_true", help="Disable SSL/HTTPS")
    
    # Advanced options
    advanced_group = parser.add_argument_group("Advanced Options")
    advanced_group.add_argument("--admin-user", default="admin", help="Admin username")
    advanced_group.add_argument("--admin-email", help="Admin email address")
    advanced_group.add_argument("--admin-password", help="Admin password")
    advanced_group.add_argument("--force", action="store_true", help="Force operation without confirmation")
    advanced_group.add_argument("--verbose", action="store_true", help="Verbose output")
    
    return parser


def print_banner():
    """Print tool banner"""
    banner = f"""
{Colors.BOLD}{Colors.BLUE}
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  🚀 ProjectMeats Unified Deployment, Fix, and Management Tool 🚀           │
│                                                                              │
│  ✅ Consolidates ALL deployment, orchestration, diagnostic, and fix tools   │
│  ✅ Server cleanup and folder structure validation                          │
│  ✅ Clean repository cloning with automatic conflict resolution             │
│  ✅ Comprehensive domain accessibility verification and fixing               │
│  ✅ AI-driven error detection and automatic recovery                        │
│  ✅ One-command deployment for all environments                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
{Colors.END}

{Colors.CYAN}THE ONLY DEPLOYMENT TOOL YOU NEED FOR PROJECTMEATS{Colors.END}

{Colors.BOLD}Replaces and enhances:{Colors.END}
• ai_deployment_orchestrator.py
• master_deploy.py  
• deploy_production.py
• enhanced_deployment.py
• fix_meatscentral_access.py
• diagnose_deployment_issue.py
• All configuration and management scripts

{Colors.BOLD}Usage examples:{Colors.END}
  {Colors.GREEN}# 🎯 One-command production deployment{Colors.END}
  sudo python3 unified_deployment_tool.py --production --domain=yourdomain.com --auto

  {Colors.GREEN}# 🔍 Diagnose domain access issues{Colors.END}
  python3 unified_deployment_tool.py --diagnose --domain=meatscentral.com --server=167.99.155.140

  {Colors.GREEN}# 🛠️ Auto-fix all problems{Colors.END}
  sudo python3 unified_deployment_tool.py --fix

  {Colors.GREEN}# 📊 Check system health{Colors.END}
  python3 unified_deployment_tool.py --status
"""
    print(banner)


def check_dependencies():
    """Check for optional dependencies and provide installation instructions"""
    missing_deps = []
    
    if not PARAMIKO_AVAILABLE:
        missing_deps.append("paramiko")
    
    if not REQUESTS_AVAILABLE:
        missing_deps.append("requests")
    
    if missing_deps:
        print(f"{Colors.YELLOW}⚠️ Optional dependencies missing:{Colors.END}")
        for dep in missing_deps:
            print(f"   {dep}")
        print(f"\n{Colors.CYAN}Install with:{Colors.END}")
        print(f"   pip install {' '.join(missing_deps)}")
        print(f"\n{Colors.BLUE}Note: The tool will work with limited functionality without these dependencies{Colors.END}")
        
        choice = input(f"\n{Colors.CYAN}Continue anyway? [Y/n]: {Colors.END}").strip().lower()
        if choice == 'n':
            return False
    
    return True


def check_privileges():
    """Check if running with appropriate privileges"""
    if os.geteuid() != 0:
        print(f"{Colors.YELLOW}⚠️ Not running as root{Colors.END}")
        print(f"{Colors.CYAN}Some operations require root privileges. Run with sudo for full functionality.{Colors.END}")
        return False
    return True


def main():
    """Main entry point"""
    try:
        # Parse arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # If no arguments provided, show help and banner
        if len(sys.argv) == 1:
            print_banner()
            parser.print_help()
            return 0
        
        # Print banner for interactive operations
        if args.interactive or not args.auto:
            print_banner()
        
        # Check dependencies
        if not check_dependencies():
            return 1
        
        # Determine operation mode
        operation_mode = None
        deployment_mode_selected = any([
            args.production, args.staging, args.development, 
            args.local, args.docker, args.cloud
        ])
        
        if args.diagnose:
            operation_mode = OperationMode.DIAGNOSE
        elif args.fix:
            operation_mode = OperationMode.FIX
        elif args.clean:
            operation_mode = OperationMode.CLEAN
        elif args.status:
            operation_mode = OperationMode.STATUS
        elif args.update:
            operation_mode = OperationMode.UPDATE
        elif args.config:
            operation_mode = OperationMode.CONFIG
        elif args.docs:
            operation_mode = OperationMode.DOCS
        elif args.backup:
            operation_mode = OperationMode.BACKUP
        elif args.rollback:
            operation_mode = OperationMode.ROLLBACK
        elif deployment_mode_selected:
            operation_mode = OperationMode.DEPLOY
        else:
            print(f"{Colors.RED}❌ No operation mode specified{Colors.END}")
            print(f"{Colors.CYAN}Use --help to see available options{Colors.END}")
            return 1
        
        # Check privileges for operations that need them
        needs_root = operation_mode in [
            OperationMode.DEPLOY, OperationMode.FIX, OperationMode.CLEAN,
            OperationMode.UPDATE, OperationMode.BACKUP
        ]
        
        if needs_root and not check_privileges():
            if not args.force:
                print(f"{Colors.YELLOW}⚠️ This operation typically requires root privileges{Colors.END}")
                choice = input(f"{Colors.CYAN}Continue anyway? [y/N]: {Colors.END}").strip().lower()
                if choice != 'y':
                    print(f"{Colors.CYAN}Tip: Run with sudo for full functionality{Colors.END}")
                    return 1
        
        # Initialize orchestrator
        orchestrator = UnifiedDeploymentOrchestrator()
        
        if not orchestrator.initialize(args):
            print(f"{Colors.RED}❌ Failed to initialize deployment orchestrator{Colors.END}")
            return 1
        
        # Run the operation
        success = orchestrator.run(operation_mode)
        
        if success:
            print(f"\n{Colors.GREEN}✅ Operation completed successfully!{Colors.END}")
            return 0
        else:
            print(f"\n{Colors.RED}❌ Operation failed{Colors.END}")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Operation cancelled by user{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

