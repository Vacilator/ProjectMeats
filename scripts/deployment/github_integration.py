#!/usr/bin/env python3
"""
GitHub Integration Module for AI Deployment Orchestrator
========================================================

This module provides GitHub API integration for:
- Posting deployment logs to GitHub
- Creating issues on deployment errors
- Tracking deployment status in GitHub

Usage:
    from github_integration import GitHubIntegration
    
    github = GitHubIntegration(token="ghp_...", repo="Vacilator/ProjectMeats")
    github.post_deployment_log(deployment_id, logs)
    github.create_deployment_issue(error_details)
"""

import os
import json
import requests
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging


@dataclass
class DeploymentLogEntry:
    """Single deployment log entry"""
    timestamp: str
    level: str
    message: str
    step: Optional[str] = None
    deployment_id: Optional[str] = None


@dataclass
class GitHubIssue:
    """GitHub issue data structure"""
    title: str
    body: str
    labels: List[str]
    assignees: List[str] = None
    milestone: Optional[int] = None


class GitHubIntegration:
    """GitHub API integration for deployment orchestrator"""
    
    def __init__(self, token: str, repo: str, owner: Optional[str] = None):
        """
        Initialize GitHub integration
        
        Args:
            token: GitHub Personal Access Token
            repo: Repository name (e.g., "ProjectMeats" or "Vacilator/ProjectMeats")
            owner: Repository owner (auto-detected if repo includes owner)
        """
        self.token = token
        
        if "/" in repo:
            self.owner, self.repo = repo.split("/", 1)
        else:
            self.owner = owner or "Vacilator"
            self.repo = repo
            
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ProjectMeats-AI-Deployment-Orchestrator"
        })
        
        self.logger = logging.getLogger(__name__)
        
        # Test authentication on initialization
        self._test_authentication()
    
    def _test_authentication(self) -> bool:
        """Test GitHub API authentication"""
        try:
            response = self.session.get(f"{self.base_url}/user")
            if response.status_code == 200:
                user_data = response.json()
                self.logger.info(f"GitHub authentication successful for user: {user_data.get('login')}")
                return True
            else:
                self.logger.error(f"GitHub authentication failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"GitHub authentication error: {e}")
            return False
    
    def create_deployment_issue(self, deployment_id: str, error_details: Dict[str, Any], 
                              logs: List[DeploymentLogEntry] = None) -> Optional[int]:
        """
        Create a GitHub issue for deployment failure
        
        Args:
            deployment_id: Unique deployment identifier
            error_details: Dictionary containing error information
            logs: Optional deployment logs to include
            
        Returns:
            Issue number if successful, None if failed
        """
        try:
            # Format error details
            server_info = error_details.get('server_info', {})
            failed_step = error_details.get('failed_step', 'Unknown')
            error_message = error_details.get('error_message', 'No error message provided')
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Create issue title
            title = f"🚨 Deployment Failed: {deployment_id} - {failed_step}"
            
            # Create detailed issue body
            body = f"""# Deployment Failure Report
            
## Deployment Information
- **Deployment ID**: `{deployment_id}`
- **Timestamp**: {timestamp}
- **Failed Step**: {failed_step}
- **Server**: {server_info.get('hostname', 'Unknown')}
- **Domain**: {server_info.get('domain', 'Unknown')}

## Error Details
```
{error_message}
```

## Server Configuration
```json
{json.dumps(server_info, indent=2)}
```

## Environment Information
- **OS**: Ubuntu (assumed)
- **Deployment Method**: AI Deployment Orchestrator
- **Auto-Recovery**: {'Enabled' if error_details.get('auto_recovery', False) else 'Disabled'}

## Recent Deployment Logs
"""
            
            # Add recent logs if provided
            if logs:
                body += "\n```\n"
                for log_entry in logs[-20:]:  # Last 20 log entries
                    body += f"[{log_entry.timestamp}] [{log_entry.level}] {log_entry.message}\n"
                body += "```\n"
            
            # Add troubleshooting steps
            body += """
## Suggested Troubleshooting Steps

1. **Check Server Connectivity**:
   ```bash
   ssh root@{server}
   systemctl status nginx postgresql
   ```

2. **Verify Domain Configuration**:
   ```bash
   nslookup {domain}
   curl -I http://{domain}/health
   ```

3. **Check Application Logs**:
   ```bash
   journalctl -u projectmeats -f
   tail -f /opt/projectmeats/backend/logs/*.log
   ```

4. **Re-run Deployment**:
   ```bash
   python ai_deployment_orchestrator.py --server {server} --domain {domain}
   ```

## Auto-Generated Tags
- deployment-failure
- needs-investigation
- server-{server_tag}

---
*This issue was automatically created by the AI Deployment Orchestrator*
""".format(
                server=server_info.get('hostname', 'unknown'),
                domain=server_info.get('domain', 'unknown'),
                server_tag=server_info.get('hostname', 'unknown').replace('.', '-')
            )
            
            # Create GitHub issue
            issue_data = {
                "title": title,
                "body": body,
                "labels": [
                    "deployment-failure",
                    "auto-generated",
                    "needs-investigation",
                    f"server-{server_info.get('hostname', 'unknown').replace('.', '-')}"
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/repos/{self.owner}/{self.repo}/issues",
                json=issue_data
            )
            
            if response.status_code == 201:
                issue = response.json()
                issue_number = issue['number']
                self.logger.info(f"Created GitHub issue #{issue_number} for deployment failure")
                return issue_number
            else:
                self.logger.error(f"Failed to create GitHub issue: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating GitHub issue: {e}")
            return None
    
    def post_deployment_log(self, deployment_id: str, logs: List[DeploymentLogEntry], 
                           status: str = "running") -> bool:
        """
        Post deployment logs as a GitHub issue comment or gist
        
        Args:
            deployment_id: Unique deployment identifier
            logs: List of deployment log entries
            status: Deployment status (running, success, failed)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a gist with deployment logs
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Format logs for gist
            log_content = f"# ProjectMeats Deployment Log\n"
            log_content += f"**Deployment ID**: {deployment_id}\n"
            log_content += f"**Status**: {status.upper()}\n"
            log_content += f"**Timestamp**: {timestamp}\n\n"
            log_content += "## Deployment Logs\n\n"
            
            for log_entry in logs:
                log_content += f"[{log_entry.timestamp}] [{log_entry.level}] {log_entry.message}\n"
            
            gist_data = {
                "description": f"ProjectMeats Deployment Log - {deployment_id} ({status})",
                "public": False,  # Private gist
                "files": {
                    f"deployment-{deployment_id}.md": {
                        "content": log_content
                    }
                }
            }
            
            response = self.session.post(f"{self.base_url}/gists", json=gist_data)
            
            if response.status_code == 201:
                gist = response.json()
                gist_url = gist['html_url']
                self.logger.info(f"Posted deployment logs to GitHub gist: {gist_url}")
                return True
            else:
                self.logger.error(f"Failed to create GitHub gist: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error posting deployment log: {e}")
            return False
    
    def update_deployment_status(self, deployment_id: str, status: str, 
                               target_url: Optional[str] = None) -> bool:
        """
        Update deployment status using GitHub Deployments API
        
        Args:
            deployment_id: Unique deployment identifier
            status: Deployment status (pending, in_progress, success, failure)
            target_url: URL to access the deployed application
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, create a deployment if it doesn't exist
            deployment_data = {
                "ref": "main",  # or current branch
                "environment": "production",
                "description": f"AI Deployment Orchestrator - {deployment_id}",
                "auto_merge": False,
                "required_contexts": []
            }
            
            # Create deployment
            response = self.session.post(
                f"{self.base_url}/repos/{self.owner}/{self.repo}/deployments",
                json=deployment_data
            )
            
            if response.status_code == 201:
                deployment = response.json()
                deployment_github_id = deployment['id']
                
                # Create deployment status
                status_data = {
                    "state": status,
                    "description": f"Deployment {deployment_id} - {status}",
                    "environment": "production"
                }
                
                if target_url:
                    status_data["target_url"] = target_url
                
                status_response = self.session.post(
                    f"{self.base_url}/repos/{self.owner}/{self.repo}/deployments/{deployment_github_id}/statuses",
                    json=status_data
                )
                
                if status_response.status_code == 201:
                    self.logger.info(f"Updated deployment status to {status}")
                    return True
                else:
                    self.logger.error(f"Failed to update deployment status: {status_response.status_code}")
                    return False
            else:
                self.logger.error(f"Failed to create deployment: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating deployment status: {e}")
            return False
    
    def search_existing_deployment_issues(self, server_hostname: str) -> List[Dict[str, Any]]:
        """
        Search for existing deployment issues for a specific server
        
        Args:
            server_hostname: Server hostname to search for
            
        Returns:
            List of existing issues
        """
        try:
            # Search for open deployment issues for this server
            query = f"repo:{self.owner}/{self.repo} is:issue is:open label:deployment-failure server-{server_hostname.replace('.', '-')}"
            
            response = self.session.get(
                f"{self.base_url}/search/issues",
                params={"q": query}
            )
            
            if response.status_code == 200:
                search_results = response.json()
                return search_results.get('items', [])
            else:
                self.logger.error(f"Failed to search issues: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching deployment issues: {e}")
            return []
    
    def add_comment_to_issue(self, issue_number: int, comment: str) -> bool:
        """
        Add a comment to an existing GitHub issue
        
        Args:
            issue_number: GitHub issue number
            comment: Comment text to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            comment_data = {"body": comment}
            
            response = self.session.post(
                f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments",
                json=comment_data
            )
            
            if response.status_code == 201:
                self.logger.info(f"Added comment to issue #{issue_number}")
                return True
            else:
                self.logger.error(f"Failed to add comment: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding comment to issue: {e}")
            return False


class DeploymentLogManager:
    """Manages deployment logs for GitHub integration"""
    
    def __init__(self, deployment_id: str):
        self.deployment_id = deployment_id
        self.logs: List[DeploymentLogEntry] = []
        self.github: Optional[GitHubIntegration] = None
        
        # Initialize GitHub integration if token is available
        github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_PAT')
        if github_token:
            try:
                self.github = GitHubIntegration(token=github_token, repo="Vacilator/ProjectMeats")
            except Exception as e:
                logging.getLogger(__name__).warning(f"GitHub integration not available: {e}")
    
    def add_log(self, level: str, message: str, step: Optional[str] = None):
        """Add a log entry"""
        entry = DeploymentLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level,
            message=message,
            step=step,
            deployment_id=self.deployment_id
        )
        self.logs.append(entry)
        
        # Optionally post to GitHub in real-time for critical errors
        if level in ["ERROR", "CRITICAL"] and self.github:
            try:
                self.github.post_deployment_log(self.deployment_id, self.logs[-10:], "running")
            except Exception:
                pass  # Don't fail deployment for logging issues
    
    def post_final_logs(self, status: str) -> bool:
        """Post final deployment logs to GitHub"""
        if not self.github:
            return False
            
        return self.github.post_deployment_log(self.deployment_id, self.logs, status)
    
    def create_failure_issue(self, error_details: Dict[str, Any]) -> Optional[int]:
        """Create a GitHub issue for deployment failure"""
        if not self.github:
            return None
            
        return self.github.create_deployment_issue(self.deployment_id, error_details, self.logs)
    
    def update_status(self, status: str, target_url: Optional[str] = None) -> bool:
        """Update deployment status on GitHub"""
        if not self.github:
            return False
            
        return self.github.update_deployment_status(self.deployment_id, status, target_url)