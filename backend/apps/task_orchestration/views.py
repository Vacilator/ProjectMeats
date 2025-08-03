"""
Task Orchestration views for ProjectMeats AI system.

Provides comprehensive REST API endpoints for task management,
agent orchestration, and system monitoring.
"""
from datetime import timedelta
from typing import Dict, Any

from django.utils import timezone
from django.db.models import Q, Count
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import (
    Agent, Task, TaskAssignment, TaskExecutionLog, 
    OrchestrationRule, SystemHealth, TaskStatus, AgentStatus
)
from .serializers import (
    AgentSerializer, TaskListSerializer, TaskDetailSerializer, TaskCreateSerializer,
    TaskAssignmentSerializer, TaskExecutionLogSerializer, OrchestrationRuleSerializer,
    SystemHealthSerializer, OrchestrationStatusSerializer, TaskActionSerializer,
    AgentActionSerializer, CreateTaskFromBugReportSerializer,
    CreateTaskFromDeploymentFailureSerializer
)
from .services.orchestration_engine import orchestration_engine
from apps.bug_reports.models import BugReport


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for orchestration API."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orchestrated tasks.
    
    Provides CRUD operations plus special actions for task management
    including assignment, retry, escalation, and status updates.
    """
    
    queryset = Task.objects.all()
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = {
        'task_type': ['exact', 'in'],
        'priority': ['exact', 'in'],
        'status': ['exact', 'in'],
        'assigned_agent': ['exact'],
        'auto_assign': ['exact'],
        'escalation_level': ['exact', 'gte', 'lte'],
        'created_on': ['gte', 'lte'],
        'due_date': ['gte', 'lte'],
    }
    
    search_fields = ['title', 'description', 'error_details']
    ordering_fields = ['created_on', 'modified_on', 'priority', 'due_date', 'escalation_level']
    ordering = ['-priority', '-created_on']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        else:
            return TaskDetailSerializer
    
    def get_queryset(self):
        """Filter tasks based on user permissions."""
        queryset = Task.objects.select_related('assigned_agent', 'owner').prefetch_related('depends_on', 'dependent_tasks')
        
        # Filter by owner if not staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create task with current user as owner."""
        task = serializer.save(owner=self.request.user)
        
        # Auto-assign if requested
        if task.auto_assign and task.can_be_assigned:
            try:
                orchestration_engine.assign_task_to_best_agent(task)
            except Exception as e:
                # Log error but don't fail task creation
                pass
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Manually assign task to an agent."""
        task = self.get_object()
        serializer = TaskActionSerializer(data=request.data)
        
        if serializer.is_valid():
            agent_id = serializer.validated_data.get('agent_id')
            reason = serializer.validated_data.get('reason', 'Manual assignment')
            
            if agent_id:
                try:
                    agent = Agent.objects.get(id=agent_id, is_active=True)
                    
                    if not agent.is_available_for_assignment:
                        return Response(
                            {'error': 'Agent is not available for assignment'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Create manual assignment
                    assignment = TaskAssignment.objects.create(
                        task=task,
                        agent=agent,
                        assigned_by=f"manual_{request.user.username}",
                        assignment_reason=reason
                    )
                    
                    task.assigned_agent = agent
                    task.status = TaskStatus.ASSIGNED
                    task.save()
                    
                    return Response({
                        'message': f'Task assigned to {agent.name}',
                        'assignment_id': assignment.id
                    })
                    
                except Agent.DoesNotExist:
                    return Response(
                        {'error': 'Agent not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Auto-assign to best agent
                assignment = orchestration_engine.assign_task_to_best_agent(task)
                
                if assignment:
                    return Response({
                        'message': f'Task auto-assigned to {assignment.agent.name}',
                        'assignment_id': assignment.id
                    })
                else:
                    return Response(
                        {'error': 'No suitable agent available'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed task."""
        task = self.get_object()
        
        if not task.can_retry():
            return Response(
                {'error': 'Task cannot be retried'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset task for retry
        task.retry_count += 1
        task.status = TaskStatus.PENDING
        task.assigned_agent = None
        task.error_details = None
        task.save()
        
        # Try to auto-assign
        assignment = orchestration_engine.assign_task_to_best_agent(task)
        
        message = f'Task retried (attempt {task.retry_count})'
        if assignment:
            message += f' and assigned to {assignment.agent.name}'
        
        return Response({'message': message})
    
    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """Escalate a task."""
        task = self.get_object()
        serializer = TaskActionSerializer(data=request.data)
        
        if serializer.is_valid():
            reason = serializer.validated_data.get('reason', 'Manual escalation')
            
            # Escalate task
            orchestration_engine.handle_task_failure(task, f"Manual escalation: {reason}")
            
            return Response({
                'message': f'Task escalated to level {task.escalation_level}',
                'new_priority': task.priority
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark task as completed."""
        task = self.get_object()
        serializer = TaskActionSerializer(data=request.data)
        
        if serializer.is_valid():
            output_data = serializer.validated_data.get('output_data', {})
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = timezone.now()
            task.output_data = output_data
            task.save()
            
            # Update agent statistics
            if task.assigned_agent:
                duration = task.duration_so_far if task.started_at else None
                task.assigned_agent.update_statistics(True, duration)
            
            return Response({'message': 'Task marked as completed'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a task."""
        task = self.get_object()
        
        task.status = TaskStatus.CANCELLED
        task.save()
        
        return Response({'message': 'Task cancelled'})
    
    @action(detail=True, methods=['get'])
    def execution_logs(self, request, pk=None):
        """Get execution logs for a task."""
        task = self.get_object()
        logs = task.execution_logs.order_by('-created_on')
        
        serializer = TaskExecutionLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_from_bug_report(self, request):
        """Create a task from a bug report."""
        serializer = CreateTaskFromBugReportSerializer(data=request.data)
        
        if serializer.is_valid():
            bug_report_id = serializer.validated_data['bug_report_id']
            
            try:
                bug_report = BugReport.objects.get(id=bug_report_id)
                task = orchestration_engine.create_task_from_bug_report(bug_report)
                
                response_serializer = TaskDetailSerializer(task)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
            except BugReport.DoesNotExist:
                return Response(
                    {'error': 'Bug report not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def create_from_deployment_failure(self, request):
        """Create a task from a deployment failure."""
        serializer = CreateTaskFromDeploymentFailureSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            error_details = {
                'error_message': data['error_message'],
                'failed_step': data.get('failed_step', 'Unknown'),
                'source': 'manual_api_creation'
            }
            
            server_info = {
                'hostname': data.get('server_hostname', 'Unknown'),
                'domain': data.get('domain', 'Unknown'),
                **data.get('additional_info', {})
            }
            
            task = orchestration_engine.create_task_from_production_failure(
                deployment_id=data['deployment_id'],
                error_details=error_details,
                server_info=server_info
            )
            
            response_serializer = TaskDetailSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing AI agents.
    
    Provides CRUD operations plus special actions for agent management
    including status updates and configuration changes.
    """
    
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = {
        'agent_type': ['exact', 'in'],
        'status': ['exact', 'in'],
        'is_active': ['exact'],
        'priority_weight': ['gte', 'lte'],
        'success_rate': ['gte', 'lte'],
    }
    
    search_fields = ['name', 'capabilities']
    ordering_fields = ['name', 'created_on', 'priority_weight', 'success_rate', 'total_tasks_completed']
    ordering = ['-priority_weight', 'name']
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update agent status."""
        agent = self.get_object()
        serializer = AgentActionSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            reason = serializer.validated_data.get('reason', f'Manual {action}')
            
            if action == 'activate':
                agent.is_active = True
                agent.status = AgentStatus.AVAILABLE
            elif action == 'deactivate':
                agent.is_active = False
                agent.status = AgentStatus.OFFLINE
            elif action == 'set_available':
                agent.status = AgentStatus.AVAILABLE
            elif action == 'set_busy':
                agent.status = AgentStatus.BUSY
            elif action == 'set_offline':
                agent.status = AgentStatus.OFFLINE
            elif action == 'set_maintenance':
                agent.status = AgentStatus.MAINTENANCE
            
            agent.save()
            
            return Response({
                'message': f'Agent status updated: {action}',
                'new_status': agent.status,
                'is_active': agent.is_active
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def current_tasks(self, request, pk=None):
        """Get current tasks assigned to this agent."""
        agent = self.get_object()
        current_tasks = agent.assigned_tasks.filter(
            status__in=[TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
        )
        
        serializer = TaskListSerializer(current_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def task_history(self, request, pk=None):
        """Get task history for this agent."""
        agent = self.get_object()
        tasks = agent.assigned_tasks.order_by('-modified_on')[:50]  # Last 50 tasks
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def heartbeat(self, request, pk=None):
        """Update agent heartbeat."""
        agent = self.get_object()
        agent.last_heartbeat = timezone.now()
        
        # Update status to available if agent was offline
        if agent.status == AgentStatus.OFFLINE and agent.is_active:
            agent.status = AgentStatus.AVAILABLE
        
        agent.save()
        
        return Response({'message': 'Heartbeat updated', 'timestamp': agent.last_heartbeat})


class TaskAssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing task assignments."""
    
    queryset = TaskAssignment.objects.select_related('task', 'agent')
    serializer_class = TaskAssignmentSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    filterset_fields = {
        'task': ['exact'],
        'agent': ['exact'],
        'is_active': ['exact'],
        'assigned_at': ['gte', 'lte'],
    }
    
    ordering_fields = ['assigned_at', 'completed_at']
    ordering = ['-assigned_at']


class TaskExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing task execution logs."""
    
    queryset = TaskExecutionLog.objects.select_related('task', 'agent')
    serializer_class = TaskExecutionLogSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = {
        'task': ['exact'],
        'agent': ['exact'],
        'log_level': ['exact', 'in'],
        'created_on': ['gte', 'lte'],
    }
    
    search_fields = ['message', 'step_name']
    ordering_fields = ['created_on']
    ordering = ['-created_on']


class OrchestrationRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing orchestration rules."""
    
    queryset = OrchestrationRule.objects.all()
    serializer_class = OrchestrationRuleSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = {
        'rule_type': ['exact', 'in'],
        'is_active': ['exact'],
        'priority': ['gte', 'lte'],
    }
    
    search_fields = ['name', 'description']
    ordering_fields = ['priority', 'name', 'created_on']
    ordering = ['priority', 'name']


class SystemHealthViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing system health metrics."""
    
    queryset = SystemHealth.objects.all()
    serializer_class = SystemHealthSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    filterset_fields = {
        'component': ['exact', 'in'],
        'status': ['exact', 'in'],
        'last_check': ['gte', 'lte'],
    }
    
    ordering_fields = ['component', 'metric_name', 'last_check']
    ordering = ['component', 'metric_name']


class OrchestrationStatusViewSet(viewsets.ViewSet):
    """ViewSet for orchestration system status and control."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get comprehensive orchestration system status."""
        status_data = orchestration_engine.get_orchestration_status()
        serializer = OrchestrationStatusSerializer(status_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard data for orchestration monitoring."""
        # Recent tasks
        recent_tasks = Task.objects.filter(
            created_on__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Active tasks by status
        task_stats = Task.objects.aggregate(
            pending=Count('id', filter=Q(status=TaskStatus.PENDING)),
            assigned=Count('id', filter=Q(status=TaskStatus.ASSIGNED)),
            in_progress=Count('id', filter=Q(status=TaskStatus.IN_PROGRESS)),
            completed_today=Count('id', filter=Q(
                status=TaskStatus.COMPLETED,
                completed_at__gte=timezone.now() - timedelta(hours=24)
            )),
            failed_today=Count('id', filter=Q(
                status=TaskStatus.FAILED,
                modified_on__gte=timezone.now() - timedelta(hours=24)
            )),
        )
        
        # Agent stats
        agent_stats = Agent.objects.aggregate(
            total=Count('id'),
            available=Count('id', filter=Q(status=AgentStatus.AVAILABLE, is_active=True)),
            busy=Count('id', filter=Q(status=AgentStatus.BUSY, is_active=True)),
            offline=Count('id', filter=Q(status=AgentStatus.OFFLINE)),
        )
        
        # Recent deployment failures
        from .services.deployment_monitor import deployment_monitor
        recent_failures = deployment_monitor.get_recent_deployment_failures(hours=24)
        
        return Response({
            'timestamp': timezone.now(),
            'tasks': {
                'recent_24h': recent_tasks,
                **task_stats
            },
            'agents': agent_stats,
            'recent_deployment_failures': len(recent_failures),
            'system_health': orchestration_engine._get_system_health_summary()
        })
    
    @action(detail=False, methods=['post'])
    def process_pending_tasks(self, request):
        """Manually trigger processing of pending tasks."""
        assigned_count = orchestration_engine.process_pending_tasks()
        return Response({
            'message': f'Processed pending tasks',
            'assigned_count': assigned_count
        })
    
    @action(detail=False, methods=['post'])
    def check_deployment_failures(self, request):
        """Manually trigger deployment failure check."""
        from .services.deployment_monitor import deployment_monitor
        created_tasks = deployment_monitor.monitor_deployment_status()
        
        return Response({
            'message': 'Checked for deployment failures',
            'tasks_created': len(created_tasks),
            'task_ids': [str(task.id) for task in created_tasks]
        })
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get detailed metrics for monitoring."""
        # Task metrics by type
        task_types = Task.objects.values('task_type').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status=TaskStatus.COMPLETED)),
            failed=Count('id', filter=Q(status=TaskStatus.FAILED)),
        )
        
        # Agent performance
        agents = Agent.objects.filter(is_active=True).values(
            'id', 'name', 'agent_type', 'status', 'success_rate',
            'total_tasks_completed', 'total_tasks_failed'
        )
        
        # Recent activity timeline
        recent_activity = []
        for hours_ago in range(24):
            start_time = timezone.now() - timedelta(hours=hours_ago+1)
            end_time = timezone.now() - timedelta(hours=hours_ago)
            
            activity = {
                'hour': hours_ago,
                'timestamp': end_time,
                'tasks_created': Task.objects.filter(
                    created_on__gte=start_time,
                    created_on__lt=end_time
                ).count(),
                'tasks_completed': Task.objects.filter(
                    status=TaskStatus.COMPLETED,
                    completed_at__gte=start_time,
                    completed_at__lt=end_time
                ).count(),
                'tasks_failed': Task.objects.filter(
                    status=TaskStatus.FAILED,
                    modified_on__gte=start_time,
                    modified_on__lt=end_time
                ).count(),
            }
            recent_activity.append(activity)
        
        return Response({
            'task_types': list(task_types),
            'agents': list(agents),
            'recent_activity': recent_activity[:24],  # Last 24 hours
        })
