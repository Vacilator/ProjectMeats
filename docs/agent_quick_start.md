# Agent Quick Start Guide

Welcome to the ProjectMeats migration project! This guide helps you get started quickly and follow the required logging procedures.

## 🚨 REQUIRED FIRST STEP: Log Your Objectives

**Before starting any work**, you MUST add an entry to the [Agent Activity Log](./agent_activity_log.md). This is a project requirement.

### Quick Start Logging

1. **Open the log file**:
   ```bash
   make agent-log-edit
   ```

2. **Copy the template** from the log file and fill in:
   - Your agent name/ID
   - Current date and time
   - Your objectives (what you plan to work on)
   - Initial status

3. **Save and commit** your initial log entry

## 📋 Development Workflow

### Phase 1: Setup and Planning
1. ✅ Log initial objectives in agent activity log
2. Read [migration_mapping.md](./migration_mapping.md) to understand current status
3. Choose an entity or task to work on
4. Review existing patterns (e.g., `accounts_receivables` app)

### Phase 2: Development
1. Follow entity migration patterns
2. Update your log entry with progress regularly
3. Test your changes frequently
4. Update documentation as needed

### Phase 3: Completion
1. Mark objectives as completed in the log
2. Update migration status in [migration_mapping.md](./migration_mapping.md)
3. Hand off any remaining work clearly in the log

## 🔧 Useful Commands

```bash
# View agent activity log
make agent-log

# Edit agent activity log
make agent-log-edit

# View agent activity summary
make agent-status

# View current migration status
cat docs/migration_mapping.md | grep -A 20 "Migration Status"

# Start development servers
make dev

# Run tests
make test

# Generate API docs
make docs
```

## 📚 Key Documentation

- **[Agent Activity Log](./agent_activity_log.md)** - **REQUIRED** logging for all agents
- **[Migration Mapping](./migration_mapping.md)** - Entity migration status and technical details
- **[API Reference](./api_reference.md)** - API documentation
- **[Complete Setup Guide](./setup_guide.md)** - Comprehensive setup for all platforms and scenarios
- **[Production Deployment](./production_deployment.md)** - Enterprise production deployment guide

## 🎯 Common Tasks

### Migrating a New Entity
1. Log your objective in the activity log
2. Analyze PowerApps entity structure
3. Create Django model following existing patterns
4. Add serializers, views, and URLs
5. Create React components
6. Add tests
7. Update documentation
8. Log completion and test results

### Frontend Implementation for Existing Backend
1. Log your objective in the activity log
2. Review existing Django model and API endpoints
3. Create React screen component
4. Add API service integration
5. Implement CRUD operations
6. Add routing and navigation
7. Test thoroughly
8. Log completion

### Bug Fixes and Improvements
1. Log the issue and your planned approach
2. Identify root cause
3. Implement minimal fix
4. Test fix thoroughly
5. Update relevant documentation if needed
6. Log resolution and testing results

## ⚠️ Important Notes

- **Always log first** - no exceptions
- **Update logs regularly** - daily for active work
- **Follow existing patterns** - consistency is key
- **Test thoroughly** - both backend and frontend
- **Update documentation** - keep mappings current
- **Communicate clearly** - logs help coordinate with other agents

## 🆘 Getting Help

1. Check existing documentation first
2. Review similar implemented entities for patterns
3. Add questions/blockers to your agent log entry
4. Reference other agents' log entries for similar work

---

**Remember**: The agent activity log is not just a requirement - it's a valuable coordination tool that helps all agents work effectively together on this migration project.