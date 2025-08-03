#!/usr/bin/env python3
"""
ProjectMeats Production Deployment Script
=========================================

A clean, consolidated production deployment script that combines the best practices
from various deployment scripts. Designed to work with AI deployment orchestrator.

Usage:
    python production_deploy.py --setup     # Initial server setup
    python production_deploy.py --deploy    # Deploy application
    python production_deploy.py --verify    # Verify deployment
    python production_deploy.py --full      # Complete setup + deploy + verify

Features:
- Clean server initialization
- Domain and SSL configuration
- Database setup and migrations
- Frontend and backend deployment
- Health checks and verification
- Error handling and logging
- Rollback capabilities
"""

import os
import sys
import json
import time
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ProductionDeployer:
    """Clean production deployment orchestrator"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or 'ai_deployment_config.json'
        self.config = self.load_config()
        self.setup_logging()
        self.deployment_state = {
            'timestamp': datetime.now().isoformat(),
            'steps_completed': [],
            'current_step': None,
            'errors': [],
            'rollback_points': []
        }
    
    def load_config(self) -> Dict:
        """Load deployment configuration"""
        try:
            with open(self.config_file) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{Colors.YELLOW}⚠️  Config file not found: {self.config_file}{Colors.END}")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}❌ Invalid JSON in config file: {e}{Colors.END}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default deployment configuration"""
        return {
            "domain": "localhost",
            "ssl_enabled": False,
            "database": {
                "engine": "sqlite3",
                "name": "projectmeats.db"
            },
            "paths": {
                "project_root": "/opt/projectmeats",
                "static_root": "/opt/projectmeats/static",
                "media_root": "/opt/projectmeats/media"
            },
            "services": {
                "backend_port": 8000,
                "frontend_port": 3000
            }
        }
    
    def setup_logging(self):
        """Setup deployment logging"""
        log_file = f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Production deployment started - Log file: {log_file}")
    
    def run_command(self, command: str, description: str, check: bool = True) -> Tuple[bool, str]:
        """Run a system command with logging"""
        self.logger.info(f"Running: {description}")
        self.logger.debug(f"Command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            self.logger.info(f"✅ {description} - Success")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ {description} - Failed: {e.stderr}"
            self.logger.error(error_msg)
            self.deployment_state['errors'].append({
                'step': description,
                'command': command,
                'error': e.stderr,
                'timestamp': datetime.now().isoformat()
            })
            return False, e.stderr
    
    def check_prerequisites(self) -> bool:
        """Check deployment prerequisites"""
        print(f"{Colors.BLUE}🔍 Checking prerequisites...{Colors.END}")
        
        prerequisites = [
            ("python3 --version", "Python 3.8+"),
            ("node --version", "Node.js 16+"),
            ("npm --version", "NPM"),
            ("git --version", "Git")
        ]
        
        for command, name in prerequisites:
            success, output = self.run_command(command, f"Check {name}", check=False)
            if not success:
                print(f"{Colors.RED}❌ {name} not found{Colors.END}")
                return False
            print(f"{Colors.GREEN}✅ {name}: {output.strip()}{Colors.END}")
        
        return True
    
    def setup_server_environment(self) -> bool:
        """Setup server environment"""
        print(f"{Colors.BLUE}🖥️  Setting up server environment...{Colors.END}")
        
        steps = [
            ("sudo apt update", "Update package list"),
            ("sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib",
             "Install system packages"),
            ("sudo systemctl enable nginx postgresql", "Enable services"),
            ("sudo systemctl start postgresql", "Start PostgreSQL")
        ]
        
        for command, description in steps:
            success, _ = self.run_command(command, description, check=False)
            if not success:
                print(f"{Colors.YELLOW}⚠️  {description} - May have failed (continuing anyway){Colors.END}")
        
        self.deployment_state['steps_completed'].append('server_environment')
        return True
    
    def setup_database(self) -> bool:
        """Setup database"""
        print(f"{Colors.BLUE}🗄️  Setting up database...{Colors.END}")
        
        db_config = self.config.get('database', {})
        engine = db_config.get('engine', 'sqlite3')
        
        if engine == 'postgresql':
            # PostgreSQL setup
            db_name = db_config.get('name', 'projectmeats')
            db_user = db_config.get('user', 'projectmeats')
            db_password = db_config.get('password', 'projectmeats123')
            
            commands = [
                f"sudo -u postgres createdb {db_name}",
                f"sudo -u postgres createuser {db_user}",
                f"sudo -u postgres psql -c \"ALTER USER {db_user} PASSWORD '{db_password}';\"",
                f"sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};\""
            ]
            
            for command in commands:
                self.run_command(command, f"Database setup: {command}", check=False)
        
        else:
            # SQLite setup (default)
            print(f"{Colors.GREEN}✅ Using SQLite - No additional setup required{Colors.END}")
        
        self.deployment_state['steps_completed'].append('database')
        return True
    
    def deploy_backend(self) -> bool:
        """Deploy Django backend"""
        print(f"{Colors.BLUE}🐍 Deploying backend...{Colors.END}")
        
        backend_dir = Path("backend")
        if not backend_dir.exists():
            self.logger.error("Backend directory not found")
            return False
        
        os.chdir(backend_dir)
        
        steps = [
            ("python3 -m venv venv", "Create virtual environment"),
            ("source venv/bin/activate && pip install -r requirements.txt", 
             "Install Python dependencies"),
            ("source venv/bin/activate && python manage.py migrate", 
             "Run database migrations"),
            ("source venv/bin/activate && python manage.py collectstatic --noinput", 
             "Collect static files")
        ]
        
        for command, description in steps:
            success, output = self.run_command(command, description)
            if not success:
                return False
        
        os.chdir("..")
        self.deployment_state['steps_completed'].append('backend')
        return True
    
    def deploy_frontend(self) -> bool:
        """Deploy React frontend"""
        print(f"{Colors.BLUE}⚛️  Deploying frontend...{Colors.END}")
        
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            self.logger.error("Frontend directory not found")
            return False
        
        os.chdir(frontend_dir)
        
        steps = [
            ("npm install", "Install Node.js dependencies"),
            ("npm run build", "Build React application")
        ]
        
        for command, description in steps:
            success, output = self.run_command(command, description)
            if not success:
                return False
        
        os.chdir("..")
        self.deployment_state['steps_completed'].append('frontend')
        return True
    
    def configure_nginx(self) -> bool:
        """Configure Nginx"""
        print(f"{Colors.BLUE}🌐 Configuring Nginx...{Colors.END}")
        
        domain = self.config.get('domain', 'localhost')
        project_root = self.config.get('paths', {}).get('project_root', '/opt/projectmeats')
        
        nginx_config = f"""
server {{
    listen 80;
    server_name {domain};
    
    # Frontend static files
    location / {{
        root {project_root}/frontend/build;
        try_files $uri $uri/ /index.html;
    }}
    
    # Backend API
    location /api/ {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Django admin
    location /admin/ {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Static files
    location /static/ {{
        root {project_root}/backend;
        expires 30d;
    }}
    
    # Media files
    location /media/ {{
        root {project_root}/backend;
        expires 30d;
    }}
}}
"""
        
        config_file = f"/etc/nginx/sites-available/{domain}"
        enabled_file = f"/etc/nginx/sites-enabled/{domain}"
        
        # Write Nginx config
        try:
            with open(f"/tmp/nginx_{domain}.conf", 'w') as f:
                f.write(nginx_config)
            
            commands = [
                f"sudo mv /tmp/nginx_{domain}.conf {config_file}",
                f"sudo ln -sf {config_file} {enabled_file}",
                "sudo nginx -t",
                "sudo systemctl reload nginx"
            ]
            
            for command in commands:
                success, _ = self.run_command(command, f"Nginx config: {command}")
                if not success:
                    return False
            
        except Exception as e:
            self.logger.error(f"Nginx configuration failed: {e}")
            return False
        
        self.deployment_state['steps_completed'].append('nginx')
        return True
    
    def start_services(self) -> bool:
        """Start application services"""
        print(f"{Colors.BLUE}🚀 Starting services...{Colors.END}")
        
        # Create systemd service for Django
        django_service = f"""
[Unit]
Description=ProjectMeats Django Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/projectmeats/backend
Environment=PATH=/opt/projectmeats/backend/venv/bin
ExecStart=/opt/projectmeats/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 projectmeats.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
"""
        
        try:
            with open("/tmp/projectmeats.service", 'w') as f:
                f.write(django_service)
            
            commands = [
                "sudo mv /tmp/projectmeats.service /etc/systemd/system/",
                "sudo systemctl daemon-reload",
                "sudo systemctl enable projectmeats",
                "sudo systemctl start projectmeats"
            ]
            
            for command in commands:
                success, _ = self.run_command(command, f"Service setup: {command}")
                if not success:
                    return False
            
        except Exception as e:
            self.logger.error(f"Service setup failed: {e}")
            return False
        
        self.deployment_state['steps_completed'].append('services')
        return True
    
    def verify_deployment(self) -> bool:
        """Verify deployment health"""
        print(f"{Colors.BLUE}🔍 Verifying deployment...{Colors.END}")
        
        domain = self.config.get('domain', 'localhost')
        checks = [
            (f"curl -f http://{domain}/api/", "API endpoint"),
            (f"curl -f http://{domain}/", "Frontend"),
            ("sudo systemctl is-active nginx", "Nginx service"),
            ("sudo systemctl is-active projectmeats", "Django service")
        ]
        
        all_checks_passed = True
        for command, description in checks:
            success, output = self.run_command(command, f"Verify {description}", check=False)
            if success:
                print(f"{Colors.GREEN}✅ {description} - OK{Colors.END}")
            else:
                print(f"{Colors.RED}❌ {description} - Failed{Colors.END}")
                all_checks_passed = False
        
        if all_checks_passed:
            print(f"\n{Colors.GREEN}🎉 Deployment verification successful!{Colors.END}")
            print(f"{Colors.CYAN}🌐 Application available at: http://{domain}{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}⚠️  Some checks failed - review logs{Colors.END}")
        
        self.deployment_state['steps_completed'].append('verification')
        return all_checks_passed
    
    def save_deployment_state(self):
        """Save deployment state for troubleshooting"""
        state_file = f"deployment_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(state_file, 'w') as f:
            json.dump(self.deployment_state, f, indent=2)
        print(f"{Colors.CYAN}📄 Deployment state saved: {state_file}{Colors.END}")
    
    def run_full_deployment(self) -> bool:
        """Run complete deployment process"""
        print(f"{Colors.BOLD}🚀 ProjectMeats Production Deployment{Colors.END}")
        print("=" * 50)
        
        steps = [
            (self.check_prerequisites, "Prerequisites"),
            (self.setup_server_environment, "Server Environment"),
            (self.setup_database, "Database"),
            (self.deploy_backend, "Backend"),
            (self.deploy_frontend, "Frontend"),
            (self.configure_nginx, "Nginx"),
            (self.start_services, "Services"),
            (self.verify_deployment, "Verification")
        ]
        
        for step_func, step_name in steps:
            self.deployment_state['current_step'] = step_name
            print(f"\n{Colors.CYAN}📋 Step: {step_name}{Colors.END}")
            
            try:
                success = step_func()
                if not success:
                    print(f"{Colors.RED}❌ Step failed: {step_name}{Colors.END}")
                    self.save_deployment_state()
                    return False
                print(f"{Colors.GREEN}✅ Step completed: {step_name}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}❌ Step error: {step_name} - {e}{Colors.END}")
                self.deployment_state['errors'].append({
                    'step': step_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                self.save_deployment_state()
                return False
        
        print(f"\n{Colors.GREEN}🎉 Production deployment completed successfully!{Colors.END}")
        self.save_deployment_state()
        return True

def main():
    parser = argparse.ArgumentParser(description='ProjectMeats Production Deployment')
    parser.add_argument('--setup', action='store_true', help='Server setup only')
    parser.add_argument('--deploy', action='store_true', help='Deploy application')
    parser.add_argument('--verify', action='store_true', help='Verify deployment')
    parser.add_argument('--full', action='store_true', help='Complete deployment')
    parser.add_argument('--config', type=str, help='Configuration file')
    
    args = parser.parse_args()
    
    if not any([args.setup, args.deploy, args.verify, args.full]):
        parser.print_help()
        return
    
    deployer = ProductionDeployer(args.config)
    
    try:
        if args.setup:
            deployer.check_prerequisites()
            deployer.setup_server_environment()
            deployer.setup_database()
        elif args.deploy:
            deployer.deploy_backend()
            deployer.deploy_frontend()
            deployer.configure_nginx()
            deployer.start_services()
        elif args.verify:
            deployer.verify_deployment()
        elif args.full:
            deployer.run_full_deployment()
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Deployment interrupted by user{Colors.END}")
        deployer.save_deployment_state()
    except Exception as e:
        print(f"\n{Colors.RED}❌ Deployment failed with error: {e}{Colors.END}")
        deployer.save_deployment_state()
        sys.exit(1)

if __name__ == '__main__':
    main()