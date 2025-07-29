# 🎯 Agent Orchestration Examples & Common Scenarios

*Real-world examples of using the ProjectMeats agent orchestration system*

## 🌟 Complete Example Walkthroughs

### Example 1: Backend Developer Fixing a Bug

**Context**: Sarah is a backend developer who wants to fix the failing purchase order test.

#### Step-by-Step Walkthrough

**1. Sarah checks what's available**
```bash
$ make agent-tasks-priority
🎯 High Priority Tasks:

🎯 **TASK-001** (P0) - 3h
   Fix failing purchase order creation test
   Category: bug_fix
   Files: backend/apps/purchase_orders/tests.py

🎯 **TASK-002** (P0) - 10h
   Add Jest tests for React components
   Category: testing
   Files: frontend/src/screens/*.test.tsx, frontend/src/components/*.test.tsx
```

**2. Sarah picks TASK-001 (matches her backend skills) and checks conflicts**
```bash
$ make agent-conflicts TASK=TASK-001 AGENT=sarah_backend
✅ No conflicts detected. Task can be assigned.
```

**3. Sarah assigns the task to herself**
```bash
$ make agent-assign TASK=TASK-001 AGENT=sarah_backend
✅ Assigned TASK-001 to sarah_backend
📋 Task: Fix failing purchase order creation test
⏰ Estimate: 3 hours
📁 Files: backend/apps/purchase_orders/tests.py
```

**4. Sarah starts working and updates status**
```bash
$ make agent-update TASK=TASK-001 AGENT=sarah_backend STATUS=in_progress NOTES="Investigating the test failure, looks like invalid file upload test data"
✅ Updated TASK-001 status: available → in_progress
📝 Notes: Investigating the test failure, looks like invalid file upload test data
```

**5. Sarah investigates the issue**
```bash
$ cd backend
$ python manage.py test apps.purchase_orders.tests
# Sees the failing test and identifies the problem
```

**6. Sarah provides a progress update**
```bash
$ make agent-update TASK=TASK-001 AGENT=sarah_backend STATUS=in_progress NOTES="Found the issue: test_create_purchase_order using invalid file data. Fixing the test fixture."
✅ Updated TASK-001 status: in_progress → in_progress
📝 Notes: Found the issue: test_create_purchase_order using invalid file data. Fixing the test fixture.
```

**7. Sarah fixes the test and validates**
```bash
$ cd backend
$ python manage.py test
# All 77 tests pass!
```

**8. Sarah completes the task**
```bash
$ make agent-update TASK=TASK-001 AGENT=sarah_backend STATUS=completed NOTES="Fixed the purchase order test. Updated test data with valid file format. All 77 tests now pass."
✅ Updated TASK-001 status: in_progress → completed
📝 Notes: Fixed the purchase order test. Updated test data with valid file format. All 77 tests now pass.
```

**9. Sarah updates the project dashboard**
```bash
$ make agent-dashboard
📊 Generating Visual Progress Dashboard...
✅ Dashboard saved to AGENT_PROGRESS_DASHBOARD.md
```

### Example 2: Frontend Developer Adding Tests

**Context**: Mike is a frontend developer who wants to add Jest tests to React components.

#### Step-by-Step Walkthrough

**1. Mike checks current project status**
```bash
$ make agent-project-status
📊 **ProjectMeats Status**
   Total Tasks: 7
   Completion: 14.8%  # Increased because Sarah completed TASK-001
   Hours: 8/54
   Active Agents: 1

📈 **Breakdown**:
   Available: 5
   In_progress: 1  # Sarah's task is now complete
   Completed: 2
```

**2. Mike sees what's available for frontend work**
```bash
$ make agent-tasks
📋 Available Tasks (5 found):

🎯 **TASK-002** (P0) - 10h
   Add Jest tests for React components
   Category: testing
   Files: frontend/src/screens/*.test.tsx, frontend/src/components/*.test.tsx
   ...
```

**3. Mike checks for conflicts**
```bash
$ make agent-conflicts TASK=TASK-002 AGENT=mike_frontend
✅ No conflicts detected. Task can be assigned.
```

**4. Mike assigns and starts the task**
```bash
$ make agent-assign TASK=TASK-002 AGENT=mike_frontend
✅ Assigned TASK-002 to mike_frontend

$ make agent-update TASK=TASK-002 AGENT=mike_frontend STATUS=in_progress NOTES="Starting test implementation. First auditing existing components to plan test strategy."
```

**5. Mike works in phases and provides regular updates**

**Day 1:**
```bash
$ make agent-update TASK=TASK-002 AGENT=mike_frontend STATUS=in_progress NOTES="Completed audit of components. Adding tests for core components: CustomerScreen, SupplierScreen. 25% complete."
```

**Day 2:**
```bash
$ make agent-update TASK=TASK-002 AGENT=mike_frontend STATUS=in_progress NOTES="Added tests for 6 screen components. Working on shared components now. 60% complete."
```

**Day 3:**
```bash
$ make agent-update TASK=TASK-002 AGENT=mike_frontend STATUS=completed NOTES="All React components now have Jest tests. Coverage: 87% (exceeds 80% requirement). All tests passing."
```

### Example 3: Handling Conflicts

**Context**: Two developers try to work on related tasks simultaneously.

#### Scenario Setup
- **Alex**: Wants to work on TASK-006 (Modernize dashboard)
- **Jordan**: Wants to work on TASK-007 (Implement responsive design)
- Both tasks involve frontend UI changes

#### Conflict Detection

**Alex tries first:**
```bash
$ make agent-assign TASK=TASK-006 AGENT=alex_fullstack
✅ Assigned TASK-006 to alex_fullstack
```

**Jordan tries 30 minutes later:**
```bash
$ make agent-conflicts TASK=TASK-007 AGENT=jordan_ui
⚠️ Conflicts detected:
   - Conflicts with TASK-006: Modernize dashboard with business KPIs (assigned to alex_fullstack)
```

#### Conflict Resolution

**Option 1: Jordan chooses a different task**
```bash
$ make agent-tasks-priority
# Jordan picks TASK-004 (Database optimization) instead
$ make agent-assign TASK=TASK-004 AGENT=jordan_ui
```

**Option 2: Coordination**
Jordan could coordinate with Alex:
```bash
$ make agent-status
# Shows Alex is working on TASK-006
# Jordan waits or works on backend tasks until Alex completes
```

### Example 4: Team Lead Managing Multiple Agents

**Context**: Team lead Lisa wants to assign work to her team efficiently.

#### Morning Planning Session

**1. Lisa checks overall status**
```bash
$ make agent-project-status
📊 **ProjectMeats Status**
   Total Tasks: 7
   Completion: 32.1%
   Hours: 18/54
   Active Agents: 3

📈 **Breakdown**:
   Available: 3
   In_progress: 2
   Completed: 3
```

**2. Lisa sees what's in progress**
```bash
$ make agent-status
👤 **alex_fullstack**
   Assigned: 1 tasks
   Completed: 0 tasks
   Total Hours: 0h

👤 **jordan_ui** 
   Assigned: 1 tasks
   Completed: 1 tasks
   Total Hours: 7h

👤 **mike_frontend**
   Assigned: 1 tasks
   Completed: 1 tasks
   Total Hours: 10h
```

**3. Lisa checks what's available for assignment**
```bash
$ make agent-tasks-priority
🎯 High Priority Tasks:

🎯 **TASK-004** (P1) - 7h
   Database query optimization audit
   Category: performance
   Files: backend/apps/*/models.py, backend/apps/*/views.py

🎯 **TASK-005** (P1) - 5h
   Security validation and hardening
   Category: security
   Files: backend/projectmeats/settings.py, security middleware
```

**4. Lisa assigns work based on team skills**
```bash
# Assign database work to backend specialist
$ make agent-assign TASK=TASK-004 AGENT=database_specialist_new

# Assign security work to senior developer
$ make agent-assign TASK=TASK-005 AGENT=senior_dev_security
```

### Example 5: Handling Blockers

**Context**: Developer encounters an unexpected blocker during work.

#### Scenario
Emma is working on database optimization but encounters a blocker.

**1. Emma reports the blocker**
```bash
$ make agent-update TASK=TASK-004 AGENT=emma_backend STATUS=blocked NOTES="Need access to production database metrics to identify slow queries. Waiting for DevOps team to provide read-only access."
```

**2. Emma chooses alternative work**
```bash
$ make agent-tasks-priority
# Emma picks a different task she can work on while waiting
$ make agent-assign TASK=TASK-005 AGENT=emma_backend
```

**3. When blocker is resolved, Emma returns to original task**
```bash
$ make agent-update TASK=TASK-004 AGENT=emma_backend STATUS=in_progress NOTES="Got database access. Starting performance analysis of customer and supplier queries."
```

### Example 6: QA Validation Workflow

**Context**: QA team validating completed development work.

#### QA Process

**1. QA checks recently completed tasks**
```bash
$ make agent-progress-report
# Shows all completed tasks with validation criteria
```

**2. QA validates TASK-002 (Jest tests)**
```bash
$ cd frontend
$ npm test -- --coverage
# Checks that coverage is above 80% as required
```

**3. QA finds an issue**
```bash
$ make agent-update TASK=TASK-002 AGENT=mike_frontend STATUS=blocked NOTES="QA Review: Tests pass but coverage is only 78% on CustomerScreen component. Need additional test cases for error handling."
```

**4. Developer fixes the issue**
```bash
$ make agent-update TASK=TASK-002 AGENT=mike_frontend STATUS=in_progress NOTES="Adding additional test cases for CustomerScreen error scenarios to reach 80%+ coverage."

# After fixing:
$ make agent-update TASK=TASK-002 AGENT=mike_frontend STATUS=completed NOTES="Added missing test cases. Final coverage: 83%. All validation criteria met."
```

## 🎯 Scenario-Based Examples

### Scenario: New Team Member Onboarding

**Context**: New developer joins the team and needs to start contributing.

#### Onboarding Workflow
```bash
# 1. New developer reads documentation
# docs/agent_quick_start_guide.md

# 2. Sets up development environment
$ make setup-python

# 3. Checks what tasks are available for beginners
$ python agent_orchestrator.py list-tasks --priority P2
# Starts with medium priority tasks to learn the system

# 4. Picks their first task
$ make agent-assign TASK=TASK-006 AGENT=new_developer

# 5. Gets mentorship through progress updates
$ make agent-update TASK=TASK-006 AGENT=new_developer STATUS=in_progress NOTES="First day: familiarizing with dashboard code structure. Would appreciate code review when ready."
```

### Scenario: Sprint Planning

**Context**: Team planning a 2-week sprint with multiple developers.

#### Sprint Planning Process
```bash
# 1. Product manager checks overall status
$ make agent-project-status

# 2. Reviews available high-priority work
$ make agent-tasks-priority

# 3. Assigns work based on team capacity
# Backend team: 2 developers × 2 weeks = 160 hours capacity
# Available backend tasks: TASK-004 (7h) + TASK-005 (5h) = 12h
# Can take on additional P2 tasks

# 4. Tracks progress throughout sprint
$ make agent-dashboard  # Daily
$ make agent-progress-report  # Weekly
```

### Scenario: Emergency Hotfix

**Context**: Production issue requires immediate attention.

#### Emergency Response
```bash
# 1. Create emergency task (coordinate with team lead)
# Add EMERGENCY-001 to task database manually

# 2. Assign to available senior developer
$ make agent-assign TASK=EMERGENCY-001 AGENT=senior_dev_oncall

# 3. Track progress closely
$ make agent-update TASK=EMERGENCY-001 AGENT=senior_dev_oncall STATUS=in_progress NOTES="Identified production issue in purchase order API. Creating hotfix branch."

# 4. Expedite through QA
$ make agent-update TASK=EMERGENCY-001 AGENT=senior_dev_oncall STATUS=completed NOTES="Hotfix deployed. Production issue resolved. Full fix to be included in next regular release."
```

## 📊 Reporting Examples

### Daily Standup Report
```bash
$ make agent-status && echo "=== HIGH PRIORITY WORK ===" && make agent-tasks-priority

# Output shows:
# - Who's working on what
# - Progress on current tasks  
# - What's available for new assignments
```

### Weekly Stakeholder Update
```bash
$ make agent-dashboard
# Generates comprehensive visual dashboard with:
# - Progress bars showing completion
# - Task status breakdown
# - Agent productivity metrics
# - Upcoming work priorities
```

### Monthly Project Review
```bash
$ make agent-progress-report
# Provides detailed analysis including:
# - Completion statistics
# - Agent performance metrics
# - Risk analysis (blocked tasks)
# - Upcoming milestone planning
```

## 🔧 Integration Examples

### Git Workflow Integration
```bash
# 1. Normal development process
$ git checkout -b feature/task-001-purchase-order-fix

# 2. Make code changes
$ git add .
$ git commit -m "Fix purchase order test data validation"

# 3. Update orchestration system
$ make agent-update TASK=TASK-001 AGENT=your_name STATUS=completed NOTES="PR created: feature/task-001-purchase-order-fix"

# 4. Create PR normally
$ git push origin feature/task-001-purchase-order-fix
```

### CI/CD Integration Example
```yaml
# In .github/workflows/ci-cd.yml
- name: Validate Task Assignment
  run: |
    # Check if PR branch matches assigned task
    python scripts/validate_task_assignment.py ${{ github.head_ref }}

- name: Update Task Progress
  if: success()
  run: |
    # Auto-update task status when PR is merged
    make agent-update TASK=$TASK_ID AGENT=$AGENT_ID STATUS=completed NOTES="PR merged successfully"
```

## 💡 Best Practices from Examples

### From Backend Development (Sarah's Example)
1. **Quick status updates** keep team informed
2. **Specific error descriptions** help future debugging
3. **Validation before completion** ensures quality
4. **Clear completion notes** document what was fixed

### From Frontend Development (Mike's Example)
1. **Phase-based progress** for longer tasks
2. **Percentage completion** helps with planning
3. **Exceed requirements** when possible (87% vs 80% coverage)
4. **Regular milestone updates** maintain momentum

### From Conflict Resolution (Alex & Jordan Example)
1. **Always check conflicts** before starting work
2. **Coordinate early** when conflicts arise
3. **Have backup tasks** ready
4. **Communicate timing** with team

### From Team Management (Lisa's Example)
1. **Daily status checks** for team oversight
2. **Skills-based assignment** improves efficiency
3. **Monitor team workload** to prevent burnout
4. **Plan for dependencies** between tasks

### From Blocker Handling (Emma's Example)
1. **Report blockers immediately** with specific details
2. **Find alternative work** to stay productive
3. **Return to blocked tasks** as soon as possible
4. **Document blocker resolution** for future reference

## 🚨 Common Mistakes from Real Examples

### ❌ What NOT to Do

**Don't skip conflict checking:**
```bash
# WRONG: Assign without checking
$ make agent-assign TASK=TASK-007 AGENT=dev1
❌ Cannot assign task due to conflicts

# RIGHT: Check first
$ make agent-conflicts TASK=TASK-007 AGENT=dev1
$ make agent-assign TASK=TASK-007 AGENT=dev1
```

**Don't use vague progress notes:**
```bash
# WRONG: Unhelpful update
$ make agent-update TASK=TASK-001 AGENT=dev1 STATUS=in_progress NOTES="working on it"

# RIGHT: Specific and useful
$ make agent-update TASK=TASK-001 AGENT=dev1 STATUS=in_progress NOTES="Found failing test in test_create_purchase_order. Invalid file upload data causing assertion error. Fixing test fixture."
```

**Don't forget regular updates:**
```bash
# WRONG: No updates for 2 days
# Team doesn't know if you're stuck or making progress

# RIGHT: Regular updates every 4-6 hours for active work
$ make agent-update TASK=TASK-002 AGENT=dev1 STATUS=in_progress NOTES="Day 1: Added tests for 4 screen components, 40% complete"
```

## 📚 Next Steps

After reviewing these examples:

1. **Practice with a simple task** - Start with a P2 task to learn the system
2. **Read the workflow guide** - [Agent Workflow Guide](agent_workflow_guide.md)
3. **Join team coordination** - Use `make agent-status` daily
4. **Provide feedback** - Help improve the orchestration system

---

**Ready to contribute?** Pick an example that matches your role and try it out! 🚀