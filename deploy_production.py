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
        return ''.join(secrets.choice(
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)'
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
        
        env_content = self.generate_env_content()
        env_file = self.backend_dir / ".env"
        
        # Backup existing .env if it exists
        if env_file.exists():
            backup_file = self.backend_dir / ".env.backup"
            shutil.copy2(env_file, backup_file)
            self.log(f"Backed up existing .env to .env.backup", "WARNING")
        
        # Write new environment file
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        self.log("✓ Environment file created successfully", "SUCCESS")
        
        # Create production config backup
        config_backup = self.project_root / "production_config.json"
        with open(config_backup, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
        
        self.log(f"✓ Configuration saved to production_config.json", "SUCCESS")
    
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
        
        frontend_env = self.frontend_dir / ".env.production"
        with open(frontend_env, 'w', encoding='utf-8') as f:
            f.write('\n'.join(env_content) + '\n')
        
        self.log("✓ Frontend environment file created", "SUCCESS")
    
    def create_deployment_scripts(self):
        """Create deployment and management scripts"""
        self.log("Creating deployment scripts...", "INFO")
        
        # Create deployment script
        deploy_script = self.create_server_deployment_script()
        deploy_file = self.project_root / "deploy_server.sh"
        
        with open(deploy_file, 'w', encoding='utf-8') as f:
            f.write(deploy_script)
        
        os.chmod(deploy_file, 0o755)
        
        # Create management scripts
        self.create_management_scripts()
        
        self.log("✓ Deployment scripts created", "SUCCESS")
    
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
    # Try git clone with error handling
    if ! sudo -u projectmeats git clone https://github.com/Vacilator/ProjectMeats.git /home/projectmeats/app 2>/dev/null; then
        log_error "Git clone failed due to authentication issues."
        echo ""
        echo "GitHub authentication error detected!"
        echo "This is because GitHub no longer supports password authentication."
        echo ""
        echo "Solutions:"
        echo "1. Use the no-authentication deployment script:"
        echo "   curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash"
        echo ""
        echo "2. Setup Personal Access Token (PAT):"
        echo "   - Go to GitHub.com -> Settings -> Developer settings -> Personal access tokens"
        echo "   - Generate a new token with 'repo' scope"
        echo "   - Use: git clone https://USERNAME:TOKEN@github.com/Vacilator/ProjectMeats.git"
        echo ""
        echo "3. Setup SSH keys:"
        echo "   - Generate: ssh-keygen -t ed25519"
        echo "   - Add public key to GitHub -> Settings -> SSH keys"
        echo "   - Use: git clone git@github.com:Vacilator/ProjectMeats.git"
        echo ""
        echo "4. Manual transfer:"
        echo "   - Download the project on a machine with GitHub access"
        echo "   - Transfer to this server via SCP"
        echo ""
        echo "For detailed instructions, see:"
        echo "https://github.com/Vacilator/ProjectMeats/blob/main/docs/deployment_authentication_guide.md"
        echo ""
        exit 1
    fi
else
    cd /home/projectmeats/app
    if ! sudo -u projectmeats git pull origin main 2>/dev/null; then
        log_warning "Git pull failed, continuing with existing code..."
        echo "Note: Unable to update code from GitHub. Using existing installation."
        echo "If you need the latest version, see the authentication guide:"
        echo "https://github.com/Vacilator/ProjectMeats/blob/main/docs/deployment_authentication_guide.md"
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
        """Create management and maintenance scripts"""
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
        
        with open(scripts_dir / "update.sh", 'w', encoding='utf-8') as f:
            f.write(update_script)
        os.chmod(scripts_dir / "update.sh", 0o755)
        
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

"""
        
        if self.config['database_type'] == 'postgresql':
            status_script += """
echo ""
echo "🗄️  PostgreSQL Database:"
systemctl status postgresql --no-pager -l
"""

        status_script += """
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
        
        with open(scripts_dir / "status.sh", 'w', encoding='utf-8') as f:
            f.write(status_script)
        os.chmod(scripts_dir / "status.sh", 0o755)
        
        self.log("✓ Management scripts created in scripts/ directory", "SUCCESS")
    
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
            
            # Generate configuration files
            self.create_environment_file()
            self.create_frontend_env()
            self.create_deployment_scripts()
            
            # Show next steps
            self.show_next_steps()
            
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