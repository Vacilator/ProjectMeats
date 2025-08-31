# Developer Quick Start Guide - ProjectMeats

> **🎯 Goal**: Get new developers productive with ProjectMeats deployment in 15 minutes.

## 🚀 TL;DR - What You Need to Know

### Primary Rules
1. **Production Deployments**: Use `ai_deployment_orchestrator.py` ONLY
2. **Development**: Use `python setup.py` for local development setup
3. **Testing**: Use `docker-compose up` for quick testing
4. **Legacy Code**: Ignore everything in `legacy-deployment/` and most of `scripts/deployment/`

### Quick Commands
```bash
# Production deployment (PRIMARY METHOD)
python ai_deployment_orchestrator.py --server=your-server.com --domain=your-domain.com --auto

# Local development setup
python setup.py

# Local testing with Docker
docker-compose up
```

## 🛠️ Development Environment Setup

### 1. Clone and Setup (2 minutes)
```bash
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats
python setup.py  # Cross-platform setup script
```

### 2. Backend Development (Django)
```bash
cd backend
python manage.py migrate
python manage.py runserver
# Backend runs on http://localhost:8000
```

### 3. Frontend Development (React)
```bash
cd frontend
npm install
npm start
# Frontend runs on http://localhost:3000
```

### 4. Development with Docker (Alternative)
```bash
docker-compose up
# Full stack runs on http://localhost:3000
```

## 🎯 Tool Decision Matrix

| I Want To... | Use This Tool | Command |
|--------------|---------------|---------|
| **Deploy to production** | AI Orchestrator | `python ai_deployment_orchestrator.py --auto` |
| **Set up local dev environment** | Setup Script | `python setup.py` |
| **Test changes quickly** | Docker Compose | `docker-compose up` |
| **Run backend only** | Django | `cd backend && python manage.py runserver` |
| **Run frontend only** | React | `cd frontend && npm start` |
| **Run tests** | Make | `make test` |
| **Lint code** | Make | `make lint` |

## 🚨 What NOT to Use

### ❌ Deprecated/Legacy Tools
- `legacy-deployment/master_deploy.py` - Old deployment system
- `scripts/deployment/one_click_deploy.sh` - Superseded by AI orchestrator
- `scripts/deployment/deploy_production.py` - Legacy deployment
- Most files in `scripts/deployment/` - Use AI orchestrator instead

### ❌ Outdated Documentation
If you see docs mentioning these tools, they're outdated:
- References to "master_deploy.py"
- Instructions to run multiple deployment scripts
- Complex multi-step deployment procedures

## 📁 Repository Structure (What Matters for Development)

```
ProjectMeats/
├── ai_deployment_orchestrator.py          # 🎯 PRIMARY production deployment
├── setup.py                               # ✅ Local development setup
├── docker-compose.yml                     # ✅ Quick testing
├── backend/                               # ✅ Django application
├── frontend/                              # ✅ React application
├── docs/                                  # ✅ Current documentation
├── PRODUCTION_DEPLOYMENT_GUIDE.md         # ✅ Main deployment guide
│
├── legacy-deployment/                     # ❌ IGNORE - deprecated
├── scripts/deployment/                    # ❌ MOSTLY IGNORE - legacy scripts
└── [lots of other .md files]             # ❌ MOSTLY IGNORE - outdated docs
```

## 🔄 Common Development Workflows

### New Feature Development
```bash
# 1. Setup local environment
python setup.py

# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Develop and test locally
cd backend && python manage.py test
cd frontend && npm test

# 4. Test with Docker
docker-compose up

# 5. Deploy to staging/production
python ai_deployment_orchestrator.py --server=staging-server.com --auto
```

### Bug Fix Workflow
```bash
# 1. Reproduce issue locally
docker-compose up

# 2. Fix and test
make test

# 3. Deploy fix
python ai_deployment_orchestrator.py --server=production-server.com --auto
```

### Database Changes
```bash
# 1. Create migration locally
cd backend
python manage.py makemigrations

# 2. Test migration
python manage.py migrate

# 3. Deploy with migration
python ai_deployment_orchestrator.py --server=your-server.com --migrate-only
```

## 🐛 Common Developer Issues & Solutions

### "Which deployment tool should I use?"
**Answer**: `ai_deployment_orchestrator.py` for production, `python setup.py` for local development.

### "The documentation says to use master_deploy.py"
**Answer**: That documentation is outdated. Always use the AI orchestrator for production.

### "There are so many deployment scripts, which one is right?"
**Answer**: Ignore them all. Use only `ai_deployment_orchestrator.py` for production deployments.

### "My local setup isn't working"
**Answer**: Run `python setup.py` - it handles cross-platform setup automatically.

### "How do I deploy just my changes?"
**Answer**: `python ai_deployment_orchestrator.py --server=your-server.com --update-only`

### "The deployment failed, what do I do?"
**Answer**: The AI orchestrator automatically creates GitHub issues with @copilot for failed deployments. Check your GitHub issues.

## 📚 Essential Documentation (Only These 5 Files)

1. **[PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)** - Main deployment guide
2. **[DEVELOPER_QUICK_START.md](DEVELOPER_QUICK_START.md)** - This file
3. **[TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)** - When things go wrong
4. **[CONFIGURATION_REFERENCE.md](CONFIGURATION_REFERENCE.md)** - All config options
5. **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)** - Power user features

**Ignore all other .md files** - they're either outdated or duplicative.

## 🎓 Onboarding Checklist for New Developers

### Day 1: Environment Setup
- [ ] Clone repository
- [ ] Run `python setup.py` for local development
- [ ] Test local backend: `cd backend && python manage.py runserver`
- [ ] Test local frontend: `cd frontend && npm start`
- [ ] Test with Docker: `docker-compose up`
- [ ] Read this guide and the Production Deployment Guide

### Day 2: First Deployment
- [ ] Get access to staging server
- [ ] Deploy to staging: `python ai_deployment_orchestrator.py --server=staging.com --auto`
- [ ] Verify deployment worked
- [ ] Read troubleshooting guide

### Day 3: Development Workflow
- [ ] Create a test feature branch
- [ ] Make a small change
- [ ] Test locally and with Docker
- [ ] Deploy to staging
- [ ] Review code with team

## 🔧 IDE/Editor Setup

### VS Code (Recommended)
The repository includes `.vscode/` settings with:
- Python/Django configuration
- React/TypeScript configuration
- Recommended extensions
- Debug configurations

### PyCharm
- Open the `backend/` folder as a Django project
- Open the `frontend/` folder as a React project
- Configure Python interpreter to use virtual environment

## 🚀 Quick Deployment Examples

### Deploy to Production
```bash
python ai_deployment_orchestrator.py \
  --server=production.mycompany.com \
  --domain=mycompany.com \
  --github-user=myusername \
  --github-token=$GITHUB_TOKEN \
  --auto
```

### Deploy to Staging
```bash
python ai_deployment_orchestrator.py \
  --server=staging.mycompany.com \
  --domain=staging.mycompany.com \
  --auto
```

### Update Existing Deployment
```bash
python ai_deployment_orchestrator.py \
  --server=production.mycompany.com \
  --update-only \
  --auto
```

---

## 🎯 Summary for New Developers

**Remember these key points:**

1. **One Tool for Production**: `ai_deployment_orchestrator.py` is the ONLY tool for production deployments
2. **Simple Local Setup**: `python setup.py` gets you started locally
3. **Ignore Legacy Code**: Don't use anything in `legacy-deployment/` or most of `scripts/deployment/`
4. **Five Essential Docs**: Only read the 5 essential documentation files listed above
5. **When in Doubt**: Use the AI orchestrator or ask for help

**You're now ready to develop and deploy ProjectMeats efficiently!** 🎉