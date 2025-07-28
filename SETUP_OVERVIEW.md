# ProjectMeats Setup Overview

**👋 Start here for setup guidance!** This document provides a comprehensive overview of the ProjectMeats tech stack and setup process. For detailed instructions, consult the specific guides linked below.

## 🏗️ Tech Stack Summary

**ProjectMeats** is a business management application migrated from PowerApps/Dataverse to a modern web stack:

### Backend
- **Django REST Framework** - Python-based REST API
- **PostgreSQL** - Primary database (SQLite for development)
- **Gunicorn** - WSGI HTTP server for production
- **User Profiles** - Authentication and user management system

### Frontend  
- **React** - Modern JavaScript UI framework
- **TypeScript** - Type-safe JavaScript development
- **Styled Components** - Component-based styling
- **User Authentication** - Profile management with image uploads

### Prerequisites
- **Python 3.9+** - Backend development
- **Node.js 16+** - Frontend development  
- **PostgreSQL 12+** - Production database (optional for development)

## 🚀 Local Development Setup

### Quick Start (Recommended)
Use the provided Makefile for streamlined setup:

```bash
# Complete environment setup
make setup

# Start both backend and frontend servers
make dev

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs/
```

### Manual Setup
If you prefer step-by-step setup:

1. **Backend Setup:**
   ```bash
   cd backend
   cp .env.example .env
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Additional Development Commands
```bash
make test           # Run all tests
make migrate        # Run database migrations
make docs          # Generate API documentation
make clean         # Clean build artifacts
```

## 👤 User Profile System

ProjectMeats includes a comprehensive user profile management system:

### Features
- **User Authentication** - Login/logout with Django authentication
- **Profile Management** - User details, job titles, departments
- **Image Uploads** - Profile picture support with validation
- **Responsive UI** - User dropdown in header with mobile support
- **API Integration** - RESTful endpoints for profile management

### Key Components
- **Backend**: `/api/v1/user-profiles/` endpoints
- **Frontend**: `UserProfile.tsx` component with dropdown menu
- **Authentication**: Integration with Django User model
- **File Handling**: Profile image upload and serving

### Usage
```bash
# Access user profile API
curl http://localhost:8000/api/v1/user-profiles/me/

# Update profile via API
curl -X PATCH http://localhost:8000/api/v1/user-profiles/me/ \
  -H "Content-Type: application/json" \
  -d '{"job_title": "Manager", "department": "Sales"}'
```

## 🌐 Production Setup

### Stack Overview
- **Backend:** Django + Gunicorn + PostgreSQL
- **Frontend:** React build served via CDN/static hosting
- **API Documentation:** Auto-generated via Django REST Framework

### Environment Configuration

Create production environment files with proper values:

**Backend (.env):**
```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

**Frontend (.env.production):**
```bash
REACT_APP_API_BASE_URL=https://api.yourdomain.com/api/v1
REACT_APP_ENVIRONMENT=production
```

### Build and Deploy Commands

**Backend:**
```bash
pip install gunicorn
python manage.py collectstatic
gunicorn projectmeats.wsgi:application --bind 0.0.0.0:8000
```

**Frontend:**
```bash
npm run build
# Deploy build/ folder to your hosting service
```

## 🔧 Environment Variables

### Development Environment

**Backend (.env):**
```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/projectmeats
# Or use SQLite: DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend (.env.local):**
```bash
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
```

### Production Environment
See [Production Setup](#-production-setup) section above for production environment variables.

## 📚 Detailed Documentation

**Required for All Contributors:**
- **[Agent Quick Start Guide](docs/agent_quick_start.md)** - **Essential reading for all developers and agents**
- **[Agent Activity Log](docs/agent_activity_log.md)** - **Required logging for all work performed**

**Setup and Development:**
- **[Backend Setup Guide](docs/backend_setup.md)** - Comprehensive Django REST Framework development setup
- **[Frontend Setup Guide](docs/frontend_setup.md)** - Detailed React development environment configuration

**API and Integration:**
- **[API Reference](docs/api_reference.md)** - Complete REST API documentation with examples (includes User Profiles)
- **[Migration Mapping](docs/migration_mapping.md)** - PowerApps to Django entity and field mappings

## 📋 Development Workflow

### For New Contributors
1. **Start here** with this overview document
2. **Read** [Agent Quick Start Guide](docs/agent_quick_start.md) (**required**)
3. **Set up** your environment using [Backend Setup](docs/backend_setup.md) and [Frontend Setup](docs/frontend_setup.md)
4. **Log your work** in [Agent Activity Log](docs/agent_activity_log.md) (**required for all agents**)

### For Entity Migration
1. Review existing patterns in `accounts_receivables` implementation
2. Consult [Migration Mapping](docs/migration_mapping.md) for PowerApps mappings
3. Follow development standards in [Backend Setup](docs/backend_setup.md) and [Frontend Setup](docs/frontend_setup.md)

### For API Development
- Use [API Reference](docs/api_reference.md) for endpoint patterns and standards
- Follow Django REST Framework best practices
- Include comprehensive filtering, searching, and pagination

## 🚨 Important Requirements

### Agent Activity Logging
**ALL AGENTS AND DEVELOPERS** must log their activities in [docs/agent_activity_log.md](docs/agent_activity_log.md):
- Log objectives when starting work
- Update progress during development  
- Document completion and handoffs
- Report any issues or blockers

This logging requirement is **mandatory** and helps maintain project continuity and knowledge sharing.

## 🆘 Getting Help

1. **Check this overview** for high-level guidance
2. **Consult specific guides** in the `/docs` folder for detailed instructions
3. **Review existing code** in `accounts_receivables` for implementation patterns
4. **Check the main** [README.md](README.md) for additional project information

---

**Remember:** This overview provides the big picture. Always refer to the detailed guides linked above for comprehensive setup and development instructions.