# ProjectMeats GitHub PAT Authentication - Usage Examples

## Problem Solved
The deployment script now supports Personal Access Token (PAT) authentication as requested in the issue. This resolves the GitHub authentication error:
```
remote: Invalid username or token. Password authentication is not supported for Git operations.
```

## How to Use the Enhanced Authentication

### Method 1: Environment Variables (Recommended)
```bash
# Set your GitHub credentials
export GITHUB_USER=Vacilator
export GITHUB_TOKEN=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

# Run deployment with environment preservation
sudo -E ./master_deploy.py
```

### Method 2: Command Line Arguments
```bash
sudo ./master_deploy.py --github-user=Vacilator --github-token=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
```

### Method 3: Interactive Setup
```bash
# Run normally - it will prompt for credentials when needed
sudo ./master_deploy.py

# When prompted, choose option 2 for PAT authentication
# Enter your username: Vacilator
# Enter your token: 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
```

## What Was Enhanced

### 1. master_deploy.py
- Added `get_github_authentication()` method for credential collection
- Enhanced `download_application()` with PAT authentication priority
- Added environment variable support (GITHUB_USER, GITHUB_TOKEN)
- Added command-line arguments (--github-user, --github-token)
- Added comprehensive error handling with actionable guidance

### 2. deploy_production.py
- Enhanced generated shell scripts to support PAT authentication
- Added environment variable detection in generated scripts
- Improved fallback methods (PAT → Public → SSH)
- Enhanced error messages with multiple solution paths

### 3. auth_helper.sh
- Added environment variable setup guidance
- Enhanced PAT setup instructions
- Added sudo -E usage examples

## Authentication Flow

1. **PAT Authentication** (if credentials provided)
   ```bash
   git clone https://USERNAME:TOKEN@github.com/Vacilator/ProjectMeats.git
   ```

2. **Public Access** (fallback)
   ```bash
   git clone https://github.com/Vacilator/ProjectMeats.git
   ```

3. **Direct Download** (fallback)
   ```bash
   curl -L https://github.com/Vacilator/ProjectMeats/archive/main.zip
   ```

4. **Detailed Error Help** (if all fail)
   - Instructions for PAT setup
   - SSH key setup guidance
   - Manual transfer methods
   - Link to no-auth deployment script

## Security Features
- Credentials masked in logs
- Environment variable support (no command-line exposure)
- Token validation before usage
- Clear cleanup instructions

This enhancement directly addresses the user's issue by implementing the exact PAT authentication format they were successfully using manually.