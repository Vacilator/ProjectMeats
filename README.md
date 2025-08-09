# ProjectMeats

A comprehensive business management application for meat sales brokers, migrated from PowerApps/Dataverse to a modern Django REST Framework (backend) and React TypeScript (frontend) stack. This system manages suppliers, customers, purchase orders, accounts receivables, and related business entities.

## 🚀 DEPLOYMENT OPTIONS

### ⭐ NEW: Production Deployment Fix (Recommended)

**Fixes deployment issues with missing static files and backend service problems:**

```bash
# Clone the repository and run the improved deployment script:
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats
sudo ./production_deploy.sh
```

**This fixes common deployment issues:**
- ✅ Django backend not running (uses gunicorn + systemd, not PM2)
- ✅ Missing React static files (404 errors for `/static/js/main.*.js`, `/favicon.ico`)  
- ✅ Proper Nginx configuration for frontend + backend integration
- ✅ Complete React build process with all assets
- ✅ Automated service management and monitoring

### Option 1: One-Click Production Deployment (Legacy)

**Deploy ProjectMeats to production in minutes with one command:**

```bash
# Fully automated deployment (Ubuntu 20.04+):
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/one_click_deploy.sh | sudo bash
```

**Having Node.js conflicts?** Fix them first:
```bash
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/fix_nodejs.sh | sudo bash
```

### Option 2: Docker Compose Deployment

**For containerized environments or development:**

```bash
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats
docker compose up --build -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser --username admin --email admin@example.com
```

**🔐 HTTPS/SSL Support**: ProjectMeats supports secure HTTPS connections:

```bash
# Quick HTTPS setup with self-signed certificate (development)
./setup_ssl.sh localhost

# Production HTTPS with Let's Encrypt
./setup_ssl.sh yourdomain.com

# Start with HTTPS enabled
docker compose -f docker-compose.prod.yml up -d
```

See [HTTPS_SETUP.md](HTTPS_SETUP.md) for complete SSL configuration guide.

**📖 Deployment guides:**
- [One-Click Deployment Guide](PRODUCTION_DEPLOYMENT.md)
- [Docker Compose Guide](DOCKER_COMPOSE_GUIDE.md)

### ✨ What You Get
- ✅ **Professional UI** at your domain with SSL
- ✅ **Complete API** with Swagger documentation
- ✅ **Admin interface** for business management
- ✅ **Automated backups** and monitoring
- ✅ **Enterprise security** (firewall, fail2ban, SSL)
- ✅ **15-30 minute setup** on recommended hosting ($15-25/month)

## 🏗️ Technology Stack

- **Backend**: Django 4.2.7 + Django REST Framework + PostgreSQL
- **Frontend**: React 18.2.0 + TypeScript + Styled Components  
- **Authentication**: Django User system with profile management
- **API**: RESTful endpoints with OpenAPI documentation
- **Testing**: 95+ comprehensive backend tests

## 📁 Project Structure

```
ProjectMeats/
├── backend/                    # Django REST Framework API
│   ├── apps/                  # Business entities (9 complete)
│   │   ├── accounts_receivables/  # Customer payments
│   │   ├── suppliers/            # Supplier management
│   │   ├── customers/            # Customer relationships
│   │   ├── purchase_orders/      # Order processing
│   │   ├── plants/              # Processing facilities
│   │   ├── contacts/            # Contact management
│   │   └── core/                # Shared utilities
│   └── requirements.txt
├── frontend/                   # React TypeScript application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── screens/           # Main application screens
│   │   └── services/         # API communication
│   └── package.json
├── docs/                      # Documentation
└── powerapps_export/          # Original PowerApps solution
```

## 🚀 Quick Setup

**Prerequisites**: Python 3.9+, Node.js 16+, Git

### Option 1: Interactive AI Assistant Setup (Recommended)
```bash
# Clone repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Run comprehensive AI assistant setup wizard
python setup_ai_assistant.py
```

This guided setup will configure:
- ✅ Backend authentication and database
- ✅ AI provider credentials (OpenAI, Anthropic, Azure OpenAI)
- ✅ Environment variables and secrets
- ✅ Frontend integration
- ✅ Database initialization

### Option 2: Standard Setup
```bash
# Clone repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Full setup (backend + frontend)
python setup.py

# Configure AI assistant separately
python setup_ai_assistant.py
```

### Option 3: Platform-Specific Setup

**Windows Users:**
```cmd
setup_windows.bat
```

**Linux/macOS:**
```bash
make setup
# or
./setup.sh
```

### Manual Setup (Advanced Users)
```bash
# Backend only
python setup.py --backend

# Frontend only  
python setup.py --frontend

# AI assistant only
python setup.py --ai-only
```

## 🚀 Production Deployment

### Quick Deployment (No Authentication Required)

**Fastest method - works without GitHub authentication:**

```bash
# One-command production deployment
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash
```

### Alternative Deployment Methods

**If you have GitHub authentication set up:**

```bash
# Traditional git clone method
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats
sudo python3 deploy_production.py
```

**Having authentication issues?** See [DEPLOYMENT_AUTH_QUICKREF.md](DEPLOYMENT_AUTH_QUICKREF.md)

### Deployment Verification

Check if your system is ready for deployment:

```bash
# Download and run verification
curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/verify_deployment_readiness.sh | bash

# Or if you have the project locally
./verify_deployment_readiness.sh
```

### Documentation

- 📖 [Complete Production Guide](docs/production_deployment.md)
- 🔐 [Authentication Solutions](docs/deployment_authentication_guide.md)  
- ⚡ [Quick Setup Guide](docs/production_setup_guide.md)
- 📋 [Quick Reference](DEPLOYMENT_AUTH_QUICKREF.md)

## 🔧 Development

### Start Development Servers
```bash
# Start both servers (Linux/macOS)
make dev

# Windows users - use separate terminals:
# Terminal 1: cd backend && python manage.py runserver
# Terminal 2: cd frontend && npm start
```

### Access URLs
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000  
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

### AI Assistant Features
After running `python setup_ai_assistant.py`:
- **Chat Interface**: Intelligent conversational AI for business operations
- **Document Processing**: Upload and analyze purchase orders, invoices, contracts
- **Entity Extraction**: Automatic data extraction and database integration
- **Business Intelligence**: Natural language queries about your data

### Default Credentials
- **Username**: admin
- **Password**: WATERMELON1219

### Development Commands
```bash
make test          # Run all tests
make migrate       # Run Django migrations
make docs          # Generate API documentation
make clean         # Clean build artifacts
```

## 📋 Migration Status

**Completed Entities**:
- ✅ **Accounts Receivables** - Customer payment tracking
- ✅ **Suppliers** - Supplier management system  
- ✅ **Customers** - Customer relationship management
- ✅ **Purchase Orders** - Order processing workflow
- ✅ **Plants** - Processing facility management
- ✅ **Contacts** - Contact information system
- ✅ **User Profiles** - Authentication and user management

*See [docs/migration_mapping.md](docs/migration_mapping.md) for detailed PowerApps → Django field mappings.*

## 🧪 Testing

```bash
# Backend tests
cd backend && python manage.py test

# Frontend tests  
cd frontend && npm test

# Full test suite
make test
```

**Test Status**: ✅ 95+ backend tests covering all business entities

## 📚 Documentation

### Quick Start Guides
- **[QUICK_SETUP.md](QUICK_SETUP.md)** - Solve authentication issues in 5 minutes
- **[AI Assistant Setup](docs/ai_assistant_setup.md)** - Complete AI configuration guide
- **[Setup & Development Guide](docs/setup-and-development.md)** - Complete setup and development instructions

### Technical Documentation  
- **[API Reference](docs/api_reference.md)** - Complete API documentation  
- **[Production Deployment](docs/production_deployment.md)** - Production deployment guide
- **[Migration Mapping](docs/migration_mapping.md)** - PowerApps to Django mappings
- **[Architecture Guide](docs/architecture.md)** - System architecture and design decisions

## 🚀 Performance & Production

### Recent Optimizations ✅
- **Database indexes**: Strategic indexes for improved query performance
- **Query optimization**: Reduced N+1 queries with `select_related()`
- **Code quality**: Automated formatting and linting
- **Security review**: Comprehensive security assessment

### Production Deployment

ProjectMeats includes an **interactive production deployment system** with guided setup:

```bash
# Interactive production setup with server recommendations
python deploy_production.py

# Or quick server provider comparison
python server_guide.py
```

**Features**:
- 🎯 **Interactive console prompts** for all configuration values
- 🌟 **Server provider recommendations** with cost comparisons
- 🔧 **Automated configuration file generation**
- 🚀 **One-command server deployment**
- 🔒 **Security best practices** (SSL, firewall, fail2ban)
- 📊 **Deployment verification** and health checks

**Quick Setup**:
1. Choose server provider (DigitalOcean, Linode, Vultr, AWS Lightsail)
2. Run `python deploy_production.py` for guided configuration
3. Upload and execute generated deployment script on server
4. Access your production application with SSL/HTTPS

See [docs/production_setup_guide.md](docs/production_setup_guide.md) for the simplified setup guide.

## 👥 Contributing

1. Follow the [Setup & Development Guide](docs/setup-and-development.md)
2. Use existing patterns from implemented entities
3. Add tests for new functionality
4. Update documentation for changes

**Code Standards**:
- **Backend**: Django/DRF best practices, type hints, comprehensive tests
- **Frontend**: React functional components with TypeScript
- **Documentation**: Clear inline comments for PowerApps migrations

---

**Need Help?** Check the [docs/](docs/) folder or create an issue for questions.