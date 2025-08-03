"""URL configuration for task orchestration app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TaskViewSet, AgentViewSet, TaskAssignmentViewSet, TaskExecutionLogViewSet,
    OrchestrationRuleViewSet, SystemHealthViewSet, OrchestrationStatusViewSet
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'agents', AgentViewSet, basename='agents')
router.register(r'assignments', TaskAssignmentViewSet, basename='assignments')
router.register(r'execution-logs', TaskExecutionLogViewSet, basename='execution-logs')
router.register(r'rules', OrchestrationRuleViewSet, basename='rules')
router.register(r'health', SystemHealthViewSet, basename='health')
router.register(r'status', OrchestrationStatusViewSet, basename='status')

app_name = 'task_orchestration'

urlpatterns = [
    path('orchestration/', include(router.urls)),
]