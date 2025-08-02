# ProjectMeats Deployment Authentication Solutions
# ================================================

This guide addresses GitHub authentication issues during production deployment and provides multiple solutions.

## 🚨 The Problem

If you encounter this error during deployment:
```
remote: Invalid username or token. Password authentication is not supported for Git operations.
fatal: Authentication failed for 'https://github.com/Vacilator/ProjectMeats.git/'
```

**This is because GitHub no longer supports password authentication for Git operations (deprecated August 2021).**

## ✅ Solutions (Choose One)

### Solution 1: No-Authentication Deployment (Recommended)

Use our special deployment script that downloads the code without requiring GitHub authentication:

```bash
# On your production server
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash
```

**This method:**
- ✅ No GitHub account needed
- ✅ No authentication setup required
- ✅ Downloads code via public GitHub APIs
- ✅ Falls back to multiple download methods
- ✅ Provides manual instructions if all else fails

### Solution 2: Personal Access Token (PAT)

If you prefer using `git clone`, set up a Personal Access Token:

#### Step 1: Create a PAT
1. Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Set expiration (recommend 90 days)
4. Select scopes: `repo` (for private repos) or `public_repo` (for public repos)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

#### Step 2: Use PAT for Deployment
```bash
# On your production server
git clone https://<YOUR_USERNAME>:<YOUR_TOKEN>@github.com/Vacilator/ProjectMeats.git
cd ProjectMeats
sudo ./deploy_production.py
```

Replace:
- `<YOUR_USERNAME>` with your GitHub username
- `<YOUR_TOKEN>` with the PAT you created

### Solution 3: SSH Key Authentication

Set up SSH keys for seamless authentication:

#### Step 1: Generate SSH Key on Server
```bash
# On your production server
ssh-keygen -t ed25519 -C "your-email@domain.com"
# Press Enter for default file location
# Optionally set a passphrase

# Display your public key
cat ~/.ssh/id_ed25519.pub
```

#### Step 2: Add SSH Key to GitHub
1. Copy the output from the `cat` command above
2. Go to GitHub.com → Settings → SSH and GPG keys
3. Click "New SSH key"
4. Paste your public key
5. Click "Add SSH key"

#### Step 3: Use SSH for Deployment
```bash
# On your production server
git clone git@github.com:Vacilator/ProjectMeats.git
cd ProjectMeats
sudo ./deploy_production.py
```

### Solution 4: Download Release Package

Download a pre-packaged release:

```bash
# Create working directory
mkdir -p /tmp/projectmeats && cd /tmp/projectmeats

# Download latest release
curl -L https://github.com/Vacilator/ProjectMeats/archive/refs/heads/main.tar.gz | tar -xz

# Move to installation directory
sudo mv ProjectMeats-main /home/projectmeats/app
sudo chown -R projectmeats:projectmeats /home/projectmeats
cd /home/projectmeats/app

# Run deployment
sudo python3 deploy_production.py
```

## 🔧 Quick Troubleshooting

### If you get "Permission denied (publickey)"
Your SSH key isn't properly configured. Use Solution 1 (No-Authentication) or Solution 2 (PAT) instead.

### If you get "Repository not found"
- Check your GitHub username in the URL
- Verify the repository name is correct
- Ensure your PAT has the right permissions

### If download methods fail
Your server might have limited internet access. Try the manual method:

1. **On your local machine:**
   ```bash
   git clone https://github.com/Vacilator/ProjectMeats.git
   tar -czf projectmeats.tar.gz ProjectMeats/
   ```

2. **Transfer to server:**
   ```bash
   scp projectmeats.tar.gz root@YOUR_SERVER_IP:/tmp/
   ```

3. **On server:**
   ```bash
   cd /tmp
   tar -xzf projectmeats.tar.gz
   sudo mv ProjectMeats /home/projectmeats/app
   cd /home/projectmeats/app
   sudo python3 deploy_production.py
   ```

## 🚀 Recommended Deployment Flow

For the fastest, most reliable deployment:

```bash
# Step 1: Use no-authentication method
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash

# Step 2: The script will guide you through the rest
# Follow the interactive prompts for your domain, database, etc.

# Step 3: Access your application
# Website: https://your-domain.com
# Admin: https://your-domain.com/admin/
```

## 🔒 Security Notes

- **PATs**: Treat them like passwords. Store securely and rotate regularly.
- **SSH Keys**: More secure than PATs. Use ed25519 keys when possible.
- **No-Auth Method**: Downloads from public GitHub APIs. Safe and recommended.

## 📞 Still Having Issues?

If none of these solutions work:

1. Check if your server has internet connectivity: `curl -I https://github.com`
2. Verify DNS resolution: `nslookup github.com`
3. Check firewall settings: `sudo ufw status`
4. Try using a different DNS server: `echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf`

## ✅ Success Verification

After successful deployment, verify everything works:

```bash
# Check services are running
sudo systemctl status projectmeats nginx postgresql

# Test your website
curl -I https://your-domain.com

# Check admin access
curl -I https://your-domain.com/admin/
```

---

**Choose Solution 1 (No-Authentication) for the easiest deployment experience!**