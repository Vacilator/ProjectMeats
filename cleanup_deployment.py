#!/usr/bin/env python3
"""
ProjectMeats Deployment Cleanup Script
====================================

This script consolidates and organizes deployment files, removing redundancy
and creating a clean, standardized deployment structure.

The AI Deployment Orchestrator is now the primary deployment tool.
"""

import os
import shutil
import json
from pathlib import Path

def main():
    """Clean up and consolidate deployment files"""
    
    print("🧹 ProjectMeats Deployment Cleanup")
    print("=" * 40)
    
    # Create organized structure
    create_organized_structure()
    
    # Move legacy files to archive
    archive_legacy_files()
    
    # Update documentation
    consolidate_documentation()
    
    # Create .gitignore entries for temporary files
    update_gitignore()
    
    print("\n✅ Deployment cleanup completed!")
    print("\n📋 New structure:")
    print("  • ai_deployment_orchestrator.py - Primary deployment tool")
    print("  • deploy.py - Simple launcher script") 
    print("  • docker-compose.prod.yml - Production Docker configuration")
    print("  • .env.prod.template - Environment template")
    print("  • deployment/ - Organized deployment utilities")
    print("  • legacy-deployment/ - Archived legacy scripts")

def create_organized_structure():
    """Create organized directory structure"""
    print("📁 Creating organized directory structure...")
    
    # Create directories
    dirs = [
        'deployment/configs',
        'deployment/scripts', 
        'deployment/templates',
        'deployment/monitoring',
        'legacy-deployment'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  ✓ Created {dir_path}/")

def archive_legacy_files():
    """Move legacy deployment files to archive"""
    print("\n📦 Archiving legacy deployment files...")
    
    # Files to archive (keeping them but moving to legacy directory)
    legacy_files = [
        'master_deploy.py',
        'deploy_production.py', 
        'production_deploy.sh',
        'ai_deploy.sh',
        'setup_ai_deployment.py',
        'setup_ssl.sh'
    ]
    
    for file_name in legacy_files:
        if os.path.exists(file_name):
            shutil.move(file_name, f'legacy-deployment/{file_name}')
            print(f"  ✓ Archived {file_name}")
    
    # Archive redundant Docker files
    docker_files = [
        'docker-compose.yml',  # Keep dev version 
        'docker-compose.dev.yml'  # Archive dev version if prod exists
    ]
    
    for file_name in docker_files:
        if os.path.exists(file_name) and file_name != 'docker-compose.yml':
            shutil.move(file_name, f'legacy-deployment/{file_name}')
            print(f"  ✓ Archived {file_name}")

def consolidate_documentation():
    """Consolidate deployment documentation"""
    print("\n📚 Consolidating documentation...")
    
    # Create comprehensive deployment README
    readme_content = """# ProjectMeats Production Deployment

## Quick Start

### Docker Deployment (Recommended)
```bash
# Interactive setup
./deploy.py --interactive

# Direct deployment  
./deploy.py --server myserver.com --domain mydomain.com --docker

# With monitoring
./deploy.py --server myserver.com --domain mydomain.com --docker --monitoring
```

### Using AI Orchestrator Directly
```bash  
# Full automated deployment
python3 ai_deployment_orchestrator.py --server myserver.com --domain mydomain.com --docker --auto

# Interactive setup
python3 ai_deployment_orchestrator.py --interactive
```

## Features

✅ **Docker Deployment**: Industry-standard containerization with security hardening
✅ **Auto SSL/HTTPS**: Automatic SSL certificate generation and renewal
✅ **Security Hardening**: Non-root containers, security headers, rate limiting
✅ **DigitalOcean Optimized**: Optimized for DigitalOcean droplet performance
✅ **Monitoring**: Optional Prometheus/Grafana monitoring stack  
✅ **Health Checks**: Comprehensive health monitoring and alerting
✅ **Backup Strategy**: Automated database backups and retention
✅ **Zero Downtime**: Rolling updates and graceful shutdowns

## Architecture  

- **Frontend**: React TypeScript app served via nginx
- **Backend**: Django REST API with gunicorn
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis for sessions and caching
- **Reverse Proxy**: nginx with SSL termination
- **Background Tasks**: Celery worker processes
- **Monitoring**: Prometheus + Grafana (optional)

## File Structure

```
├── ai_deployment_orchestrator.py  # Primary deployment tool
├── deploy.py                      # Simple launcher
├── docker-compose.prod.yml        # Production Docker config
├── .env.prod.template             # Environment template
├── nginx/                         # nginx configurations
├── monitoring/                    # Prometheus/Grafana configs
└── legacy-deployment/             # Archived legacy scripts
```

## Support

For issues or questions, see the troubleshooting guides in `/docs/` or create an issue.
"""
    
    with open('deployment/README.md', 'w') as f:
        f.write(readme_content)
    print("  ✓ Created deployment/README.md")

def update_gitignore():
    """Update .gitignore for temporary deployment files"""
    print("\n🚫 Updating .gitignore...")
    
    gitignore_entries = [
        "",
        "# Deployment temporary files",
        ".env.prod",
        "deployment_state.json", 
        "deployment_log.json",
        "cookies.txt",
        "logs/",
        "backups/",
        "ssl/private/",
        "monitoring/data/",
    ]
    
    # Read existing gitignore
    gitignore_path = '.gitignore'
    existing_content = ""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            existing_content = f.read()
    
    # Add new entries if they don't exist
    new_entries = []
    for entry in gitignore_entries:
        if entry and entry not in existing_content:
            new_entries.append(entry)
    
    if new_entries:
        with open(gitignore_path, 'a') as f:
            f.write('\n'.join(new_entries) + '\n')
        print(f"  ✓ Added {len(new_entries)} entries to .gitignore")
    else:
        print("  ✓ .gitignore already up to date")

if __name__ == "__main__":
    main()