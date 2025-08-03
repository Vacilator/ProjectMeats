# ProjectMeats AI Assistant - Quick Setup Reference

## 🚨 Solving "Authentication credentials were not provided"

This error typically occurs when the AI Assistant backend isn't properly configured. Here's the **fastest solution**:

### Step 1: Run the Interactive Setup
```bash
cd ProjectMeats
python setup_ai_assistant.py
```

This will guide you through:
- ✅ Django authentication setup
- ✅ Database configuration  
- ✅ AI provider credentials
- ✅ Environment variables
- ✅ Admin user creation

### Step 2: Start the Servers
```bash
# Terminal 1: Backend
cd backend
python manage.py runserver

# Terminal 2: Frontend  
cd frontend
npm start
```

### Step 3: Login
- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: WATERMELON1219 (or what you set during setup)

## Alternative Quick Fixes

### Fix 1: Check Environment Files
```bash
# Verify files exist
ls -la backend/.env
ls -la frontend/.env.local

# If missing, run:
python setup_ai_assistant.py
```

### Fix 2: Create Admin User
```bash
cd backend
python manage.py createsuperuser
```

### Fix 3: Verify Django Settings
```bash
cd backend
python manage.py check
```

### Fix 4: Reset Everything
```bash
# Delete old config and start fresh
rm backend/.env
rm frontend/.env.local
rm backend/db.sqlite3

# Run complete setup
python setup_ai_assistant.py
```

## What the Setup Configures

### Backend (.env)
```bash
# Authentication
SECRET_KEY=auto-generated-secure-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database  
DATABASE_URL=sqlite:///db.sqlite3

# CORS (fixes frontend connection)
CORS_ALLOWED_ORIGINS=http://localhost:3000

# AI Provider (choose one)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
# OR leave empty for mock AI responses
```

### Frontend (.env.local)
```bash
# API Connection
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_AI_ASSISTANT_ENABLED=true
```

## AI Provider Options

| Provider | Setup Required | Cost | Features |
|----------|---------------|------|----------|
| **Mock** | None | Free | Testing, demo responses |
| **OpenAI** | API key | Paid | GPT-3.5, GPT-4 |
| **Anthropic** | API key | Paid | Claude models |
| **Azure OpenAI** | Azure setup | Paid | Enterprise GPT |

### Getting API Keys

**OpenAI:**
1. Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create account and add billing
3. Generate API key (starts with `sk-`)

**Anthropic:**
1. Visit [console.anthropic.com](https://console.anthropic.com)
2. Create account
3. Generate API key

**Mock (No Setup):**
- Select "Mock Provider" during setup
- No API key needed
- Perfect for testing

## Common Issues

### Issue: "Module not found: django"
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "npm command not found"
- Install Node.js from [nodejs.org](https://nodejs.org)
- Restart terminal

### Issue: "Permission denied"
```bash
# Linux/Mac - fix permissions
chmod +x setup_ai_assistant.py
```

### Issue: Windows PowerShell Errors
```cmd
# Use Command Prompt instead of PowerShell
setup_windows.bat
```

## Platform-Specific Commands

### Windows
```cmd
setup_windows.bat
```

### Linux/macOS
```bash
python setup_ai_assistant.py
# or
make setup
```

### Manual Setup
```bash
# Backend only
python setup.py --backend

# AI assistant only  
python setup.py --ai-only

# Full guided setup
python setup_ai_assistant.py
```

## Validation

Test your setup:
```bash
python test_setup.py
```

Should show:
```
🎉 All tests passed! Setup is ready to use.
```

## Need Help?

1. **Check logs:**
   ```bash
   cd backend
   python manage.py runserver --verbosity=2
   ```

2. **Documentation:**
   - `docs/ai_assistant_setup.md` - Comprehensive guide
   - `docs/setup-and-development.md` - Development guide

3. **Reset and retry:**
   ```bash
   python setup_ai_assistant.py
   ```

The interactive setup wizard is designed to solve 99% of configuration issues automatically. If you're still having problems, create an issue with your error messages.