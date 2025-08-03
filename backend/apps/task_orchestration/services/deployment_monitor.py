"""
Production Deployment Monitor for AI Orchestration.

This service monitors production deployments and automatically creates
tasks and GitHub issues when deployments fail, providing complete
autonomous error handling and recovery workflows.
"""
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from django.utils import timezone
from django.conf import settings

from ..models import Task, TaskType, TaskPriority
from .orchestration_engine import orchestration_engine


logger = logging.getLogger(__name__)


@dataclass
class DeploymentError:
    """Represents a deployment error that needs orchestration."""
    deployment_id: str
    error_message: str
    failed_step: str
    server_info: Dict[str, Any]
    timestamp: datetime
    severity: str
    recovery_suggestions: List[str]


class ProductionDeploymentMonitor:
    """
    Monitor for production deployment failures.
    
    Integrates with the existing AI deployment orchestrator to automatically
    detect failures and create appropriate tasks and GitHub issues for
    immediate resolution.
    """
    
    def __init__(self):
        self.logger = logger
        self.deployment_log_path = self._get_deployment_log_path()
        self.last_check_time = timezone.now()
        
    def _get_deployment_log_path(self) -> str:
        """Get the path to the deployment log file."""
        # Use configurable path from Django settings if available
        deployment_log_path = getattr(settings, "DEPLOYMENT_LOG_PATH", None)
        if deployment_log_path and os.path.exists(deployment_log_path):
            return deployment_log_path

        # Fallback to common locations
        possible_paths = [
            os.path.join(settings.BASE_DIR.parent, "deployment_log.json"),
            "deployment_log.json",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        # Default to the root project path
        return os.path.join(settings.BASE_DIR.parent, "deployment_log.json")
    
    def monitor_deployment_status(self) -> List[Task]:
        """
        Monitor deployment status and create tasks for any failures.
        
        This method should be called periodically (e.g., every minute)
        to check for new deployment failures and automatically create
        orchestration tasks.
        """
        try:
            deployment_errors = self._check_for_deployment_failures()
            created_tasks = []
            
            for error in deployment_errors:
                try:
                    task = self._handle_deployment_failure(error)
                    if task:
                        created_tasks.append(task)
                except Exception as e:
                    self.logger.error(f"Failed to handle deployment error {error.deployment_id}: {e}")
            
            if created_tasks:
                self.logger.info(f"Created {len(created_tasks)} tasks for deployment failures")
            
            return created_tasks
            
        except Exception as e:
            self.logger.error(f"Error monitoring deployment status: {e}")
            return []
    
    def _check_for_deployment_failures(self) -> List[DeploymentError]:
        """Check deployment logs for new failures since last check."""
        if not os.path.exists(self.deployment_log_path):
            self.logger.debug(f"Deployment log not found at {self.deployment_log_path}")
            return []
        
        try:
            with open(self.deployment_log_path, 'r') as f:
                log_data = json.load(f)
            
            errors = []
            deployment_entries = log_data.get('deployments', [])
            
            for entry in deployment_entries:
                # Check if this is a failure that occurred after our last check
                entry_time = self._parse_timestamp(entry.get('timestamp'))
                if entry_time and entry_time > self.last_check_time:
                    if self._is_deployment_failure(entry):
                        error = self._create_deployment_error(entry)
                        if error:
                            errors.append(error)
            
            # Update last check time
            self.last_check_time = timezone.now()
            
            return errors
            
        except Exception as e:
            self.logger.error(f"Error reading deployment log: {e}")
            return []
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object."""
        if not timestamp_str:
            return None
        
        try:
            # Try various timestamp formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    # Make timezone aware
                    if dt.tzinfo is None:
                        dt = timezone.make_aware(dt)
                    return dt
                except ValueError:
                    continue
            
            self.logger.warning(f"Could not parse timestamp: {timestamp_str}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing timestamp {timestamp_str}: {e}")
            return None
    
    def _is_deployment_failure(self, entry: Dict) -> bool:
        """Check if a deployment log entry represents a failure."""
        status = entry.get('status', '').lower()
        success = entry.get('success', None)
        error_message = entry.get('error_message', '')
        exit_code = entry.get('exit_code', 0)
        
        # Check for explicit failure indicators
        if status in ['failed', 'error', 'failure']:
            return True
        
        if success is False:
            return True
        
        if exit_code != 0:
            return True
        
        if error_message and any(keyword in error_message.lower() for keyword in [
            'error', 'failed', 'failure', 'exception', 'timeout', 'connection refused'
        ]):
            return True
        
        # Check for specific deployment failure patterns
        logs = entry.get('logs', [])
        for log_entry in logs:
            log_message = log_entry.get('message', '').lower()
            if any(pattern in log_message for pattern in [
                'deployment failed',
                'build failed',
                'connection error',
                'timeout',
                'permission denied',
                'command not found',
                'no such file',
                'cannot connect'
            ]):
                return True
        
        return False
    
    def _create_deployment_error(self, entry: Dict) -> Optional[DeploymentError]:
        """Create a DeploymentError object from a log entry."""
        try:
            deployment_id = entry.get('deployment_id') or entry.get('id') or f"deploy_{int(timezone.now().timestamp())}"
            
            # Extract error message
            error_message = entry.get('error_message', '')
            if not error_message:
                # Try to extract from logs
                logs = entry.get('logs', [])
                error_logs = [log for log in logs if log.get('level', '').upper() in ['ERROR', 'CRITICAL']]
                if error_logs:
                    error_message = error_logs[-1].get('message', 'Deployment failed')
                else:
                    error_message = 'Deployment failed - see logs for details'
            
            # Extract failed step
            failed_step = entry.get('failed_step', entry.get('current_step', 'Unknown'))
            
            # Extract server information
            server_info = {
                'hostname': entry.get('server', entry.get('hostname', 'Unknown')),
                'domain': entry.get('domain', 'Unknown'),
                'deployment_method': entry.get('deployment_method', 'AI Deployment Orchestrator'),
                'git_branch': entry.get('git_branch', 'main'),
                'git_commit': entry.get('git_commit', 'Unknown'),
                'user': entry.get('user', 'root'),
                'exit_code': entry.get('exit_code', -1),
                'duration': entry.get('duration', 'Unknown'),
            }
            
            # Determine severity
            severity = self._determine_severity(entry)
            
            # Generate recovery suggestions
            recovery_suggestions = self._generate_recovery_suggestions(entry)
            
            timestamp = self._parse_timestamp(entry.get('timestamp')) or timezone.now()
            
            return DeploymentError(
                deployment_id=deployment_id,
                error_message=error_message,
                failed_step=failed_step,
                server_info=server_info,
                timestamp=timestamp,
                severity=severity,
                recovery_suggestions=recovery_suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Error creating deployment error from entry: {e}")
            return None
    
    def _determine_severity(self, entry: Dict) -> str:
        """Determine the severity of a deployment failure."""
        error_message = entry.get('error_message', '').lower()
        failed_step = entry.get('failed_step', '').lower()
        
        # Critical failures that affect production immediately
        if any(keyword in error_message or keyword in failed_step for keyword in [
            'database', 'production', 'live', 'critical', 'service unavailable'
        ]):
            return 'critical'
        
        # High priority failures
        if any(keyword in error_message or keyword in failed_step for keyword in [
            'deployment', 'build', 'configuration', 'permission'
        ]):
            return 'high'
        
        # Medium priority by default
        return 'medium'
    
    def _generate_recovery_suggestions(self, entry: Dict) -> List[str]:
        """Generate recovery suggestions based on the failure type."""
        suggestions = []
        error_message = entry.get('error_message', '').lower()
        failed_step = entry.get('failed_step', '').lower()
        
        # Connection-related issues
        if any(keyword in error_message for keyword in ['connection', 'ssh', 'timeout']):
            suggestions.extend([
                "Check server connectivity and SSH access",
                "Verify server is running and accessible",
                "Check firewall settings and network configuration"
            ])
        
        # Permission issues
        if any(keyword in error_message for keyword in ['permission', 'denied', 'unauthorized']):
            suggestions.extend([
                "Check file and directory permissions",
                "Verify user has necessary sudo privileges",
                "Check SSH key authentication"
            ])
        
        # Database issues
        if 'database' in error_message or 'database' in failed_step:
            suggestions.extend([
                "Check database connectivity and status",
                "Verify database credentials and permissions",
                "Check for pending migrations"
            ])
        
        # Build/dependency issues
        if any(keyword in error_message for keyword in ['build', 'dependency', 'package', 'npm', 'pip']):
            suggestions.extend([
                "Check for missing dependencies",
                "Verify package manager configuration",
                "Clear package caches and retry installation"
            ])
        
        # Configuration issues
        if any(keyword in error_message for keyword in ['config', 'environment', 'variable']):
            suggestions.extend([
                "Verify environment variables and configuration",
                "Check configuration file syntax and values",
                "Ensure all required settings are present"
            ])
        
        # Generic suggestions if no specific patterns found
        if not suggestions:
            suggestions.extend([
                "Review deployment logs for specific error details",
                "Check server resources (disk space, memory, CPU)",
                "Verify all services are running properly",
                "Consider manual deployment verification"
            ])
        
        return suggestions
    
    def _handle_deployment_failure(self, error: DeploymentError) -> Optional[Task]:
        """
        Handle a deployment failure by creating appropriate orchestration tasks.
        
        This integrates with the orchestration engine to create emergency tasks
        that will be automatically assigned to the best available agents.
        """
        self.logger.critical(f"Handling deployment failure: {error.deployment_id}")
        
        try:
            # Check if we already have a task for this deployment
            existing_task = Task.objects.filter(
                input_data__deployment_id=error.deployment_id
            ).first()
            
            if existing_task:
                self.logger.info(f"Task already exists for deployment {error.deployment_id}: {existing_task.id}")
                return existing_task
            
            # Prepare error details for the orchestration engine
            error_details = {
                'error_message': error.error_message,
                'failed_step': error.failed_step,
                'severity': error.severity,
                'recovery_suggestions': error.recovery_suggestions,
                'timestamp': error.timestamp.isoformat(),
                'source': 'production_deployment_monitor'
            }
            
            # Create task through orchestration engine
            task = orchestration_engine.create_task_from_production_failure(
                deployment_id=error.deployment_id,
                error_details=error_details,
                server_info=error.server_info
            )
            
            self.logger.info(f"Created orchestration task {task.id} for deployment failure {error.deployment_id}")
            
            # Log the deployment failure for monitoring
            self._log_deployment_failure_handled(error, task)
            
            return task
            
        except Exception as e:
            self.logger.error(f"Failed to handle deployment failure {error.deployment_id}: {e}")
            return None
    
    def _log_deployment_failure_handled(self, error: DeploymentError, task: Task):
        """Log that a deployment failure has been handled."""
        try:
            log_entry = {
                'timestamp': timezone.now().isoformat(),
                'deployment_id': error.deployment_id,
                'task_id': str(task.id),
                'severity': error.severity,
                'handled_by': 'production_deployment_monitor',
                'server': error.server_info.get('hostname'),
                'domain': error.server_info.get('domain'),
            }
            
            # Append to deployment handling log
            log_file_path = os.path.join(
                os.path.dirname(self.deployment_log_path),
                'deployment_failures_handled.json'
            )
            
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'handled_failures': []}
            
            log_data['handled_failures'].append(log_entry)
            
            # Keep only recent entries (last 1000)
            if len(log_data['handled_failures']) > 1000:
                log_data['handled_failures'] = log_data['handled_failures'][-1000:]
            
            with open(log_file_path, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to log deployment failure handling: {e}")
    
    def get_recent_deployment_failures(self, hours: int = 24) -> List[Dict]:
        """Get recent deployment failures for monitoring dashboard."""
        try:
            log_file_path = os.path.join(
                os.path.dirname(self.deployment_log_path),
                'deployment_failures_handled.json'
            )
            
            if not os.path.exists(log_file_path):
                return []
            
            with open(log_file_path, 'r') as f:
                log_data = json.load(f)
            
            cutoff_time = timezone.now() - timedelta(hours=hours)
            recent_failures = []
            
            for entry in log_data.get('handled_failures', []):
                entry_time = self._parse_timestamp(entry.get('timestamp'))
                if entry_time and entry_time > cutoff_time:
                    recent_failures.append(entry)
            
            return recent_failures
            
        except Exception as e:
            self.logger.error(f"Error getting recent deployment failures: {e}")
            return []


# Global deployment monitor instance
deployment_monitor = ProductionDeploymentMonitor()