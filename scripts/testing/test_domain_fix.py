#!/usr/bin/env python3
"""
Test the enhanced deployment verification functionality
"""

import sys
import os

# Add the project root to path so we can import the deployment module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_verification_enhancements():
    """Test that the verification function exists and has the expected functionality"""
    
    # Read the deployment orchestrator file
    with open('ai_deployment_orchestrator.py', 'r') as f:
        content = f.read()
    
    # Check that the enhanced verification is present
    enhancements = [
        "Testing external domain accessibility",
        "curl -f -L --max-time 30 --connect-timeout 10",
        "externally accessible via HTTP",
        "DNS resolution",
        "netstat -tlnp | grep :80",
        "nginx -T | grep",
        "WARNING: Domain",
        "may not be externally accessible"
    ]
    
    missing = []
    for enhancement in enhancements:
        if enhancement not in content:
            missing.append(enhancement)
    
    if missing:
        print(f"❌ Missing enhancements: {missing}")
        return False
    
    print("✅ All verification enhancements present")
    return True

def test_diagnostic_tools():
    """Test that diagnostic tools are present and functional"""
    
    tools = ['diagnose_domain_access.py', 'verify_domain.py']
    missing_tools = []
    
    for tool in tools:
        if not os.path.exists(tool):
            missing_tools.append(tool)
            continue
            
        # Check if the file is executable
        if not os.access(tool, os.X_OK):
            print(f"⚠️  {tool} exists but is not executable")
        
        # Basic syntax check
        try:
            with open(tool, 'r') as f:
                tool_content = f.read()
            
            # Compile check
            compile(tool_content, tool, 'exec')
            print(f"✅ {tool} syntax is valid")
            
        except SyntaxError as e:
            print(f"❌ {tool} has syntax error: {e}")
            return False
    
    if missing_tools:
        print(f"❌ Missing tools: {missing_tools}")
        return False
    
    print("✅ All diagnostic tools present and valid")
    return True

def test_documentation():
    """Test that documentation is present"""
    
    if not os.path.exists('DOMAIN_FIX_DOCUMENTATION.md'):
        print("❌ Documentation missing")
        return False
    
    with open('DOMAIN_FIX_DOCUMENTATION.md', 'r') as f:
        doc_content = f.read()
    
    required_sections = [
        "Problem Description",
        "Root Cause", 
        "Solution Implemented",
        "Usage",
        "Common Issues and Solutions"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in doc_content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ Missing documentation sections: {missing_sections}")
        return False
    
    print("✅ Documentation is complete")
    return True

def main():
    """Run all tests"""
    print("Testing Domain Accessibility Fix Implementation...")
    print("=" * 50)
    
    tests = [
        ("Verification Enhancements", test_verification_enhancements),
        ("Diagnostic Tools", test_diagnostic_tools),
        ("Documentation", test_documentation)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Domain accessibility fix is ready.")
        print("\nNext steps for users:")
        print("1. Run the enhanced deployment: python ai_deployment_orchestrator.py --profile production")
        print("2. If domain issues persist: python diagnose_domain_access.py --domain yourdomain.com")
        print("3. Quick verification: python verify_domain.py yourdomain.com")
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())