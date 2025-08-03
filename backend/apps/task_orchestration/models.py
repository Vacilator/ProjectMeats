"""
Task Orchestration models for ProjectMeats AI system.

This module provides comprehensive task management, agent delegation,
and autonomous workflow orchestration for the ProjectMeats AI system.
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import OwnedModel, StatusModel, TimestampedModel


class TaskPriority(models.TextChoices):
    """Priority levels for tasks with autonomous escalation."""
    
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"
    EMERGENCY = "emergency", "Emergency"


class TaskStatus(models.TextChoices):
    """Comprehensive task status tracking."""
    
    PENDING = "pending", "Pending Assignment"
    ASSIGNED = "assigned", "Assigned to Agent"
    IN_PROGRESS = "in_progress", "In Progress"
    BLOCKED = "blocked", "Blocked"
    REVIEW = "review", "Under Review"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    ESCALATED = "escalated", "Escalated"


class TaskType(models.TextChoices):
    """Types of tasks that can be orchestrated."""
    
    DEPLOYMENT = "deployment", "Deployment Task"
    BUG_FIX = "bug_fix", "Bug Fix"
    FEATURE_DEVELOPMENT = "feature_development", "Feature Development"
    SYSTEM_MONITORING = "system_monitoring", "System Monitoring"
    DATA_PROCESSING = "data_processing", "Data Processing"
    GITHUB_ISSUE = "github_issue", "GitHub Issue Management"
    CODE_REVIEW = "code_review", "Code Review"
    TESTING = "testing", "Testing"
    DOCUMENTATION = "documentation", "Documentation"
    MAINTENANCE = "maintenance", "System Maintenance"


class AgentType(models.TextChoices):
    """Types of AI agents available for task execution."""
    
    DEPLOYMENT_AGENT = "deployment", "Deployment Agent"
    CODE_AGENT = "code", "Code Agent"
    TESTING_AGENT = "testing", "Testing Agent"
    MONITORING_AGENT = "monitoring", "Monitoring Agent"
    GITHUB_AGENT = "github", "GitHub Agent"
    GENERAL_AGENT = "general", "General Purpose Agent"


class AgentStatus(models.TextChoices):
    """Status of AI agents."""
    
    AVAILABLE = "available", "Available"
    BUSY = "busy", "Busy"
    OFFLINE = "offline", "Offline"
    MAINTENANCE = "maintenance", "Under Maintenance"
    ERROR = "error", "Error State"


class Agent(TimestampedModel):
    """
    AI Agent model for task execution.
    
    Represents individual AI agents that can be assigned tasks
    based on their capabilities and current availability.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the agent"
    )
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name for the agent"
    )
    
    agent_type = models.CharField(
        max_length=20,
        choices=AgentType.choices,
        help_text="Type of agent and its primary capabilities"
    )
    
    status = models.CharField(
        max_length=20,
        choices=AgentStatus.choices,
        default=AgentStatus.AVAILABLE,
        help_text="Current status of the agent"
    )
    
    # Capabilities and configuration
    capabilities = models.JSONField(
        default=list,
        help_text="List of task types this agent can handle"
    )
    
    max_concurrent_tasks = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Maximum number of concurrent tasks this agent can handle"
    )
    
    priority_weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        help_text="Priority weight for agent selection (higher = more preferred)"
    )
    
    # Performance metrics
    success_rate = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Historical success rate (0.0 to 1.0)"
    )
    
    average_completion_time = models.DurationField(
        default=timedelta(hours=1),
        help_text="Average time to complete tasks"
    )
    
    # Health and monitoring
    last_heartbeat = models.DateTimeField(
        auto_now=True,
        help_text="Last time agent reported being alive"
    )
    
    endpoint_url = models.URLField(
        blank=True,
        null=True,
        help_text="API endpoint for the agent (if applicable)"
    )
    
    configuration = models.JSONField(
        default=dict,
        help_text="Agent-specific configuration parameters"
    )
    
    # Statistics
    total_tasks_completed = models.PositiveIntegerField(
        default=0,
        help_text="Total number of tasks completed by this agent"
    )
    
    total_tasks_failed = models.PositiveIntegerField(
        default=0,
        help_text="Total number of tasks failed by this agent"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this agent is active and available for assignments"
    )
    
    class Meta:
        db_table = "task_orchestration_agents"
        verbose_name = "AI Agent"
        verbose_name_plural = "AI Agents"
        ordering = ["-priority_weight", "name"]
        indexes = [
            models.Index(fields=["agent_type", "status"]),
            models.Index(fields=["status", "is_active"]),
            models.Index(fields=["priority_weight"]),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_agent_type_display()})"
    
    @property
    def current_task_count(self):
        """Get current number of assigned/in-progress tasks."""
        return self.assigned_tasks.filter(
            status__in=[TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
        ).count()
    
    @property
    def is_available_for_assignment(self):
        """Check if agent is available for new task assignment."""
        return (
            self.is_active
            and self.status == AgentStatus.AVAILABLE
            and self.current_task_count < self.max_concurrent_tasks
        )
    
    @property
    def efficiency_score(self):
        """Calculate agent efficiency score for selection algorithm."""
        total_tasks = self.total_tasks_completed + self.total_tasks_failed
        if total_tasks == 0:
            return self.priority_weight
        
        success_factor = self.success_rate
        load_factor = 1.0 - (self.current_task_count / self.max_concurrent_tasks)
        
        return self.priority_weight * success_factor * load_factor
    
    def update_statistics(self, task_completed: bool, completion_time: Optional[timedelta] = None):
        """Update agent statistics after task completion."""
        if task_completed:
            self.total_tasks_completed += 1
        else:
            self.total_tasks_failed += 1
        
        # Update success rate
        total_tasks = self.total_tasks_completed + self.total_tasks_failed
        if total_tasks > 0:
            self.success_rate = self.total_tasks_completed / total_tasks
        
        # Update average completion time
        if completion_time and task_completed:
            if self.total_tasks_completed == 1:
                self.average_completion_time = completion_time
            else:
                # Weighted average
                weight = 0.9  # Give more weight to recent performance
                self.average_completion_time = (
                    weight * completion_time + 
                    (1 - weight) * self.average_completion_time
                )
        
        self.save()


class Task(OwnedModel, StatusModel):
    """
    Comprehensive task model for AI orchestration.
    
    Represents individual tasks that can be created, assigned to agents,
    and tracked through their lifecycle with autonomous management.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the task"
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Brief descriptive title for the task"
    )
    
    description = models.TextField(
        help_text="Detailed description of the task"
    )
    
    task_type = models.CharField(
        max_length=30,
        choices=TaskType.choices,
        help_text="Type/category of the task"
    )
    
    priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
        help_text="Priority level of the task"
    )
    
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
        help_text="Current status of the task"
    )
    
    # Assignment and execution
    assigned_agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        help_text="Agent assigned to execute this task"
    )
    
    # Timing and deadlines
    due_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Deadline for task completion"
    )
    
    estimated_duration = models.DurationField(
        default=timedelta(hours=1),
        help_text="Estimated time to complete the task"
    )
    
    started_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the task execution started"
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the task was completed"
    )
    
    # Task data and configuration
    input_data = models.JSONField(
        default=dict,
        help_text="Input data and parameters for task execution"
    )
    
    output_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Output data and results from task execution"
    )
    
    error_details = models.TextField(
        blank=True,
        null=True,
        help_text="Error details if task failed"
    )
    
    # Dependencies and relationships
    depends_on = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="dependent_tasks",
        help_text="Tasks that must be completed before this task can start"
    )
    
    # GitHub integration
    github_issue_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Associated GitHub issue number"
    )
    
    github_issue_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL of the associated GitHub issue"
    )
    
    # Retry and escalation
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this task has been retried"
    )
    
    max_retries = models.PositiveIntegerField(
        default=3,
        help_text="Maximum number of retry attempts"
    )
    
    escalation_level = models.PositiveIntegerField(
        default=0,
        help_text="Current escalation level (0 = no escalation)"
    )
    
    # Autonomous management
    auto_assign = models.BooleanField(
        default=True,
        help_text="Whether this task should be automatically assigned to agents"
    )
    
    auto_retry = models.BooleanField(
        default=True,
        help_text="Whether this task should be automatically retried on failure"
    )
    
    auto_escalate = models.BooleanField(
        default=True,
        help_text="Whether this task should be automatically escalated"
    )
    
    class Meta:
        db_table = "task_orchestration_tasks"
        verbose_name = "Orchestrated Task"
        verbose_name_plural = "Orchestrated Tasks"
        ordering = ["-priority", "-created_on"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["task_type", "status"]),
            models.Index(fields=["assigned_agent", "status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["auto_assign", "status"]),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()}) - {self.get_status_display()}"
    
    @property
    def is_overdue(self):
        """Check if task is past its due date."""
        return self.due_date and timezone.now() > self.due_date
    
    @property
    def duration_so_far(self):
        """Calculate how long the task has been running."""
        if self.started_at:
            end_time = self.completed_at or timezone.now()
            return end_time - self.started_at
        return timedelta(0)
    
    @property
    def can_be_assigned(self):
        """Check if task can be assigned to an agent."""
        return (
            self.status == TaskStatus.PENDING
            and self.assigned_agent is None
            and not self.has_unmet_dependencies
        )
    
    @property
    def has_unmet_dependencies(self):
        """Check if task has unmet dependencies."""
        return self.depends_on.exclude(status=TaskStatus.COMPLETED).exists()
    
    @property
    def priority_score(self):
        """Calculate numeric priority score for ordering."""
        priority_values = {
            TaskPriority.LOW: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.HIGH: 3,
            TaskPriority.CRITICAL: 4,
            TaskPriority.EMERGENCY: 5,
        }
        base_score = priority_values.get(self.priority, 2)
        
        # Add urgency factor based on due date
        if self.due_date:
            time_to_deadline = self.due_date - timezone.now()
            if time_to_deadline.total_seconds() < 0:  # Overdue
                base_score += 2
            elif time_to_deadline.total_seconds() < 3600:  # Less than 1 hour
                base_score += 1
        
        # Add escalation factor
        base_score += self.escalation_level * 0.5
        
        return base_score
    
    def can_retry(self):
        """Check if task can be retried."""
        return (
            self.status == TaskStatus.FAILED
            and self.auto_retry
            and self.retry_count < self.max_retries
        )
    
    def should_escalate(self):
        """Check if task should be escalated."""
        if not self.auto_escalate:
            return False
        
        # Escalate if overdue and not completed
        if self.is_overdue and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return True
        
        # Escalate if failed multiple times
        if self.retry_count >= self.max_retries:
            return True
        
        # Escalate if blocked for too long
        if self.status == TaskStatus.BLOCKED:
            blocked_duration = timezone.now() - self.modified_on
            if blocked_duration > timedelta(hours=2):
                return True
        
        return False


class TaskAssignment(TimestampedModel):
    """
    Task assignment tracking model.
    
    Tracks the assignment of tasks to agents with detailed history
    and performance metrics for optimization.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="assignments",
        help_text="Task being assigned"
    )
    
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="task_assignments",
        help_text="Agent receiving the assignment"
    )
    
    assigned_by = models.CharField(
        max_length=100,
        default="orchestration_engine",
        help_text="Who/what assigned this task"
    )
    
    assignment_reason = models.TextField(
        help_text="Reason for this specific assignment"
    )
    
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the assignment was made"
    )
    
    accepted_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the agent accepted the assignment"
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the assignment was completed"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this assignment is currently active"
    )
    
    class Meta:
        db_table = "task_orchestration_assignments"
        verbose_name = "Task Assignment"
        verbose_name_plural = "Task Assignments"
        ordering = ["-assigned_at"]
        indexes = [
            models.Index(fields=["task", "is_active"]),
            models.Index(fields=["agent", "is_active"]),
            models.Index(fields=["assigned_at"]),
        ]
    
    def __str__(self):
        return f"{self.task.title} → {self.agent.name}"


class TaskExecutionLog(TimestampedModel):
    """
    Detailed execution log for task progress tracking.
    
    Provides comprehensive logging of task execution steps
    for debugging, monitoring, and optimization.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="execution_logs",
        help_text="Task being executed"
    )
    
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="execution_logs",
        help_text="Agent executing the task"
    )
    
    log_level = models.CharField(
        max_length=20,
        choices=[
            ("DEBUG", "Debug"),
            ("INFO", "Info"),
            ("WARNING", "Warning"),
            ("ERROR", "Error"),
            ("CRITICAL", "Critical"),
        ],
        default="INFO",
        help_text="Log level"
    )
    
    message = models.TextField(
        help_text="Log message"
    )
    
    step_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of the execution step"
    )
    
    step_data = models.JSONField(
        default=dict,
        help_text="Data associated with this execution step"
    )
    
    execution_time = models.FloatField(
        blank=True,
        null=True,
        help_text="Time taken for this step (in seconds)"
    )
    
    class Meta:
        db_table = "task_orchestration_execution_logs"
        verbose_name = "Task Execution Log"
        verbose_name_plural = "Task Execution Logs"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["task", "-created_on"]),
            models.Index(fields=["agent", "-created_on"]),
            models.Index(fields=["log_level"]),
        ]
    
    def __str__(self):
        return f"[{self.log_level}] {self.task.title}: {self.message[:50]}"


class OrchestrationRule(TimestampedModel):
    """
    Rules for autonomous task orchestration.
    
    Defines rules and conditions for automatic task creation,
    assignment, escalation, and other orchestration decisions.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name for the orchestration rule"
    )
    
    description = models.TextField(
        help_text="Description of what this rule does"
    )
    
    rule_type = models.CharField(
        max_length=30,
        choices=[
            ("task_creation", "Task Creation"),
            ("task_assignment", "Task Assignment"),
            ("task_escalation", "Task Escalation"),
            ("agent_selection", "Agent Selection"),
            ("failure_handling", "Failure Handling"),
            ("monitoring", "Monitoring"),
        ],
        help_text="Type of orchestration rule"
    )
    
    # Conditions
    trigger_conditions = models.JSONField(
        help_text="Conditions that trigger this rule"
    )
    
    # Actions
    actions = models.JSONField(
        help_text="Actions to take when rule is triggered"
    )
    
    # Rule configuration
    priority = models.PositiveIntegerField(
        default=100,
        help_text="Rule priority (lower number = higher priority)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this rule is active"
    )
    
    # Statistics
    trigger_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this rule has been triggered"
    )
    
    last_triggered = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When this rule was last triggered"
    )
    
    class Meta:
        db_table = "task_orchestration_rules"
        verbose_name = "Orchestration Rule"
        verbose_name_plural = "Orchestration Rules"
        ordering = ["priority", "name"]
        indexes = [
            models.Index(fields=["rule_type", "is_active"]),
            models.Index(fields=["priority"]),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


class SystemHealth(TimestampedModel):
    """
    System health monitoring for autonomous decision making.
    
    Tracks overall system health metrics to inform orchestration
    decisions and trigger appropriate responses.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    component = models.CharField(
        max_length=50,
        help_text="System component being monitored"
    )
    
    metric_name = models.CharField(
        max_length=100,
        help_text="Name of the health metric"
    )
    
    metric_value = models.JSONField(
        help_text="Current value of the metric"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ("healthy", "Healthy"),
            ("warning", "Warning"),
            ("critical", "Critical"),
            ("unknown", "Unknown"),
        ],
        help_text="Health status"
    )
    
    threshold_warning = models.JSONField(
        blank=True,
        null=True,
        help_text="Warning threshold for this metric"
    )
    
    threshold_critical = models.JSONField(
        blank=True,
        null=True,
        help_text="Critical threshold for this metric"
    )
    
    last_check = models.DateTimeField(
        auto_now=True,
        help_text="When this metric was last checked"
    )
    
    class Meta:
        db_table = "task_orchestration_system_health"
        verbose_name = "System Health Metric"
        verbose_name_plural = "System Health Metrics"
        ordering = ["-last_check"]
        unique_together = ["component", "metric_name"]
        indexes = [
            models.Index(fields=["component", "status"]),
            models.Index(fields=["status", "-last_check"]),
        ]
    
    def __str__(self):
        return f"{self.component}.{self.metric_name}: {self.status}"
