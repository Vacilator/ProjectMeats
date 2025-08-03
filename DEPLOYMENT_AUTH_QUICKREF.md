# ProjectMeats Deployment Authentication - Quick Reference

## The Problem

**Error:** `remote: Invalid username or token. Password authentication is not supported for Git operations.`

**Cause:** GitHub deprecated password authentication for Git operations in August 2021.

## ✅ Quick Solutions

### 1. 🚀 No-Authentication Method (FASTEST)
```bash
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash
```
**Why this works:** Downloads code via public GitHub APIs, no authentication needed.

### 2. 🔑 Personal Access Token
1. GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. **Option A - Environment Variables (Recommended):**
```bash
export GITHUB_USER=your_username
export GITHUB_TOKEN=your_token
sudo -E ./master_deploy.py
```
4. **Option B - Command Line:**
```bash
sudo ./master_deploy.py --github-user=your_username --github-token=your_token
```
5. **Option C - Direct Git Clone:**
```bash
git clone https://USERNAME:TOKEN@github.com/Vacilator/ProjectMeats.git
```

### 3. 🔐 SSH Key Setup
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@domain.com"

# Add public key to GitHub → Settings → SSH keys
cat ~/.ssh/id_ed25519.pub

# Clone with SSH
git clone git@github.com:Vacilator/ProjectMeats.git
```

### 4. 📋 Manual Transfer
1. Download on local machine: `git clone https://github.com/Vacilator/ProjectMeats.git`
2. Create archive: `tar -czf projectmeats.tar.gz ProjectMeats/`
3. Transfer to server: `scp projectmeats.tar.gz user@server:/tmp/`
4. Extract: `tar -xzf /tmp/projectmeats.tar.gz`

## 🛠️ Helper Scripts

- **Authentication help:** `curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/auth_helper.sh | bash`
- **Deployment readiness:** `./verify_deployment_readiness.sh`
- **No-auth deployment:** `./deploy_no_auth.sh`

## 📖 Full Documentation

- [Complete Authentication Guide](docs/deployment_authentication_guide.md)
- [Production Deployment Guide](docs/production_deployment.md)
- [Quick Setup Guide](docs/production_setup_guide.md)

---
**Recommended:** Use Method 1 (No-Authentication) for fastest deployment!