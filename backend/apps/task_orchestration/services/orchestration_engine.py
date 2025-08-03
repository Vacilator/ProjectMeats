"""
Task Orchestration Engine for ProjectMeats AI System.

This module provides the core orchestration engine that autonomously
manages task creation, agent assignment, execution monitoring, and
failure handling with complete end-to-end automation.
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from ..models import (
    Task, Agent, TaskAssignment, TaskExecutionLog, OrchestrationRule,
    TaskStatus, TaskPriority, TaskType, AgentStatus, AgentType, SystemHealth
)
from apps.bug_reports.github_service import GitHubIssueService
from apps.bug_reports.models import BugReport


logger = logging.getLogger(__name__)


@dataclass
class TaskCreationRequest:
    """Request for creating a new task."""
    title: str
    description: str
    task_type: str
    priority: str = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    input_data: Dict = None
    auto_assign: bool = True
    estimated_duration: timedelta = timedelta(hours=1)
    depends_on_task_ids: List[str] = None
    github_issue_data: Dict = None


@dataclass
class AgentSelectionResult:
    """Result of agent selection algorithm."""
    agent: Optional[Agent]
    score: float
    reason: str
    alternative_agents: List[Tuple[Agent, float]]


class OrchestrationEngine:
    """
    Main orchestration engine for autonomous task management.
    
    Provides complete end-to-end task lifecycle management including:
    - Autonomous task creation from various triggers
    - Intelligent agent selection and assignment
    - Real-time execution monitoring
    - Automatic failure handling and recovery
    - GitHub integration for issue management
    - Production deployment error handling
    """
    
    def __init__(self):
        self.logger = logger
        self.github_service = None
        try:
            self.github_service = GitHubIssueService()
        except Exception as e:
            self.logger.warning(f"GitHub service unavailable: {e}")
    
    def create_task_from_production_failure(
        self,
        deployment_id: str,
        error_details: Dict[str, Any],
        server_info: Dict[str, Any]
    ) -> Task:
        """
        Automatically create a high-priority task from production deployment failure.
        
        This is called when production deployment fails and needs immediate attention.
        Creates both a task for the orchestration system and a GitHub issue.
        """
        self.logger.critical(f"Creating emergency task for production failure: {deployment_id}")
        
        # Get or create system user for automated tasks
        from django.contrib.auth.models import User
        try:
            system_user = User.objects.get(username='orchestration_system')
        except User.DoesNotExist:
            self.logger.error("System user 'orchestration_system' does not exist. Please create it using the dedicated management command or service.")
            raise
        
        # Determine priority based on error severity
        priority = TaskPriority.CRITICAL
        if "database" in str(error_details).lower() or "critical" in str(error_details).lower():
            priority = TaskPriority.EMERGENCY
        
        # Create task description with all relevant context
        description = f"""
PRODUCTION DEPLOYMENT FAILURE - IMMEDIATE ACTION REQUIRED

Deployment ID: {deployment_id}
Timestamp: {timezone.now().isoformat()}
Server: {server_info.get('hostname', 'Unknown')}
Domain: {server_info.get('domain', 'Unknown')}

Error Details:
{error_details.get('error_message', 'No error message provided')}

Failed Step: {error_details.get('failed_step', 'Unknown')}

Server Configuration:
{server_info}

This task was automatically created by the AI Orchestration Engine in response to a production deployment failure.
Immediate investigation and resolution required to restore service.
"""
        
        # Prepare input data for the task
        input_data = {
            "deployment_id": deployment_id,
            "error_details": error_details,
            "server_info": server_info,
            "failure_timestamp": timezone.now().isoformat(),
            "auto_created": True,
            "source": "production_deployment_failure"
        }
        
        # Create the task
        task_request = TaskCreationRequest(
            title=f"🚨 PRODUCTION FAILURE: {deployment_id}",
            description=description,
            task_type=TaskType.DEPLOYMENT,
            priority=priority,
            due_date=timezone.now() + timedelta(hours=1),  # 1 hour deadline
            input_data=input_data,
            auto_assign=True,
            estimated_duration=timedelta(hours=2)
        )
        
        # Create task with system user
        with transaction.atomic():
            task = Task.objects.create(
                title=task_request.title,
                description=task_request.description,
                task_type=task_request.task_type,
                priority=task_request.priority,
                due_date=task_request.due_date,
                estimated_duration=task_request.estimated_duration,
                input_data=task_request.input_data,
                auto_assign=task_request.auto_assign,
                owner=system_user,
                created_by=system_user,
                modified_by=system_user,
            )
        
        # Create GitHub issue asynchronously
        if self.github_service:
            try:
                self._create_github_issue_for_task(task, error_details)
            except Exception as e:
                self.logger.error(f"Failed to create GitHub issue for task {task.id}: {e}")
        
        # Auto-assign if possible
        if task.auto_assign and task.can_be_assigned:
            try:
                self.assign_task_to_best_agent(task)
            except Exception as e:
                self.logger.error(f"Failed to auto-assign task {task.id}: {e}")
        
        self.logger.info(f"Created emergency task {task.id} for production failure {deployment_id}")
        return task
    
    def create_task_from_bug_report(self, bug_report: BugReport) -> Task:
        """
        Create a task from a user-submitted bug report.
        
        Automatically prioritizes and assigns based on bug severity and type.
        """
        self.logger.info(f"Creating task from bug report {bug_report.id}")
        
        # Map bug priority to task priority
        priority_mapping = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "critical": TaskPriority.CRITICAL,
        }
        
        task_priority = priority_mapping.get(bug_report.priority, TaskPriority.MEDIUM)
        
        # Determine task type based on bug context
        task_type = TaskType.BUG_FIX
        if bug_report.current_url and "api" in bug_report.current_url:
            task_type = TaskType.BUG_FIX
        elif bug_report.browser_info:
            task_type = TaskType.BUG_FIX
        
        description = f"""
BUG REPORT TASK

Original Report: {bug_report.title}
Reporter: {bug_report.reporter.get_full_name() or bug_report.reporter.username}
Email: {bug_report.reporter_email}
Priority: {bug_report.get_priority_display()}

Description:
{bug_report.description}

Steps to Reproduce:
{bug_report.steps_to_reproduce}

Expected Behavior:
{bug_report.expected_behavior}

Actual Behavior:
{bug_report.actual_behavior}

Technical Context:
- URL: {bug_report.current_url}
- Page: {bug_report.page_title}
- Browser Info: {bug_report.browser_info}
- User Agent: {bug_report.user_agent}

Bug Report ID: {bug_report.id}
GitHub Issue: {bug_report.github_issue_url or 'Not created yet'}
"""
        
        input_data = {
            "bug_report_id": bug_report.id,
            "github_issue_number": bug_report.github_issue_number,
            "github_issue_url": bug_report.github_issue_url,
            "reporter_info": {
                "username": bug_report.reporter.username,
                "email": bug_report.reporter_email,
            },
            "context": {
                "url": bug_report.current_url,
                "page_title": bug_report.page_title,
                "browser_info": bug_report.browser_info,
                "user_agent": bug_report.user_agent,
                "application_state": bug_report.application_state,
            },
            "auto_created": True,
            "source": "bug_report"
        }
        
        task_request = TaskCreationRequest(
            title=f"🐛 Bug Fix: {bug_report.title}",
            description=description,
            task_type=task_type,
            priority=task_priority,
            input_data=input_data,
            auto_assign=True,
            estimated_duration=timedelta(hours=4)
        )
        
        task = self.create_task(task_request, owner=bug_report.reporter)
        
        # Link the GitHub issue if it exists
        if bug_report.github_issue_number:
            task.github_issue_number = bug_report.github_issue_number
            task.github_issue_url = bug_report.github_issue_url
            task.save()
        
        self.logger.info(f"Created task {task.id} from bug report {bug_report.id}")
        return task
    
    def create_task(self, request: TaskCreationRequest, owner: User = None) -> Task:
        """
        Create a new task and optionally auto-assign it to an agent.
        
        Handles task creation with all validation, dependency checking,
        and automatic assignment if requested.
        """
        # Get system user if no owner provided
        if not owner:
            from django.contrib.auth.models import User
            owner, created = User.objects.get_or_create(
                username='orchestration_system',
                defaults={
                    'email': 'orchestration@projectmeats.com',
                    'first_name': 'Orchestration',
                    'last_name': 'System',
                    'is_staff': False,
                    'is_active': True
                }
            )
        
        with transaction.atomic():
            # Create the task
            task = Task.objects.create(
                title=request.title,
                description=request.description,
                task_type=request.task_type,
                priority=request.priority,
                due_date=request.due_date,
                estimated_duration=request.estimated_duration,
                input_data=request.input_data or {},
                auto_assign=request.auto_assign,
                github_issue_number=request.github_issue_data.get('issue_number') if request.github_issue_data else None,
                github_issue_url=request.github_issue_data.get('issue_url') if request.github_issue_data else None,
                owner=owner,
                created_by=owner,
                modified_by=owner,
            )
            
            # Set up dependencies
            if request.depends_on_task_ids:
                dependent_tasks = Task.objects.filter(id__in=request.depends_on_task_ids)
                task.depends_on.set(dependent_tasks)
            
            self.logger.info(f"Created task {task.id}: {task.title}")
            
            # Auto-assign if requested and possible
            if request.auto_assign and task.can_be_assigned:
                try:
                    self.assign_task_to_best_agent(task)
                except Exception as e:
                    self.logger.error(f"Failed to auto-assign task {task.id}: {e}")
            
            return task
    
    def assign_task_to_best_agent(self, task: Task) -> Optional[TaskAssignment]:
        """
        Assign a task to the best available agent using intelligent selection.
        
        Uses a sophisticated algorithm considering agent capabilities,
        current load, success rate, and task requirements.
        """
        if not task.can_be_assigned:
            self.logger.warning(f"Task {task.id} cannot be assigned (status: {task.status}, dependencies: {task.has_unmet_dependencies})")
            return None
        
        # Find the best agent for this task
        selection_result = self.select_best_agent_for_task(task)
        
        if not selection_result.agent:
            self.logger.warning(f"No suitable agent found for task {task.id}: {selection_result.reason}")
            return None
        
        # Create the assignment
        with transaction.atomic():
            assignment = TaskAssignment.objects.create(
                task=task,
                agent=selection_result.agent,
                assignment_reason=selection_result.reason
            )
            
            # Update task status
            task.assigned_agent = selection_result.agent
            task.status = TaskStatus.ASSIGNED
            task.save()
            
            # Update agent status if at capacity
            if selection_result.agent.current_task_count >= selection_result.agent.max_concurrent_tasks:
                selection_result.agent.status = AgentStatus.BUSY
                selection_result.agent.save()
            
            self.logger.info(f"Assigned task {task.id} to agent {selection_result.agent.name} (score: {selection_result.score:.2f})")
            
            # Log the assignment
            self.log_task_execution(
                task, selection_result.agent, "INFO",
                f"Task assigned to {selection_result.agent.name}. Reason: {selection_result.reason}",
                step_name="assignment",
                step_data={"selection_score": selection_result.score}
            )
            
            return assignment
    
    def select_best_agent_for_task(self, task: Task) -> AgentSelectionResult:
        """
        Intelligent agent selection algorithm.
        
        Considers multiple factors:
        - Agent capabilities and task type compatibility
        - Current workload and availability
        - Historical success rate and performance
        - Agent priority weights
        """
        available_agents = Agent.objects.filter(
            is_active=True,
            status__in=[AgentStatus.AVAILABLE, AgentStatus.BUSY]
        )
        
        if not available_agents.exists():
            return AgentSelectionResult(
                agent=None, 
                score=0.0, 
                reason="No active agents available",
                alternative_agents=[]
            )
        
        # Score each agent
        agent_scores = []
        for agent in available_agents:
            score = self._calculate_agent_score(agent, task)
            if score > 0:  # Only consider agents that can handle the task
                agent_scores.append((agent, score))
        
        if not agent_scores:
            return AgentSelectionResult(
                agent=None,
                score=0.0,
                reason="No agents have compatible capabilities for this task type",
                alternative_agents=[]
            )
        
        # Sort by score (highest first)
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Check if best agent is actually available for assignment
        best_agent, best_score = agent_scores[0]
        if not best_agent.is_available_for_assignment:
            # Look for next best available agent
            for agent, score in agent_scores[1:]:
                if agent.is_available_for_assignment:
                    return AgentSelectionResult(
                        agent=agent,
                        score=score,
                        reason=f"Selected based on availability and capability match (score: {score:.2f})",
                        alternative_agents=agent_scores
                    )
            
            return AgentSelectionResult(
                agent=None,
                score=0.0,
                reason="No agents currently available for assignment (all at capacity)",
                alternative_agents=agent_scores
            )
        
        reason = f"Best match based on capability ({task.task_type}), efficiency ({best_agent.efficiency_score:.2f}), and availability"
        
        return AgentSelectionResult(
            agent=best_agent,
            score=best_score,
            reason=reason,
            alternative_agents=agent_scores[1:5]  # Top 5 alternatives
        )
    
    def _calculate_agent_score(self, agent: Agent, task: Task) -> float:
        """
        Calculate a score for how well an agent matches a task.
        
        Returns 0 if agent cannot handle the task, otherwise returns a score
        based on capability match, performance, and current load.
        """
        # Check if agent can handle this task type
        if task.task_type not in agent.capabilities and agent.agent_type != AgentType.GENERAL_AGENT:
            # Check if agent type is compatible
            type_compatibility = {
                TaskType.DEPLOYMENT: [AgentType.DEPLOYMENT_AGENT, AgentType.GENERAL_AGENT],
                TaskType.BUG_FIX: [AgentType.CODE_AGENT, AgentType.GENERAL_AGENT],
                TaskType.GITHUB_ISSUE: [AgentType.GITHUB_AGENT, AgentType.GENERAL_AGENT],
                TaskType.TESTING: [AgentType.TESTING_AGENT, AgentType.GENERAL_AGENT],
                TaskType.SYSTEM_MONITORING: [AgentType.MONITORING_AGENT, AgentType.GENERAL_AGENT],
            }
            
            compatible_types = type_compatibility.get(task.task_type, [AgentType.GENERAL_AGENT])
            if agent.agent_type not in compatible_types:
                return 0.0
        
        # Base score from agent efficiency
        score = agent.efficiency_score
        
        # Capability bonus (higher if task type is in agent's explicit capabilities)
        if task.task_type in agent.capabilities:
            score *= 1.5
        
        # Priority match bonus
        if task.priority == TaskPriority.EMERGENCY and agent.priority_weight >= 5.0:
            score *= 2.0
        elif task.priority == TaskPriority.CRITICAL and agent.priority_weight >= 3.0:
            score *= 1.5
        
        # Load penalty
        load_factor = agent.current_task_count / agent.max_concurrent_tasks
        score *= (1.0 - load_factor * 0.5)  # Reduce score based on current load
        
        # Availability bonus
        if agent.status == AgentStatus.AVAILABLE:
            score *= 1.2
        
        return max(0.0, score)
    
    def process_pending_tasks(self) -> int:
        """
        Process all pending tasks that can be assigned.
        
        This is called periodically by the orchestration system to
        assign pending tasks to available agents.
        """
        pending_tasks = Task.objects.filter(
            status=TaskStatus.PENDING,
            auto_assign=True
        ).order_by('-priority', 'created_on')
        
        assigned_count = 0
        for task in pending_tasks:
            if task.can_be_assigned:
                try:
                    assignment = self.assign_task_to_best_agent(task)
                    if assignment:
                        assigned_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to assign pending task {task.id}: {e}")
        
        if assigned_count > 0:
            self.logger.info(f"Assigned {assigned_count} pending tasks to agents")
        
        return assigned_count
    
    def handle_task_failure(self, task: Task, error_message: str) -> bool:
        """
        Handle task failure with automatic retry and escalation logic.
        
        Implements intelligent failure handling including:
        - Automatic retry with backoff
        - Task reassignment to different agents
        - Priority escalation
        - GitHub issue creation for critical failures
        """
        self.logger.warning(f"Handling failure for task {task.id}: {error_message}")
        
        with transaction.atomic():
            # Update task with failure information
            task.status = TaskStatus.FAILED
            task.error_details = error_message
            task.save()
            
            # Log the failure
            if task.assigned_agent:
                self.log_task_execution(
                    task, task.assigned_agent, "ERROR",
                    f"Task failed: {error_message}",
                    step_name="failure",
                    step_data={"retry_count": task.retry_count}
                )
                
                # Update agent statistics
                duration = task.duration_so_far if task.started_at else None
                task.assigned_agent.update_statistics(False, duration)
            
            # Check if task can be retried
            if task.can_retry():
                return self._retry_task(task)
            
            # Check if task should be escalated
            if task.should_escalate():
                return self._escalate_task(task, error_message)
            
            # Create GitHub issue for critical failures that can't be retried
            if task.priority in [TaskPriority.CRITICAL, TaskPriority.EMERGENCY]:
                self._create_github_issue_for_failed_task(task, error_message)
            
            return False
    
    def _retry_task(self, task: Task) -> bool:
        """Retry a failed task with improved assignment."""
        self.logger.info(f"Retrying task {task.id} (attempt {task.retry_count + 1})")
        
        with transaction.atomic():
            task.retry_count += 1
            task.status = TaskStatus.PENDING
            task.assigned_agent = None
            task.error_details = None
            task.save()
            
            # Try to assign to a different agent if possible
            try:
                assignment = self.assign_task_to_best_agent(task)
                return assignment is not None
            except Exception as e:
                self.logger.error(f"Failed to reassign retried task {task.id}: {e}")
                return False
    
    def _escalate_task(self, task: Task, error_message: str) -> bool:
        """Escalate a task that has failed multiple times or is overdue."""
        self.logger.warning(f"Escalating task {task.id}")
        
        with transaction.atomic():
            task.escalation_level += 1
            task.status = TaskStatus.ESCALATED
            
            # Increase priority if not already at maximum
            if task.priority == TaskPriority.LOW:
                task.priority = TaskPriority.MEDIUM
            elif task.priority == TaskPriority.MEDIUM:
                task.priority = TaskPriority.HIGH
            elif task.priority == TaskPriority.HIGH:
                task.priority = TaskPriority.CRITICAL
            
            task.save()
            
            # Create GitHub issue for escalated tasks
            self._create_github_issue_for_escalated_task(task, error_message)
            
            # Try to reassign with higher priority
            try:
                task.status = TaskStatus.PENDING
                task.assigned_agent = None
                task.save()
                assignment = self.assign_task_to_best_agent(task)
                return assignment is not None
            except Exception as e:
                self.logger.error(f"Failed to reassign escalated task {task.id}: {e}")
                return False
    
    def _create_github_issue_for_task(self, task: Task, error_details: Dict = None):
        """Create a GitHub issue for a task."""
        if not self.github_service:
            return
        
        try:
            # Create a bug report to use the existing GitHub integration
            issue_title = f"Task Failure: {task.title}"
            issue_body = f"""
# Automated Task Failure Report

**Task ID**: {task.id}
**Task Type**: {task.get_task_type_display()}
**Priority**: {task.get_priority_display()}
**Status**: {task.get_status_display()}
**Created**: {task.created_on}

## Task Description
{task.description}

## Error Details
{task.error_details or 'No error details available'}

## Input Data
```json
{task.input_data}
```

## Additional Context
- Assigned Agent: {task.assigned_agent.name if task.assigned_agent else 'None'}
- Retry Count: {task.retry_count}
- Escalation Level: {task.escalation_level}
- Due Date: {task.due_date or 'No deadline'}

---
*This issue was automatically created by the ProjectMeats AI Orchestration Engine*
"""
            
            # Create a minimal bug report for GitHub integration
            from apps.bug_reports.models import BugReport, BugReportPriority
            from django.contrib.auth.models import User
            
            # Use the system user for automated reports
            system_user, created = User.objects.get_or_create(
                username='orchestration_engine',
                defaults={
                    'email': 'orchestration@projectmeats.com',
                    'first_name': 'Orchestration',
                    'last_name': 'Engine'
                }
            )
            
            priority_mapping = {
                TaskPriority.LOW: BugReportPriority.LOW,
                TaskPriority.MEDIUM: BugReportPriority.MEDIUM,
                TaskPriority.HIGH: BugReportPriority.HIGH,
                TaskPriority.CRITICAL: BugReportPriority.CRITICAL,
                TaskPriority.EMERGENCY: BugReportPriority.CRITICAL,
            }
            
            bug_report = BugReport.objects.create(
                reporter=system_user,
                reporter_email='orchestration@projectmeats.com',
                title=issue_title,
                description=issue_body,
                priority=priority_mapping.get(task.priority, BugReportPriority.MEDIUM),
                application_state={
                    'task_id': str(task.id),
                    'task_type': task.task_type,
                    'orchestration_engine': True
                }
            )
            
            # Use the existing GitHub service to create the issue
            result = self.github_service.create_bug_issue(bug_report)
            
            if result.get('success'):
                task.github_issue_number = result['issue_number']
                task.github_issue_url = result['issue_url']
                task.save()
                
                self.logger.info(f"Created GitHub issue #{result['issue_number']} for task {task.id}")
            else:
                self.logger.error(f"Failed to create GitHub issue for task {task.id}: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Error creating GitHub issue for task {task.id}: {e}")
    
    def _create_github_issue_for_failed_task(self, task: Task, error_message: str):
        """Create GitHub issue specifically for failed tasks."""
        self._create_github_issue_for_task(task)
    
    def _create_github_issue_for_escalated_task(self, task: Task, error_message: str):
        """Create GitHub issue specifically for escalated tasks."""
        self._create_github_issue_for_task(task)
    
    def log_task_execution(
        self,
        task: Task,
        agent: Agent,
        level: str,
        message: str,
        step_name: str = None,
        step_data: Dict = None,
        execution_time: float = None
    ):
        """Log task execution details for monitoring and debugging."""
        TaskExecutionLog.objects.create(
            task=task,
            agent=agent,
            log_level=level,
            message=message,
            step_name=step_name or "",
            step_data=step_data or {},
            execution_time=execution_time
        )
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the orchestration system."""
        from django.db.models import Count, Q
        
        # Task statistics
        task_stats = Task.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status=TaskStatus.PENDING)),
            assigned=Count('id', filter=Q(status=TaskStatus.ASSIGNED)),
            in_progress=Count('id', filter=Q(status=TaskStatus.IN_PROGRESS)),
            completed=Count('id', filter=Q(status=TaskStatus.COMPLETED)),
            failed=Count('id', filter=Q(status=TaskStatus.FAILED)),
            escalated=Count('id', filter=Q(status=TaskStatus.ESCALATED)),
        )
        
        # Agent statistics
        agent_stats = Agent.objects.aggregate(
            total=Count('id'),
            available=Count('id', filter=Q(status=AgentStatus.AVAILABLE, is_active=True)),
            busy=Count('id', filter=Q(status=AgentStatus.BUSY, is_active=True)),
            offline=Count('id', filter=Q(status=AgentStatus.OFFLINE)),
            error=Count('id', filter=Q(status=AgentStatus.ERROR)),
        )
        
        # Recent activity
        recent_tasks = Task.objects.filter(
            created_on__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        recent_failures = Task.objects.filter(
            status=TaskStatus.FAILED,
            modified_on__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        return {
            'timestamp': timezone.now(),
            'tasks': task_stats,
            'agents': agent_stats,
            'recent_activity': {
                'tasks_created_24h': recent_tasks,
                'failures_24h': recent_failures,
            },
            'system_health': self._get_system_health_summary()
        }
    
    def _get_system_health_summary(self) -> Dict[str, str]:
        """Get summary of system health."""
        try:
            recent_health = SystemHealth.objects.filter(
                last_check__gte=timezone.now() - timedelta(minutes=30)
            )
            
            if not recent_health.exists():
                return {'status': 'unknown', 'message': 'No recent health data'}
            
            critical_count = recent_health.filter(status='critical').count()
            warning_count = recent_health.filter(status='warning').count()
            
            if critical_count > 0:
                return {'status': 'critical', 'message': f'{critical_count} critical issues detected'}
            elif warning_count > 0:
                return {'status': 'warning', 'message': f'{warning_count} warnings detected'}
            else:
                return {'status': 'healthy', 'message': 'All systems operational'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Health check failed: {str(e)}'}


# Global orchestration engine instance
orchestration_engine = OrchestrationEngine()