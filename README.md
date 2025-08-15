# ProjectMeats

A comprehensive business management application for meat sales brokers, migrated from PowerApps/Dataverse to a modern Django REST Framework (backend) and React TypeScript (frontend) stack. This system manages suppliers, customers, purchase orders, accounts receivables, and related business entities.

## 🚀 Production Deployment

### ⭐ AI Deployment Orchestrator (Recommended)

**The primary production deployment tool with intelligent automation and error recovery:**

```bash
# Clone the repository and run the AI deployment orchestrator:
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Interactive deployment with guided setup
python ai_deployment_orchestrator.py --interactive

# Automated deployment for specific server/domain
python ai_deployment_orchestrator.py --server=myserver.com --domain=mydomain.com --auto

# With GitHub authentication
python ai_deployment_orchestrator.py --server=myserver.com --domain=mydomain.com --github-user=USERNAME --github-token=TOKEN
```

**Features:**
- ✅ Intelligent error detection and automatic recovery
- ✅ Comprehensive server setup and configuration
- ✅ Automated SSL certificate management
- ✅ Database configuration with PostgreSQL
- ✅ Complete security hardening
- ✅ Health monitoring and verification

### Docker Compose Deployment (Alternative)

**For containerized environments and development:**

#### Development Setup (with hot reload)
```bash
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Copy environment template and configure
cp .env.example .env
# Edit .env file with your settings

# Start development environment with hot reload
docker compose -f docker-compose.dev.yml up --build -d

# Run migrations
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate

# Create superuser
docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser --username admin --email admin@example.com

# Access services:
# Frontend: http://localhost:3000 (with hot reload)
# Backend API: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/
```

#### Production Setup
```bash
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Copy and configure production environment
cp .env.example .env
# Edit .env with production values (strong passwords, proper domains, etc.)

# Start production services
docker compose up --build -d

# Run migrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser --username admin --email admin@example.com

# Collect static files (if needed)
docker compose exec backend python manage.py collectstatic --noinput

# Access services:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/
```

#### High-Availability Production Setup
```bash
# Use the production-optimized compose file
docker compose -f docker-compose.prod.yml up --build -d
```

#### Docker Commands Cheat Sheet
```bash
# View logs
docker compose logs -f [service_name]

# Stop services
docker compose down

# Stop and remove volumes (⚠️ destroys data)
docker compose down --volumes

# Rebuild specific service
docker compose up --build [service_name]

# Run Django commands
docker compose exec backend python manage.py [command]

# Access database
docker compose exec db psql -U projectmeats_user -d projectmeats_db

# Test the setup
./test_docker.sh
```

**Features of our Docker setup:**
- ✅ Multi-stage builds for optimized images
- ✅ Health checks for all services  
- ✅ Production-ready nginx frontend serving
- ✅ PostgreSQL with persistent data
- ✅ Environment-based configuration
- ✅ Development mode with hot reload
- ✅ Comprehensive testing script

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

## 🛠️ Troubleshooting

### Service Startup Issues

If the Django service fails to start during deployment:

```bash
# Run comprehensive diagnostics
sudo ./deployment/scripts/diagnose_service.sh

# Test deployment configuration
make test-deployment

# Fix permissions if needed
sudo ./deployment/scripts/fix_permissions.sh

# Check service status
sudo systemctl status projectmeats
sudo journalctl -xeu projectmeats -n 50
```

### Common Issues

**Service won't start:**
- Check `/var/log/projectmeats/deployment_errors.log` for detailed logs
- Verify dependencies: `pip install -r backend/requirements.txt --upgrade`
- Ensure environment files exist: `/etc/projectmeats/projectmeats.env`
- Fix permissions: `sudo ./deployment/scripts/fix_permissions.sh`

**Port binding errors:**
- Check if another service is using port 8000: `lsof -i :8000`
- Use fallback service: Copy `deployment/systemd/projectmeats-port.service` to `/etc/systemd/system/`

**Environment variable issues:**
- Verify `DJANGO_SETTINGS_MODULE=apps.settings.production` in environment file
- Check database URL format: `DATABASE_URL=postgres://user:pass@localhost/db`

### Manual Testing

```bash
# Test Django configuration
cd backend && python manage.py check --deploy

# Test WSGI application
cd backend && python -c "from projectmeats.wsgi import application; print('OK')"

# Test Gunicorn manually
cd backend && ../venv/bin/gunicorn --bind 127.0.0.1:8001 projectmeats.wsgi:application
```

## 📚 Documentation

### Quick Start Guides
- **[QUICK_SETUP.md](QUICK_SETUP.md)** - Solve authentication issues in 5 minutes
- **[AI Assistant Setup](docs/ai_assistant_setup.md)** - Complete AI configuration guide
- **[Setup & Development Guide](docs/setup-and-development.md)** - Complete setup and development instructions

### Technical Documentation  
- **[API Reference](docs/api_reference.md)** - Complete API documentation  
- **[AI Deployment Guide](docs/ai_deployment_guide.md)** - AI deployment system documentation
- **[Migration Mapping](docs/migration_mapping.md)** - PowerApps to Django mappings
- **[Architecture Guide](docs/architecture.md)** - System architecture and design decisions

## 🚀 Performance & Production Features

### Recent Optimizations ✅
- **Database indexes**: Strategic indexes for improved query performance
- **Query optimization**: Reduced N+1 queries with `select_related()`
- **Code quality**: Automated formatting and linting
- **Security review**: Comprehensive security assessment
- **AI-powered deployment**: Intelligent deployment with error recovery
- **Monitoring**: Built-in health checks and performance monitoring

### Production Features
- 🎯 **AI Deployment Orchestrator**: Primary deployment tool with intelligent automation
- 🔒 **Security**: SSL/HTTPS, firewall, fail2ban protection
- 📊 **Monitoring**: Health checks, logging, and performance metrics
- 🐘 **Database**: PostgreSQL with optimized configuration
- 🌐 **Load Balancing**: Nginx with optimized configuration
- 🔧 **Auto-recovery**: Intelligent error detection and resolution

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