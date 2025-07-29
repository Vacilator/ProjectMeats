#!/usr/bin/env python3
"""
Agent Orchestration Framework for ProjectMeats

This script provides automated task management and conflict prevention
for agents working on the ProjectMeats migration project.
"""

import json
import os
import sys
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import subprocess

class AgentOrchestrator:
    """Manages agent task assignment and conflict prevention."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tasks_file = project_root / "docs" / "agent_tasks.json"
        self.activity_log = project_root / "docs" / "agent_activity_log.md"
        self.todo_system = project_root / "docs" / "agent_todo_system.md"
        
        # Initialize tasks database if it doesn't exist
        if not self.tasks_file.exists():
            self._initialize_tasks_database()
    
    def _initialize_tasks_database(self):
        """Initialize the tasks database with current TO-DO items."""
        tasks = {
            "tasks": {
                "TASK-001": {
                    "title": "Fix failing purchase order creation test",
                    "priority": "P0",
                    "status": "available",
                    "estimate_hours": 3,
                    "files": ["backend/apps/purchase_orders/tests.py"],
                    "dependencies": [],
                    "conflicts_with": [],
                    "assigned_to": None,
                    "created_date": datetime.datetime.now().isoformat(),
                    "description": "Fix the failing test in purchase order creation API",
                    "validation_criteria": "All 77 tests pass",
                    "category": "bug_fix"
                },
                "TASK-002": {
                    "title": "Add Jest tests for React components",
                    "priority": "P0",
                    "status": "available", 
                    "estimate_hours": 10,
                    "files": ["frontend/src/screens/*.test.tsx", "frontend/src/components/*.test.tsx"],
                    "dependencies": [],
                    "conflicts_with": [],
                    "assigned_to": None,
                    "created_date": datetime.datetime.now().isoformat(),
                    "description": "Add comprehensive Jest tests for all React components",
                    "validation_criteria": "80%+ test coverage for all components",
                    "category": "testing"
                },
                "TASK-003": {
                    "title": "Set up automated test running in CI/CD",
                    "priority": "P0",
                    "status": "available",
                    "estimate_hours": 5,
                    "files": [".github/workflows/", "Makefile"],
                    "dependencies": [],
                    "conflicts_with": [],
                    "assigned_to": None,
                    "created_date": datetime.datetime.now().isoformat(),
                    "description": "Set up GitHub Actions for automated testing",
                    "validation_criteria": "Tests run automatically on PR creation",
                    "category": "devops"
                },
                "TASK-004": {
                    "title": "Database query optimization audit",
                    "priority": "P1",
                    "status": "available",
                    "estimate_hours": 7,
                    "files": ["backend/apps/*/models.py", "backend/apps/*/views.py"],
                    "dependencies": ["TASK-001"],
                    "conflicts_with": [],
                    "assigned_to": None,
                    "created_date": datetime.datetime.now().isoformat(),
                    "description": "Audit and optimize database queries across all entities",
                    "validation_criteria": "Query count reduction measured and documented",
                    "category": "performance"
                },
                "TASK-005": {
                    "title": "Security validation and hardening",
                    "priority": "P1",
                    "status": "available",
                    "estimate_hours": 5,
                    "files": ["backend/projectmeats/settings.py", "security middleware"],
                    "dependencies": [],
                    "conflicts_with": [],
                    "assigned_to": None,
                    "created_date": datetime.datetime.now().isoformat(),
                    "description": "Comprehensive security audit and hardening",
                    "validation_criteria": "Security audit passes with no critical issues",
                    "category": "security"
                },
                "TASK-006": {
                    "title": "Modernize dashboard with business KPIs",
                    "priority": "P2",
                    "status": "available",
                    "estimate_hours": 10,
                    "files": ["frontend/src/screens/DashboardScreen.tsx"],
                    "dependencies": ["TASK-002"],
                    "conflicts_with": [],
                    "assigned_to": None,
                    "created_date": datetime.datetime.now().isoformat(),
                    "description": "Create modern business intelligence dashboard",
                    "validation_criteria": "Stakeholder approval on design",
                    "category": "ui_ux"
                },
                "TASK-007": {
                    "title": "Implement responsive design system",
                    "priority": "P2",
                    "status": "available",
                    "estimate_hours": 14,
                    "files": ["frontend/src/components/DesignSystem.tsx"],
                    "dependencies": ["TASK-002"],
                    "conflicts_with": ["TASK-006"],
                    "assigned_to": None,
                    "created_date": datetime.datetime.now().isoformat(),
                    "description": "Implement comprehensive responsive design system",
                    "validation_criteria": "Mobile-friendly on all screens",
                    "category": "ui_ux"
                }
            },
            "agents": {},
            "metadata": {
                "last_updated": datetime.datetime.now().isoformat(),
                "version": "1.0",
                "total_tasks": 7
            }
        }
        
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        print(f"✅ Initialized tasks database with {len(tasks['tasks'])} tasks")
    
    def load_tasks(self) -> Dict:
        """Load tasks from the database."""
        with open(self.tasks_file, 'r') as f:
            return json.load(f)
    
    def save_tasks(self, tasks: Dict):
        """Save tasks to the database."""
        tasks['metadata']['last_updated'] = datetime.datetime.now().isoformat()
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
    
    def get_available_tasks(self) -> List[Dict]:
        """Get all available tasks sorted by priority."""
        tasks_data = self.load_tasks()
        available = []
        
        for task_id, task in tasks_data['tasks'].items():
            if task['status'] == 'available':
                # Check if dependencies are met
                dependencies_met = True
                for dep_id in task['dependencies']:
                    dep_task = tasks_data['tasks'].get(dep_id)
                    if not dep_task or dep_task['status'] != 'completed':
                        dependencies_met = False
                        break
                
                if dependencies_met:
                    task['id'] = task_id
                    available.append(task)
        
        # Sort by priority (P0, P1, P2, P3)
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        available.sort(key=lambda x: priority_order.get(x['priority'], 99))
        
        return available
    
    def check_conflicts(self, task_id: str, agent_id: str) -> List[str]:
        """Check for conflicts with other assigned tasks."""
        tasks_data = self.load_tasks()
        task = tasks_data['tasks'].get(task_id)
        
        if not task:
            return [f"Task {task_id} not found"]
        
        conflicts = []
        
        # Check explicit conflicts
        for conflict_task_id in task['conflicts_with']:
            conflict_task = tasks_data['tasks'].get(conflict_task_id)
            if conflict_task and conflict_task['status'] == 'in_progress':
                conflicts.append(f"Conflicts with {conflict_task_id}: {conflict_task['title']} (assigned to {conflict_task['assigned_to']})")
        
        # Check file-level conflicts
        task_files = set(task['files'])
        for other_task_id, other_task in tasks_data['tasks'].items():
            if other_task_id != task_id and other_task['status'] == 'in_progress':
                other_files = set(other_task['files'])
                file_conflicts = task_files.intersection(other_files)
                if file_conflicts:
                    conflicts.append(f"File conflict with {other_task_id}: {list(file_conflicts)} (assigned to {other_task['assigned_to']})")
        
        return conflicts
    
    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent."""
        conflicts = self.check_conflicts(task_id, agent_id)
        
        if conflicts:
            print("❌ Cannot assign task due to conflicts:")
            for conflict in conflicts:
                print(f"   - {conflict}")
            return False
        
        tasks_data = self.load_tasks()
        task = tasks_data['tasks'].get(task_id)
        
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        if task['status'] != 'available':
            print(f"❌ Task {task_id} is not available (status: {task['status']})")
            return False
        
        # Update task
        task['status'] = 'in_progress'
        task['assigned_to'] = agent_id
        task['started_date'] = datetime.datetime.now().isoformat()
        
        # Update agent record
        if 'agents' not in tasks_data:
            tasks_data['agents'] = {}
        
        if agent_id not in tasks_data['agents']:
            tasks_data['agents'][agent_id] = {
                'name': agent_id,
                'tasks_assigned': [],
                'tasks_completed': [],
                'total_hours': 0
            }
        
        tasks_data['agents'][agent_id]['tasks_assigned'].append(task_id)
        
        self.save_tasks(tasks_data)
        
        # Log to activity log
        self._log_agent_activity(agent_id, f"Assigned task {task_id}: {task['title']}")
        
        print(f"✅ Assigned {task_id} to {agent_id}")
        print(f"📋 Task: {task['title']}")
        print(f"⏰ Estimate: {task['estimate_hours']} hours")
        print(f"📁 Files: {', '.join(task['files'])}")
        
        return True
    
    def update_task_status(self, task_id: str, agent_id: str, status: str, notes: str = ""):
        """Update task status and progress."""
        tasks_data = self.load_tasks()
        task = tasks_data['tasks'].get(task_id)
        
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        if task['assigned_to'] != agent_id:
            print(f"❌ Task {task_id} is not assigned to {agent_id}")
            return False
        
        valid_statuses = ['in_progress', 'blocked', 'completed', 'cancelled']
        if status not in valid_statuses:
            print(f"❌ Invalid status. Use one of: {valid_statuses}")
            return False
        
        # Update task
        old_status = task['status']
        task['status'] = status
        task['last_updated'] = datetime.datetime.now().isoformat()
        
        if notes:
            if 'progress_notes' not in task:
                task['progress_notes'] = []
            task['progress_notes'].append({
                'date': datetime.datetime.now().isoformat(),
                'agent': agent_id,
                'status': status,
                'notes': notes
            })
        
        # Handle completion
        if status == 'completed':
            task['completed_date'] = datetime.datetime.now().isoformat()
            agent_data = tasks_data['agents'][agent_id]
            agent_data['tasks_completed'].append(task_id)
            agent_data['total_hours'] += task['estimate_hours']
        
        self.save_tasks(tasks_data)
        
        # Log to activity log
        self._log_agent_activity(agent_id, f"Updated {task_id} status: {old_status} → {status}. Notes: {notes}")
        
        print(f"✅ Updated {task_id} status: {old_status} → {status}")
        if notes:
            print(f"📝 Notes: {notes}")
        
        return True
    
    def _log_agent_activity(self, agent_id: str, activity: str):
        """Log agent activity to the activity log."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        log_entry = f"## [{timestamp}] - Agent: {agent_id}\n\n"
        log_entry += f"### 🔄 Progress Update\n"
        log_entry += f"- **Activity**: {activity}\n"
        log_entry += f"- **Timestamp**: {timestamp}\n\n"
        log_entry += "---\n\n"
        
        # Read existing log
        if self.activity_log.exists():
            with open(self.activity_log, 'r') as f:
                existing_content = f.read()
        else:
            existing_content = "# Agent Activity Log\n\n"
        
        # Insert new entry after the header
        lines = existing_content.split('\n')
        header_end = 0
        for i, line in enumerate(lines):
            if line.startswith('## [') or i > 20:  # Find first existing entry or reasonable header
                header_end = i
                break
        
        new_content = '\n'.join(lines[:header_end]) + '\n\n' + log_entry + '\n'.join(lines[header_end:])
        
        with open(self.activity_log, 'w') as f:
            f.write(new_content)
    
    def get_agent_status(self, agent_id: str = None) -> Dict:
        """Get status for a specific agent or all agents."""
        tasks_data = self.load_tasks()
        
        if agent_id:
            agent_data = tasks_data['agents'].get(agent_id, {})
            return {agent_id: agent_data}
        else:
            return tasks_data['agents']
    
    def get_project_status(self) -> Dict:
        """Get overall project status."""
        tasks_data = self.load_tasks()
        
        status_counts = {}
        total_hours = 0
        completed_hours = 0
        
        for task in tasks_data['tasks'].values():
            status = task['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            total_hours += task['estimate_hours']
            
            if status == 'completed':
                completed_hours += task['estimate_hours']
        
        return {
            'total_tasks': len(tasks_data['tasks']),
            'status_breakdown': status_counts,
            'total_estimated_hours': total_hours,
            'completed_hours': completed_hours,
            'completion_percentage': (completed_hours / total_hours) * 100 if total_hours > 0 else 0,
            'active_agents': len([a for a in tasks_data['agents'].values() if a.get('tasks_assigned')]),
            'last_updated': tasks_data['metadata']['last_updated']
        }
    
    def generate_progress_report(self) -> str:
        """Generate a comprehensive progress report."""
        status = self.get_project_status()
        tasks_data = self.load_tasks()
        
        report = f"""
# ProjectMeats Agent Orchestration Progress Report

Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Project Overview

- **Total Tasks**: {status['total_tasks']}
- **Completion**: {status['completion_percentage']:.1f}% ({status['completed_hours']}/{status['total_estimated_hours']} hours)
- **Active Agents**: {status['active_agents']}

## 📈 Task Status Breakdown

"""
        
        for status_name, count in status['status_breakdown'].items():
            percentage = (count / status['total_tasks']) * 100
            report += f"- **{status_name.title()}**: {count} tasks ({percentage:.1f}%)\n"
        
        report += "\n## 🎯 High Priority Tasks\n\n"
        
        available_tasks = self.get_available_tasks()
        high_priority = [t for t in available_tasks if t['priority'] in ['P0', 'P1']]
        
        if high_priority:
            for task in high_priority[:5]:  # Top 5 high priority
                report += f"- **{task['id']}** ({task['priority']}): {task['title']} - {task['estimate_hours']}h\n"
        else:
            report += "No high priority tasks available.\n"
        
        report += "\n## 👥 Agent Activity\n\n"
        
        for agent_id, agent_data in tasks_data['agents'].items():
            assigned = len(agent_data.get('tasks_assigned', []))
            completed = len(agent_data.get('tasks_completed', []))
            hours = agent_data.get('total_hours', 0)
            
            report += f"- **{agent_id}**: {assigned} assigned, {completed} completed, {hours}h total\n"
        
        report += f"\n## 🔄 Recent Updates\n\n"
        report += f"Last database update: {status['last_updated']}\n"
        
        return report

def main():
    """Main CLI interface for agent orchestration."""
    parser = argparse.ArgumentParser(description='ProjectMeats Agent Orchestration Framework')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List available tasks
    list_parser = subparsers.add_parser('list-tasks', help='List available tasks')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--priority', help='Filter by priority')
    
    # Assign task
    assign_parser = subparsers.add_parser('assign-task', help='Assign task to agent')
    assign_parser.add_argument('task_id', help='Task ID to assign')
    assign_parser.add_argument('agent_id', help='Agent ID')
    
    # Update task
    update_parser = subparsers.add_parser('update-task', help='Update task status')
    update_parser.add_argument('task_id', help='Task ID')
    update_parser.add_argument('agent_id', help='Agent ID')
    update_parser.add_argument('status', help='New status')
    update_parser.add_argument('--notes', default='', help='Progress notes')
    
    # Check conflicts
    conflict_parser = subparsers.add_parser('check-conflicts', help='Check task conflicts')
    conflict_parser.add_argument('task_id', help='Task ID to check')
    conflict_parser.add_argument('agent_id', help='Agent ID')
    
    # Agent status
    status_parser = subparsers.add_parser('agent-status', help='Get agent status')
    status_parser.add_argument('--agent-id', help='Specific agent ID')
    
    # Project status
    subparsers.add_parser('project-status', help='Get project status')
    
    # Progress report
    subparsers.add_parser('progress-report', help='Generate progress report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    project_root = Path(args.project_root).resolve()
    orchestrator = AgentOrchestrator(project_root)
    
    if args.command == 'list-tasks':
        tasks = orchestrator.get_available_tasks()
        
        if args.category:
            tasks = [t for t in tasks if t['category'] == args.category]
        
        if args.priority:
            tasks = [t for t in tasks if t['priority'] == args.priority]
        
        if not tasks:
            print("No available tasks found.")
            return
        
        print(f"📋 Available Tasks ({len(tasks)} found):\n")
        for task in tasks:
            print(f"🎯 **{task['id']}** ({task['priority']}) - {task['estimate_hours']}h")
            print(f"   {task['title']}")
            print(f"   Category: {task['category']}")
            print(f"   Files: {', '.join(task['files'][:3])}{'...' if len(task['files']) > 3 else ''}")
            if task['dependencies']:
                print(f"   Dependencies: {', '.join(task['dependencies'])}")
            print()
    
    elif args.command == 'assign-task':
        orchestrator.assign_task(args.task_id, args.agent_id)
    
    elif args.command == 'update-task':
        orchestrator.update_task_status(args.task_id, args.agent_id, args.status, args.notes)
    
    elif args.command == 'check-conflicts':
        conflicts = orchestrator.check_conflicts(args.task_id, args.agent_id)
        if conflicts:
            print("⚠️ Conflicts detected:")
            for conflict in conflicts:
                print(f"   - {conflict}")
        else:
            print("✅ No conflicts detected. Task can be assigned.")
    
    elif args.command == 'agent-status':
        status = orchestrator.get_agent_status(args.agent_id)
        
        if not status:
            print("No agents found.")
            return
        
        for agent_id, agent_data in status.items():
            print(f"👤 **{agent_id}**")
            print(f"   Assigned: {len(agent_data.get('tasks_assigned', []))} tasks")
            print(f"   Completed: {len(agent_data.get('tasks_completed', []))} tasks")
            print(f"   Total Hours: {agent_data.get('total_hours', 0)}h")
            print()
    
    elif args.command == 'project-status':
        status = orchestrator.get_project_status()
        
        print("📊 **ProjectMeats Status**")
        print(f"   Total Tasks: {status['total_tasks']}")
        print(f"   Completion: {status['completion_percentage']:.1f}%")
        print(f"   Hours: {status['completed_hours']}/{status['total_estimated_hours']}")
        print(f"   Active Agents: {status['active_agents']}")
        print()
        print("📈 **Breakdown**:")
        for status_name, count in status['status_breakdown'].items():
            print(f"   {status_name.title()}: {count}")
    
    elif args.command == 'progress-report':
        report = orchestrator.generate_progress_report()
        print(report)

if __name__ == '__main__':
    main()