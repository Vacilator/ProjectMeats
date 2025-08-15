#!/usr/bin/env python3
"""
ProjectMeats Production Deployment Launcher
==========================================

This is a simplified launcher script that uses the AI Deployment Orchestrator
as the primary deployment tool. It provides easy access to the most common
deployment scenarios with industry best practices.

Usage:
    # Quick Docker deployment
    ./deploy.py --server myserver.com --domain mydomain.com --docker
    
    # Interactive setup with Docker  
    ./deploy.py --interactive
    
    # Standard deployment (systemd)
    ./deploy.py --server myserver.com --domain mydomain.com
    
    # With monitoring stack
    ./deploy.py --server myserver.com --domain mydomain.com --docker --monitoring

Features:
- Uses AI Deployment Orchestrator as the backend
- Docker deployment with industry best practices
- Automatic SSL/HTTPS configuration  
- Security hardening and optimization
- DigitalOcean droplet optimization
- Comprehensive monitoring and health checks
"""

import sys
import os
import subprocess
import argparse

def main():
    """Main launcher that delegates to AI Deployment Orchestrator"""
    
    # Check if AI orchestrator exists
    orchestrator_path = os.path.join(os.path.dirname(__file__), 'ai_deployment_orchestrator.py')
    if not os.path.exists(orchestrator_path):
        print("❌ Error: ai_deployment_orchestrator.py not found")
        print("   Please ensure the AI deployment orchestrator is in the same directory")
        return 1
    
    parser = argparse.ArgumentParser(
        description="ProjectMeats Production Deployment Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --server myserver.com --domain mydomain.com --docker
  %(prog)s --interactive  
  %(prog)s --server myserver.com --domain mydomain.com --monitoring
        """
    )
    
    # Core deployment options
    parser.add_argument("--server", help="Server hostname or IP address")
    parser.add_argument("--domain", help="Domain name for the application") 
    parser.add_argument("--interactive", action="store_true", help="Interactive deployment setup")
    
    # Deployment modes
    parser.add_argument("--docker", action="store_true", 
                       help="Use Docker deployment (recommended for production)")
    parser.add_argument("--monitoring", action="store_true",
                       help="Include monitoring stack (Prometheus, Grafana)")
    
    # Authentication
    parser.add_argument("--username", default="root", help="SSH username")
    parser.add_argument("--key-file", help="SSH private key file path")
    parser.add_argument("--github-user", help="GitHub username for authentication")
    parser.add_argument("--github-token", help="GitHub Personal Access Token")
    
    # Advanced options
    parser.add_argument("--config", help="Custom configuration file path")
    parser.add_argument("--profile", help="Use predefined server profile")
    
    args = parser.parse_args()
    
    # Show banner
    print("""
🚀 ProjectMeats Production Deployment
=====================================
Using AI Deployment Orchestrator with industry best practices
""")
    
    # Validate arguments
    if not args.interactive and not args.server:
        print("❌ Error: Either --server or --interactive is required")
        print("   Use --help for more information")
        return 1
    
    # Build command for AI orchestrator
    cmd = ['python3', orchestrator_path]
    
    # Pass through all arguments
    if args.interactive:
        cmd.append('--interactive')
    if args.server:
        cmd.extend(['--server', args.server])
    if args.domain:
        cmd.extend(['--domain', args.domain])
    if args.username != 'root':
        cmd.extend(['--username', args.username])
    if args.key_file:
        cmd.extend(['--key-file', args.key_file])
    if args.github_user:
        cmd.extend(['--github-user', args.github_user])
    if args.github_token:
        cmd.extend(['--github-token', args.github_token])
    if args.config:
        cmd.extend(['--config', args.config])
    if args.profile:
        cmd.extend(['--profile', args.profile])
    
    # Add Docker deployment flags
    if args.docker:
        cmd.append('--docker')
        print("🐳 Docker deployment mode enabled")
        
    if args.monitoring:
        cmd.append('--docker-monitoring')  
        print("📊 Monitoring stack will be deployed")
        
    # Auto-approve for non-interactive deployments
    if not args.interactive:
        cmd.append('--auto-approve')
    
    print(f"Executing: {' '.join(cmd)}")
    print("=" * 50)
    
    # Execute AI deployment orchestrator
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Deployment cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error launching deployment: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())