# ProjectMeats AI Deployment - Complete Execution Guide

## 🎯 Overview: Where and How to Execute

This guide explains **exactly where and how** to run each part of the AI deployment system, including which environment to use and in what order.

### 📍 Execution Context Summary

| Component | Where to Run | Environment | Purpose |
|-----------|--------------|-------------|---------|
| **Setup Wizard** | 💻 **Local Machine** | PowerShell/Terminal | Configure deployment system |
| **Configuration** | 💻 **Local Machine** | Any text editor | Edit server settings |
| **Deployment Script** | 💻 **Local Machine** | PowerShell/Terminal | Orchestrates remote deployment |
| **Testing** | 💻 **Local Machine** | PowerShell/Terminal | Verify system readiness |
| **Actual Deployment** | 🌐 **Remote Server** | Automated via SSH | ProjectMeats application |

> **Key Point**: Everything runs from your LOCAL machine. The deployment system connects to your REMOTE server via SSH and deploys ProjectMeats there automatically.

---

## 🖥️ Environment-Specific Instructions

### Windows (PowerShell)

#### Prerequisites
```powershell
# Check Python installation
python --version
# Should show Python 3.8 or higher

# Check Git installation  
git --version

# Install dependencies if needed
# Download Python from: https://python.org
# Download Git from: https://git-scm.com/downloads
```

#### Execution Commands
```powershell
# 1. Navigate to project directory
cd C:\path\to\ProjectMeats

# 2. Run setup wizard (LOCAL)
python setup_ai_deployment.py

# 3. Test system readiness (LOCAL)
python test_ai_deployment.py

# 4. Deploy to remote server (LOCAL → REMOTE)
.\ai_deploy.sh --interactive
# Note: PowerShell can run .sh files if you have Git Bash installed
# Alternative: Use bash if available, or run Python directly:
python ai_deployment_orchestrator.py --interactive
```

### Linux/Ubuntu (Bash)

#### Prerequisites
```bash
# Check installations
python3 --version
git --version

# Install if needed
sudo apt update
sudo apt install python3 python3-pip git openssh-client
```

#### Execution Commands
```bash
# 1. Navigate to project directory
cd /path/to/ProjectMeats

# 2. Run setup wizard (LOCAL)
python3 setup_ai_deployment.py

# 3. Test system readiness (LOCAL)
python3 test_ai_deployment.py

# 4. Deploy to remote server (LOCAL → REMOTE)
./ai_deploy.sh --interactive

# Make script executable if needed
chmod +x ai_deploy.sh
```

### macOS (Terminal)

#### Prerequisites
```bash
# Check installations
python3 --version
git --version

# Install if needed (using Homebrew)
brew install python git

# Or install Python from python.org and Git from git-scm.com
```

#### Execution Commands
```bash
# 1. Navigate to project directory
cd /path/to/ProjectMeats

# 2. Run setup wizard (LOCAL)
python3 setup_ai_deployment.py

# 3. Test system readiness (LOCAL)  
python3 test_ai_deployment.py

# 4. Deploy to remote server (LOCAL → REMOTE)
./ai_deploy.sh --interactive

# Make script executable if needed
chmod +x ai_deploy.sh
```

---

## 📋 Step-by-Step Execution Workflow

### Phase 1: Local Setup (Run on YOUR computer)

#### Step 1: Get the Code
```bash
# Clone the repository (if you haven't already)
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Or navigate to existing clone
cd /path/to/your/ProjectMeats
```

#### Step 2: Install Dependencies (LOCAL)
```bash
# Install Python dependencies for deployment system
pip install -r ai_deployment_requirements.txt

# This installs tools needed for SSH connection and deployment orchestration
```

#### Step 3: Run Setup Wizard (LOCAL)
```bash
# Start the interactive setup
python setup_ai_deployment.py

# This wizard will:
# - Generate SSH keys for server access
# - Ask for your server details (IP, domain, username)
# - Configure deployment settings
# - Create configuration files
```

**What the Setup Wizard Does:**
- ✅ Creates SSH keys on your LOCAL machine
- ✅ Asks for your REMOTE server details
- ✅ Configures connection settings
- ✅ Creates `ai_deployment_config.json` on your LOCAL machine
- ✅ Shows you the public key to add to your server

#### Step 4: Configure Server Access (ONE-TIME SETUP)

After the setup wizard, you need to add the SSH key to your server:

```bash
# The wizard will show you a command like this:
# Copy this key to your server's ~/.ssh/authorized_keys file:

# Option A: Copy key manually
cat ~/.ssh/id_ed25519.pub
# Copy the output and paste it into your server's ~/.ssh/authorized_keys

# Option B: Use ssh-copy-id (if available)
ssh-copy-id -i ~/.ssh/id_ed25519.pub your-username@your-server.com
```

#### Step 5: Test Connection (LOCAL)
```bash
# Verify everything is set up correctly
python test_ai_deployment.py

# This will:
# - Check if configuration exists
# - Test SSH connection to your server
# - Verify all deployment files are ready
# - Show you exactly what commands to run next
```

### Phase 2: Deployment Execution (LOCAL → REMOTE)

#### Interactive Deployment (Recommended)
```bash
# Start interactive deployment
./ai_deploy.sh --interactive

# This will:
# 1. Connect to your remote server via SSH
# 2. Install ProjectMeats and dependencies on the server
# 3. Configure the web server on the remote server
# 4. Set up SSL certificates on the remote server
# 5. Start the application on the remote server
```

#### Direct Deployment (Advanced)
```bash
# Deploy directly with parameters
./ai_deploy.sh --server myserver.com --domain mydomain.com

# Test connection only
./ai_deploy.sh --test --server myserver.com

# Use predefined profile
./ai_deploy.sh --profile production
```

### Phase 3: Verification (LOCAL)

```bash
# Check deployment status
python test_ai_deployment.py

# Monitor deployment logs
tail -f logs/deployment_*.log

# Test the deployed application
curl https://yourdomain.com
```

---

## 🌐 Server Requirements

Your **REMOTE server** needs:
- ✅ SSH access enabled
- ✅ Sudo privileges for your user
- ✅ Internet connection
- ✅ Ubuntu 18.04+ or similar Linux distribution

Your **LOCAL machine** needs:
- ✅ Python 3.8+
- ✅ Git
- ✅ SSH client (built into most systems)
- ✅ Terminal/PowerShell access

---

## 🔄 Complete Example Workflow

### Windows PowerShell Example
```powershell
# 1. Setup (LOCAL - run once)
cd C:\Projects\ProjectMeats
python -m pip install -r ai_deployment_requirements.txt
python setup_ai_deployment.py

# 2. Configure server access (ONE-TIME)
# Follow wizard instructions to add SSH key to server

# 3. Test readiness (LOCAL)
python test_ai_deployment.py

# 4. Deploy (LOCAL → REMOTE)
python ai_deployment_orchestrator.py --interactive

# 5. Verify (LOCAL)
python test_ai_deployment.py
```

### Linux/Mac Example
```bash
# 1. Setup (LOCAL - run once)
cd ~/Projects/ProjectMeats
pip3 install -r ai_deployment_requirements.txt
python3 setup_ai_deployment.py

# 2. Configure server access (ONE-TIME)
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@yourserver.com

# 3. Test readiness (LOCAL)
python3 test_ai_deployment.py

# 4. Deploy (LOCAL → REMOTE)
./ai_deploy.sh --interactive

# 5. Verify (LOCAL)
python3 test_ai_deployment.py
```

---

## 🚨 Important Notes

### What Runs Where
- **📱 Local Machine**: Setup, configuration, deployment orchestration, monitoring
- **🌐 Remote Server**: Only the final ProjectMeats application (deployed automatically)
- **🔗 Connection**: SSH from local to remote (encrypted and secure)

### File Locations
- **Local Config**: `./ai_deployment_config.json` (on your computer)
- **Local Logs**: `./logs/` directory (on your computer)
- **Remote App**: `/var/www/ProjectMeats/` (on your server, created automatically)

### Security
- 🔐 SSH keys are generated locally and never transmitted unencrypted
- 🔒 All communication uses SSH encryption
- 🛡️ No passwords stored in config files
- 🔑 You control access via SSH key management

---

## 🆘 Troubleshooting by Environment

### Windows Issues
```powershell
# If .sh files don't run in PowerShell:
python ai_deployment_orchestrator.py --interactive

# If Python is not found:
python.exe ai_deployment_orchestrator.py --interactive

# If permission errors:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux/Mac Issues
```bash
# If script not executable:
chmod +x ai_deploy.sh

# If Python command not found:
python3 setup_ai_deployment.py  # Use python3 instead of python

# If SSH key issues:
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519  # Generate manually if needed
```

### Connection Issues
```bash
# Test SSH connection manually:
ssh -i ~/.ssh/id_ed25519 username@your-server.com

# Test with verbose output:
ssh -v username@your-server.com

# Check SSH key is added to server:
ssh username@your-server.com "cat ~/.ssh/authorized_keys"
```

---

## 🎉 Success Indicators

### Setup Complete
- ✅ SSH keys generated in `~/.ssh/`
- ✅ Config file created: `ai_deployment_config.json`
- ✅ Test script shows "SYSTEM READY TO DEPLOY"

### Deployment Complete
- ✅ No errors in deployment output
- ✅ Application accessible at your domain
- ✅ SSL certificate working (https://)
- ✅ Backend and frontend both responding

### Verification Complete
- ✅ `curl https://yourdomain.com` returns HTML
- ✅ `curl https://yourdomain.com/api/` returns API response
- ✅ Web browser shows ProjectMeats application

---

## 📞 Quick Reference Commands

| Task | Windows PowerShell | Linux/Mac Terminal |
|------|-------------------|-------------------|
| **Setup** | `python setup_ai_deployment.py` | `python3 setup_ai_deployment.py` |
| **Test** | `python test_ai_deployment.py` | `python3 test_ai_deployment.py` |
| **Deploy** | `python ai_deployment_orchestrator.py --interactive` | `./ai_deploy.sh --interactive` |
| **Check Status** | `python test_ai_deployment.py` | `python3 test_ai_deployment.py` |

Remember: **Everything runs from your local machine** - the deployment system automatically connects to and configures your remote server!