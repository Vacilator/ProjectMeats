# ProjectMeats Production Configuration - User Guide

## Quick Start

When deploying ProjectMeats to production, the AI Deployment Orchestrator will now prompt you for essential configuration settings to ensure a secure, customized deployment.

## What You'll Be Asked For

### 1. Domain Configuration
- **Your domain name** (e.g., `example.com`, `mycompany.com`)
- Used for: CORS settings, SSL certificates, allowed hosts

### 2. Database Configuration  
- **Database name** (default: `projectmeats_prod`)
- **Database username** (default: `projectmeats_user`)
- **Database password** (you choose a secure password)

### 3. Company Information (Optional)
- **Company name** (default: `ProjectMeats`)
- **Company email** (e.g., `info@yourcompany.com`)
- **Company phone** (optional)
- **Company address** (optional)

### 4. Email Configuration (Optional)
- **SMTP server** (e.g., `smtp.gmail.com`)
- **Email username and password** for sending notifications
- Can be configured later if skipped

### 5. Security Settings
- **SSL/HTTPS** (recommended: Yes)
- System automatically configures secure production settings

## What Happens Automatically

✅ **Django Secret Key** - Auto-generated 50-character secure key  
✅ **Security Headers** - HSTS, XSS protection, etc.  
✅ **Database Creation** - PostgreSQL database and user created with your credentials  
✅ **Environment File** - Secure .env file generated with all settings  
✅ **Permissions** - Files secured with proper access permissions  

## Sample Interaction

```bash
$ python ai_deployment_orchestrator.py --server=myserver.com --domain=mydomain.com

============================================================
  ProjectMeats Production Configuration  
============================================================

✓ Django secret key generated automatically

Domain Configuration:
✓ Domain configured: mydomain.com

Database Configuration:
Setting up PostgreSQL database configuration...
Database name [projectmeats_prod]: 
Database username [projectmeats_user]: 
Database password (will be hidden): ********
✓ Database configuration collected

Company Information (Optional):
Company name [ProjectMeats]: My Company
Company email (optional): info@mydomain.com
✓ Company information configured

Security Configuration:
✓ SSL/HTTPS security will be enabled

============================================================
  Configuration Summary
============================================================
Domain: mydomain.com
Database: projectmeats_prod
Database User: projectmeats_user
Company: My Company
SSL enabled: Yes
✓ Production environment file created successfully
```

## Tips for Success

### Database Passwords
- Choose a strong password with letters, numbers, and symbols
- Keep it secure - you'll need it for any future database access
- The system will test connectivity automatically

### Domain Configuration
- Use your actual domain name (not IP address) for proper SSL/HTTPS
- Include both `domain.com` and `www.domain.com` if needed
- DNS should already point to your server

### Email Configuration  
- Gmail users: Use "App Passwords" instead of your regular password
- Can be skipped during deployment and configured later
- Used for system notifications and password resets

### Company Information
- Used in email templates and system branding  
- All fields are optional but improve user experience
- Can be updated later by modifying the .env file

## Security Features

🔒 **No Hardcoded Passwords** - All credentials are user-provided  
🔒 **Encrypted Storage** - Sensitive files have restricted permissions  
🔒 **Production Security** - HTTPS, secure cookies, security headers enabled  
🔒 **Secure Key Generation** - Cryptographically secure Django secret keys  

## After Deployment

Your production environment will have:

- **Environment file**: `/opt/projectmeats/backend/.env`
- **Database**: PostgreSQL with your custom credentials
- **Security**: Production-ready HTTPS and security settings
- **Logging**: Comprehensive logging in `/opt/projectmeats/logs/`
- **Backups**: Backup directory at `/opt/projectmeats/backups/`

## Need Help?

- **Configuration errors**: Check the deployment logs for details
- **Database issues**: Verify credentials and PostgreSQL service status  
- **Domain issues**: Ensure DNS is properly configured
- **SSL problems**: Check domain accessibility and certificate installation

The AI Deployment Orchestrator includes automatic error detection and recovery for most common issues!