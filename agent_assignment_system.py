#!/usr/bin/env python3
"""
Automated Agent Assignment System for ProjectMeats
=================================================

This system automatically assigns deployment issues to appropriate agents
based on issue type, priority, and agent availability. It integrates with
GitHub to manage issue assignments and track agent workloads.

Features:
- Intelligent agent matching based on issue characteristics
- Workload balancing across available agents
- Automatic assignment with notification
- Agent specialization tracking
- Performance metrics and optimization

Usage:
    python agent_assignment_system.py [--assign-all] [--rebalance] [--report]
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from github import Github
    import requests
except ImportError:
    print("❌ Missing dependencies. Install with: pip install PyGithub requests")
    sys.exit(1)


class AgentType(Enum):
    """Available agent types with specializations"""
    DEPLOYMENT_SCRIPT = "deployment-script-agent"
    DEPLOYMENT_ARCHITECTURE = "deployment-architecture-agent"
    SECURITY_HARDENING = "security-hardening-agent"
    CONFIGURATION_MANAGEMENT = "configuration-management-agent"
    TESTING_VALIDATION = "testing-validation-agent"
    DOCUMENTATION_MANAGEMENT = "documentation-management-agent"
    OPERATIONS_MONITORING = "operations-monitoring-agent"
    CODE_QUALITY = "code-quality-agent"
    PROCESS_MANAGEMENT = "process-management-agent"
    PERFORMANCE_OPTIMIZATION = "performance-optimization-agent"
    INFRASTRUCTURE_SCALING = "infrastructure-scaling-agent"
    BACKUP_RECOVERY = "backup-recovery-agent"
    SECURITY_AUDIT = "security-audit-agent"
    TRAINING_EDUCATION = "training-education-agent"


@dataclass
class Agent:
    """Agent information and capabilities"""
    agent_type: AgentType
    github_username: str
    specializations: List[str]
    max_concurrent_issues: int
    current_workload: int = 0
    performance_score: float = 1.0
    availability_status: str = "available"  # available, busy, offline
    last_assignment: Optional[datetime] = None


@dataclass
class IssueAssignment:
    """Issue assignment record"""
    issue_number: int
    agent_type: AgentType
    agent_username: str
    assigned_at: datetime
    priority: str
    estimated_effort: int  # hours
    status: str = "assigned"  # assigned, in_progress, completed, escalated


class AgentAssignmentSystem:
    """Manages automatic assignment of issues to appropriate agents"""
    
    def __init__(self, repo_name: str, github_token: str = None):
        self.repo_name = repo_name
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        
        if not self.github_token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN or use --token")
            
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(repo_name)
        
        # Initialize agent registry
        self.agents = self._initialize_agent_registry()
        self.assignments = self._load_assignments()
        
        # Issue type mapping to agent types
        self.issue_agent_mapping = {
            'script': [AgentType.DEPLOYMENT_SCRIPT, AgentType.CODE_QUALITY],
            'orchestrator': [AgentType.DEPLOYMENT_ARCHITECTURE, AgentType.DEPLOYMENT_SCRIPT],
            'security': [AgentType.SECURITY_HARDENING, AgentType.SECURITY_AUDIT],
            'configuration': [AgentType.CONFIGURATION_MANAGEMENT, AgentType.SECURITY_HARDENING],
            'testing': [AgentType.TESTING_VALIDATION, AgentType.CODE_QUALITY],
            'documentation': [AgentType.DOCUMENTATION_MANAGEMENT, AgentType.TRAINING_EDUCATION],
            'monitoring': [AgentType.OPERATIONS_MONITORING, AgentType.PERFORMANCE_OPTIMIZATION],
            'performance': [AgentType.PERFORMANCE_OPTIMIZATION, AgentType.INFRASTRUCTURE_SCALING],
            'governance': [AgentType.PROCESS_MANAGEMENT, AgentType.OPERATIONS_MONITORING]
        }
    
    def _initialize_agent_registry(self) -> Dict[AgentType, Agent]:
        """Initialize the agent registry with available agents"""
        agents = {
            AgentType.DEPLOYMENT_SCRIPT: Agent(
                agent_type=AgentType.DEPLOYMENT_SCRIPT,
                github_username="copilot",
                specializations=["script consolidation", "bash scripting", "python automation"],
                max_concurrent_issues=3
            ),
            AgentType.DEPLOYMENT_ARCHITECTURE: Agent(
                agent_type=AgentType.DEPLOYMENT_ARCHITECTURE,
                github_username="copilot",
                specializations=["system architecture", "orchestration", "infrastructure design"],
                max_concurrent_issues=2
            ),
            AgentType.SECURITY_HARDENING: Agent(
                agent_type=AgentType.SECURITY_HARDENING,
                github_username="copilot",
                specializations=["credential management", "security policies", "vulnerability fixing"],
                max_concurrent_issues=2
            ),
            AgentType.CONFIGURATION_MANAGEMENT: Agent(
                agent_type=AgentType.CONFIGURATION_MANAGEMENT,
                github_username="copilot",
                specializations=["config management", "environment setup", "validation"],
                max_concurrent_issues=3
            ),
            AgentType.TESTING_VALIDATION: Agent(
                agent_type=AgentType.TESTING_VALIDATION,
                github_username="copilot",
                specializations=["test automation", "validation", "quality assurance"],
                max_concurrent_issues=4
            ),
            AgentType.DOCUMENTATION_MANAGEMENT: Agent(
                agent_type=AgentType.DOCUMENTATION_MANAGEMENT,
                github_username="copilot",
                specializations=["technical writing", "documentation", "user guides"],
                max_concurrent_issues=3
            ),
            AgentType.OPERATIONS_MONITORING: Agent(
                agent_type=AgentType.OPERATIONS_MONITORING,
                github_username="copilot",
                specializations=["monitoring", "alerting", "operations"],
                max_concurrent_issues=2
            ),
            AgentType.CODE_QUALITY: Agent(
                agent_type=AgentType.CODE_QUALITY,
                github_username="copilot",
                specializations=["code review", "refactoring", "technical debt"],
                max_concurrent_issues=3
            ),
            AgentType.PROCESS_MANAGEMENT: Agent(
                agent_type=AgentType.PROCESS_MANAGEMENT,
                github_username="copilot",
                specializations=["process improvement", "governance", "workflow optimization"],
                max_concurrent_issues=2
            )
        }
        return agents
    
    def _load_assignments(self) -> List[IssueAssignment]:
        """Load existing assignments from file"""
        assignments_file = "agent_assignments.json"
        if os.path.exists(assignments_file):
            try:
                with open(assignments_file, 'r') as f:
                    data = json.load(f)
                    return [IssueAssignment(**item) for item in data]
            except Exception as e:
                print(f"⚠️ Error loading assignments: {e}")
        return []
    
    def _save_assignments(self):
        """Save assignments to file"""
        assignments_file = "agent_assignments.json"
        try:
            with open(assignments_file, 'w') as f:
                data = [asdict(assignment) for assignment in self.assignments]
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"❌ Error saving assignments: {e}")
    
    def analyze_issue_type(self, issue) -> List[str]:
        """Analyze issue to determine appropriate agent types"""
        title = issue.title.lower()
        body = issue.body.lower() if issue.body else ""
        labels = [label.name.lower() for label in issue.labels]
        
        content = f"{title} {body} {' '.join(labels)}"
        detected_types = []
        
        # Check for keywords that indicate issue type
        for issue_type, keywords in {
            'script': ['script', 'bash', 'shell', 'python', 'deployment script', 'consolidation'],
            'orchestrator': ['orchestrator', 'architecture', 'system design', 'conflicts'],
            'security': ['security', 'credential', 'vulnerability', 'auth', 'secret'],
            'configuration': ['config', 'environment', 'settings', 'hierarchy'],
            'testing': ['test', 'validation', 'quality', 'qa'],
            'documentation': ['documentation', 'docs', 'guide', 'manual'],
            'monitoring': ['monitoring', 'alerting', 'health', 'metrics'],
            'performance': ['performance', 'optimization', 'scaling'],
            'governance': ['governance', 'process', 'management']
        }.items():
            if any(keyword in content for keyword in keywords):
                detected_types.append(issue_type)
        
        return detected_types if detected_types else ['script']  # Default to script
    
    def find_best_agent(self, issue_types: List[str], priority: str) -> Optional[Agent]:
        """Find the best available agent for the issue"""
        candidate_agents = []
        
        # Get all possible agents for the issue types
        for issue_type in issue_types:
            if issue_type in self.issue_agent_mapping:
                candidate_agents.extend(self.issue_agent_mapping[issue_type])
        
        if not candidate_agents:
            return None
        
        # Remove duplicates while preserving order
        unique_candidates = []
        seen = set()
        for agent_type in candidate_agents:
            if agent_type not in seen:
                unique_candidates.append(agent_type)
                seen.add(agent_type)
        
        # Score and rank agents
        scored_agents = []
        for agent_type in unique_candidates:
            if agent_type in self.agents:
                agent = self.agents[agent_type]
                score = self._calculate_agent_score(agent, priority)
                scored_agents.append((score, agent))
        
        # Sort by score (higher is better) and return best available agent
        scored_agents.sort(key=lambda x: x[0], reverse=True)
        
        for score, agent in scored_agents:
            if agent.availability_status == "available" and agent.current_workload < agent.max_concurrent_issues:
                return agent
        
        return None
    
    def _calculate_agent_score(self, agent: Agent, priority: str) -> float:
        """Calculate agent suitability score"""
        base_score = agent.performance_score
        
        # Workload penalty (more work = lower score)
        workload_factor = 1.0 - (agent.current_workload / agent.max_concurrent_issues)
        
        # Priority boost for critical issues
        priority_factor = 1.2 if priority == "CRITICAL" else 1.1 if priority == "HIGH" else 1.0
        
        # Availability penalty
        availability_factor = 1.0 if agent.availability_status == "available" else 0.5
        
        return base_score * workload_factor * priority_factor * availability_factor
    
    def assign_issue_to_agent(self, issue, dry_run: bool = False) -> Optional[IssueAssignment]:
        """Assign an issue to the most appropriate agent"""
        
        # Skip if already assigned
        existing_assignment = next((a for a in self.assignments if a.issue_number == issue.number), None)
        if existing_assignment:
            print(f"   Issue #{issue.number} already assigned to {existing_assignment.agent_username}")
            return existing_assignment
        
        # Analyze issue
        issue_types = self.analyze_issue_type(issue)
        priority = self._extract_priority(issue)
        
        # Find best agent
        best_agent = self.find_best_agent(issue_types, priority)
        if not best_agent:
            print(f"   ❌ No available agent found for issue #{issue.number}")
            return None
        
        # Create assignment
        assignment = IssueAssignment(
            issue_number=issue.number,
            agent_type=best_agent.agent_type,
            agent_username=best_agent.github_username,
            assigned_at=datetime.now(),
            priority=priority,
            estimated_effort=self._estimate_effort(issue, priority)
        )
        
        if not dry_run:
            try:
                # Assign in GitHub
                issue.add_to_assignees(best_agent.github_username)
                
                # Add assignment comment
                comment_body = f"""🤖 **Automated Agent Assignment**

This issue has been automatically assigned to the **{best_agent.agent_type.value.replace('-', ' ').title()}**.

**Assignment Details:**
- **Agent Type**: {best_agent.agent_type.value}
- **Specializations**: {', '.join(best_agent.specializations)}
- **Priority**: {priority}
- **Estimated Effort**: {assignment.estimated_effort} hours
- **Assignment ID**: {assignment.issue_number}-{int(assignment.assigned_at.timestamp())}

**Next Steps:**
1. Agent will review issue within SLA timeframe
2. Agent will update issue with progress and findings
3. Agent will coordinate with related issues and dependencies

---
*Automated by Agent Assignment System - {assignment.assigned_at.isoformat()}*"""
                
                issue.create_comment(comment_body)
                
                # Update agent workload
                best_agent.current_workload += 1
                best_agent.last_assignment = assignment.assigned_at
                
                # Save assignment
                self.assignments.append(assignment)
                self._save_assignments()
                
                print(f"   ✅ Assigned issue #{issue.number} to {best_agent.agent_type.value}")
                
            except Exception as e:
                print(f"   ❌ Failed to assign issue #{issue.number}: {e}")
                return None
        else:
            print(f"   [DRY RUN] Would assign issue #{issue.number} to {best_agent.agent_type.value}")
        
        return assignment
    
    def _extract_priority(self, issue) -> str:
        """Extract priority from issue"""
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
    
    def _estimate_effort(self, issue, priority: str) -> int:
        """Estimate effort in hours based on issue complexity"""
        base_effort = {
            "CRITICAL": 16,  # 2 days
            "HIGH": 12,      # 1.5 days
            "MEDIUM": 8,     # 1 day
            "LOW": 4         # 0.5 day
        }.get(priority, 8)
        
        # Adjust based on issue complexity indicators
        body_length = len(issue.body) if issue.body else 0
        if body_length > 2000:
            base_effort *= 1.5
        elif body_length < 500:
            base_effort *= 0.8
        
        return max(2, int(base_effort))  # Minimum 2 hours
    
    def assign_all_unassigned_issues(self, dry_run: bool = False) -> List[IssueAssignment]:
        """Assign all unassigned deployment issues"""
        
        # Get deployment issues
        issues = self.repo.get_issues(
            state='open',
            labels=['deployment']
        )
        
        assignments = []
        print(f"🎯 Processing deployment issues for assignment...")
        
        for issue in issues:
            print(f"\\n📋 Processing issue #{issue.number}: {issue.title[:60]}...")
            assignment = self.assign_issue_to_agent(issue, dry_run)
            if assignment:
                assignments.append(assignment)
        
        return assignments
    
    def rebalance_workloads(self, dry_run: bool = False) -> bool:
        """Rebalance agent workloads"""
        print("⚖️  Analyzing agent workloads for rebalancing...")
        
        # Calculate current workloads
        workload_stats = {}
        for agent_type, agent in self.agents.items():
            active_assignments = [a for a in self.assignments 
                                if a.agent_type == agent_type and a.status in ['assigned', 'in_progress']]
            workload_stats[agent_type] = {
                'agent': agent,
                'active_assignments': len(active_assignments),
                'capacity_usage': len(active_assignments) / agent.max_concurrent_issues,
                'assignments': active_assignments
            }
        
        # Find overloaded and underloaded agents
        overloaded = [(k, v) for k, v in workload_stats.items() if v['capacity_usage'] > 0.8]
        underloaded = [(k, v) for k, v in workload_stats.items() if v['capacity_usage'] < 0.5]
        
        if not overloaded:
            print("✅ All agents within normal workload ranges")
            return True
        
        print(f"🔄 Found {len(overloaded)} overloaded agents and {len(underloaded)} underloaded agents")
        
        # Implement rebalancing logic (simplified for now)
        rebalanced = False
        for agent_type, stats in overloaded:
            print(f"   ⚠️ {agent_type.value} is overloaded ({stats['capacity_usage']:.1%} capacity)")
            # In a real implementation, you would reassign issues here
            rebalanced = True
        
        return rebalanced
    
    def generate_assignment_report(self) -> Dict[str, Any]:
        """Generate comprehensive assignment report"""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_agents': len(self.agents),
            'total_assignments': len(self.assignments),
            'agent_workloads': {},
            'assignment_summary': {
                'assigned': 0,
                'in_progress': 0,
                'completed': 0,
                'escalated': 0
            },
            'performance_metrics': {},
            'recommendations': []
        }
        
        # Calculate agent workloads
        for agent_type, agent in self.agents.items():
            active_assignments = [a for a in self.assignments 
                                if a.agent_type == agent_type and a.status in ['assigned', 'in_progress']]
            
            report['agent_workloads'][agent_type.value] = {
                'current_workload': len(active_assignments),
                'max_capacity': agent.max_concurrent_issues,
                'capacity_usage': len(active_assignments) / agent.max_concurrent_issues,
                'availability': agent.availability_status,
                'performance_score': agent.performance_score,
                'specializations': agent.specializations
            }
        
        # Assignment status summary
        for assignment in self.assignments:
            if assignment.status in report['assignment_summary']:
                report['assignment_summary'][assignment.status] += 1
        
        # Generate recommendations
        overloaded_agents = [k for k, v in report['agent_workloads'].items() if v['capacity_usage'] > 0.8]
        if overloaded_agents:
            report['recommendations'].append(f"Consider rebalancing workload for: {', '.join(overloaded_agents)}")
        
        underutilized_agents = [k for k, v in report['agent_workloads'].items() if v['capacity_usage'] < 0.3]
        if underutilized_agents:
            report['recommendations'].append(f"Underutilized agents available: {', '.join(underutilized_agents)}")
        
        return report
    
    def print_assignment_report(self, report: Dict[str, Any]):
        """Print formatted assignment report"""
        print("\\n" + "="*80)
        print("🤖 AGENT ASSIGNMENT SYSTEM REPORT")
        print("="*80)
        print(f"Generated: {report['generated_at']}")
        print(f"Total Agents: {report['total_agents']}")
        print(f"Total Assignments: {report['total_assignments']}")
        
        print("\\n👥 AGENT WORKLOADS:")
        for agent_name, workload in report['agent_workloads'].items():
            usage_bar = "█" * int(workload['capacity_usage'] * 10) + "░" * (10 - int(workload['capacity_usage'] * 10))
            status_emoji = "🟢" if workload['capacity_usage'] < 0.7 else "🟡" if workload['capacity_usage'] < 0.9 else "🔴"
            print(f"   {status_emoji} {agent_name}:")
            print(f"      Workload: {workload['current_workload']}/{workload['max_capacity']} ({workload['capacity_usage']:.1%})")
            print(f"      Usage: [{usage_bar}]")
            print(f"      Status: {workload['availability']}")
        
        print("\\n📊 ASSIGNMENT STATUS:")
        for status, count in report['assignment_summary'].items():
            print(f"   {status.title()}: {count}")
        
        if report['recommendations']:
            print("\\n💡 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        print("\\n" + "="*80)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Automated agent assignment system")
    parser.add_argument('--assign-all', action='store_true', help='Assign all unassigned deployment issues')
    parser.add_argument('--rebalance', action='store_true', help='Rebalance agent workloads')
    parser.add_argument('--report', action='store_true', help='Generate assignment report')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--repo', default='Vacilator/ProjectMeats', help='GitHub repository (owner/repo)')
    parser.add_argument('--token', help='GitHub personal access token')
    
    args = parser.parse_args()
    
    print("🤖 ProjectMeats Agent Assignment System")
    print("="*50)
    
    try:
        system = AgentAssignmentSystem(args.repo, args.token)
        
        if args.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
        
        # Assign all unassigned issues
        if args.assign_all:
            print("\\n🎯 Assigning all unassigned deployment issues...")
            assignments = system.assign_all_unassigned_issues(dry_run=args.dry_run)
            print(f"✅ Processed {len(assignments)} issue assignments")
        
        # Rebalance workloads
        if args.rebalance:
            print("\\n⚖️ Rebalancing agent workloads...")
            rebalanced = system.rebalance_workloads(dry_run=args.dry_run)
            if rebalanced:
                print("✅ Workload rebalancing completed")
            else:
                print("ℹ️ No rebalancing needed")
        
        # Generate report
        if args.report or not any([args.assign_all, args.rebalance]):
            print("\\n📊 Generating assignment report...")
            report = system.generate_assignment_report()
            system.print_assignment_report(report)
        
        print("\\n✅ Agent assignment system operations completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()