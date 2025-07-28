# Bug Reporting Feature

The ProjectMeats application includes a comprehensive bug reporting system that automatically creates GitHub issues assigned to copilot agents for efficient bug tracking and resolution.

## Features

### User Interface
- **Header Button**: Red "🐛 Report Bug" button in the top navigation bar
- **Floating Action Button**: Circular bug report button in the bottom-right corner
- **Modal Form**: Professional, user-friendly bug reporting interface

### Bug Report Form
The form captures comprehensive information for effective bug diagnosis:

#### Required Fields
- **Bug Title**: Brief summary of the issue
- **Description**: Detailed description of what happened
- **Priority**: Low, Medium, High, or Critical

#### Optional Details
- **Steps to Reproduce**: Numbered steps to recreate the bug
- **Expected Behavior**: What should have happened
- **Actual Behavior**: What actually happened
- **Screenshot**: Image file upload for visual evidence
- **Email**: Contact email for updates

#### Auto-Captured Context
- Current page URL and title
- Browser information (user agent, language, platform, etc.)
- Application state (route, timestamp, etc.)
- Screen and window dimensions

### GitHub Integration

When a bug report is submitted:

1. **API Call**: Data is sent to Django REST API endpoint
2. **GitHub Issue Creation**: Automatic issue creation via GitHub API
3. **Copilot Assignment**: Issues are auto-assigned to 'copilot' user
4. **Structured Content**: Well-formatted issue body with all details
5. **Smart Labels**: Automatic labeling based on priority and context

#### Issue Format
```
🐛 Bug Report: [Title]

**Reported by:** User Name
**Email:** user@example.com
**Priority:** High
**Reported on:** 2024-01-15 10:30:00 UTC

### 📝 Description
[User's description]

### 🔄 Steps to Reproduce
[User's steps]

### 📊 Expected vs Actual Behavior
**Expected:** [Expected behavior]
**Actual:** [Actual behavior]

### 🔧 Technical Context
**URL:** http://localhost:3000/dashboard
**Page:** Dashboard
**Browser Info:**
- userAgent: Mozilla/5.0...
- language: en-US
- platform: Linux

### 📷 Screenshot
[If provided]

---
*This issue was automatically created from a bug report in ProjectMeats.*
*Bug Report ID: #123*
```

#### Labels Applied
- `bug` - Identifies this as a bug report
- `auto-reported` - Indicates automatic creation
- `priority:low/medium/high/critical` - Priority level
- `component:[area]` - Based on URL context (dashboard, suppliers, etc.)

## API Endpoints

### Bug Reports API
- `GET /api/v1/bug-reports/` - List bug reports (auth required)
- `POST /api/v1/bug-reports/` - Create new bug report
- `GET /api/v1/bug-reports/{id}/` - Get specific bug report
- `POST /api/v1/bug-reports/{id}/retry_github_creation/` - Retry failed GitHub creation
- `GET /api/v1/bug-reports/stats/` - Get bug report statistics
- `GET /api/v1/bug-reports/user_reports/` - Get current user's reports

### Permissions
- Regular users can only see their own bug reports
- Staff users can see all bug reports
- All authenticated users can create bug reports

## Configuration

### Environment Variables
Set these in your `.env` file:

```bash
# GitHub Integration
GITHUB_TOKEN=your-github-personal-access-token
GITHUB_REPO=Vacilator/ProjectMeats
GITHUB_COPILOT_USERNAME=copilot
```

### GitHub Token Requirements
The GitHub token needs the following permissions:
- `repo` - Full repository access
- `issues` - Create and modify issues

## Error Handling

### GitHub API Failures
- Bug reports are still saved locally even if GitHub creation fails
- Failed reports are marked with status "failed" and error message
- Manual retry available through API endpoint
- Graceful degradation ensures user experience is maintained

### Frontend Error Handling
- Form validation prevents invalid submissions
- Network errors are displayed to users
- Success feedback confirms submission
- Automatic modal closure after successful submission

## Usage Examples

### For End Users
1. Click the "🐛 Report Bug" button in the header or bottom-right
2. Fill out the bug title and description (required)
3. Optionally add reproduction steps, expected/actual behavior
4. Upload screenshot if helpful
5. Submit - a GitHub issue will be created automatically

### For Developers
```python
# Create a bug report programmatically
from apps.bug_reports.models import BugReport, BugReportPriority

bug_report = BugReport.objects.create(
    reporter=user,
    reporter_email=user.email,
    title="API endpoint returning 500 error",
    description="The /api/v1/suppliers/ endpoint is returning 500 errors",
    priority=BugReportPriority.HIGH,
    current_url="http://localhost:3000/suppliers",
    page_title="Suppliers",
    browser_info={"userAgent": "..."},
    application_state={"route": "/suppliers"}
)
```

### For Administrators
- View all bug reports in Django admin at `/admin/bug_reports/bugreport/`
- Monitor GitHub issues in the repository
- Review statistics through the API endpoints

## Testing

The feature includes comprehensive tests:
- Model tests for bug report creation and properties
- API tests for CRUD operations and permissions
- GitHub service tests with mocked API calls
- End-to-end frontend testing

Run tests with:
```bash
cd backend
python manage.py test apps.bug_reports
```

## Benefits

1. **Streamlined Reporting**: Users can report bugs without leaving the application
2. **Rich Context**: Automatic capture of technical details aids debugging
3. **Immediate Assignment**: Issues are instantly assigned to copilot for fast response
4. **Consistent Format**: Structured GitHub issues improve triage efficiency
5. **Audit Trail**: Complete history of bug reports and their resolution status
6. **User Feedback Loop**: Optional email contact for progress updates

This bug reporting system significantly improves the application's maintainability and user satisfaction by making it easy to report issues and ensuring they receive prompt attention from AI agents.