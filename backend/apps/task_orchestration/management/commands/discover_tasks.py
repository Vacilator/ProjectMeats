"""
Django management command for autonomous task discovery.

This command implements the scheduled AI agent that analyzes the running
task list and discovers new tasks for continuous application growth,
keeping the agents busy and the application evolving.
"""
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from apps.task_orchestration.services.task_discovery_service import task_discovery_service
from apps.task_orchestration.models import Task, Agent, TaskType, AgentType, TaskStatus


class Command(BaseCommand):
    """
    Management command for autonomous task discovery and creation.
    
    This command is designed to be run every 30-60 minutes via GitHub Actions
    or cron to ensure continuous application growth and agent utilization.
    """
    
    help = 'Discover and create new tasks for continuous application growth'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats = {
            'start_time': None,
            'discovery_runs': 0,
            'tasks_discovered': 0,
            'tasks_created': 0,
            'errors': 0,
        }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--max-tasks',
            type=int,
            default=3,
            help='Maximum number of tasks to create in one discovery run (default: 3)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run discovery analysis without creating tasks'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force discovery run even if recent tasks exist'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging output'
        )
        
        parser.add_argument(
            '--report-format',
            choices=['text', 'json'],
            default='text',
            help='Output format for discovery report (default: text)'
        )
    
    def handle(self, *args, **options):
        """Main entry point for the discovery command."""
        self.stats['start_time'] = timezone.now()
        
        max_tasks = options['max_tasks']
        dry_run = options['dry_run']
        force = options['force']
        verbose = options['verbose']
        report_format = options['report_format']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Running in DRY-RUN mode - no tasks will be created')
            )
        
        if verbose:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Starting task discovery process\n'
                    f'Max tasks: {max_tasks}\n'
                    f'Dry run: {dry_run}\n'
                    f'Force: {force}\n'
                    f'Report format: {report_format}'
                )
            )
        
        try:
            # Check if discovery should run
            if not force and not self._should_run_discovery():
                result = {
                    'discovery_needed': False,
                    'reason': 'Recent discovery run detected',
                    'tasks_created': 0,
                    'timestamp': timezone.now()
                }
                self._output_result(result, report_format)
                return
            
            # Run discovery process
            if dry_run:
                result = self._run_dry_discovery(max_tasks, verbose)
            else:
                result = task_discovery_service.discover_and_create_tasks(max_tasks)
            
            self.stats['discovery_runs'] = 1
            self.stats['tasks_created'] = result.get('tasks_created', 0)
            
            # Output results
            self._output_result(result, report_format)
            
            # Log success
            if verbose:
                self._print_final_stats()
            
        except Exception as e:
            self.stats['errors'] = 1
            error_msg = f"Error during task discovery: {e}"
            self.stderr.write(self.style.ERROR(error_msg))
            
            if report_format == 'json':
                error_result = {
                    'error': True,
                    'message': str(e),
                    'timestamp': timezone.now().isoformat()
                }
                self.stdout.write(json.dumps(error_result, indent=2))
            
            sys.exit(1)
    
    def _should_run_discovery(self) -> bool:
        """Check if discovery should run based on recent activity."""
        # Check for recent discovery tasks
        recent_discovery = Task.objects.filter(
            task_type=TaskType.TASK_DISCOVERY,
            created_on__gte=timezone.now() - timedelta(minutes=45)
        ).exists()
        
        if recent_discovery:
            return False
        
        # Check for recent discovery agent activity
        discovery_agent = Agent.objects.filter(
            agent_type=AgentType.DISCOVERY_AGENT,
            is_active=True,
            last_heartbeat__gte=timezone.now() - timedelta(minutes=30)
        ).first()
        
        if discovery_agent and discovery_agent.current_task_count > 0:
            return False
        
        return True
    
    def _run_dry_discovery(self, max_tasks: int, verbose: bool) -> Dict[str, Any]:
        """Run discovery analysis without creating tasks."""
        from apps.task_orchestration.services.task_discovery_service import (
            TaskQueueAnalyzer, ApplicationGrowthAnalyzer
        )
        
        try:
            # Analyze current state
            queue_analyzer = TaskQueueAnalyzer()
            growth_analyzer = ApplicationGrowthAnalyzer()
            
            queue_analysis = queue_analyzer.analyze_task_distribution()
            underrepresented_areas = queue_analyzer.identify_underrepresented_areas()
            potential_growth_tasks = growth_analyzer.analyze_missing_features()
            
            return {
                'dry_run': True,
                'discovery_needed': True,
                'queue_analysis': queue_analysis,
                'underrepresented_areas': underrepresented_areas,
                'potential_growth_tasks': len(potential_growth_tasks),
                'growth_task_samples': [
                    {
                        'title': task.title,
                        'type': task.task_type,
                        'priority': task.priority,
                        'growth_area': task.growth_area
                    }
                    for task in potential_growth_tasks[:3]
                ],
                'max_tasks_requested': max_tasks,
                'timestamp': timezone.now()
            }
            
        except Exception as e:
            return {
                'dry_run': True,
                'error': str(e),
                'timestamp': timezone.now()
            }
    
    def _output_result(self, result: Dict[str, Any], format_type: str):
        """Output discovery results in specified format."""
        if format_type == 'json':
            # Convert datetime objects to strings for JSON serialization
            json_result = self._prepare_for_json(result)
            self.stdout.write(json.dumps(json_result, indent=2, default=str))
        else:
            self._output_text_result(result)
    
    def _prepare_for_json(self, obj):
        """Prepare object for JSON serialization by converting datetime objects."""
        if isinstance(obj, dict):
            return {key: self._prepare_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_for_json(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
    
    def _output_text_result(self, result: Dict[str, Any]):
        """Output discovery results in human-readable text format."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📋 TASK DISCOVERY REPORT"))
        self.stdout.write("="*60)
        
        timestamp = result.get('timestamp', timezone.now())
        self.stdout.write(f"⏰ Timestamp: {timestamp}")
        
        if result.get('dry_run'):
            self.stdout.write(self.style.WARNING("🧪 DRY RUN MODE - No tasks created"))
        
        discovery_needed = result.get('discovery_needed', False)
        if not discovery_needed:
            reason = result.get('reason', 'Unknown')
            self.stdout.write(f"❌ Discovery not needed: {reason}")
            return
        
        self.stdout.write(self.style.SUCCESS("✅ Discovery process completed"))
        
        # Task creation summary
        tasks_created = result.get('tasks_created', 0)
        if tasks_created > 0:
            self.stdout.write(f"🎯 Tasks created: {tasks_created}")
            
            created_task_ids = result.get('created_task_ids', [])
            if created_task_ids:
                self.stdout.write("📝 Created task IDs:")
                for task_id in created_task_ids:
                    self.stdout.write(f"  • {task_id}")
        else:
            self.stdout.write("📝 No tasks created")
        
        # Queue analysis
        queue_analysis = result.get('queue_analysis', {})
        if queue_analysis:
            self.stdout.write("\n📊 QUEUE ANALYSIS")
            self.stdout.write("-" * 40)
            self.stdout.write(f"Total tasks: {queue_analysis.get('total_tasks', 0)}")
            self.stdout.write(f"Pending tasks: {queue_analysis.get('pending_count', 0)}")
            self.stdout.write(f"Active tasks: {queue_analysis.get('active_count', 0)}")
            self.stdout.write(f"Stale tasks: {queue_analysis.get('old_tasks_count', 0)}")
        
        # Underrepresented areas
        underrepresented = result.get('underrepresented_areas', [])
        if underrepresented:
            self.stdout.write("\n🔍 UNDERREPRESENTED AREAS")
            self.stdout.write("-" * 40)
            for area in underrepresented:
                self.stdout.write(f"  • {area}")
        
        # Growth task samples (for dry run)
        growth_samples = result.get('growth_task_samples', [])
        if growth_samples:
            self.stdout.write("\n🌱 POTENTIAL GROWTH TASKS")
            self.stdout.write("-" * 40)
            for task in growth_samples:
                self.stdout.write(f"  • {task['title']}")
                self.stdout.write(f"    Type: {task['type']}, Priority: {task['priority']}")
                self.stdout.write(f"    Growth Area: {task['growth_area']}")
        
        # Error reporting
        error = result.get('error')
        if error:
            self.stdout.write(f"\n❌ Error: {error}")
        
        self.stdout.write("\n" + "="*60)
    
    def _print_final_stats(self):
        """Print final statistics."""
        if self.stats['start_time']:
            duration = timezone.now() - self.stats['start_time']
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n--- Task Discovery Statistics ---\n'
                    f'Runtime: {duration}\n'
                    f'Discovery runs: {self.stats["discovery_runs"]}\n'
                    f'Tasks created: {self.stats["tasks_created"]}\n'
                    f'Errors: {self.stats["errors"]}'
                )
            )
        
        self.stdout.write(self.style.SUCCESS('Task discovery completed successfully'))