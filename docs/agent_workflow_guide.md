# 📋 Agent Orchestration Workflows and Task Queuing Guide

*Complete workflows for using the ProjectMeats agent orchestration system effectively*

## 🎯 Overview

This guide provides detailed workflows for common scenarios when using the agent orchestration system. Each workflow includes step-by-step instructions, examples, and validation steps.

## 🔄 Core Workflows

### Workflow 1: Starting Your First Task

**Scenario**: New developer wants to contribute to ProjectMeats

#### Step 1: Understand the Current State
```bash
# Get project overview
make agent-project-status

# See what's available for your skills
make agent-tasks-priority
```

**Expected Output**: You'll see completion percentage, task breakdown, and high-priority tasks.

#### Step 2: Choose an Appropriate Task
```bash
# List all tasks with details
make agent-tasks

# Filter by category if you have specific skills
python agent_orchestrator.py list-tasks --category bug_fix    # For backend work
python agent_orchestrator.py list-tasks --category testing   # For QA work
python agent_orchestrator.py list-tasks --category ui_ux     # For frontend work
```

**Decision Criteria**:
- Choose P0 tasks first (critical priority)
- Pick tasks matching your skill level
- Estimate 2-8 hours for first tasks

#### Step 3: Check for Conflicts
```bash
make agent-conflicts TASK=TASK-001 AGENT=your_github_username
```

**Possible Results**:
- ✅ "No conflicts detected" → Proceed to assignment
- ⚠️ "Conflicts detected" → Choose different task or coordinate

#### Step 4: Assign Task to Yourself
```bash
make agent-assign TASK=TASK-001 AGENT=your_github_username
```

**Validation**: Should see confirmation with task details, files, and estimate.

#### Step 5: Set Up Development Environment
```bash
# If not already set up
make setup-python

# Start development servers
make dev
```

#### Step 6: Begin Work and Update Status
```bash
make agent-update TASK=TASK-001 AGENT=your_github_username STATUS=in_progress NOTES="Setting up environment and investigating the issue"
```

### Workflow 2: Making Progress Updates

**Scenario**: You're working on a task and want to keep the team informed

#### Regular Progress Updates (Every 2-4 hours)
```bash
make agent-update TASK=TASK-001 AGENT=your_github_username STATUS=in_progress NOTES="Found the root cause: invalid test data in purchase order creation. Working on fix."
```

#### When You Hit a Blocker
```bash
make agent-update TASK=TASK-001 AGENT=your_github_username STATUS=blocked NOTES="Need clarification on expected test data format. Waiting for feedback from product team."
```

#### When You Make a Breakthrough
```bash
make agent-update TASK=TASK-001 AGENT=your_github_username STATUS=in_progress NOTES="Fixed the test data issue. Now running full test suite to ensure no regressions."
```

### Workflow 3: Completing a Task

**Scenario**: You've finished your work and want to properly close the task

#### Step 1: Validate Completion Criteria
Before marking complete, ensure you've met the task's validation criteria:

```bash
# For TASK-001 example: "All 77 tests pass"
cd backend && python manage.py test

# For testing tasks: Check coverage
cd frontend && npm test -- --coverage --watchAll=false
```

#### Step 2: Mark Task as Complete
```bash
make agent-update TASK=TASK-001 AGENT=your_github_username STATUS=completed NOTES="Fixed purchase order test. All 77 tests now pass. Fixed invalid file upload test data in test_create_purchase_order method."
```

#### Step 3: Update Progress Dashboard
```bash
make agent-dashboard
```

This generates an updated stakeholder dashboard showing your completion.

### Workflow 4: Task Queue Management

**Scenario**: Planning work for a team or understanding dependencies

#### Viewing the Task Queue
```bash
# High-priority ready tasks
make agent-tasks-priority

# All available tasks
make agent-tasks

# Tasks by specific priority
python agent_orchestrator.py list-tasks --priority P0
python agent_orchestrator.py list-tasks --priority P1
```

#### Understanding Dependencies
Tasks have dependencies that must be completed first. Example:

```json
"TASK-004": {
  "dependencies": ["TASK-001"],  // Must complete TASK-001 first
}
```

To see what's blocking a task:
```bash
python agent_orchestrator.py list-tasks
```
Dependencies are shown for each task.

#### Queue Prioritization Strategy
1. **P0 tasks first** - Critical bugs and blockers
2. **Dependencies** - Tasks that unblock others
3. **Agent skills** - Match tasks to expertise
4. **Time estimates** - Balance short and long tasks

### Workflow 5: Team Coordination

**Scenario**: Multiple agents working simultaneously

#### Daily Team Standup Workflow
```bash
# 1. Project status overview
make agent-project-status

# 2. See who's working on what
make agent-status

# 3. Available high-priority work
make agent-tasks-priority

# 4. Recent progress
make agent-progress-report
```

#### Coordinating with Other Agents
```bash
# Before starting work, check current assignments
make agent-status

# If you need to work on related files, check conflicts
make agent-conflicts TASK=TASK-006 AGENT=your_name

# See recent team activity
make agent-log
```

#### Handling Conflicts
If you get a conflict warning:

1. **Check who has the conflicting task**:
   ```bash
   make agent-status
   ```

2. **Coordinate directly** or choose alternative task

3. **Wait for completion** if the other task is nearly done

4. **Split the work** if both tasks are large

### Workflow 6: Stakeholder Reporting

**Scenario**: Management wants project status updates

#### Quick Status for Management
```bash
# Generate visual dashboard
make agent-dashboard

# Create detailed report
make agent-progress-report
```

The dashboard includes:
- Completion percentage with visual progress bars
- Task status breakdown
- Agent activity summary
- High-priority tasks ready for assignment
- Current work in progress
- Recent completions

#### Regular Reporting Schedule
- **Daily**: `make agent-dashboard` (automated if needed)
- **Weekly**: `make agent-progress-report` 
- **Milestone**: Custom reports highlighting major completions

## 🎯 Advanced Workflows

### Workflow 7: Handling Large Tasks

**Scenario**: Task is estimated at 16+ hours

#### Breaking Down Large Tasks
1. **Analyze the scope** in task description
2. **Create sub-tasks** if possible (coordinate with team)
3. **Use frequent progress updates** (every 4-6 hours)
4. **Consider pair programming** for complex tasks

#### Progress Tracking for Large Tasks
```bash
# Day 1
make agent-update TASK=TASK-007 AGENT=your_name STATUS=in_progress NOTES="Started responsive design system. Completed initial component audit (25% complete)"

# Day 2  
make agent-update TASK=TASK-007 AGENT=your_name STATUS=in_progress NOTES="Implemented responsive grid system and basic components (50% complete)"

# Day 3
make agent-update TASK=TASK-007 AGENT=your_name STATUS=in_progress NOTES="Added mobile optimizations and testing (75% complete)"

# Day 4
make agent-update TASK=TASK-007 AGENT=your_name STATUS=completed NOTES="Responsive design system complete. All screens tested on mobile/tablet/desktop."
```

### Workflow 8: Emergency Bug Fixes

**Scenario**: Critical production issue needs immediate attention

#### Emergency Task Assignment
```bash
# 1. Check if emergency task exists
make agent-tasks-priority

# 2. If not, coordinate with team lead to add P0 task

# 3. Check conflicts immediately  
make agent-conflicts TASK=EMERGENCY-001 AGENT=your_name

# 4. Assign and start immediately
make agent-assign TASK=EMERGENCY-001 AGENT=your_name
make agent-update TASK=EMERGENCY-001 AGENT=your_name STATUS=in_progress NOTES="Starting emergency fix for production issue"
```

#### Hotfix Workflow
1. **Create branch** for hotfix
2. **Update status frequently** (every 30-60 minutes for critical issues)
3. **Coordinate testing** with QA team
4. **Document fix thoroughly** in completion notes

### Workflow 9: Quality Assurance Integration

**Scenario**: QA team wants to validate completed tasks

#### QA Validation Workflow
```bash
# 1. See recently completed tasks
python agent_orchestrator.py list-tasks | grep completed

# 2. Check completion details
make agent-progress-report

# 3. Validate against criteria in task description

# 4. If issues found, agent can update task
make agent-update TASK=TASK-XXX AGENT=original_agent STATUS=blocked NOTES="QA found issues: [list specific problems]"
```

## 🔧 Integration with Development Workflow

### Git Integration
The orchestration system works alongside normal Git workflow:

```bash
# Normal development
git checkout -b feature/task-001-fix-purchase-orders
# ... do your work ...
git commit -m "Fix purchase order test data validation"
git push origin feature/task-001-fix-purchase-orders

# Create PR as normal
# Orchestration system tracks progress separately
```

### CI/CD Integration
The orchestration system enhances CI/CD:

- **Task validation**: CI can check that PR matches assigned task
- **Quality gates**: Validate completion criteria in automated tests
- **Progress updates**: Automated updates when PR is merged

### IDE Integration
Use your normal development tools:

- **VSCode**: Regular development workflow
- **PyCharm**: Normal Django development
- **Terminal**: Orchestration commands via Makefile

## 📊 Metrics and Analytics

### Individual Performance Tracking
```bash
# Your personal stats
python agent_orchestrator.py agent-status --agent-id your_name

# Project-wide metrics
make agent-project-status
```

### Team Analytics
The system tracks:
- **Completion rates** per agent
- **Average task duration** vs estimates
- **Conflict frequency** (should be low)
- **Queue velocity** (tasks completed per week)

## 🚨 Troubleshooting Common Issues

### Issue: "Cannot assign task due to conflicts"
**Cause**: Another agent is working on the same files
**Solution**:
```bash
# 1. Check who has the conflicting task
make agent-status

# 2. Choose a different task or coordinate timing
make agent-tasks-priority

# 3. Check when the conflicting task might be done
make agent-progress-report
```

### Issue: "Task dependencies not met"
**Cause**: Prerequisites haven't been completed yet
**Solution**:
```bash
# 1. Check which dependencies are needed
make agent-tasks

# 2. Work on the dependency first, or
# 3. Choose a task without dependencies
```

### Issue: "Invalid task status"
**Cause**: Typo in status name
**Solution**: Use exact status names:
- `available`
- `in_progress` 
- `blocked`
- `completed`
- `cancelled`

## 📚 Additional Resources

- [🚀 Quick Start Guide](agent_quick_start_guide.md) - 5-minute setup
- [📖 Complete Documentation](../AGENT_ORCHESTRATION_README.md) - Full system guide
- [📋 Task System](agent_todo_system.md) - All available tasks
- [📝 Activity Log](agent_activity_log.md) - Team activity tracking

---

**Need help?** Start with the [Quick Start Guide](agent_quick_start_guide.md) or use `make agent-help` for command reference.