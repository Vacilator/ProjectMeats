#!/usr/bin/env python3
"""
ProjectMeats Unified Deployment Tool
===================================

🚀 THE AUTONOMOUS DEPLOYMENT SOLUTION FOR PROJECTMEATS 🚀

A truly intelligent, autonomous deployment tool that:
- Automatically detects what needs to be done
- Provides intuitive guidance for any skill level
- Handles all deployment, diagnostic, and management tasks
- Self-heals common issues automatically

Author: ProjectMeats AI Assistant
Version: 2.0 - Autonomous & Intuitive
"""

import os
import sys
import json
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import platform

# ============================================================================
# CORE CONFIGURATION AND TYPES
# ============================================================================

class Colors:
    """Clean terminal colors"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class DeploymentMode(Enum):
    """Available deployment modes"""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    LOCAL = "local"


class OperationType(Enum):
    """Available operation types"""
    DEPLOY = "deploy"
    DIAGNOSE = "diagnose"
    FIX = "fix"
    STATUS = "status"
    CLEAN = "clean"


@dataclass
class SystemState:
    """Current system state information"""
    python_installed: bool = False
    node_installed: bool = False
    git_installed: bool = False
    services_running: List[str] = None
    domain_accessible: bool = False
    deployment_exists: bool = False
    
    def __post_init__(self):
        if self.services_running is None:
            self.services_running = []


@dataclass
class DeploymentConfig:
    """Simplified deployment configuration"""
    domain: Optional[str] = None
    server: Optional[str] = None
    github_user: Optional[str] = None
    github_token: Optional[str] = None
    auto_mode: bool = False
    interactive: bool = False


# ============================================================================
# AUTONOMOUS SYSTEM INTELLIGENCE
# ============================================================================

class SystemAnalyzer:
    """Intelligent system analysis and recommendations"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
    
    def analyze_system(self) -> Tuple[SystemState, List[str]]:
        """Analyze current system state and return recommendations"""
        state = SystemState()
        recommendations = []
        
        # Check core dependencies
        state.python_installed = self._check_command("python3", "--version")
        state.node_installed = self._check_command("node", "--version")
        state.git_installed = self._check_command("git", "--version")
        
        # Check if deployment exists
        state.deployment_exists = self._check_deployment_exists()
        
        # Check services
        state.services_running = self._get_running_services()
        
        # Generate recommendations
        if not state.python_installed:
            recommendations.append("Install Python 3")
        if not state.node_installed:
            recommendations.append("Install Node.js (or fix conflicts)")
        if not state.git_installed:
            recommendations.append("Install Git")
        if not state.deployment_exists:
            recommendations.append("Deploy ProjectMeats")
        elif len(state.services_running) < 2:
            recommendations.append("Check service status and restart if needed")
        
        return state, recommendations
    
    def _check_command(self, command: str, *args) -> bool:
        """Check if a command exists and works"""
        try:
            result = subprocess.run([command] + list(args), 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_deployment_exists(self) -> bool:
        """Check if ProjectMeats is already deployed"""
        common_paths = [
            "/opt/projectmeats",
            "/var/www/projectmeats", 
            "/home/projectmeats"
        ]
        return any(Path(p).exists() for p in common_paths)
    
    def _get_running_services(self) -> List[str]:
        """Get list of running ProjectMeats-related services"""
        services = ["nginx", "postgresql", "projectmeats"]
        running = []
        
        for service in services:
            try:
                result = subprocess.run(["systemctl", "is-active", service],
                                      capture_output=True, timeout=3)
                if result.returncode == 0 and b"active" in result.stdout:
                    running.append(service)
            except:
                pass
        
        return running


# ============================================================================
# AUTONOMOUS OPERATION EXECUTOR
# ============================================================================

class AutonomousExecutor:
    """Handles autonomous execution of operations"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.analyzer = SystemAnalyzer()
    
    def auto_deploy(self, config: DeploymentConfig) -> bool:
        """Autonomous deployment with intelligent decision making"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🚀 Starting Autonomous Deployment{Colors.END}")
        
        # Analyze system first
        state, recommendations = self.analyzer.analyze_system()
        
        if recommendations:
            print(f"\n{Colors.YELLOW}🔍 System analysis found some issues to address first:{Colors.END}")
            for rec in recommendations:
                print(f"  • {rec}")
            
            if not config.auto_mode:
                response = input(f"\n{Colors.CYAN}Proceed with automatic fixes? (y/N): {Colors.END}")
                if response.lower() != 'y':
                    print(f"{Colors.YELLOW}Deployment cancelled by user{Colors.END}")
                    return False
            
            # Auto-fix issues
            if not self._auto_fix_issues(state):
                print(f"{Colors.RED}❌ Failed to fix all issues automatically{Colors.END}")
                return False
        
        # Execute deployment
        return self._execute_deployment(config)
    
    def smart_diagnose(self, config: DeploymentConfig) -> bool:
        """Smart diagnostic that focuses on likely issues"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 Smart System Diagnosis{Colors.END}")
        
        state, recommendations = self.analyzer.analyze_system()
        
        print(f"\n{Colors.CYAN}📋 System Status:{Colors.END}")
        print(f"  Python 3: {'✅' if state.python_installed else '❌'}")
        print(f"  Node.js:  {'✅' if state.node_installed else '❌'}")
        print(f"  Git:      {'✅' if state.git_installed else '❌'}")
        print(f"  Deployment: {'✅' if state.deployment_exists else '❌'}")
        print(f"  Services: {len(state.services_running)}/3 running")
        
        if recommendations:
            print(f"\n{Colors.YELLOW}🎯 Recommendations:{Colors.END}")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
            
            print(f"\n{Colors.CYAN}💡 Run with --fix to apply automatic fixes{Colors.END}")
            return False
        else:
            print(f"\n{Colors.GREEN}✅ All systems appear healthy!{Colors.END}")
            return True
    
    def intelligent_fix(self, config: DeploymentConfig) -> bool:
        """Intelligent auto-fix that addresses the most likely issues"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🛠️ Intelligent Auto-Fix{Colors.END}")
        
        state, _ = self.analyzer.analyze_system()
        return self._auto_fix_issues(state)
    
    def _auto_fix_issues(self, state: SystemState) -> bool:
        """Apply automatic fixes based on system state"""
        fixes_applied = 0
        
        # Fix Node.js conflicts (common issue)
        if not state.node_installed:
            print(f"{Colors.CYAN}🔧 Fixing Node.js installation...{Colors.END}")
            if self._run_script("fix_nodejs.sh"):
                print(f"{Colors.GREEN}  ✅ Node.js fixed{Colors.END}")
                fixes_applied += 1
            else:
                print(f"{Colors.YELLOW}  ⚠️ Node.js fix had issues{Colors.END}")
        
        # Run domain access fixes if available
        domain_fix_script = self.script_dir / "deprecated_deployment_scripts" / "fix_meatscentral_access.py"
        if domain_fix_script.exists():
            print(f"{Colors.CYAN}🔧 Running domain access fixes...{Colors.END}")
            if self._run_script(str(domain_fix_script), timeout=60):
                print(f"{Colors.GREEN}  ✅ Domain access fixed{Colors.END}")
                fixes_applied += 1
        
        return fixes_applied > 0
    
    def _execute_deployment(self, config: DeploymentConfig) -> bool:
        """Execute the actual deployment"""
        print(f"\n{Colors.YELLOW}📋 Executing deployment script...{Colors.END}")
        
        # Set environment variables
        env = os.environ.copy()
        if config.domain:
            env['DOMAIN'] = config.domain
        if config.server:
            env['SERVER_IP'] = config.server
        if config.github_user:
            env['GITHUB_USER'] = config.github_user
        if config.github_token:
            env['GITHUB_TOKEN'] = config.github_token
        
        # Execute deployment script
        script_path = self.script_dir / "one_click_deploy.sh"
        if not script_path.exists():
            print(f"{Colors.RED}❌ Deployment script not found{Colors.END}")
            return False
        
        try:
            result = subprocess.run([str(script_path)], env=env, check=False)
            success = result.returncode == 0
            
            if success:
                print(f"\n{Colors.BOLD}{Colors.GREEN}✅ Deployment completed successfully!{Colors.END}")
            else:
                print(f"\n{Colors.BOLD}{Colors.RED}❌ Deployment failed{Colors.END}")
            
            return success
            
        except Exception as e:
            print(f"{Colors.RED}❌ Deployment error: {e}{Colors.END}")
            return False
    
    def _run_script(self, script_name: str, timeout: int = 120) -> bool:
        """Run a script with timeout and error handling"""
        script_path = self.script_dir / script_name
        if not script_path.exists():
            return False
        
        try:
            if script_name.endswith('.sh'):
                result = subprocess.run(["bash", str(script_path)], 
                                      capture_output=True, timeout=timeout)
            else:
                result = subprocess.run(["python3", str(script_path)], 
                                      capture_output=True, timeout=timeout)
            return result.returncode == 0
        except:
            return False


# ============================================================================
# INTUITIVE USER INTERFACE
# ============================================================================

class IntuitiveInterface:
    """Provides an intuitive user interface"""
    
    def __init__(self):
        self.executor = AutonomousExecutor()
        self.analyzer = SystemAnalyzer()
    
    def interactive_mode(self) -> bool:
        """Interactive mode for guided setup"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}🧙‍♂️ ProjectMeats Interactive Setup Wizard{Colors.END}")
        print(f"{Colors.CYAN}This wizard will guide you through deployment step by step.{Colors.END}")
        
        # Quick system check
        state, recommendations = self.analyzer.analyze_system()
        
        if recommendations:
            print(f"\n{Colors.YELLOW}⚠️ Some issues were detected:{Colors.END}")
            for rec in recommendations:
                print(f"  • {rec}")
            
            fix_response = input(f"\n{Colors.CYAN}Would you like me to fix these automatically? (Y/n): {Colors.END}")
            if fix_response.lower() != 'n':
                self.executor._auto_fix_issues(state)
        
        # Gather configuration
        config = DeploymentConfig()
        
        print(f"\n{Colors.BOLD}📋 Deployment Configuration{Colors.END}")
        
        # Domain
        config.domain = input(f"{Colors.CYAN}Enter your domain name (e.g., meatscentral.com): {Colors.END}").strip()
        if not config.domain:
            print(f"{Colors.YELLOW}No domain provided - deployment will use server IP{Colors.END}")
        
        # Auto mode
        auto_response = input(f"{Colors.CYAN}Use automatic configuration? (Y/n): {Colors.END}")
        config.auto_mode = auto_response.lower() != 'n'
        
        if not config.auto_mode:
            config.server = input(f"{Colors.CYAN}Server IP (optional): {Colors.END}").strip()
            config.github_user = input(f"{Colors.CYAN}GitHub username (optional): {Colors.END}").strip()
            
            if config.github_user:
                config.github_token = input(f"{Colors.CYAN}GitHub token (optional): {Colors.END}").strip()
        
        # Execute deployment
        print(f"\n{Colors.BOLD}🚀 Starting deployment...{Colors.END}")
        return self.executor.auto_deploy(config)
    
    def show_smart_help(self):
        """Show context-aware help"""
        print(f"""
{Colors.BOLD}{Colors.BLUE}🚀 ProjectMeats Unified Deployment Tool{Colors.END}

{Colors.BOLD}🎯 QUICK COMMANDS:{Colors.END}
  {Colors.GREEN}python3 unified_deployment_tool.py{Colors.END}
    → Interactive setup wizard (recommended for beginners)

  {Colors.GREEN}python3 unified_deployment_tool.py --auto{Colors.END}
    → Fully automatic deployment (detects and fixes issues)

  {Colors.GREEN}python3 unified_deployment_tool.py --diagnose{Colors.END}
    → Smart system diagnosis with recommendations

  {Colors.GREEN}python3 unified_deployment_tool.py --fix{Colors.END}
    → Intelligent auto-fix for common issues

{Colors.BOLD}🔧 DEPLOYMENT MODES:{Colors.END}
  --production     Production deployment (default)
  --staging        Staging environment
  --development    Development setup
  --local          Local development

{Colors.BOLD}🛠️ OPERATIONS:{Colors.END}
  --diagnose       Smart system analysis
  --fix            Intelligent auto-repair
  --status         Quick health check
  --clean          Clean environment

{Colors.BOLD}⚙️ OPTIONS:{Colors.END}
  --domain=NAME    Your domain name
  --server=IP      Server IP address
  --auto           Automatic mode (no prompts)
  --interactive    Step-by-step wizard

{Colors.BOLD}💡 EXAMPLES:{Colors.END}
  # Interactive setup (recommended)
  sudo python3 unified_deployment_tool.py

  # One-command deployment
  sudo python3 unified_deployment_tool.py --auto --domain=mysite.com

  # Fix issues automatically
  sudo python3 unified_deployment_tool.py --fix

  # Check what's wrong
  python3 unified_deployment_tool.py --diagnose

{Colors.CYAN}The tool automatically detects what needs to be done and guides you through it.{Colors.END}
""")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def create_parser():
    """Create streamlined argument parser"""
    parser = argparse.ArgumentParser(
        description="ProjectMeats Unified Deployment Tool - Autonomous & Intuitive",
        add_help=False
    )
    
    # Primary modes
    parser.add_argument("--production", action="store_true", help="Production deployment")
    parser.add_argument("--staging", action="store_true", help="Staging deployment")  
    parser.add_argument("--development", action="store_true", help="Development setup")
    parser.add_argument("--local", action="store_true", help="Local development")
    
    # Operations
    parser.add_argument("--diagnose", action="store_true", help="Smart system diagnosis")
    parser.add_argument("--fix", action="store_true", help="Intelligent auto-fix")
    parser.add_argument("--status", action="store_true", help="Quick status check")
    parser.add_argument("--clean", action="store_true", help="Clean environment")
    
    # Configuration
    parser.add_argument("--domain", help="Domain name")
    parser.add_argument("--server", help="Server IP address")
    parser.add_argument("--github-user", help="GitHub username")
    parser.add_argument("--github-token", help="GitHub token")
    
    # Modes
    parser.add_argument("--auto", action="store_true", help="Automatic mode")
    parser.add_argument("--interactive", action="store_true", help="Interactive wizard")
    
    # Help
    parser.add_argument("--help", "-h", action="store_true", help="Show help")
    
    return parser


def main():
    """Main entry point with autonomous intelligence"""
    parser = create_parser()
    args = parser.parse_args()
    
    interface = IntuitiveInterface()
    
    # Handle help or no arguments
    if args.help or len(sys.argv) == 1:
        if len(sys.argv) == 1:
            # No arguments - start interactive mode
            return interface.interactive_mode()
        else:
            # Explicit help request
            interface.show_smart_help()
            return 0
    
    # Create configuration
    config = DeploymentConfig(
        domain=args.domain,
        server=args.server,
        github_user=args.github_user,
        github_token=args.github_token,
        auto_mode=args.auto,
        interactive=args.interactive
    )
    
    try:
        # Route to appropriate handler
        if args.interactive:
            return interface.interactive_mode()
        elif args.diagnose:
            success = interface.executor.smart_diagnose(config)
            return 0 if success else 1
        elif args.fix:
            success = interface.executor.intelligent_fix(config)
            return 0 if success else 1
        elif args.status:
            # Quick status check
            state, recommendations = interface.analyzer.analyze_system()
            if recommendations:
                print(f"{Colors.YELLOW}⚠️ Issues found: {len(recommendations)}{Colors.END}")
                return 1
            else:
                print(f"{Colors.GREEN}✅ System healthy{Colors.END}")
                return 0
        elif args.clean:
            # Clean environment
            cleanup_script = Path(__file__).parent / "cleanup_deprecated_scripts.sh"
            if cleanup_script.exists():
                result = subprocess.run(["bash", str(cleanup_script)], check=False)
                return result.returncode
            return 0
        else:
            # Default to deployment
            success = interface.executor.auto_deploy(config)
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Cancelled by user{Colors.END}")
        return 130
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())