"""
GitHub integration service for creating bug report issues.

Handles creation of GitHub issues with auto-assignment to copilot
and proper formatting for bug report data.
"""
import json
import os
from typing import Dict, List

import requests


class GitHubIssueService:
    """
    Service for creating and managing GitHub issues from bug reports.
    """

    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.github_repo = os.environ.get("GITHUB_REPO", "Vacilator/ProjectMeats")
        self.copilot_username = os.environ.get("GITHUB_COPILOT_USERNAME", "copilot")
        self.base_url = f"https://api.github.com/repos/{self.github_repo}"

        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        return {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

    def create_bug_issue(self, bug_report) -> Dict[str, any]:
        """
        Create a GitHub issue from a bug report.

        Args:
            bug_report: BugReport model instance

        Returns:
            Dict with issue data or error information
        """
        try:
            # Format issue title
            title = f"🐛 Bug Report: {bug_report.title}"

            # Create detailed issue body
            body = self._format_issue_body(bug_report)

            # Prepare labels
            labels = self._get_issue_labels(bug_report)

            # Create issue payload
            issue_data = {
                "title": title,
                "body": body,
                "labels": labels,
                "assignees": [self.copilot_username],
            }

            # Create the issue
            response = requests.post(
                f"{self.base_url}/issues",
                headers=self._get_headers(),
                data=json.dumps(issue_data),
                timeout=30,
            )

            if response.status_code == 201:
                issue_data = response.json()
                return {
                    "success": True,
                    "issue_number": issue_data["number"],
                    "issue_url": issue_data["html_url"],
                    "assigned_to_copilot": self.copilot_username
                    in [a["login"] for a in issue_data.get("assignees", [])],
                    "labels": [label["name"] for label in issue_data.get("labels", [])],
                }
            else:
                error_detail = (
                    response.json()
                    if response.content
                    else {"message": "Unknown error"}
                )
                return {
                    "success": False,
                    "error": f"GitHub API error {response.status_code}: {error_detail.get('message', 'Unknown error')}",
                    "status_code": response.status_code,
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }

    def _format_issue_body(self, bug_report) -> str:
        """
        Format the bug report data into a structured GitHub issue body.
        """
        body_parts = []

        # Header
        body_parts.append("## 🐛 Bug Report")
        body_parts.append(
            f"**Reported by:** {bug_report.reporter.get_full_name() or bug_report.reporter.username}"
        )
        body_parts.append(f"**Email:** {bug_report.reporter_email}")
        body_parts.append(f"**Priority:** {bug_report.get_priority_display()}")
        body_parts.append(
            f"**Reported on:** {bug_report.created_on.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        body_parts.append("")

        # Bug description
        body_parts.append("### 📝 Description")
        body_parts.append(bug_report.description)
        body_parts.append("")

        # Steps to reproduce
        if bug_report.steps_to_reproduce:
            body_parts.append("### 🔄 Steps to Reproduce")
            body_parts.append(bug_report.steps_to_reproduce)
            body_parts.append("")

        # Expected vs actual behavior
        if bug_report.expected_behavior or bug_report.actual_behavior:
            body_parts.append("### 📊 Expected vs Actual Behavior")
            if bug_report.expected_behavior:
                body_parts.append("**Expected:**")
                body_parts.append(bug_report.expected_behavior)
                body_parts.append("")
            if bug_report.actual_behavior:
                body_parts.append("**Actual:**")
                body_parts.append(bug_report.actual_behavior)
                body_parts.append("")

        # Context information
        body_parts.append("### 🔧 Technical Context")
        if bug_report.current_url:
            body_parts.append(f"**URL:** {bug_report.current_url}")
        if bug_report.page_title:
            body_parts.append(f"**Page:** {bug_report.page_title}")

        # Browser information
        if bug_report.browser_info:
            body_parts.append("**Browser Info:**")
            browser_info = bug_report.browser_info
            if isinstance(browser_info, dict):
                for key, value in browser_info.items():
                    body_parts.append(f"- {key}: {value}")
            else:
                body_parts.append(f"- {browser_info}")

        if bug_report.user_agent:
            body_parts.append(f"**User Agent:** `{bug_report.user_agent}`")

        body_parts.append("")

        # Application state (if relevant)
        if bug_report.application_state and bug_report.application_state != {}:
            body_parts.append("### 🔍 Application State")
            try:
                state_str = json.dumps(bug_report.application_state, indent=2)
                body_parts.append("```json")
                body_parts.append(state_str)
                body_parts.append("```")
            except (TypeError, ValueError):
                body_parts.append(str(bug_report.application_state))
            body_parts.append("")

        # Screenshots and files
        if bug_report.screenshot:
            body_parts.append("### 📷 Screenshot")
            body_parts.append(f"Screenshot attached: `{bug_report.screenshot.name}`")
            body_parts.append("")

        if bug_report.additional_files:
            body_parts.append("### 📎 Additional Files")
            body_parts.append(f"Additional files: `{bug_report.additional_files.name}`")
            body_parts.append("")

        # Footer
        body_parts.append("---")
        body_parts.append(
            "*This issue was automatically created from a bug report in ProjectMeats.*"
        )
        body_parts.append(f"*Bug Report ID: #{bug_report.id}*")

        return "\n".join(body_parts)

    def _get_issue_labels(self, bug_report) -> List[str]:
        """
        Generate appropriate labels for the GitHub issue.
        """
        labels = ["bug", "auto-reported"]

        # Priority labels
        priority_labels = {
            "low": "priority:low",
            "medium": "priority:medium",
            "high": "priority:high",
            "critical": "priority:critical",
        }
        if bug_report.priority in priority_labels:
            labels.append(priority_labels[bug_report.priority])

        # Component labels based on URL/context
        if bug_report.current_url:
            url = bug_report.current_url.lower()
            if "accounts-receivables" in url:
                labels.append("component:accounts-receivables")
            elif "suppliers" in url:
                labels.append("component:suppliers")
            elif "customers" in url:
                labels.append("component:customers")
            elif "purchase-orders" in url:
                labels.append("component:purchase-orders")
            elif "dashboard" in url:
                labels.append("component:dashboard")
            else:
                labels.append("component:frontend")

        return labels

    def update_issue(
        self,
        issue_number: int,
        title: str = None,
        body: str = None,
        state: str = None,
        labels: List[str] = None,
    ) -> Dict[str, any]:
        """
        Update an existing GitHub issue.

        Args:
            issue_number: GitHub issue number
            title: New title (optional)
            body: New body (optional)
            state: New state - 'open' or 'closed' (optional)
            labels: New labels list (optional)

        Returns:
            Dict with update result
        """
        try:
            update_data = {}
            if title:
                update_data["title"] = title
            if body:
                update_data["body"] = body
            if state:
                update_data["state"] = state
            if labels:
                update_data["labels"] = labels

            if not update_data:
                return {"success": False, "error": "No update data provided"}

            response = requests.patch(
                f"{self.base_url}/issues/{issue_number}",
                headers=self._get_headers(),
                data=json.dumps(update_data),
                timeout=30,
            )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error_detail = (
                    response.json()
                    if response.content
                    else {"message": "Unknown error"}
                )
                return {
                    "success": False,
                    "error": f"GitHub API error {response.status_code}: {error_detail.get('message', 'Unknown error')}",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error updating issue: {str(e)}",
            }
