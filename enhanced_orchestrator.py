#!/usr/bin/env python3
"""
Enhanced AI Deployment Orchestrator Integration.

This script enhances the existing AI deployment orchestrator with
complete task orchestration capabilities, automatic GitHub issue creation,
and autonomous error handling workflows.
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Add the Django project to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectmeats.settings')

import django
django.setup()

from apps.task_orchestration.services.orchestration_engine import orchestration_engine
from apps.task_orchestration.services.deployment_monitor import deployment_monitor
from apps.task_orchestration.models import Agent, Task, TaskType, TaskPriority, AgentType, AgentStatus


logger = logging.getLogger(__name__)


class EnhancedDeploymentOrchestrator:
    """
    Enhanced deployment orchestrator with complete AI task orchestration.
    
    Integrates with the existing AI deployment system to provide:
    - Automatic task creation for deployment failures
    - GitHub issue creation and management
    - Agent assignment and monitoring
    - Complete autonomous error handling
    """
    
    def __init__(self):
        self.logger = logger
        self.setup_default_agents()
    
    def setup_default_agents(self):
        """Set up default agents if they don't exist."""
        default_agents = [
            {
                'name': 'DeploymentAgent-Primary',
                'agent_type': AgentType.DEPLOYMENT_AGENT,
                'capabilities': [TaskType.DEPLOYMENT, TaskType.SYSTEM_MONITORING],
                'max_concurrent_tasks': 5,
                'priority_weight': 8.0,
                'configuration': {
                    'specialization': 'primary_deployment',
                    'handles_production': True,
                    'auto_recovery': True
                }
            },
            {
                'name': 'GitHubAgent-Issues',
                'agent_type': AgentType.GITHUB_AGENT,
                'capabilities': [TaskType.GITHUB_ISSUE, TaskType.BUG_FIX],
                'max_concurrent_tasks': 10,
                'priority_weight': 6.0,
                'configuration': {
                    'github_integration': True,
                    'issue_management': True,
                    'auto_assignment': True
                }
            },
            {
                'name': 'CodeAgent-Emergency',
                'agent_type': AgentType.CODE_AGENT,
                'capabilities': [TaskType.BUG_FIX, TaskType.CODE_REVIEW, TaskType.TESTING],
                'max_concurrent_tasks': 3,
                'priority_weight': 7.0,
                'configuration': {
                    'emergency_response': True,
                    'critical_fixes': True,
                    'rapid_deployment': True
                }
            },
            {
                'name': 'MonitoringAgent-System',
                'agent_type': AgentType.MONITORING_AGENT,
                'capabilities': [TaskType.SYSTEM_MONITORING, TaskType.DEPLOYMENT],
                'max_concurrent_tasks': 8,
                'priority_weight': 5.0,
                'configuration': {
                    'continuous_monitoring': True,
                    'health_checks': True,
                    'alert_management': True
                }
            },
            {
                'name': 'GeneralAgent-Backup',
                'agent_type': AgentType.GENERAL_AGENT,
                'capabilities': [TaskType.DEPLOYMENT, TaskType.BUG_FIX, TaskType.GITHUB_ISSUE],
                'max_concurrent_tasks': 4,
                'priority_weight': 4.0,
                'configuration': {
                    'backup_support': True,
                    'overflow_handling': True,
                    'general_purpose': True
                }
            }
        ]
        
        for agent_data in default_agents:
            agent, created = Agent.objects.get_or_create(
                name=agent_data['name'],
                defaults={
                    'agent_type': agent_data['agent_type'],
                    'capabilities': agent_data['capabilities'],
                    'max_concurrent_tasks': agent_data['max_concurrent_tasks'],
                    'priority_weight': agent_data['priority_weight'],
                    'configuration': agent_data['configuration'],
                    'status': AgentStatus.AVAILABLE,
                    'is_active': True
                }
            )
            
            if created:
                self.logger.info(f"Created default agent: {agent.name}")
            else:
                # Update existing agent configuration
                agent.capabilities = agent_data['capabilities']
                agent.configuration.update(agent_data['configuration'])
                agent.save()
    
    def handle_deployment_failure(self, deployment_data: Dict[str, Any]) -> Optional[Task]:
        """
        Handle a deployment failure with complete orchestration.
        
        This method is called when a deployment fails and creates all necessary
        tasks and GitHub issues for autonomous recovery.
        """
        try:
            deployment_id = deployment_data.get('deployment_id', f"deploy_{int(datetime.now().timestamp())}")
            
            self.logger.critical(f"Handling deployment failure: {deployment_id}")
            
            # Extract error information
            error_details = {
                'error_message': deployment_data.get('error_message', 'Deployment failed'),
                'failed_step': deployment_data.get('failed_step', 'Unknown'),
                'exit_code': deployment_data.get('exit_code', -1),
                'duration': deployment_data.get('duration', 'Unknown'),
                'logs': deployment_data.get('logs', []),
                'timestamp': datetime.now().isoformat(),
                'severity': self._determine_severity(deployment_data),
                'source': 'enhanced_deployment_orchestrator'
            }
            
            # Extract server information
            server_info = {
                'hostname': deployment_data.get('server', deployment_data.get('hostname', 'Unknown')),
                'domain': deployment_data.get('domain', 'Unknown'),
                'deployment_method': 'Enhanced AI Deployment Orchestrator',
                'git_branch': deployment_data.get('git_branch', 'main'),
                'git_commit': deployment_data.get('git_commit', 'Unknown'),
                'user': deployment_data.get('user', 'root'),
                'python_version': deployment_data.get('python_version', 'Unknown'),
                'node_version': deployment_data.get('node_version', 'Unknown'),
                'nginx_status': deployment_data.get('nginx_status', 'Unknown'),
                'postgresql_status': deployment_data.get('postgresql_status', 'Unknown'),
            }
            
            # Create orchestration task
            task = orchestration_engine.create_task_from_production_failure(
                deployment_id=deployment_id,
                error_details=error_details,
                server_info=server_info
            )
            
            # Log the event
            self._log_orchestration_event(deployment_id, task.id, error_details, server_info)
            
            self.logger.info(f"Created orchestration task {task.id} for deployment failure {deployment_id}")
            
            return task
            
        except Exception as e:
            self.logger.error(f"Failed to handle deployment failure: {e}")
            return None
    
    def _determine_severity(self, deployment_data: Dict[str, Any]) -> str:
        """Determine the severity of a deployment failure."""
        error_message = deployment_data.get('error_message', '').lower()
        failed_step = deployment_data.get('failed_step', '').lower()
        exit_code = deployment_data.get('exit_code', 0)
        
        # Critical failures
        if any(keyword in error_message or keyword in failed_step for keyword in [
            'database', 'production', 'critical', 'service unavailable', 'nginx error'
        ]):
            return 'critical'
        
        # High severity failures
        if exit_code != 0 or any(keyword in error_message or keyword in failed_step for keyword in [
            'build failed', 'deployment failed', 'configuration error'
        ]):
            return 'high'
        
        # Medium severity by default
        return 'medium'
    
    def _log_orchestration_event(self, deployment_id: str, task_id: str, error_details: Dict, server_info: Dict):
        """Log orchestration event for tracking and analysis."""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'deployment_failure_orchestration',
                'deployment_id': deployment_id,
                'task_id': str(task_id),  # Convert UUID to string
                'server': server_info.get('hostname'),
                'domain': server_info.get('domain'),
                'severity': error_details.get('severity'),
                'error_message': error_details.get('error_message'),
                'failed_step': error_details.get('failed_step'),
                'orchestrator_version': '2.0.0'
            }
            
            # Log to orchestration events file
            log_file_path = os.path.join(project_root, 'orchestration_events.json')
            
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'events': []}
            
            log_data['events'].append(log_entry)
            
            # Keep only recent events (last 1000)
            if len(log_data['events']) > 1000:
                log_data['events'] = log_data['events'][-1000:]
            
            with open(log_file_path, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to log orchestration event: {e}")
    
    def monitor_and_respond(self) -> Dict[str, Any]:
        """
        Monitor deployment status and respond to issues autonomously.
        
        This method should be called periodically to check for deployment
        failures and trigger appropriate orchestration responses.
        """
        try:
            # Check for deployment failures
            created_tasks = deployment_monitor.monitor_deployment_status()
            
            # Process any pending tasks
            assigned_count = orchestration_engine.process_pending_tasks()
            
            # Get system status
            status = orchestration_engine.get_orchestration_status()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'new_failure_tasks': len(created_tasks),
                'tasks_assigned': assigned_count,
                'system_status': status,
                'monitoring_active': True
            }
            
        except Exception as e:
            self.logger.error(f"Error in monitoring and response: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'monitoring_active': False
            }
    
    def get_deployment_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive status of deployment orchestration."""
        try:
            # Get orchestration status
            orchestration_status = orchestration_engine.get_orchestration_status()
            
            # Get recent deployment failures
            recent_failures = deployment_monitor.get_recent_deployment_failures(hours=24)
            
            # Get agent status
            agents = Agent.objects.filter(is_active=True)
            agent_status = []
            
            for agent in agents:
                agent_status.append({
                    'name': agent.name,
                    'type': agent.agent_type,
                    'status': agent.status,
                    'current_tasks': agent.current_task_count,
                    'max_tasks': agent.max_concurrent_tasks,
                    'success_rate': agent.success_rate,
                    'efficiency': agent.efficiency_score
                })
            
            return {
                'timestamp': datetime.now().isoformat(),
                'orchestration': orchestration_status,
                'recent_failures_24h': len(recent_failures),
                'agents': agent_status,
                'version': '2.0.0',
                'integration_active': True
            }
            
        except Exception as e:
            self.logger.error(f"Error getting orchestration status: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'integration_active': False
            }


def main():
    """Main function for running the enhanced deployment orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced AI Deployment Orchestrator')
    parser.add_argument('--setup', action='store_true', help='Set up default agents')
    parser.add_argument('--monitor', action='store_true', help='Run monitoring cycle')
    parser.add_argument('--status', action='store_true', help='Get orchestration status')
    parser.add_argument('--test-failure', help='Test failure handling with deployment ID')
    
    args = parser.parse_args()
    
    orchestrator = EnhancedDeploymentOrchestrator()
    
    if args.setup:
        print("✅ Setting up default agents...")
        orchestrator.setup_default_agents()
        print("✅ Default agents configured")
    
    elif args.monitor:
        print("🔍 Running monitoring cycle...")
        result = orchestrator.monitor_and_respond()
        print(f"✅ Monitoring complete: {json.dumps(result, indent=2)}")
    
    elif args.status:
        print("📊 Getting orchestration status...")
        status = orchestrator.get_deployment_orchestration_status()
        print(json.dumps(status, indent=2))
    
    elif args.test_failure:
        print(f"🧪 Testing failure handling for deployment: {args.test_failure}")
        test_data = {
            'deployment_id': args.test_failure,
            'error_message': 'Test deployment failure for orchestration testing',
            'failed_step': 'test_step',
            'server': 'test.projectmeats.com',
            'domain': 'test.projectmeats.com',
            'exit_code': 1
        }
        task = orchestrator.handle_deployment_failure(test_data)
        if task:
            print(f"✅ Created test task: {task.id}")
        else:
            print("❌ Failed to create test task")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()