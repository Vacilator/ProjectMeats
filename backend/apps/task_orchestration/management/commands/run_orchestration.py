"""
Django management command to run the AI Orchestration Engine.

This command provides continuous orchestration of tasks, agent management,
deployment monitoring, and autonomous error handling.
"""
import time
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from apps.task_orchestration.services.orchestration_engine import orchestration_engine
from apps.task_orchestration.services.deployment_monitor import deployment_monitor
from apps.task_orchestration.models import (
    Task, Agent, TaskStatus, AgentStatus, SystemHealth
)


class Command(BaseCommand):
    """
    AI Orchestration Engine management command.
    
    Runs the complete orchestration system including:
    - Task assignment and monitoring
    - Deployment failure detection
    - Agent health monitoring
    - Automatic GitHub issue creation
    - System health tracking
    """
    
    help = 'Run the AI Orchestration Engine for autonomous task management'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.should_stop = False
        self.stats = {
            'start_time': None,
            'tasks_processed': 0,
            'failures_handled': 0,
            'issues_created': 0,
            'agents_monitored': 0,
        }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Interval in seconds between orchestration cycles (default: 30)'
        )
        
        parser.add_argument(
            '--deployment-check-interval',
            type=int,
            default=60,
            help='Interval in seconds between deployment failure checks (default: 60)'
        )
        
        parser.add_argument(
            '--health-check-interval',
            type=int,
            default=300,
            help='Interval in seconds between system health checks (default: 300)'
        )
        
        parser.add_argument(
            '--max-cycles',
            type=int,
            default=0,
            help='Maximum number of cycles to run (0 = unlimited, default: 0)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run in dry-run mode (no actual changes)'
        )
    
    def handle(self, *args, **options):
        """Main orchestration loop."""
        self.setup_signal_handlers()
        self.stats['start_time'] = timezone.now()
        
        interval = options['interval']
        deployment_check_interval = options['deployment_check_interval']
        health_check_interval = options['health_check_interval']
        max_cycles = options['max_cycles']
        verbose = options['verbose']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Running in DRY-RUN mode - no changes will be made')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting AI Orchestration Engine\n'
                f'Task processing interval: {interval}s\n'
                f'Deployment monitoring interval: {deployment_check_interval}s\n'
                f'Health check interval: {health_check_interval}s\n'
                f'Max cycles: {max_cycles if max_cycles > 0 else "unlimited"}\n'
                f'Verbose: {verbose}\n'
                f'Dry-run: {dry_run}'
            )
        )
        
        cycle_count = 0
        last_deployment_check = timezone.now()
        last_health_check = timezone.now()
        
        try:
            while not self.should_stop:
                cycle_start = timezone.now()
                cycle_count += 1
                
                if verbose:
                    self.stdout.write(f'\n--- Orchestration Cycle {cycle_count} at {cycle_start} ---')
                
                # Run main orchestration tasks
                self.run_orchestration_cycle(verbose=verbose, dry_run=dry_run)
                
                # Check for deployment failures
                if (cycle_start - last_deployment_check).total_seconds() >= deployment_check_interval:
                    self.check_deployment_failures(verbose=verbose, dry_run=dry_run)
                    last_deployment_check = cycle_start
                
                # Run system health checks
                if (cycle_start - last_health_check).total_seconds() >= health_check_interval:
                    self.run_health_checks(verbose=verbose, dry_run=dry_run)
                    last_health_check = cycle_start
                
                # Check if we've reached max cycles
                if max_cycles > 0 and cycle_count >= max_cycles:
                    self.stdout.write(
                        self.style.SUCCESS(f'Reached maximum cycles ({max_cycles}), stopping')
                    )
                    break
                
                # Calculate sleep time
                cycle_duration = (timezone.now() - cycle_start).total_seconds()
                sleep_time = max(0, interval - cycle_duration)
                
                if verbose and sleep_time > 0:
                    self.stdout.write(f'Cycle completed in {cycle_duration:.1f}s, sleeping {sleep_time:.1f}s')
                
                # Sleep until next cycle
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nReceived interrupt signal, shutting down...'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Orchestration engine error: {e}'))
            raise
        finally:
            self.print_final_stats()
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.stdout.write(self.style.WARNING(f'\nReceived signal {signum}, initiating shutdown...'))
            self.should_stop = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run_orchestration_cycle(self, verbose: bool = False, dry_run: bool = False):
        """Run a single orchestration cycle."""
        try:
            # Process pending tasks
            if not dry_run:
                assigned_count = orchestration_engine.process_pending_tasks()
                self.stats['tasks_processed'] += assigned_count
                
                if verbose and assigned_count > 0:
                    self.stdout.write(f'  ✓ Assigned {assigned_count} pending tasks')
            
            # Check for failed tasks that need retry/escalation
            failed_tasks = Task.objects.filter(
                status=TaskStatus.FAILED,
                modified_on__gte=timezone.now() - timedelta(hours=1)
            )
            
            for task in failed_tasks:
                if task.can_retry() or task.should_escalate():
                    if verbose:
                        self.stdout.write(f'  ⚠ Processing failed task: {task.title}')
                    
                    if not dry_run:
                        orchestration_engine.handle_task_failure(task, task.error_details or 'Task failure detected')
                        self.stats['failures_handled'] += 1
            
            # Monitor agent health
            self.monitor_agent_health(verbose=verbose, dry_run=dry_run)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in orchestration cycle: {e}'))
    
    def check_deployment_failures(self, verbose: bool = False, dry_run: bool = False):
        """Check for deployment failures and handle them."""
        try:
            if verbose:
                self.stdout.write('  🔍 Checking for deployment failures...')
            
            if not dry_run:
                created_tasks = deployment_monitor.monitor_deployment_status()
                
                if created_tasks:
                    self.stats['failures_handled'] += len(created_tasks)
                    if verbose:
                        self.stdout.write(f'  🚨 Created {len(created_tasks)} tasks for deployment failures')
                        for task in created_tasks:
                            self.stdout.write(f'    - {task.title} (Priority: {task.priority})')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error checking deployment failures: {e}'))
    
    def monitor_agent_health(self, verbose: bool = False, dry_run: bool = False):
        """Monitor the health of all agents."""
        try:
            agents = Agent.objects.filter(is_active=True)
            
            for agent in agents:
                # Check if agent has been idle too long
                if agent.status == AgentStatus.BUSY:
                    # Check if any of the agent's tasks are actually running
                    active_tasks = agent.assigned_tasks.filter(
                        status__in=[TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
                    )
                    
                    if not active_tasks.exists():
                        if verbose:
                            self.stdout.write(f'  🔧 Agent {agent.name} marked as busy but has no active tasks')
                        
                        if not dry_run:
                            agent.status = AgentStatus.AVAILABLE
                            agent.save()
                
                # Check for agents that haven't reported heartbeat recently
                heartbeat_threshold = timezone.now() - timedelta(minutes=10)
                if agent.last_heartbeat < heartbeat_threshold and agent.status != AgentStatus.OFFLINE:
                    if verbose:
                        self.stdout.write(f'  ⚠ Agent {agent.name} heartbeat is stale, marking offline')
                    
                    if not dry_run:
                        agent.status = AgentStatus.OFFLINE
                        agent.save()
                
                self.stats['agents_monitored'] += 1
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error monitoring agent health: {e}'))
    
    def run_health_checks(self, verbose: bool = False, dry_run: bool = False):
        """Run comprehensive system health checks."""
        try:
            if verbose:
                self.stdout.write('  🏥 Running system health checks...')
            
            health_data = []
            
            # Check task queue health
            pending_tasks = Task.objects.filter(status=TaskStatus.PENDING).count()
            failed_tasks = Task.objects.filter(
                status=TaskStatus.FAILED,
                modified_on__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            task_queue_status = 'healthy'
            if pending_tasks > 50:
                task_queue_status = 'warning'
            if pending_tasks > 100:
                task_queue_status = 'critical'
            
            health_data.append({
                'component': 'task_queue',
                'metric_name': 'pending_tasks',
                'metric_value': {'count': pending_tasks, 'failed_1h': failed_tasks},
                'status': task_queue_status
            })
            
            # Check agent availability
            available_agents = Agent.objects.filter(
                is_active=True,
                status=AgentStatus.AVAILABLE
            ).count()
            
            total_agents = Agent.objects.filter(is_active=True).count()
            
            agent_status = 'healthy'
            if total_agents == 0:
                agent_status = 'critical'
            elif available_agents / total_agents < 0.3:
                agent_status = 'warning'
            
            health_data.append({
                'component': 'agents',
                'metric_name': 'availability',
                'metric_value': {'available': available_agents, 'total': total_agents},
                'status': agent_status
            })
            
            # Save health data
            if not dry_run:
                for health_item in health_data:
                    SystemHealth.objects.update_or_create(
                        component=health_item['component'],
                        metric_name=health_item['metric_name'],
                        defaults={
                            'metric_value': health_item['metric_value'],
                            'status': health_item['status'],
                        }
                    )
            
            if verbose:
                for health_item in health_data:
                    status_color = self.style.SUCCESS if health_item['status'] == 'healthy' else (
                        self.style.WARNING if health_item['status'] == 'warning' else self.style.ERROR
                    )
                    self.stdout.write(f"    {health_item['component']}.{health_item['metric_name']}: " + 
                                    status_color(health_item['status']))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running health checks: {e}'))
    
    def print_final_stats(self):
        """Print final statistics when shutting down."""
        if self.stats['start_time']:
            duration = timezone.now() - self.stats['start_time']
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n--- Orchestration Engine Statistics ---\n'
                    f'Runtime: {duration}\n'
                    f'Tasks processed: {self.stats["tasks_processed"]}\n'
                    f'Failures handled: {self.stats["failures_handled"]}\n'
                    f'Agents monitored: {self.stats["agents_monitored"]}\n'
                    f'Average tasks/minute: {self.stats["tasks_processed"] / max(1, duration.total_seconds() / 60):.1f}'
                )
            )
        
        self.stdout.write(self.style.SUCCESS('Orchestration Engine shutdown complete'))