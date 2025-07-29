# ProjectMeats

A comprehensive business management application for meat sales brokers, migrated from PowerApps/Dataverse to a modern Django REST Framework (backend) and React TypeScript (frontend) stack. This system manages suppliers, customers, purchase orders, accounts receivables, and related business entities.

## ⚠️ Python 3.13+ Setup Issue

**Windows users with Python 3.13+**: If setup fails with PostgreSQL adapter errors, see **[docs/troubleshooting.md](docs/troubleshooting.md)** for solutions.


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

**Cross-Platform Setup** (recommended):
```bash
# Clone repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Full setup (backend + frontend)
python setup.py

# Backend only
python setup.py --backend

# Frontend only  
python setup.py --frontend
```

**Alternative Setup Methods**:
- **Windows**: `setup.ps1` or `setup.bat`
- **Linux/macOS**: `make setup` or `./setup.sh`

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

- **[Setup & Development Guide](docs/setup-and-development.md)** - Complete setup and development instructions
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
- **Backend**: Django + Gunicorn + PostgreSQL
- **Frontend**: React build served via CDN/static hosting
- **API Documentation**: Auto-generated via DRF Spectacular

See [docs/production_deployment.md](docs/production_deployment.md) for complete deployment instructions.

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