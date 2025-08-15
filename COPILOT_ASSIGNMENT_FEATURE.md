# @copilot Assignment for Deployment Failures

## Overview

The AI Deployment Orchestrator now automatically assigns `@copilot` to GitHub issues and PRs created when deployment failures occur. This enables automatic resolution of deployment problems through GitHub Copilot's AI assistance.

## Features Implemented

### ✅ Automatic @copilot Assignment
- Every deployment failure issue is automatically assigned to `@copilot`
- Special `copilot-fix-needed` label triggers immediate attention
- Enhanced issue titles include `@copilot please fix` for clear instruction

### ✅ Critical Failure PR Creation
For critical deployment steps (server_connection, configure_backend, setup_webserver, final_verification):
- **Both** an issue AND a pull request are created
- PR includes dedicated branch for the fix
- @copilot is assigned to both issue and PR for faster resolution

### ✅ Enhanced Issue Content
Issues now include:
- Direct @copilot instructions in title and body
- Detailed error analysis and context
- Step-by-step troubleshooting commands
- Complete deployment logs
- Server and domain information
- Priority and categorization labels

### ✅ PAT Token Integration
- Uses existing GitHub authentication from orchestrator parameters
- Supports `--github-token` and `--github-user` command line arguments
- Supports `GITHUB_TOKEN` and `GITHUB_PAT` environment variables
- Falls back gracefully when no token is provided

## Usage

### Command Line with PAT
```bash
# Standard deployment with @copilot integration
python ai_deployment_orchestrator.py --server myserver.com --domain mydomain.com --github-user USERNAME --github-token ghp_YOUR_TOKEN

# Environment variable method (recommended)
export GITHUB_TOKEN="ghp_YOUR_TOKEN"
python ai_deployment_orchestrator.py --server myserver.com --domain mydomain.com
```

### Automatic Behavior on Failure

When any deployment step fails:

1. **Issue Creation**: 
   - Title: `🚨 Deployment Failed: {deployment_id} - {step} - @copilot please fix`
   - Assigned to: `@copilot`
   - Labels: `deployment-failure`, `copilot-fix-needed`, `priority-high`, etc.

2. **PR Creation** (for critical failures):
   - Title: `🔧 Fix deployment failure: {step} ({deployment_id})`
   - Branch: `fix/deployment-{deployment_id}-{step}`
   - Assigned to: `@copilot`
   - Includes testing checklist and validation steps

## Example Workflow

```
1. Run deployment: python ai_deployment_orchestrator.py --server prod.com --domain app.com --github-token ghp_xyz
2. Failure occurs at "configure_backend" step
3. Orchestrator automatically creates:
   - GitHub Issue #123 assigned to @copilot
   - GitHub PR #124 assigned to @copilot (since it's a critical step)
4. @copilot analyzes the failure and creates fixes
5. User can review and merge the PR to resolve the deployment issue
```

## Labels Added

| Label | Purpose |
|-------|---------|
| `copilot-fix-needed` | Triggers @copilot attention |
| `deployment-failure` | Categorizes as deployment issue |
| `priority-high` | Indicates high priority for deployment failures |
| `step-{step-name}` | Identifies which deployment step failed |
| `server-{hostname}` | Tags the specific server |

## Files Modified

- `scripts/deployment/github_integration.py`: Enhanced issue/PR creation with @copilot assignment
- `ai_deployment_orchestrator.py`: Updated failure handling to use @copilot features
- Added test and demo scripts for validation

## Testing

Run the test suite to verify functionality:

```bash
# Basic functionality test
python3 test_copilot_assignment.py

# Demo with mock data
python3 demo_copilot_assignment.py

# Live test with real GitHub token
export GITHUB_TOKEN="ghp_your_token"
python3 demo_copilot_assignment.py
```

## Benefits

1. **Automatic Resolution**: @copilot begins working on fixes immediately
2. **Reduced Downtime**: Faster identification and resolution of deployment issues  
3. **Comprehensive Context**: All necessary information provided to @copilot
4. **Prioritized Handling**: Critical failures get both issues and PRs
5. **Audit Trail**: Full deployment context preserved in GitHub

## Security

- PAT tokens are handled securely via environment variables
- Tokens are not logged or exposed in issue content
- Uses existing GitHub authentication patterns from the repository
- Private repository issues maintain confidentiality