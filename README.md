# ProjectMeats

A comprehensive business management application for meat sales brokers, migrated from PowerApps/Dataverse to a modern Django REST Framework (backend) and React TypeScript (frontend) stack. This system manages suppliers, customers, purchase orders, accounts receivables, and related business entities with enterprise-grade security and scalability.

## 📖 Documentation Navigation

**🚀 New to ProjectMeats?** Start with the **[Setup Overview](SETUP_OVERVIEW.md)** for a comprehensive setup guide and links to all documentation.

**🤖 New to Agent Orchestration?** Check out the **[Agent Developer Guide](AGENT_ORCHESTRATION_DEVELOPER_GUIDE.md)** for the simplified workflow system that enables conflict-free parallel development.

## ⚠️ Python 3.13+ Setup Issue

**Windows users with Python 3.13+**: If setup fails with PostgreSQL adapter errors, see **[Python 3.13+ Setup Guide](PYTHON_3_13_SETUP.md)** for solutions.


## 🏗️ System Architecture

**Technology Stack:**
- **Backend**: Django 4.2.7 + Django REST Framework + PostgreSQL
- **Frontend**: React 18.2.0 + TypeScript + Styled Components  
- **Authentication**: Django User system with profile management
- **API**: RESTful endpoints with OpenAPI documentation
- **Testing**: 76+ comprehensive backend tests

**Project Structure:**

## 🏗️ Architecture Overview


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
│   │   ├── services/         # API communication
│   │   └── utils/
│   └── package.json
├── docs/                      # Documentation
│   ├── setup_guide.md         # Complete setup guide
│   ├── production_deployment.md # Enterprise deployment
│   ├── api_reference.md       # API documentation
│   └── migration_mapping.md   # PowerApps → Django mapping
├── powerapps_export/          # Original PowerApps solution
├── Makefile                   # Development commands
└── README.md                  # This file
```

## 🚀 Quick Setup

**⚡ Cross-Platform Setup Script** - Works on Windows, macOS, and Linux!

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

### Alternative Platform-Specific Methods

#### 🖥️ Windows
```powershell
python setup.py              # Recommended
.\setup.ps1                   # PowerShell script
setup.bat                     # Batch file (interactive)
```

#### 🐧 Linux/macOS
```bash
python setup.py              # Recommended
make setup                    # Makefile
./setup.sh                    # Shell script
```

## 🔧 Development Commands

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

## 🤖 AI-Enhanced Development with Smart Copilot

**💡 You can make Copilot smarter by setting up custom instructions, customizing its development environment and configuring Model Context Protocol (MCP) servers. Learn more Copilot coding agent tips in the docs.**

ProjectMeats provides an **enterprise-grade GitHub Copilot setup** with advanced AI context and optimization!

### 🚀 One-Click Enhanced Setup
```bash
# 🎯 Enhanced Copilot setup with MCP servers & optimization
python setup_copilot_enhanced.py

# 🔍 Verify existing configuration  
python verify_copilot_setup.py

# ⚡ Quick start with optimized workspace
python copilot_quickstart.py
```

### ✨ Smart Features Included

#### 🧠 **Advanced AI Context**
- **Custom Instructions**: Django/React/PowerApps migration patterns
- **MCP Servers**: Filesystem, Git, SQLite, Memory, and Documentation context
- **Smart Code Completion**: 5x more relevant suggestions with project context
- **Context Persistence**: AI remembers previous conversations and decisions

#### ⚙️ **Optimized Development Environment**  
- **VS Code Workspace**: Multi-folder setup with intelligent debugging
- **Enhanced Settings**: Smart formatting, linting, and code actions
- **Performance Tuned**: Optimized file watching and search exclusions
- **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux

#### 🎯 **Project-Specific Intelligence**
- **PowerApps Migration**: AI assistance for entity conversions
- **Django Patterns**: Model inheritance, DRF ViewSets, serializer templates
- **React Components**: TypeScript patterns, styled-components, hooks
- **API Design**: RESTful patterns with proper filtering and pagination

### 📚 Complete Documentation
- **[Enhanced Copilot Usage Guide](docs/copilot_usage_guide.md)** - Setup and advanced features
- **[Developer Guidelines](docs/copilot_developer_guidelines.md)** - Best practices and security
- **[Interactive Examples](docs/copilot_examples.md)** - Hands-on tutorials and demos
- **[Advanced Features](docs/copilot_advanced_features.md)** - Power-user workflows and optimization

### 🔧 Manual Setup (Alternative)
```bash
# Open with optimized VS Code workspace
code ProjectMeats.code-workspace

# Verify all configurations
python verify_copilot_setup.py
```

## 📋 Migration Status

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

### 🤖 AI-Enhanced Development 
- **[Enhanced Copilot Usage Guide](docs/copilot_usage_guide.md)** - **Advanced AI development with MCP servers**
- **[Copilot Developer Guidelines](docs/copilot_developer_guidelines.md)** - **Best practices for AI-assisted development**
- **[Interactive Copilot Examples](docs/copilot_examples.md)** - **Hands-on tutorials and demos**
- **[Advanced Copilot Features](docs/copilot_advanced_features.md)** - **Power-user workflows and optimization**

### 🛠️ Setup & Development
- **[Setup Overview](SETUP_OVERVIEW.md)** - **Start here! Complete setup guide and documentation index**
- **[Cross-Platform Setup Guide](docs/cross_platform_setup.md)** - **Comprehensive setup instructions with troubleshooting**
- **[Agent Quick Start Guide](docs/agent_quick_start.md)** - **Required reading for all agents**
- **[Agent Activity Log](docs/agent_activity_log.md)** - **Required logging for all work**
- **[Backend Setup Guide](docs/backend_setup.md)** - Detailed backend development setup
- **[Frontend Setup Guide](docs/frontend_setup.md)** - React development environment

### 📖 Reference & Deployment
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