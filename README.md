# ProjectMeats

A comprehensive business management application for meat sales brokers, migrated from PowerApps/Dataverse to a modern Django REST Framework (backend) and React TypeScript (frontend) stack.

## 🚀 Quick Server Setup

**Having deployment issues? Two simple commands fix everything:**

### Step 1: Fix Server Configuration
```bash
sudo ./fix_server.sh
```

### Step 2: Deploy
```bash
cd /home/projectmeats/setup && sudo ./deploy.sh
```

**That's it!** Your server will be running at https://meatscentral.com

### 🔑 Default Login
- **Admin Panel**: https://meatscentral.com/admin/
- **Username**: admin
- **Password**: WATERMELON1219

## 🆘 Having Problems?

**Common Issues Fixed by `fix_server.sh`:**
- ❌ Missing directories (`/home/projectmeats/setup: No such file or directory`)
- ❌ Node.js conflicts (`nodejs : Conflicts: npm`)  
- ❌ Missing deployment files (`./deploy_server.sh: command not found`)
- ❌ Permission issues

**Quick Troubleshooting:**
```bash
# Check if fix worked
sudo ./fix_server.sh

# Check deployment status  
cd /home/projectmeats/setup && sudo ./deploy.sh
```

## 🏗️ Technology Stack

- **Backend**: Django 4.2.7 + Django REST Framework + PostgreSQL
- **Frontend**: React 18.2.0 + TypeScript + Styled Components  
- **Authentication**: Django User system with profile management
- **API**: RESTful endpoints with OpenAPI documentation

## 📁 Project Structure

```
ProjectMeats/
├── backend/                    # Django REST Framework API
│   ├── apps/                  # Business entities
│   │   ├── accounts_receivables/  # Customer payments
│   │   ├── suppliers/            # Supplier management
│   │   ├── customers/            # Customer relationships
│   │   └── purchase_orders/      # Order processing
│   └── requirements.txt
├── frontend/                   # React TypeScript application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── screens/           # Main application screens
│   │   └── services/         # API communication
│   └── package.json
└── docs/                      # Documentation
```

## 🚀 Development Setup

**Prerequisites**: Python 3.9+, Node.js 16+

```bash
# Clone repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Setup both backend and frontend
python setup.py

# Start development servers
make dev
```

## 📝 API Documentation

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🧪 Testing

```bash
# Run all tests
make test

# Backend tests only
cd backend && python manage.py test

# Frontend tests only
cd frontend && npm test
```

## 📋 Migration Status

This project migrates from PowerApps/Dataverse to Django + React. See `docs/migration_mapping.md` for detailed entity mapping and migration progress.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.