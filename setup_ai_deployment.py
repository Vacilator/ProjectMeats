#!/usr/bin/env python3
"""
ProjectMeats AI Deployment Orchestrator Setup v2.0
==================================================

Enhanced setup wizard for the AI-driven deployment system, featuring:
- 🤖 Intelligent configuration detection and optimization
- 🔐 Advanced SSH key management with security best practices
- 🌐 Multi-environment server profile configuration
- 📊 AI performance optimization settings
- 🔄 Automated validation and testing capabilities

This setup wizard configures the enhanced AI deployment system with
consolidated features from 5 major releases and intelligent error recovery.

Usage:
    python3 setup_ai_deployment.py
    
Features:
    - AI-powered deployment optimization
    - Predictive error detection and resolution
    - Multi-environment deployment profiles
    - Advanced security configuration
    - Performance monitoring and analytics
"""

import os
import sys
import json
import subprocess
import getpass
from pathlib import Path
from typing import Dict, Any, Optional


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class AIDeploymentSetup:
    """
    Enhanced setup wizard for AI deployment orchestrator v2.0
    
    Features:
    - Intelligent configuration detection
    - AI-powered optimization recommendations
    - Multi-environment profile management
    - Advanced security configuration
    - Performance monitoring setup
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config = {}
        self.ai_features_enabled = True
        self.setup_version = "2.0"
        
    def log(self, message: str, level: str = "INFO"):
        """Colored logging"""
        colors = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "HEADER": Colors.PURPLE + Colors.BOLD
        }
        color = colors.get(level, Colors.BLUE)
        print(f"{color}[{level}] {message}{Colors.END}")
    
    def print_header(self):
        """Print enhanced setup header with AI features"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}")
        print("🤖 ProjectMeats AI Deployment Orchestrator Setup v2.0")
        print(f"{'='*80}{Colors.END}\n")
        
        print(f"{Colors.BOLD}🚀 ENHANCED AI FEATURES:{Colors.END}")
        print(f"  {Colors.GREEN}✅ Intelligent Error Detection & Recovery{Colors.END}")
        print(f"  {Colors.GREEN}✅ Predictive Deployment Analysis{Colors.END}")
        print(f"  {Colors.GREEN}✅ Autonomous Performance Optimization{Colors.END}")
        print(f"  {Colors.GREEN}✅ Real-time Monitoring & Alerting{Colors.END}")
        print(f"  {Colors.GREEN}✅ Multi-Environment Configuration{Colors.END}")
        print(f"  {Colors.GREEN}✅ Consolidated Knowledge from 5 Major Releases{Colors.END}")
        print()
        
        print(f"{Colors.BOLD}📋 SETUP PROCESS:{Colors.END}")
        print(f"  {Colors.CYAN}1.{Colors.END} Dependency validation and installation")
        print(f"  {Colors.CYAN}2.{Colors.END} SSH key generation and security configuration")
        print(f"  {Colors.CYAN}3.{Colors.END} Multi-environment server profile setup")
        print(f"  {Colors.CYAN}4.{Colors.END} AI features configuration and optimization")
        print(f"  {Colors.CYAN}5.{Colors.END} Deployment templates and validation")
        print()
        
        self.log("This wizard will configure the enhanced AI deployment system", "INFO")
        self.log(f"Setup version: {self.setup_version} | AI features: {'Enabled' if self.ai_features_enabled else 'Disabled'}", "INFO")
        print()
        
    def check_dependencies(self):
        """Check and install required dependencies"""
        self.log("Checking dependencies...", "HEADER")
        
        # Check if requirements file exists
        req_file = self.project_root / "ai_deployment_requirements.txt"
        if not req_file.exists():
            self.log("Requirements file not found", "ERROR")
            return False
        
        # Install requirements
        try:
            self.log("Installing required packages...", "INFO")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(req_file)
            ], check=True, capture_output=True)
            self.log("Dependencies installed successfully", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to install dependencies: {e}", "ERROR")
            self.log("Please install manually: pip install -r ai_deployment_requirements.txt", "WARNING")
            return False
    
    def setup_ssh_keys(self):
        """Setup SSH key authentication"""
        self.log("SSH Key Configuration", "HEADER")
        
        ssh_dir = Path.home() / ".ssh"
        ssh_dir.mkdir(exist_ok=True)
        
        # Check for existing keys
        key_files = list(ssh_dir.glob("id_*"))
        private_keys = [f for f in key_files if not f.name.endswith('.pub')]
        
        if private_keys:
            self.log("Existing SSH keys found:", "INFO")
            for i, key in enumerate(private_keys):
                print(f"  {i+1}. {key}")
            
            choice = input(f"\nUse existing key? (1-{len(private_keys)}) or 'n' for new: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(private_keys):
                selected_key = private_keys[int(choice) - 1]
                self.config['ssh_key_file'] = str(selected_key)
                self.log(f"Using key: {selected_key}", "SUCCESS")
                return True
        
        # Generate new key
        create_new = input("Generate new SSH key? [Y/n]: ").lower()
        if create_new != 'n':
            email = input("Enter email for SSH key: ").strip()
            key_name = input("Key name [projectmeats_deploy]: ").strip() or "projectmeats_deploy"
            
            key_path = ssh_dir / key_name
            
            try:
                cmd = [
                    "ssh-keygen", "-t", "ed25519", "-C", email,
                    "-f", str(key_path), "-N", ""
                ]
                subprocess.run(cmd, check=True)
                
                self.config['ssh_key_file'] = str(key_path)
                
                self.log(f"SSH key generated: {key_path}", "SUCCESS")
                self.log(f"Public key: {key_path}.pub", "INFO")
                
                # Display public key
                with open(f"{key_path}.pub", 'r') as f:
                    pub_key = f.read().strip()
                
                print(f"\n{Colors.CYAN}Copy this public key to your server:{Colors.END}")
                print(f"{Colors.YELLOW}{pub_key}{Colors.END}")
                print()
                
                input("Press Enter after adding the key to your server...")
                
                return True
                
            except subprocess.CalledProcessError as e:
                self.log(f"Failed to generate SSH key: {e}", "ERROR")
                return False
        
        return False
    
    def configure_server_profiles(self):
        """Configure server profiles"""
        self.log("Server Profile Configuration", "HEADER")
        
        profiles = {}
        
        while True:
            profile_name = input("\nEnter server profile name (or 'done' to finish): ").strip()
            if profile_name.lower() == 'done':
                break
            
            if not profile_name:
                continue
            
            profile = {}
            profile['hostname'] = input("Server hostname/IP: ").strip()
            profile['username'] = input("SSH username [root]: ").strip() or "root"
            profile['domain'] = input("Domain name (optional): ").strip() or None
            
            # Authentication method
            auth_method = input("Authentication (1=SSH key, 2=password): ").strip()
            if auth_method == "2":
                profile['use_password'] = True
                profile['key_file'] = None
            else:
                profile['use_password'] = False
                profile['key_file'] = self.config.get('ssh_key_file')
            
            # Server specs
            profile['specs'] = {
                'cpu_cores': input("CPU cores [2]: ").strip() or "2",
                'memory_gb': input("Memory GB [4]: ").strip() or "4",
                'storage_gb': input("Storage GB [50]: ").strip() or "50"
            }
            
            profiles[profile_name] = profile
            self.log(f"Profile '{profile_name}' configured", "SUCCESS")
        
        self.config['server_profiles'] = profiles
        return len(profiles) > 0
    
    def configure_deployment_settings(self):
        """Configure deployment settings"""
        self.log("Deployment Settings Configuration", "HEADER")
        
        settings = {}
        
        # Auto-recovery settings
        settings['auto_recovery'] = input("Enable automatic error recovery? [Y/n]: ").lower() != 'n'
        settings['max_retries'] = int(input("Maximum retry attempts [3]: ").strip() or "3")
        settings['retry_delay'] = int(input("Retry delay seconds [5]: ").strip() or "5")
        
        # Backup settings
        settings['backup_on_failure'] = input("Backup on deployment failure? [Y/n]: ").lower() != 'n'
        settings['keep_backups'] = int(input("Number of backups to keep [5]: ").strip() or "5")
        
        # Monitoring settings
        settings['enable_monitoring'] = input("Enable deployment monitoring? [Y/n]: ").lower() != 'n'
        settings['log_level'] = input("Log level (DEBUG/INFO/WARNING/ERROR) [INFO]: ").strip().upper() or "INFO"
        
        # Security settings
        settings['verify_ssl'] = input("Verify SSL certificates? [Y/n]: ").lower() != 'n'
        settings['enable_firewall'] = input("Configure firewall automatically? [Y/n]: ").lower() != 'n'
        
        self.config['deployment'] = settings
        
    def configure_ai_features(self):
        """Configure AI-specific features"""
        self.log("AI Features Configuration", "HEADER")
        
        ai_config = {}
        
        # Error detection
        ai_config['intelligent_error_detection'] = input("Enable intelligent error detection? [Y/n]: ").lower() != 'n'
        ai_config['auto_fix_common_issues'] = input("Auto-fix common deployment issues? [Y/n]: ").lower() != 'n'
        
        # Learning from failures
        ai_config['learn_from_failures'] = input("Learn from deployment failures? [Y/n]: ").lower() != 'n'
        ai_config['share_anonymized_metrics'] = input("Share anonymized metrics for improvement? [y/N]: ").lower() == 'y'
        
        # Advanced features
        ai_config['predictive_scaling'] = input("Enable predictive resource scaling? [y/N]: ").lower() == 'y'
        ai_config['optimization_suggestions'] = input("Provide optimization suggestions? [Y/n]: ").lower() != 'n'
        
        self.config['ai_features'] = ai_config
    
    def generate_deployment_templates(self):
        """Generate deployment templates"""
        self.log("Generating deployment templates...", "INFO")
        
        templates_dir = self.project_root / "deployment_templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Quick deployment template
        quick_template = {
            "name": "Quick Production Deployment",
            "description": "Fast deployment with minimal configuration",
            "steps": [
                "validate_server",
                "install_dependencies", 
                "setup_database",
                "download_application",
                "configure_backend",
                "configure_frontend",
                "setup_webserver",
                "final_verification"
            ],
            "config": {
                "auto_approve": True,
                "skip_ssl": False,
                "enable_monitoring": True
            }
        }
        
        with open(templates_dir / "quick_deployment.json", 'w', encoding='utf-8') as f:
            json.dump(quick_template, f, indent=2)
        
        # Full deployment template
        full_template = {
            "name": "Full Production Deployment",
            "description": "Complete deployment with all security features",
            "steps": [
                "validate_server",
                "setup_authentication",
                "install_dependencies",
                "handle_nodejs_conflicts",
                "setup_database",
                "download_application",
                "configure_backend",
                "configure_frontend", 
                "setup_webserver",
                "setup_services",
                "final_verification"
            ],
            "config": {
                "auto_approve": False,
                "enable_ssl": True,
                "enable_firewall": True,
                "enable_monitoring": True,
                "enable_backups": True
            }
        }
        
        with open(templates_dir / "full_deployment.json", 'w', encoding='utf-8') as f:
            json.dump(full_template, f, indent=2)
        
        self.log("Deployment templates generated", "SUCCESS")
    
    def save_configuration(self):
        """Save configuration to file"""
        config_file = self.project_root / "ai_deployment_config.json"
        
        full_config = {
            "version": "1.0",
            "created": str(os.times()),
            "ssh": {
                "key_file": self.config.get('ssh_key_file'),
                "port": 22,
                "timeout": 30
            },
            "deployment": self.config.get('deployment', {}),
            "ai_features": self.config.get('ai_features', {}),
            "server_profiles": self.config.get('server_profiles', {}),
            "logging": {
                "level": self.config.get('deployment', {}).get('log_level', 'INFO'),
                "max_files": 10,
                "max_size": "50MB"
            }
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=2)
            
            self.log(f"Configuration saved: {config_file}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to save configuration: {e}", "ERROR")
            return False
    
    def create_quick_start_script(self):
        """Verify quick start script exists"""
        script_file = self.project_root / "ai_deploy.sh"
        if script_file.exists():
            self.log(f"Quick start script verified: {script_file}", "SUCCESS")
        else:
            self.log(f"Quick start script missing: {script_file}", "WARNING")
            self.log("Please ensure ai_deploy.sh exists in the project root", "INFO")
    
    def print_completion_message(self):
        """Print setup completion message with clear execution instructions"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}")
        print("[SUCCESS] AI Deployment Orchestrator Setup Complete!")
        print(f"{'='*70}{Colors.END}\n")
        
        self.log("Your AI deployment system is ready to use!", "SUCCESS")
        print()
        
        # Important execution context
        print(f"{Colors.BOLD}{Colors.YELLOW}📍 IMPORTANT: WHERE TO RUN COMMANDS{Colors.END}")
        print(f"  {Colors.CYAN}💻 LOCAL MACHINE{Colors.END}: Run setup and deployment commands from YOUR computer")
        print(f"  {Colors.CYAN}🌐 REMOTE SERVER{Colors.END}: ProjectMeats will be deployed automatically via SSH")
        print(f"  {Colors.CYAN}🔗 CONNECTION{Colors.END}: Commands below connect from local → remote automatically")
        print()
        
        self.log("🚀 Ready to Deploy! Here's how to start:", "HEADER")
        print()
        
        # Environment-specific instructions
        print(f"{Colors.BOLD}🖥️ CHOOSE YOUR ENVIRONMENT:{Colors.END}")
        print()
        
        # Check if ai_deploy.sh exists
        ai_deploy_script = self.project_root / "ai_deploy.sh"
        if ai_deploy_script.exists():
            print(f"  {Colors.PURPLE}Windows PowerShell:{Colors.END}")
            print(f"    python ai_deployment_orchestrator.py --interactive")
            print()
            print(f"  {Colors.PURPLE}Linux/Mac Terminal:{Colors.END}")
            print(f"    ./ai_deploy.sh --interactive")
            print()
            print(f"  {Colors.PURPLE}Git Bash (Windows):{Colors.END}")
            print(f"    ./ai_deploy.sh --interactive")
        else:
            print(f"  {Colors.YELLOW}⚠️  Using Python directly (works on all platforms):{Colors.END}")
            print(f"    python ai_deployment_orchestrator.py --interactive")
        
        print()
        print(f"{Colors.BOLD}📋 EXECUTION WORKFLOW:{Colors.END}")
        print(f"  {Colors.GREEN}1. Test readiness (LOCAL):{Colors.END}")
        print(f"     python test_ai_deployment.py")
        print()
        print(f"  {Colors.GREEN}2. Deploy to server (LOCAL → REMOTE):{Colors.END}")
        if ai_deploy_script.exists():
            print(f"     ./ai_deploy.sh --interactive          # Linux/Mac")
            print(f"     python ai_deployment_orchestrator.py --interactive  # Windows")
        else:
            print(f"     python ai_deployment_orchestrator.py --interactive")
        print()
        print(f"  {Colors.GREEN}3. Verify deployment (LOCAL):{Colors.END}")
        print(f"     curl https://yourdomain.com")
        
        print()
        print(f"{Colors.BOLD}🔧 OTHER DEPLOYMENT OPTIONS:{Colors.END}")
        if ai_deploy_script.exists():
            print(f"  {Colors.CYAN}🎯 Direct deployment:{Colors.END}")
            print(f"    ./ai_deploy.sh --server myserver.com --domain mydomain.com")
            print()
            print(f"  {Colors.CYAN}🧪 Test connection first:{Colors.END}")
            print(f"    ./ai_deploy.sh --test --server myserver.com")
            print()
            print(f"  {Colors.CYAN}🔧 Use predefined profile:{Colors.END}")
            print(f"    ./ai_deploy.sh --profile production")
        
        print()
        print(f"{Colors.BOLD}📚 DETAILED INSTRUCTIONS:{Colors.END}")
        print(f"  {Colors.CYAN}Complete guide:{Colors.END} See EXECUTION_GUIDE.md for step-by-step instructions")
        print(f"  {Colors.CYAN}Environment help:{Colors.END} Windows PowerShell, Linux, Mac specific commands")
        print(f"  {Colors.CYAN}Troubleshooting:{Colors.END} Common issues and solutions by platform")
        
        print()
        self.log("Available Command Options:", "INFO")
        print(f"  {Colors.GREEN}--interactive{Colors.END}     Interactive setup with prompts")
        print(f"  {Colors.GREEN}--server HOST{Colors.END}     Deploy to specific server")
        print(f"  {Colors.GREEN}--domain NAME{Colors.END}     Set domain for SSL")
        print(f"  {Colors.GREEN}--profile NAME{Colors.END}    Use server profile")
        print(f"  {Colors.GREEN}--test{Colors.END}            Test connection only")
        print(f"  {Colors.GREEN}--auto{Colors.END}            Auto-approve all prompts")
        print()
        
        self.log("🔥 Features Enabled:", "INFO")
        
        if self.config.get('ai_features', {}).get('intelligent_error_detection'):
            print(f"  {Colors.GREEN}✅ Intelligent error detection and recovery{Colors.END}")
        
        if self.config.get('deployment', {}).get('auto_recovery'):
            print(f"  {Colors.GREEN}✅ Automatic error recovery{Colors.END}")
        
        if self.config.get('deployment', {}).get('backup_on_failure'):
            print(f"  {Colors.GREEN}✅ Automatic backups on failure{Colors.END}")
        
        if self.config.get('deployment', {}).get('enable_monitoring'):
            print(f"  {Colors.GREEN}✅ Real-time deployment monitoring{Colors.END}")
        
        print()
        self.log("📁 Configuration Files Created:", "INFO")
        print(f"  Config: ai_deployment_config.json")
        print(f"  Templates: deployment_templates/")
        print(f"  Logs: logs/")
        
        # Show server profiles
        profiles = self.config.get('server_profiles', {})
        if profiles:
            print()
            self.log("🌐 Server Profiles Configured:", "INFO")
            for name, profile in profiles.items():
                hostname = profile.get('hostname', 'N/A')
                username = profile.get('username', 'root')
                print(f"  {Colors.CYAN}{name}{Colors.END}: {hostname} ({username})")
        
        print()
        print(f"{Colors.BOLD}{Colors.GREEN}🎉 READY TO DEPLOY! Run the commands above to start.{Colors.END}")
        print()
        self.log("For help and troubleshooting, see: docs/ai_deployment_guide.md", "INFO")
    
    def run(self):
        """Run the setup wizard"""
        try:
            self.print_header()
            
            if not self.check_dependencies():
                return False
            
            if not self.setup_ssh_keys():
                self.log("SSH key setup required for deployment", "ERROR")
                return False
            
            if not self.configure_server_profiles():
                self.log("At least one server profile is required", "ERROR")
                return False
            
            self.configure_deployment_settings()
            self.configure_ai_features()
            self.generate_deployment_templates()
            
            if not self.save_configuration():
                return False
            
            self.create_quick_start_script()
            self.print_completion_message()
            
            return True
            
        except KeyboardInterrupt:
            self.log("\nSetup cancelled by user", "WARNING")
            return False
        except Exception as e:
            self.log(f"Setup failed: {e}", "ERROR")
            return False


if __name__ == "__main__":
    setup = AIDeploymentSetup()
    success = setup.run()
    sys.exit(0 if success else 1)