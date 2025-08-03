"""
Admin interface for Task Orchestration models.

Provides comprehensive admin interface for managing tasks, agents,
and orchestration system components.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Agent, Task, TaskAssignment, TaskExecutionLog, 
    OrchestrationRule, SystemHealth
)


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    """Admin interface for AI agents."""
    
    list_display = [
        'name', 'agent_type', 'status_badge', 'efficiency_display', 
        'current_tasks', 'success_rate_display', 'is_active', 'last_heartbeat'
    ]
    list_filter = ['agent_type', 'status', 'is_active', 'created_on']
    search_fields = ['name', 'capabilities']
    readonly_fields = [
        'id', 'created_on', 'modified_on', 'last_heartbeat', 'success_rate',
        'total_tasks_completed', 'total_tasks_failed', 'current_task_count',
        'efficiency_score'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'agent_type', 'status', 'is_active')
        }),
        ('Capabilities', {
            'fields': ('capabilities', 'max_concurrent_tasks', 'priority_weight')
        }),
        ('Performance Metrics', {
            'fields': ('success_rate', 'average_completion_time', 'efficiency_score',
                     'total_tasks_completed', 'total_tasks_failed')
        }),
        ('Configuration', {
            'fields': ('endpoint_url', 'configuration')
        }),
        ('Monitoring', {
            'fields': ('last_heartbeat', 'current_task_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_on', 'modified_on'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        colors = {
            'available': 'green',
            'busy': 'orange',
            'offline': 'red',
            'maintenance': 'blue',
            'error': 'darkred'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def efficiency_display(self, obj):
        return f"{obj.efficiency_score:.2f}"
    efficiency_display.short_description = 'Efficiency'
    
    def current_tasks(self, obj):
        return f"{obj.current_task_count}/{obj.max_concurrent_tasks}"
    current_tasks.short_description = 'Tasks'
    
    def success_rate_display(self, obj):
        return f"{obj.success_rate:.1%}"
    success_rate_display.short_description = 'Success Rate'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for orchestrated tasks."""
    
    list_display = [
        'title', 'task_type', 'priority_badge', 'status_badge', 
        'assigned_agent', 'owner', 'created_on', 'due_date_display'
    ]
    list_filter = [
        'task_type', 'priority', 'status', 'auto_assign', 'escalation_level',
        'created_on', 'assigned_agent__agent_type'
    ]
    search_fields = ['title', 'description', 'error_details']
    readonly_fields = [
        'id', 'created_on', 'modified_on', 'priority_score', 'is_overdue',
        'duration_so_far', 'can_be_assigned', 'has_unmet_dependencies'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'task_type', 'priority', 'status')
        }),
        ('Assignment', {
            'fields': ('assigned_agent', 'owner', 'auto_assign')
        }),
        ('Timing', {
            'fields': ('due_date', 'estimated_duration', 'started_at', 'completed_at')
        }),
        ('Data', {
            'fields': ('input_data', 'output_data', 'error_details'),
            'classes': ('collapse',)
        }),
        ('Dependencies', {
            'fields': ('depends_on',),
            'classes': ('collapse',)
        }),
        ('GitHub Integration', {
            'fields': ('github_issue_number', 'github_issue_url'),
            'classes': ('collapse',)
        }),
        ('Retry & Escalation', {
            'fields': ('retry_count', 'max_retries', 'escalation_level', 
                     'auto_retry', 'auto_escalate')
        }),
        ('Computed Fields', {
            'fields': ('priority_score', 'is_overdue', 'duration_so_far',
                     'can_be_assigned', 'has_unmet_dependencies'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_on', 'modified_on'),
            'classes': ('collapse',)
        })
    )
    
    def priority_badge(self, obj):
        colors = {
            'low': 'green',
            'medium': 'orange', 
            'high': 'red',
            'critical': 'darkred',
            'emergency': 'purple'
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_priority_display().upper()
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'assigned': 'blue',
            'in_progress': 'purple',
            'blocked': 'red',
            'review': 'yellow',
            'completed': 'green',
            'failed': 'darkred',
            'cancelled': 'gray',
            'escalated': 'maroon'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def due_date_display(self, obj):
        if not obj.due_date:
            return '-'
        
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                obj.due_date.strftime('%Y-%m-%d %H:%M')
            )
        return obj.due_date.strftime('%Y-%m-%d %H:%M')
    due_date_display.short_description = 'Due Date'
    
    actions = ['assign_to_agent', 'retry_failed_tasks', 'escalate_tasks']
    
    def assign_to_agent(self, request, queryset):
        """Admin action to assign tasks to agents."""
        from .services.orchestration_engine import orchestration_engine
        
        assigned_count = 0
        for task in queryset.filter(status='pending'):
            if orchestration_engine.assign_task_to_best_agent(task):
                assigned_count += 1
        
        self.message_user(request, f"Assigned {assigned_count} tasks to agents.")
    assign_to_agent.short_description = "Assign selected tasks to agents"
    
    def retry_failed_tasks(self, request, queryset):
        """Admin action to retry failed tasks."""
        retried_count = 0
        for task in queryset.filter(status='failed'):
            if task.can_retry():
                task.retry_count += 1
                task.status = 'pending'
                task.assigned_agent = None
                task.error_details = None
                task.save()
                retried_count += 1
        
        self.message_user(request, f"Retried {retried_count} failed tasks.")
    retry_failed_tasks.short_description = "Retry selected failed tasks"


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    """Admin interface for task assignments."""
    
    list_display = [
        'task_title', 'agent_name', 'assigned_by', 'assigned_at',
        'accepted_at', 'completed_at', 'is_active'
    ]
    list_filter = ['assigned_by', 'is_active', 'assigned_at', 'agent__agent_type']
    search_fields = ['task__title', 'agent__name', 'assignment_reason']
    readonly_fields = ['id', 'assigned_at', 'accepted_at', 'completed_at']
    
    def task_title(self, obj):
        return obj.task.title
    task_title.short_description = 'Task'
    
    def agent_name(self, obj):
        return obj.agent.name
    agent_name.short_description = 'Agent'


@admin.register(TaskExecutionLog)
class TaskExecutionLogAdmin(admin.ModelAdmin):
    """Admin interface for task execution logs."""
    
    list_display = [
        'task_title', 'agent_name', 'log_level_badge', 'step_name',
        'message_preview', 'created_on'
    ]
    list_filter = ['log_level', 'created_on', 'agent__name']
    search_fields = ['task__title', 'agent__name', 'message', 'step_name']
    readonly_fields = ['id', 'created_on']
    
    def task_title(self, obj):
        return obj.task.title
    task_title.short_description = 'Task'
    
    def agent_name(self, obj):
        return obj.agent.name
    agent_name.short_description = 'Agent'
    
    def log_level_badge(self, obj):
        colors = {
            'DEBUG': 'gray',
            'INFO': 'blue',
            'WARNING': 'orange',
            'ERROR': 'red',
            'CRITICAL': 'darkred'
        }
        color = colors.get(obj.log_level, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.log_level
        )
    log_level_badge.short_description = 'Level'
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'


@admin.register(OrchestrationRule)
class OrchestrationRuleAdmin(admin.ModelAdmin):
    """Admin interface for orchestration rules."""
    
    list_display = [
        'name', 'rule_type', 'priority', 'is_active',
        'trigger_count', 'last_triggered'
    ]
    list_filter = ['rule_type', 'is_active', 'created_on']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'trigger_count', 'last_triggered', 'created_on', 'modified_on']


@admin.register(SystemHealth)
class SystemHealthAdmin(admin.ModelAdmin):
    """Admin interface for system health metrics."""
    
    list_display = [
        'component', 'metric_name', 'status_badge', 'metric_value_display',
        'last_check'
    ]
    list_filter = ['component', 'status', 'last_check']
    search_fields = ['component', 'metric_name']
    readonly_fields = ['id', 'last_check', 'created_on', 'modified_on']
    
    def status_badge(self, obj):
        colors = {
            'healthy': 'green',
            'warning': 'orange',
            'critical': 'red',
            'unknown': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def metric_value_display(self, obj):
        return str(obj.metric_value)[:100]
    metric_value_display.short_description = 'Value'
