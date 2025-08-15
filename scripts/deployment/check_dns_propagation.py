#!/usr/bin/env python3
"""
DNS Propagation Checker for MeatsCentral.com
===========================================

This tool helps diagnose DNS propagation issues specifically for meatscentral.com
when the domain works from some locations but not others.
"""

import socket
import subprocess
import sys
import time
from typing import List, Tuple

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DNSPropagationChecker:
    def __init__(self):
        self.domain = "meatscentral.com"
        self.expected_ip = "167.99.155.140"
        self.dns_servers = [
            ("Google DNS 1", "8.8.8.8"),
            ("Google DNS 2", "8.8.4.4"),
            ("Cloudflare DNS 1", "1.1.1.1"),
            ("Cloudflare DNS 2", "1.0.0.1"),
            ("OpenDNS 1", "208.67.222.222"),
            ("OpenDNS 2", "208.67.220.220"),
            ("Quad9", "9.9.9.9"),
            ("System Default", None)  # Use system default
        ]
    
    def print_header(self, title: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    
    def check_dns_server(self, name: str, dns_server: str = None) -> Tuple[bool, str]:
        """Check DNS resolution using a specific DNS server"""
        try:
            if dns_server:
                # Use nslookup with specific DNS server
                result = subprocess.run(
                    ["nslookup", self.domain, dns_server],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Parse nslookup output to find IP
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if "Name:" in line and self.domain in line:
                        # Look for Address in next few lines
                        for j in range(i+1, min(i+5, len(lines))):
                            if "Address:" in lines[j]:
                                ip = lines[j].split("Address:")[-1].strip()
                                return True, ip
                
                # Alternative parsing for different nslookup formats
                for line in lines:
                    if line.strip().startswith(self.domain):
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                socket.inet_aton(parts[-1])  # Validate IP
                                return True, parts[-1]
                            except socket.error:
                                pass
                
                return False, "No address found"
            else:
                # Use system default resolver
                ip = socket.gethostbyname(self.domain)
                return True, ip
                
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except socket.gaierror:
            return False, "Resolution failed"
        except Exception as e:
            return False, str(e)
    
    def check_all_dns_servers(self):
        """Check DNS resolution across multiple DNS servers"""
        self.print_header("DNS Propagation Check for MeatsCentral.com")
        
        print(f"{Colors.BOLD}Domain:{Colors.END} {self.domain}")
        print(f"{Colors.BOLD}Expected IP:{Colors.END} {self.expected_ip}")
        print(f"{Colors.BOLD}Checking propagation across major DNS providers...{Colors.END}\n")
        
        correct_count = 0
        total_count = 0
        
        for name, dns_server in self.dns_servers:
            success, ip = self.check_dns_server(name, dns_server)
            total_count += 1
            
            if success:
                if ip == self.expected_ip:
                    print(f"{Colors.GREEN}✓ {name:<20} {ip} (CORRECT){Colors.END}")
                    correct_count += 1
                else:
                    print(f"{Colors.RED}✗ {name:<20} {ip} (WRONG - should be {self.expected_ip}){Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠ {name:<20} {ip}{Colors.END}")
        
        print(f"\n{Colors.BOLD}Propagation Status:{Colors.END}")
        percentage = (correct_count / total_count) * 100
        
        if percentage == 100:
            print(f"{Colors.GREEN}✓ DNS fully propagated ({correct_count}/{total_count} servers correct){Colors.END}")
        elif percentage >= 75:
            print(f"{Colors.YELLOW}⚠ DNS mostly propagated ({correct_count}/{total_count} servers correct){Colors.END}")
            print(f"{Colors.YELLOW}  Some users may still experience issues{Colors.END}")
        elif percentage >= 50:
            print(f"{Colors.YELLOW}⚠ DNS partially propagated ({correct_count}/{total_count} servers correct){Colors.END}")
            print(f"{Colors.YELLOW}  Many users will experience issues{Colors.END}")
        else:
            print(f"{Colors.RED}✗ DNS not propagated ({correct_count}/{total_count} servers correct){Colors.END}")
            print(f"{Colors.RED}  Most users will experience issues{Colors.END}")
        
        return percentage
    
    def provide_user_solutions(self, propagation_percentage: float):
        """Provide solutions based on propagation status"""
        self.print_header("Solutions for User")
        
        if propagation_percentage == 100:
            print(f"{Colors.GREEN}Great! DNS is fully propagated.{Colors.END}")
            print("If you still can't access the site, try these:")
            print("1. Clear your browser cache and try again")
            print("2. Try a different browser or incognito mode")
            print("3. Restart your router/modem")
            print("4. Try using a different DNS server temporarily")
        else:
            print(f"{Colors.YELLOW}DNS propagation is still in progress ({propagation_percentage:.0f}% complete).{Colors.END}")
            print(f"{Colors.BOLD}Immediate fixes you can try:{Colors.END}")
            
            print(f"\n{Colors.BOLD}Option 1: Use Direct IP Access{Colors.END}")
            print(f"• Open your browser and go to: http://{self.expected_ip}")
            print(f"• This bypasses DNS entirely")
            
            print(f"\n{Colors.BOLD}Option 2: Change Your DNS Servers{Colors.END}")
            print("• Change your computer's DNS to Google DNS:")
            print("  - Primary: 8.8.8.8")
            print("  - Secondary: 8.8.4.4")
            print("• Or use Cloudflare DNS:")
            print("  - Primary: 1.1.1.1")
            print("  - Secondary: 1.0.0.1")
            
            print(f"\n{Colors.BOLD}Option 3: Wait for Propagation{Colors.END}")
            print("• DNS changes can take 24-48 hours to fully propagate")
            print("• Check back in a few hours")
            
            print(f"\n{Colors.BOLD}How to Change DNS on Different Systems:{Colors.END}")
            print(f"{Colors.BOLD}Windows:{Colors.END}")
            print("1. Go to Network and Internet Settings")
            print("2. Click 'Change adapter options'")
            print("3. Right-click your connection → Properties")
            print("4. Select 'Internet Protocol Version 4 (TCP/IPv4)' → Properties")
            print("5. Select 'Use the following DNS server addresses'")
            print("6. Enter 8.8.8.8 and 8.8.4.4")
            
            print(f"\n{Colors.BOLD}Mac:{Colors.END}")
            print("1. System Preferences → Network")
            print("2. Select your connection → Advanced → DNS")
            print("3. Click + and add 8.8.8.8 and 8.8.4.4")
            
            print(f"\n{Colors.BOLD}Router Level (affects all devices):{Colors.END}")
            print("1. Access your router admin panel (usually 192.168.1.1)")
            print("2. Find DNS settings")
            print("3. Set primary DNS to 8.8.8.8 and secondary to 8.8.4.4")
            print("4. Restart your router")
    
    def check_local_cache(self):
        """Check and provide instructions for clearing local DNS cache"""
        self.print_header("Clear Local DNS Cache")
        
        print("Your computer might have cached old DNS records.")
        print("Try clearing your DNS cache:\n")
        
        print(f"{Colors.BOLD}Windows:{Colors.END}")
        print("1. Open Command Prompt as Administrator")
        print("2. Run: ipconfig /flushdns")
        print("3. Run: ipconfig /release")
        print("4. Run: ipconfig /renew")
        
        print(f"\n{Colors.BOLD}Mac:{Colors.END}")
        print("1. Open Terminal")
        print("2. Run: sudo dscacheutil -flushcache")
        print("3. Run: sudo killall -HUP mDNSResponder")
        
        print(f"\n{Colors.BOLD}Linux:{Colors.END}")
        print("1. Run: sudo systemctl restart systemd-resolved")
        print("2. Or: sudo service nscd restart")
        
        print(f"\n{Colors.BOLD}Browser Cache:{Colors.END}")
        print("1. Clear browser cache and cookies")
        print("2. Try incognito/private browsing mode")
        print("3. Try a different browser")

def main():
    checker = DNSPropagationChecker()
    
    # Check DNS propagation
    propagation_percentage = checker.check_all_dns_servers()
    
    # Provide solutions
    checker.provide_user_solutions(propagation_percentage)
    
    # Cache clearing instructions
    checker.check_local_cache()
    
    print(f"\n{Colors.BOLD}Quick Test:{Colors.END}")
    print(f"Try accessing: http://{checker.expected_ip}/health")
    print("If this works but {checker.domain} doesn't, it's definitely a DNS issue on your end.")

if __name__ == "__main__":
    main()