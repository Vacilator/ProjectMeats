#!/usr/bin/env python3
"""
ProjectMeats Deployment Manager
==============================

Unified management script for ProjectMeats production deployments.
Provides easy access to all deployment, monitoring, and maintenance tasks.

This script uses the AI Deployment Orchestrator as the backend and adds
convenient management commands for day-to-day operations.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

class Colors:
    """ANSI color codes for output formatting"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class DeploymentManager:
    """Main deployment management class"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.orchestrator_path = self.script_dir / 'ai_deployment_orchestrator.py'
        
    def log(self, message, color=Colors.BLUE):
        """Log a message with color formatting"""
        print(f"{color}[MANAGER] {message}{Colors.END}")
        
    def success(self, message):
        """Log a success message"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
        
    def warning(self, message):
        """Log a warning message"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
        
    def error(self, message):
        """Log an error message"""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
        
    def run_command(self, cmd, check=True):
        """Run a shell command"""
        self.log(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        try:
            result = subprocess.run(cmd, shell=isinstance(cmd, str), check=check, 
                                  capture_output=False)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            self.error(f"Command failed with exit code {e.returncode}")
            return False
        except Exception as e:
            self.error(f"Error running command: {e}")
            return False
    
    def deploy_docker(self, server, domain, monitoring=False, interactive=False):
        """Deploy using Docker with industry best practices"""
        self.log("Starting Docker deployment...", Colors.CYAN)
        
        cmd = ['python3', str(self.orchestrator_path)]
        
        if interactive:
            cmd.append('--interactive')
        else:
            cmd.extend(['--server', server, '--domain', domain, '--docker'])
            if monitoring:
                cmd.append('--docker-monitoring')
                
        return self.run_command(cmd)
    
    def deploy_standard(self, server, domain, interactive=False):
        """Deploy using standard systemd approach"""
        self.log("Starting standard deployment...", Colors.CYAN)
        
        cmd = ['python3', str(self.orchestrator_path)]
        
        if interactive:
            cmd.append('--interactive')
        else:
            cmd.extend(['--server', server, '--domain', domain])
            
        return self.run_command(cmd)
    
    def health_check(self, domain=None):
        """Run comprehensive health check"""
        self.log("Running health check...", Colors.CYAN)
        
        health_script = self.script_dir / 'scripts' / 'health_check.sh'
        cmd = ['bash', str(health_script)]
        
        if domain:
            cmd.extend(['--domain', domain])
            
        return self.run_command(cmd)
    
    def backup_database(self):
        """Run database backup"""
        self.log("Running database backup...", Colors.CYAN)
        
        backup_script = self.script_dir / 'scripts' / 'backup_database.sh'
        return self.run_command(['bash', str(backup_script)])
    
    def setup_ssl(self, domain, email=None, staging=False):
        """Setup SSL certificates"""
        self.log(f"Setting up SSL for {domain}...", Colors.CYAN)
        
        ssl_script = self.script_dir / 'scripts' / 'ssl_automation.sh'
        cmd = ['sudo', 'bash', str(ssl_script), '--domain', domain]
        
        if email:
            cmd.extend(['--email', email])
        if staging:
            cmd.append('--staging')
            
        return self.run_command(cmd)
    
    def renew_ssl(self):
        """Renew SSL certificates"""
        self.log("Renewing SSL certificates...", Colors.CYAN)
        
        ssl_script = self.script_dir / 'scripts' / 'ssl_automation.sh'
        return self.run_command(['sudo', 'bash', str(ssl_script), '--renew'])
    
    def check_ssl(self, domain):
        """Check SSL certificate status"""
        self.log(f"Checking SSL certificate for {domain}...", Colors.CYAN)
        
        ssl_script = self.script_dir / 'scripts' / 'ssl_automation.sh'
        return self.run_command(['sudo', 'bash', str(ssl_script), '--check', '--domain', domain])
    
    def view_logs(self, service=None):
        """View Docker container logs"""
        self.log("Viewing container logs...", Colors.CYAN)
        
        if service:
            cmd = ['docker-compose', 'logs', '-f', service]
        else:
            cmd = ['docker-compose', 'logs', '-f']
            
        return self.run_command(cmd)
    
    def restart_services(self):
        """Restart all Docker services"""
        self.log("Restarting Docker services...", Colors.CYAN)
        
        return self.run_command(['docker-compose', 'restart'])
    
    def update_deployment(self):
        """Update deployment with latest code"""
        self.log("Updating deployment...", Colors.CYAN)
        
        commands = [
            ['git', 'pull'],
            ['docker-compose', 'build', '--no-cache'],
            ['docker-compose', 'up', '-d'],
        ]
        
        for cmd in commands:
            if not self.run_command(cmd):
                return False
                
        return True
    
    def cleanup_deployment(self):
        """Run deployment cleanup script"""
        self.log("Running deployment cleanup...", Colors.CYAN)
        
        cleanup_script = self.script_dir / 'cleanup_deployment.py'
        return self.run_command(['python3', str(cleanup_script)])
    
    def show_status(self):
        """Show deployment status"""
        self.log("Checking deployment status...", Colors.CYAN)
        
        # Show Docker containers status
        print(f"\n{Colors.BOLD}Docker Containers:{Colors.END}")
        self.run_command(['docker-compose', 'ps'], check=False)
        
        # Show disk usage
        print(f"\n{Colors.BOLD}Disk Usage:{Colors.END}")
        self.run_command(['df', '-h', '/opt/projectmeats'], check=False)
        
        # Show memory usage
        print(f"\n{Colors.BOLD}Memory Usage:{Colors.END}")
        self.run_command(['free', '-h'], check=False)
        
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ProjectMeats Deployment Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  deploy-docker     Deploy using Docker (recommended)
  deploy-standard   Deploy using systemd services  
  health-check      Run comprehensive health check
  backup           Backup database
  ssl-setup        Setup SSL certificates
  ssl-renew        Renew SSL certificates
  ssl-check        Check SSL certificate status
  logs             View container logs
  restart          Restart all services
  update           Update deployment with latest code
  cleanup          Clean up deployment files
  status           Show deployment status
        """
    )
    
    # Common arguments
    parser.add_argument('--server', help='Server hostname or IP')
    parser.add_argument('--domain', help='Domain name')
    parser.add_argument('--email', help='Email for SSL certificates')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--monitoring', action='store_true', help='Include monitoring stack')
    parser.add_argument('--staging', action='store_true', help='Use staging environment')
    parser.add_argument('--service', help='Specific service name for logs')
    
    # Command
    parser.add_argument('command', nargs='?', choices=[
        'deploy-docker', 'deploy-standard', 'health-check', 'backup',
        'ssl-setup', 'ssl-renew', 'ssl-check', 'logs', 'restart',
        'update', 'cleanup', 'status'
    ], help='Command to execute')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = DeploymentManager()
    
    # Show banner
    print(f"""
{Colors.CYAN}🚀 ProjectMeats Deployment Manager{Colors.END}
{Colors.CYAN}==================================={Colors.END}
Command: {args.command}
""")
    
    success = False
    
    try:
        if args.command == 'deploy-docker':
            if args.interactive:
                success = manager.deploy_docker(None, None, args.monitoring, True)
            elif args.server and args.domain:
                success = manager.deploy_docker(args.server, args.domain, args.monitoring)
            else:
                manager.error("--server and --domain are required for non-interactive deployment")
                
        elif args.command == 'deploy-standard':
            if args.interactive:
                success = manager.deploy_standard(None, None, True)
            elif args.server and args.domain:
                success = manager.deploy_standard(args.server, args.domain)
            else:
                manager.error("--server and --domain are required for non-interactive deployment")
                
        elif args.command == 'health-check':
            success = manager.health_check(args.domain)
            
        elif args.command == 'backup':
            success = manager.backup_database()
            
        elif args.command == 'ssl-setup':
            if not args.domain:
                manager.error("--domain is required for SSL setup")
            else:
                success = manager.setup_ssl(args.domain, args.email, args.staging)
                
        elif args.command == 'ssl-renew':
            success = manager.renew_ssl()
            
        elif args.command == 'ssl-check':
            if not args.domain:
                manager.error("--domain is required for SSL check")
            else:
                success = manager.check_ssl(args.domain)
                
        elif args.command == 'logs':
            success = manager.view_logs(args.service)
            
        elif args.command == 'restart':
            success = manager.restart_services()
            
        elif args.command == 'update':
            success = manager.update_deployment()
            
        elif args.command == 'cleanup':
            success = manager.cleanup_deployment()
            
        elif args.command == 'status':
            success = manager.show_status()
            
        if success:
            manager.success(f"Command '{args.command}' completed successfully")
            return 0
        else:
            manager.error(f"Command '{args.command}' failed")
            return 1
            
    except KeyboardInterrupt:
        manager.warning("Command cancelled by user")
        return 1
    except Exception as e:
        manager.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())