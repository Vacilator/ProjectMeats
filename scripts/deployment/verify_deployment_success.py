#!/usr/bin/env python3
"""
ProjectMeats Deployment Success Verification Tool
=================================================

This script verifies that a ProjectMeats deployment actually succeeded and 
the application is accessible. Use this to confirm deployment status.

Usage:
    python verify_deployment_success.py --domain meatscentral.com
    python verify_deployment_success.py --server 167.99.155.140
"""

import argparse
import sys
import subprocess
import time
import requests
from urllib.parse import urlparse

class DeploymentVerifier:
    def __init__(self, domain=None, server_ip=None):
        self.domain = domain
        self.server_ip = server_ip
        self.checks_passed = 0
        self.total_checks = 0
        
    def log(self, message, level="INFO"):
        colors = {
            "SUCCESS": "\033[92m",
            "ERROR": "\033[91m", 
            "WARNING": "\033[93m",
            "INFO": "\033[94m",
            "END": "\033[0m"
        }
        
        if level in colors:
            print(f"{colors[level]}[{level}]{colors['END']} {message}")
        else:
            print(f"[{level}] {message}")
    
    def run_command(self, cmd):
        """Run a system command and return result"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    def check_domain_resolution(self):
        """Check if domain resolves to an IP"""
        self.total_checks += 1
        self.log(f"Checking DNS resolution for {self.domain}...")
        
        exit_code, stdout, stderr = self.run_command(f"nslookup {self.domain}")
        if exit_code != 0:
            self.log(f"✗ DNS resolution failed for {self.domain}", "ERROR")
            self.log(f"Error: {stderr}", "ERROR")
            return False
        
        # Extract IP from nslookup output
        lines = stdout.split('\n')
        for line in lines:
            if 'Address:' in line and '::' not in line and '#53' not in line:
                ip = line.split('Address:')[1].strip()
                self.log(f"✓ Domain {self.domain} resolves to {ip}", "SUCCESS")
                self.server_ip = ip
                self.checks_passed += 1
                return True
        
        self.log(f"✗ Could not extract IP from DNS lookup", "ERROR")
        return False
    
    def check_http_accessibility(self):
        """Check if the website is accessible via HTTP"""
        self.total_checks += 1
        target = self.domain or self.server_ip
        
        if not target:
            self.log("No domain or server IP provided", "ERROR")
            return False
        
        self.log(f"Checking HTTP accessibility for {target}...")
        
        urls_to_test = [
            f"http://{target}/",
            f"http://{target}/health",
            f"http://{target}/api/",
        ]
        
        for url in urls_to_test:
            try:
                self.log(f"Testing: {url}")
                response = requests.get(url, timeout=10, allow_redirects=True)
                
                if response.status_code == 200:
                    self.log(f"✓ {url} responded with 200 OK", "SUCCESS")
                    self.checks_passed += 1
                    return True
                elif 300 <= response.status_code < 400:
                    self.log(f"✓ {url} responded with redirect ({response.status_code}) - likely HTTPS redirect", "SUCCESS")
                    self.checks_passed += 1
                    return True
                else:
                    self.log(f"⚠ {url} responded with {response.status_code}", "WARNING")
                    
            except requests.exceptions.ConnectionError:
                self.log(f"✗ Connection refused to {url}", "WARNING")
            except requests.exceptions.Timeout:
                self.log(f"✗ Timeout connecting to {url}", "WARNING")
            except Exception as e:
                self.log(f"✗ Error accessing {url}: {e}", "WARNING")
        
        self.log("All HTTP accessibility tests failed", "ERROR")
        return False
    
    def check_https_accessibility(self):
        """Check if HTTPS is working"""
        self.total_checks += 1
        target = self.domain or self.server_ip
        
        if not target:
            return False
            
        self.log(f"Checking HTTPS accessibility for {target}...")
        
        try:
            url = f"https://{target}/"
            response = requests.get(url, timeout=10, verify=True)
            
            if response.status_code == 200:
                self.log(f"✓ HTTPS is working: {url}", "SUCCESS")
                self.checks_passed += 1
                return True
            else:
                self.log(f"⚠ HTTPS responded with {response.status_code}", "WARNING")
                
        except requests.exceptions.SSLError:
            self.log("⚠ SSL certificate issue (normal for new deployments)", "WARNING")
        except requests.exceptions.ConnectionError:
            self.log("⚠ HTTPS connection refused", "WARNING")
        except Exception as e:
            self.log(f"⚠ HTTPS error: {e}", "WARNING")
        
        return False
    
    def check_server_status(self):
        """Check if we can connect to the server directly"""
        if not self.server_ip:
            return True
            
        self.total_checks += 1
        self.log(f"Checking server connectivity to {self.server_ip}...")
        
        exit_code, stdout, stderr = self.run_command(f"ping -c 3 {self.server_ip}")
        if exit_code == 0:
            self.log(f"✓ Server {self.server_ip} is reachable", "SUCCESS")
            self.checks_passed += 1
            return True
        else:
            self.log(f"✗ Server {self.server_ip} is not reachable", "ERROR")
            return False
    
    def check_port_accessibility(self):
        """Check if web ports are accessible"""
        if not self.server_ip:
            return True
            
        self.total_checks += 1
        self.log(f"Checking port accessibility on {self.server_ip}...")
        
        ports_to_check = [80, 443]
        accessible_ports = []
        
        for port in ports_to_check:
            exit_code, stdout, stderr = self.run_command(f"nc -z -w5 {self.server_ip} {port}")
            if exit_code == 0:
                accessible_ports.append(port)
                self.log(f"✓ Port {port} is accessible", "SUCCESS")
            else:
                self.log(f"✗ Port {port} is not accessible", "WARNING")
        
        if accessible_ports:
            self.checks_passed += 1
            return True
        else:
            self.log("No web ports are accessible", "ERROR")
            return False
    
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "=" * 60)
        print("DEPLOYMENT VERIFICATION SUMMARY")
        print("=" * 60)
        
        if self.checks_passed >= 3:
            self.log(f"✓ DEPLOYMENT SUCCESSFUL ({self.checks_passed}/{self.total_checks} checks passed)", "SUCCESS")
            print("\n🎉 Your ProjectMeats deployment is working correctly!")
            if self.domain:
                print(f"🌐 Visit your application: http://{self.domain}")
            elif self.server_ip:
                print(f"🌐 Visit your application: http://{self.server_ip}")
        elif self.checks_passed >= 1:
            self.log(f"⚠ PARTIAL SUCCESS ({self.checks_passed}/{self.total_checks} checks passed)", "WARNING")
            print("\n⚠️  Your deployment is partially working but may have issues.")
            print("This often indicates DNS propagation delays or SSL certificate setup.")
            print("Try again in 10-30 minutes for DNS propagation.")
        else:
            self.log(f"✗ DEPLOYMENT FAILED ({self.checks_passed}/{self.total_checks} checks passed)", "ERROR")
            print("\n❌ Your deployment has not succeeded.")
            print("The deployment orchestrator may have reported false success.")
            print("\nTroubleshooting steps:")
            print("1. Check if the deployment actually completed all steps")
            print("2. Verify DNS configuration if using a custom domain")
            print("3. Check server firewall settings")
            print("4. Re-run the deployment with the fixed orchestrator")
        
        print("=" * 60)
    
    def run_verification(self):
        """Run all verification checks"""
        print("\n" + "🔍" * 30)
        print("ProjectMeats Deployment Verification")  
        print("🔍" * 30)
        
        target = self.domain or self.server_ip
        print(f"\nTarget: {target}")
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run checks
        if self.domain:
            self.check_domain_resolution()
        
        self.check_http_accessibility()
        self.check_https_accessibility()
        self.check_server_status()
        self.check_port_accessibility()
        
        # Print summary
        self.print_summary()
        
        # Return success status for scripting
        return self.checks_passed >= 3


def main():
    parser = argparse.ArgumentParser(
        description="Verify ProjectMeats deployment success",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--domain', 
        help="Domain name to verify (e.g., meatscentral.com)"
    )
    
    parser.add_argument(
        '--server', 
        help="Server IP address to verify (e.g., 167.99.155.140)"
    )
    
    args = parser.parse_args()
    
    if not args.domain and not args.server:
        parser.print_help()
        print("\nError: Must provide either --domain or --server")
        return 1
    
    verifier = DeploymentVerifier(domain=args.domain, server_ip=args.server)
    success = verifier.run_verification()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())