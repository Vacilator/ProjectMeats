"""
Task Discovery Service for Continuous Application Growth.

This service analyzes the current task queue and application state to
autonomously generate new tasks for continuous improvement, feature
development, and application growth based on ProjectMeats business priorities.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from django.db.models import Q, Count
from django.utils import timezone

from ..models import (
    Task, Agent, TaskStatus, TaskPriority, TaskType, AgentType, AgentStatus
)
from .orchestration_engine import orchestration_engine, TaskCreationRequest


logger = logging.getLogger(__name__)


class GrowthPriority(Enum):
    """Priority levels for application growth areas."""
    CRITICAL_BUSINESS = 1  # Core business functionality
    USER_EXPERIENCE = 2    # UI/UX improvements
    PERFORMANCE = 3        # Performance optimizations
    SECURITY = 4          # Security enhancements
    MAINTAINABILITY = 5    # Code quality and maintenance
    INNOVATION = 6        # New features and capabilities


@dataclass
class DiscoveryTask:
    """Represents a discovered task for creation."""
    title: str
    description: str
    task_type: str
    priority: str
    growth_area: str
    estimated_hours: int = 2
    depends_on: List[str] = None
    rationale: str = ""


class ApplicationGrowthAnalyzer:
    """
    Analyzes the ProjectMeats application for growth opportunities.
    
    Focuses on the core business domain: meat sales broker management system
    with PowerApps/Dataverse migration to Django/React stack.
    """
    
    def __init__(self):
        self.logger = logger
        self.business_priorities = self._define_business_priorities()
    
    def _define_business_priorities(self) -> Dict[str, Dict]:
        """Define ProjectMeats business growth priorities."""
        return {
            "supplier_management": {
                "priority": GrowthPriority.CRITICAL_BUSINESS,
                "description": "Supplier relationship and inventory management",
                "features": ["supplier_profiles", "product_catalogs", "pricing_management"]
            },
            "customer_management": {
                "priority": GrowthPriority.CRITICAL_BUSINESS,
                "description": "Customer relationship and order management",
                "features": ["customer_profiles", "order_history", "credit_management"]
            },
            "purchase_orders": {
                "priority": GrowthPriority.CRITICAL_BUSINESS,
                "description": "Purchase order lifecycle management",
                "features": ["order_creation", "approval_workflows", "tracking"]
            },
            "accounts_receivable": {
                "priority": GrowthPriority.CRITICAL_BUSINESS,
                "description": "Financial management and billing",
                "features": ["invoicing", "payment_tracking", "aging_reports"]
            },
            "reporting_analytics": {
                "priority": GrowthPriority.USER_EXPERIENCE,
                "description": "Business intelligence and reporting",
                "features": ["dashboard", "custom_reports", "data_export"]
            },
            "mobile_optimization": {
                "priority": GrowthPriority.USER_EXPERIENCE,
                "description": "Mobile-first user experience",
                "features": ["responsive_design", "mobile_app", "offline_capability"]
            },
            "api_performance": {
                "priority": GrowthPriority.PERFORMANCE,
                "description": "API and database performance",
                "features": ["query_optimization", "caching", "pagination"]
            },
            "security_compliance": {
                "priority": GrowthPriority.SECURITY,
                "description": "Security and compliance features",
                "features": ["authentication", "authorization", "audit_logging"]
            }
        }
    
    def analyze_missing_features(self) -> List[DiscoveryTask]:
        """Analyze and identify missing or incomplete features."""
        discovery_tasks = []
        
        # Check for incomplete business modules
        for area, config in self.business_priorities.items():
            tasks = self._analyze_business_area(area, config)
            discovery_tasks.extend(tasks)
        
        return discovery_tasks
    
    def _analyze_business_area(self, area: str, config: Dict) -> List[DiscoveryTask]:
        """Analyze a specific business area for improvement opportunities."""
        tasks = []
        priority_mapping = {
            GrowthPriority.CRITICAL_BUSINESS: TaskPriority.HIGH,
            GrowthPriority.USER_EXPERIENCE: TaskPriority.MEDIUM,
            GrowthPriority.PERFORMANCE: TaskPriority.MEDIUM,
            GrowthPriority.SECURITY: TaskPriority.HIGH,
            GrowthPriority.MAINTAINABILITY: TaskPriority.LOW,
            GrowthPriority.INNOVATION: TaskPriority.LOW
        }
        
        priority = priority_mapping.get(config["priority"], TaskPriority.MEDIUM)
        
        # Generate feature development tasks
        if area == "supplier_management":
            tasks.extend([
                DiscoveryTask(
                    title="Enhance Supplier Profile Management",
                    description="Improve supplier profile functionality with advanced contact management, performance metrics, and automated communications",
                    task_type=TaskType.FEATURE_DEVELOPMENT,
                    priority=priority,
                    growth_area=area,
                    estimated_hours=8,
                    rationale="Core business functionality for meat broker operations"
                ),
                DiscoveryTask(
                    title="Implement Supplier Performance Analytics",
                    description="Create analytics dashboard for supplier performance tracking including delivery times, quality metrics, and cost analysis",
                    task_type=TaskType.FEATURE_DEVELOPMENT,
                    priority=priority,
                    growth_area=area,
                    estimated_hours=12,
                    rationale="Critical for informed supplier selection and management"
                )
            ])
        
        elif area == "customer_management":
            tasks.extend([
                DiscoveryTask(
                    title="Enhance Customer Order History",
                    description="Implement comprehensive customer order history with filtering, search, and export capabilities",
                    task_type=TaskType.FEATURE_DEVELOPMENT,
                    priority=priority,
                    growth_area=area,
                    estimated_hours=6,
                    rationale="Essential for customer service and relationship management"
                ),
                DiscoveryTask(
                    title="Implement Customer Credit Management",
                    description="Add customer credit limits, payment terms management, and automated credit checks",
                    task_type=TaskType.FEATURE_DEVELOPMENT,
                    priority=priority,
                    growth_area=area,
                    estimated_hours=10,
                    rationale="Critical for financial risk management"
                )
            ])
        
        elif area == "reporting_analytics":
            tasks.extend([
                DiscoveryTask(
                    title="Create Executive Dashboard",
                    description="Implement executive-level dashboard with key business metrics, trends, and performance indicators",
                    task_type=TaskType.FEATURE_DEVELOPMENT,
                    priority=priority,
                    growth_area=area,
                    estimated_hours=15,
                    rationale="Essential for business decision making and growth tracking"
                ),
                DiscoveryTask(
                    title="Implement Custom Report Builder",
                    description="Add drag-and-drop report builder for users to create custom business reports",
                    task_type=TaskType.FEATURE_DEVELOPMENT,
                    priority=priority,
                    growth_area=area,
                    estimated_hours=20,
                    rationale="Empowers users with self-service analytics capabilities"
                )
            ])
        
        elif area == "api_performance":
            tasks.extend([
                DiscoveryTask(
                    title="Optimize Database Queries",
                    description="Analyze and optimize slow database queries, implement proper indexing and query optimization",
                    task_type=TaskType.PERFORMANCE_OPTIMIZATION,
                    priority=priority,
                    growth_area=area,
                    estimated_hours=8,
                    rationale="Improves application responsiveness and user experience"
                ),
                DiscoveryTask(
                    title="Implement API Caching Strategy",
                    description="Add Redis-based caching for frequently accessed API endpoints and database queries",
                    task_type=TaskType.PERFORMANCE_OPTIMIZATION,
                    priority=priority,
                    growth_area=area,
                    estimated_hours=6,
                    rationale="Reduces server load and improves response times"
                )
            ])
        
        return tasks


class TaskQueueAnalyzer:
    """
    Analyzes the current task queue to identify gaps and opportunities.
    """
    
    def __init__(self):
        self.logger = logger
    
    def analyze_task_distribution(self) -> Dict[str, Any]:
        """Analyze current task distribution and identify gaps."""
        # Get task counts by type and status
        task_stats = Task.objects.values('task_type', 'status').annotate(count=Count('id'))
        
        # Analyze pending vs in-progress ratio
        pending_count = Task.objects.filter(status=TaskStatus.PENDING).count()
        active_count = Task.objects.filter(
            status__in=[TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
        ).count()
        
        # Analyze task age
        old_tasks = Task.objects.filter(
            created_on__lt=timezone.now() - timedelta(days=7),
            status__in=[TaskStatus.PENDING, TaskStatus.ASSIGNED]
        ).count()
        
        # Analyze priority distribution
        priority_stats = Task.objects.values('priority').annotate(count=Count('id'))
        
        return {
            'task_stats': list(task_stats),
            'pending_count': pending_count,
            'active_count': active_count,
            'old_tasks_count': old_tasks,
            'priority_stats': list(priority_stats),
            'total_tasks': Task.objects.count(),
            'analysis_timestamp': timezone.now()
        }
    
    def identify_underrepresented_areas(self) -> List[str]:
        """Identify task types that are underrepresented in the queue."""
        # Get current task type distribution
        current_types = set(Task.objects.filter(
            status__in=[TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
        ).values_list('task_type', flat=True))
        
        # Define essential task types for continuous growth
        essential_types = {
            TaskType.FEATURE_DEVELOPMENT,
            TaskType.PERFORMANCE_OPTIMIZATION,
            TaskType.SECURITY_ENHANCEMENT,
            TaskType.TESTING,
            TaskType.DOCUMENTATION,
            TaskType.USER_EXPERIENCE_IMPROVEMENT
        }
        
        # Find missing types
        missing_types = essential_types - current_types
        
        return list(missing_types)


class TaskDiscoveryService:
    """
    Main service for autonomous task discovery and generation.
    
    Analyzes the current task queue and application state to continuously
    generate new tasks for application growth and improvement.
    """
    
    def __init__(self):
        self.logger = logger
        self.growth_analyzer = ApplicationGrowthAnalyzer()
        self.queue_analyzer = TaskQueueAnalyzer()
        self.discovery_agent = None
    
    def discover_and_create_tasks(self, max_tasks: int = 5) -> Dict[str, Any]:
        """
        Main method for discovering and creating new tasks.
        
        Args:
            max_tasks: Maximum number of tasks to create in one discovery run
            
        Returns:
            Dictionary with discovery results and created tasks
        """
        try:
            self.logger.info("Starting task discovery process")
            
            # Ensure discovery agent exists
            self._ensure_discovery_agent()
            
            # Analyze current state
            queue_analysis = self.queue_analyzer.analyze_task_distribution()
            underrepresented_areas = self.queue_analyzer.identify_underrepresented_areas()
            
            # Check if discovery is needed
            discovery_needed, reason = self._should_run_discovery(queue_analysis)
            
            if not discovery_needed:
                return {
                    'discovery_needed': False,
                    'reason': reason,
                    'queue_analysis': queue_analysis,
                    'tasks_created': 0,
                    'timestamp': timezone.now()
                }
            
            # Discover new tasks
            potential_tasks = self._discover_tasks(queue_analysis, underrepresented_areas)
            
            # Prioritize and filter tasks
            selected_tasks = self._prioritize_tasks(potential_tasks, max_tasks)
            
            # Create tasks
            created_tasks = self._create_discovered_tasks(selected_tasks)
            
            self.logger.info(f"Discovery complete: {len(created_tasks)} tasks created")
            
            return {
                'discovery_needed': True,
                'reason': reason,
                'queue_analysis': queue_analysis,
                'potential_tasks_found': len(potential_tasks),
                'tasks_created': len(created_tasks),
                'created_task_ids': [str(task.id) for task in created_tasks],
                'underrepresented_areas': underrepresented_areas,
                'timestamp': timezone.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error in task discovery: {e}")
            return {
                'discovery_needed': False,
                'error': str(e),
                'tasks_created': 0,
                'timestamp': timezone.now()
            }
    
    def _ensure_discovery_agent(self):
        """Ensure discovery agent exists and is configured."""
        try:
            self.discovery_agent = Agent.objects.get(
                agent_type=AgentType.DISCOVERY_AGENT,
                is_active=True
            )
        except Agent.DoesNotExist:
            # Create discovery agent
            self.discovery_agent = Agent.objects.create(
                name="DiscoveryAgent-Growth",
                agent_type=AgentType.DISCOVERY_AGENT,
                capabilities=[
                    TaskType.TASK_DISCOVERY,
                    TaskType.APPLICATION_ANALYSIS,
                    TaskType.FEATURE_DEVELOPMENT,
                    TaskType.PERFORMANCE_OPTIMIZATION
                ],
                max_concurrent_tasks=3,
                priority_weight=9.0,  # High priority for growth tasks
                configuration={
                    'specialization': 'application_growth',
                    'discovery_enabled': True,
                    'growth_focus': 'business_value',
                    'analysis_depth': 'comprehensive'
                },
                status=AgentStatus.AVAILABLE,
                is_active=True
            )
            self.logger.info(f"Created discovery agent: {self.discovery_agent.name}")
    
    def _should_run_discovery(self, queue_analysis: Dict) -> Tuple[bool, str]:
        """Determine if task discovery should run based on current queue state."""
        pending_count = queue_analysis['pending_count']
        active_count = queue_analysis['active_count']
        total_tasks = queue_analysis['total_tasks']
        old_tasks = queue_analysis['old_tasks_count']
        
        # Run discovery if task queue is low
        if pending_count < 3:
            return True, f"Low pending task count: {pending_count}"
        
        # Run discovery if no active development tasks
        if active_count < 2:
            return True, f"Low active task count: {active_count}"
        
        # Run discovery if there are stale tasks
        if old_tasks > 2:
            return True, f"Stale tasks detected: {old_tasks}"
        
        # Run discovery if total task count is very low
        if total_tasks < 5:
            return True, f"Total task count low: {total_tasks}"
        
        # Always run discovery periodically for continuous growth
        last_discovery = Task.objects.filter(
            task_type=TaskType.TASK_DISCOVERY,
            created_on__gte=timezone.now() - timedelta(hours=2)
        ).exists()
        
        if not last_discovery:
            return True, "Periodic discovery for continuous growth"
        
        return False, "Task queue is adequately populated"
    
    def _discover_tasks(self, queue_analysis: Dict, underrepresented_areas: List[str]) -> List[DiscoveryTask]:
        """Discover potential new tasks based on analysis."""
        potential_tasks = []
        
        # Get tasks from growth analyzer
        growth_tasks = self.growth_analyzer.analyze_missing_features()
        potential_tasks.extend(growth_tasks)
        
        # Add tasks for underrepresented areas
        for area in underrepresented_areas:
            area_tasks = self._generate_tasks_for_area(area)
            potential_tasks.extend(area_tasks)
        
        # Add maintenance and improvement tasks
        maintenance_tasks = self._generate_maintenance_tasks()
        potential_tasks.extend(maintenance_tasks)
        
        return potential_tasks
    
    def _generate_tasks_for_area(self, task_type: str) -> List[DiscoveryTask]:
        """Generate tasks for underrepresented areas."""
        tasks = []
        
        if task_type == TaskType.TESTING:
            tasks.append(DiscoveryTask(
                title="Expand Test Coverage for Core Business Logic",
                description="Add comprehensive unit and integration tests for supplier and customer management modules",
                task_type=TaskType.TESTING,
                priority=TaskPriority.MEDIUM,
                growth_area="quality_assurance",
                estimated_hours=6,
                rationale="Ensures reliability of core business functionality"
            ))
        
        elif task_type == TaskType.DOCUMENTATION:
            tasks.append(DiscoveryTask(
                title="Update API Documentation",
                description="Refresh API documentation with latest endpoints and add usage examples for business operations",
                task_type=TaskType.DOCUMENTATION,
                priority=TaskPriority.LOW,
                growth_area="developer_experience",
                estimated_hours=4,
                rationale="Improves developer productivity and system maintainability"
            ))
        
        elif task_type == TaskType.SECURITY_ENHANCEMENT:
            tasks.append(DiscoveryTask(
                title="Implement Advanced Security Audit Logging",
                description="Add comprehensive audit logging for all financial and sensitive business operations",
                task_type=TaskType.SECURITY_ENHANCEMENT,
                priority=TaskPriority.HIGH,
                growth_area="security_compliance",
                estimated_hours=8,
                rationale="Essential for compliance and fraud prevention"
            ))
        
        return tasks
    
    def _generate_maintenance_tasks(self) -> List[DiscoveryTask]:
        """Generate maintenance and improvement tasks."""
        return [
            DiscoveryTask(
                title="Code Quality Analysis and Refactoring",
                description="Analyze code quality metrics and refactor high-complexity modules for better maintainability",
                task_type=TaskType.MAINTENANCE,
                priority=TaskPriority.LOW,
                growth_area="code_quality",
                estimated_hours=10,
                rationale="Improves long-term maintainability and reduces technical debt"
            ),
            DiscoveryTask(
                title="Dependency Security Updates",
                description="Review and update dependencies with security vulnerabilities, test compatibility",
                task_type=TaskType.SECURITY_ENHANCEMENT,
                priority=TaskPriority.MEDIUM,
                growth_area="security_maintenance",
                estimated_hours=4,
                rationale="Maintains security posture and prevents vulnerabilities"
            )
        ]
    
    def _prioritize_tasks(self, tasks: List[DiscoveryTask], max_tasks: int) -> List[DiscoveryTask]:
        """Prioritize discovered tasks and select top candidates."""
        # Sort by priority and business value
        priority_order = {
            TaskPriority.EMERGENCY: 0,
            TaskPriority.CRITICAL: 1,
            TaskPriority.HIGH: 2,
            TaskPriority.MEDIUM: 3,
            TaskPriority.LOW: 4
        }
        
        # Sort by priority, then by estimated business value
        sorted_tasks = sorted(tasks, key=lambda t: (
            priority_order.get(t.priority, 5),
            -t.estimated_hours  # Prefer smaller tasks for quick wins
        ))
        
        return sorted_tasks[:max_tasks]
    
    def _create_discovered_tasks(self, tasks: List[DiscoveryTask]) -> List[Task]:
        """Create actual Task objects from discovered tasks."""
        created_tasks = []
        
        for discovered_task in tasks:
            try:
                request = TaskCreationRequest(
                    title=discovered_task.title,
                    description=f"{discovered_task.description}\n\nGrowth Area: {discovered_task.growth_area}\nRationale: {discovered_task.rationale}",
                    task_type=discovered_task.task_type,
                    priority=discovered_task.priority,
                    estimated_duration=timedelta(hours=discovered_task.estimated_hours),
                    input_data={
                        'growth_area': discovered_task.growth_area,
                        'discovery_source': 'autonomous_discovery',
                        'estimated_hours': discovered_task.estimated_hours,
                        'discovery_timestamp': timezone.now().isoformat()
                    }
                )
                
                task = orchestration_engine.create_task(request)
                created_tasks.append(task)
                
                self.logger.info(f"Created discovery task: {task.title}")
                
            except Exception as e:
                self.logger.error(f"Failed to create discovery task '{discovered_task.title}': {e}")
        
        return created_tasks


# Global instance for easy access
task_discovery_service = TaskDiscoveryService()