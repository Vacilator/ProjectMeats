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
│   │   └── core/              # Shared utilities
│   ├── requirements.txt
│   ├── .env.example
│   └── manage.py
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # Reusable components
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

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+ (recommended) or SQLite for development

### 1. Backend Setup
```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 3. Using Make Commands (Recommended)
```bash
make setup      # Complete environment setup
make dev        # Start both backend and frontend
make test       # Run all tests
make docs       # Generate API documentation
```

## 📋 Migration Status

### ✅ Completed Entities
- **Accounts Receivables** (`cr7c4_accountsreceivables`)
  - Django Model: `AccountsReceivable`
  - API Endpoints: `/api/v1/accounts-receivables/`
  - React Component: `AccountsReceivablesScreen`

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
- **[Agent Quick Start Guide](docs/agent_quick_start.md)** - **Required reading for all agents**
- **[Agent Activity Log](docs/agent_activity_log.md)** - **Required logging for all work**
- **[Backend Setup Guide](docs/backend_setup.md)** - Detailed backend development setup
- **[Frontend Setup Guide](docs/frontend_setup.md)** - React development environment
- **[API Reference](docs/api_reference.md)** - Complete API documentation
- **[Migration Mapping](docs/migration_mapping.md)** - PowerApps to Django mappings

## 🧪 Testing

```bash
# Backend tests
cd backend && python manage.py test

# Frontend tests  
cd frontend && npm test

# Full test suite
make test
```

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