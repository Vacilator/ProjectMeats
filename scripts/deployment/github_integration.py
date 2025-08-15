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
        self.authenticated = False
        self.auth_error = None
        
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
        
        # Test authentication on initialization and store result
        self.authenticated = self._test_authentication()
    
    def _test_authentication(self) -> bool:
        """Test GitHub API authentication"""
        try:
            response = self.session.get(f"{self.base_url}/user")
            if response.status_code == 200:
                user_data = response.json()
                self.logger.info(f"GitHub authentication successful for user: {user_data.get('login')}")
                return True
            else:
                self.auth_error = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"GitHub authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.auth_error = str(e)
            self.logger.error(f"GitHub authentication error: {e}")
            return False
    
    def create_deployment_issue(self, deployment_id: str, error_details: Dict[str, Any], 
                              logs: List[DeploymentLogEntry] = None) -> Optional[int]:
        """
        Create a GitHub issue for deployment failure with @copilot assignment
        
        Args:
            deployment_id: Unique deployment identifier
            error_details: Dictionary containing error information
            logs: Optional deployment logs to include
            
        Returns:
            Issue number if successful, None if failed
        """
        # Check authentication before attempting API call
        if not self.authenticated:
            self.logger.error(f"Cannot create GitHub issue - authentication failed: {self.auth_error}")
            return None
            
        try:
            # Format error details
            server_info = error_details.get('server_info', {})
            failed_step = error_details.get('failed_step', 'Unknown')
            error_message = error_details.get('error_message', 'No error message provided')
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Create issue title with enhanced copilot trigger
            title = f"🚨 Deployment Failed: {deployment_id} - {failed_step} - @copilot please fix"
            
            # Create detailed issue body with copilot instructions
            body = f"""# 🚨 Deployment Failure Report - @copilot Please Fix

@copilot This deployment has failed and needs your attention to create a fix. Please analyze the error details below and create a solution.

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
            
            # Add troubleshooting steps and copilot instructions
            body += f"""

## @copilot Action Required

Please analyze the deployment failure above and:
1. **Identify the root cause** of the error in step `{failed_step}`
2. **Create a pull request** with fixes for the identified issues
3. **Test the fixes** to ensure they resolve the deployment failure
4. **Document any changes** made to prevent future occurrences

## Suggested Troubleshooting Steps

1. **Check Server Connectivity**:
   ```bash
   ssh root@{server_info.get('hostname', 'unknown')}
   systemctl status nginx postgresql
   ```

2. **Verify Domain Configuration**:
   ```bash
   nslookup {server_info.get('domain', 'unknown')}
   curl -I http://{server_info.get('domain', 'unknown')}/health
   ```

3. **Check Application Logs**:
   ```bash
   journalctl -u projectmeats -f
   tail -f /opt/projectmeats/backend/logs/*.log
   ```

4. **Re-run Deployment**:
   ```bash
   python ai_deployment_orchestrator.py --server {server_info.get('hostname', 'unknown')} --domain {server_info.get('domain', 'unknown')}
   ```

## Auto-Generated Tags for @copilot
- deployment-failure: Indicates this is a deployment issue
- copilot-fix-needed: Requests @copilot to create a fix
- needs-investigation: Requires deep analysis
- server-{server_info.get('hostname', 'unknown').replace('.', '-')}: Server-specific issue
- step-{failed_step.replace('_', '-')}: Failed at specific deployment step

---
*This issue was automatically created by the AI Deployment Orchestrator and assigned to @copilot for automatic resolution.*
"""
            
            # Create GitHub issue with @copilot assignment
            issue_data = {
                "title": title,
                "body": body,
                "labels": [
                    "deployment-failure",
                    "copilot-fix-needed",  # Special label to trigger @copilot attention
                    "auto-generated",
                    "needs-investigation",
                    "priority-high",  # High priority for deployment failures
                    f"server-{server_info.get('hostname', 'unknown').replace('.', '-')}",
                    f"step-{failed_step.replace('_', '-')}"  # Step-specific label
                ],
                "assignees": ["copilot"]  # Automatically assign to @copilot
            }
            
            response = self.session.post(
                f"{self.base_url}/repos/{self.owner}/{self.repo}/issues",
                json=issue_data
            )
            
            if response.status_code == 201:
                issue = response.json()
                issue_number = issue['number']
                self.logger.info(f"Created GitHub issue #{issue_number} for deployment failure with @copilot assignment")
                return issue_number
            else:
                self.logger.error(f"Failed to create GitHub issue: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating GitHub issue: {e}")
            return None
                
    def create_deployment_fix_pr(self, deployment_id: str, error_details: Dict[str, Any], 
                              logs: List[DeploymentLogEntry] = None) -> Optional[int]:
        """
        Create a GitHub PR for deployment failure fixes (for critical failures)
        
        Args:
            deployment_id: Unique deployment identifier
            error_details: Dictionary containing error information
            logs: Optional deployment logs to include
            
        Returns:
            PR number if successful, None if failed
        """
        # Check authentication before attempting API call
        if not self.authenticated:
            self.logger.error(f"Cannot create GitHub PR - authentication failed: {self.auth_error}")
            return None
            
        try:
            # Format error details
            server_info = error_details.get('server_info', {})
            failed_step = error_details.get('failed_step', 'Unknown')
            error_message = error_details.get('error_message', 'No error message provided')
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Create branch name for the fix
            branch_name = f"fix/deployment-{deployment_id}-{failed_step}".replace('_', '-').replace(' ', '-').lower()[:50]
            
            # Create PR title
            title = f"🔧 Fix deployment failure: {failed_step} ({deployment_id})"
            
            # Create detailed PR body
            body = f"""# 🔧 Deployment Failure Fix for {deployment_id}

## Problem
Deployment failed at step `{failed_step}` with the following error:

```
{error_message}
```

## Server Information
- **Server**: {server_info.get('hostname', 'Unknown')}
- **Domain**: {server_info.get('domain', 'Unknown')} 
- **Timestamp**: {timestamp}

## Proposed Solution
@copilot Please implement fixes for the deployment failure identified above.

## Testing Checklist
- [ ] Verify fix addresses the root cause in `{failed_step}` step
- [ ] Test deployment script with fix applied
- [ ] Ensure no regression in other deployment steps
- [ ] Validate on target server: {server_info.get('hostname', 'Unknown')}

## Deployment Logs
"""
            
            # Add recent logs if provided
            if logs:
                body += "\n```\n"
                for log_entry in logs[-10:]:  # Last 10 log entries
                    body += f"[{log_entry.timestamp}] [{log_entry.level}] {log_entry.message}\n"
                body += "```\n"
                
            body += f"""
---
*This PR was automatically created for deployment failure {deployment_id} and assigned to @copilot for resolution.*
"""

            # First, try to create the branch (this may fail if branch exists, that's ok)
            try:
                # Get the latest main branch SHA
                main_ref_response = self.session.get(f"{self.base_url}/git/refs/heads/main")
                if main_ref_response.status_code == 200:
                    main_sha = main_ref_response.json()['object']['sha']
                    
                    # Create new branch
                    branch_data = {
                        "ref": f"refs/heads/{branch_name}",
                        "sha": main_sha
                    }
                    
                    branch_response = self.session.post(
                        f"{self.base_url}/git/refs",
                        json=branch_data
                    )
                    # Branch creation may fail if exists, continue anyway
            except Exception:
                pass  # Continue even if branch creation fails
            
            # Create GitHub PR
            pr_data = {
                "title": title,
                "head": branch_name,
                "base": "main", 
                "body": body,
                "draft": False,
                "maintainer_can_modify": True
            }
            
            response = self.session.post(
                f"{self.base_url}/pulls",
                json=pr_data
            )
            
            if response.status_code == 201:
                pr = response.json()
                pr_number = pr['number']
                self.logger.info(f"Created GitHub PR #{pr_number} for deployment failure with @copilot assignment")
                
                # Add @copilot as assignee to the PR
                try:
                    assign_data = {"assignees": ["copilot"]}
                    assign_response = self.session.post(
                        f"{self.base_url}/issues/{pr_number}/assignees",
                        json=assign_data
                    )
                    if assign_response.status_code == 201:
                        self.logger.info(f"Assigned @copilot to PR #{pr_number}")
                except Exception as e:
                    self.logger.warning(f"Could not assign @copilot to PR: {e}")
                
                return pr_number
            else:
                self.logger.error(f"Failed to create GitHub PR: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating GitHub PR: {e}")
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
        # Check authentication before attempting API call
        if not self.authenticated:
            self.logger.error(f"Cannot post deployment log - authentication failed: {self.auth_error}")
            return False
            
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
        # Check authentication before attempting API call
        if not self.authenticated:
            self.logger.error(f"Cannot update deployment status - authentication failed: {self.auth_error}")
            return False
            
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
        self.github_available = False
        
        # Initialize GitHub integration if token is available
        github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_PAT')
        if github_token:
            try:
                self.github = GitHubIntegration(token=github_token, repo="Vacilator/ProjectMeats")
                # Only mark as available if authentication succeeded
                self.github_available = self.github.authenticated if self.github else False
                if not self.github_available:
                    logging.getLogger(__name__).warning(f"GitHub integration failed authentication - features disabled")
            except Exception as e:
                logging.getLogger(__name__).warning(f"GitHub integration not available: {e}")
                self.github_available = False
    
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
        if level in ["ERROR", "CRITICAL"] and self.github_available and self.github:
            try:
                self.github.post_deployment_log(self.deployment_id, self.logs[-10:], "running")
            except Exception:
                pass  # Don't fail deployment for logging issues
    
    def post_final_logs(self, status: str) -> bool:
        """Post final deployment logs to GitHub"""
        if not self.github_available or not self.github:
            return False
            
        return self.github.post_deployment_log(self.deployment_id, self.logs, status)
    
    def create_failure_issue(self, error_details: Dict[str, Any]) -> Optional[int]:
        """Create a GitHub issue for deployment failure"""
        if not self.github_available or not self.github:
            return None
            
        return self.github.create_deployment_issue(self.deployment_id, error_details, self.logs)
    
    def create_failure_pr(self, error_details: Dict[str, Any]) -> Optional[int]:
        """Create a GitHub PR for critical deployment failure fixes"""
        if not self.github_available or not self.github:
            return None
            
        return self.github.create_deployment_fix_pr(self.deployment_id, error_details, self.logs)
    
    def update_status(self, status: str, target_url: Optional[str] = None) -> bool:
        """Update deployment status on GitHub"""
        if not self.github_available or not self.github:
            return False
            
        return self.github.update_deployment_status(self.deployment_id, status, target_url)