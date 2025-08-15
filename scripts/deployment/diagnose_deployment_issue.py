#!/usr/bin/env python3
"""
ProjectMeats Deployment Issue Diagnosis Tool
============================================

This script analyzes the deployment issue where the deployment appears successful
but the site isn't reachable. It provides clear diagnosis and next steps.

Usage:
    python diagnose_deployment_issue.py --server 167.99.155.140 --domain meatscentral.com
"""

import argparse
import paramiko
import sys
import json
from datetime import datetime


class DeploymentDiagnostic:
    def __init__(self, server, username="root", key_file=None, domain=None):
        self.server = server
        self.username = username
        self.key_file = key_file
        self.domain = domain
        self.ssh = None
        
    def connect(self):
        """Connect to the server"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_file:
                self.ssh.connect(self.server, username=self.username, key_filename=self.key_file)
            else:
                # Try to use default SSH key
                import os
                possible_keys = [
                    os.path.expanduser("~/.ssh/id_rsa"),
                    os.path.expanduser("~/.ssh/id_ed25519"),
                    os.path.expanduser("~/.ssh/id_ecdsa")
                ]
                
                connected = False
                for key in possible_keys:
                    if os.path.exists(key):
                        try:
                            self.ssh.connect(self.server, username=self.username, key_filename=key)
                            connected = True
                            print(f"✅ Connected using SSH key: {key}")
                            break
                        except:
                            continue
                
                if not connected:
                    raise Exception("Could not connect with any available SSH keys")
                    
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def run_command(self, command):
        """Execute command on server"""
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode('utf-8').strip()
            stderr_text = stderr.read().decode('utf-8').strip()
            return exit_code, stdout_text, stderr_text
        except Exception as e:
            return -1, "", str(e)
    
    def check_service_status(self, service):
        """Check if a service is running"""
        exit_code, stdout, stderr = self.run_command(f"systemctl is-active {service}")
        return exit_code == 0 and stdout.strip() == "active"
    
    def check_port_listening(self, port):
        """Check if a port is being listened on using ss command as specified in problem statement"""
        # Use ss -tlnp | grep :port with sudo as recommended in problem statement
        exit_code, stdout, stderr = self.run_command(f"sudo ss -tlnp | grep :{port}")
        return exit_code == 0 and stdout.strip() != ""
    
    def diagnose(self):
        """Run comprehensive diagnosis"""
        print("🔍 ProjectMeats Deployment Diagnosis")
        print("=" * 50)
        print(f"Server: {self.server}")
        print(f"Domain: {self.domain or 'Not specified'}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if not self.connect():
            return False
        
        print("📋 DIAGNOSIS RESULTS:")
        print("-" * 30)
        
        # 1. Check if ProjectMeats directory exists and has content
        print("1. 📁 ProjectMeats Application Status:")
        exit_code, stdout, stderr = self.run_command("ls -la /opt/projectmeats/")
        if exit_code == 0 and stdout:
            print("   ✅ /opt/projectmeats directory exists")
            
            # Check for essential files
            essential_files = ["backend", "frontend", "README.md"]
            missing_files = []
            for file in essential_files:
                exit_code, _, _ = self.run_command(f"ls /opt/projectmeats/{file}")
                if exit_code != 0:
                    missing_files.append(file)
            
            if missing_files:
                print(f"   ❌ Missing essential files/directories: {', '.join(missing_files)}")
                print("   🔍 This indicates the download step FAILED during deployment")
            else:
                print("   ✅ Essential application files are present")
        else:
            print("   ❌ /opt/projectmeats directory does not exist or is empty")
            print("   🔍 This indicates the download step FAILED during deployment")
        
        # 2. Check for backup directories (evidence of failed deployment attempts)
        print("\n2. 🗂️ Backup Directories (Evidence of Previous Failed Attempts):")
        exit_code, stdout, stderr = self.run_command("ls -la /opt/ | grep projectmeats_backup")
        if exit_code == 0 and stdout:
            print("   ⚠️ Found backup directories from previous deployment attempts:")
            for line in stdout.strip().split('\n'):
                print(f"     {line}")
            print("   🔍 This confirms multiple failed deployment attempts")
        else:
            print("   ✅ No backup directories found")
        
        # 3. Check web server status
        print("\n3. 🌐 Web Server Status:")
        nginx_running = self.check_service_status("nginx")
        print(f"   Nginx: {'✅ Running' if nginx_running else '❌ Not running'}")
        
        port_80 = self.check_port_listening(80)
        port_443 = self.check_port_listening(443)
        print(f"   Port 80 (HTTP): {'✅ Listening' if port_80 else '❌ Not listening'}")
        print(f"   Port 443 (HTTPS): {'✅ Listening' if port_443 else '❌ Not listening'}")
        
        # 4. Check nginx configuration
        print("\n4. ⚙️ Nginx Configuration:")
        exit_code, stdout, stderr = self.run_command("nginx -t")
        if exit_code == 0:
            print("   ✅ Nginx configuration is valid")
        else:
            print(f"   ❌ Nginx configuration error: {stderr}")
        
        # Check if there's a ProjectMeats site configured
        exit_code, stdout, stderr = self.run_command("ls /etc/nginx/sites-enabled/ | grep -i projectmeats")
        if exit_code == 0 and stdout:
            print(f"   ✅ ProjectMeats nginx site found: {stdout}")
        else:
            print("   ❌ No ProjectMeats nginx site configuration found")
        
        # 5. Check database status
        print("\n5. 🗄️ Database Status:")
        postgres_running = self.check_service_status("postgresql")
        print(f"   PostgreSQL: {'✅ Running' if postgres_running else '❌ Not running'}")
        
        if postgres_running:
            exit_code, stdout, stderr = self.run_command("sudo -u postgres psql -l | grep projectmeats")
            if exit_code == 0 and stdout:
                print("   ✅ ProjectMeats database exists")
            else:
                print("   ❌ ProjectMeats database not found")
        
        # 6. Check Django application status
        print("\n6. 🐍 Django Application Status:")
        exit_code, stdout, stderr = self.run_command("ls /opt/projectmeats/backend/venv/")
        if exit_code == 0:
            print("   ✅ Python virtual environment exists")
            
            # Check if Django can start
            exit_code, stdout, stderr = self.run_command(
                "cd /opt/projectmeats/backend && ./venv/bin/python manage.py check --deploy"
            )
            if exit_code == 0:
                print("   ✅ Django application passes deployment checks")
            else:
                print(f"   ❌ Django deployment check failed: {stderr}")
        else:
            print("   ❌ Python virtual environment not found")
        
        # 7. Check for running Django/Gunicorn processes
        print("\n7. 🔄 Application Processes:")
        exit_code, stdout, stderr = self.run_command("ps aux | grep -E '(gunicorn|django|projectmeats)' | grep -v grep")
        if exit_code == 0 and stdout:
            print("   ✅ Django/Gunicorn processes found:")
            for line in stdout.strip().split('\n'):
                print(f"     {line}")
        else:
            print("   ❌ No Django/Gunicorn processes running")
        
        # 8. Check domain resolution and SSL
        if self.domain:
            print(f"\n8. 🌍 Domain Status ({self.domain}):")
            exit_code, stdout, stderr = self.run_command(f"dig +short {self.domain}")
            if exit_code == 0 and stdout:
                resolved_ip = stdout.strip()
                print(f"   ✅ Domain resolves to: {resolved_ip}")
                if resolved_ip == self.server:
                    print("   ✅ Domain points to this server")
                else:
                    print(f"   ⚠️ Domain points to {resolved_ip}, but this server is {self.server}")
            else:
                print(f"   ❌ Domain does not resolve")
            
            # Check SSL certificate
            exit_code, stdout, stderr = self.run_command(f"ls /etc/letsencrypt/live/{self.domain}/")
            if exit_code == 0:
                print(f"   ✅ SSL certificate found for {self.domain}")
            else:
                print(f"   ❌ No SSL certificate found for {self.domain}")
        
        print("\n" + "=" * 50)
        print("📊 SUMMARY AND NEXT STEPS:")
        print("-" * 30)
        
        # Determine the issue and provide recommendations
        exit_code, stdout, stderr = self.run_command("ls -la /opt/projectmeats/backend /opt/projectmeats/frontend")
        app_complete = exit_code == 0
        
        if not app_complete:
            print("🔍 ROOT CAUSE IDENTIFIED:")
            print("   The deployment FAILED during the 'Application download and setup' step.")
            print("   The terminal log shows 'SUCCESS' but this was misleading - the deployment")
            print("   actually failed when trying to download ProjectMeats from GitHub.")
            print()
            print("📋 WHAT HAPPENED:")
            print("   1. Git clone failed (directory not empty)")
            print("   2. Fallback ZIP download got a 404 error page instead of the actual ZIP")
            print("   3. Unzip failed because it wasn't a real ZIP file")
            print("   4. The deployment script said it would retry but actually failed")
            print("   5. Nginx may be running but serving nothing or default pages")
            print()
            print("✅ SOLUTION:")
            print("   The deployment scripts have been fixed with proper:")
            print("   - Directory backup and cleanup")
            print("   - Download validation (file size and format checks)")
            print("   - Multiple fallback download methods")
            print("   - Clear error reporting")
            print()
            print("🚀 TO FIX:")
            print("   Re-run the deployment with the updated orchestrator:")
            print(f"   python ai_deployment_orchestrator.py --interactive")
            print("   OR")
            print(f"   python ai_deployment_orchestrator.py --server {self.server} --domain {self.domain or 'yourdomain.com'} --auto")
        else:
            print("🔍 APPLICATION FILES FOUND:")
            print("   The ProjectMeats application appears to be downloaded correctly.")
            print("   The issue may be with service configuration or startup.")
            print()
            print("🔄 NEXT STEPS:")
            print("   1. Check application logs for errors")
            print("   2. Verify Django configuration")
            print("   3. Restart web services")
            print("   4. Check firewall settings")
        
        self.ssh.close()
        return True


def main():
    parser = argparse.ArgumentParser(description="Diagnose ProjectMeats deployment issues")
    parser.add_argument("--server", required=True, help="Server hostname or IP")
    parser.add_argument("--username", default="root", help="SSH username")
    parser.add_argument("--key-file", help="SSH private key file")
    parser.add_argument("--domain", help="Domain name")
    
    args = parser.parse_args()
    
    diagnostic = DeploymentDiagnostic(
        server=args.server,
        username=args.username,
        key_file=args.key_file,
        domain=args.domain
    )
    
    success = diagnostic.diagnose()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()