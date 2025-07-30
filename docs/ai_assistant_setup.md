# AI Assistant Setup & Configuration Guide

## Overview

The ProjectMeats AI Assistant provides intelligent automation for meat market operations, including document processing, business analytics, and conversational assistance. This guide covers the complete setup and configuration process.

## Quick Setup (Recommended)

### Interactive Setup Wizard

Run the interactive setup wizard for guided configuration:

```bash
python setup_ai_assistant.py
```

This wizard will:
- ✅ Configure authentication and database
- ✅ Set up AI provider credentials (OpenAI, Anthropic, etc.)
- ✅ Create environment files with all necessary variables
- ✅ Install dependencies and initialize the database
- ✅ Test the configuration and provide next steps

## Manual Setup

If you prefer manual configuration or need to troubleshoot:

### 1. Backend Environment Configuration

Create `backend/.env` with the following variables:

```bash
# Django Core Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# CORS Settings (for React frontend)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# AI Provider Configuration (choose one)

# Option 1: OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Option 2: Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-01

# Option 3: Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-sonnet

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# File Upload Settings
MEDIA_ROOT=media/
STATIC_ROOT=static/

# Logging Level
LOG_LEVEL=INFO
```

### 2. Frontend Environment Configuration

Create `frontend/.env.local`:

```bash
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development

# Feature Flags
REACT_APP_AI_ASSISTANT_ENABLED=true

# Development Settings
GENERATE_SOURCEMAP=false
```

### 3. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
```

### 4. Initialize Database

```bash
cd backend

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Create AI configuration (optional)
python manage.py shell
```

In the Django shell:
```python
from apps.ai_assistant.models import AIConfiguration

# Create OpenAI configuration
AIConfiguration.objects.create(
    name="openai_primary",
    provider="openai",
    model_name="gpt-3.5-turbo",
    api_key_name="OPENAI_API_KEY",
    configuration={
        "temperature": 0.7,
        "max_tokens": 2000
    },
    is_active=True,
    is_default=True
)
```

## AI Provider Setup

### OpenAI Setup

1. **Get API Key:**
   - Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key (starts with `sk-`)

2. **Configuration:**
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4, gpt-4-turbo
   OPENAI_TEMPERATURE=0.7
   OPENAI_MAX_TOKENS=2000
   ```

3. **Billing:** Ensure you have billing set up in your OpenAI account.

### Azure OpenAI Setup

1. **Azure Setup:**
   - Create an Azure OpenAI resource in Azure Portal
   - Deploy a model (e.g., gpt-35-turbo)
   - Get your endpoint URL and API key

2. **Configuration:**
   ```bash
   AZURE_OPENAI_API_KEY=your-azure-key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   AZURE_OPENAI_API_VERSION=2024-02-01
   ```

### Anthropic Setup

1. **Get API Key:**
   - Visit [Anthropic Console](https://console.anthropic.com/)
   - Create an API key
   - Copy the key

2. **Configuration:**
   ```bash
   ANTHROPIC_API_KEY=your-anthropic-key
   ANTHROPIC_MODEL=claude-3-sonnet  # or claude-3-haiku, claude-3-opus
   ```

### Mock Provider (Testing)

For development and testing without API costs:

```bash
# No API key required - uses mock responses
AI_PROVIDER=mock
```

## Authentication Configuration

### Django REST Framework Authentication

The AI Assistant uses Django REST Framework with:

- **Session Authentication**: For web-based access
- **Token Authentication**: For API access

### Creating API Tokens

For programmatic access, create tokens:

```bash
cd backend
python manage.py shell
```

```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create token for a user
user = User.objects.get(username='admin')
token, created = Token.objects.get_or_create(user=user)
print(f"Token: {token.key}")
```

### Frontend Authentication

The frontend uses session authentication by default. Update `frontend/src/services/auth.ts` if needed:

```typescript
// API client configuration
const authClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
  withCredentials: true, // Include session cookies
});
```

## Common Issues & Solutions

### Issue: "Authentication credentials were not provided"

**Cause:** Missing or incorrect authentication setup.

**Solutions:**

1. **Check Environment Variables:**
   ```bash
   # Verify .env files exist
   ls -la backend/.env
   ls -la frontend/.env.local
   ```

2. **Verify API URLs:**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/api/v1/auth/status/
   ```

3. **Check CORS Configuration:**
   ```python
   # In backend/.env
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

4. **Create Admin User:**
   ```bash
   cd backend
   python manage.py createsuperuser
   ```

### Issue: AI Provider Not Working

**Solutions:**

1. **Check API Key:**
   ```bash
   # Verify key is set
   echo $OPENAI_API_KEY
   ```

2. **Test AI Configuration:**
   ```bash
   cd backend
   python manage.py shell
   ```
   ```python
   from apps.ai_assistant.services.ai_service import ai_service
   response, metadata = ai_service.generate_chat_response("Test message")
   print(response)
   ```

3. **Check AI Configuration in Database:**
   ```python
   from apps.ai_assistant.models import AIConfiguration
   configs = AIConfiguration.objects.filter(is_active=True)
   for config in configs:
       print(f"{config.name}: {config.provider} - {config.model_name}")
   ```

### Issue: Dependencies Not Installing

**Solutions:**

1. **Python Dependencies:**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   
   # Install dependencies
   pip install -r backend/requirements.txt
   ```

2. **Node.js Dependencies:**
   ```bash
   # Clear npm cache
   npm cache clean --force
   
   # Install dependencies
   cd frontend
   npm install
   ```

### Issue: Database Migrations Failing

**Solutions:**

1. **Reset Database (Development):**
   ```bash
   cd backend
   rm db.sqlite3
   python manage.py migrate
   ```

2. **Check Migration Status:**
   ```bash
   python manage.py showmigrations
   ```

3. **Manual Migration:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

## Development Workflow

### 1. Start Development Servers

```bash
# Terminal 1: Backend
cd backend
python manage.py runserver

# Terminal 2: Frontend
cd frontend
npm start
```

### 2. Access Applications

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/v1
- **Admin Panel:** http://localhost:8000/admin
- **API Documentation:** http://localhost:8000/api/docs/

### 3. Test AI Assistant

1. **Login** to the frontend
2. **Navigate** to AI Assistant section
3. **Send a test message:** "Hello, test the AI assistant"
4. **Upload a document** to test document processing

## Production Configuration

### Environment Variables

```bash
# Production settings
DEBUG=False
SECRET_KEY=generate-a-strong-secret-key
ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Email (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
```

### Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Use PostgreSQL database
- [ ] Configure proper SECRET_KEY
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS for production domains
- [ ] Set up email backend
- [ ] Configure static file serving
- [ ] Set up monitoring and logging

## Advanced Configuration

### Multiple AI Providers

Configure multiple AI providers for redundancy:

```python
# In Django shell
from apps.ai_assistant.models import AIConfiguration

# Primary OpenAI
AIConfiguration.objects.create(
    name="openai_primary",
    provider="openai",
    model_name="gpt-4",
    api_key_name="OPENAI_API_KEY",
    is_default=True
)

# Backup Anthropic
AIConfiguration.objects.create(
    name="anthropic_backup",
    provider="anthropic",
    model_name="claude-3-sonnet",
    api_key_name="ANTHROPIC_API_KEY",
    is_default=False
)
```

### Custom AI Models

For local or custom models:

```python
AIConfiguration.objects.create(
    name="local_model",
    provider="local",
    model_name="custom-model-v1",
    api_endpoint="http://localhost:8080/v1/chat/completions",
    configuration={
        "temperature": 0.7,
        "max_tokens": 2000
    }
)
```

### Performance Optimization

1. **Caching:**
   ```bash
   # Install Redis
   pip install redis
   
   # Configure caching in settings
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

2. **Database Optimization:**
   ```bash
   # Use PostgreSQL for better performance
   DATABASE_URL=postgresql://user:password@localhost/projectmeats
   ```

3. **AI Response Caching:**
   - Similar queries are cached for 1 hour
   - Configurable in AI service settings

## Support

If you encounter issues:

1. **Check logs:**
   ```bash
   # Backend logs
   cd backend
   python manage.py runserver --verbosity=2
   
   # Check debug.log file
   tail -f debug.log
   ```

2. **Run diagnostics:**
   ```bash
   python setup_ai_assistant.py --test-only
   ```

3. **Reset configuration:**
   ```bash
   # Re-run setup wizard
   python setup_ai_assistant.py --reset
   ```

For additional support, create an issue in the repository with:
- Error messages
- Environment configuration (without API keys)
- Steps to reproduce the issue