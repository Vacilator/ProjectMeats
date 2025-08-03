# AI Task Discovery System Documentation

## Overview

The AI Task Discovery System extends the ProjectMeats AI Orchestration System (PR #99) with autonomous task discovery capabilities. This system ensures continuous application growth by analyzing the current state and automatically generating new development tasks every 30-60 minutes.

## Architecture

### Core Components

#### 1. TaskDiscoveryService
**Location**: `backend/apps/task_orchestration/services/task_discovery_service.py`

Main service responsible for:
- Analyzing current task queue state
- Identifying gaps in development coverage
- Generating new tasks for application growth
- Integrating with existing orchestration engine

Key classes:
- `TaskDiscoveryService`: Main orchestration logic
- `ApplicationGrowthAnalyzer`: Business domain analysis
- `TaskQueueAnalyzer`: Current queue analysis
- `DiscoveryTask`: Task template for generation

#### 2. Discovery Management Command
**Location**: `backend/apps/task_orchestration/management/commands/discover_tasks.py`

Django management command for scheduled execution:
- Command: `python manage.py discover_tasks`
- Supports dry-run analysis, force discovery, and verbose output
- JSON and text output formats
- Configurable task limits and parameters

#### 3. GitHub Workflow
**Location**: `.github/workflows/ai-task-discovery.yml`

Automated scheduling via GitHub Actions:
- Runs every 45 minutes via cron schedule
- Manual trigger with configurable parameters
- Full database setup and agent initialization
- Comprehensive logging and artifact uploads

#### 4. Discovery Agent
**Type**: `DISCOVERY_AGENT`
**Name**: `DiscoveryAgent-Growth`

Specialized AI agent for task discovery:
- Priority weight: 9.0 (highest priority)
- Capabilities: Task discovery, application analysis, feature development
- Configuration: Autonomous discovery enabled, business value focused

## Business Growth Priorities

### ProjectMeats Domain Focus

The system focuses on the core business domain of meat sales broker management:

#### Critical Business Areas
1. **Supplier Management**
   - Supplier profile enhancements
   - Performance analytics
   - Automated communications

2. **Customer Management**
   - Order history improvements
   - Credit management features
   - Relationship tracking

3. **Purchase Orders**
   - Lifecycle management
   - Approval workflows
   - Tracking and notifications

4. **Accounts Receivable**
   - Financial management
   - Billing automation
   - Aging reports

#### Enhancement Areas
5. **Reporting & Analytics**
   - Executive dashboards
   - Custom report builders
   - Business intelligence

6. **Performance Optimization**
   - Database query optimization
   - API caching strategies
   - Response time improvements

7. **User Experience**
   - Mobile optimization
   - UI/UX improvements
   - Accessibility features

8. **Security & Compliance**
   - Audit logging
   - Authentication enhancements
   - Compliance features

## Task Types

### New Task Types Added

- `TASK_DISCOVERY`: Analysis and discovery tasks
- `APPLICATION_ANALYSIS`: Application state analysis
- `PERFORMANCE_OPTIMIZATION`: Performance improvement tasks
- `SECURITY_ENHANCEMENT`: Security improvement tasks
- `USER_EXPERIENCE_IMPROVEMENT`: UX enhancement tasks

### Agent Type Added

- `DISCOVERY_AGENT`: Specialized agent for autonomous task discovery

## Usage

### Command Line Interface

```bash
# Basic discovery run
python manage.py discover_tasks

# Dry run analysis (no task creation)
python manage.py discover_tasks --dry-run --verbose

# Force discovery with custom limits
python manage.py discover_tasks --force --max-tasks=5

# JSON output for automation
python manage.py discover_tasks --report-format=json
```

### Parameters

- `--max-tasks`: Maximum number of tasks to create (default: 3)
- `--dry-run`: Analyze without creating tasks
- `--force`: Force discovery even if recent tasks exist
- `--verbose`: Enable detailed logging
- `--report-format`: Output format (text or json)

### GitHub Workflow

#### Automatic Execution
- Runs every 45 minutes automatically
- Uses PostgreSQL database for testing
- Initializes full orchestration system
- Validates task creation and assignment

#### Manual Trigger
1. Go to GitHub Actions → "AI Task Discovery Agent"
2. Click "Run workflow"
3. Configure parameters:
   - Max tasks (1-10)
   - Force discovery (true/false)
   - Dry run (true/false)

## Integration Points

### With Existing System

The discovery system seamlessly integrates with PR #99:

1. **Extends Agent System**: Adds 6th agent type without disrupting existing 5 agents
2. **Uses Existing Models**: Leverages existing Task and Agent models
3. **Follows Patterns**: Uses same service and command patterns
4. **Preserves Functionality**: All existing error handling and deployment monitoring continues

### With Business Operations

1. **PowerApps Migration**: Tracks completion of PowerApps to Django migration
2. **Business Modules**: Analyzes core business functionality gaps
3. **User Workflows**: Identifies user experience improvement opportunities
4. **Performance Needs**: Detects performance optimization requirements

## Discovery Logic

### When Discovery Runs

Discovery runs when:
- Pending task count < 3
- Active task count < 2
- Stale tasks exist (> 7 days old)
- Total task count < 5
- No discovery run in last 2 hours (periodic growth)

### Task Generation Strategy

1. **Queue Analysis**: Identify underrepresented task types
2. **Growth Analysis**: Analyze business area completeness
3. **Priority Mapping**: Map business priorities to task priorities
4. **Task Creation**: Generate contextual improvement tasks
5. **Assignment**: Integrate with existing agent assignment logic

### Business Value Focus

Tasks are prioritized by business value:
1. Critical business functionality (HIGH priority)
2. User experience improvements (MEDIUM priority)  
3. Performance optimizations (MEDIUM priority)
4. Security enhancements (HIGH priority)
5. Maintainability improvements (LOW priority)
6. Innovation features (LOW priority)

## Monitoring and Observability

### Logging

The system provides comprehensive logging:
- Discovery analysis results
- Task creation details
- Agent assignment outcomes
- Error conditions and recovery

### Metrics

Key metrics tracked:
- Discovery runs per day
- Tasks created per discovery run
- Business area coverage
- Agent utilization rates
- Task completion times

### Artifacts

GitHub workflow uploads:
- Discovery results JSON
- Agent status reports
- Task creation logs
- System health metrics

## Configuration

### Environment Variables

```bash
# Standard Django configuration
DJANGO_SETTINGS_MODULE=projectmeats.settings
DATABASE_URL=postgresql://...

# Optional GitHub integration
GITHUB_TOKEN=ghp_...  # For issue creation
```

### Agent Configuration

Discovery agent automatically created with:
```python
{
    'name': 'DiscoveryAgent-Growth',
    'agent_type': AgentType.DISCOVERY_AGENT,
    'capabilities': [
        TaskType.TASK_DISCOVERY,
        TaskType.APPLICATION_ANALYSIS,
        TaskType.FEATURE_DEVELOPMENT,
        TaskType.PERFORMANCE_OPTIMIZATION
    ],
    'max_concurrent_tasks': 2,
    'priority_weight': 9.0,
    'configuration': {
        'specialization': 'continuous_growth',
        'discovery_enabled': True,
        'analysis_focus': 'business_value',
        'autonomous_discovery': True
    }
}
```

## Troubleshooting

### Common Issues

1. **No Tasks Created**
   - Check queue analysis output
   - Verify discovery conditions are met
   - Use `--force` flag to override conditions

2. **Discovery Agent Missing**
   - Run enhanced orchestrator setup
   - Check agent configuration in admin
   - Verify database migrations applied

3. **Workflow Failures**
   - Check PostgreSQL service status
   - Verify environment variables
   - Review workflow logs for specific errors

### Debug Commands

```bash
# Test discovery system
python test_enhanced_discovery.py

# Check agent status
python manage.py shell -c "
from apps.task_orchestration.models import Agent
for agent in Agent.objects.filter(is_active=True):
    print(f'{agent.name}: {agent.status} ({agent.current_task_count} tasks)')
"

# Analyze queue state
python manage.py discover_tasks --dry-run --verbose
```

## Future Enhancements

### Planned Improvements

1. **Machine Learning Integration**: Learn from task completion patterns
2. **User Feedback Loop**: Incorporate user preferences and feedback
3. **Business Metrics Integration**: Connect to actual business performance data
4. **Advanced Analytics**: Predictive task generation based on trends
5. **Cross-Repository Discovery**: Analyze related repositories for improvement ideas

### Extensibility Points

1. **Custom Growth Analyzers**: Add domain-specific analysis logic
2. **Priority Algorithms**: Implement custom prioritization strategies
3. **Task Templates**: Create reusable task generation templates
4. **Integration APIs**: Connect to external business systems
5. **Notification Systems**: Add Slack, email, or webhook notifications

## Best Practices

### Development

1. **Test Changes**: Always test discovery logic with `--dry-run` first
2. **Monitor Output**: Review discovery results regularly for relevance
3. **Adjust Priorities**: Update business priorities based on actual needs
4. **Validate Integration**: Ensure new tasks integrate with existing workflows

### Operations

1. **Monitor Workflows**: Check GitHub Actions for discovery run status
2. **Review Tasks**: Regularly review generated tasks for business value
3. **Agent Health**: Monitor agent utilization and performance
4. **Queue Balance**: Ensure task queue maintains healthy distribution

### Business Alignment

1. **Stakeholder Review**: Regularly review generated tasks with business stakeholders
2. **Priority Updates**: Update business priorities based on changing needs
3. **Feedback Integration**: Incorporate feedback into discovery logic
4. **Metrics Tracking**: Track business impact of generated tasks

## Summary

The AI Task Discovery System transforms the ProjectMeats orchestration from a reactive error-handling system into a proactive growth platform. By automatically analyzing the application state and generating business-focused improvement tasks every 45 minutes, it ensures continuous application evolution while maintaining all existing autonomous capabilities.

This system keeps development agents busy with meaningful work, drives consistent application improvement, and aligns technical development with business priorities for the meat sales broker management domain.