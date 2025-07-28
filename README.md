# ProjectMeats

A comprehensive business management application for meat sales brokers, migrated from PowerApps/Dataverse to a modern Django REST Framework (backend) and React TypeScript (frontend) stack. This system manages suppliers, customers, purchase orders, accounts receivables, and related business entities with enterprise-grade security and scalability.

## 📖 Documentation Navigation

**🚀 New to ProjectMeats?** Start here:
- **[Quick Setup](#-quick-setup)** - Get running in minutes
- **[Developer Setup](#-developer-setup)** - Complete development environment
- **[Production Deployment](#-production-deployment)** - Deploy to production

## ⚠️ Python 3.13+ Setup Issue

**Windows users with Python 3.13+**: If setup fails with PostgreSQL adapter errors, see **[Python 3.13+ Setup Guide](PYTHON_3_13_SETUP.md)** for solutions.

**📚 Complete Documentation:**
- **[Complete Setup Guide](docs/setup_guide.md)** - Comprehensive setup for all platforms and scenarios
- **[Production Deployment Guide](docs/production_deployment.md)** - Enterprise production deployment
- **[API Reference](docs/api_reference.md)** - Complete REST API documentation
- **[Migration Mapping](docs/migration_mapping.md)** - PowerApps to Django migration details
- **[GitHub Copilot Guide](docs/copilot_usage_guide.md)** - AI-enhanced development
- **[Agent Activity Log](docs/agent_activity_log.md)** - Development activity tracking

## 🏗️ System Architecture

**Technology Stack:**
- **Backend**: Django 4.2.7 + Django REST Framework + PostgreSQL
- **Frontend**: React 18.2.0 + TypeScript + Styled Components  
- **Authentication**: Django User system with profile management
- **API**: RESTful endpoints with OpenAPI documentation
- **Testing**: 76+ comprehensive backend tests

**Project Structure:**
```
ProjectMeats/
├── backend/                    # Django REST Framework API
│   ├── apps/                  # Business entities (9 complete)
│   │   ├── accounts_receivables/  # Customer payments
│   │   ├── suppliers/            # Supplier management
│   │   ├── customers/            # Customer relationships
│   │   ├── user_profiles/        # User authentication & profiles
│   │   ├── purchase_orders/      # Order processing
│   │   ├── plants/              # Processing facilities
│   │   ├── contacts/            # Contact management
│   │   └── core/                # Shared utilities
│   └── requirements.txt
├── frontend/                   # React TypeScript application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── screens/           # Main application screens
│   │   ├── services/          # API communication layer
│   │   └── types/             # TypeScript definitions
│   └── package.json
├── docs/                      # Complete documentation
└── powerapps_export/          # Original PowerApps reference
```

## 🚀 Quick Setup

Get ProjectMeats running in minutes with our cross-platform setup script:

### Prerequisites
- **Python 3.9+** - [Download from python.org](https://python.org)
- **Node.js 16+** - [Download from nodejs.org](https://nodejs.org)
- **Git** - For cloning the repository

### One-Command Setup (All Platforms)
```bash
# Clone repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Full setup (backend + frontend) - Works on Windows, macOS, Linux
python setup.py

# Backend only
python setup.py --backend

# Frontend only  
python setup.py --frontend
```

### Access Your Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

### Alternative Setup Methods
**Windows Users:**
```powershell
# PowerShell script with options
.\\setup.ps1
.\\setup.ps1 -Backend
.\\setup.ps1 -Frontend
```

**macOS/Linux Users:**
```bash
# Make commands
make setup           # Complete setup
make setup-backend   # Backend only
make setup-frontend  # Frontend only
make dev            # Start both servers
```

### Troubleshooting
- **"python: command not found"**: Try `python3 setup.py`
- **Windows CLI errors**: Use `python setup.py` instead of make commands
- **Permission errors**: Run as administrator/sudo if needed
- **More help**: See [Complete Setup Guide](docs/setup_guide.md)

## 🔧 Developer Setup

For detailed development environment setup and advanced configuration:

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Development  
```bash
cd frontend
npm install
echo "REACT_APP_API_BASE_URL=http://localhost:8000/api/v1" > .env.local
npm start
```

### AI-Enhanced Development (GitHub Copilot)
ProjectMeats includes comprehensive AI development support:

```bash
# Verify Copilot configuration
python verify_copilot_setup.py

# Open with enhanced VS Code workspace  
code ProjectMeats.code-workspace
```

**Features:**
- Custom Copilot instructions for Django/React patterns
- MCP (Model Context Protocol) server integration
- Optimized VS Code configuration with debugging and tasks
- PowerApps migration context for AI suggestions

See [GitHub Copilot Usage Guide](docs/copilot_usage_guide.md) for complete setup.

### Development Commands
```bash
# Run tests
make test              # All tests
cd backend && python manage.py test  # Backend only
cd frontend && npm test               # Frontend only

# Code quality
cd backend && black . && flake8 .    # Python formatting
cd frontend && npm run lint           # JavaScript/TypeScript

# Database management
cd backend && python manage.py makemigrations
cd backend && python manage.py migrate
```

## 📋 PowerApps Migration Status

ProjectMeats successfully migrates 9 core business entities from PowerApps/Dataverse:

### ✅ Completed Entities (Full Stack)
1. **Accounts Receivables** (`cr7c4_accountsreceivables`)
   - Django Model: `AccountsReceivable` 
   - API: `/api/v1/accounts-receivables/`
   - React Component: Complete management interface

2. **Suppliers** (`cr7c4_supplier`)
   - Django Model: `Supplier`
   - API: `/api/v1/suppliers/`
   - React Component: Supplier management

3. **Customers** (`pro_customer`)
   - Django Model: `Customer`
   - API: `/api/v1/customers/`
   - React Component: Customer relationship management

4. **Contact Info** (`pro_contactinfo`)
   - Django Model: `ContactInfo`
   - API: `/api/v1/contacts/`
   - React Component: Contact management with relationships

5. **User Profiles** (Django-native enhancement)
   - Django Model: `UserProfile`
   - API: `/api/v1/user-profiles/`
   - React Component: User authentication and profile management

### ✅ Backend Complete (Frontend In Progress)
6. **Purchase Orders** (`pro_purchaseorder`) - Order processing with file attachments
7. **Plants** (`cr7c4_plant`) - Processing facilities and locations  
8. **Supplier Plant Mappings** (`pro_supplierplantmapping`) - Business relationships
9. **Carrier Info** (`cr7c4_carrierinfo`) - Transportation management

### Migration Details
- **Zero Data Loss**: All PowerApps data and relationships preserved
- **Enhanced Features**: Modern UI, file uploads, advanced search/filtering
- **API-First**: RESTful endpoints with OpenAPI documentation
- **Type Safety**: TypeScript integration for robust frontend development

See [Migration Mapping](docs/migration_mapping.md) for detailed field mappings and migration information.

## 🚀 Production Deployment

Deploy ProjectMeats to production with enterprise-grade security and performance:

### Quick Production Setup
```bash
# Clone and navigate
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Run automated production deployment
sudo ./deploy_production.sh
```

### Infrastructure Requirements
**Minimum Production:**
- 2 vCPU, 4GB RAM, 50GB SSD
- Ubuntu 20.04+ LTS
- PostgreSQL 12+, Nginx, SSL certificate

**Recommended Production:**
- 4 vCPU, 8GB RAM, 100GB SSD  
- Load balancer, Redis caching, CDN
- Monitoring and automated backups

### Production Features
- **HTTPS/TLS Encryption** - Industry-standard security
- **Web Application Firewall** - Attack protection
- **Automated Backups** - 30-day retention with encryption
- **Performance Optimization** - Database indexing, query optimization
- **Monitoring & Alerting** - Health checks and error tracking

### Manual Production Setup
1. **Server Setup**: Install dependencies (Python, Node.js, PostgreSQL, Nginx)
2. **Database Configuration**: Create production database and user
3. **Application Deployment**: Clone code, install dependencies, run migrations
4. **Web Server Configuration**: Configure Nginx with SSL termination
5. **Security Hardening**: Firewall, Fail2Ban, security headers
6. **Monitoring Setup**: Health checks, log monitoring, backup verification

See [Production Deployment Guide](docs/production_deployment.md) for complete step-by-step instructions.

### Deployment Checklist
- [ ] DNS and SSL certificate configured
- [ ] Environment variables set for production
- [ ] Database migrations applied
- [ ] Static files collected and served
- [ ] Security hardening completed
- [ ] Monitoring and backup systems active
- [ ] Performance optimization applied
- [ ] User acceptance testing completed

*See [docs/migration_mapping.md](docs/migration_mapping.md) for detailed field mappings.*

## 🛠️ Development Workflow

### Adding New Entities
1. **Analyze PowerApps Entity**: Review XML export for field definitions
2. **Create Django Model**: Use standard Django patterns
3. **Add Serializers**: DRF serializers for API responses
4. **Create ViewSets**: REST API endpoints with filtering/pagination
5. **Build React Components**: Screens and reusable components
6. **Update Documentation**: API docs and migration notes

## 🧪 Testing & Quality Assurance

ProjectMeats includes comprehensive testing and quality assurance:

### Test Coverage
- **Backend**: 76+ comprehensive tests covering all entities
- **Frontend**: Component tests with React Testing Library
- **Integration**: API endpoint testing with real data
- **Performance**: Database query optimization and load testing

### Running Tests
```bash
# All tests
make test

# Backend tests only
cd backend && python manage.py test

# Frontend tests only  
cd frontend && npm test

# Coverage reports
cd backend && coverage run --source='.' manage.py test
cd backend && coverage report
```

### Code Quality
- **Python**: Black formatting, Flake8 linting, type hints
- **TypeScript**: ESLint, Prettier formatting, strict type checking
- **Security**: Django security middleware, input validation
- **Performance**: Database indexing, query optimization, caching

### Performance Metrics
- **Database**: 3-5x query reduction with strategic indexes
- **API Response**: Sub-second response times for all endpoints
- **Frontend**: Code splitting and lazy loading for optimal performance
- **Reliability**: 99.9% uptime with comprehensive error handling

## 👥 Contributing & Development Guidelines

### 🚨 Required: Agent Activity Logging
**ALL DEVELOPERS AND AGENTS** must log their work in [docs/agent_activity_log.md](docs/agent_activity_log.md):
- Log initial objectives when starting work
- Update progress regularly during development
- Document completed work and handoffs
- Report any issues or blockers

### Development Workflow
1. **Review Documentation**: Start with this README and relevant docs
2. **Setup Environment**: Use `python setup.py` for quick setup
3. **Choose Entity**: Pick from planned entities in migration mapping
4. **Follow Patterns**: Use existing code patterns from completed entities
5. **Write Tests**: Add comprehensive tests for new functionality
6. **Update Documentation**: Keep docs current with changes
7. **Log Activity**: Record work in agent activity log

### Code Standards
- **Backend**: Django/DRF best practices, type hints, comprehensive docstrings
- **Frontend**: React functional components, TypeScript strict mode
- **Testing**: Unit tests for models, integration tests for APIs
- **Documentation**: PowerApps field mappings, inline comments for complex logic
- **Security**: Input validation, proper authentication, security headers

### Adding New Entities (PowerApps Migration)
1. **Analyze PowerApps XML**: Review entity structure in `powerapps_export/`
2. **Create Django App**: Follow naming conventions
3. **Define Models**: Use `OwnedModel` and `StatusModel` base classes
4. **Add Serializers**: Create list, detail, and create serializers
5. **Implement ViewSets**: Include filtering, search, and pagination
6. **Build React Components**: Create screen and reusable components
7. **Update API Documentation**: Add endpoints to API reference
8. **Write Tests**: Comprehensive test coverage

### PowerApps Legacy Reference
The original PowerApps solution is preserved in `powerapps_export/` for reference. All migration decisions and field mappings are documented to ensure no business logic is lost during the transition.

## 📞 Support & Resources

### Getting Help
- **Documentation**: Check this README and docs/ folder first
- **Existing Code**: Review completed entities for patterns
- **Migration Reference**: See PowerApps export for original logic
- **API Testing**: Use http://localhost:8000/api/docs/ for interactive testing

### Key Resources
- **Django Documentation**: https://docs.djangoproject.com/
- **React Documentation**: https://react.dev/
- **TypeScript Handbook**: https://www.typescriptlang.org/docs/
- **PowerApps Migration**: See `docs/migration_mapping.md` for field mappings

### Performance & Security
- **Optimized**: 18 database indexes, query optimization, caching strategies
- **Secure**: HTTPS, security headers, input validation, audit logging
- **Tested**: 76+ backend tests, frontend component tests, integration tests
- **Monitored**: Health checks, error tracking, performance monitoring

---

**ProjectMeats** - Modernizing meat industry business management with enterprise-grade technology.

*Need help? Create an issue or refer to the comprehensive documentation in the `docs/` folder.*
- **Database queries**: 3-5x reduction in queries for list endpoints
- **Code quality**: 1000+ linting violations reduced to 146 non-critical line length issues
- **Test stability**: All 76 tests passing consistently

See [OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md) for detailed analysis.

## 🚀 Deployment

### Development
```bash
make dev  # Runs both backend (8000) and frontend (3000)
```

### Production
- Backend: Django + Gunicorn + PostgreSQL
- Frontend: React build served via CDN/static hosting
- API Documentation: Auto-generated via DRF

## 🔧 Environment Variables

### Backend (.env)
```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/projectmeats
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```bash
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
```

## 👥 Contributing

### 🚨 **REQUIRED: Agent Activity Logging**
**ALL AGENTS MUST** log their work in [docs/agent_activity_log.md](docs/agent_activity_log.md):
- Log initial objectives when starting work
- Update progress regularly during development
- Document completed work and handoffs

### Development Guidelines
1. **New Developers**: Follow [docs/backend_setup.md](docs/backend_setup.md) and [docs/frontend_setup.md](docs/frontend_setup.md)
2. **Entity Migration**: Use existing patterns from `accounts_receivables` 
3. **Code Review**: Ensure PowerApps field mappings are documented
4. **Testing**: Add tests for new functionality
5. **Documentation**: Update [agent activity log](docs/agent_activity_log.md) for all work

## 📝 PowerApps Legacy

The original PowerApps solution is preserved in `powerapps_export/` for reference. Key migration decisions and field mappings are documented to ensure no business logic is lost during the transition.

---

**Need Help?** Check the docs folder or create an issue for questions about the migration process.