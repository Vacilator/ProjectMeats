# ProjectMeats

A comprehensive business management application migrated from PowerApps/Dataverse to Django REST Framework (backend) and React (frontend). This system manages suppliers, customers, purchase orders, accounts receivables, and related business entities.

**🚀 New to ProjectMeats?** Start with the **[Setup Overview](SETUP_OVERVIEW.md)** for a comprehensive setup guide and links to all documentation.

## 🏗️ Architecture Overview

```
ProjectMeats/
├── backend/                    # Django REST Framework API
│   ├── projectmeats/          # Django project
│   ├── apps/                  # Django applications
│   │   ├── accounts_receivables/  # First migrated entity
│   │   ├── suppliers/
│   │   ├── customers/
│   │   ├── user_profiles/     # User authentication & profiles
│   │   └── core/              # Shared utilities
│   ├── requirements.txt
│   ├── .env.example
│   └── manage.py
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   │   ├── UserProfile.tsx   # User profile dropdown
│   │   │   └── DesignSystem.tsx  # Design system
│   │   ├── screens/          # Main application screens
│   │   │   └── AccountsReceivablesScreen.js
│   │   ├── services/         # API communication
│   │   └── utils/
│   ├── package.json
│   └── public/
├── docs/                      # Documentation
│   ├── backend_setup.md       # Backend development guide
│   ├── frontend_setup.md      # Frontend development guide
│   ├── api_reference.md       # API documentation
│   └── migration_mapping.md   # PowerApps → Django mapping
├── powerapps_export/          # Original PowerApps solution
├── Makefile                   # Development commands
└── README.md                  # This file
```

## 🚀 Quick Start

**⚡ New: Cross-Platform Setup Script** - Works on Windows, macOS, and Linux!

### Recommended Setup (All Platforms)
```bash
# Full setup (backend + frontend) - Works everywhere!
python setup.py

# Backend only
python setup.py --backend

# Frontend only  
python setup.py --frontend

# Show help and options
python setup.py --help
```

### All Available Setup Methods

#### 🌍 Universal (All Platforms)
- `python setup.py` - **Recommended!** Cross-platform with error handling

#### 🖥️ Windows Options
- `python setup.py` - **Recommended**
- `.\setup.ps1` - PowerShell script with parameters  
- `setup.bat` - Interactive batch file

#### 🐧 Linux/macOS Options
- `python setup.py` - **Recommended**
- `make setup` - Traditional Makefile
- `./setup.sh` - Bash script with colored output

### Alternative Setup Methods

#### For Windows Users
```powershell
# Enhanced PowerShell script
.\setup.ps1

# With options
.\setup.ps1 -Backend
.\setup.ps1 -Frontend
.\setup.ps1 -Help
```

#### For macOS/Linux Users
```bash
# Make commands (Unix/Linux/macOS)
make setup           # Complete setup
make setup-python    # Use Python script (recommended)
make setup-backend   # Backend only
make setup-frontend  # Frontend only
```

### 💡 Quick Troubleshooting
- **Windows users experiencing "true is not recognized"**: Use `python setup.py` instead of make commands
- **"python: command not found"**: Try `python3 setup.py` or install Python from python.org
- **"node: command not found"**: Install Node.js from nodejs.org
- **Setup errors**: See [Cross-Platform Setup Guide](docs/cross_platform_setup.md) for detailed troubleshooting

### Prerequisites
- **Python 3.9+** - [Download from python.org](https://python.org)
- **Node.js 16+** - [Download from nodejs.org](https://nodejs.org)
- **PostgreSQL 12+** (recommended) or SQLite for development

## 📋 Migration Status

### ✅ Completed Entities
- **Accounts Receivables** (`cr7c4_accountsreceivables`)
  - Django Model: `AccountsReceivable`
  - API Endpoints: `/api/v1/accounts-receivables/`
  - React Component: `AccountsReceivablesScreen`
- **User Profiles** (Django-native)
  - Django Model: `UserProfile`
  - API Endpoints: `/api/v1/user-profiles/`
  - React Component: `UserProfile` dropdown with authentication

### 🔄 In Progress
- Infrastructure and documentation setup

### 📋 Planned Entities
- Suppliers (`cr7c4_supplier`)
- Customers (`pro_customer`)
- Contact Info (`pro_contactinfo`)
- Purchase Orders (`pro_purchaseorder`)
- Plants (`cr7c4_plant`)
- Carrier Info (`cr7c4_carrierinfo`)
- Supplier Locations (`pro_supplier_locations`)
- Supplier Plant Mapping (`pro_supplierplantmapping`)

## 🔄 PowerApps → Django Migration Mapping

| PowerApps Entity | Django Model | Key Fields | Status |
|------------------|--------------|------------|---------|
| `cr7c4_accountsreceivables` | `AccountsReceivable` | names, email, phone, terms | ✅ Complete |
| N/A (Django-native) | `UserProfile` | username, email, profile_image | ✅ Complete |
| `cr7c4_supplier` | `Supplier` | TBD | 📋 Planned |
| `pro_customer` | `Customer` | TBD | 📋 Planned |

*See [docs/migration_mapping.md](docs/migration_mapping.md) for detailed field mappings.*

## 🛠️ Development Workflow

### Adding New Entities
1. **Analyze PowerApps Entity**: Review XML export for field definitions
2. **Create Django Model**: Use standard Django patterns
3. **Add Serializers**: DRF serializers for API responses
4. **Create ViewSets**: REST API endpoints with filtering/pagination
5. **Build React Components**: Screens and reusable components
6. **Update Documentation**: API docs and migration notes

### Code Standards
- **Backend**: Follow Django/DRF best practices, use type hints
- **Frontend**: React functional components with hooks
- **Documentation**: Inline comments for PowerApps migrations
- **Testing**: Unit tests for models, integration tests for APIs

## 📚 Documentation

- **[Setup Overview](SETUP_OVERVIEW.md)** - **Start here! Complete setup guide and documentation index**
- **[Cross-Platform Setup Guide](docs/cross_platform_setup.md)** - **Comprehensive setup instructions with troubleshooting**
- **[Agent Quick Start Guide](docs/agent_quick_start.md)** - **Required reading for all agents**
- **[Agent Activity Log](docs/agent_activity_log.md)** - **Required logging for all work**
- **[Backend Setup Guide](docs/backend_setup.md)** - Detailed backend development setup
- **[Frontend Setup Guide](docs/frontend_setup.md)** - React development environment
- **[Production Deployment](docs/production_deployment.md)** - **Complete production deployment guide**
- **[API Reference](docs/api_reference.md)** - Complete API documentation
- **[Migration Mapping](docs/migration_mapping.md)** - PowerApps to Django mappings
- **[Optimization Report](OPTIMIZATION_REPORT.md)** - **Performance & security analysis**

## 🧪 Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests  
cd frontend
npm test

# Full test suite (Unix/Linux/macOS)
make test

# Windows PowerShell users can use:
# cd backend; python manage.py test
# cd frontend; npm test
```

**Test Status**: ✅ 76 backend tests passing consistently

## 🚀 Performance & Optimization

### Recent Optimizations ✅
- **Database indexes**: 18 strategic indexes added for improved query performance
- **Query optimization**: `select_related()` implemented to prevent N+1 queries
- **Code quality**: All critical linting issues resolved, automated formatting applied
- **Security review**: Comprehensive security assessment completed

### Performance Metrics
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