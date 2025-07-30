#!/usr/bin/env python3
"""
ProjectMeats Deployment Verification Script
==========================================

Quick verification script to test if ProjectMeats deployment was successful.
Checks all critical components and provides troubleshooting guidance.
"""

import os
import sys
import subprocess
import urllib.request
import urllib.error
import json
import time
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class DeploymentVerifier:
    def __init__(self):
        self.config = self.load_config()
        self.issues = []
        self.warnings = []
    
    def load_config(self):
        """Load deployment configuration"""
        config_file = Path("production_config.json")
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        return {}
    
    def log(self, message, level="INFO"):
        colors = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED
        }
        color = colors.get(level, Colors.BLUE)
        print(f"{color}[{level}]{Colors.END} {message}")
    
    def run_command(self, command, capture_output=True):
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=capture_output, 
                text=True, timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def check_http_endpoint(self, url, timeout=10):
        """Check if HTTP endpoint is accessible"""
        try:
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'ProjectMeats-Deployment-Verifier/1.0')
            
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return True, response.getcode(), response.read().decode()
        except urllib.error.HTTPError as e:
            return False, e.code, str(e)
        except urllib.error.URLError as e:
            return False, 0, str(e)
        except Exception as e:
            return False, 0, str(e)
    
    def check_service_status(self, service_name):
        """Check systemd service status"""
        success, stdout, stderr = self.run_command(f"systemctl is-active {service_name}")
        if success and "active" in stdout:
            return True, "active"
        
        # Get detailed status
        success, stdout, stderr = self.run_command(f"systemctl status {service_name} --no-pager -l")
        return False, stdout
    
    def check_environment_files(self):
        """Verify environment configuration files exist"""
        self.log("Checking environment configuration files...")
        
        backend_env = Path("backend/.env")
        frontend_env = Path("frontend/.env.production")
        
        if backend_env.exists():
            self.log("✓ Backend environment file exists", "SUCCESS")
        else:
            self.issues.append("Backend .env file missing")
            self.log("✗ Backend .env file missing", "ERROR")
        
        if frontend_env.exists():
            self.log("✓ Frontend environment file exists", "SUCCESS")
        else:
            self.warnings.append("Frontend .env.production file missing")
            self.log("⚠ Frontend .env.production file missing", "WARNING")
    
    def check_services(self):
        """Check all required services are running"""
        self.log("Checking system services...")
        
        services = ['projectmeats', 'nginx']
        if self.config.get('database_type') == 'postgresql':
            services.append('postgresql')
        
        for service in services:
            is_active, status = self.check_service_status(service)
            if is_active:
                self.log(f"✓ {service} service is running", "SUCCESS")
            else:
                self.issues.append(f"{service} service not running")
                self.log(f"✗ {service} service not running", "ERROR")
                self.log(f"  Status: {status[:200]}...", "ERROR")
    
    def check_database_connection(self):
        """Check database connectivity"""
        self.log("Checking database connection...")
        
        if self.config.get('database_type') == 'postgresql':
            db_name = self.config.get('db_name', 'projectmeats_prod')
            db_user = self.config.get('db_user', 'projectmeats_user')
            
            success, stdout, stderr = self.run_command(
                f'sudo -u postgres psql -d {db_name} -c "SELECT version();" -t'
            )
            
            if success:
                self.log("✓ PostgreSQL database connection successful", "SUCCESS")
            else:
                self.issues.append("Database connection failed")
                self.log("✗ PostgreSQL connection failed", "ERROR")
                self.log(f"  Error: {stderr}", "ERROR")
        else:
            # Check SQLite
            sqlite_path = Path("backend/db.sqlite3")
            if sqlite_path.exists():
                self.log("✓ SQLite database file exists", "SUCCESS")
            else:
                self.issues.append("SQLite database file missing")
                self.log("✗ SQLite database file missing", "ERROR")
    
    def check_web_endpoints(self):
        """Check web application endpoints"""
        self.log("Checking web application endpoints...")
        
        domain = self.config.get('domain', 'localhost')
        use_ssl = self.config.get('use_ssl', False)
        protocol = 'https' if use_ssl else 'http'
        
        endpoints = [
            (f"{protocol}://{domain}/", "Frontend"),
            (f"{protocol}://{domain}/api/v1/", "API"),
            (f"{protocol}://{domain}/admin/", "Admin"),
            (f"{protocol}://{domain}/api/docs/", "API Documentation")
        ]
        
        for url, name in endpoints:
            self.log(f"Testing {name}: {url}")
            success, status_code, content = self.check_http_endpoint(url)
            
            if success and status_code == 200:
                self.log(f"✓ {name} accessible (HTTP {status_code})", "SUCCESS")
            elif success and status_code in [301, 302]:
                self.log(f"⚠ {name} redirected (HTTP {status_code})", "WARNING")
            else:
                self.issues.append(f"{name} not accessible")
                self.log(f"✗ {name} not accessible (HTTP {status_code})", "ERROR")
                if "refused" in str(content).lower():
                    self.log("  Possible cause: Service not running", "ERROR")
                elif "timeout" in str(content).lower():
                    self.log("  Possible cause: Firewall blocking access", "ERROR")
    
    def check_ssl_certificate(self):
        """Check SSL certificate if HTTPS is enabled"""
        if not self.config.get('use_ssl'):
            return
        
        self.log("Checking SSL certificate...")
        domain = self.config.get('domain')
        
        if domain and domain != 'localhost':
            success, stdout, stderr = self.run_command(
                f'echo | openssl s_client -servername {domain} -connect {domain}:443 2>/dev/null | openssl x509 -noout -dates'
            )
            
            if success and "notAfter" in stdout:
                self.log("✓ SSL certificate is valid", "SUCCESS")
                self.log(f"  Certificate info: {stdout.strip()}", "INFO")
            else:
                self.issues.append("SSL certificate issue")
                self.log("✗ SSL certificate issue", "ERROR")
                self.log("  Try running: sudo certbot renew", "INFO")
    
    def check_file_permissions(self):
        """Check critical file permissions"""
        self.log("Checking file permissions...")
        
        critical_paths = [
            "/home/projectmeats/app",
            "/home/projectmeats/uploads", 
            "/home/projectmeats/logs"
        ]
        
        for path in critical_paths:
            if os.path.exists(path):
                stat_info = os.stat(path)
                owner_readable = bool(stat_info.st_mode & 0o400)
                owner_writable = bool(stat_info.st_mode & 0o200)
                
                if owner_readable and owner_writable:
                    self.log(f"✓ {path} permissions correct", "SUCCESS")
                else:
                    self.warnings.append(f"Permissions issue: {path}")
                    self.log(f"⚠ {path} permissions may be incorrect", "WARNING")
            else:
                self.warnings.append(f"Path not found: {path}")
                self.log(f"⚠ Path not found: {path}", "WARNING")
    
    def check_disk_space(self):
        """Check available disk space"""
        self.log("Checking disk space...")
        
        success, stdout, stderr = self.run_command("df -h /")
        if success:
            lines = stdout.strip().split('\n')
            if len(lines) >= 2:
                usage_line = lines[1].split()
                if len(usage_line) >= 5:
                    usage_percent = usage_line[4].rstrip('%')
                    try:
                        usage = int(usage_percent)
                        if usage < 80:
                            self.log(f"✓ Disk usage: {usage}% (healthy)", "SUCCESS")
                        elif usage < 90:
                            self.warnings.append(f"Disk usage high: {usage}%")
                            self.log(f"⚠ Disk usage: {usage}% (warning)", "WARNING")
                        else:
                            self.issues.append(f"Disk usage critical: {usage}%")
                            self.log(f"✗ Disk usage: {usage}% (critical)", "ERROR")
                    except ValueError:
                        self.log("Could not parse disk usage", "WARNING")
    
    def check_memory_usage(self):
        """Check memory usage"""
        self.log("Checking memory usage...")
        
        success, stdout, stderr = self.run_command("free -m")
        if success:
            lines = stdout.strip().split('\n')
            if len(lines) >= 2:
                mem_line = lines[1].split()
                if len(mem_line) >= 3:
                    try:
                        total = int(mem_line[1])
                        used = int(mem_line[2])
                        usage_percent = (used / total) * 100
                        
                        if usage_percent < 80:
                            self.log(f"✓ Memory usage: {usage_percent:.1f}% (healthy)", "SUCCESS")
                        elif usage_percent < 90:
                            self.warnings.append(f"Memory usage high: {usage_percent:.1f}%")
                            self.log(f"⚠ Memory usage: {usage_percent:.1f}% (warning)", "WARNING")
                        else:
                            self.issues.append(f"Memory usage critical: {usage_percent:.1f}%")
                            self.log(f"✗ Memory usage: {usage_percent:.1f}% (critical)", "ERROR")
                    except ValueError:
                        self.log("Could not parse memory usage", "WARNING")
    
    def check_logs_for_errors(self):
        """Check recent logs for errors"""
        self.log("Checking recent application logs...")
        
        log_files = [
            "/home/projectmeats/logs/gunicorn_error.log",
            "/var/log/nginx/error.log"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                success, stdout, stderr = self.run_command(f"tail -20 {log_file}")
                if success and stdout:
                    error_indicators = ['error', 'exception', 'failed', 'critical']
                    recent_errors = []
                    
                    for line in stdout.split('\n'):
                        if any(indicator in line.lower() for indicator in error_indicators):
                            recent_errors.append(line.strip())
                    
                    if recent_errors:
                        self.warnings.append(f"Recent errors in {log_file}")
                        self.log(f"⚠ Found recent errors in {log_file}", "WARNING")
                        for error in recent_errors[-3:]:  # Show last 3 errors
                            self.log(f"  {error}", "WARNING")
                    else:
                        self.log(f"✓ No recent errors in {log_file}", "SUCCESS")
    
    def generate_summary(self):
        """Generate verification summary"""
        print(f"\n{Colors.BOLD}📋 Deployment Verification Summary{Colors.END}")
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        
        if not self.issues and not self.warnings:
            self.log("🎉 All checks passed! Deployment is healthy.", "SUCCESS")
            
            domain = self.config.get('domain', 'localhost')
            protocol = 'https' if self.config.get('use_ssl') else 'http'
            
            print(f"\n{Colors.GREEN}🌐 Your application is ready:{Colors.END}")
            print(f"   Website: {Colors.CYAN}{protocol}://{domain}{Colors.END}")
            print(f"   Admin:   {Colors.CYAN}{protocol}://{domain}/admin/{Colors.END}")
            print(f"   API:     {Colors.CYAN}{protocol}://{domain}/api/docs/{Colors.END}")
            
            admin_user = self.config.get('admin_username', 'admin')
            admin_pass = self.config.get('admin_password', 'WATERMELON1219')
            print(f"\n{Colors.GREEN}👤 Admin Credentials:{Colors.END}")
            print(f"   Username: {Colors.CYAN}{admin_user}{Colors.END}")
            print(f"   Password: {Colors.CYAN}{admin_pass}{Colors.END}")
            
        else:
            if self.issues:
                self.log(f"❌ Found {len(self.issues)} critical issues:", "ERROR")
                for i, issue in enumerate(self.issues, 1):
                    self.log(f"  {i}. {issue}", "ERROR")
            
            if self.warnings:
                self.log(f"⚠️  Found {len(self.warnings)} warnings:", "WARNING")
                for i, warning in enumerate(self.warnings, 1):
                    self.log(f"  {i}. {warning}", "WARNING")
        
        # Troubleshooting suggestions
        if self.issues or self.warnings:
            print(f"\n{Colors.BOLD}🔧 Troubleshooting Suggestions:{Colors.END}")
            
            if any("service not running" in issue for issue in self.issues):
                print(f"{Colors.CYAN}• Restart services:{Colors.END}")
                print(f"  sudo systemctl restart projectmeats nginx")
                if self.config.get('database_type') == 'postgresql':
                    print(f"  sudo systemctl restart postgresql")
            
            if any("not accessible" in issue for issue in self.issues):
                print(f"{Colors.CYAN}• Check firewall:{Colors.END}")
                print(f"  sudo ufw status")
                print(f"  sudo ufw allow 'Nginx Full'")
            
            if any("database" in issue.lower() for issue in self.issues):
                print(f"{Colors.CYAN}• Database troubleshooting:{Colors.END}")
                print(f"  sudo systemctl status postgresql")
                print(f"  sudo -u postgres psql -c '\\l'")
            
            if any("ssl" in issue.lower() for issue in self.issues):
                print(f"{Colors.CYAN}• SSL certificate issues:{Colors.END}")
                print(f"  sudo certbot renew")
                print(f"  sudo systemctl reload nginx")
            
            print(f"\n{Colors.CYAN}📖 For detailed troubleshooting, check:{Colors.END}")
            print(f"  • Application logs: /home/projectmeats/logs/")
            print(f"  • Service status: ./scripts/status.sh")
            print(f"  • System logs: journalctl -u projectmeats -f")
    
    def run(self):
        """Run all verification checks"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 ProjectMeats Deployment Verification{Colors.END}")
        print(f"{Colors.BLUE}{'='*50}{Colors.END}\n")
        
        try:
            self.check_environment_files()
            self.check_services()
            self.check_database_connection()
            self.check_web_endpoints()
            self.check_ssl_certificate()
            self.check_file_permissions()
            self.check_disk_space()
            self.check_memory_usage()
            self.check_logs_for_errors()
            
            self.generate_summary()
            
        except KeyboardInterrupt:
            self.log("\nVerification cancelled by user.", "WARNING")
        except Exception as e:
            self.log(f"Verification failed with error: {e}", "ERROR")


if __name__ == "__main__":
    verifier = DeploymentVerifier()
    verifier.run()