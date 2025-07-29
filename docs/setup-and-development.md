# ProjectMeats Setup & Development Guide

## Prerequisites

Before starting, ensure you have:
- **Python 3.9+** - [Download from python.org](https://python.org)
- **Node.js 16+** - [Download from nodejs.org](https://nodejs.org)
- **Git** - For cloning the repository
- **PostgreSQL 12+** (optional - SQLite works for development)

⚠️ **Python 3.13+ Windows users**: See [troubleshooting.md](troubleshooting.md) for PostgreSQL compatibility issues.

## Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats
```

### 2. Cross-Platform Setup (Recommended)
```bash
# Full setup (backend + frontend)
python setup.py

# Backend only
python setup.py --backend

# Frontend only  
python setup.py --frontend

# Show help and options
python setup.py --help
```

### 3. Alternative Setup Methods

#### Windows
```powershell
# PowerShell script
.\setup.ps1

# Interactive batch file
setup.bat
```

#### Linux/macOS
```bash
# Make commands
make setup           # Complete setup
make setup-backend   # Backend only
make setup-frontend  # Frontend only

# Shell script
./setup.sh
```

## Manual Setup (If Automated Setup Fails)

### Backend Setup
```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Create test data (optional)
python create_test_data.py
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create environment file (optional)
cp .env.production.template .env.local
```

## Development Workflow

### Starting Development Servers

#### Option 1: Both Servers (Linux/macOS)
```bash
make dev
```

#### Option 2: Separate Terminals
```bash
# Terminal 1: Backend
cd backend
python manage.py runserver

# Terminal 2: Frontend  
cd frontend
npm start
```

### Access URLs
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000  
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

### Common Development Commands

#### Backend
```bash
cd backend

# Database operations
python manage.py migrate              # Apply migrations
python manage.py makemigrations       # Create migrations
python manage.py shell                # Django shell
python manage.py createsuperuser      # Create admin user

# Testing
python manage.py test                 # Run all tests
python manage.py test apps.suppliers  # Test specific app

# Code quality
black .                               # Format code
flake8 .                              # Lint code
isort .                               # Sort imports
```

#### Frontend
```bash
cd frontend

# Development
npm start                             # Start dev server
npm run build                         # Production build
npm test                              # Run tests

# Code quality
npm run lint                          # Lint TypeScript
npm run format                        # Format code (if configured)
```

#### Project-wide
```bash
# Using Makefile (Linux/macOS)
make test                             # Run all tests
make docs                             # Generate API documentation
make clean                            # Clean build artifacts
make format                           # Format all code
make lint                             # Lint all code
```

## Environment Configuration

### Backend Environment Variables (.env)
```bash
# Development settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database (choose one)
DATABASE_URL=sqlite:///db.sqlite3                                    # SQLite (default)
DATABASE_URL=postgresql://user:password@localhost:5432/projectmeats  # PostgreSQL

# CORS for frontend
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Optional settings
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend Environment Variables (.env.local)
```bash
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
```

## Adding New Features

### Backend: Adding New Django App
```bash
cd backend
python manage.py startapp new_app_name

# Then:
# 1. Add to INSTALLED_APPS in settings.py
# 2. Create models, serializers, views
# 3. Add URL patterns
# 4. Create migrations
# 5. Write tests
```

### Frontend: Adding New React Component
```bash
cd frontend/src

# Create component structure
mkdir components/NewComponent
touch components/NewComponent/index.tsx
touch components/NewComponent/NewComponent.tsx
touch components/NewComponent/styles.ts
```

### Database Changes
```bash
cd backend

# After modifying models
python manage.py makemigrations
python manage.py migrate

# Review migration before applying
python manage.py sqlmigrate app_name migration_number
```

## Code Standards

### Backend (Python/Django)
- Follow Django coding conventions
- Use type hints where appropriate
- Write comprehensive tests
- Document PowerApps field mappings in model docstrings
- Use `black` for formatting, `flake8` for linting

### Frontend (TypeScript/React)
- Use functional components with hooks
- Implement proper TypeScript types
- Use styled-components for styling
- Write component tests with React Testing Library
- Follow React/TypeScript best practices

### General
- Write clear commit messages
- Update documentation for new features
- Ensure tests pass before committing
- Use consistent code formatting

## Testing

### Running Tests
```bash
# All tests
make test

# Backend only
cd backend && python manage.py test

# Frontend only
cd frontend && npm test

# Specific backend app
cd backend && python manage.py test apps.suppliers

# With coverage
cd backend && python manage.py test --with-coverage
```

### Writing Tests
- **Backend**: Use Django's TestCase and DRF's APITestCase
- **Frontend**: Use Jest and React Testing Library
- **Integration**: Test API endpoints with realistic data
- **Unit**: Test individual functions and components

## Debugging

### Backend Debugging
- Use Django Debug Toolbar in development
- Add `breakpoint()` for Python debugger
- Check Django logs for errors
- Use `python manage.py shell` for interactive testing

### Frontend Debugging
- Use browser developer tools
- Add `console.log()` statements
- Use React Developer Tools extension
- Check network tab for API calls

## Performance Optimization

### Backend
- Use `select_related()` and `prefetch_related()` for database queries
- Add database indexes for frequently queried fields
- Use Django's caching framework
- Profile slow queries with Django Debug Toolbar

### Frontend
- Lazy load components with React.lazy()
- Optimize images and assets
- Use React.memo() for expensive components
- Minimize API calls with proper state management

## Common Issues

See [troubleshooting.md](troubleshooting.md) for solutions to common setup and development issues.