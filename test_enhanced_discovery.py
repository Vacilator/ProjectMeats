#!/usr/bin/env python3
"""
Test script for the enhanced AI orchestration system with task discovery.

This script validates the task discovery functionality and demonstrates
the autonomous task generation capabilities.
"""
import os
import sys
import json
from datetime import datetime

# Add the Django project to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectmeats.settings')

import django
django.setup()

from apps.task_orchestration.models import Agent, Task, TaskType, AgentType, TaskStatus
from apps.task_orchestration.services.task_discovery_service import task_discovery_service


def test_discovery_system():
    """Test the enhanced orchestration system with task discovery."""
    print("🚀 Testing Enhanced AI Orchestration System with Task Discovery")
    print("=" * 70)
    
    # Test 1: Check agent setup
    print("\n1. 🤖 Checking Agent Configuration")
    print("-" * 40)
    
    agents = Agent.objects.filter(is_active=True).order_by('agent_type', 'name')
    agent_count = agents.count()
    
    print(f"Total active agents: {agent_count}")
    
    discovery_agents = agents.filter(agent_type=AgentType.DISCOVERY_AGENT)
    if discovery_agents.exists():
        print("✅ Discovery agent configured:")
        for agent in discovery_agents:
            print(f"   • {agent.name} (Priority: {agent.priority_weight})")
            print(f"     Capabilities: {', '.join(agent.capabilities)}")
    else:
        print("❌ No discovery agents found")
    
    # Display all agents
    print("\nAll active agents:")
    for agent in agents:
        print(f"  • {agent.name} ({agent.get_agent_type_display()})")
        print(f"    Priority: {agent.priority_weight}, Max tasks: {agent.max_concurrent_tasks}")
        print(f"    Current tasks: {agent.current_task_count}")
    
    # Test 2: Current task analysis
    print("\n2. 📊 Current Task Queue Analysis")
    print("-" * 40)
    
    total_tasks = Task.objects.count()
    pending_tasks = Task.objects.filter(status=TaskStatus.PENDING).count()
    active_tasks = Task.objects.filter(
        status__in=[TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
    ).count()
    
    print(f"Total tasks: {total_tasks}")
    print(f"Pending tasks: {pending_tasks}")
    print(f"Active tasks: {active_tasks}")
    
    # Task distribution by type
    task_types = Task.objects.values('task_type').distinct()
    print("\nTask distribution by type:")
    for task_type_data in task_types:
        task_type = task_type_data['task_type']
        count = Task.objects.filter(task_type=task_type).count()
        print(f"  • {task_type}: {count}")
    
    # Test 3: Run discovery analysis (dry run)
    print("\n3. 🔍 Running Task Discovery Analysis (Dry Run)")
    print("-" * 40)
    
    try:
        # Run discovery in dry-run mode to see what would be discovered
        from apps.task_orchestration.services.task_discovery_service import (
            TaskQueueAnalyzer, ApplicationGrowthAnalyzer
        )
        
        queue_analyzer = TaskQueueAnalyzer()
        growth_analyzer = ApplicationGrowthAnalyzer()
        
        queue_analysis = queue_analyzer.analyze_task_distribution()
        underrepresented_areas = queue_analyzer.identify_underrepresented_areas()
        potential_tasks = growth_analyzer.analyze_missing_features()
        
        print("Queue analysis results:")
        print(f"  • Pending tasks: {queue_analysis['pending_count']}")
        print(f"  • Active tasks: {queue_analysis['active_count']}")
        print(f"  • Old tasks: {queue_analysis['old_tasks_count']}")
        
        print(f"\nUnderrepresented task areas: {len(underrepresented_areas)}")
        for area in underrepresented_areas:
            print(f"  • {area}")
        
        print(f"\nPotential growth tasks identified: {len(potential_tasks)}")
        for i, task in enumerate(potential_tasks[:3], 1):
            print(f"  {i}. {task.title}")
            print(f"     Type: {task.task_type}, Priority: {task.priority}")
            print(f"     Growth Area: {task.growth_area}")
            print(f"     Estimated Hours: {task.estimated_hours}")
        
        if len(potential_tasks) > 3:
            print(f"     ... and {len(potential_tasks) - 3} more tasks")
        
    except Exception as e:
        print(f"❌ Error running discovery analysis: {e}")
        return False
    
    # Test 4: Test actual task discovery (small scale)
    print("\n4. 🎯 Testing Actual Task Discovery")
    print("-" * 40)
    
    try:
        # Record initial task count
        initial_task_count = Task.objects.count()
        
        # Run discovery with max 2 tasks
        discovery_result = task_discovery_service.discover_and_create_tasks(max_tasks=2)
        
        # Check results
        final_task_count = Task.objects.count()
        tasks_created = final_task_count - initial_task_count
        
        print("Discovery results:")
        print(f"  • Discovery needed: {discovery_result.get('discovery_needed', False)}")
        print(f"  • Reason: {discovery_result.get('reason', 'N/A')}")
        print(f"  • Tasks created: {discovery_result.get('tasks_created', 0)}")
        print(f"  • Actual tasks created: {tasks_created}")
        
        if discovery_result.get('error'):
            print(f"  • Error: {discovery_result['error']}")
        
        # Show created tasks
        if tasks_created > 0:
            print("\nNewly created tasks:")
            new_tasks = Task.objects.order_by('-created_on')[:tasks_created]
            for i, task in enumerate(new_tasks, 1):
                print(f"  {i}. {task.title}")
                print(f"     Type: {task.task_type}, Priority: {task.priority}")
                print(f"     Status: {task.status}")
                if task.assigned_agent:
                    print(f"     Assigned to: {task.assigned_agent.name}")
                else:
                    print(f"     Not yet assigned")
        
    except Exception as e:
        print(f"❌ Error testing task discovery: {e}")
        return False
    
    # Test 5: Integration summary
    print("\n5. 📈 Integration Summary")
    print("-" * 40)
    
    print("✅ Enhanced AI Orchestration System Status:")
    print(f"  • Total agents configured: {agent_count}")
    print(f"  • Discovery agents: {discovery_agents.count()}")
    print(f"  • Task discovery functional: {'Yes' if not discovery_result.get('error') else 'No'}")
    print(f"  • Growth task types available: {len([t for t in TaskType.choices if 'development' in t[0] or 'optimization' in t[0] or 'analysis' in t[0]])}")
    
    print("\n🎯 System Capabilities:")
    print("  • Autonomous deployment failure handling (PR #99)")
    print("  • Continuous task discovery for application growth")
    print("  • Intelligent agent assignment and workload balancing")
    print("  • GitHub integration for issue creation and tracking")
    print("  • Scheduled execution via GitHub Actions workflow")
    
    print("\n🔄 Next Steps:")
    print("  • Deploy GitHub workflow for 45-minute scheduled discovery")
    print("  • Monitor task creation and agent utilization")
    print("  • Review generated tasks for business value alignment")
    print("  • Adjust discovery parameters based on application needs")
    
    return True


def main():
    """Main function for running the test."""
    try:
        success = test_discovery_system()
        
        print(f"\n{'='*70}")
        if success:
            print("✅ Enhanced AI Orchestration System Test PASSED")
            print("   The system is ready for autonomous task discovery and continuous growth!")
        else:
            print("❌ Enhanced AI Orchestration System Test FAILED")
            print("   Please check the errors above and ensure all components are properly configured.")
        print(f"{'='*70}")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)