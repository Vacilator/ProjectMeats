# 🔧 Agent Orchestration Troubleshooting & FAQ

*Solutions to common issues and frequently asked questions*

## 🚨 Quick Troubleshooting

### Most Common Issues

#### ❌ "Cannot assign task due to conflicts"

**What it means**: Another agent is working on the same files or has an explicit conflict.

**Quick fix**:
```bash
# 1. See who's working on what
make agent-status

# 2. Choose a different task
make agent-tasks-priority

# 3. Or check when the conflicting task might be done
make agent-progress-report
```

**Example**:
```bash
$ make agent-assign TASK=TASK-006 AGENT=john
❌ Cannot assign task due to conflicts:
   - File conflict with TASK-007: ['frontend/src/components/DesignSystem.tsx'] (assigned to sarah)

# Solution: Pick a different task or wait for sarah to complete
$ make agent-tasks
$ make agent-assign TASK=TASK-004 AGENT=john  # Different task, no conflicts
```

#### ❌ "Task not found"

**What it means**: You have a typo in the task ID.

**Quick fix**:
```bash
# Check exact task IDs
make agent-tasks
```

**Example**:
```bash
$ make agent-assign TASK=task-001 AGENT=john
❌ Task task-001 not found

# Solution: Use correct format
$ make agent-assign TASK=TASK-001 AGENT=john  # Capital letters, hyphen
```

#### ❌ "Invalid status"

**What it means**: You misspelled a status name.

**Valid statuses**: `available`, `in_progress`, `blocked`, `completed`, `cancelled`

**Example**:
```bash
$ make agent-update TASK=TASK-001 AGENT=john STATUS=complete NOTES="Done"
❌ Invalid status. Use one of: ['in_progress', 'blocked', 'completed', 'cancelled']

# Solution: Use exact status name
$ make agent-update TASK=TASK-001 AGENT=john STATUS=completed NOTES="Done"
```

## 🛠️ Detailed Troubleshooting

### Task Assignment Issues

#### Problem: "Task is not available"
**Possible causes**:
1. Task is already assigned to someone else
2. Task is completed
3. Task dependencies aren't met
4. Task is blocked or cancelled

**Diagnosis**:
```bash
# Check task status
make agent-project-status

# See specific task details
python agent_orchestrator.py list-tasks
```

**Solutions**:
- If assigned: Wait for completion or coordinate with assigned agent
- If completed: Choose a different task
- If dependencies not met: Work on dependencies first or choose another task

#### Problem: "Dependencies not met"
**Example**: TASK-004 requires TASK-001 to be completed first.

**Diagnosis**:
```bash
# Check which tasks are ready (dependencies met)
make agent-tasks-priority
```

**Solutions**:
1. Work on the dependency task first
2. Choose a task without dependencies
3. Coordinate with team to complete dependencies

### Progress Update Issues

#### Problem: "Task is not assigned to you"
**Cause**: Trying to update a task assigned to someone else.

**Example**:
```bash
$ make agent-update TASK=TASK-001 AGENT=john STATUS=completed NOTES="Done"
❌ Task TASK-001 is not assigned to john

# Check who it's assigned to
$ make agent-status
```

**Solution**: Only update tasks assigned to you, or coordinate task reassignment.

#### Problem: Make commands not working on Windows
**Cause**: Windows doesn't have native `make` support.

**Solutions**:
1. **Recommended**: Use Python scripts directly:
   ```cmd
   python agent_orchestrator.py list-tasks --priority P0
   python agent_orchestrator.py assign-task TASK-001 your_name
   python agent_orchestrator.py update-task TASK-001 your_name completed --notes "Done"
   ```

2. **Alternative**: Use PowerShell scripts (if available)

3. **WSL**: Use Windows Subsystem for Linux

### System Issues

#### Problem: "No module named 'agent_orchestrator'"
**Cause**: Running commands from wrong directory.

**Solution**:
```bash
# Make sure you're in the project root
cd /path/to/ProjectMeats
pwd  # Should show ProjectMeats directory

# Then run commands
make agent-tasks
```

#### Problem: JSON file corruption
**Symptoms**: Strange errors, tasks disappearing, system not working.

**Diagnosis**:
```bash
# Check if JSON is valid
python -c "import json; print(json.load(open('docs/agent_tasks.json')))"
```

**Recovery**:
1. **If you have a backup**: Restore from backup
2. **If no backup**: Reinitialize the system:
   ```bash
   # CAUTION: This will reset all task assignments
   rm docs/agent_tasks.json
   python agent_orchestrator.py list-tasks  # Will recreate with defaults
   ```

## ❓ Frequently Asked Questions

### General Usage

**Q: How do I see all available tasks?**
```bash
make agent-tasks
```

**Q: How do I see only high-priority tasks?**
```bash
make agent-tasks-priority
```

**Q: How do I check if anyone is working on something?**
```bash
make agent-status
```

**Q: Can I work on multiple tasks at once?**
A: The system allows it, but it's not recommended. Focus on one task at a time for better quality and faster completion.

**Q: What if I need to stop working on a task?**
```bash
make agent-update TASK=TASK-XXX AGENT=your_name STATUS=cancelled NOTES="Reason for stopping"
```

**Q: How do I see the overall project progress?**
```bash
make agent-project-status
make agent-dashboard  # For visual dashboard
```

### Task Management

**Q: What's the difference between priority levels?**
- **P0** (Critical): Blocking issues, must be done immediately
- **P1** (High): Important for project success, do after P0
- **P2** (Medium): Valuable improvements, do when P0/P1 are complete
- **P3** (Low): Nice-to-have, do when time permits

**Q: How do I know what tasks I can work on?**
```bash
# See tasks that have no conflicts and met dependencies
make agent-tasks-priority
```

**Q: Can I create new tasks?**
A: Currently, tasks are predefined. Coordinate with team lead to add new tasks to the JSON file.

**Q: What if a task estimate is wrong?**
A: Update your progress notes with realistic time estimates. This helps improve future planning.

**Q: How often should I update progress?**
A: 
- **Short tasks (2-4h)**: Update when starting and completing
- **Medium tasks (6-12h)**: Update every 4-6 hours
- **Long tasks (16h+)**: Update every 6-8 hours, or daily

### Collaboration

**Q: How do I coordinate with other team members?**
1. Use `make agent-status` to see current work
2. Check `make agent-log` for recent activity
3. Update your progress regularly with meaningful notes
4. Check conflicts before starting work

**Q: What if I need help with my task?**
Update your status with specific questions:
```bash
make agent-update TASK=TASK-XXX AGENT=your_name STATUS=in_progress NOTES="Need help with: specific question or blocker description"
```

**Q: Can two people work on the same task?**
A: The system prevents this to avoid conflicts, but you can coordinate manually for pair programming.

**Q: What if someone else's task is blocking me?**
1. Check their progress: `make agent-status`
2. If needed, mark your task as blocked: 
   ```bash
   make agent-update TASK=TASK-XXX AGENT=your_name STATUS=blocked NOTES="Waiting for TASK-YYY to complete"
   ```

### Technical Issues

**Q: The dashboard isn't updating**
```bash
# Regenerate the dashboard
make agent-dashboard
```

**Q: I made a mistake in my progress update**
A: Add a new update with the correction:
```bash
make agent-update TASK=TASK-XXX AGENT=your_name STATUS=in_progress NOTES="Correction to previous update: actual details"
```

**Q: Commands are slow or hanging**
1. Check if you're in the right directory
2. Ensure Python dependencies are installed: `pip install -r backend/requirements.txt`
3. Check if JSON file is accessible: `ls -la docs/agent_tasks.json`

**Q: How do I backup my progress?**
The system automatically saves to `docs/agent_tasks.json`. You can copy this file as a backup.

### Workflow Integration

**Q: How does this work with Git?**
A: The orchestration system is separate from Git. Use normal Git workflow for code changes, and use orchestration for task coordination.

**Q: Do I need to create branches for each task?**
A: Not required by the orchestration system, but it's a good Git practice:
```bash
git checkout -b feature/task-001-description
```

**Q: How does this work with pull requests?**
A: Create PRs normally. Include task ID in PR description for tracking.

**Q: Can I work offline?**
A: Yes, but you won't be able to update task status or check for conflicts. Update when you're back online.

## 🔍 Diagnostic Commands

### System Health Check
```bash
# Check if system is working
make agent-project-status

# Verify JSON file is valid
python -c "import json; print('JSON Valid:', bool(json.load(open('docs/agent_tasks.json'))))"

# Check Python dependencies
python -c "import argparse, datetime, pathlib; print('Dependencies OK')"
```

### Debug Information
```bash
# Detailed task information
python agent_orchestrator.py list-tasks

# Raw task data
cat docs/agent_tasks.json | python -m json.tool

# System files check
ls -la agent_orchestrator.py agent_dashboard.py docs/agent_tasks.json
```

### Performance Check
```bash
# Time how long commands take
time make agent-tasks
time make agent-project-status
```

## 🚑 Emergency Procedures

### If the system is completely broken
1. **Check basic functionality**:
   ```bash
   python agent_orchestrator.py --help
   ```

2. **Verify files exist**:
   ```bash
   ls agent_orchestrator.py docs/agent_tasks.json
   ```

3. **Reset if necessary** (CAUTION: Loses all progress):
   ```bash
   rm docs/agent_tasks.json
   python agent_orchestrator.py list-tasks  # Reinitializes
   ```

### If tasks are corrupted
1. **Backup current state**:
   ```bash
   cp docs/agent_tasks.json docs/agent_tasks.json.backup
   ```

2. **Try to fix JSON manually** or restore from backup

3. **If all else fails**, reinitialize and manually re-enter critical assignments

### If you can't update task status
1. **Use direct Python commands**:
   ```bash
   python agent_orchestrator.py update-task TASK-001 your_name completed --notes "Done"
   ```

2. **Check file permissions**:
   ```bash
   ls -la docs/agent_tasks.json
   # Should be writable
   ```

3. **Manually edit JSON** as last resort (be very careful with syntax)

## 📞 Getting Help

### Self-Help Resources
1. **This troubleshooting guide** - covers 90% of issues
2. **Quick start guide**: [agent_quick_start_guide.md](agent_quick_start_guide.md)
3. **Workflow guide**: [agent_workflow_guide.md](agent_workflow_guide.md)
4. **Examples**: [agent_examples_guide.md](agent_examples_guide.md)

### Command Reference
```bash
make agent-help           # Full command reference
python agent_orchestrator.py --help  # Direct Python interface
```

### Team Communication
1. **Activity log**: `make agent-log` - see recent team activity
2. **Status check**: `make agent-status` - see who's working on what
3. **Progress report**: `make agent-progress-report` - detailed status

### When to Escalate
Contact team lead or project manager if:
- System is completely broken after trying troubleshooting steps
- Multiple team members report the same issue
- Data loss or corruption occurs
- You need new tasks added to the system

## 🔧 Advanced Troubleshooting

### JSON File Issues
The task database is stored in `docs/agent_tasks.json`. If this file becomes corrupted:

**Check JSON validity**:
```bash
python -c "
import json
try:
    with open('docs/agent_tasks.json', 'r') as f:
        data = json.load(f)
    print('JSON is valid')
    print(f'Tasks: {len(data.get(\"tasks\", {}))}')
    print(f'Agents: {len(data.get(\"agents\", {}))}')
except Exception as e:
    print(f'JSON error: {e}')
"
```

**Fix common JSON issues**:
1. **Missing comma**: Add commas between JSON objects
2. **Trailing comma**: Remove commas after last items
3. **Quote issues**: Ensure all strings are in double quotes
4. **Bracket mismatch**: Check that all `{` have matching `}`

### Performance Issues
If commands are slow:

**Check file size**:
```bash
ls -lh docs/agent_tasks.json
# Should be under 100KB for normal usage
```

**Optimize if needed**:
- Archive old completed tasks
- Remove unnecessary progress notes
- Compress JSON (remove extra whitespace)

### Network/Permission Issues
**Check file permissions**:
```bash
ls -la docs/agent_tasks.json
# Should show write permissions for your user
```

**Fix permissions**:
```bash
chmod 644 docs/agent_tasks.json
```

## 📊 Monitoring and Maintenance

### Daily Health Checks
```bash
# Quick system status
make agent-project-status

# Check for stuck tasks (same status for >24 hours)
make agent-progress-report | grep -A 5 "in_progress"
```

### Weekly Maintenance
```bash
# Generate comprehensive report
make agent-dashboard

# Archive completed tasks (manual process)
# Review and clean up old progress notes
```

---

**Still having issues?** Check the [Quick Start Guide](agent_quick_start_guide.md) or use `make agent-help` for command reference.