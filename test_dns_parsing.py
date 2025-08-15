#!/usr/bin/env python3
"""
Quick test for the enhanced DNS parsing functionality
"""
import subprocess
import re

def test_dns_parsing():
    """Test the enhanced DNS parsing logic"""
    print("🧪 Testing enhanced DNS parsing...")
    
    # Test data that simulates dig output
    test_dig_output = """
; <<>> DiG 9.18.10-2-Debian <<>> google.com A
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 12345
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		300	IN	A	172.217.164.46

;; Query time: 30 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Thu Aug 15 08:00:00 UTC 2024
;; MSG SIZE  rcvd: 55
"""
    
    def parse_dig_output_enhanced(domain, dig_output):
        """Enhanced DNS parsing as specified in problem statement"""
        try:
            # Parse with grep and awk simulation
            lines = dig_output.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith(f'{domain}.') and 'IN' in line and 'A' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        for part in parts:
                            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', part):
                                return part
            return None
        except Exception as e:
            print(f"Enhanced DNS parsing error: {e}")
            return None
    
    # Test the parsing
    result = parse_dig_output_enhanced('google.com', test_dig_output)
    
    if result == '172.217.164.46':
        print("✅ Enhanced DNS parsing works correctly")
        return True
    else:
        print(f"❌ Enhanced DNS parsing failed. Got: {result}")
        return False

def test_dig_availability():
    """Test if dig command is available"""
    print("\n🧪 Testing dig command availability...")
    
    try:
        result = subprocess.run(['dig', '--version'], 
                              capture_output=True, check=True, timeout=10)
        print("✅ dig command is available")
        print(f"Version: {result.stdout.decode().strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ dig command not available")
        return False

if __name__ == "__main__":
    print("🚀 DNS Parsing Tests")
    print("=" * 50)
    
    success = True
    success &= test_dns_parsing()
    success &= test_dig_availability()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All DNS parsing tests passed!")
    else:
        print("❌ Some tests failed")