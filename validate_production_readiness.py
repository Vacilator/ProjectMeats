#!/usr/bin/env python3
"""
ProjectMeats Production Readiness Validator
===========================================

This script validates that the repository is ready for production deployment
by testing all the critical components that the CI/CD pipeline expects.

It simulates the deployment validation step that was failing and ensures
all required orchestrator files are present and functional.
"""

import os
import sys
import subprocess
from pathlib import Path


class ProductionValidator:
    """Validates production readiness of ProjectMeats."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = []
        
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log a test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append((test_name, passed, message))
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
    
    def test_required_orchestrator_files(self):
        """Test that all required orchestrator files exist and are valid."""
        print("\n🔍 Testing Required Orchestrator Files")
        print("=" * 50)
        
        required_files = [
            "ai_deployment_orchestrator.py",
            "master_deploy.py", 
            "setup_ai_deployment.py"
        ]
        
        all_files_valid = True
        
        for filename in required_files:
            file_path = self.project_root / filename
            
            # Check file exists
            if not file_path.exists():
                self.log_result(f"{filename} exists", False, f"File not found: {file_path}")
                all_files_valid = False
                continue
            
            # Check syntax is valid
            try:
                subprocess.run([
                    sys.executable, "-m", "py_compile", str(file_path)
                ], check=True, capture_output=True, text=True)
                self.log_result(f"{filename} syntax", True)
            except subprocess.CalledProcessError as e:
                self.log_result(f"{filename} syntax", False, f"Syntax error: {e}")
                all_files_valid = False
            
            # Test execution
            try:
                result = subprocess.run([
                    sys.executable, str(file_path)
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    self.log_result(f"{filename} execution", True)
                else:
                    self.log_result(f"{filename} execution", False, 
                                  f"Exit code: {result.returncode}")
                    all_files_valid = False
            except subprocess.TimeoutExpired:
                self.log_result(f"{filename} execution", False, "Execution timeout")
                all_files_valid = False
            except Exception as e:
                self.log_result(f"{filename} execution", False, f"Execution error: {e}")
                all_files_valid = False
        
        return all_files_valid
    
    def test_deployment_tools(self):
        """Test that deployment tools are accessible."""
        print("\n🚀 Testing Deployment Tools")
        print("=" * 50)
        
        deployment_files = [
            "unified_deployment_tool.py",
            "enhanced_orchestrator.py",
            "agent_orchestrator.py",
            "setup.py"
        ]
        
        all_tools_valid = True
        
        for filename in deployment_files:
            file_path = self.project_root / filename
            
            if file_path.exists():
                # Test syntax
                try:
                    subprocess.run([
                        sys.executable, "-m", "py_compile", str(file_path)
                    ], check=True, capture_output=True, text=True)
                    self.log_result(f"{filename} syntax", True)
                except subprocess.CalledProcessError:
                    self.log_result(f"{filename} syntax", False)
                    all_tools_valid = False
            else:
                self.log_result(f"{filename} exists", False)
                all_tools_valid = False
        
        return all_tools_valid
    
    def test_project_structure(self):
        """Test that the project structure is intact."""
        print("\n📁 Testing Project Structure")
        print("=" * 50)
        
        required_dirs = [
            "backend",
            "frontend", 
            "docs"
        ]
        
        required_files = [
            "README.md",
            "Makefile",
            "setup.py"
        ]
        
        structure_valid = True
        
        for dirname in required_dirs:
            dir_path = self.project_root / dirname
            if dir_path.exists() and dir_path.is_dir():
                self.log_result(f"Directory {dirname}", True)
            else:
                self.log_result(f"Directory {dirname}", False, f"Missing: {dir_path}")
                structure_valid = False
        
        for filename in required_files:
            file_path = self.project_root / filename
            if file_path.exists():
                self.log_result(f"File {filename}", True)
            else:
                self.log_result(f"File {filename}", False, f"Missing: {file_path}")
                structure_valid = False
        
        return structure_valid
    
    def test_cicd_simulation(self):
        """Simulate the CI/CD deployment validation step."""
        print("\n🔄 Simulating CI/CD Deployment Validation")
        print("=" * 50)
        
        # This replicates the exact check from the failed CI/CD run
        validation_script = '''
# Check if AI deployment orchestrator exists and is valid
if [ -f "ai_deployment_orchestrator.py" ]; then
  echo "✅ AI Deployment Orchestrator (PRIMARY) exists"
  python3 -m py_compile ai_deployment_orchestrator.py
  echo "✅ AI orchestrator syntax is valid"
else
  echo "❌ ai_deployment_orchestrator.py not found"
  exit 1
fi

# Check unified deployment script
if [ -f "master_deploy.py" ]; then
  echo "✅ Master Deploy System (SECONDARY) exists"
  python3 -m py_compile master_deploy.py
  echo "✅ Master deploy syntax is valid"
else
  echo "❌ master_deploy.py not found"
  exit 1
fi

# Check setup wizard
if [ -f "setup_ai_deployment.py" ]; then
  echo "✅ AI Setup Wizard exists"
  python3 -m py_compile setup_ai_deployment.py
  echo "✅ Setup wizard syntax is valid"
else
  echo "❌ setup_ai_deployment.py not found"
  exit 1
fi
'''
        
        try:
            result = subprocess.run([
                "bash", "-c", validation_script
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result("CI/CD Deployment Validation", True, "All orchestrator files validated")
                print("\n📋 CI/CD Output:")
                print(result.stdout)
                return True
            else:
                self.log_result("CI/CD Deployment Validation", False, 
                              f"Exit code: {result.returncode}")
                print("\n❌ CI/CD Output:")
                print(result.stdout)
                print(result.stderr)
                return False
        except Exception as e:
            self.log_result("CI/CD Deployment Validation", False, f"Error: {e}")
            return False
    
    def generate_report(self):
        """Generate a final validation report."""
        print("\n📊 Production Readiness Report")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for _, passed, _ in self.results if passed)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for test_name, passed, message in self.results:
                if not passed:
                    print(f"  • {test_name}: {message}")
        
        production_ready = failed_tests == 0
        
        print(f"\n{'🚀 PRODUCTION READY' if production_ready else '⚠️ NOT PRODUCTION READY'}")
        
        return production_ready
    
    def run_validation(self):
        """Run complete validation suite."""
        print("🔍 ProjectMeats Production Readiness Validation")
        print("=" * 60)
        
        # Run all validation tests
        orchestrator_valid = self.test_required_orchestrator_files()
        tools_valid = self.test_deployment_tools()
        structure_valid = self.test_project_structure()
        cicd_valid = self.test_cicd_simulation()
        
        # Generate final report
        production_ready = self.generate_report()
        
        return production_ready


def main():
    """Main validation entry point."""
    validator = ProductionValidator()
    
    if validator.run_validation():
        print("\n✅ Repository is ready for production deployment!")
        return 0
    else:
        print("\n❌ Repository needs fixes before production deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())