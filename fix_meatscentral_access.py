#!/usr/bin/env python3
"""
MeatsCentral.com Access Fix Tool
===============================

This tool specifically diagnoses and helps fix access issues for meatscentral.com
pointing to server 167.99.155.140.

Usage:
    # Run local diagnostics from your computer
    python fix_meatscentral_access.py --local-check
    
    # Run server diagnostics (run this on the server after SSH)
    python fix_meatscentral_access.py --server-check
    
    # Auto-fix common issues (run on server as root)
    python fix_meatscentral_access.py --auto-fix
"""

import argparse
import subprocess
import socket
import sys
import requests
from typing import Tuple

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class MeatsCentralFixer:
    def __init__(self):
        self.domain = "meatscentral.com"
        self.server_ip = "167.99.155.140"
        
    def print_header(self, title: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    
    def print_success(self, message: str):
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    
    def print_error(self, message: str):
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    
    def print_warning(self, message: str):
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    
    def print_info(self, message: str):
        print(f"{Colors.CYAN}ℹ {message}{Colors.END}")
    
    def run_command(self, command: str) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def local_diagnostics(self):
        """Run diagnostics from local machine"""
        self.print_header(f"Local Diagnostics for {self.domain}")
        
        print(f"{Colors.BOLD}Domain:{Colors.END} {self.domain}")
        print(f"{Colors.BOLD}Expected Server IP:{Colors.END} {self.server_ip}")
        
        # 1. DNS Resolution Test
        print(f"\n{Colors.BOLD}1. DNS Resolution Test{Colors.END}")
        try:
            resolved_ip = socket.gethostbyname(self.domain)
            if resolved_ip == self.server_ip:
                self.print_success(f"{self.domain} correctly resolves to {resolved_ip}")
            else:
                self.print_error(f"{self.domain} resolves to {resolved_ip}, but should be {self.server_ip}")
                self.print_info("DNS is not pointing to your server!")
                self.print_info("You need to update your domain's A record to point to 167.99.155.140")
                return False
        except socket.gaierror:
            self.print_error(f"DNS resolution failed for {self.domain}")
            self.print_info("Domain does not exist or DNS is not configured")
            return False
        
        # 2. Port Connectivity Test
        print(f"\n{Colors.BOLD}2. Port Connectivity Test{Colors.END}")
        for port, service in [(80, "HTTP"), (443, "HTTPS"), (22, "SSH")]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.server_ip, port))
                sock.close()
                
                if result == 0:
                    self.print_success(f"Port {port} ({service}) is accessible")
                else:
                    if port == 80:
                        self.print_error(f"Port {port} ({service}) is NOT accessible - This is the problem!")
                    elif port == 443:
                        self.print_info(f"Port {port} ({service}) is not accessible (normal without SSL)")
                    else:
                        self.print_warning(f"Port {port} ({service}) is not accessible")
            except Exception as e:
                self.print_error(f"Error testing port {port}: {e}")
        
        # 3. HTTP Request Test
        print(f"\n{Colors.BOLD}3. HTTP Request Test{Colors.END}")
        try:
            response = requests.get(f"http://{self.domain}/health", timeout=10)
            if response.status_code == 200:
                self.print_success(f"HTTP request to {self.domain} successful")
            else:
                self.print_warning(f"HTTP request returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.print_error(f"Cannot connect to {self.domain} via HTTP")
            self.print_info("This confirms the domain is not accessible")
        except requests.exceptions.Timeout:
            self.print_error(f"HTTP request to {self.domain} timed out")
        except Exception as e:
            self.print_error(f"HTTP request failed: {e}")
        
        # 4. Direct IP Test
        print(f"\n{Colors.BOLD}4. Direct IP Test{Colors.END}")
        try:
            response = requests.get(f"http://{self.server_ip}/health", timeout=10)
            if response.status_code == 200:
                self.print_success(f"Direct IP access to {self.server_ip} works")
                self.print_info("Server is working, issue is with domain configuration")
            else:
                self.print_warning(f"Direct IP access returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.print_error(f"Cannot connect to {self.server_ip} directly")
            self.print_info("Server may have firewall blocking HTTP traffic")
        except Exception as e:
            self.print_error(f"Direct IP test failed: {e}")
        
        self.print_recommendations()
        return True
    
    def server_diagnostics(self):
        """Run diagnostics on the server"""
        self.print_header("Server-Side Diagnostics")
        
        # 1. Service Status Check
        print(f"\n{Colors.BOLD}1. Service Status Check{Colors.END}")
        services = ["nginx", "projectmeats", "postgresql"]
        for service in services:
            exit_code, stdout, stderr = self.run_command(f"systemctl is-active {service}")
            if exit_code == 0:
                self.print_success(f"{service} is running")
            else:
                self.print_error(f"{service} is not running")
        
        # 2. Nginx Configuration Check
        print(f"\n{Colors.BOLD}2. Nginx Configuration Check{Colors.END}")
        exit_code, stdout, stderr = self.run_command("nginx -t")
        if exit_code == 0:
            self.print_success("Nginx configuration is valid")
        else:
            self.print_error(f"Nginx configuration error: {stderr}")
        
        # Check if domain is configured in nginx
        exit_code, stdout, stderr = self.run_command(f"nginx -T | grep -i {self.domain}")
        if exit_code == 0:
            self.print_success(f"Nginx is configured for {self.domain}")
        else:
            self.print_error(f"Nginx is NOT configured for {self.domain}")
            self.print_info("This is likely the main issue!")
        
        # 3. Port Binding Check
        print(f"\n{Colors.BOLD}3. Port Binding Check{Colors.END}")
        exit_code, stdout, stderr = self.run_command("netstat -tlnp | grep :80")
        if exit_code == 0:
            self.print_success("Something is listening on port 80:")
            print(f"  {stdout}")
        else:
            self.print_error("Nothing is listening on port 80")
        
        # 4. Firewall Check
        print(f"\n{Colors.BOLD}4. Firewall Check{Colors.END}")
        exit_code, stdout, stderr = self.run_command("ufw status")
        if exit_code == 0:
            if "inactive" in stdout:
                self.print_info("UFW firewall is inactive")
            else:
                print(f"UFW Status:\n{stdout}")
        
        # Check iptables
        exit_code, stdout, stderr = self.run_command("iptables -L -n | grep -E '(80|443)'")
        if exit_code == 0 and stdout:
            print(f"Firewall rules for HTTP/HTTPS:\n{stdout}")
        
        # 5. Local Connectivity Test
        print(f"\n{Colors.BOLD}5. Local Connectivity Test{Colors.END}")
        exit_code, stdout, stderr = self.run_command("curl -s http://localhost/health")
        if exit_code == 0:
            self.print_success("Local health check works")
        else:
            self.print_error("Local health check failed")
            self.print_info("Backend service may not be responding")
        
        return True
    
    def auto_fix(self):
        """Attempt to automatically fix common issues"""
        self.print_header("Auto-Fix for MeatsCentral.com")
        
        self.print_info("Attempting to fix common configuration issues...")
        
        # 1. Create proper nginx configuration for the domain
        print(f"\n{Colors.BOLD}1. Creating Nginx Configuration{Colors.END}")
        
        nginx_config = f"""server {{
    listen 80;
    server_name {self.domain} www.{self.domain};
    
    # Frontend static files
    location / {{
        root /opt/projectmeats/frontend/build;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }}
    
    # Backend API
    location /api/ {{
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Health check endpoint
    location /health {{
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Static files for Django admin
    location /static/ {{
        alias /opt/projectmeats/backend/staticfiles/;
    }}
    
    # Media files
    location /media/ {{
        alias /opt/projectmeats/backend/media/;
    }}
}}"""
        
        exit_code, stdout, stderr = self.run_command(
            f"cat > /etc/nginx/sites-available/{self.domain} << 'EOF'\n{nginx_config}\nEOF"
        )
        if exit_code == 0:
            self.print_success(f"Created nginx configuration for {self.domain}")
        else:
            self.print_error(f"Failed to create nginx configuration: {stderr}")
            return False
        
        # 2. Enable the site
        print(f"\n{Colors.BOLD}2. Enabling Nginx Site{Colors.END}")
        exit_code, stdout, stderr = self.run_command(f"ln -sf /etc/nginx/sites-available/{self.domain} /etc/nginx/sites-enabled/")
        if exit_code == 0:
            self.print_success(f"Enabled nginx site for {self.domain}")
        else:
            self.print_error(f"Failed to enable site: {stderr}")
        
        # 3. Remove default nginx site if it exists
        self.run_command("rm -f /etc/nginx/sites-enabled/default")
        self.print_info("Removed default nginx site")
        
        # 4. Test nginx configuration
        print(f"\n{Colors.BOLD}3. Testing Nginx Configuration{Colors.END}")
        exit_code, stdout, stderr = self.run_command("nginx -t")
        if exit_code == 0:
            self.print_success("Nginx configuration test passed")
        else:
            self.print_error(f"Nginx configuration test failed: {stderr}")
            return False
        
        # 5. Restart services
        print(f"\n{Colors.BOLD}4. Restarting Services{Colors.END}")
        services = ["projectmeats", "nginx"]
        for service in services:
            exit_code, stdout, stderr = self.run_command(f"systemctl restart {service}")
            if exit_code == 0:
                self.print_success(f"Restarted {service}")
            else:
                self.print_error(f"Failed to restart {service}: {stderr}")
        
        # 6. Final verification
        print(f"\n{Colors.BOLD}5. Final Verification{Colors.END}")
        import time
        time.sleep(3)  # Give services time to start
        
        exit_code, stdout, stderr = self.run_command("curl -s http://localhost/health")
        if exit_code == 0:
            self.print_success("Local health check works")
        else:
            self.print_warning("Local health check still not working")
        
        # 7. Open firewall if needed
        print(f"\n{Colors.BOLD}6. Firewall Configuration{Colors.END}")
        exit_code, stdout, stderr = self.run_command("ufw allow 80/tcp")
        if exit_code == 0:
            self.print_success("Opened port 80 in firewall")
        
        exit_code, stdout, stderr = self.run_command("ufw allow 443/tcp")
        if exit_code == 0:
            self.print_success("Opened port 443 in firewall")
        
        self.print_success("Auto-fix completed!")
        self.print_info(f"Try accessing http://{self.domain} now")
        return True
    
    def print_recommendations(self):
        """Print specific recommendations for fixing the issue"""
        self.print_header("Recommendations")
        
        print(f"{Colors.BOLD}To fix meatscentral.com access, follow these steps:{Colors.END}\n")
        
        print(f"{Colors.BOLD}1. SSH into your server:{Colors.END}")
        print(f"   ssh -i ~/.ssh/id_ed25519 root@{self.server_ip}")
        
        print(f"\n{Colors.BOLD}2. Run server diagnostics:{Colors.END}")
        print(f"   python3 fix_meatscentral_access.py --server-check")
        
        print(f"\n{Colors.BOLD}3. Auto-fix common issues:{Colors.END}")
        print(f"   python3 fix_meatscentral_access.py --auto-fix")
        
        print(f"\n{Colors.BOLD}4. Manual checks if auto-fix doesn't work:{Colors.END}")
        print(f"   • Check nginx config: nginx -T | grep -A 10 {self.domain}")
        print(f"   • Check services: systemctl status nginx projectmeats")
        print(f"   • Check logs: tail -f /var/log/nginx/error.log")
        print(f"   • Test locally: curl http://localhost/health")
        
        print(f"\n{Colors.BOLD}5. DNS Configuration:{Colors.END}")
        print(f"   • Ensure your domain registrar has an A record:")
        print(f"   • Name: @ (or meatscentral.com)")
        print(f"   • Type: A")
        print(f"   • Value: {self.server_ip}")
        print(f"   • TTL: 300 (5 minutes)")
        
        print(f"\n{Colors.BOLD}6. Common Issues:{Colors.END}")
        print(f"   • DNS propagation can take up to 48 hours")
        print(f"   • Check DNS propagation: https://dnschecker.org/")
        print(f"   • Test direct IP: http://{self.server_ip}/health")

def main():
    parser = argparse.ArgumentParser(description="Fix MeatsCentral.com access issues")
    parser.add_argument("--local-check", action="store_true", help="Run diagnostics from local machine")
    parser.add_argument("--server-check", action="store_true", help="Run diagnostics on server")
    parser.add_argument("--auto-fix", action="store_true", help="Attempt to auto-fix issues (run on server)")
    
    args = parser.parse_args()
    
    fixer = MeatsCentralFixer()
    
    if args.local_check:
        fixer.local_diagnostics()
    elif args.server_check:
        fixer.server_diagnostics()
    elif args.auto_fix:
        fixer.auto_fix()
    else:
        print("Usage:")
        print("  python fix_meatscentral_access.py --local-check    (run from your computer)")
        print("  python fix_meatscentral_access.py --server-check   (run on server)")
        print("  python fix_meatscentral_access.py --auto-fix       (run on server to fix)")

if __name__ == "__main__":
    main()