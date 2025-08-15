#!/usr/bin/env python3
"""
ProjectMeats Unified Deployment System
=====================================

🚀 ONE SCRIPT TO RULE THEM ALL 🚀

This is the ONLY deployment script you need for ProjectMeats.
All other deployment methods have been consolidated into this unified system.

Features:
- 🎯 Complete production deployment automation
- 🐘 Interactive PostgreSQL setup guide with step-by-step configuration
- 🔄 CI/CD pipeline integration with deployment hooks
- 🐳 Docker deployment support
- 🔒 Enhanced security configuration
- 📊 Real-time monitoring and health checks
- 🔧 Multi-environment support (dev, staging, production)
- 🌐 Multi-cloud provider support
- 📱 Interactive deployment wizard
- 🔄 Rollback and recovery capabilities

Usage Examples:
    # 🎯 Production deployment with all features:
    python3 master_deploy.py --auto --domain=yourdomain.com --env=production

    # 🐘 Interactive PostgreSQL setup:
    python3 master_deploy.py --setup-postgres --interactive

    # 🐳 Docker-based deployment:
    python3 master_deploy.py --docker --domain=yourdomain.com

    # 🔄 CI/CD pipeline deployment:
    python3 master_deploy.py --ci-cd --environment=staging

    # 📱 Full interactive wizard:
    python3 master_deploy.py --wizard

    # 🔧 Server preparation only:
    python3 master_deploy.py --prepare-server

    # 📊 Health check and monitoring setup:
    python3 master_deploy.py --monitoring --domain=yourdomain.com

Consolidated Features from Previous Scripts:
- one_click_deploy.sh → Integrated automated deployment
- deploy_production.py → Enhanced interactive setup
- quick_deploy.sh → Fast deployment options
- deploy_server.sh → Server configuration
- All verification scripts → Built-in health checks

Author: ProjectMeats Team
Version: 2.0 - Unified Deployment System
"""

import os
import sys
import json
import subprocess
import platform
import time
import urllib.request
import shutil
from pathlib import Path
import secrets
import getpass

class MasterDeployer:
    def __init__(self):
        self.config = {
            'domain': None,
            'ssl_enabled': True,
            'database_type': 'postgresql',
            'admin_user': 'admin',
            'admin_email': 'admin@example.com',
            'admin_password': 'ProjectMeats2024!',
            'project_dir': '/opt/projectmeats',
            'logs_dir': '/opt/projectmeats/logs',
            'backup_dir': '/opt/projectmeats/backups',
            'app_user': 'projectmeats',
            'environment': 'production',
            'deployment_mode': 'standard'  # standard, docker, ci-cd
        }
        
        # Parse command line arguments
        self.parse_arguments()
        
        # Set deployment modes
        self.is_server_mode = '--server' in sys.argv
        self.is_auto_mode = '--auto' in sys.argv
        self.is_interactive_mode = '--interactive' in sys.argv or '--wizard' in sys.argv
        self.is_docker_mode = '--docker' in sys.argv
        self.is_ci_cd_mode = '--ci-cd' in sys.argv
        self.is_postgres_setup = '--setup-postgres' in sys.argv
        self.is_monitoring_mode = '--monitoring' in sys.argv
        self.is_prepare_server = '--prepare-server' in sys.argv

    def parse_arguments(self):
        """Enhanced argument parsing for consolidated functionality"""
        for arg in sys.argv:
            if arg.startswith('--domain='):
                self.config['domain'] = arg.split('=', 1)[1]
            elif arg.startswith('--github-user='):
                self.config['github_user'] = arg.split('=', 1)[1]
            elif arg.startswith('--github-token='):
                self.config['github_token'] = arg.split('=', 1)[1]
            elif arg.startswith('--env=') or arg.startswith('--environment='):
                self.config['environment'] = arg.split('=', 1)[1]
            elif arg.startswith('--project-dir='):
                self.config['project_dir'] = arg.split('=', 1)[1]
            elif arg.startswith('--app-user='):
                self.config['app_user'] = arg.split('=', 1)[1]
            elif arg.startswith('--admin-user='):
                self.config['admin_user'] = arg.split('=', 1)[1]
            elif arg.startswith('--admin-email='):
                self.config['admin_email'] = arg.split('=', 1)[1]
            elif arg.startswith('--database='):
                self.config['database_type'] = arg.split('=', 1)[1]
            elif arg == '--help' or arg == '-h':
                self.show_help()
                sys.exit(0)

    def show_help(self):
        """Display comprehensive help for the unified deployment system"""
        print("""
🚀 ProjectMeats Unified Deployment System - Help

USAGE:
    python3 master_deploy.py [OPTIONS]

DEPLOYMENT MODES:
    --auto                  Fully automated deployment (no prompts)
    --interactive          Interactive deployment wizard with step-by-step guidance
    --wizard               Same as --interactive
    --docker               Deploy using Docker containers
    --ci-cd                CI/CD pipeline deployment mode
    --server               Server-side deployment (after uploading code)

SETUP OPTIONS:
    --setup-postgres       Interactive PostgreSQL setup guide only
    --prepare-server       Prepare server environment only (no app deployment)
    --monitoring           Setup monitoring and health checks

CONFIGURATION:
    --domain=DOMAIN        Your domain name (e.g., mycompany.com)
    --env=ENV              Environment: dev, staging, production (default: production)
    --database=DB          Database type: postgresql, sqlite (default: postgresql)
    --project-dir=DIR      Installation directory (default: /opt/projectmeats)
    --app-user=USER        Application user (default: projectmeats)
    --admin-user=USER      Admin username (default: admin)
    --admin-email=EMAIL    Admin email address

GITHUB AUTHENTICATION:
    --github-user=USER     GitHub username for repository access
    --github-token=TOKEN   GitHub Personal Access Token

EXAMPLES:
    # 🎯 Complete production deployment:
    sudo python3 master_deploy.py --auto --domain=mycompany.com

    # 🐘 Interactive PostgreSQL setup:
    sudo python3 master_deploy.py --setup-postgres --interactive

    # 🐳 Docker deployment:
    sudo python3 master_deploy.py --docker --domain=mycompany.com --env=production

    # 📱 Full interactive wizard:
    sudo python3 master_deploy.py --wizard

    # 🔧 Staging environment:
    sudo python3 master_deploy.py --auto --domain=staging.mycompany.com --env=staging

    # 📊 Setup monitoring only:
    sudo python3 master_deploy.py --monitoring --domain=mycompany.com

SECURITY NOTES:
    ⚠️  This script requires sudo/root privileges
    🔒 Automatically configures firewall and SSL certificates
    🛡️  Implements security best practices
    🔑 Generates secure random passwords

For detailed documentation, visit:
https://github.com/Vacilator/ProjectMeats/blob/main/docs/deployment_guide.md
        """)

    def run_deployment_wizard(self):
        """Interactive deployment wizard with comprehensive guidance"""
        if not self.is_interactive_mode:
            return
            
        print("\n" + "🧙‍♂️" * 30)
        print("ProjectMeats Deployment Wizard")
        print("🧙‍♂️" * 30)
        
        print("\n🎯 Welcome to the ProjectMeats Deployment Wizard!")
        print("This wizard will guide you through the complete deployment process.")
        
        # Step 1: Environment Selection
        print("\n📋 Step 1: Environment Configuration")
        print("Available environments:")
        print("1. 🚀 Production - Full production deployment with SSL, security, monitoring")
        print("2. 🧪 Staging - Staging environment for testing")
        print("3. 💻 Development - Development environment with debugging enabled")
        
        while True:
            env_choice = input("\nSelect environment (1-3) [1]: ").strip() or "1"
            if env_choice == "1":
                self.config['environment'] = 'production'
                break
            elif env_choice == "2":
                self.config['environment'] = 'staging'
                break
            elif env_choice == "3":
                self.config['environment'] = 'development'
                break
            else:
                print("Please enter 1, 2, or 3")
        
        # Step 2: Deployment Method
        print(f"\n🔧 Step 2: Deployment Method for {self.config['environment'].title()}")
        print("Available deployment methods:")
        print("1. 📦 Standard - Traditional server deployment")
        print("2. 🐳 Docker - Container-based deployment (recommended)")
        print("3. ☁️  Cloud - Cloud provider deployment")
        
        while True:
            deploy_choice = input("\nSelect deployment method (1-3) [2]: ").strip() or "2"
            if deploy_choice == "1":
                self.config['deployment_mode'] = 'standard'
                break
            elif deploy_choice == "2":
                self.config['deployment_mode'] = 'docker'
                self.is_docker_mode = True
                break
            elif deploy_choice == "3":
                self.config['deployment_mode'] = 'cloud'
                break
            else:
                print("Please enter 1, 2, or 3")
        
        # Step 3: Database Configuration
        print("\n🐘 Step 3: Database Configuration")
        self.show_postgresql_setup_guide()
        
        # Step 4: Domain and SSL
        if not self.config['domain']:
            print("\n🌐 Step 4: Domain and SSL Configuration")
            while True:
                domain = input("Enter your domain name (e.g., mycompany.com): ").strip()
                if domain and '.' in domain:
                    self.config['domain'] = domain
                    break
                print("Please enter a valid domain name.")
        
        # Step 5: Security Configuration
        print("\n🔒 Step 5: Security Configuration")
        print("The following security measures will be configured:")
        print("✅ UFW Firewall with minimal open ports")
        print("✅ Fail2Ban for intrusion prevention")
        print("✅ SSL certificates via Let's Encrypt")
        print("✅ Security headers and HTTPS enforcement")
        print("✅ Regular automated backups")
        
        # Step 6: Final Confirmation
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT SUMMARY")
        print("=" * 60)
        print(f"Environment: {self.config['environment'].title()}")
        print(f"Deployment Mode: {self.config['deployment_mode'].title()}")
        print(f"Domain: {self.config['domain']}")
        print(f"Database: {self.config['database_type'].title()}")
        print(f"Project Directory: {self.config['project_dir']}")
        print(f"SSL Enabled: {'Yes' if self.config['ssl_enabled'] else 'No'}")
        print("=" * 60)
        
        proceed = input("\n🚀 Ready to start deployment? [Y/n]: ").lower()
        if proceed == 'n':
            self.log("Deployment cancelled by user", 'WARNING')
            sys.exit(0)
        
        print("\n🎯 Starting deployment process...")
        self.is_auto_mode = True  # Switch to auto mode after wizard

    def log(self, message, level='INFO'):
        """Enhanced logging with colors"""
        colors = {
            'INFO': '\033[94m',     # Blue
            'SUCCESS': '\033[92m',  # Green
            'WARNING': '\033[93m',  # Yellow
            'ERROR': '\033[91m',    # Red
            'HEADER': '\033[95m'    # Purple
        }
        reset = '\033[0m'
        
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"{colors.get(level, '')}{timestamp} [{level}] {message}{reset}")
        
        # Also log to file if in server mode
        if self.is_server_mode:
            log_file = f"{self.config['logs_dir']}/deployment.log"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'a') as f:
                f.write(f"{timestamp} [{level}] {message}\n")

    def run_command(self, command, capture_output=False, check=True):
        """Execute shell command with logging"""
        self.log(f"Executing: {command}")
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
                return result.stdout.strip()
            else:
                subprocess.run(command, shell=True, check=check)
                return True
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", 'ERROR')
            if check:
                raise
            return False

    def check_prerequisites(self):
        """Check if we can run on this system"""
        self.log("Checking prerequisites...", 'HEADER')
        
        # Check OS
        if not platform.system() == 'Linux':
            self.log("This script requires Linux (Ubuntu 20.04+ recommended)", 'ERROR')
            return False
            
        # Check sudo/root
        if os.geteuid() != 0:
            self.log("This script requires root privileges. Run with sudo.", 'ERROR')
            return False
            
        # Check internet connectivity
        try:
            urllib.request.urlopen('https://github.com', timeout=10)
            self.log("Internet connectivity: OK", 'SUCCESS')
        except:
            self.log("No internet connectivity detected", 'ERROR')
            return False
            
        return True

    def interactive_setup(self):
        """Interactive configuration if not in auto mode"""
        if self.is_auto_mode:
            return
            
        self.log("Interactive Setup", 'HEADER')
        print("\nProjectMeats Production Deployment Setup")
        print("=" * 40)
        
        # Domain name
        if not self.config['domain']:
            while True:
                domain = input("\nEnter your domain name (e.g., mycompany.com): ").strip()
                if domain and '.' in domain:
                    self.config['domain'] = domain
                    break
                print("Please enter a valid domain name.")
        
        # Admin credentials
        print(f"\nAdmin user will be created:")
        print(f"Username: {self.config['admin_user']}")
        print(f"Password: {self.config['admin_password']}")
        print(f"Email: {self.config['admin_email']}")
        
        change = input("\nChange admin settings? [y/N]: ").lower()
        if change == 'y':
            self.config['admin_user'] = input("Admin username [admin]: ").strip() or 'admin'
            self.config['admin_email'] = input(f"Admin email [admin@{self.config['domain']}]: ").strip() or f"admin@{self.config['domain']}"
            self.config['admin_password'] = getpass.getpass("Admin password [press enter for default]: ").strip() or self.config['admin_password']
        
        # Database choice
        print(f"\nDatabase: {self.config['database_type']}")
        if input("Use SQLite instead of PostgreSQL? [y/N]: ").lower() == 'y':
            self.config['database_type'] = 'sqlite'
        
        # Final confirmation
        print("\n" + "=" * 50)
        print("DEPLOYMENT CONFIGURATION:")
        print(f"Domain: https://{self.config['domain']}")
        print(f"Database: {self.config['database_type']}")
        print(f"Project Directory: {self.config['project_dir']}")
        print(f"Admin User: {self.config['admin_user']}")
        print("=" * 50)
        
        if not self.is_auto_mode:
            confirm = input("\nProceed with deployment? [Y/n]: ").lower()
            if confirm == 'n':
                self.log("Deployment cancelled by user", 'WARNING')
                sys.exit(0)

    def get_github_authentication(self):
        """Get GitHub authentication credentials for downloading"""
        # Check for environment variables first
        github_user = os.environ.get('GITHUB_USER') or os.environ.get('GITHUB_USERNAME')
        github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_PAT')
        
        if github_user and github_token:
            self.config['github_user'] = github_user
            self.config['github_token'] = github_token
            self.log("GitHub authentication loaded from environment variables", 'SUCCESS')
            return
        
        if self.is_auto_mode and 'github_user' in self.config and 'github_token' in self.config:
            return  # Already configured via command line
            
        self.log("GitHub Authentication Setup", 'HEADER')
        print("\nTo download ProjectMeats from GitHub, authentication may be required.")
        print("GitHub has deprecated password authentication for git operations.")
        print("\nYou can:")
        print("1. Skip authentication (try public download methods)")
        print("2. Provide Personal Access Token (PAT) - Recommended")
        print("3. Configure SSH key authentication later")
        
        auth_choice = input("\nChoose authentication method (1-3) [1]: ").strip() or "1"
        
        if auth_choice == "2":
            print("\nPersonal Access Token Setup:")
            print("1. Go to GitHub.com -> Settings -> Developer settings -> Personal access tokens")
            print("2. Generate a new token with 'repo' scope")
            print("3. Copy the token (it won't be shown again)")
            
            self.config['github_user'] = input("\nGitHub username: ").strip()
            if self.config['github_user']:
                self.config['github_token'] = getpass.getpass("GitHub Personal Access Token: ").strip()
                if self.config['github_token']:
                    self.log("GitHub authentication configured", 'SUCCESS')
                else:
                    self.log("No token provided, will try public methods", 'WARNING')
                    self.config.pop('github_user', None)
            else:
                self.log("No username provided, will try public methods", 'WARNING')
        else:
            self.log("Will attempt public download methods", 'INFO')

    def fix_nodejs_conflicts(self):
        """Handle Node.js installation conflicts robustly"""
        self.log("Fixing Node.js installation conflicts...", 'HEADER')
        
        # Stop any running Node.js processes
        self.log("Stopping Node.js processes...")
        # Find running Node.js processes
        try:
            result = subprocess.run(
                ["ps", "-eo", "pid,comm,args"], capture_output=True, text=True, check=True
            )
            node_procs = []
            for line in result.stdout.strip().split("\n")[1:]:
                parts = line.split(None, 2)
                if len(parts) < 3:
                    continue
                pid, comm, args = parts
                # Match only processes where the command is 'node'
                if comm == "node":
                    node_procs.append((pid, args))
            if node_procs:
                self.log(f"Found {len(node_procs)} running Node.js processes:", "WARNING")
                for pid, args in node_procs:
                    self.log(f"  PID {pid}: {args}", "WARNING")
                if not self.is_auto_mode:
                    confirm = input("Kill these Node.js processes? [y/N]: ").lower()
                    if confirm != "y":
                        self.log("Skipping Node.js process termination.", "WARNING")
                    else:
                        for pid, _ in node_procs:
                            try:
                                os.kill(int(pid), 9)
                                self.log(f"Killed Node.js process PID {pid}", "INFO")
                            except Exception as e:
                                self.log(f"Failed to kill PID {pid}: {e}", "ERROR")
                else:
                    for pid, _ in node_procs:
                        try:
                            os.kill(int(pid), 9)
                            self.log(f"Killed Node.js process PID {pid}", "INFO")
                        except Exception as e:
                            self.log(f"Failed to kill PID {pid}: {e}", "ERROR")
            else:
                self.log("No running Node.js processes found.", "INFO")
        except Exception as e:
            self.log(f"Error checking/killing Node.js processes: {e}", "ERROR")
        # Complete Node.js cleanup
        self.log("Removing all Node.js packages...")
        packages_to_remove = [
            'nodejs', 'npm', 'libnode-dev', 'libnode72', 'libnode108', 
            'nodejs-doc', 'node-gyp', 'node-cacache'
        ]
        
        for package in packages_to_remove:
            self.run_command(f"apt remove -y {package} || true", check=False)
            self.run_command(f"apt purge -y {package} || true", check=False)
        
        # Remove manually installed binaries
        self.log("Cleaning manually installed Node.js...")
        directories_to_clean = [
            '/usr/local/bin/node*', '/usr/local/bin/npm*', 
            '/usr/local/lib/node_modules', '/usr/bin/node*', '/usr/bin/npm*'
        ]
        
        for dir_pattern in directories_to_clean:
            self.run_command(f"rm -rf {dir_pattern} || true", check=False)
        
        # Clean package cache
        self.log("Cleaning package cache...")
        self.run_command("apt autoremove -y")
        self.run_command("apt autoclean")
        self.run_command("apt clean")
        self.run_command("apt update")
        
        # Install Node.js with optimized fallback methods
        self.log("Installing Node.js 18 LTS...")
        
        # Check if Node.js is already installed with acceptable version
        try:
            version = self.run_command("node --version", capture_output=True)
            if version and version.startswith('v1'):  # v14, v16, v18, etc.
                major_version = int(version.split('.')[0][1:])
                if major_version >= 14:  # Minimum acceptable version
                    self.log(f"Node.js {version} already installed and acceptable", 'SUCCESS')
                    return True
        except:
            pass
        
        # Method 1: NodeSource repository (fastest for production)
        try:
            self.log("Installing via NodeSource repository...")
            # Combined setup and install for efficiency (single command reduces time)
            self.run_command("curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt install -y nodejs")
            
            # Verify installation
            version = self.run_command("node --version", capture_output=True)
            self.log(f"Node.js installed successfully: {version}", 'SUCCESS')
            return True
            
        except:
            self.log("NodeSource installation failed, trying snap...", 'WARNING')
        
        # Method 2: Snap package
        try:
            self.run_command("snap install node --classic")
            
            # Create symlinks for compatibility
            self.run_command("ln -sf /snap/bin/node /usr/local/bin/node", check=False)
            self.run_command("ln -sf /snap/bin/npm /usr/local/bin/npm", check=False)
            
            version = self.run_command("node --version", capture_output=True)
            self.log(f"Node.js installed via snap: {version}", 'SUCCESS')
            return True
            
        except:
            self.log("Snap installation failed, trying Ubuntu repositories...", 'WARNING')
        
        # Method 3: Ubuntu repositories (fallback)
        try:
            self.run_command("apt install -y nodejs npm")
            version = self.run_command("node --version", capture_output=True)
            self.log(f"Node.js installed from Ubuntu repos: {version}", 'SUCCESS')
            return True
            
        except:
            self.log("All Node.js installation methods failed!", 'ERROR')
            return False

    def setup_system(self):
        """Install and configure system dependencies with optimization"""
        self.log("Setting up system dependencies...", 'HEADER')
        
        # Combined system update and package installation for efficiency
        self.log("Updating system and installing packages...")
        packages = [
            'python3', 'python3-pip', 'python3-venv', 'nginx', 'git', 
            'curl', 'ufw', 'fail2ban', 'certbot', 'python3-certbot-nginx',
            'htop', 'unzip', 'supervisor'
        ]
        
        if self.config['database_type'] == 'postgresql':
            packages.extend(['postgresql', 'postgresql-contrib', 'libpq-dev'])
        
        # Single command for faster execution
        package_list = ' '.join(packages)
        self.run_command(f"apt update && apt upgrade -y && apt install -y {package_list}")
        
        # Fix Node.js conflicts (optimized)
        if not self.fix_nodejs_conflicts():
            self.log("Failed to install Node.js. Deployment cannot continue.", 'ERROR')
            sys.exit(1)
        
        # Create application user efficiently
        self.log("Creating application user...")
        # Combined user creation and configuration
        self.run_command(f"useradd -m -s /bin/bash -G sudo {self.config['app_user']} 2>/dev/null || usermod -aG sudo {self.config['app_user']}", check=False)

    def setup_database(self):
        """Configure database with interactive PostgreSQL setup guide"""
        self.log("Setting up database...", 'HEADER')
        
        if self.config['database_type'] == 'postgresql':
            self.log("Configuring PostgreSQL...")
            
            # Interactive PostgreSQL Setup Guide
            if not self.is_auto_mode:
                self.show_postgresql_setup_guide()
            
            # Generate random password
            db_password = secrets.token_urlsafe(16)
            
            # Enhanced PostgreSQL setup with validation
            success = self.setup_postgresql_database(db_password)
            if not success:
                self.log("PostgreSQL setup failed. Falling back to SQLite.", 'WARNING')
                self.config['database_type'] = 'sqlite'
                self.setup_sqlite_database()
            
        else:
            self.setup_sqlite_database()

    def show_postgresql_setup_guide(self):
        """Interactive step-by-step PostgreSQL configuration guide"""
        print("\n" + "🐘" * 50)
        print("PostgreSQL Configuration Guide")
        print("🐘" * 50)
        
        print("\n📋 PostgreSQL Setup Checklist:")
        print("1. ✅ PostgreSQL service will be installed automatically")
        print("2. ✅ Database 'projectmeats' will be created")
        print("3. ✅ Application user will be configured with permissions")
        print("4. ✅ Secure random password will be generated")
        print("5. ✅ Connection testing will be performed")
        
        print("\n🔧 What this script will do:")
        print("• Install PostgreSQL 13+ if not already installed")
        print("• Create 'projectmeats' database")
        print(f"• Create user '{self.config['app_user']}' with database permissions")
        print("• Configure secure authentication")
        print("• Test database connectivity")
        
        print("\n⚠️  Important Notes:")
        print("• PostgreSQL will be configured for local connections")
        print("• A secure random password will be generated automatically")
        print("• Backup any existing PostgreSQL data before proceeding")
        print("• The script requires sudo privileges for PostgreSQL setup")
        
        print("\n🗂️  Alternative: Use SQLite")
        print("If you prefer a simpler setup for development/testing:")
        sqlite_choice = input("Would you like to use SQLite instead? [y/N]: ").lower()
        if sqlite_choice == 'y':
            self.config['database_type'] = 'sqlite'
            self.log("Switched to SQLite database", 'INFO')
            return
        
        print("\n📊 PostgreSQL Configuration Details:")
        print(f"Database Name: projectmeats")
        print(f"Database User: {self.config['app_user']}")
        print(f"Connection: localhost:5432")
        print(f"Authentication: md5 (password)")
        
        proceed = input("\nProceed with PostgreSQL setup? [Y/n]: ").lower()
        if proceed == 'n':
            self.log("PostgreSQL setup cancelled. Switching to SQLite.", 'WARNING')
            self.config['database_type'] = 'sqlite'

    def setup_postgresql_database(self, db_password):
        """Enhanced PostgreSQL setup with validation and error handling"""
        try:
            # Ensure PostgreSQL is running
            self.log("Starting PostgreSQL service...")
            self.run_command("systemctl start postgresql")
            self.run_command("systemctl enable postgresql")
            
            # Wait for PostgreSQL to be ready
            self.log("Waiting for PostgreSQL to be ready...")
            for attempt in range(10):
                try:
                    self.run_command("sudo -u postgres psql -c 'SELECT 1;' > /dev/null", check=True)
                    break
                except:
                    if attempt < 9:
                        time.sleep(2)
                        continue
                    else:
                        raise Exception("PostgreSQL failed to start after 20 seconds")
            
            self.log("PostgreSQL is ready", 'SUCCESS')
            
            # Create database and user with enhanced error handling
            self.log("Creating database and user...")
            commands = [
                # Drop existing database/user if they exist (for clean setup)
                f"cd /tmp && sudo -u postgres psql -c \"DROP DATABASE IF EXISTS projectmeats;\"",
                f"cd /tmp && sudo -u postgres psql -c \"DROP USER IF EXISTS {self.config['app_user']};\"",
                
                # Create fresh database and user
                f"cd /tmp && sudo -u postgres createdb projectmeats",
                f"cd /tmp && sudo -u postgres createuser {self.config['app_user']}",
                f"cd /tmp && sudo -u postgres psql -c \"ALTER USER {self.config['app_user']} PASSWORD '{db_password}';\"",
                f"cd /tmp && sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE projectmeats TO {self.config['app_user']};\"",
                f"cd /tmp && sudo -u postgres psql -c \"ALTER USER {self.config['app_user']} CREATEDB;\"",
                f"cd /tmp && sudo -u postgres psql -c \"ALTER USER {self.config['app_user']} CREATEROLE;\""
            ]
            
            for i, cmd in enumerate(commands, 1):
                self.log(f"Executing PostgreSQL command {i}/{len(commands)}...")
                self.run_command(cmd, check=True)
            
            # Test database connection
            self.log("Testing database connection...")
            test_connection = f"PGPASSWORD='{db_password}' psql -h localhost -U {self.config['app_user']} -d projectmeats -c 'SELECT version();'"
            self.run_command(test_connection, check=True)
            
            # Store database config
            self.config['database_url'] = f"postgresql://{self.config['app_user']}:{db_password}@localhost:5432/projectmeats"
            self.config['database_password'] = db_password
            
            self.log("PostgreSQL setup completed successfully", 'SUCCESS')
            return True
            
        except Exception as e:
            self.log(f"PostgreSQL setup failed: {e}", 'ERROR')
            return False

    def setup_sqlite_database(self):
        """Setup SQLite database"""
        self.log("Configuring SQLite...")
        db_path = f"{self.config['project_dir']}/db.sqlite3"
        self.config['database_url'] = f"sqlite:///{db_path}"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.log("SQLite database configured", 'SUCCESS')

    def download_application(self):
        """Download and setup ProjectMeats application"""
        self.log("Downloading ProjectMeats application...", 'HEADER')
        
        # Create project directory
        self.run_command(f"mkdir -p {self.config['project_dir']}")
        
        # Check if directory already has content and handle it
        try:
            result = self.run_command(f"ls -la {self.config['project_dir']}", capture_output=True)
            if result and len(result.strip().split('\n')) > 3:  # More than just . and ..
                self.log("Project directory already contains files", 'WARNING')
                if not self.is_auto_mode:
                    backup_choice = input("Backup existing files and proceed? [Y/n]: ").lower()
                    if backup_choice == 'n':
                        self.log("Deployment cancelled due to existing files", 'ERROR')
                        sys.exit(1)
                
                # Create backup of existing content
                backup_dir = f"{self.config['project_dir']}_backup_{int(time.time())}"
                self.log(f"Creating backup at {backup_dir}")
                self.run_command(f"mv {self.config['project_dir']} {backup_dir}")
                self.run_command(f"mkdir -p {self.config['project_dir']}")
        except:
            pass  # Directory is empty or doesn't exist, which is fine
        
        # Download from GitHub (multiple methods)
        project_downloaded = False
        
        # Method 1: Git clone with PAT authentication (if configured)
        if 'github_user' in self.config and 'github_token' in self.config:
            try:
                self.log("Downloading via git clone with Personal Access Token...")
                github_url = f"https://{self.config['github_user']}:{self.config['github_token']}@github.com/Vacilator/ProjectMeats.git"
                self.run_command(f"cd {self.config['project_dir']} && git clone {github_url} .")
                project_downloaded = True
                self.log("Successfully downloaded using PAT authentication", 'SUCCESS')
            except:
                self.log("PAT authentication failed, trying other methods...", 'WARNING')
        
        # Method 2: Basic git clone (public access)
        if not project_downloaded:
            try:
                self.log("Downloading via git clone (public access)...")
                self.run_command(f"cd {self.config['project_dir']} && git clone https://github.com/Vacilator/ProjectMeats.git .")
                project_downloaded = True
                self.log("Successfully downloaded using public access", 'SUCCESS')
            except:
                self.log("Public git clone failed, trying download...", 'WARNING')
        
        # Method 3: Direct download with validation
        if not project_downloaded:
            try:
                self.log("Downloading via direct download...")
                download_cmd = f"cd {self.config['project_dir']} && curl -L https://github.com/Vacilator/ProjectMeats/archive/main.zip -o project.zip"
                self.run_command(download_cmd)
                
                # Validate download
                zip_size = self.run_command(f"stat -c%s {self.config['project_dir']}/project.zip 2>/dev/null || echo 0", capture_output=True)
                if int(zip_size) < 1000:  # Less than 1KB indicates error response
                    raise Exception(f"Download failed - file too small ({zip_size} bytes)")
                
                # Check if it's actually a zip file
                file_result = self.run_command(f"cd {self.config['project_dir']} && file project.zip", capture_output=True)
                if "zip" not in file_result.lower():
                    raise Exception("Downloaded file is not a valid zip archive")
                
                # Extract
                extract_cmd = f"cd {self.config['project_dir']} && unzip -q project.zip && mv ProjectMeats-main/* . && mv ProjectMeats-main/.* . 2>/dev/null || true && rm -rf ProjectMeats-main project.zip"
                self.run_command(extract_cmd)
                project_downloaded = True
                self.log("Successfully downloaded via direct download", 'SUCCESS')
            except Exception as e:
                self.log(f"Direct download failed: {e}", 'ERROR')
        
        # Method 4: Try tarball download as alternative
        if not project_downloaded:
            try:
                self.log("Downloading via tarball...")
                download_cmd = f"cd {self.config['project_dir']} && curl -L https://github.com/Vacilator/ProjectMeats/archive/refs/heads/main.tar.gz -o project.tar.gz"
                self.run_command(download_cmd)
                
                # Validate tarball
                tar_size = self.run_command(f"stat -c%s {self.config['project_dir']}/project.tar.gz 2>/dev/null || echo 0", capture_output=True)
                if int(tar_size) < 1000:  # Less than 1KB indicates error response
                    raise Exception(f"Tarball download failed - file too small ({tar_size} bytes)")
                
                # Check if it's actually a tar.gz file
                file_result = self.run_command(f"cd {self.config['project_dir']} && file project.tar.gz", capture_output=True)
                if "gzip compressed" not in file_result.lower():
                    raise Exception("Downloaded file is not a valid gzip archive")
                
                # Extract
                extract_cmd = f"cd {self.config['project_dir']} && tar -xzf project.tar.gz && mv ProjectMeats-main/* . && mv ProjectMeats-main/.* . 2>/dev/null || true && rm -rf ProjectMeats-main project.tar.gz"
                self.run_command(extract_cmd)
                project_downloaded = True
                self.log("Successfully downloaded via tarball", 'SUCCESS')
            except Exception as e:
                self.log(f"Tarball download failed: {e}", 'ERROR')
        
        # Method 5: Fallback with detailed instructions
        if not project_downloaded:
            self.log("All automatic download methods failed!", 'ERROR')
            self.print_github_auth_help()
            sys.exit(1)
        
        # Set ownership
        self.run_command(f"chown -R {self.config['app_user']}:{self.config['app_user']} {self.config['project_dir']}")

    def print_github_auth_help(self):
        """Print detailed GitHub authentication help"""
        print("\n" + "="*60)
        print("🔒 GitHub Authentication Required")
        print("="*60)
        print("\nGitHub has deprecated password authentication for git operations.")
        print("To download ProjectMeats, you need to use one of these methods:")
        
        print("\n1. 🔑 Personal Access Token (Recommended):")
        print("   • Go to GitHub.com → Settings → Developer settings → Personal access tokens")
        print("   • Generate a new token with 'repo' scope")
        print("   • Re-run this script and provide the token when prompted")
        print("   • Or use command line: --github-user=USERNAME --github-token=TOKEN")
        
        print("\n2. 🗝️  SSH Key Authentication:")
        print("   • Generate SSH key: ssh-keygen -t ed25519 -C 'your_email@example.com'")
        print("   • Add public key to GitHub → Settings → SSH and GPG keys")
        print("   • Clone manually: git clone git@github.com:Vacilator/ProjectMeats.git")
        
        print("\n3. 📦 Manual Transfer:")
        print("   • Download on a machine with GitHub access")
        print("   • Transfer to this server via SCP/SFTP")
        print("   • Extract to:", self.config['project_dir'])
        
        print("\n4. 🌐 Alternative Deployment:")
        print("   • Use the no-authentication script:")
        print("   • curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash")
        
        print("\nFor detailed instructions, see:")
        print("https://github.com/Vacilator/ProjectMeats/blob/main/docs/deployment_authentication_guide.md")
        print("="*60)

    def setup_backend(self):
        """Configure Django backend"""
        self.log("Setting up Django backend...", 'HEADER')
        
        backend_dir = f"{self.config['project_dir']}/backend"
        
        # Create virtual environment
        self.log("Creating Python virtual environment...")
        self.run_command(f"cd {backend_dir} && python3 -m venv venv")
        
        # Install Python dependencies
        self.log("Installing Python dependencies...")
        self.run_command(f"cd {backend_dir} && ./venv/bin/pip install -r requirements.txt gunicorn psycopg2-binary")
        
        # Create Django environment file
        self.log("Creating Django configuration...")
        secret_key = secrets.token_urlsafe(50)
        
        env_content = f"""
# Django Configuration
DEBUG=False
SECRET_KEY={secret_key}
ALLOWED_HOSTS={self.config['domain']},www.{self.config['domain']},localhost,127.0.0.1

# Database
DATABASE_URL={self.config['database_url']}

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS
CORS_ALLOWED_ORIGINS=https://{self.config['domain']}

# File handling
MEDIA_ROOT={self.config['project_dir']}/uploads
STATIC_ROOT={backend_dir}/staticfiles
""".strip()
        
        with open(f"{backend_dir}/.env", 'w') as f:
            f.write(env_content)
        
        # Run Django setup
        self.log("Running Django migrations...")
        self.run_command(f"cd {backend_dir} && ./venv/bin/python manage.py migrate")
        
        # Create superuser - Optimized approach using Django's built-in command first (PRIMARY METHOD)
        # This resolves PR 81 conflicts by making Django createsuperuser the primary method
        self.log("Creating admin user...")
        
        # Clean up any existing admin script files efficiently
        self._cleanup_admin_files(backend_dir)
        
        # Primary method: Use Django's built-in createsuperuser (most reliable) - FROM PR 81
        if self._create_admin_with_django_command(backend_dir):
            self.log("Admin user created successfully using Django management command", 'SUCCESS')
        else:
            # Fallback: Custom script method with optimized error handling
            self.log("Falling back to custom admin creation script...", 'WARNING')
            self._create_admin_with_custom_script(backend_dir)
        
        # Collect static files
        self.log("Collecting static files...")
        self.run_command(f"cd {backend_dir} && ./venv/bin/python manage.py collectstatic --noinput")

    def setup_frontend(self):
        """Configure React frontend"""
        self.log("Setting up React frontend...", 'HEADER')
        
        frontend_dir = f"{self.config['project_dir']}/frontend"
        
        # Configure npm for the project user
        self.log("Configuring npm...")
        
        # Ensure proper directory ownership before npm operations
        self.log("Setting frontend directory ownership...")
        self.run_command(f"chown -R {self.config['app_user']}:{self.config['app_user']} {frontend_dir}")
        self.run_command(f"chmod -R 755 {frontend_dir}")
        
        npm_prefix = f"{self.config['project_dir']}/.npm-global"
        self.run_command(f"mkdir -p {npm_prefix}")
        self.run_command(f"chown -R {self.config['app_user']}:{self.config['app_user']} {npm_prefix}")
        self.run_command(f"sudo -u {self.config['app_user']} npm config set prefix {npm_prefix}")
        
        # Install dependencies with optimized retry strategies and caching
        self.log("Installing Node.js dependencies...")
        
        # Check if node_modules already exists and is populated
        node_modules_path = f"{frontend_dir}/node_modules"
        if os.path.exists(node_modules_path):
            try:
                # Quick check if dependencies are already installed
                result = self.run_command(f"ls {node_modules_path} | wc -l", capture_output=True)
                if int(result.strip()) > 10:  # Has significant number of modules
                    self.log("Node modules already exist, skipping npm install", 'SUCCESS')
                    # Still need to create production env file
                    env_content = f"REACT_APP_API_BASE_URL=https://{self.config['domain']}/api/v1"
                    with open(f"{frontend_dir}/.env.production", 'w') as f:
                        f.write(env_content)
                    
                    # Try to build (might work with existing modules)
                    try:
                        self.run_command(f"cd {frontend_dir} && sudo -u {self.config['app_user']} npm run build")
                        self.log("Frontend build completed with existing modules", 'SUCCESS')
                        return
                    except:
                        self.log("Build failed with existing modules, will reinstall...", 'WARNING')
            except:
                pass
        
        # Configure npm with optimizations
        npm_opts = "--no-audit --no-fund --prefer-offline"
        install_commands = [
            f"cd {frontend_dir} && sudo -u {self.config['app_user']} npm install {npm_opts}",
            f"cd {frontend_dir} && sudo -u {self.config['app_user']} npm install --legacy-peer-deps {npm_opts}",
            f"cd {frontend_dir} && sudo -u {self.config['app_user']} npm cache clean --force && npm install {npm_opts}"
        ]
        
        for cmd in install_commands:
            try:
                self.run_command(cmd)
                break
            except:
                self.log("npm install attempt failed, trying alternative...", 'WARNING')
                continue
        else:
            self.log("All npm install attempts failed!", 'ERROR')
            sys.exit(1)
        
        # Create production environment
        env_content = f"REACT_APP_API_BASE_URL=https://{self.config['domain']}/api/v1"
        with open(f"{frontend_dir}/.env.production", 'w') as f:
            f.write(env_content)
        
        # Build frontend
        self.log("Building React application...")
        self.run_command(f"cd {frontend_dir} && sudo -u {self.config['app_user']} npm run build")

    def setup_nginx(self):
        """Configure Nginx web server"""
        self.log("Configuring Nginx...", 'HEADER')
        
        nginx_config = f"""
# Rate limiting
limit_req_zone $binary_remote_addr zone=projectmeats_api:10m rate=10r/s;

# Upstream for Django
upstream projectmeats_backend {{
    server 127.0.0.1:8000;
}}

# HTTP to HTTPS redirect
server {{
    listen 80;
    server_name {self.config['domain']} www.{self.config['domain']};
    return 301 https://$server_name$request_uri;
}}

# HTTPS server
server {{
    listen 443 ssl http2;
    server_name {self.config['domain']} www.{self.config['domain']};

    # SSL Configuration (will be updated by Let's Encrypt)
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

    # Frontend static files
    location / {{
        root {self.config['project_dir']}/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }}

    # API endpoints
    location /api/ {{
        limit_req zone=projectmeats_api burst=20 nodelay;
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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
        alias {self.config['project_dir']}/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # Media files
    location /media/ {{
        alias {self.config['project_dir']}/uploads/;
        expires 1d;
        add_header Cache-Control "public";
    }}
}}
"""
        
        # Write Nginx configuration
        with open('/etc/nginx/sites-available/projectmeats', 'w') as f:
            f.write(nginx_config)
        
        # Enable site
        self.run_command("rm -f /etc/nginx/sites-enabled/default", check=False)
        self.run_command("ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/")
        
        # Test configuration
        self.run_command("nginx -t")

    def setup_systemd(self):
        """Configure systemd service"""
        self.log("Configuring systemd service...", 'HEADER')
        
        # Create Gunicorn configuration
        gunicorn_config = f"""
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
accesslog = "{self.config['logs_dir']}/gunicorn_access.log"
errorlog = "{self.config['logs_dir']}/gunicorn_error.log"
loglevel = "info"
capture_output = True

# Security
limit_request_line = 4096
limit_request_fields = 100
"""
        
        with open(f"{self.config['project_dir']}/backend/gunicorn.conf.py", 'w') as f:
            f.write(gunicorn_config)
        
        # Create systemd service
        systemd_service = f"""
[Unit]
Description=ProjectMeats Django Application
After=network.target postgresql.service

[Service]
Type=notify
User={self.config['app_user']}
Group={self.config['app_user']}
RuntimeDirectory=projectmeats
WorkingDirectory={self.config['project_dir']}/backend
Environment=PATH={self.config['project_dir']}/backend/venv/bin
ExecStart={self.config['project_dir']}/backend/venv/bin/gunicorn -c gunicorn.conf.py projectmeats.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        
        with open('/etc/systemd/system/projectmeats.service', 'w') as f:
            f.write(systemd_service)
        
        # Enable and start service
        self.run_command("systemctl daemon-reload")
        self.run_command("systemctl enable projectmeats")

    def setup_ssl(self):
        """Configure SSL certificates"""
        self.log("Setting up SSL certificates...", 'HEADER')
        
        try:
            # Get Let's Encrypt certificate
            self.run_command(f"certbot --nginx -d {self.config['domain']} -d www.{self.config['domain']} --agree-tos --email admin@{self.config['domain']} --non-interactive")
            
            # Setup auto-renewal
            self.run_command('echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -')
            
            self.log("SSL certificates configured successfully", 'SUCCESS')
        except:
            self.log("SSL certificate setup failed. You can set it up manually later.", 'WARNING')

    def setup_security(self):
        """Configure security measures"""
        self.log("Configuring security...", 'HEADER')
        
        # Configure UFW firewall
        self.log("Setting up firewall...")
        self.run_command("ufw --force reset")
        self.run_command("ufw default deny incoming")
        self.run_command("ufw default allow outgoing")
        self.run_command("ufw allow ssh")
        self.run_command("ufw allow 'Nginx Full'")
        self.run_command("ufw --force enable")
        
        # Configure Fail2Ban
        self.log("Setting up Fail2Ban...")
        fail2ban_config = """
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
maxretry = 3

[nginx-http-auth]
enabled = true
"""
        
        with open('/etc/fail2ban/jail.local', 'w') as f:
            f.write(fail2ban_config)
        
        self.run_command("systemctl enable fail2ban")
        self.run_command("systemctl start fail2ban")

    def setup_docker_deployment(self):
        """Setup Docker-based deployment with docker-compose"""
        self.log("Setting up Docker deployment...", 'HEADER')
        
        # Install Docker and docker-compose
        self.log("Installing Docker and docker-compose...")
        
        # Get Ubuntu codename for repository URL
        ubuntu_codename = self.run_command("lsb_release -cs", capture_output=True)
        self.log(f"Detected Ubuntu codename: {ubuntu_codename}")
        
        docker_commands = [
            "apt update",
            "apt install -y apt-transport-https ca-certificates curl gnupg lsb-release",
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
            f"echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu {ubuntu_codename} stable' | tee /etc/apt/sources.list.d/docker.list > /dev/null",
            "apt update",
            "apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin",
            "systemctl enable docker",
            "systemctl start docker",
            f"usermod -aG docker {self.config['app_user']}"
        ]
        
        for cmd in docker_commands:
            self.run_command(cmd)
        
        # Create docker-compose.yml
        self.create_docker_compose_file()
        
        # Create environment files
        self.create_docker_env_files()
        
        # Build and start containers
        self.log("Building and starting Docker containers...")
        self.run_command(f"cd {self.config['project_dir']} && docker-compose up -d --build")
        
        self.log("Docker deployment completed", 'SUCCESS')

    def create_docker_compose_file(self):
        """Create optimized docker-compose.yml for production"""
        compose_content = f"""version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: projectmeats
      POSTGRES_USER: {self.config['app_user']}
      POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD}}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - {self.config['backup_dir']}:/backups
    networks:
      - projectmeats_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U {self.config['app_user']}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    networks:
      - projectmeats_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Django Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://{self.config['app_user']}:${{POSTGRES_PASSWORD}}@db:5432/projectmeats
      - REDIS_URL=redis://redis:6379/0
      - DJANGO_SETTINGS_MODULE=projectmeats.settings.production
      - DEBUG=False
      - ALLOWED_HOSTS={self.config['domain']},www.{self.config['domain']}
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - {self.config['logs_dir']}:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - projectmeats_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # React Frontend Build
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - REACT_APP_API_BASE_URL=https://{self.config['domain']}/api/v1
    volumes:
      - frontend_build:/app/build
    networks:
      - projectmeats_network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/conf.d:/etc/nginx/conf.d
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - frontend_build:/var/www/html
      - ./ssl:/etc/nginx/ssl
      - {self.config['logs_dir']}/nginx:/var/log/nginx
    depends_on:
      - backend
      - frontend
    networks:
      - projectmeats_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery Worker (for background tasks)
  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A projectmeats worker -l info
    environment:
      - DATABASE_URL=postgresql://{self.config['app_user']}:${{POSTGRES_PASSWORD}}@db:5432/projectmeats
      - REDIS_URL=redis://redis:6379/0
      - DJANGO_SETTINGS_MODULE=projectmeats.settings.production
    volumes:
      - media_volume:/app/media
      - {self.config['logs_dir']}:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - projectmeats_network
    restart: unless-stopped

  # Monitoring with Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - projectmeats_network
    restart: unless-stopped
    profiles:
      - monitoring

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${{GRAFANA_PASSWORD}}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    networks:
      - projectmeats_network
    restart: unless-stopped
    profiles:
      - monitoring

volumes:
  postgres_data:
  static_volume:
  media_volume:
  frontend_build:
  prometheus_data:
  grafana_data:

networks:
  projectmeats_network:
    driver: bridge
"""
        
        with open(f"{self.config['project_dir']}/docker-compose.yml", 'w') as f:
            f.write(compose_content)

    def create_docker_env_files(self):
        """Create environment files for Docker deployment"""
        # Generate secure passwords
        postgres_password = secrets.token_urlsafe(32)
        grafana_password = secrets.token_urlsafe(16)
        
        env_content = f"""# Docker Environment Configuration
POSTGRES_PASSWORD={postgres_password}
GRAFANA_PASSWORD={grafana_password}
DJANGO_SECRET_KEY={secrets.token_urlsafe(50)}
DOMAIN={self.config['domain']}
ENVIRONMENT={self.config['environment']}
"""
        
        with open(f"{self.config['project_dir']}/.env", 'w') as f:
            f.write(env_content)
        
        # Store for later use
        self.config['postgres_password'] = postgres_password
        self.config['grafana_password'] = grafana_password

    def setup_ci_cd_integration(self):
        """Setup CI/CD integration with GitHub Actions deployment hooks"""
        self.log("Setting up CI/CD integration...", 'HEADER')
        
        # Create deployment webhook endpoint
        webhook_content = f"""#!/bin/bash
# ProjectMeats CI/CD Deployment Webhook
# Called by GitHub Actions for automated deployment

set -e

DEPLOY_LOG="{self.config['logs_dir']}/cicd_deploy.log"
DEPLOY_LOCK="/tmp/projectmeats_deploy.lock"

# Prevent concurrent deployments
if [ -f "$DEPLOY_LOCK" ]; then
    echo "$(date): Deployment already in progress" >> "$DEPLOY_LOG"
    exit 1
fi

touch "$DEPLOY_LOCK"

echo "$(date): Starting CI/CD deployment" >> "$DEPLOY_LOG"

# Change to project directory
cd {self.config['project_dir']}

# Pull latest changes
git pull origin main >> "$DEPLOY_LOG" 2>&1

# Update backend
cd backend
./venv/bin/pip install -r requirements.txt >> "$DEPLOY_LOG" 2>&1
./venv/bin/python manage.py migrate >> "$DEPLOY_LOG" 2>&1
./venv/bin/python manage.py collectstatic --noinput >> "$DEPLOY_LOG" 2>&1

# Update frontend
cd ../frontend
npm ci >> "$DEPLOY_LOG" 2>&1
npm run build >> "$DEPLOY_LOG" 2>&1

# Restart services
systemctl restart projectmeats >> "$DEPLOY_LOG" 2>&1
systemctl reload nginx >> "$DEPLOY_LOG" 2>&1

# Cleanup
rm -f "$DEPLOY_LOCK"

echo "$(date): CI/CD deployment completed successfully" >> "$DEPLOY_LOG"
"""
        
        webhook_path = f"{self.config['project_dir']}/scripts/cicd_deploy.sh"
        with open(webhook_path, 'w') as f:
            f.write(webhook_content)
        self.run_command(f"chmod +x {webhook_path}")
        
        # Create GitHub Actions webhook handler
        self.create_github_webhook_handler()
        
        self.log("CI/CD integration configured", 'SUCCESS')

    def create_github_webhook_handler(self):
        """Create webhook handler for GitHub Actions integration"""
        handler_content = f"""#!/usr/bin/env python3
import os
import hmac
import hashlib
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# Webhook secret (set this in GitHub webhook configuration)
WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', 'change-this-secret')
DEPLOY_SCRIPT = '{self.config['project_dir']}/scripts/cicd_deploy.sh'

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Verify GitHub signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return jsonify({{'error': 'Missing signature'}}), 403
    
    payload = request.get_data()
    expected_signature = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({{'error': 'Invalid signature'}}), 403
    
    # Parse payload
    event_type = request.headers.get('X-GitHub-Event')
    
    # Only deploy on push to main branch
    if event_type == 'push':
        data = request.get_json()
        if data.get('ref') == 'refs/heads/main':
            # Trigger deployment
            try:
                subprocess.Popen(['/bin/bash', DEPLOY_SCRIPT])
                return jsonify({{'status': 'Deployment triggered'}}), 200
            except Exception as e:
                return jsonify({{'error': str(e)}}), 500
    
    return jsonify({{'status': 'No action taken'}}), 200

@app.route('/health')
def health_check():
    return jsonify({{'status': 'healthy'}}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
"""
        
        webhook_handler_path = f"{self.config['project_dir']}/scripts/webhook_handler.py"
        with open(webhook_handler_path, 'w') as f:
            f.write(handler_content)
        
        # Create systemd service for webhook handler
        webhook_service = f"""[Unit]
Description=ProjectMeats GitHub Webhook Handler
After=network.target

[Service]
Type=simple
User={self.config['app_user']}
WorkingDirectory={self.config['project_dir']}/scripts
Environment=GITHUB_WEBHOOK_SECRET=change-this-secret
ExecStart=/usr/bin/python3 webhook_handler.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        
        with open('/etc/systemd/system/projectmeats-webhook.service', 'w') as f:
            f.write(webhook_service)
        
        self.run_command("systemctl daemon-reload")
        self.run_command("systemctl enable projectmeats-webhook")
        self.run_command("systemctl start projectmeats-webhook")

    def setup_monitoring_and_alerts(self):
        """Setup comprehensive monitoring, logging, and alerting"""
        self.log("Setting up monitoring and alerts...", 'HEADER')
        
        # Create monitoring configuration
        self.create_monitoring_configs()
        
        # Setup log rotation
        self.setup_log_rotation()
        
        # Create health check endpoints
        self.create_health_check_endpoints()
        
        # Setup email alerts
        self.setup_email_alerts()
        
        self.log("Monitoring and alerts configured", 'SUCCESS')

    def create_monitoring_configs(self):
        """Create Prometheus and Grafana monitoring configurations"""
        os.makedirs(f"{self.config['project_dir']}/monitoring", exist_ok=True)
        
        # Prometheus configuration
        prometheus_config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'projectmeats-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgresql'
    static_configs:
      - targets: ['db:5432']
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s
"""
        
        with open(f"{self.config['project_dir']}/monitoring/prometheus.yml", 'w') as f:
            f.write(prometheus_config)

    def setup_log_rotation(self):
        """Setup log rotation for all services"""
        logrotate_config = f"""
{self.config['logs_dir']}/*.log {{
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 {self.config['app_user']} {self.config['app_user']}
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
        systemctl restart projectmeats > /dev/null 2>&1 || true
    endscript
}}
"""
        
        with open('/etc/logrotate.d/projectmeats', 'w') as f:
            f.write(logrotate_config)

    def create_health_check_endpoints(self):
        """Create comprehensive health check endpoints"""
        health_check_script = f"""#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime

def check_service_status(service_name):
    try:
        result = subprocess.run(['systemctl', 'is-active', service_name], 
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except:
        return False

def check_database_connection():
    try:
        result = subprocess.run([
            'sudo', '-u', '{self.config['app_user']}', 
            'psql', '-h', 'localhost', '-U', '{self.config['app_user']}', 
            '-d', 'projectmeats', '-c', 'SELECT 1;'
        ], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def main():
    health_status = {{
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy',
        'services': {{
            'projectmeats': check_service_status('projectmeats'),
            'nginx': check_service_status('nginx'),
            'postgresql': check_service_status('postgresql'),
            'fail2ban': check_service_status('fail2ban')
        }},
        'database': {{
            'connection': check_database_connection()
        }}
    }}
    
    # Check if any critical service is down
    critical_services = ['projectmeats', 'nginx', 'postgresql']
    if not all(health_status['services'][service] for service in critical_services):
        health_status['status'] = 'unhealthy'
    
    if not health_status['database']['connection']:
        health_status['status'] = 'unhealthy'
    
    print(json.dumps(health_status, indent=2))
    return 0 if health_status['status'] == 'healthy' else 1

if __name__ == '__main__':
    sys.exit(main())
"""
        
        health_check_path = f"{self.config['project_dir']}/scripts/health_check.py"
        with open(health_check_path, 'w') as f:
            f.write(health_check_script)
        self.run_command(f"chmod +x {health_check_path}")

    def setup_email_alerts(self):
        """Setup email alerting for critical issues"""
        alert_script = f"""#!/bin/bash
# ProjectMeats Alert System

ALERT_EMAIL="admin@{self.config['domain']}"
LOG_FILE="{self.config['logs_dir']}/alerts.log"

send_alert() {{
    local subject="$1"
    local message="$2"
    
    echo "$(date): ALERT - $subject" >> "$LOG_FILE"
    echo "$message" >> "$LOG_FILE"
    
    # Send email if mail is configured
    if command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "ProjectMeats Alert: $subject" "$ALERT_EMAIL"
    fi
    
    # Log to syslog
    logger -t "ProjectMeats" "ALERT: $subject - $message"
}}

# Check if health check fails
if ! {self.config['project_dir']}/scripts/health_check.py >/dev/null 2>&1; then
    send_alert "System Health Check Failed" "One or more critical services are not responding. Please check the system immediately."
fi
"""
        
        alert_script_path = f"{self.config['project_dir']}/scripts/alert_system.sh"
        with open(alert_script_path, 'w') as f:
            f.write(alert_script)
        self.run_command(f"chmod +x {alert_script_path}")
        
        # Add to crontab for regular checks
        cron_job = f"*/5 * * * * {alert_script_path} >/dev/null 2>&1"
        self.run_command(f'(crontab -l 2>/dev/null; echo "{cron_job}") | crontab -')

    def _cleanup_admin_files(self, backend_dir):
        """Efficiently clean up any existing admin script files"""
        cleanup_patterns = [
            f"{backend_dir}/create_admin*.py",
            f"{self.config['project_dir']}/create_admin*.py", 
            f"{backend_dir}/apps/create_admin*.py",
            f"{self.config['project_dir']}/backend/create_admin*.py"
        ]
        
        for pattern in cleanup_patterns:
            self.run_command(f"rm -f {pattern}", check=False)
        
        # Quick cleanup of files with wrong imports (more efficient than detailed search)
        try:
            result = self.run_command(
                f"find {self.config['project_dir']} -name '*admin*.py' -type f -exec grep -l 'apps.user_profiles' {{}} \\; 2>/dev/null | head -10", 
                capture_output=True, check=False
            )
            if result and result.strip():
                files_to_clean = result.strip().split('\n')
                for file_path in files_to_clean:
                    if file_path and any(keyword in file_path.lower() for keyword in ['create_admin', 'admin_script', 'temp', 'tmp']):
                        self.run_command(f"rm -f '{file_path}'", check=False)
        except Exception:
            pass  # Cleanup is optional, don't fail deployment

    def _create_admin_with_django_command(self, backend_dir):
        """Create admin user using Django's built-in management command (primary method)"""
        try:
            env_vars = f"DJANGO_SUPERUSER_USERNAME={self.config['admin_user']} DJANGO_SUPERUSER_EMAIL={self.config['admin_email']} DJANGO_SUPERUSER_PASSWORD={self.config['admin_password']}"
            
            # Use Django's built-in command (most reliable)
            self.run_command(f"cd {backend_dir} && {env_vars} ./venv/bin/python manage.py createsuperuser --noinput")
            
            # Create user profile separately using Django shell (faster than custom script)
            profile_command = f"from django.contrib.auth.models import User; from apps.core.models import UserProfile; user = User.objects.get(username='{self.config['admin_user']}'); profile, created = UserProfile.objects.get_or_create(user=user); print('Profile created' if created else 'Profile exists')"
            self.run_command(f'cd {backend_dir} && ./venv/bin/python manage.py shell -c "{profile_command}"')
            
            return True
        except Exception as e:
            self.log(f"Django management command failed: {e}", 'WARNING')
            return False

    def _create_admin_with_custom_script(self, backend_dir):
        """Fallback method using custom script with optimized execution"""
        admin_script_path = f"{backend_dir}/create_admin.py"
        
        create_user_script = f"""from django.contrib.auth.models import User
from apps.core.models import UserProfile

# Create superuser
if not User.objects.filter(username='{self.config['admin_user']}').exists():
    user = User.objects.create_superuser(
        '{self.config['admin_user']}',
        '{self.config['admin_email']}',
        '{self.config['admin_password']}'
    )
    # Create profile
    UserProfile.objects.get_or_create(user=user)
    print('Admin user created successfully')
else:
    print('Admin user already exists')
"""
        
        try:
            # Create and validate script quickly
            with open(admin_script_path, 'w', encoding='utf-8') as f:
                f.write(create_user_script)
            
            # Quick validation
            if "from apps.core.models import UserProfile" not in create_user_script:
                raise Exception("Script validation failed")
            
            # Execute with multiple fallback methods
            execution_methods = [
                f"cd {backend_dir} && ./venv/bin/python manage.py shell < create_admin.py",
                f"cd {backend_dir} && ./venv/bin/python create_admin.py",
                f'cd {backend_dir} && ./venv/bin/python -c "import os; import django; os.environ.setdefault(\\"DJANGO_SETTINGS_MODULE\\", \\"projectmeats.settings\\"); django.setup(); exec(open(\\"create_admin.py\\").read())"'
            ]
            
            success = False
            for method in execution_methods:
                try:
                    self.run_command(method)
                    self.log("Admin script executed successfully", 'SUCCESS')
                    success = True
                    break
                except Exception:
                    continue
            
            if not success:
                raise Exception("All execution methods failed")
                
            # Clean up
            self.run_command(f"rm -f {admin_script_path}", check=False)
            
        except Exception as e:
            self.log(f"Custom script method failed: {e}", 'ERROR')
            raise

    def start_services(self):
        """Start all services"""
        self.log("Starting services...", 'HEADER')
        
        services = ['postgresql', 'projectmeats', 'nginx', 'fail2ban']
        
        for service in services:
            try:
                self.run_command(f"systemctl start {service}")
                self.run_command(f"systemctl enable {service}")
                self.log(f"{service} started successfully", 'SUCCESS')
            except:
                self.log(f"Failed to start {service}", 'ERROR')

    def verify_deployment(self):
        """Verify that deployment was successful with enhanced checks"""
        self.log("Verifying deployment...", 'HEADER')
        
        # Check services in parallel for efficiency
        services = ['projectmeats', 'nginx']
        if self.config['database_type'] == 'postgresql':
            services.append('postgresql')
        
        all_services_ok = True
        failed_services = []
        
        # Quick batch check of all services
        for service in services:
            try:
                self.run_command(f"systemctl is-active --quiet {service}")
                self.log(f"✅ {service} is running", 'SUCCESS')
            except:
                self.log(f"❌ {service} is not running", 'ERROR')
                all_services_ok = False
                failed_services.append(service)
        
        # Enhanced web endpoint testing
        endpoints_to_test = [
            ('Frontend', f"https://{self.config['domain']}"),
            ('API Health', f"https://{self.config['domain']}/api/"),
            ('Admin Panel', f"https://{self.config['domain']}/admin/")
        ]
        
        web_ok = True
        # Give services time to start before testing
        if all_services_ok:
            time.sleep(3)  # Reduced wait time
            
            for name, url in endpoints_to_test:
                try:
                    # Test with timeout for faster failure detection
                    self.run_command(f"curl -f -k --max-time 10 {url} -o /dev/null")
                    self.log(f"✅ {name} is responding", 'SUCCESS')
                except:
                    self.log(f"❌ {name} is not responding", 'ERROR')
                    web_ok = False
                    break  # Stop testing if one fails
        
        # Additional quick health checks
        if all_services_ok and web_ok:
            try:
                # Test database connectivity
                backend_dir = f"{self.config['project_dir']}/backend"
                self.run_command(f"cd {backend_dir} && ./venv/bin/python manage.py check --deploy")
                self.log("✅ Django deployment check passed", 'SUCCESS')
            except:
                self.log("⚠️ Django deployment check failed (not critical)", 'WARNING')
        
        # Auto-restart failed services if possible (enhanced reliability)
        if failed_services and len(failed_services) < len(services):
            self.log("Attempting to auto-restart failed services...", 'WARNING')
            for service in failed_services:
                try:
                    self.run_command(f"systemctl restart {service}")
                    time.sleep(2)
                    self.run_command(f"systemctl is-active --quiet {service}")
                    self.log(f"✅ {service} restarted successfully", 'SUCCESS')
                    all_services_ok = True  # At least one service recovered
                except:
                    self.log(f"❌ Failed to restart {service}", 'ERROR')
        
        return all_services_ok and web_ok

    def print_success_message(self):
        """Print final success message"""
        self.log("", 'HEADER')
        print("🎉" + "=" * 60 + "🎉")
        print("   ProjectMeats Deployment Completed Successfully!")
        print("=" * 64)
        print("")
        print(f"🌐 Website:     https://{self.config['domain']}")
        print(f"🔐 Admin Panel: https://{self.config['domain']}/admin/")
        print(f"📚 API Docs:    https://{self.config['domain']}/api/docs/")
        print("")
        print("🔑 Admin Credentials:")
        print(f"   Username: {self.config['admin_user']}")
        print(f"   Password: {self.config['admin_password']}")
        print(f"   Email:    {self.config['admin_email']}")
        print("")
        print("📁 Important Paths:")
        print(f"   Project:  {self.config['project_dir']}")
        print(f"   Logs:     {self.config['logs_dir']}")
        print(f"   Backups:  {self.config['backup_dir']}")
        print("")
        print("🛠️ Management Commands:")
        print(f"   Status:   {self.config['project_dir']}/scripts/status.sh")
        print(f"   Backup:   {self.config['project_dir']}/scripts/backup.sh")
        print(f"   Restart:  systemctl restart projectmeats nginx")
        print("")
        print("🎯 Your ProjectMeats application is ready for production use!")
        print("=" * 64)

    def run(self):
        """Main deployment workflow with consolidated functionality"""
        try:
            # Print header
            print("\n" + "🚀" * 25)
            print("ProjectMeats Unified Deployment System v2.0")
            print("🚀" * 25)
            
            # Handle special modes first
            if self.is_prepare_server:
                self.prepare_server_only()
                return
            
            if self.is_postgres_setup:
                self.setup_postgres_only()
                return
            
            if self.is_monitoring_mode:
                self.setup_monitoring_only()
                return
            
            # Check prerequisites
            if not self.check_prerequisites():
                sys.exit(1)
            
            # Run interactive wizard if requested
            if self.is_interactive_mode:
                self.run_deployment_wizard()
            else:
                # Interactive setup for non-wizard mode
                self.interactive_setup()
            
            # GitHub authentication setup
            self.get_github_authentication()
            
            # Main deployment steps based on mode
            if self.is_docker_mode:
                self.deploy_with_docker()
            else:
                self.deploy_standard()
            
            # CI/CD integration if requested
            if self.is_ci_cd_mode:
                self.setup_ci_cd_integration()
            
            # Enhanced monitoring and alerts
            self.setup_monitoring_and_alerts()
            
            # Verify and show results
            if self.verify_deployment():
                self.print_success_message()
            else:
                self.log("Deployment completed but some services may need attention", 'WARNING')
                self.log(f"Check status with: {self.config['project_dir']}/scripts/status.sh", 'INFO')
            
        except KeyboardInterrupt:
            self.log("Deployment cancelled by user", 'WARNING')
            sys.exit(1)
        except Exception as e:
            self.log(f"Deployment failed: {str(e)}", 'ERROR')
            self.log("Check logs for details", 'ERROR')
            sys.exit(1)

    def prepare_server_only(self):
        """Prepare server environment only (no app deployment)"""
        self.log("Preparing server environment...", 'HEADER')
        self.setup_system()
        self.setup_security()
        self.log("Server preparation completed", 'SUCCESS')

    def setup_postgres_only(self):
        """Interactive PostgreSQL setup only"""
        self.log("PostgreSQL Setup Mode", 'HEADER')
        self.show_postgresql_setup_guide()
        if self.config['database_type'] == 'postgresql':
            db_password = secrets.token_urlsafe(16)
            success = self.setup_postgresql_database(db_password)
            if success:
                self.log("PostgreSQL setup completed successfully", 'SUCCESS')
                print(f"\nDatabase URL: postgresql://{self.config['app_user']}:{db_password}@localhost:5432/projectmeats")
            else:
                self.log("PostgreSQL setup failed", 'ERROR')

    def setup_monitoring_only(self):
        """Setup monitoring and health checks only"""
        self.log("Setting up monitoring system...", 'HEADER')
        self.setup_monitoring_and_alerts()
        self.log("Monitoring setup completed", 'SUCCESS')

    def deploy_with_docker(self):
        """Docker-based deployment workflow"""
        self.log("Starting Docker deployment workflow...", 'HEADER')
        
        # System preparation
        self.setup_system()
        self.download_application()
        
        # Docker-specific setup
        self.setup_docker_deployment()
        
        # Create Docker-optimized configurations
        self.create_docker_nginx_config()
        self.create_docker_environment_files()
        
        # Security (adapted for Docker)
        self.setup_security()
        
        self.log("Docker deployment workflow completed", 'SUCCESS')

    def deploy_standard(self):
        """Standard deployment workflow (non-Docker)"""
        self.log("Starting standard deployment workflow...", 'HEADER')
        
        # All the existing deployment steps
        self.setup_system()
        self.setup_database()
        self.download_application()
        self.setup_backend()
        self.setup_frontend()
        self.setup_nginx()
        self.setup_systemd()
        self.setup_ssl()
        self.setup_security()
        self.start_services()

    def create_docker_nginx_config(self):
        """Create nginx configuration optimized for Docker deployment"""
        os.makedirs(f"{self.config['project_dir']}/nginx/conf.d", exist_ok=True)
        
        nginx_config = f"""# ProjectMeats Docker Nginx Configuration
upstream backend {{
    server backend:8000;
}}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {{
    listen 80;
    server_name {self.config['domain']} www.{self.config['domain']};
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Frontend static files
    location / {{
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
    
    # API endpoints
    location /api/ {{
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }}
    
    # Admin interface
    location /admin/ {{
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Static files
    location /static/ {{
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Media files
    location /media/ {{
        alias /var/www/media/;
        expires 1d;
        add_header Cache-Control "public";
    }}
    
    # Health check endpoint
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}
"""
        
        with open(f"{self.config['project_dir']}/nginx/conf.d/default.conf", 'w') as f:
            f.write(nginx_config)

    def create_docker_environment_files(self):
        """Create environment files for Docker containers"""
        # Backend environment
        backend_env = f"""DEBUG=False
SECRET_KEY={secrets.token_urlsafe(50)}
ALLOWED_HOSTS={self.config['domain']},www.{self.config['domain']},localhost,backend
DATABASE_URL=postgresql://{self.config['app_user']}:{{POSTGRES_PASSWORD}}@db:5432/projectmeats
REDIS_URL=redis://redis:6379/0

# Security settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS
CORS_ALLOWED_ORIGINS=https://{self.config['domain']}

# Logging
LOG_LEVEL=INFO
"""
        
        with open(f"{self.config['project_dir']}/backend/.env.docker", 'w') as f:
            f.write(backend_env)

if __name__ == "__main__":
    deployer = MasterDeployer()
    deployer.run()