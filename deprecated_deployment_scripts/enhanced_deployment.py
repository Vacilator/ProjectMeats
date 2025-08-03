#!/usr/bin/env python3
"""
Enhanced deployment script with fixes for the meatscentral.com connection issue

This script addresses the ERR_CONNECTION_REFUSED issue by ensuring:
1. Proper nginx configuration is created with ProjectMeats-specific settings
2. Backend Django service is properly configured and started
3. Database setup includes proper user and permissions
4. All services are verified to be running

Usage:
    python enhanced_deployment.py --server 167.99.155.140 --domain meatscentral.com
"""

import argparse
import sys
import os
from ai_deployment_orchestrator import AIDeploymentOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Enhanced ProjectMeats deployment with connection fixes")
    parser.add_argument("--server", required=True, help="Server IP address (e.g., 167.99.155.140)")
    parser.add_argument("--domain", required=True, help="Domain name (e.g., meatscentral.com)")
    parser.add_argument("--username", default="root", help="SSH username")
    parser.add_argument("--key-file", help="SSH private key file path")
    parser.add_argument("--github-user", help="GitHub username for repository access")
    parser.add_argument("--github-token", help="GitHub Personal Access Token")
    
    args = parser.parse_args()
    
    print("🚀 ProjectMeats Enhanced Deployment")
    print("=" * 50)
    print(f"Target Server: {args.server}")
    print(f"Domain: {args.domain}")
    print()
    
    print("📋 Fixes included in this deployment:")
    print("✅ Proper nginx configuration with API proxy and frontend serving")
    print("✅ Django backend service configuration and startup")
    print("✅ PostgreSQL database with proper user and permissions")
    print("✅ Service verification and health checks")
    print("✅ Complete deployment pipeline execution")
    print()
    
    # Initialize orchestrator
    orchestrator = AIDeploymentOrchestrator()
    
    # Set configuration
    orchestrator.config['domain'] = args.domain
    
    # Set GitHub authentication if provided
    if args.github_user and args.github_token:
        orchestrator.config['github']['user'] = args.github_user
        orchestrator.config['github']['token'] = args.github_token
        print(f"🔑 GitHub authentication configured for {args.github_user}")
    
    # Prepare server configuration
    server_config = {
        'hostname': args.server,
        'username': args.username,
        'key_file': args.key_file,
        'domain': args.domain
    }
    
    print(f"🔗 Starting deployment to {args.server}...")
    print()
    
    try:
        # Run the enhanced deployment
        success = orchestrator.run_deployment(server_config)
        
        if success:
            print()
            print("🎉 DEPLOYMENT SUCCESSFUL!")
            print("=" * 50)
            print(f"✅ Website should now be accessible at: http://{args.domain}")
            print(f"✅ API endpoint: http://{args.domain}/api/")
            print(f"✅ Admin interface: http://{args.domain}/admin/")
            print()
            print("🔍 To verify the deployment:")
            print(f"   curl -I http://{args.domain}")
            print(f"   curl http://{args.domain}/health")
            print()
            print("📝 Services that should be running:")
            print("   - nginx (web server)")
            print("   - postgresql (database)")
            print("   - projectmeats (Django backend)")
            print()
            print("🛠️ If issues persist, check:")
            print(f"   ssh {args.username}@{args.server}")
            print("   systemctl status nginx")
            print("   systemctl status projectmeats")
            print("   systemctl status postgresql")
            print("   nginx -t")
            print("   curl localhost:8000/admin/")
            
        else:
            print()
            print("❌ DEPLOYMENT FAILED!")
            print("=" * 50)
            print("Please check the deployment logs for details.")
            print("Common issues and solutions:")
            print()
            print("1. Connection refused errors:")
            print("   - Check firewall settings (ufw status)")
            print("   - Verify nginx is running (systemctl status nginx)")
            print("   - Check nginx configuration (nginx -t)")
            print()
            print("2. Backend not responding:")
            print("   - Check Django service (systemctl status projectmeats)")
            print("   - Verify database connection")
            print("   - Check Python dependencies")
            print()
            print("3. Frontend not loading:")
            print("   - Verify build files exist (/opt/projectmeats/frontend/build/)")
            print("   - Check nginx frontend configuration")
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print()
        print("🛑 Deployment cancelled by user")
        return 1
    except Exception as e:
        print()
        print(f"💥 Deployment failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())