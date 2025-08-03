#!/usr/bin/env python3
"""
AI Deployment Orchestrator Usage Examples
==========================================

This script demonstrates how to use the AI deployment system for various scenarios.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def example_interactive_deployment():
    """Example: Interactive deployment setup"""
    print("🤖 Example: Interactive Deployment")
    print("=" * 40)
    
    print("To run an interactive deployment:")
    print("1. python setup_ai_deployment.py")
    print("2. ./ai_deploy.sh --interactive")
    print()
    
    print("The system will:")
    print("- Guide you through server configuration")
    print("- Test SSH connectivity")
    print("- Execute deployment steps with real-time monitoring")
    print("- Automatically recover from errors")
    print("- Provide a comprehensive deployment report")
    print()

def example_automated_deployment():
    """Example: Automated deployment"""
    print("🚀 Example: Automated Deployment")
    print("=" * 40)
    
    print("For automated deployments:")
    print("./ai_deploy.sh --server myserver.com --domain mydomain.com --auto")
    print()
    
    print("Or using Python directly:")
    print("python ai_deployment_orchestrator.py \\")
    print("  --server myserver.com \\")
    print("  --domain mydomain.com \\")
    print("  --username root \\")
    print("  --key-file ~/.ssh/id_ed25519")
    print()

def example_configuration():
    """Example: Configuration setup"""
    print("⚙️ Example: Configuration")
    print("=" * 40)
    
    config_example = {
        "server_profiles": {
            "production": {
                "hostname": "prod.example.com",
                "username": "root",
                "domain": "myapp.com",
                "key_file": "~/.ssh/id_ed25519"
            }
        },
        "ai_features": {
            "intelligent_error_detection": True,
            "auto_fix_common_issues": True,
            "learn_from_failures": True
        }
    }
    
    print("Example configuration in ai_deployment_config.json:")
    import json
    print(json.dumps(config_example, indent=2))
    print()

def example_error_recovery():
    """Example: Error recovery scenarios"""
    print("🛠️ Example: Error Recovery")
    print("=" * 40)
    
    print("The system automatically handles:")
    print("1. Node.js conflicts → Complete cleanup and reinstallation")
    print("2. Permission errors → Automatic permission fixes")
    print("3. Service failures → Service restart and repair")
    print("4. Port conflicts → Kill conflicting processes")
    print("5. SSL issues → Retry with fallback strategies")
    print()
    
    print("Example error detection in action:")
    try:
        from ai_deployment_orchestrator import AIDeploymentOrchestrator
        
        orchestrator = AIDeploymentOrchestrator()
        
        # Test error detection
        test_outputs = [
            "nodejs : Conflicts: npm",
            "E: Unable to locate package nginx", 
            "Permission denied: /opt/projectmeats",
            "Port 80 already in use"
        ]
        
        for output in test_outputs:
            errors = orchestrator.detect_errors(output)
            if errors:
                print(f"✓ Detected: {errors[0].description}")
    except ImportError:
        print("(Install dependencies to see live error detection)")
    print()

def example_monitoring():
    """Example: Monitoring and logging"""
    print("📊 Example: Monitoring")
    print("=" * 40)
    
    print("Real-time monitoring features:")
    print("1. Live command output streaming")
    print("2. Progress tracking with visual indicators")
    print("3. Structured JSON logging")
    print("4. Performance metrics collection")
    print()
    
    print("View logs:")
    print("tail -f logs/deployment_*.log")
    print("tail -f deployment_log.json | jq '.'")
    print()

def example_resumable_deployment():
    """Example: Resumable deployments"""
    print("🔄 Example: Resumable Deployments")
    print("=" * 40)
    
    print("If a deployment fails, you can resume it:")
    print("python ai_deployment_orchestrator.py --resume --deployment-id abc123")
    print()
    
    print("The system will:")
    print("- Load the previous deployment state")
    print("- Reconnect to the server")
    print("- Continue from the last successful step")
    print("- Apply learned recovery strategies")
    print()

def example_testing():
    """Example: Testing and validation"""
    print("🧪 Example: Testing")
    print("=" * 40)
    
    print("Test server connectivity:")
    print("python ai_deployment_orchestrator.py --test-connection --server myserver.com")
    print()
    
    print("Run the test suite:")
    print("python test_ai_deployment.py")
    print()
    
    print("Validate configuration:")
    print("python -c \"import json; print('Config valid:', bool(json.load(open('ai_deployment_config.json'))))\"")
    print()

def main():
    """Run all examples"""
    print("🤖 AI Deployment Orchestrator - Usage Examples")
    print("=" * 60)
    print()
    
    examples = [
        example_interactive_deployment,
        example_automated_deployment,
        example_configuration,
        example_error_recovery,
        example_monitoring,
        example_resumable_deployment,
        example_testing
    ]
    
    for example in examples:
        example()
        print()
    
    print("📋 Quick Start Commands:")
    print("1. python setup_ai_deployment.py")
    print("2. ./ai_deploy.sh --interactive")
    print("3. Monitor: tail -f logs/deployment_*.log")
    print()
    
    print("📚 For more information:")
    print("- Read: docs/ai_deployment_guide.md")
    print("- Config: ai_deployment_config.example.json")
    print("- Test: python test_ai_deployment.py")

if __name__ == "__main__":
    main()