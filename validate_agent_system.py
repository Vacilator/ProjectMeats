#!/usr/bin/env python3
"""
Validation script for the agent orchestration system.
Tests basic functionality to ensure everything works correctly.
"""

import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd, expect_success=True):
    """Run a command and return output, handling errors appropriately."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if expect_success and result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return None
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"⚠️ Command timed out: {cmd}")
        return None
    except Exception as e:
        print(f"❌ Command error: {cmd} - {e}")
        return None

def test_basic_commands():
    """Test basic orchestration commands."""
    print("🧪 Testing basic commands...")
    
    # Test help command
    output = run_command("make agent-help")
    if output and "Agent Orchestration Commands" in output:
        print("✅ Help command works")
    else:
        print("❌ Help command failed")
        return False
    
    # Test tasks listing
    output = run_command("python agent_orchestrator.py list-tasks")
    if output and ("TASK-" in output or "No available tasks" in output):
        print("✅ Task listing works")
    else:
        print("❌ Task listing failed")
        return False
    
    # Test project status
    output = run_command("python agent_orchestrator.py project-status")
    if output and "ProjectMeats Status" in output:
        print("✅ Project status works")
    else:
        print("❌ Project status failed")
        return False
    
    return True

def test_file_integrity():
    """Test that required files exist and are valid."""
    print("🧪 Testing file integrity...")
    
    required_files = [
        "agent_orchestrator.py",
        "agent_dashboard.py",
        "docs/agent_tasks.json",
        "docs/agent_quick_start_guide.md",
        "docs/agent_workflow_guide.md",
        "docs/agent_examples_guide.md",
        "docs/agent_troubleshooting_faq.md",
        "AGENT_ORCHESTRATION_README.md",
        "AGENT_ORCHESTRATION_DEVELOPER_GUIDE.md"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing file: {file_path}")
            return False
        else:
            print(f"✅ Found: {file_path}")
    
    # Test JSON validity
    try:
        with open("docs/agent_tasks.json", 'r') as f:
            data = json.load(f)
        if "tasks" in data and "agents" in data and "metadata" in data:
            print("✅ JSON file is valid and has correct structure")
        else:
            print("❌ JSON file missing required sections")
            return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON file is invalid: {e}")
        return False
    except Exception as e:
        print(f"❌ Could not read JSON file: {e}")
        return False
    
    return True

def test_task_operations():
    """Test task assignment and update operations."""
    print("🧪 Testing task operations...")
    
    # Test conflict checking (should not fail even if no conflicts)
    output = run_command("python agent_orchestrator.py check-conflicts TASK-001 test_agent")
    if output is not None:
        print("✅ Conflict checking works")
    else:
        print("❌ Conflict checking failed")
        return False
    
    # Test agent status (should work even with no agents)
    output = run_command("python agent_orchestrator.py agent-status")
    if output is not None:
        print("✅ Agent status works")
    else:
        print("❌ Agent status failed")
        return False
    
    return True

def test_documentation_accessibility():
    """Test that documentation is accessible."""
    print("🧪 Testing documentation accessibility...")
    
    # Test that new make commands work
    commands = ["make agent-docs", "make agent-help"]
    
    for cmd in commands:
        output = run_command(cmd)
        if output and len(output) > 50:  # Reasonable output length
            print(f"✅ {cmd} works")
        else:
            print(f"❌ {cmd} failed or has insufficient output")
            return False
    
    return True

def main():
    """Run all validation tests."""
    print("🚀 Validating Agent Orchestration System")
    print("=" * 50)
    
    tests = [
        ("File Integrity", test_file_integrity),
        ("Basic Commands", test_basic_commands),
        ("Task Operations", test_task_operations),
        ("Documentation", test_documentation_accessibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        if test_func():
            print(f"✅ {test_name} - PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} - FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Agent orchestration system is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())