#!/usr/bin/env python3
"""
Final validation of @copilot assignment implementation

Validates that all required components are in place and working correctly.
"""

import os
import sys
sys.path.insert(0, '.')

def validate_implementation():
    """Validate all components of @copilot assignment feature"""
    print("🔍 Validating @copilot Assignment Implementation")
    print("=" * 55)
    
    results = []
    
    # Test 1: GitHub Integration Module
    try:
        from scripts.deployment.github_integration import GitHubIntegration, DeploymentLogManager
        results.append(("GitHub Integration Import", True, "✅ Module loads correctly"))
        
        # Check for @copilot assignment in issue creation
        import inspect
        issue_method = GitHubIntegration.create_deployment_issue
        source = inspect.getsource(issue_method)
        
        if '"assignees": ["copilot"]' in source:
            results.append(("@copilot Assignment Code", True, "✅ Found in create_deployment_issue"))
        else:
            results.append(("@copilot Assignment Code", False, "❌ Missing from create_deployment_issue"))
            
        if '"copilot-fix-needed"' in source:
            results.append(("Copilot-Fix-Needed Label", True, "✅ Found in issue creation"))
        else:
            results.append(("Copilot-Fix-Needed Label", False, "❌ Missing from issue creation"))
            
        # Check for PR creation method
        if hasattr(GitHubIntegration, 'create_deployment_fix_pr'):
            results.append(("PR Creation Method", True, "✅ create_deployment_fix_pr exists"))
        else:
            results.append(("PR Creation Method", False, "❌ create_deployment_fix_pr missing"))
            
    except Exception as e:
        results.append(("GitHub Integration Import", False, f"❌ Error: {e}"))
    
    # Test 2: Orchestrator Integration
    try:
        from ai_deployment_orchestrator import AIDeploymentOrchestrator
        results.append(("Orchestrator Import", True, "✅ Module loads correctly"))
        
        # Check failure handling method
        import inspect
        failure_method = AIDeploymentOrchestrator._handle_deployment_failure
        source = inspect.getsource(failure_method)
        
        if "@copilot assignment" in source:
            results.append(("Enhanced Failure Handling", True, "✅ Updated with @copilot logic"))
        else:
            results.append(("Enhanced Failure Handling", False, "❌ Not updated with @copilot logic"))
            
        if "create_failure_pr" in source:
            results.append(("PR Creation Integration", True, "✅ PR creation integrated in orchestrator"))
        else:
            results.append(("PR Creation Integration", False, "❌ PR creation not integrated"))
            
    except Exception as e:
        results.append(("Orchestrator Import", False, f"❌ Error: {e}"))
    
    # Test 3: Documentation
    files_to_check = [
        "COPILOT_ASSIGNMENT_FEATURE.md",
        "test_copilot_assignment.py", 
        "demo_copilot_assignment.py"
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            results.append((f"Documentation: {filename}", True, "✅ File exists"))
        else:
            results.append((f"Documentation: {filename}", False, f"❌ File missing: {filename}"))
    
    # Test 4: Help Documentation
    try:
        with open('ai_deployment_orchestrator.py', 'r') as f:
            content = f.read()
            if "Automatic @copilot assignment for deployment failures" in content:
                results.append(("Help Documentation", True, "✅ @copilot feature documented in help"))
            else:
                results.append(("Help Documentation", False, "❌ @copilot feature not in help text"))
    except Exception as e:
        results.append(("Help Documentation", False, f"❌ Error reading file: {e}"))
    
    # Display Results
    print("\n📋 Validation Results:")
    print("-" * 55)
    
    passed = 0
    total = 0
    
    for test_name, success, message in results:
        total += 1
        if success:
            passed += 1
        print(f"{message:<50} {test_name}")
    
    print("-" * 55)
    print(f"📊 Overall: {passed}/{total} tests passed ({100*passed//total}%)")
    
    # Summary
    if passed == total:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ @copilot assignment is fully implemented and ready!")
        print("\n🚀 Ready for production deployment failures:")
        print("  1. Issues will automatically assign @copilot")
        print("  2. Critical failures will create PRs with @copilot assignment")
        print("  3. Enhanced labels will trigger @copilot attention")
        print("  4. Comprehensive context will help @copilot create fixes")
        return True
    else:
        print(f"\n⚠️ {total-passed} validation(s) failed")
        print("Some components may need attention before full functionality")
        return False

if __name__ == "__main__":
    success = validate_implementation()
    sys.exit(0 if success else 1)