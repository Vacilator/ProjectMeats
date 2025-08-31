#!/usr/bin/env python3
"""
Deployment Issues Monitoring and Management System
================================================

This system automatically monitors GitHub Issues related to deployment problems,
tracks progress, updates task backlogs, and escalates issues when SLAs are breached.

Features:
- Automatic issue status tracking
- SLA monitoring and breach alerts
- Progress reporting and metrics
- Integration with GitHub API
- Automated escalation procedures

Usage:
    python monitor_deployment_issues.py [--report] [--escalate] [--update-backlog]
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time

try:
    from github import Github
    import requests
except ImportError:
    print("❌ Missing dependencies. Install with: pip install PyGithub requests")
    sys.exit(1)


class DeploymentIssueMonitor:
    """Monitors and manages deployment-related GitHub Issues"""
    
    def __init__(self, repo_name: str, github_token: str = None):
        self.repo_name = repo_name
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        
        if not self.github_token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN or use --token")
            
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(repo_name)
        
        # SLA definitions (in hours)
        self.sla_hours = {
            "CRITICAL": 24,
            "HIGH": 48,
            "MEDIUM": 168,  # 1 week
            "LOW": 336      # 2 weeks
        }
        
    def get_deployment_issues(self) -> List[Any]:
        """Get all deployment-related issues"""
        try:
            issues = self.repo.get_issues(
                state='open',
                labels=['deployment']
            )
            return list(issues)
        except Exception as e:
            print(f"❌ Error fetching issues: {e}")
            return []
    
    def analyze_issue_priority(self, issue) -> str:
        """Extract priority from issue title or labels"""
        title = issue.title.lower()
        labels = [label.name.lower() for label in issue.labels]
        
        if any('critical' in item for item in [title] + labels):
            return "CRITICAL"
        elif any('high' in item for item in [title] + labels):
            return "HIGH"
        elif any('medium' in item for item in [title] + labels):
            return "MEDIUM"
        else:
            return "LOW"
    
    def calculate_sla_status(self, issue) -> Dict[str, Any]:
        """Calculate SLA status for an issue"""
        priority = self.analyze_issue_priority(issue)
        sla_hours = self.sla_hours[priority]
        
        created_at = issue.created_at
        now = datetime.now(created_at.tzinfo)
        elapsed_hours = (now - created_at).total_seconds() / 3600
        
        remaining_hours = sla_hours - elapsed_hours
        is_breached = remaining_hours <= 0
        is_warning = remaining_hours <= (sla_hours * 0.2)  # Warning at 20% remaining
        
        return {
            'priority': priority,
            'sla_hours': sla_hours,
            'elapsed_hours': round(elapsed_hours, 1),
            'remaining_hours': round(remaining_hours, 1),
            'is_breached': is_breached,
            'is_warning': is_warning,
            'breach_percentage': round((elapsed_hours / sla_hours) * 100, 1)
        }
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        issues = self.get_deployment_issues()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_issues': len(issues),
            'issues_by_priority': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
            'sla_status': {'breached': 0, 'warning': 0, 'on_track': 0},
            'issues_detail': [],
            'escalations_needed': [],
            'summary_metrics': {}
        }
        
        total_elapsed = 0
        oldest_issue_days = 0
        
        for issue in issues:
            priority = self.analyze_issue_priority(issue)
            sla_status = self.calculate_sla_status(issue)
            
            report['issues_by_priority'][priority] += 1
            
            if sla_status['is_breached']:
                report['sla_status']['breached'] += 1
                report['escalations_needed'].append({
                    'issue_number': issue.number,
                    'title': issue.title,
                    'priority': priority,
                    'breach_hours': abs(sla_status['remaining_hours']),
                    'url': issue.html_url
                })
            elif sla_status['is_warning']:
                report['sla_status']['warning'] += 1
            else:
                report['sla_status']['on_track'] += 1
            
            # Calculate metrics
            total_elapsed += sla_status['elapsed_hours']
            issue_age_days = (datetime.now() - issue.created_at.replace(tzinfo=None)).days
            if issue_age_days > oldest_issue_days:
                oldest_issue_days = issue_age_days
            
            # Issue detail
            report['issues_detail'].append({
                'number': issue.number,
                'title': issue.title,
                'priority': priority,
                'state': issue.state,
                'created_at': issue.created_at.isoformat(),
                'assignees': [a.login for a in issue.assignees],
                'labels': [l.name for l in issue.labels],
                'sla_status': sla_status,
                'url': issue.html_url
            })
        
        # Summary metrics
        report['summary_metrics'] = {
            'average_issue_age_hours': round(total_elapsed / max(len(issues), 1), 1),
            'oldest_issue_days': oldest_issue_days,
            'sla_breach_rate': round((report['sla_status']['breached'] / max(len(issues), 1)) * 100, 1),
            'critical_issues': report['issues_by_priority']['CRITICAL'],
            'urgent_action_needed': len(report['escalations_needed']) > 0
        }
        
        return report
    
    def update_task_backlog(self, report: Dict[str, Any]) -> bool:
        """Update the deployment task backlog with current status"""
        try:
            backlog_path = "DEPLOYMENT_TASK_BACKLOG.md"
            
            # Read current backlog
            if os.path.exists(backlog_path):
                with open(backlog_path, 'r') as f:
                    content = f.read()
            else:
                print(f"❌ Backlog file not found: {backlog_path}")
                return False
            
            # Update progress metrics section
            progress_section = f"""## 📊 PROGRESS TRACKING

### Completion Metrics
- [ ] Critical Tasks: {report['issues_by_priority']['CRITICAL']} active
- [ ] High Priority: {report['issues_by_priority']['HIGH']} active  
- [ ] Medium Priority: {report['issues_by_priority']['MEDIUM']} active
- [ ] Total Issues: {report['total_issues']} active

### SLA Status
- 🔴 Breached: {report['sla_status']['breached']} issues
- 🟡 Warning: {report['sla_status']['warning']} issues
- 🟢 On Track: {report['sla_status']['on_track']} issues

### Key Metrics
- Average Issue Age: {report['summary_metrics']['average_issue_age_hours']} hours
- SLA Breach Rate: {report['summary_metrics']['sla_breach_rate']}%
- Oldest Issue: {report['summary_metrics']['oldest_issue_days']} days
- Urgent Action Needed: {'YES' if report['summary_metrics']['urgent_action_needed'] else 'NO'}

**Last Updated**: {report['generated_at']}"""
            
            # Replace existing progress section
            import re
            pattern = r'## 📊 PROGRESS TRACKING.*?(?=## |$)'
            updated_content = re.sub(pattern, progress_section + "\n\n", content, flags=re.DOTALL)
            
            # Write updated backlog
            with open(backlog_path, 'w') as f:
                f.write(updated_content)
            
            print(f"✅ Updated task backlog with current status")
            return True
            
        except Exception as e:
            print(f"❌ Error updating task backlog: {e}")
            return False
    
    def create_escalation_issues(self, escalations: List[Dict[str, Any]]) -> List[Any]:
        """Create escalation issues for SLA breaches"""
        created_escalations = []
        
        for escalation in escalations:
            try:
                escalation_title = f"🚨 SLA BREACH - Escalation for Issue #{escalation['issue_number']}"
                escalation_body = f"""# SLA Breach Escalation

## 🚨 Critical Alert: SLA Breach Detected

**Original Issue**: #{escalation['issue_number']} - {escalation['title']}
**Priority**: {escalation['priority']}
**Breach Duration**: {escalation['breach_hours']:.1f} hours over SLA
**Issue URL**: {escalation['url']}

## 📊 Breach Details

- **SLA Requirement**: {self.sla_hours[escalation['priority']]} hours
- **Actual Duration**: {escalation['breach_hours'] + self.sla_hours[escalation['priority']]:.1f} hours
- **Breach Percentage**: {((escalation['breach_hours'] + self.sla_hours[escalation['priority']]) / self.sla_hours[escalation['priority']]) * 100:.1f}%

## ⚡ Required Actions

1. **Immediate**: Senior agent review and intervention
2. **Emergency**: Escalate to project manager if no response in 2 hours
3. **Critical**: Consider hotfix deployment if blocking production

## 🎯 Escalation Path

1. **Level 1**: Senior {escalation['priority'].title()} Agent
2. **Level 2**: Project Manager (@copilot)
3. **Level 3**: Engineering Leadership

## 📞 Emergency Contacts

- **Deployment Team**: @copilot
- **Security Team**: (for security-related breaches)
- **Infrastructure Team**: (for system-related breaches)

---
**Auto-generated Escalation**: {datetime.now().isoformat()}
**Escalation ID**: ESC-{escalation['issue_number']}-{int(time.time())}
"""
                
                escalation_issue = self.repo.create_issue(
                    title=escalation_title,
                    body=escalation_body,
                    labels=['escalation', 'sla-breach', 'urgent', 'deployment'],
                    assignees=['copilot'] if 'copilot' in [c.login for c in self.repo.get_collaborators()] else []
                )
                
                created_escalations.append(escalation_issue)
                print(f"🚨 Created escalation issue #{escalation_issue.number} for breach of #{escalation['issue_number']}")
                
            except Exception as e:
                print(f"❌ Failed to create escalation for issue #{escalation['issue_number']}: {e}")
        
        return created_escalations
    
    def print_status_report(self, report: Dict[str, Any]):
        """Print formatted status report to console"""
        print("\\n" + "="*80)
        print("📊 DEPLOYMENT ISSUES STATUS REPORT")
        print("="*80)
        print(f"Generated: {report['generated_at']}")
        print(f"Total Issues: {report['total_issues']}")
        
        print("\\n🎯 ISSUES BY PRIORITY:")
        for priority, count in report['issues_by_priority'].items():
            emoji = {"CRITICAL": "🔴", "HIGH": "🟡", "MEDIUM": "🟢", "LOW": "⚪"}[priority]
            print(f"   {emoji} {priority}: {count}")
        
        print("\\n⏱️  SLA STATUS:")
        print(f"   🔴 Breached: {report['sla_status']['breached']}")
        print(f"   🟡 Warning: {report['sla_status']['warning']}")
        print(f"   🟢 On Track: {report['sla_status']['on_track']}")
        
        print("\\n📈 KEY METRICS:")
        metrics = report['summary_metrics']
        print(f"   Average Issue Age: {metrics['average_issue_age_hours']} hours")
        print(f"   SLA Breach Rate: {metrics['sla_breach_rate']}%")
        print(f"   Oldest Issue: {metrics['oldest_issue_days']} days")
        print(f"   Urgent Action Needed: {'YES ⚡' if metrics['urgent_action_needed'] else 'NO ✅'}")
        
        if report['escalations_needed']:
            print("\\n🚨 ESCALATIONS REQUIRED:")
            for escalation in report['escalations_needed']:
                print(f"   #{escalation['issue_number']}: {escalation['title']}")
                print(f"      Breach: {escalation['breach_hours']:.1f}h over {escalation['priority']} SLA")
        
        print("\\n📋 ISSUE DETAILS:")
        for issue in report['issues_detail']:
            status_emoji = "🔴" if issue['sla_status']['is_breached'] else "🟡" if issue['sla_status']['is_warning'] else "🟢"
            print(f"   {status_emoji} #{issue['number']}: {issue['title'][:60]}...")
            print(f"      Priority: {issue['priority']}, Age: {issue['sla_status']['elapsed_hours']:.1f}h")
        
        print("\\n" + "="*80)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Monitor deployment issues and manage SLAs")
    parser.add_argument('--report', action='store_true', help='Generate status report')
    parser.add_argument('--escalate', action='store_true', help='Create escalation issues for SLA breaches')
    parser.add_argument('--update-backlog', action='store_true', help='Update task backlog with current status')
    parser.add_argument('--export-json', help='Export report to JSON file')
    parser.add_argument('--repo', default='Vacilator/ProjectMeats', help='GitHub repository (owner/repo)')
    parser.add_argument('--token', help='GitHub personal access token')
    
    args = parser.parse_args()
    
    print("📊 ProjectMeats Deployment Issues Monitor")
    print("="*50)
    
    try:
        monitor = DeploymentIssueMonitor(args.repo, args.token)
        
        # Generate status report
        report = monitor.generate_status_report()
        
        if args.report or not any([args.escalate, args.update_backlog, args.export_json]):
            monitor.print_status_report(report)
        
        # Create escalations for SLA breaches
        if args.escalate and report['escalations_needed']:
            print(f"\\n🚨 Creating {len(report['escalations_needed'])} escalation issues...")
            escalations = monitor.create_escalation_issues(report['escalations_needed'])
            print(f"✅ Created {len(escalations)} escalation issues")
        
        # Update task backlog
        if args.update_backlog:
            print("\\n📝 Updating task backlog...")
            if monitor.update_task_backlog(report):
                print("✅ Task backlog updated successfully")
            else:
                print("❌ Failed to update task backlog")
        
        # Export to JSON
        if args.export_json:
            with open(args.export_json, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"✅ Report exported to {args.export_json}")
        
        # Summary
        print(f"\\n📊 Monitoring Summary:")
        print(f"   Total Issues Monitored: {report['total_issues']}")
        print(f"   SLA Breaches: {report['sla_status']['breached']}")
        print(f"   Urgent Action Required: {'YES' if report['summary_metrics']['urgent_action_needed'] else 'NO'}")
        
        # Exit with error code if urgent action needed
        if report['summary_metrics']['urgent_action_needed']:
            print("\\n⚠️  WARNING: Urgent action required due to SLA breaches!")
            sys.exit(1)
        else:
            print("\\n✅ All deployment issues within SLA requirements")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()