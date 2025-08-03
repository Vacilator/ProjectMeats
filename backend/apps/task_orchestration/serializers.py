"""
Serializers for Task Orchestration API.

Provides comprehensive serialization for all orchestration models
with detailed field mappings and validation.
"""
from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    Agent, Task, TaskAssignment, TaskExecutionLog, 
    OrchestrationRule, SystemHealth, TaskStatus, TaskPriority
)


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for task ownership."""
    
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'display_name']
        read_only_fields = ['id', 'username', 'email']
    
    def get_display_name(self, obj):
        """Get user's display name."""
        return obj.get_full_name() or obj.username


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for AI agents."""
    
    current_task_count = serializers.ReadOnlyField()
    is_available_for_assignment = serializers.ReadOnlyField()
    efficiency_score = serializers.ReadOnlyField()
    
    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'agent_type', 'status', 'capabilities',
            'max_concurrent_tasks', 'priority_weight', 'success_rate',
            'average_completion_time', 'last_heartbeat', 'endpoint_url',
            'configuration', 'total_tasks_completed', 'total_tasks_failed',
            'is_active', 'created_on', 'modified_on', 'current_task_count',
            'is_available_for_assignment', 'efficiency_score'
        ]
        read_only_fields = [
            'id', 'created_on', 'modified_on', 'last_heartbeat',
            'total_tasks_completed', 'total_tasks_failed', 'success_rate',
            'current_task_count', 'is_available_for_assignment', 'efficiency_score'
        ]


class TaskListSerializer(serializers.ModelSerializer):
    """Serializer for task list view."""
    
    assigned_agent_name = serializers.CharField(source='assigned_agent.name', read_only=True)
    priority_score = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    duration_so_far = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'task_type', 'priority', 'status', 'assigned_agent_name',
            'due_date', 'estimated_duration', 'started_at', 'completed_at',
            'retry_count', 'escalation_level', 'created_on', 'modified_on',
            'priority_score', 'is_overdue', 'duration_so_far', 'github_issue_number'
        ]
        read_only_fields = [
            'id', 'created_on', 'modified_on', 'assigned_agent_name',
            'priority_score', 'is_overdue', 'duration_so_far'
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual tasks."""
    
    assigned_agent = AgentSerializer(read_only=True)
    owner = UserBasicSerializer(read_only=True)
    depends_on = TaskListSerializer(many=True, read_only=True)
    dependent_tasks = TaskListSerializer(many=True, read_only=True)
    
    # Computed fields
    priority_score = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    duration_so_far = serializers.ReadOnlyField()
    can_be_assigned = serializers.ReadOnlyField()
    has_unmet_dependencies = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'task_type', 'priority', 'status',
            'assigned_agent', 'owner', 'due_date', 'estimated_duration',
            'started_at', 'completed_at', 'input_data', 'output_data',
            'error_details', 'depends_on', 'dependent_tasks',
            'github_issue_number', 'github_issue_url', 'retry_count',
            'max_retries', 'escalation_level', 'auto_assign', 'auto_retry',
            'auto_escalate', 'created_on', 'modified_on',
            'priority_score', 'is_overdue', 'duration_so_far',
            'can_be_assigned', 'has_unmet_dependencies'
        ]
        read_only_fields = [
            'id', 'assigned_agent', 'owner', 'created_on', 'modified_on',
            'depends_on', 'dependent_tasks', 'priority_score', 'is_overdue',
            'duration_so_far', 'can_be_assigned', 'has_unmet_dependencies'
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new tasks."""
    
    depends_on_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="List of task IDs this task depends on"
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'task_type', 'priority', 'due_date',
            'estimated_duration', 'input_data', 'auto_assign', 'auto_retry',
            'auto_escalate', 'max_retries', 'depends_on_ids'
        ]
    
    def create(self, validated_data):
        """Create task with dependencies."""
        depends_on_ids = validated_data.pop('depends_on_ids', [])
        
        # Set owner to current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user
        
        task = Task.objects.create(**validated_data)
        
        # Set up dependencies
        if depends_on_ids:
            dependent_tasks = Task.objects.filter(id__in=depends_on_ids)
            task.depends_on.set(dependent_tasks)
        
        return task


class TaskAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for task assignments."""
    
    task = TaskListSerializer(read_only=True)
    agent = AgentSerializer(read_only=True)
    
    class Meta:
        model = TaskAssignment
        fields = [
            'id', 'task', 'agent', 'assigned_by', 'assignment_reason',
            'assigned_at', 'accepted_at', 'completed_at', 'is_active'
        ]
        read_only_fields = [
            'id', 'task', 'agent', 'assigned_at', 'accepted_at', 'completed_at'
        ]


class TaskExecutionLogSerializer(serializers.ModelSerializer):
    """Serializer for task execution logs."""
    
    task_title = serializers.CharField(source='task.title', read_only=True)
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    
    class Meta:
        model = TaskExecutionLog
        fields = [
            'id', 'task', 'agent', 'task_title', 'agent_name',
            'log_level', 'message', 'step_name', 'step_data',
            'execution_time', 'created_on'
        ]
        read_only_fields = ['id', 'task_title', 'agent_name', 'created_on']


class OrchestrationRuleSerializer(serializers.ModelSerializer):
    """Serializer for orchestration rules."""
    
    class Meta:
        model = OrchestrationRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'trigger_conditions',
            'actions', 'priority', 'is_active', 'trigger_count',
            'last_triggered', 'created_on', 'modified_on'
        ]
        read_only_fields = [
            'id', 'trigger_count', 'last_triggered', 'created_on', 'modified_on'
        ]


class SystemHealthSerializer(serializers.ModelSerializer):
    """Serializer for system health metrics."""
    
    class Meta:
        model = SystemHealth
        fields = [
            'id', 'component', 'metric_name', 'metric_value', 'status',
            'threshold_warning', 'threshold_critical', 'last_check',
            'created_on', 'modified_on'
        ]
        read_only_fields = ['id', 'last_check', 'created_on', 'modified_on']


class OrchestrationStatusSerializer(serializers.Serializer):
    """Serializer for overall orchestration system status."""
    
    timestamp = serializers.DateTimeField(read_only=True)
    tasks = serializers.DictField(read_only=True)
    agents = serializers.DictField(read_only=True)
    recent_activity = serializers.DictField(read_only=True)
    system_health = serializers.DictField(read_only=True)


class TaskActionSerializer(serializers.Serializer):
    """Serializer for task actions (assign, retry, escalate, etc.)."""
    
    action = serializers.ChoiceField(
        choices=[
            ('assign', 'Assign to Agent'),
            ('retry', 'Retry Task'),
            ('escalate', 'Escalate Task'),
            ('cancel', 'Cancel Task'),
            ('complete', 'Mark Complete'),
        ]
    )
    
    agent_id = serializers.UUIDField(
        required=False,
        help_text="Agent ID for manual assignment"
    )
    
    reason = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Reason for the action"
    )
    
    output_data = serializers.JSONField(
        required=False,
        help_text="Output data for task completion"
    )


class AgentActionSerializer(serializers.Serializer):
    """Serializer for agent actions (activate, deactivate, update status)."""
    
    action = serializers.ChoiceField(
        choices=[
            ('activate', 'Activate Agent'),
            ('deactivate', 'Deactivate Agent'),
            ('set_available', 'Set Available'),
            ('set_busy', 'Set Busy'),
            ('set_offline', 'Set Offline'),
            ('set_maintenance', 'Set Maintenance'),
        ]
    )
    
    reason = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Reason for the action"
    )


class CreateTaskFromBugReportSerializer(serializers.Serializer):
    """Serializer for creating tasks from bug reports."""
    
    bug_report_id = serializers.IntegerField(
        help_text="ID of the bug report to create task from"
    )
    
    override_priority = serializers.ChoiceField(
        choices=TaskPriority.choices,
        required=False,
        help_text="Override the default priority mapping"
    )


class CreateTaskFromDeploymentFailureSerializer(serializers.Serializer):
    """Serializer for creating tasks from deployment failures."""
    
    deployment_id = serializers.CharField(
        max_length=100,
        help_text="Deployment identifier"
    )
    
    error_message = serializers.CharField(
        help_text="Error message from deployment failure"
    )
    
    failed_step = serializers.CharField(
        required=False,
        help_text="Step where deployment failed"
    )
    
    server_hostname = serializers.CharField(
        required=False,
        help_text="Server hostname"
    )
    
    domain = serializers.CharField(
        required=False,
        help_text="Domain being deployed"
    )
    
    additional_info = serializers.JSONField(
        required=False,
        help_text="Additional deployment information"
    )