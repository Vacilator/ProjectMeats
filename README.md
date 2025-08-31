# ProjectMeats

A comprehensive business management application for meat sales brokers, migrated from PowerApps/Dataverse to a modern Django REST Framework (backend) and React TypeScript (frontend) stack. This system manages suppliers, customers, purchase orders, accounts receivables, and related business entities.

## 🚀 Quick Start

### 📖 Essential Documentation (Start Here)
| Purpose | Documentation | When to Use |
|---------|---------------|-------------|
| **Production Deployment** | [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md) | Deploy to production servers |
| **Developer Setup** | [DEVELOPER_QUICK_START.md](DEVELOPER_QUICK_START.md) | New developer onboarding |
| **Team Coordination** | [TEAM_COORDINATION_GUIDE.md](TEAM_COORDINATION_GUIDE.md) | Team efficiency & workflows |
| **Architecture Overview** | [DEPLOYMENT_ECOSYSTEM_ANALYSIS.md](DEPLOYMENT_ECOSYSTEM_ANALYSIS.md) | Understand system design |

> **⚠️ Important**: Ignore other .md files in the root - they're outdated or redundant. Use only the 4 documents above.

### 🎯 Quick Commands

```bash
# Production deployment (PRIMARY METHOD)
python ai_deployment_orchestrator.py --server=your-server.com --domain=your-domain.com --auto

# Local development setup
python setup.py

# Quick testing with Docker
docker-compose up
```

## 🛠️ Core Tools

### 🤖 AI Deployment Orchestrator (PRIMARY PRODUCTION TOOL)

**The only tool you need for production deployments** - intelligent, automated, and self-recovering:

```bash
# Clone and deploy
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Automated production deployment
python ai_deployment_orchestrator.py --server=your-server.com --domain=your-domain.com --auto

# Interactive setup (recommended for first time)
python ai_deployment_orchestrator.py --interactive
```

**Why Use the AI Orchestrator:**
- ✅ **Intelligent Error Recovery**: Automatically fixes 50+ common deployment issues
- ✅ **Complete Automation**: From fresh server to production-ready in one command
- ✅ **GitHub Integration**: Automatic issue creation with @copilot assignment for failures
- ✅ **Real-time Monitoring**: Live deployment progress and health monitoring
- ✅ **State Persistence**: Resume deployments from where they left off
- ✅ **Security Built-in**: SSL, firewall, and security hardening automated

### 🔧 Development Tools

#### Local Development Setup
```bash
# Cross-platform setup script
python setup.py
```

#### Docker Development
```bash
# Full stack with hot reload
docker-compose up
```

## ❌ What NOT to Use

### Deprecated/Legacy Systems
- `legacy-deployment/master_deploy.py` - Old deployment system (deprecated)
- `scripts/deployment/` - Most scripts are redundant (use AI orchestrator instead)
- Various .md files in root - Outdated documentation (use 4 essential docs above)

> **For AI Agents**: Always enhance `ai_deployment_orchestrator.py` instead of creating new deployment tools.

## 📁 Repository Structure

```
ProjectMeats/
├── 📋 PRODUCTION_DEPLOYMENT_GUIDE.md     # 🎯 Primary deployment guide
├── 📋 DEVELOPER_QUICK_START.md           # 🎯 Developer onboarding  
├── 📋 TEAM_COORDINATION_GUIDE.md         # 🎯 Team efficiency guide
├── 📋 DEPLOYMENT_ECOSYSTEM_ANALYSIS.md   # 🎯 Architecture overview
│
├── 🤖 ai_deployment_orchestrator.py      # Primary production deployment tool
├── 🔧 setup.py                           # Local development setup
├── 🐳 docker-compose.yml                 # Docker development stack
│
├── backend/                              # Django REST Framework
├── frontend/                             # React TypeScript
├── docs/                                 # Additional documentation
│
├── legacy-deployment/                    # ❌ DEPRECATED - don't use
├── scripts/deployment/                   # ❌ MOSTLY DEPRECATED
└── [Various .md files]                   # ❌ OUTDATED - use 4 essential docs above
```

## 🧠 Architecture Overview

### Backend (Django REST Framework)
- **Framework**: Django 4.2.7 + DRF 3.14.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **API Documentation**: DRF Spectacular (OpenAPI/Swagger)
- **Authentication**: Token-based authentication
- **Location**: `/backend/`

### Frontend (React TypeScript)
- **Framework**: React 18.2.0 + TypeScript 4.9.0
- **Styling**: Styled Components
- **State Management**: React hooks
- **Build Tool**: Create React App
- **Location**: `/frontend/`

### Key Features
- **PowerApps Migration**: Complete migration from PowerApps/Dataverse
- **Business Management**: Suppliers, customers, purchase orders, accounts receivables
- **Modern Stack**: Django REST + React TypeScript
- **Production Ready**: Comprehensive deployment automation

## 🚀 Getting Started

### For New Developers
1. Read [DEVELOPER_QUICK_START.md](DEVELOPER_QUICK_START.md)
2. Run `python setup.py` for local development
3. Use `docker-compose up` for quick testing

### For Production Deployment
1. Read [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)
2. Run `python ai_deployment_orchestrator.py --interactive`

### For Team Coordination
1. Read [TEAM_COORDINATION_GUIDE.md](TEAM_COORDINATION_GUIDE.md)
2. Follow established workflows and tool usage guidelines

## 💡 Support & Community

### Getting Help
- **Documentation**: Check the 4 essential guides above first
- **Issues**: Use GitHub issues for bugs and feature requests
- **Deployment Problems**: Automatic @copilot assignment for deployment failures

### Contributing
1. Read [DEVELOPER_QUICK_START.md](DEVELOPER_QUICK_START.md) for setup
2. Follow team coordination guidelines
3. Enhance existing tools rather than creating new ones
4. Update documentation when making changes

---

**ProjectMeats** - Modern business management for meat industry professionals.
Built with Django REST Framework and React TypeScript for reliability, scalability, and developer productivity.
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

## 🔧 Troubleshooting

### Health Endpoint Issues

If deployment verification fails with 404 or 301 errors on `/health` endpoint:

**Common Issues:**
- **404 on /health**: Health endpoint not properly configured in Django URLs or Nginx
- **301 redirects**: APPEND_SLASH setting causing automatic redirects
- **502 Bad Gateway**: Django backend not responding via Unix socket

**Diagnostic Commands:**
```bash
# Test health endpoint directly on server
curl -I http://localhost/health

# Check Django service status
systemctl status projectmeats

# Check Unix socket permissions
ls -la /run/projectmeats.sock

# Check Nginx configuration
nginx -t && nginx -s reload

# Check port 80 binding
sudo ss -tlnp | grep :80
```

**DNS Resolution Issues:**
```bash
# Test DNS resolution (modern method)
dig +short A yourdomain.com

# Test external connectivity
curl -m 10 -I -L http://yourdomain.com/health

# Test with DNS bypass
curl --resolve "yourdomain.com:80:YOUR_SERVER_IP" -I http://yourdomain.com/health
```

### Deployment Logs
Check deployment logs for detailed error analysis:
- **Django**: `journalctl -u projectmeats -f`
- **Nginx**: `tail -f /var/log/nginx/error.log`
- **System**: `systemctl status nginx`

---

**Need Help?** Check the [docs/](docs/) folder or create an issue for questions.