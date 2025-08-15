#!/usr/bin/env python3
"""
Quick Domain Verification Tool
=============================

This tool quickly checks if a domain is accessible from external networks.
Use this after deployment to verify your domain is working correctly.

Usage:
    python verify_domain.py meatscentral.com
    python verify_domain.py meatscentral.com --check-ssl
"""

import argparse
import requests
import socket
import sys
import time
from urllib.parse import urlparse


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def check_domain(domain, check_ssl=False, verbose=False):
    """Check if domain is accessible"""
    print(f"{Colors.BOLD}Checking domain: {domain}{Colors.END}\n")
    
    # 1. DNS Resolution
    try:
        ip = socket.gethostbyname(domain)
        print(f"{Colors.GREEN}✓ DNS Resolution: {domain} → {ip}{Colors.END}")
    except socket.gaierror:
        print(f"{Colors.RED}✗ DNS Resolution: Failed to resolve {domain}{Colors.END}")
        return False
    
    # 2. HTTP Check
    try:
        response = requests.get(f"http://{domain}/health", timeout=10)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✓ HTTP Access: {domain} is accessible{Colors.END}")
            if verbose:
                print(f"  Response: {response.text.strip()}")
        else:
            print(f"{Colors.YELLOW}⚠ HTTP Access: Status {response.status_code}{Colors.END}")
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ HTTP Access: Connection failed{Colors.END}")
        return False
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}✗ HTTP Access: Request timed out{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗ HTTP Access: {e}{Colors.END}")
        return False
    
    # 3. HTTPS Check (if requested)
    if check_ssl:
        try:
            response = requests.get(f"https://{domain}/health", timeout=10)
            if response.status_code == 200:
                print(f"{Colors.GREEN}✓ HTTPS Access: SSL certificate working{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠ HTTPS Access: Status {response.status_code}{Colors.END}")
        except requests.exceptions.SSLError:
            print(f"{Colors.YELLOW}⚠ HTTPS Access: SSL certificate issue{Colors.END}")
        except requests.exceptions.ConnectionError:
            print(f"{Colors.YELLOW}⚠ HTTPS Access: HTTPS not configured{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠ HTTPS Access: {e}{Colors.END}")
    
    # 4. Frontend Check
    try:
        response = requests.get(f"http://{domain}", timeout=10)
        if response.status_code == 200 and 'ProjectMeats' in response.text:
            print(f"{Colors.GREEN}✓ Frontend: Application is loading{Colors.END}")
        elif response.status_code == 200:
            print(f"{Colors.YELLOW}⚠ Frontend: Page loads but may not be ProjectMeats{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠ Frontend: Status {response.status_code}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}✗ Frontend: {e}{Colors.END}")
    
    print(f"\n{Colors.GREEN}Domain verification completed!{Colors.END}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Verify domain accessibility")
    parser.add_argument("domain", help="Domain to verify")
    parser.add_argument("--check-ssl", action="store_true", help="Check SSL certificate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Remove protocol if provided
    domain = args.domain.replace('http://', '').replace('https://', '').split('/')[0]
    
    success = check_domain(domain, args.check_ssl, args.verbose)
    
    if not success:
        print(f"\n{Colors.RED}Domain verification failed!{Colors.END}")
        print(f"Try running: python diagnose_domain_access.py --domain {domain}")
        sys.exit(1)


if __name__ == "__main__":
    main()