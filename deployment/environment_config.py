"""
Environment Configuration Management for ProjectMeats AI Deployment Orchestrator
================================================================================

This module provides consolidated environment variable handling, template management,
and secure configuration generation for production deployments.
"""

import os
import secrets
import string
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List


class EnvironmentConfigManager:
    """
    Centralized environment configuration management for ProjectMeats deployments.
    
    Handles:
    - Unified environment file generation
    - Secure credential generation
    - Template management
    - File permission handling
    - Configuration validation
    """
    
    def __init__(self, orchestrator=None):
        """Initialize with optional orchestrator reference for logging"""
        self.orchestrator = orchestrator
        self.template_dir = Path(__file__).parent / "templates"
        
        # Standard environment file locations
        self.env_locations = {
            "primary": "/etc/projectmeats/projectmeats.env",
            "backup": "/opt/projectmeats/backend/.env",
            "systemd": "/etc/projectmeats/projectmeats.env"  # Same as primary but explicit
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log message through orchestrator if available"""
        if self.orchestrator:
            self.orchestrator.log(message, level)
        else:
            print(f"[{level}] {message}")
    
    def generate_secure_credentials(self) -> Dict[str, str]:
        """
        Generate secure credentials for database and Django.
        
        Returns:
            Dictionary containing generated credentials
        """
        self.log("Generating secure credentials...", "INFO")
        
        # Generate Django secret key (50 chars, Django-compatible)
        secret_chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
        secret_key = ''.join(secrets.choice(secret_chars) for _ in range(50))
        
        # Generate database credentials (alphanumeric only to avoid SQL escaping issues)
        db_chars = string.ascii_letters + string.digits
        db_name = f"projectmeats_prod_{secrets.token_hex(4)}"
        db_user = f"pm_user_{secrets.token_hex(3)}"
        db_password = ''.join(secrets.choice(db_chars) for _ in range(20))
        
        return {
            "secret_key": secret_key,
            "db_name": db_name,
            "db_user": db_user,
            "db_password": db_password
        }
    
    def generate_ssl_settings(self, enable_ssl: bool = True) -> str:
        """Generate SSL configuration section"""
        if enable_ssl:
            return """# SSL/HTTPS Configuration
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
CSRF_COOKIE_SAMESITE=Strict"""
        else:
            return """# SSL disabled for development
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False"""
    
    def generate_email_settings(self, email_config: Dict[str, Any]) -> str:
        """Generate email configuration section"""
        if email_config.get("email_host"):
            return f"""# SMTP Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST={email_config.get("email_host", "")}
EMAIL_PORT={email_config.get("email_port", "587")}
EMAIL_USE_TLS={str(email_config.get("email_use_tls", True)).lower()}
EMAIL_HOST_USER={email_config.get("email_user", "")}
EMAIL_HOST_PASSWORD={email_config.get("email_password", "")}
DEFAULT_FROM_EMAIL=ProjectMeats <noreply@{email_config.get("domain", "localhost")}>"""
        else:
            return """# Email configuration (console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend"""
    
    def create_environment_file(self, config: Dict[str, Any]) -> str:
        """
        Create environment file content from configuration.
        
        Args:
            config: Configuration dictionary with all settings
            
        Returns:
            Complete environment file content as string
        """
        self.log("Generating environment file content...", "INFO")
        
        # Load template
        template_path = self.template_dir / "environment.template"
        if not template_path.exists():
            raise FileNotFoundError(f"Environment template not found: {template_path}")
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Generate dynamic sections
        ssl_settings = self.generate_ssl_settings(config.get("enable_ssl", True))
        email_settings = self.generate_email_settings(config)
        
        # Prepare template variables
        template_vars = {
            "debug": str(config.get("debug", False)).lower(),
            "secret_key": config.get("secret_key", ""),
            "allowed_hosts": config.get("allowed_hosts", "localhost,127.0.0.1"),
            "db_user": config.get("db_user", ""),
            "db_password": config.get("db_password", ""),
            "db_host": config.get("db_host", "localhost"),
            "db_port": config.get("db_port", "5432"),
            "db_name": config.get("db_name", ""),
            "ssl_settings": ssl_settings,
            "cors_origins": config.get("cors_origins", ""),
            "csrf_trusted_origins": config.get("cors_origins", ""),
            "static_root": config.get("static_root", "/opt/projectmeats/backend/staticfiles"),
            "media_root": config.get("media_root", "/opt/projectmeats/media"),
            "email_settings": email_settings,
            "log_dir": config.get("log_dir", "/opt/projectmeats/logs"),
            "company_name": config.get("company_name", "ProjectMeats"),
            "company_email": config.get("company_email", ""),
            "company_phone": config.get("company_phone", ""),
            "company_address": config.get("company_address", ""),
            "backup_dir": config.get("backup_dir", "/opt/projectmeats/backups"),
            "deployment_timestamp": datetime.now().isoformat(),
            "deployment_version": "1.0.0"
        }
        
        # Replace template variables
        try:
            env_content = template_content.format(**template_vars)
            self.log("✓ Environment file content generated successfully", "SUCCESS")
            return env_content
        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")
    
    def validate_configuration(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration completeness and security.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Required fields
        required_fields = ["secret_key", "db_name", "db_user", "db_password"]
        for field in required_fields:
            if not config.get(field):
                issues.append(f"Missing required field: {field}")
        
        # Security validation
        secret_key = config.get("secret_key", "")
        if len(secret_key) < 50:
            issues.append("Secret key is too short (minimum 50 characters)")
        
        if "django-insecure-" in secret_key:
            issues.append("Using development secret key in production")
        
        # Database password strength
        db_password = config.get("db_password", "")
        if len(db_password) < 16:
            issues.append("Database password is too short (minimum 16 characters)")
        
        # Domain validation
        if not config.get("domain") and config.get("enable_ssl", True):
            issues.append("Domain is required when SSL is enabled")
        
        return len(issues) == 0, issues
    
    def save_admin_credentials(self, config: Dict[str, Any], execute_command_func) -> bool:
        """
        Save admin credentials securely on the server.
        
        Args:
            config: Configuration dictionary
            execute_command_func: Function to execute commands on server
            
        Returns:
            Success status
        """
        try:
            self.log("Saving admin credentials securely...", "INFO")
            
            admin_info = {
                "deployment_time": datetime.now().isoformat(),
                "database_name": config.get("db_name"),
                "database_user": config.get("db_user"),
                "database_password": config.get("db_password"),
                "database_host": config.get("db_host", "localhost"),
                "database_port": config.get("db_port", "5432"),
                "domain": config.get("domain", ""),
                "company_name": config.get("company_name", "ProjectMeats")
            }
            
            # Create admin directory and credentials file
            admin_setup_cmd = f"""
            mkdir -p /opt/projectmeats/admin
            cat > /opt/projectmeats/admin/database_credentials.json << 'EOF'
{{
    "deployment_time": "{admin_info['deployment_time']}",
    "database": {{
        "name": "{admin_info['database_name']}",
        "user": "{admin_info['database_user']}",
        "password": "{admin_info['database_password']}",
        "host": "{admin_info['database_host']}",
        "port": "{admin_info['database_port']}"
    }},
    "application": {{
        "domain": "{admin_info['domain']}",
        "company_name": "{admin_info['company_name']}"
    }}
}}
EOF
            
            # Set secure permissions (readable only by root)
            chmod 600 /opt/projectmeats/admin/database_credentials.json
            chown root:root /opt/projectmeats/admin/database_credentials.json
            """
            
            exit_code, stdout, stderr = execute_command_func(admin_setup_cmd)
            if exit_code == 0:
                self.log("✓ Admin credentials saved securely", "SUCCESS")
                return True
            else:
                self.log(f"Failed to save admin credentials: {stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error saving admin credentials: {e}", "ERROR")
            return False


def create_unified_environment_manager():
    """Factory function to create environment manager"""
    return EnvironmentConfigManager()