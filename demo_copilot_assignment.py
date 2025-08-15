#!/usr/bin/env python3
"""
Demo script showing @copilot assignment for deployment failures

This demonstrates how the AI Deployment Orchestrator will automatically:
1. Create GitHub issues with @copilot assignment
2. Create PRs for critical failures
3. Use PAT credentials from the deployment parameters

Usage:
    # With environment variables (recommended)
    export GITHUB_TOKEN="ghp_your_token_here"
    python3 demo_copilot_assignment.py

    # With direct token (for demo purposes)
    python3 demo_copilot_assignment.py --github-token="ghp_your_token_here"
"""

import os
import sys
import argparse
sys.path.insert(0, '.')

from datetime import datetime, timezone
from scripts.deployment.github_integration import DeploymentLogManager

def demo_deployment_failure_with_copilot(github_token=None):
    """Demonstrate deployment failure handling with @copilot assignment"""
    
    print("🚀 ProjectMeats - @copilot Assignment Demo")
    print("=" * 50)
    
    if not github_token:
        github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_PAT')
    
    if not github_token:
        print("⚠️ No GitHub token provided")
        print("This would normally create issues with @copilot assignment")
        print("To test with real GitHub integration, provide a PAT token:")
        print("  export GITHUB_TOKEN='ghp_your_token_here'")
        print("  python3 demo_copilot_assignment.py")
        return
    
    # Mock the orchestrator's behavior during failure
    print("🔧 Simulating AI Deployment Orchestrator failure...")
    
    # Create deployment log manager (like the orchestrator does)
    deployment_id = f"demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Set the GitHub token in environment for DeploymentLogManager
    os.environ['GITHUB_TOKEN'] = github_token
    
    try:
        # This mimics what happens in the orchestrator
        log_manager = DeploymentLogManager(deployment_id)
        
        if log_manager.github:
            print(f"✅ GitHub integration initialized for deployment {deployment_id}")
            
            # Add some logs (like real deployment would)
            log_manager.add_log("INFO", "Starting deployment process", "initialization")
            log_manager.add_log("INFO", "Connecting to server...", "server_connection")
            log_manager.add_log("INFO", "Installing dependencies...", "install_dependencies")
            log_manager.add_log("ERROR", "Failed to configure backend - Django service configuration error", "configure_backend")
            log_manager.add_log("CRITICAL", "Deployment failed at configure_backend step", "configure_backend")
            
            # Simulate the orchestrator's failure handling
            error_details = {
                "failed_step": "configure_backend",  # This is a critical step
                "error_message": "Django service failed to start - configuration file missing or corrupt",
                "server_info": {
                    "hostname": "demo-server.projectmeats.com",
                    "domain": "demo.projectmeats.com"
                },
                "auto_recovery": True,
                "deployment_step": 3,
                "total_steps": 8
            }
            
            print("🚨 Creating GitHub issue with @copilot assignment...")
            issue_number = log_manager.create_failure_issue(error_details)
            
            if issue_number:
                print(f"✅ Created issue #{issue_number} with @copilot assignment!")
                print(f"📝 Issue URL: https://github.com/Vacilator/ProjectMeats/issues/{issue_number}")
                print()
                print("🔍 Issue includes:")
                print("  • @copilot assignment for automatic attention")
                print("  • 'copilot-fix-needed' label to trigger action")
                print("  • Detailed error information and logs")
                print("  • Step-by-step troubleshooting instructions")
                print("  • Server and deployment context")
                
                # Since configure_backend is a critical step, also create a PR
                print()
                print("🔧 Creating GitHub PR for critical failure...")
                pr_number = log_manager.create_failure_pr(error_details)
                
                if pr_number:
                    print(f"✅ Created PR #{pr_number} with @copilot assignment!")
                    print(f"📝 PR URL: https://github.com/Vacilator/ProjectMeats/pull/{pr_number}")
                    print()
                    print("🔍 PR includes:")
                    print("  • @copilot assignment for immediate action")
                    print("  • Dedicated branch for the fix")
                    print("  • Testing checklist for validation")
                    print("  • Deployment logs and context")
                else:
                    print("⚠️ PR creation failed (branch may exist or permissions issue)")
                
            else:
                print("❌ Issue creation failed")
            
            # Finalize logs
            log_manager.post_final_logs("failed")
            print("✅ Final deployment logs posted to GitHub")
            
        else:
            print("❌ GitHub integration not available")
            
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="Demo @copilot assignment for deployment failures")
    parser.add_argument("--github-token", help="GitHub Personal Access Token")
    
    args = parser.parse_args()
    
    demo_deployment_failure_with_copilot(args.github_token)

if __name__ == "__main__":
    main()