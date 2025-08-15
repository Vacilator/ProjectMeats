#!/usr/bin/env python3
"""
ProjectMeats Interactive Production Deployment Script
====================================================

This script provides a guided, interactive setup for deploying ProjectMeats to production.
It includes server provider recommendations, automated configuration, and one-command deployment.

Usage:
    python deploy_production.py        # Interactive production setup
    python deploy_production.py --help # Show help and options

Features:
- Interactive console prompts for all configuration values
- Server provider recommendations with setup instructions
- Automated configuration file generation
- One-command deployment process
- Security best practices implementation
- Comprehensive production environment setup
"""

import os
import sys
import json
import shutil
import getpass
import secrets
import subprocess
import platform
import time
from pathlib import Path
from urllib.parse import urlparse
import re


class Colors:
    """ANSI color codes for terminal output"""
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


class ProductionDeployment:
    """Interactive production deployment setup for ProjectMeats"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.config = {}
        self.is_local_setup = False
        
    def log(self, message, level="INFO", color=None):
        """Enhanced logging with colors and levels"""
        color_map = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "STEP": Colors.PURPLE,
            "INPUT": Colors.CYAN
        }
        
        if color is None:
            color = color_map.get(level, Colors.WHITE)
        
        print(f"{color}[{level}]{Colors.END} {message}")
    
    def input_with_default(self, prompt, default="", required=True, mask=False):
        """Get user input with default value"""
        if default:
            display_prompt = f"{prompt} [{default}]: "
        else:
            display_prompt = f"{prompt}: "
        
        self.log(display_prompt, "INPUT", Colors.CYAN)
        
        if mask:
            value = getpass.getpass(">>> ")
        else:
            value = input(">>> ").strip()
        
        if not value and default:
            return default
        elif not value and required:
            self.log("This field is required. Please enter a value.", "ERROR")
            return self.input_with_default(prompt, default, required, mask)
        
        return value or default
    
    def confirm(self, prompt, default=True):
        """Get yes/no confirmation from user"""
        default_text = "Y/n" if default else "y/N"
        response = self.input_with_default(f"{prompt} ({default_text})", 
                                         "y" if default else "n", False)
        return response.lower() in ['y', 'yes', 'true'] if response else default
    
    def print_banner(self):
        """Print welcome banner"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}  ProjectMeats Production Deployment Setup{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}  Interactive Configuration & Deployment Guide{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
        
        print(f"{Colors.CYAN}Welcome to the ProjectMeats production deployment wizard!{Colors.END}")
        print(f"{Colors.WHITE}This script will guide you through setting up a production environment.{Colors.END}\n")
    
    def show_server_recommendations(self):
        """Display server provider recommendations"""
        print(f"\n{Colors.BOLD}🌟 Recommended Server Providers{Colors.END}")
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        
        providers = [
            {
                "name": "DigitalOcean",
                "cost": "$20-40/month",
                "specs": "2-4 vCPU, 4-8GB RAM, 50-100GB SSD",
                "pros": "Simple setup, excellent documentation, predictable pricing",
                "setup_url": "https://www.digitalocean.com/products/droplets/",
                "best_for": "Small to medium businesses, easy setup"
            },
            {
                "name": "Linode (Akamai)",
                "cost": "$18-36/month", 
                "specs": "2-4 vCPU, 4-8GB RAM, 50-100GB SSD",
                "pros": "Great performance, competitive pricing, excellent support",
                "setup_url": "https://www.linode.com/products/shared/",
                "best_for": "Performance-focused deployments"
            },
            {
                "name": "Vultr",
                "cost": "$20-40/month",
                "specs": "2-4 vCPU, 4-8GB RAM, 50-100GB SSD", 
                "pros": "Fast SSDs, global locations, good value",
                "setup_url": "https://www.vultr.com/products/cloud-compute/",
                "best_for": "Global reach, fast deployment"
            },
            {
                "name": "AWS Lightsail",
                "cost": "$20-40/month",
                "specs": "2-4 vCPU, 4-8GB RAM, 50-100GB SSD",
                "pros": "AWS ecosystem, predictable pricing, easy scaling",
                "setup_url": "https://aws.amazon.com/lightsail/",
                "best_for": "AWS integration, future scaling"
            }
        ]
        
        for i, provider in enumerate(providers, 1):
            print(f"\n{Colors.GREEN}{i}. {provider['name']}{Colors.END}")
            print(f"   💰 Cost: {Colors.YELLOW}{provider['cost']}{Colors.END}")
            print(f"   ⚙️  Specs: {provider['specs']}")
            print(f"   ✅ Pros: {provider['pros']}")
            print(f"   🌐 Setup: {Colors.CYAN}{provider['setup_url']}{Colors.END}")
            print(f"   🎯 Best for: {provider['best_for']}")
        
        print(f"\n{Colors.BOLD}💡 Server Setup Requirements:{Colors.END}")
        print(f"   • Ubuntu 20.04+ LTS (recommended)")
        print(f"   • Root or sudo access")
        print(f"   • Domain name pointed to server IP")
        print(f"   • SSH key authentication (recommended)")
        
        print(f"\n{Colors.BOLD}📋 Quick Server Setup Steps:{Colors.END}")
        print(f"   1. Create server instance with Ubuntu 20.04+")
        print(f"   2. Point your domain DNS to server IP")
        print(f"   3. SSH into server as root or with sudo user")
        print(f"   4. Run this deployment script on the server")
        
        print(f"\n{Colors.BLUE}{'='*50}{Colors.END}")
    
    def get_deployment_type(self):
        """Determine deployment type"""
        print(f"\n{Colors.BOLD}📍 Deployment Location{Colors.END}")
        print(f"Where are you setting up ProjectMeats?")
        print(f"1. {Colors.GREEN}Production Server{Colors.END} - Cloud hosting (DigitalOcean, AWS, etc.)")
        print(f"2. {Colors.YELLOW}Local Server{Colors.END} - On-premises or local network")
        print(f"3. {Colors.CYAN}Development Testing{Colors.END} - Local production-like setup")
        
        choice = self.input_with_default("Select deployment type (1-3)", "1")
        
        if choice == "1":
            self.is_local_setup = False
            self.show_server_recommendations()
            return "production"
        elif choice == "2":
            self.is_local_setup = True
            return "local"
        elif choice == "3":
            self.is_local_setup = True
            return "development"
        else:
            self.log("Invalid choice. Please select 1, 2, or 3.", "ERROR")
            return self.get_deployment_type()
    
    def get_domain_configuration(self):
        """Get domain and SSL configuration"""
        print(f"\n{Colors.BOLD}🌐 Domain Configuration{Colors.END}")
        
        if self.is_local_setup:
            self.config['domain'] = self.input_with_default(
                "Domain or IP address", "localhost"
            )
            self.config['use_ssl'] = self.confirm("Enable SSL/HTTPS", False)
        else:
            self.config['domain'] = self.input_with_default(
                "Your domain name (e.g., mycompany.com)", required=True
            )
            self.config['use_ssl'] = self.confirm("Enable SSL/HTTPS with Let's Encrypt", True)
        
        if self.config['domain'] != 'localhost':
            self.config['www_redirect'] = self.confirm(
                f"Redirect www.{self.config['domain']} to {self.config['domain']}", True
            )
        else:
            self.config['www_redirect'] = False
    
    def get_database_configuration(self):
        """Get database configuration"""
        print(f"\n{Colors.BOLD}🗄️  Database Configuration{Colors.END}")
        
        if self.is_local_setup:
            print(f"1. {Colors.GREEN}SQLite{Colors.END} - Simple file-based database (recommended for local)")
            print(f"2. {Colors.YELLOW}PostgreSQL{Colors.END} - Full-featured database server")
            db_choice = self.input_with_default("Select database type (1-2)", "1")
        else:
            print(f"1. {Colors.GREEN}PostgreSQL{Colors.END} - Recommended for production")
            print(f"2. {Colors.YELLOW}SQLite{Colors.END} - Simple but not recommended for production")
            db_choice = self.input_with_default("Select database type (1-2)", "1")
        
        if db_choice == "1" and not self.is_local_setup:
            # PostgreSQL for production
            self.config['database_type'] = 'postgresql'
            self.config['db_name'] = self.input_with_default("Database name", "projectmeats_prod")
            self.config['db_user'] = self.input_with_default("Database username", "projectmeats_user")
            self.config['db_password'] = self.input_with_default(
                "Database password", self.generate_password(), mask=True
            )
        elif db_choice == "2" or self.is_local_setup:
            # SQLite
            self.config['database_type'] = 'sqlite'
        else:
            # PostgreSQL for local
            self.config['database_type'] = 'postgresql'
            self.config['db_name'] = self.input_with_default("Database name", "projectmeats_local")
            self.config['db_user'] = self.input_with_default("Database username", "projectmeats")
            self.config['db_password'] = self.input_with_default(
                "Database password", "password", mask=True
            )
    
    def get_admin_configuration(self):
        """Get admin user configuration"""
        print(f"\n{Colors.BOLD}👤 Admin User Configuration{Colors.END}")
        
        self.config['admin_username'] = self.input_with_default("Admin username", "admin")
        self.config['admin_email'] = self.input_with_default(
            "Admin email", f"admin@{self.config.get('domain', 'localhost')}"
        )
        self.config['admin_password'] = self.input_with_default(
            "Admin password", "WATERMELON1219", mask=True
        )
    
    def get_email_configuration(self):
        """Get email configuration"""
        print(f"\n{Colors.BOLD}📧 Email Configuration{Colors.END}")
        
        use_email = self.confirm("Configure email sending (SMTP)", not self.is_local_setup)
        
        if use_email:
            self.config['email_backend'] = 'smtp'
            self.config['email_host'] = self.input_with_default("SMTP host", "smtp.gmail.com")
            self.config['email_port'] = self.input_with_default("SMTP port", "587")
            self.config['email_use_tls'] = self.confirm("Use TLS", True)
            self.config['email_user'] = self.input_with_default("Email username", required=True)
            self.config['email_password'] = self.input_with_default(
                "Email password", mask=True, required=True
            )
            self.config['from_email'] = self.input_with_default(
                "From email address", self.config['email_user']
            )
        else:
            self.config['email_backend'] = 'console'
    
    def get_security_configuration(self):
        """Get security configuration"""
        print(f"\n{Colors.BOLD}🔒 Security Configuration{Colors.END}")
        
        self.config['secret_key'] = self.generate_secret_key()
        self.log(f"Generated secure Django secret key", "SUCCESS")
        
        if not self.is_local_setup:
            self.config['debug'] = False
            self.config['secure_settings'] = True
        else:
            self.config['debug'] = self.confirm("Enable debug mode", True)
            self.config['secure_settings'] = self.confirm("Enable security headers", False)
    
    def get_advanced_configuration(self):
        """Get advanced configuration options"""
        print(f"\n{Colors.BOLD}⚙️  Advanced Configuration{Colors.END}")
        
        configure_advanced = self.confirm("Configure advanced options", False)
        
        if configure_advanced:
            self.config['time_zone'] = self.input_with_default("Time zone", "America/New_York")
            self.config['language'] = self.input_with_default("Language code", "en-us")
            self.config['company_name'] = self.input_with_default("Company name", "ProjectMeats")
            
            # Redis configuration
            use_redis = self.confirm("Configure Redis for caching", not self.is_local_setup)
            if use_redis:
                self.config['redis_url'] = self.input_with_default(
                    "Redis URL", "redis://localhost:6379/1"
                )
            
            # File storage
            self.config['media_root'] = self.input_with_default(
                "Media files directory", "/home/projectmeats/uploads" if not self.is_local_setup else "./uploads"
            )
        else:
            # Use defaults
            self.config['time_zone'] = 'America/New_York'
            self.config['language'] = 'en-us'
            self.config['company_name'] = 'ProjectMeats'
            self.config['media_root'] = "/home/projectmeats/uploads" if not self.is_local_setup else "./uploads"
    
    def generate_secret_key(self):
        """Generate a secure Django secret key"""
        # Use only alphanumeric and safe special characters to avoid bash parsing issues
        return ''.join(secrets.choice(
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#%^&*-_=+'
        ) for _ in range(50))
    
    def generate_password(self, length=16):
        """Generate a secure password"""
        return ''.join(secrets.choice(
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
        ) for _ in range(length))
    
    def display_configuration_summary(self):
        """Display configuration summary for review"""
        print(f"\n{Colors.BOLD}📋 Configuration Summary{Colors.END}")
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        
        print(f"{Colors.CYAN}Domain:{Colors.END} {self.config['domain']}")
        print(f"{Colors.CYAN}SSL/HTTPS:{Colors.END} {'Enabled' if self.config.get('use_ssl') else 'Disabled'}")
        print(f"{Colors.CYAN}Database:{Colors.END} {self.config['database_type'].upper()}")
        
        if self.config['database_type'] == 'postgresql':
            print(f"{Colors.CYAN}DB Name:{Colors.END} {self.config['db_name']}")
            print(f"{Colors.CYAN}DB User:{Colors.END} {self.config['db_user']}")
        
        print(f"{Colors.CYAN}Admin User:{Colors.END} {self.config['admin_username']}")
        print(f"{Colors.CYAN}Admin Email:{Colors.END} {self.config['admin_email']}")
        print(f"{Colors.CYAN}Email Backend:{Colors.END} {self.config['email_backend'].upper()}")
        print(f"{Colors.CYAN}Debug Mode:{Colors.END} {'Enabled' if self.config.get('debug') else 'Disabled'}")
        print(f"{Colors.CYAN}Company:{Colors.END} {self.config.get('company_name', 'ProjectMeats')}")
        
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        
        if not self.confirm("Is this configuration correct", True):
            return False
        
        return True
    
    def create_environment_file(self):
        """Create the production environment file"""
        self.log("Creating production environment file...", "INFO")
        
        try:
            env_content = self.generate_env_content()
            env_file = self.backend_dir / ".env"
            
            # Ensure backend directory exists
            self.backend_dir.mkdir(exist_ok=True)
            
            # Backup existing .env if it exists
            if env_file.exists():
                backup_file = self.backend_dir / ".env.backup"
                shutil.copy2(env_file, backup_file)
                self.log(f"Backed up existing .env to .env.backup", "WARNING")
            
            # Write new environment file
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            # Verify file was created
            if env_file.exists():
                self.log("✓ Environment file created successfully", "SUCCESS")
            else:
                self.log("❌ Failed to create environment file", "ERROR")
                return False
            
            # Create production config backup
            config_backup = self.project_root / "production_config.json"
            with open(config_backup, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            
            # Verify config backup was created
            if config_backup.exists():
                self.log(f"✓ Configuration saved to production_config.json", "SUCCESS")
            else:
                self.log("❌ Failed to create production_config.json", "ERROR")
                return False
                
            return True
            
        except Exception as e:
            self.log(f"❌ Error creating environment file: {e}", "ERROR")
            return False
    
    def generate_env_content(self):
        """Generate environment file content"""
        content = [
            "# ProjectMeats Production Environment Configuration",
            "# Generated by deploy_production.py",
            f"# Generated on: {__import__('datetime').datetime.now().isoformat()}",
            "",
            "# ==========================================",
            "# DJANGO CORE SETTINGS", 
            "# ==========================================",
            "",
            f"DEBUG={str(self.config.get('debug', False))}",
            f"SECRET_KEY={self.config['secret_key']}",
        ]
        
        # Allowed hosts
        allowed_hosts = [self.config['domain']]
        if self.config.get('www_redirect') and self.config['domain'] != 'localhost':
            allowed_hosts.append(f"www.{self.config['domain']}")
        if self.config['domain'] != 'localhost':
            allowed_hosts.append('127.0.0.1')
        
        content.append(f"ALLOWED_HOSTS={','.join(allowed_hosts)}")
        content.extend([
            "",
            "# ==========================================",
            "# DATABASE CONFIGURATION",
            "# ==========================================",
            ""
        ])
        
        # Database configuration
        if self.config['database_type'] == 'postgresql':
            db_url = f"postgresql://{self.config['db_user']}:{self.config['db_password']}@localhost:5432/{self.config['db_name']}"
            content.append(f"DATABASE_URL={db_url}")
        else:
            content.append("DATABASE_URL=sqlite:///db.sqlite3")
        
        # Security settings
        if self.config.get('secure_settings'):
            content.extend([
                "",
                "# ==========================================",
                "# SECURITY SETTINGS",
                "# ==========================================",
                "",
                f"SECURE_SSL_REDIRECT={self.config.get('use_ssl', False)}",
                "SECURE_HSTS_SECONDS=31536000" if self.config.get('use_ssl') else "SECURE_HSTS_SECONDS=0",
                f"SECURE_HSTS_INCLUDE_SUBDOMAINS={self.config.get('use_ssl', False)}",
                f"SECURE_HSTS_PRELOAD={self.config.get('use_ssl', False)}",
                "SECURE_CONTENT_TYPE_NOSNIFF=True",
                "SECURE_BROWSER_XSS_FILTER=True",
                f"SESSION_COOKIE_SECURE={self.config.get('use_ssl', False)}",
                f"CSRF_COOKIE_SECURE={self.config.get('use_ssl', False)}",
            ])
        
        # CORS settings
        cors_origins = [f"http{'s' if self.config.get('use_ssl') else ''}://{self.config['domain']}"]
        if self.config.get('www_redirect'):
            cors_origins.append(f"http{'s' if self.config.get('use_ssl') else ''}://www.{self.config['domain']}")
        
        content.extend([
            "",
            "# ==========================================",
            "# CORS CONFIGURATION", 
            "# ==========================================",
            "",
            f"CORS_ALLOWED_ORIGINS={','.join(cors_origins)}",
        ])
        
        # Email configuration
        content.extend([
            "",
            "# ==========================================",
            "# EMAIL CONFIGURATION",
            "# ==========================================",
            ""
        ])
        
        if self.config['email_backend'] == 'smtp':
            content.extend([
                "EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend",
                f"EMAIL_HOST={self.config['email_host']}",
                f"EMAIL_PORT={self.config['email_port']}",
                f"EMAIL_USE_TLS={self.config['email_use_tls']}",
                f"EMAIL_HOST_USER={self.config['email_user']}",
                f"EMAIL_HOST_PASSWORD={self.config['email_password']}",
                f"DEFAULT_FROM_EMAIL={self.config['from_email']}",
            ])
        else:
            content.append("EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend")
        
        # File storage
        content.extend([
            "",
            "# ==========================================",
            "# FILE STORAGE",
            "# ==========================================",
            "",
            f"MEDIA_ROOT={self.config['media_root']}",
            f"STATIC_ROOT={self.backend_dir}/staticfiles" if self.is_local_setup else "/home/projectmeats/app/backend/staticfiles",
        ])
        
        # Redis cache (if configured)
        if 'redis_url' in self.config:
            content.extend([
                "",
                "# ==========================================",
                "# CACHE CONFIGURATION",
                "# ==========================================",
                "",
                f"CACHE_URL={self.config['redis_url']}",
            ])
        
        # Business configuration
        content.extend([
            "",
            "# ==========================================",
            "# BUSINESS CONFIGURATION",
            "# ==========================================",
            "",
            f"COMPANY_NAME={self.config.get('company_name', 'ProjectMeats')}",
            f"TIME_ZONE={self.config.get('time_zone', 'America/New_York')}",
            f"LANGUAGE_CODE={self.config.get('language', 'en-us')}",
        ])
        
        return '\n'.join(content) + '\n'
    
    def create_frontend_env(self):
        """Create frontend environment file"""
        self.log("Creating frontend environment file...", "INFO")
        
        try:
            protocol = 'https' if self.config.get('use_ssl') else 'http'
            api_url = f"{protocol}://{self.config['domain']}/api/v1"
            
            env_content = [
                "# ProjectMeats Frontend Production Configuration",
                f"# Generated on: {__import__('datetime').datetime.now().isoformat()}",
                "",
                f"REACT_APP_API_BASE_URL={api_url}",
                "REACT_APP_ENVIRONMENT=production",
                f"REACT_APP_COMPANY_NAME={self.config.get('company_name', 'ProjectMeats')}",
            ]
            
            # Ensure frontend directory exists
            self.frontend_dir.mkdir(exist_ok=True)
            
            frontend_env = self.frontend_dir / ".env.production"
            with open(frontend_env, 'w', encoding='utf-8') as f:
                f.write('\n'.join(env_content) + '\n')
            
            # Verify file was created
            if frontend_env.exists():
                self.log("✓ Frontend environment file created", "SUCCESS")
                return True
            else:
                self.log("❌ Failed to create frontend environment file", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error creating frontend environment file: {e}", "ERROR")
            return False
    
    def create_deployment_scripts(self):
        """Create deployment and management scripts"""
        self.log("Creating deployment scripts...", "INFO")
        
        try:
            # Create deployment script
            deploy_script = self.create_server_deployment_script()
            deploy_file = self.project_root / "deploy_server.sh"
            
            with open(deploy_file, 'w', encoding='utf-8') as f:
                f.write(deploy_script)
            
            os.chmod(deploy_file, 0o755)
            
            # Verify deployment script was created
            if not deploy_file.exists():
                self.log("❌ Failed to create deploy_server.sh", "ERROR")
                return False
            
            # Create management scripts
            if not self.create_management_scripts():
                self.log("❌ Failed to create management scripts", "ERROR")
                return False
            
            self.log("✓ Deployment scripts created", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Error creating deployment scripts: {e}", "ERROR")
            return False
    
    def create_server_deployment_script(self):
        """Generate server deployment script"""
        domain = self.config['domain']
        use_ssl = self.config.get('use_ssl', False)
        db_type = self.config['database_type']
        
        script = f"""#!/bin/bash
# ProjectMeats Production Server Deployment Script
# Generated by deploy_production.py

set -e  # Exit on any error

echo "🚀 Starting ProjectMeats production deployment..."

# Color codes for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

log_info() {{
    echo -e "${{BLUE}}[INFO]${{NC}} $1"
}}

log_success() {{
    echo -e "${{GREEN}}[SUCCESS]${{NC}} $1"
}}

log_warning() {{
    echo -e "${{YELLOW}}[WARNING]${{NC}} $1"
}}

log_error() {{
    echo -e "${{RED}}[ERROR]${{NC}} $1"
}}

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    log_info "Running as root user"
elif sudo -n true 2>/dev/null; then
    log_info "Running with sudo privileges"
else
    log_error "This script requires root privileges or sudo access"
    exit 1
fi

log_info "Deployment configuration:"
log_info "  Domain: {domain}"
log_info "  SSL: {'Enabled' if use_ssl else 'Disabled'}"
log_info "  Database: {db_type.upper()}"

# Update system packages
log_info "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
log_info "Installing system dependencies..."
apt install -y python3 python3-pip python3-venv nodejs npm nginx git curl ufw fail2ban

# Install Node.js 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt install -y nodejs

"""

        if db_type == 'postgresql':
            script += f"""
# Install and configure PostgreSQL
log_info "Installing PostgreSQL..."
apt install -y postgresql postgresql-contrib

# Configure PostgreSQL
log_info "Configuring PostgreSQL database..."
sudo -u postgres createdb {self.config['db_name']} || true
sudo -u postgres createuser {self.config['db_user']} || true
sudo -u postgres psql << EOF
ALTER USER {self.config['db_user']} PASSWORD '{self.config['db_password']}';
GRANT ALL PRIVILEGES ON DATABASE {self.config['db_name']} TO {self.config['db_user']};
ALTER USER {self.config['db_user']} CREATEDB;
\\q
EOF

log_success "PostgreSQL configured"
"""

        script += f"""
# Create application user
log_info "Creating application user..."
useradd -m -s /bin/bash projectmeats || true
usermod -aG sudo projectmeats || true

# Create application directories
log_info "Creating application directories..."
mkdir -p /home/projectmeats/{{app,logs,backups,uploads}}
chown -R projectmeats:projectmeats /home/projectmeats/

# Clone or update application
log_info "Setting up application code..."
if [ ! -d "/home/projectmeats/app" ]; then
    # Try multiple git clone methods with authentication
    clone_success=false
    
    # Method 1: Try PAT authentication if credentials are available
    if [ -n "\\$GITHUB_USER" ] && [ -n "\\$GITHUB_TOKEN" ]; then
        log_info "Attempting git clone with Personal Access Token..."
        if sudo -u projectmeats git clone "https://\\$GITHUB_USER:\\$GITHUB_TOKEN@github.com/Vacilator/ProjectMeats.git" /home/projectmeats/app 2>/dev/null; then
            log_success "Successfully cloned with PAT authentication"
            clone_success=true
        else
            log_warning "PAT authentication failed, trying other methods..."
        fi
    fi
    
    # Method 2: Try public access
    if [ "\\$clone_success" = false ]; then
        log_info "Attempting public git clone..."
        if sudo -u projectmeats git clone https://github.com/Vacilator/ProjectMeats.git /home/projectmeats/app 2>/dev/null; then
            log_success "Successfully cloned with public access"
            clone_success=true
        else
            log_warning "Public git clone failed"
        fi
    fi
    
    # Method 3: Try SSH if available
    if [ "\\$clone_success" = false ] && sudo -u projectmeats ssh -T git@github.com 2>/dev/null; then
        log_info "Attempting SSH git clone..."
        if sudo -u projectmeats git clone git@github.com:Vacilator/ProjectMeats.git /home/projectmeats/app 2>/dev/null; then
            log_success "Successfully cloned with SSH"
            clone_success=true
        else
            log_warning "SSH git clone failed"
        fi
    fi
    
    # If all methods failed, show detailed error message
    if [ "\\$clone_success" = false ]; then
        log_error "All git clone methods failed due to authentication issues."
        echo ""
        echo "🔒 GitHub Authentication Required"
        echo "================================"
        echo "GitHub has deprecated password authentication for git operations."
        echo ""
        echo "Solutions:"
        echo ""
        echo "1. 🔑 Use Personal Access Token (Recommended):"
        echo "   Set environment variables before running this script:"
        echo "   export GITHUB_USER=your_username"
        echo "   export GITHUB_TOKEN=your_personal_access_token"
        echo "   Then re-run this deployment script"
        echo ""
        echo "2. 🌐 Use the no-authentication deployment script:"
        echo "   curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash"
        echo ""
        echo "3. 🗝️  Setup SSH keys:"
        echo "   - Generate: ssh-keygen -t ed25519 -C 'your_email@example.com'"
        echo "   - Add public key to GitHub → Settings → SSH and GPG keys"
        echo "   - Test: ssh -T git@github.com"
        echo "   - Then re-run this script"
        echo ""
        echo "4. 📦 Manual transfer:"
        echo "   - Download on a machine with GitHub access:"
        echo "     git clone https://github.com/Vacilator/ProjectMeats.git"
        echo "   - Transfer to this server:"
        echo "     scp -r ProjectMeats/ user@SERVER_IP:/home/projectmeats/app"
        echo ""
        echo "For detailed instructions, see:"
        echo "https://github.com/Vacilator/ProjectMeats/blob/main/docs/deployment_authentication_guide.md"
        echo ""
        exit 1
    fi
else
    cd /home/projectmeats/app
    
    # Try to update existing installation
    update_success=false
    
    # Try PAT authentication for updates
    if [ -n "\\$GITHUB_USER" ] && [ -n "\\$GITHUB_TOKEN" ]; then
        log_info "Updating with PAT authentication..."
        if sudo -u projectmeats git pull origin main 2>/dev/null; then
            log_success "Successfully updated with PAT authentication"
            update_success=true
        fi
    fi
    
    # Try public or SSH for updates
    if [ "\\$update_success" = false ]; then
        log_info "Attempting to update existing installation..."
        if sudo -u projectmeats git pull origin main 2>/dev/null; then
            log_success "Successfully updated"
            update_success=true
        else
            log_warning "Git pull failed, continuing with existing code..."
            echo "Note: Unable to update code from GitHub. Using existing installation."
            echo "If you need the latest version, see the authentication guide:"
            echo "https://github.com/Vacilator/ProjectMeats/blob/main/docs/deployment_authentication_guide.md"
        fi
    fi
fi

# Copy environment configuration
log_info "Copying environment configuration..."
cp backend/.env /home/projectmeats/app/backend/.env
cp frontend/.env.production /home/projectmeats/app/frontend/.env.production
chown projectmeats:projectmeats /home/projectmeats/app/backend/.env
chown projectmeats:projectmeats /home/projectmeats/app/frontend/.env.production

# Setup backend
log_info "Setting up Django backend..."
cd /home/projectmeats/app/backend
sudo -u projectmeats python3 -m venv venv
sudo -u projectmeats ./venv/bin/pip install -r requirements.txt
sudo -u projectmeats ./venv/bin/pip install gunicorn

# Run migrations and setup
sudo -u projectmeats ./venv/bin/python manage.py migrate
sudo -u projectmeats ./venv/bin/python manage.py collectstatic --noinput

# Create admin user
log_info "Creating admin user..."
sudo -u projectmeats ./venv/bin/python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
User.objects.filter(username='{self.config['admin_username']}').exists() or User.objects.create_superuser('{self.config['admin_username']}', '{self.config['admin_email']}', '{self.config['admin_password']}')
"

# Setup frontend
log_info "Setting up React frontend..."
cd /home/projectmeats/app/frontend
sudo -u projectmeats npm install
sudo -u projectmeats npm run build

# Create Gunicorn configuration
log_info "Creating Gunicorn configuration..."
cat > /home/projectmeats/app/backend/gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
keepalive = 5

# Logging
accesslog = "/home/projectmeats/logs/gunicorn_access.log"
errorlog = "/home/projectmeats/logs/gunicorn_error.log"
loglevel = "info"
capture_output = True

# Process naming
proc_name = "projectmeats"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
timeout = 120
graceful_timeout = 120
EOF

# Create systemd service
log_info "Creating systemd service..."
cat > /etc/systemd/system/projectmeats.service << 'EOF'
[Unit]
Description=ProjectMeats Django Application
After=network.target"""

        if db_type == 'postgresql':
            script += " postgresql.service"

        script += f"""

[Service]
Type=notify
User=projectmeats
Group=projectmeats
RuntimeDirectory=projectmeats
WorkingDirectory=/home/projectmeats/app/backend
Environment=PATH=/home/projectmeats/app/backend/venv/bin
ExecStart=/home/projectmeats/app/backend/venv/bin/gunicorn -c gunicorn.conf.py projectmeats.wsgi:application
ExecReload=/bin/kill -s HUP \\$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
log_info "Configuring Nginx..."
rm -f /etc/nginx/sites-enabled/default

cat > /etc/nginx/sites-available/projectmeats << 'EOF'
# Rate limiting
limit_req_zone \\$binary_remote_addr zone=projectmeats_api:10m rate=10r/s;

# Upstream for Django
upstream projectmeats_backend {{
    server 127.0.0.1:8000;
}}
"""

        if not use_ssl:
            script += f"""
# HTTP server
server {{
    listen 80;
    server_name {domain}"""
            
            if self.config.get('www_redirect'):
                script += f" www.{domain}"
            
            script += f""";

    # Frontend static files
    location / {{
        root /home/projectmeats/app/frontend/build;
        index index.html;
        try_files \\$uri \\$uri/ /index.html;
        
        # Caching for static assets
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\\$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}

    # API endpoints
    location /api/ {{
        limit_req zone=projectmeats_api burst=20 nodelay;
        
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}

    # Admin interface
    location /admin/ {{
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
    }}

    # Django static files
    location /static/ {{
        alias /home/projectmeats/app/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # Media files
    location /media/ {{
        alias {self.config['media_root']}/;
        expires 1d;
        add_header Cache-Control "public";
    }}
}}
"""
        else:
            # HTTPS configuration
            script += f"""
# HTTP to HTTPS redirect
server {{
    listen 80;
    server_name {domain}"""
            
            if self.config.get('www_redirect'):
                script += f" www.{domain}"
                
            script += f""";
    return 301 https://\\$server_name\\$request_uri;
}}

# HTTPS server
server {{
    listen 443 ssl http2;
    server_name {domain}"""
            
            if self.config.get('www_redirect'):
                script += f" www.{domain}"
                
            script += f""";

    # SSL Configuration (will be updated by Let's Encrypt)
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Frontend static files
    location / {{
        root /home/projectmeats/app/frontend/build;
        index index.html;
        try_files \\$uri \\$uri/ /index.html;
        
        # Caching for static assets
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\\$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}

    # API endpoints
    location /api/ {{
        limit_req zone=projectmeats_api burst=20 nodelay;
        
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}

    # Admin interface
    location /admin/ {{
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
    }}

    # Django static files
    location /static/ {{
        alias /home/projectmeats/app/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # Media files
    location /media/ {{
        alias {self.config['media_root']}/;
        expires 1d;
        add_header Cache-Control "public";
    }}
}}
"""

        script += """
EOF

# Enable site
ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
nginx -t

# Configure firewall
log_info "Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Start services
log_info "Starting services..."
systemctl daemon-reload
systemctl enable projectmeats
systemctl start projectmeats
systemctl enable nginx
systemctl start nginx
"""

        if db_type == 'postgresql':
            script += "systemctl enable postgresql\nsystemctl start postgresql\n"

        if use_ssl:
            script += f"""
# Setup SSL with Let's Encrypt
log_info "Setting up SSL certificate..."
apt install -y certbot python3-certbot-nginx
certbot --nginx -d {domain}"""
            
            if self.config.get('www_redirect'):
                script += f" -d www.{domain}"
                
            script += f""" --agree-tos --email {self.config['admin_email']} --non-interactive

# Setup auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
"""

        script += """
# Create backup script
log_info "Creating backup script..."
cat > /home/projectmeats/backup.sh << 'EOF'
#!/bin/bash
# ProjectMeats backup script

BACKUP_DIR="/home/projectmeats/backups"
DATE=$(date +%Y%m%d_%H%M%S)
"""

        if db_type == 'postgresql':
            script += f"""
# Database backup
pg_dump -h localhost -U {self.config['db_user']} -d {self.config['db_name']} | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"
"""
        else:
            script += """
# SQLite backup
cp /home/projectmeats/app/backend/db.sqlite3 "$BACKUP_DIR/db_backup_$DATE.sqlite3"
"""

        script += """
# Application backup
tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" /home/projectmeats/app/backend /home/projectmeats/uploads

# Cleanup old backups (keep 7 days)
find "$BACKUP_DIR" -name "*backup_*" -mtime +7 -delete

echo "$(date): Backup completed" >> /home/projectmeats/logs/backup.log
EOF

chmod +x /home/projectmeats/backup.sh
chown projectmeats:projectmeats /home/projectmeats/backup.sh

# Setup backup cron job
echo "0 2 * * * /home/projectmeats/backup.sh" | sudo -u projectmeats crontab -

# Final setup
log_info "Final setup and permissions..."
chown -R projectmeats:projectmeats /home/projectmeats/
chmod -R 755 /home/projectmeats/uploads

log_success "🎉 ProjectMeats deployment completed successfully!"
echo ""
log_info "Next steps:"
"""

        if use_ssl:
            script += f'log_info "  🌐 Your application is available at: https://{domain}"'
        else:
            script += f'log_info "  🌐 Your application is available at: http://{domain}"'
            
        script += f"""
log_info "  👤 Admin login: {self.config['admin_username']} / {self.config['admin_password']}"
"""

        if use_ssl:
            script += f'log_info "  🔒 Admin panel: https://{domain}/admin/"'
            script += f'log_info "  📚 API docs: https://{domain}/api/docs/"'
        else:
            script += f'log_info "  🔒 Admin panel: http://{domain}/admin/"'
            script += f'log_info "  📚 API docs: http://{domain}/api/docs/"'

        script += """
log_info "  📁 Logs: /home/projectmeats/logs/"
log_info "  💾 Backups: /home/projectmeats/backups/"
echo ""
log_info "Services status:"
systemctl status projectmeats --no-pager -l
systemctl status nginx --no-pager -l
"""

        if db_type == 'postgresql':
            script += "systemctl status postgresql --no-pager -l\n"

        script += """
echo ""
log_success "Deployment completed! 🚀"
"""

        return script
    
    def create_management_scripts(self):
        """Create server management and monitoring scripts"""
        # ... (existing implementation continues below)

    def check_dns_configuration(self, server_ip="167.99.155.140"):
        """
        Check if domain A record matches server IP and wait for DNS propagation if needed.
        Now includes DigitalOcean API integration for automatic DNS setup.
        
        Args:
            server_ip (str): Expected server IP address
            
        Returns:
            bool: True if DNS is properly configured, False otherwise
        """
        if not self.config.get('domain') or self.config['domain'] == 'localhost':
            self.log("Skipping DNS check for localhost deployment", "INFO")
            return True
            
        domain = self.config['domain']
        self.log(f"🔍 Checking DNS configuration for {domain}", "INFO")
        
        # Check if dig command is available
        try:
            subprocess.run(['dig', '--version'], 
                         capture_output=True, check=True, timeout=10)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.log("Warning: 'dig' command not found. DNS check will be skipped.", "WARNING")
            self.log(f"Please manually verify that {domain} points to {server_ip}", "WARNING")
            return True
        
        # Function to parse dig output properly
        def parse_dig_output(domain):
            """Parse dig output using improved method from problem statement"""
            try:
                # Use the improved parsing from problem statement
                result = subprocess.run(
                    ['dig', domain, 'A'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # Parse with grep and awk as suggested in problem statement
                    grep_result = subprocess.run(
                        ['grep', f'^{domain}\\.', result.stdout],
                        capture_output=True,
                        text=True,
                        input=result.stdout
                    )
                    
                    if grep_result.returncode == 0:
                        lines = grep_result.stdout.strip().split('\n')
                        for line in lines:
                            parts = line.split()
                            if len(parts) >= 5 and parts[3] == 'A':
                                ip = parts[4]
                                # Validate IP format
                                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                                    return ip
                return None
            except Exception as e:
                self.log(f"DNS parsing error: {e}", "WARNING")
                return None
        
        max_attempts = 10  # 10 minutes total with 1-minute intervals as specified
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Parse DNS resolution
                resolved_ip = parse_dig_output(domain)
                
                if resolved_ip:
                    if resolved_ip == server_ip:
                        self.log(f"✅ DNS correctly configured: {domain} -> {resolved_ip}", "SUCCESS")
                        return True
                    else:
                        self.log(f"DNS mismatch: {domain} -> {resolved_ip} (expected {server_ip})", "WARNING")
                        self.log("This could indicate the domain is pointed to a different server", "INFO")
                else:
                    self.log(f"No A record found for {domain}", "WARNING")
                    
            except subprocess.TimeoutExpired:
                self.log("DNS query timed out", "WARNING")
            except Exception as e:
                self.log(f"DNS check error: {e}", "WARNING")
            
            attempt += 1
            if attempt < max_attempts:
                self.log(f"DNS not yet propagated. Waiting 60 seconds... (attempt {attempt}/{max_attempts})", "INFO")
                time.sleep(60)
        
        # DNS check failed - offer automated solution
        self.log("⚠️  DNS Configuration Issue Detected", "WARNING")
        self.log("", "INFO")
        
        # Check for DO_TOKEN environment variable for automated DNS setup
        do_token = os.environ.get('DO_TOKEN')
        if do_token:
            self.log("DigitalOcean token found - attempting automatic DNS configuration...", "INFO")
            
            try:
                # Use the dns_config.sh script for automated setup
                dns_script_path = Path(__file__).parent / 'dns_config.sh'
                if dns_script_path.exists():
                    result = subprocess.run([
                        'bash', str(dns_script_path),
                        '--domain', domain,
                        '--ip', server_ip,
                        '--do-token', do_token
                    ], capture_output=True, text=True, timeout=600)
                    
                    if result.returncode == 0:
                        self.log("✅ Automatic DNS configuration completed!", "SUCCESS")
                        
                        # Re-verify DNS after automated setup
                        self.log("Re-verifying DNS configuration...", "INFO")
                        time.sleep(30)  # Wait 30 seconds for initial propagation
                        
                        for verify_attempt in range(3):
                            resolved_ip = parse_dig_output(domain)
                            if resolved_ip == server_ip:
                                self.log(f"✅ DNS verification successful: {domain} -> {resolved_ip}", "SUCCESS")
                                return True
                            
                            if verify_attempt < 2:
                                self.log("Waiting for DNS propagation...", "INFO")
                                time.sleep(60)
                        
                        self.log("DNS setup completed but propagation may still be in progress", "INFO")
                        self.log(f"Monitor propagation at: https://dnschecker.org/#A/{domain}", "INFO")
                        
                        # Ask user if they want to continue
                        if self.confirm("Continue deployment while DNS propagates?", True):
                            return True
                    else:
                        self.log(f"Automatic DNS setup failed: {result.stderr}", "ERROR")
                        self.log("Falling back to manual configuration instructions", "INFO")
                else:
                    self.log("DNS configuration script not found", "WARNING")
            except Exception as e:
                self.log(f"Error during automatic DNS setup: {e}", "ERROR")
        
        # Provide manual DNS configuration instructions
        self.log("DNS is not properly configured. Your site may not be accessible externally.", "WARNING")
        self.log("", "INFO")
        self.log("🔧 Manual DNS Configuration Required:", "INFO")
        self.log(f"  1. Go to your domain registrar (GoDaddy, Namecheap, etc.)", "INFO")
        self.log(f"  2. Add an A record: {domain} -> {server_ip}", "INFO")
        self.log(f"  3. If using www, add: www.{domain} -> {server_ip}", "INFO")
        self.log("  4. DNS propagation can take up to 48 hours", "INFO")
        self.log(f"  5. Monitor propagation: https://dnschecker.org/#A/{domain}", "INFO")
        self.log("", "INFO")
        
        if not do_token:
            self.log("💡 For automatic DNS setup, set DO_TOKEN environment variable with your DigitalOcean API token", "INFO")
        
        # Ask if user wants to continue anyway
        if self.confirm("Continue deployment without proper DNS? (site won't be externally accessible)", False):
            return True
        else:
            self.log("Deployment cancelled. Please configure DNS first.", "ERROR")
            return False

    def verify_domain_accessibility(self, server_ip="167.99.155.140"):
        """
        Comprehensive domain accessibility verification with proper DNS parsing and external testing.
        Now includes improved DNS parsing and curl --resolve bypass testing.
        
        Args:
            server_ip (str): Expected server IP address
            
        Returns:
            bool: True if domain is accessible, False otherwise
        """
        if not self.config.get('domain') or self.config['domain'] == 'localhost':
            self.log("Skipping domain verification for localhost deployment", "INFO")
            return True
        
        domain = self.config['domain']
        self.log(f"🌐 Verifying domain accessibility for {domain}", "INFO")
        
        # Step 1: Enhanced DNS parsing using improved method from problem statement
        dns_ok = False
        resolved_ip = None
        
        def parse_dig_output_enhanced(domain):
            """Enhanced DNS parsing as specified in problem statement"""
            try:
                # Use the exact parsing method from problem statement:
                # dig domain A | grep '^domain.' | awk '{print $5}'
                dig_result = subprocess.run(
                    ['dig', domain, 'A'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if dig_result.returncode == 0:
                    # Parse with grep and awk as suggested
                    grep_cmd = f"grep '^{domain}\\.' <<< '{dig_result.stdout}' | awk '{{print $5}}'"
                    parse_result = subprocess.run(
                        ['bash', '-c', grep_cmd],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if parse_result.returncode == 0:
                        ip = parse_result.stdout.strip()
                        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                            return ip
                
                # Fallback to simpler parsing
                lines = [line.strip() for line in dig_result.stdout.strip().split('\n') 
                        if line.strip() and not line.startswith(';')]
                
                for line in lines:
                    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', line):
                        return line
                        
                return None
            except Exception as e:
                self.log(f"Enhanced DNS parsing error: {e}", "WARNING")
                return None
        
        try:
            resolved_ip = parse_dig_output_enhanced(domain)
            
            if resolved_ip:
                if resolved_ip == server_ip:
                    self.log(f"✅ DNS correctly resolves: {domain} -> {resolved_ip}", "SUCCESS")
                    dns_ok = True
                else:
                    self.log(f"❌ DNS mismatch: {domain} -> {resolved_ip} (expected {server_ip})", "ERROR")
                    self.log("Check your DNS configuration - A record may be pointing to wrong IP", "WARNING")
            else:
                self.log(f"❌ No valid A record found for {domain}", "ERROR")
                self.log(f"Check external DNS status: https://dnschecker.org/#A/{domain}", "INFO")
        except Exception as e:
            self.log(f"DNS verification error: {e}", "ERROR")
        
        # Step 2: DNS Bypass Test using curl --resolve (from problem statement)
        bypass_ok = False
        if server_ip:
            self.log(f"Testing HTTP connectivity bypassing DNS (--resolve)...", "INFO")
            try:
                # Use curl --resolve as specified in problem statement
                cmd = [
                    'curl', '--resolve', f'{domain}:80:{server_ip}',
                    '-m', '10', '-I', f'http://{domain}'
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    # Check for successful HTTP status codes
                    if any(code in result.stdout for code in ['200 OK', '404', '302', '301']):
                        self.log("✅ HTTP connectivity works (DNS bypass test)", "SUCCESS")
                        bypass_ok = True
                    else:
                        self.log(f"HTTP response received but status unclear:", "WARNING")
                        self.log(result.stdout.split('\n')[0], "INFO")
                else:
                    self.log("❌ HTTP connectivity failed even with DNS bypass", "ERROR")
                    self.log(f"This indicates server/nginx/firewall issues", "WARNING")
                    self.log(f"Curl error: {result.stderr.strip()}", "WARNING")
            except Exception as e:
                self.log(f"DNS bypass test error: {e}", "ERROR")
        
        # Step 3: External connectivity test with original DNS (if resolved)
        http_ok = False
        if resolved_ip:
            self.log("Testing external HTTP connectivity with DNS...", "INFO")
            try:
                cmd = ['curl', '-m', '10', '-I', f'http://{domain}']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    if any(code in result.stdout for code in ['200 OK', '404', '302', '301']):
                        self.log("✅ External HTTP connectivity working", "SUCCESS")
                        http_ok = True
                    else:
                        self.log(f"HTTP response received but status unclear:", "WARNING")
                        self.log(result.stdout.split('\n')[0], "INFO")
                else:
                    self.log("❌ External HTTP connectivity failed", "ERROR")
                    self.log(f"Curl error: {result.stderr.strip()}", "WARNING")
            except Exception as e:
                self.log(f"External connectivity test error: {e}", "ERROR")
        
        # Step 4: Direct IP test
        direct_ip_ok = False
        if server_ip:
            self.log(f"Testing direct IP connectivity to {server_ip}...", "INFO")
            try:
                result = subprocess.run([
                    'curl', '-m', '10', '-I', f'http://{server_ip}'
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    self.log("✅ Direct IP connectivity working", "SUCCESS")
                    direct_ip_ok = True
                else:
                    self.log("❌ Direct IP connectivity failed", "ERROR")
                    self.log("Check if HTTP server is running and firewall allows port 80", "WARNING")
            except Exception as e:
                self.log(f"Direct IP test error: {e}", "ERROR")
        
        # Step 5: Summary and recommendations
        self.log("", "INFO")
        self.log("📊 Domain Accessibility Summary:", "INFO")
        self.log(f"  DNS Resolution: {'✅' if dns_ok else '❌'}", "INFO")
        self.log(f"  HTTP via Domain: {'✅' if http_ok else '❌'}", "INFO")
        self.log(f"  HTTP via DNS Bypass: {'✅' if bypass_ok else '❌'}", "INFO")
        self.log(f"  HTTP via Direct IP: {'✅' if direct_ip_ok else '❌'}", "INFO")
        self.log("", "INFO")
        
        if dns_ok and http_ok:
            self.log("🎉 Domain verification successful - site should be accessible", "SUCCESS")
            return True
        elif bypass_ok or direct_ip_ok:
            if not dns_ok:
                self.log("🔧 DNS Configuration Required", "WARNING")
                self.log(f"Server is running but DNS needs configuration: {domain} -> {server_ip}", "INFO")
                self.log(f"Check DNS propagation: https://dnschecker.org/#A/{domain}", "INFO")
            else:
                self.log("🔧 DNS Propagation in Progress", "INFO")
                self.log("Server responds to bypass tests, DNS may still be propagating", "INFO")
            
            # Offer to continue since server is working
            if self.confirm("Server is accessible but DNS needs work. Continue anyway?", True):
                return True
        else:
            self.log("🔧 Server Configuration Issue", "WARNING")
            self.log("Neither DNS nor direct access working - check server/nginx/firewall", "ERROR")
        
        # Provide manual troubleshooting info
        if not dns_ok:
            self.log("", "INFO")
            self.log("🔧 DNS Troubleshooting:", "INFO")
            self.log(f"  1. Configure DNS: {domain} A record -> {server_ip}", "INFO")
            self.log(f"  2. Monitor propagation: https://dnschecker.org/#A/{domain}", "INFO")
            self.log("  3. DNS can take up to 48 hours to propagate globally", "INFO")
        
        if not direct_ip_ok:
            self.log("", "INFO")
            self.log("🔧 Server Troubleshooting:", "INFO")
            self.log("  1. Check if nginx is running: systemctl status nginx", "INFO")
            self.log("  2. Check if port 80 is listening: ss -tuln | grep :80", "INFO")
            self.log("  3. Check firewall: ufw status", "INFO")
            self.log("  4. Check nginx configuration: nginx -t", "INFO")
        
        return False

    def create_management_scripts(self):
        try:
            scripts_dir = self.project_root / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            
            # Create update script
            update_script = """#!/bin/bash
# ProjectMeats Update Script

echo "🔄 Updating ProjectMeats..."

# Pull latest code
cd /home/projectmeats/app
sudo -u projectmeats git pull origin main

# Update backend
cd backend
sudo -u projectmeats ./venv/bin/pip install -r requirements.txt
sudo -u projectmeats ./venv/bin/python manage.py migrate
sudo -u projectmeats ./venv/bin/python manage.py collectstatic --noinput

# Update frontend
cd ../frontend
sudo -u projectmeats npm install
sudo -u projectmeats npm run build

# Restart services
systemctl restart projectmeats
systemctl reload nginx

echo "✅ Update completed!"
"""
            
            update_file = scripts_dir / "update.sh"
            with open(update_file, 'w', encoding='utf-8') as f:
                f.write(update_script)
            os.chmod(update_file, 0o755)
            
            # Create status script
            status_script = """#!/bin/bash
# ProjectMeats Status Check

echo "📊 ProjectMeats System Status"
echo "=========================="

echo "🐍 Django Application:"
systemctl status projectmeats --no-pager -l

echo ""
echo "🌐 Nginx Web Server:"
systemctl status nginx --no-pager -l

echo ""
echo "🔥 Firewall Status:"
ufw status verbose

echo ""
echo "💾 Disk Usage:"
df -h

echo ""
echo "🧠 Memory Usage:"
free -h

echo ""
echo "⚡ CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}'

echo ""
echo "📈 Application Logs (last 10 lines):"
tail -10 /home/projectmeats/logs/gunicorn_error.log
"""
            
            status_file = scripts_dir / "status.sh"
            with open(status_file, 'w', encoding='utf-8') as f:
                f.write(status_script)
            os.chmod(status_file, 0o755)
            
            # Verify files were created
            if update_file.exists() and status_file.exists():
                self.log("✓ Management scripts created in scripts/ directory", "SUCCESS")
                return True
            else:
                self.log("❌ Failed to create management scripts", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error creating management scripts: {e}", "ERROR")
            return False
    
    def show_next_steps(self):
        """Display next steps for deployment"""
        print(f"\n{Colors.BOLD}🎯 Next Steps{Colors.END}")
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        
        if self.is_local_setup:
            print(f"{Colors.GREEN}Local Development Setup:{Colors.END}")
            print(f"1. Start the backend: {Colors.CYAN}cd backend && python manage.py runserver{Colors.END}")
            print(f"2. Start the frontend: {Colors.CYAN}cd frontend && npm start{Colors.END}")
            print(f"3. Access application: {Colors.CYAN}http://{self.config['domain']}:3000{Colors.END}")
        else:
            print(f"{Colors.GREEN}Production Server Deployment:{Colors.END}")
            print(f"1. Upload files to server: {Colors.CYAN}scp -r . user@{self.config['domain']}:/home/projectmeats/setup{Colors.END}")
            print(f"2. SSH into server: {Colors.CYAN}ssh user@{self.config['domain']}{Colors.END}")
            print(f"3. Run deployment: {Colors.CYAN}cd /home/projectmeats/setup && sudo ./deploy_server.sh{Colors.END}")
            
            protocol = 'https' if self.config.get('use_ssl') else 'http'
            print(f"\n{Colors.GREEN}After Deployment:{Colors.END}")
            print(f"• Application: {Colors.CYAN}{protocol}://{self.config['domain']}{Colors.END}")
            print(f"• Admin Panel: {Colors.CYAN}{protocol}://{self.config['domain']}/admin/{Colors.END}")
            print(f"• API Docs: {Colors.CYAN}{protocol}://{self.config['domain']}/api/docs/{Colors.END}")
        
        print(f"\n{Colors.GREEN}Admin Credentials:{Colors.END}")
        print(f"• Username: {Colors.CYAN}{self.config['admin_username']}{Colors.END}")
        print(f"• Password: {Colors.CYAN}{self.config['admin_password']}{Colors.END}")
        print(f"• Email: {Colors.CYAN}{self.config['admin_email']}{Colors.END}")
        
        print(f"\n{Colors.GREEN}Generated Files:{Colors.END}")
        print(f"• Environment: {Colors.CYAN}backend/.env{Colors.END}")
        print(f"• Frontend Config: {Colors.CYAN}frontend/.env.production{Colors.END}")
        print(f"• Deployment Script: {Colors.CYAN}deploy_server.sh{Colors.END}")
        print(f"• Configuration Backup: {Colors.CYAN}production_config.json{Colors.END}")
        print(f"• Management Scripts: {Colors.CYAN}scripts/{Colors.END}")
        
        print(f"\n{Colors.BLUE}{'='*50}{Colors.END}")
    
    def run(self):
        """Main deployment setup process"""
        try:
            self.print_banner()
            
            # Collect configuration
            deployment_type = self.get_deployment_type()
            self.get_domain_configuration()
            self.get_database_configuration()
            self.get_admin_configuration()
            self.get_email_configuration()
            self.get_security_configuration()
            self.get_advanced_configuration()
            
            # Review configuration
            if not self.display_configuration_summary():
                self.log("Configuration cancelled. Please run the script again.", "INFO")
                return 1
            
            # Post-deployment DNS verification (only for production deployments)
            if not self.is_local_setup:
                if not self.check_dns_configuration():
                    return 1
            
            # Generate configuration files
            if not self.create_environment_file():
                self.log("Failed to create environment file. Deployment setup failed.", "ERROR")
                return 1
                
            if not self.create_frontend_env():
                self.log("Failed to create frontend environment file. Deployment setup failed.", "ERROR")
                return 1
                
            if not self.create_deployment_scripts():
                self.log("Failed to create deployment scripts. Deployment setup failed.", "ERROR")
                return 1
            
            # Show next steps
            self.show_next_steps()
            
            # Final domain accessibility verification (for production deployments)
            if not self.is_local_setup:
                self.log("\n" + "="*60, "INFO")
                self.log("🔍 Performing final domain accessibility verification...", "INFO")
                self.verify_domain_accessibility()
            
            self.log("🎉 Production deployment setup completed successfully!", "SUCCESS")
            return 0
            
        except KeyboardInterrupt:
            self.log("\n\nSetup cancelled by user.", "WARNING")
            return 1
        except Exception as e:
            self.log(f"Setup failed with error: {e}", "ERROR")
            return 1


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print(__doc__)
        return 0
    
    deployment = ProductionDeployment()
    return deployment.run()


if __name__ == "__main__":
    sys.exit(main())