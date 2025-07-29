# 🚀 Agent Orchestration Quick Start Guide

*Get up and running with the ProjectMeats agent system in 5 minutes*

## 🎯 What is Agent Orchestration?

The agent orchestration system helps multiple developers work on ProjectMeats simultaneously without conflicts. Think of it as a smart task manager that:

- **Prevents merge conflicts** by ensuring only one person works on specific files
- **Manages dependencies** so work happens in the right order
- **Tracks progress** for stakeholders and team coordination
- **Automates task assignment** with priority-based queuing

## ⚡ 5-Minute Setup

### 1. Check What's Available
```bash
make agent-tasks-priority
```
This shows you high-priority tasks ready to be worked on.

### 2. Pick a Task and Check for Conflicts
```bash
make agent-conflicts TASK=TASK-001 AGENT=your_name
```
Replace `your_name` with any identifier (e.g., `john`, `frontend_dev`, `backend_specialist`).

### 3. Assign the Task to Yourself
```bash
make agent-assign TASK=TASK-001 AGENT=your_name
```

### 4. Work on the Task
Do your development work as usual. The system tracks that you're working on specific files.

### 5. Update Progress
```bash
# When you start working
make agent-update TASK=TASK-001 AGENT=your_name STATUS=in_progress NOTES="Starting work on the bug fix"

# When you make progress
make agent-update TASK=TASK-001 AGENT=your_name STATUS=in_progress NOTES="Found the issue, fixing the test data"

# When you complete the task
make agent-update TASK=TASK-001 AGENT=your_name STATUS=completed NOTES="Fixed the test, all 77 tests now pass"
```

## 📋 Common Workflows

### 🔍 Finding Work
```bash
# See all available tasks
make agent-tasks

# See only high-priority tasks
make agent-tasks-priority

# Check overall project status
make agent-project-status
```

### 🎯 Working on a Task
```bash
# 1. Check for conflicts first
make agent-conflicts TASK=TASK-XXX AGENT=your_name

# 2. If no conflicts, assign to yourself
make agent-assign TASK=TASK-XXX AGENT=your_name

# 3. Start working and update status
make agent-update TASK=TASK-XXX AGENT=your_name STATUS=in_progress NOTES="Brief description of what you're doing"

# 4. Update progress regularly
make agent-update TASK=TASK-XXX AGENT=your_name STATUS=in_progress NOTES="Progress update"

# 5. Complete the task
make agent-update TASK=TASK-XXX AGENT=your_name STATUS=completed NOTES="What you accomplished and how to verify"
```

### 🚨 When Things Go Wrong
```bash
# If you're blocked
make agent-update TASK=TASK-XXX AGENT=your_name STATUS=blocked NOTES="Describe what's blocking you"

# If you need to cancel/reassign
make agent-update TASK=TASK-XXX AGENT=your_name STATUS=cancelled NOTES="Reason for cancellation"
```

## 🏷️ Task Types and Priorities

### Priorities (work on higher first)
- **P0** (🔥 Critical): Blocking issues, must be fixed immediately
- **P1** (⚡ High): Important features for project success  
- **P2** (📋 Medium): Valuable improvements
- **P3** (💡 Low): Nice-to-have enhancements

### Categories
- **bug_fix**: Fix broken functionality
- **testing**: Add or improve tests
- **performance**: Optimize speed/efficiency
- **security**: Security improvements
- **ui_ux**: User interface improvements
- **devops**: CI/CD, deployment, infrastructure

## 🤝 Team Coordination

### Current Active Work
```bash
make agent-status
```
Shows who's working on what.

### Progress Reports
```bash
# Generate stakeholder dashboard
make agent-dashboard

# Detailed progress report
make agent-progress-report
```

## 💡 Pro Tips

### ✅ Best Practices
1. **Always check conflicts first** - prevents merge conflicts
2. **Update status regularly** - keeps team informed
3. **Use descriptive notes** - helps others understand your progress
4. **Complete validation criteria** - ensures quality
5. **Start with smaller tasks** - learn the system gradually

### ⚠️ Avoid These Mistakes
1. **Don't skip conflict checking** - can cause merge conflicts
2. **Don't forget status updates** - team loses visibility
3. **Don't work on unassigned tasks** - causes conflicts
4. **Don't modify files from other assigned tasks** - breaks isolation

### 🔍 Quick Status Check
```bash
# One command to see everything important
make agent-project-status && echo "" && make agent-tasks-priority
```

## 🆘 Troubleshooting

### "Task not found"
- Check task ID spelling: `make agent-tasks` to see available tasks
- Make sure you're using the exact task ID (e.g., `TASK-001`, not `task-1`)

### "Cannot assign task due to conflicts"
- Someone else is working on the same files
- Check who: `make agent-status`
- Choose a different task or coordinate with the other agent

### "Task is not available"
- Task might be completed, blocked, or in progress
- Check status: `make agent-project-status`
- Dependencies might not be met

### "Invalid status"
- Valid statuses: `available`, `in_progress`, `blocked`, `completed`, `cancelled`
- Check spelling and use exact status names

## 🔗 Related Documentation

- [📖 Complete Agent System Guide](../AGENT_ORCHESTRATION_README.md) - Full documentation
- [📋 All Available Tasks](agent_todo_system.md) - Complete task list
- [📝 Activity Log](agent_activity_log.md) - Team activity tracking
- [📊 Dashboard](../AGENT_PROGRESS_DASHBOARD.md) - Visual progress overview

## 📞 Need Help?

1. **Check this guide first** - covers 90% of common scenarios
2. **Look at examples** in the main documentation
3. **Check recent activity** with `make agent-log`
4. **Use the help command** `make agent-help`

---

**Ready to start?** Run `make agent-tasks-priority` to see what's available! 🚀