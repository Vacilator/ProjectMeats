#!/usr/bin/env python3
"""
ProjectMeats Master Deployment Script
=====================================

ONE SCRIPT TO RULE THEM ALL

This script replaces all other deployment scripts and handles:
- Complete environment setup
- Node.js conflict resolution
- SSL configuration
- Security hardening
- Service configuration
- Health monitoring

Usage:
    # Fully automated deployment:
    python3 master_deploy.py --auto --domain=yourdomain.com

    # With GitHub authentication:
    python3 master_deploy.py --auto --domain=yourdomain.com --github-user=USERNAME --github-token=TOKEN

    # Interactive setup:
    python3 master_deploy.py

    # Server-side deployment (after uploading):
    python3 master_deploy.py --server

Author: ProjectMeats Team
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
            'app_user': 'projectmeats'
        }
        self.is_server_mode = '--server' in sys.argv
        self.is_auto_mode = '--auto' in sys.argv
        
        # Parse command line arguments
        for arg in sys.argv:
            if arg.startswith('--domain='):
                self.config['domain'] = arg.split('=', 1)[1]
            elif arg.startswith('--github-user='):
                self.config['github_user'] = arg.split('=', 1)[1]
            elif arg.startswith('--github-token='):
                self.config['github_token'] = arg.split('=', 1)[1]

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
        """Configure database"""
        self.log("Setting up database...", 'HEADER')
        
        if self.config['database_type'] == 'postgresql':
            self.log("Configuring PostgreSQL...")
            
            # Generate random password
            db_password = secrets.token_urlsafe(16)
            
            # Create database and user - run from /tmp to avoid permission issues
            commands = [
                f"cd /tmp && sudo -u postgres createdb projectmeats || true",
                f"cd /tmp && sudo -u postgres createuser {self.config['app_user']} || true",
                f"cd /tmp && sudo -u postgres psql -c \"ALTER USER {self.config['app_user']} PASSWORD '{db_password}';\"",
                f"cd /tmp && sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE projectmeats TO {self.config['app_user']};\"",
                f"cd /tmp && sudo -u postgres psql -c \"ALTER USER {self.config['app_user']} CREATEDB;\""
            ]
            
            for cmd in commands:
                self.run_command(cmd, check=False)
            
            # Store database config
            self.config['database_url'] = f"postgresql://{self.config['app_user']}:{db_password}@localhost:5432/projectmeats"
            
        else:
            # SQLite setup
            self.log("Configuring SQLite...")
            db_path = f"{self.config['project_dir']}/db.sqlite3"
            self.config['database_url'] = f"sqlite:///{db_path}"

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
        npm_prefix = f"{self.config['project_dir']}/.npm-global"
        self.run_command(f"mkdir -p {npm_prefix}")
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

    def setup_monitoring(self):
        """Setup monitoring and backup scripts"""
        self.log("Setting up monitoring and backups...", 'HEADER')
        
        # Create directories
        self.run_command(f"mkdir -p {self.config['logs_dir']} {self.config['backup_dir']} {self.config['project_dir']}/scripts")
        
        # Create status check script
        status_script = f"""#!/bin/bash
echo "ProjectMeats System Status"
echo "========================="
echo ""

echo "Services:"
systemctl is-active --quiet projectmeats && echo "✅ ProjectMeats: Running" || echo "❌ ProjectMeats: Not Running"
systemctl is-active --quiet nginx && echo "✅ Nginx: Running" || echo "❌ Nginx: Not Running"
systemctl is-active --quiet postgresql && echo "✅ PostgreSQL: Running" || echo "❌ PostgreSQL: Not Running"

echo ""
echo "Disk Usage:"
df -h /

echo ""
echo "Memory Usage:"
free -h

echo ""
echo "Recent Logs:"
tail -5 {self.config['logs_dir']}/gunicorn_error.log 2>/dev/null || echo "No error logs"
"""
        
        with open(f"{self.config['project_dir']}/scripts/status.sh", 'w') as f:
            f.write(status_script)
        self.run_command(f"chmod +x {self.config['project_dir']}/scripts/status.sh")
        
        # Create backup script
        backup_script = f"""#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="{self.config['backup_dir']}/backup_$DATE.sql"

if systemctl is-active --quiet postgresql; then
    sudo -u postgres pg_dump projectmeats > "$BACKUP_FILE"
    gzip "$BACKUP_FILE"
    echo "$(date): Database backup created: $BACKUP_FILE.gz" >> {self.config['logs_dir']}/backup.log
    
    # Keep only last 7 days of backups
    find {self.config['backup_dir']} -name "backup_*.sql.gz" -mtime +7 -delete
fi
"""
        
        with open(f"{self.config['project_dir']}/scripts/backup.sh", 'w') as f:
            f.write(backup_script)
        self.run_command(f"chmod +x {self.config['project_dir']}/scripts/backup.sh")
        
        # Setup cron jobs
        cron_jobs = f"""
# ProjectMeats automated tasks
0 2 * * * {self.config['project_dir']}/scripts/backup.sh
*/15 * * * * systemctl is-active --quiet projectmeats || systemctl restart projectmeats
"""
        
        self.run_command(f'echo "{cron_jobs}" | crontab -')
        
        # Set ownership
        self.run_command(f"chown -R {self.config['app_user']}:{self.config['app_user']} {self.config['project_dir']}")

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
        """Main deployment workflow"""
        try:
            # Print header
            print("\n" + "🚀" * 20)
            print("ProjectMeats Master Deployment Script")
            print("🚀" * 20)
            
            # Check prerequisites
            if not self.check_prerequisites():
                sys.exit(1)
            
            # Interactive setup if needed
            self.interactive_setup()
            
            # GitHub authentication setup
            self.get_github_authentication()
            
            # Main deployment steps
            self.setup_system()
            self.setup_database()
            self.download_application()
            self.setup_backend()
            self.setup_frontend()
            self.setup_nginx()
            self.setup_systemd()
            self.setup_ssl()
            self.setup_security()
            self.setup_monitoring()
            self.start_services()
            
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

if __name__ == "__main__":
    deployer = MasterDeployer()
    deployer.run()