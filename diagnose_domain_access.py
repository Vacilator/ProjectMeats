#!/usr/bin/env python3
"""
Domain Access Diagnostic Tool for ProjectMeats
==============================================

This diagnostic tool helps troubleshoot why a domain might not be accessible
even after a successful deployment.

Usage:
    python diagnose_domain_access.py --domain meatscentral.com
    python diagnose_domain_access.py --domain meatscentral.com --server 167.99.155.140 --user root --key ~/.ssh/id_rsa
"""

import argparse
import subprocess
import sys
import socket
import requests
from typing import Optional, Tuple


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class DomainDiagnostic:
    def __init__(self, domain: str, server_ip: Optional[str] = None):
        self.domain = domain
        self.server_ip = server_ip
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    
    def print_success(self, message: str):
        """Print a success message"""
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    
    def print_warning(self, message: str):
        """Print a warning message"""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    
    def print_error(self, message: str):
        """Print an error message"""
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    
    def print_info(self, message: str):
        """Print an info message"""
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
    
    def check_dns_resolution(self):
        """Check if the domain resolves to an IP"""
        self.print_header("DNS Resolution Check")
        
        try:
            ip = socket.gethostbyname(self.domain)
            self.print_success(f"Domain {self.domain} resolves to {ip}")
            
            if self.server_ip and ip != self.server_ip:
                self.print_warning(f"Domain resolves to {ip}, but server is at {self.server_ip}")
                self.print_info("This could indicate DNS is not pointing to your server")
            elif self.server_ip and ip == self.server_ip:
                self.print_success("DNS correctly points to your server")
                
            return True, ip
        except socket.gaierror as e:
            self.print_error(f"DNS resolution failed: {e}")
            self.print_info("Check your domain's DNS settings")
            return False, None
    
    def check_http_connectivity(self):
        """Check HTTP connectivity to the domain"""
        self.print_header("HTTP Connectivity Check")
        
        # Test HTTP
        try:
            response = requests.get(f"http://{self.domain}/health", timeout=10)
            if response.status_code == 200:
                self.print_success(f"HTTP access to {self.domain}/health successful")
                self.print_info(f"Response: {response.text.strip()}")
            else:
                self.print_warning(f"HTTP access returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.print_error(f"Cannot connect to {self.domain} via HTTP")
            self.print_info("Check if the server is accessible and nginx is running")
        except requests.exceptions.Timeout:
            self.print_error(f"HTTP request to {self.domain} timed out")
        except Exception as e:
            self.print_error(f"HTTP request failed: {e}")
        
        # Test HTTPS
        try:
            response = requests.get(f"https://{self.domain}/health", timeout=10, verify=False)
            if response.status_code == 200:
                self.print_success(f"HTTPS access to {self.domain}/health successful")
            else:
                self.print_warning(f"HTTPS access returned status {response.status_code}")
        except requests.exceptions.SSLError:
            self.print_info(f"HTTPS not configured for {self.domain} (normal for new deployments)")
        except requests.exceptions.ConnectionError:
            self.print_info(f"HTTPS not available for {self.domain}")
        except Exception as e:
            self.print_info(f"HTTPS check: {e}")
    
    def check_port_accessibility(self):
        """Check if ports 80 and 443 are accessible"""
        self.print_header("Port Accessibility Check")
        
        if not self.server_ip:
            dns_success, resolved_ip = self.check_dns_resolution()
            if dns_success:
                self.server_ip = resolved_ip
            else:
                self.print_warning("Cannot check ports without server IP")
                return
        
        # Check port 80
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.server_ip, 80))
            sock.close()
            
            if result == 0:
                self.print_success(f"Port 80 is accessible on {self.server_ip}")
            else:
                self.print_error(f"Port 80 is not accessible on {self.server_ip}")
                self.print_info("Check firewall settings and nginx configuration")
        except Exception as e:
            self.print_error(f"Error checking port 80: {e}")
        
        # Check port 443
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.server_ip, 443))
            sock.close()
            
            if result == 0:
                self.print_success(f"Port 443 is accessible on {self.server_ip}")
            else:
                self.print_info(f"Port 443 is not accessible on {self.server_ip} (normal without SSL)")
        except Exception as e:
            self.print_info(f"Port 443 check: {e}")
    
    def check_common_issues(self):
        """Check for common configuration issues"""
        self.print_header("Common Issues Check")
        
        # Check if using localhost in nginx config
        exit_code, stdout, stderr = self.run_command("curl -s http://localhost/health")
        if exit_code == 0:
            self.print_success("Server responds to localhost requests")
        else:
            self.print_error("Server doesn't respond to localhost requests")
            self.print_info("Check if nginx and backend services are running")
        
        # Check server load
        exit_code, stdout, stderr = self.run_command("curl -I -s http://localhost")
        if "nginx" in stdout.lower():
            self.print_success("Nginx is serving requests")
        else:
            self.print_warning("Nginx may not be properly configured")
    
    def generate_report(self):
        """Generate a comprehensive diagnostic report"""
        self.print_header(f"Domain Diagnostic Report for {self.domain}")
        
        print(f"{Colors.BOLD}Target Domain:{Colors.END} {self.domain}")
        if self.server_ip:
            print(f"{Colors.BOLD}Server IP:{Colors.END} {self.server_ip}")
        
        # Run all checks
        self.check_dns_resolution()
        self.check_port_accessibility()
        self.check_http_connectivity()
        self.check_common_issues()
        
        # Provide recommendations
        self.print_header("Recommendations")
        
        print(f"{Colors.BOLD}If your domain is not accessible:{Colors.END}")
        print("1. Ensure DNS A record points to your server IP")
        print("2. Check firewall allows HTTP (port 80) and HTTPS (port 443)")
        print("3. Verify nginx is running: systemctl status nginx")
        print("4. Check nginx configuration: nginx -t")
        print("5. Ensure backend service is running: systemctl status projectmeats")
        print("6. Review nginx logs: tail -f /var/log/nginx/error.log")
        print("7. Consider DNS propagation delay (can take up to 48 hours)")
        
        print(f"\n{Colors.BOLD}Quick fixes to try:{Colors.END}")
        print("• Restart nginx: sudo systemctl restart nginx")
        print("• Check domain DNS at: https://dnschecker.org/")
        print(f"• Test direct IP access: http://{self.server_ip}/health")


def main():
    parser = argparse.ArgumentParser(description="Diagnose domain accessibility issues")
    parser.add_argument("--domain", required=True, help="Domain to diagnose")
    parser.add_argument("--server", help="Server IP address")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    diagnostic = DomainDiagnostic(args.domain, args.server)
    diagnostic.generate_report()


if __name__ == "__main__":
    main()