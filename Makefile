# ProjectMeats Development Makefile
# Provides common development commands for Django + React monorepo

.PHONY: help setup dev test clean docs

# Default target
help:
	@echo "ProjectMeats Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup     - Complete project setup (backend + frontend)"
	@echo "  make setup-python    - Cross-platform setup using Python script (recommended)"
	@echo "  make setup-backend   - Setup Django backend only"
	@echo "  make setup-frontend  - Setup React frontend only"
	@echo ""
	@echo "Cross-Platform Setup (Recommended):"
	@echo "  python setup.py         - Full cross-platform setup"
	@echo "  python setup.py --backend   - Backend only"
	@echo "  python setup.py --frontend  - Frontend only"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev       - Start both backend and frontend servers"
	@echo "  make backend   - Start Django development server"
	@echo "  make frontend  - Start React development server"
	@echo ""
	@echo "Database Commands:"
	@echo "  make migrate   - Run Django migrations"
	@echo "  make migrations - Create new Django migrations"
	@echo "  make shell     - Open Django shell"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test      - Run all tests (backend + frontend)"
	@echo "  make test-backend  - Run Django tests only"
	@echo "  make test-frontend - Run React tests only"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs      - Generate API documentation"
	@echo "  make clean     - Clean build artifacts"
	@echo ""
	@echo "Agent Activity Logging:"
	@echo "  make agent-log - View recent agent activity log entries"
	@echo "  make agent-log-edit - Edit agent activity log"
	@echo "  make agent-status   - View agent activity summary"

# Setup commands
setup: check-os setup-backend setup-frontend
	@echo "✅ Complete setup finished! Run 'make dev' to start development."

# Cross-platform setup using Python script (recommended)
setup-python:
	@echo "🚀 Running cross-platform setup script..."
	python setup.py

setup-python-backend:
	@echo "🚀 Running cross-platform backend setup..."
	python setup.py --backend

setup-python-frontend:
	@echo "🚀 Running cross-platform frontend setup..."
	python setup.py --frontend

# OS detection and warning
check-os:
	@echo "🔍 Detecting operating system..."
ifeq ($(OS),Windows_NT)
	@echo "⚠️  Windows detected. For best experience, use:"
	@echo "   python setup.py         (recommended)"
	@echo "   or setup.ps1            (PowerShell script)"
	@echo ""
	@echo "⚠️  Make commands may not work properly on Windows."
	@echo "   Continuing with Unix-style commands..."
else
	@echo "✅ Unix-like system detected. Make commands should work properly."
endif

setup-backend:
	@echo "🔧 Setting up Django backend..."
ifeq ($(OS),Windows_NT)
	@echo "⚠️  Windows detected. Consider using: python setup.py --backend"
	cd backend && (copy .env.example .env 2>nul || echo .env file handling...)
else
	cd backend && cp -n .env.example .env 2>/dev/null || true
endif
	cd backend && pip install -r requirements.txt
	cd backend && python manage.py migrate
	@echo "✅ Backend setup complete!"

setup-frontend:
	@echo "🔧 Setting up React frontend..."
	cd frontend && npm install
	@echo "✅ Frontend setup complete!"

# Development commands
dev:
	@echo "🚀 Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo ""
	@make -j2 backend frontend

backend:
	@echo "🐍 Starting Django development server..."
	cd backend && python manage.py runserver

frontend:
	@echo "⚛️  Starting React development server..."
	cd frontend && npm start

# Database commands
migrate:
	cd backend && python manage.py migrate

migrations:
	cd backend && python manage.py makemigrations

shell:
	cd backend && python manage.py shell

# Testing commands
test: test-backend test-frontend

test-backend:
	@echo "🧪 Running Django tests..."
	cd backend && python manage.py test

test-frontend:
	@echo "🧪 Running React tests..."
	cd frontend && npm test -- --watchAll=false

# Documentation and cleanup
docs:
	@echo "📚 Generating API documentation..."
	cd backend && python manage.py spectacular --file ../docs/api_schema.yml
	@echo "✅ API schema generated at docs/api_schema.yml"

# Agent activity logging commands
agent-log:
	@echo "📝 Opening agent activity log..."
	@echo "File: docs/agent_activity_log.md"
	@echo ""
	@echo "Recent entries:"
	@tail -n 20 docs/agent_activity_log.md 2>/dev/null || echo "No log entries yet"

agent-log-edit:
	@echo "📝 Opening agent activity log for editing..."
	@echo "Remember to use the template provided in the file!"
	@${EDITOR:-nano} docs/agent_activity_log.md

agent-status:
	@echo "📊 Agent Activity Summary:"
	@echo ""
	@grep -c "## \[" docs/agent_activity_log.md 2>/dev/null | sed 's/^/Total log entries: /' || echo "Total log entries: 0"
	@echo ""
	@echo "Recent agent activities:"
	@grep "## \[" docs/agent_activity_log.md 2>/dev/null | head -5 || echo "No activities logged yet"
	@echo ""
	@echo "To view full log: make agent-log"
	@echo "To add entry: make agent-log-edit"

clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf build node_modules/.cache 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Development utilities
format:
	@echo "🎨 Formatting code..."
	cd backend && black . --exclude=migrations
	cd frontend && npm run format 2>/dev/null || echo "No formatter configured"

lint:
	@echo "🔍 Linting code..."
	cd backend && flake8 . --exclude=migrations
	cd frontend && npm run lint 2>/dev/null || echo "No linter configured"

# Quick entity scaffolding (example for future entities)
scaffold-entity:
	@echo "🏗️  Entity scaffolding template:"
	@echo "1. Create Django model in backend/apps/{entity_name}/"
	@echo "2. Add serializer and viewset"
	@echo "3. Create React screen component"
	@echo "4. Update API documentation"
	@echo "See existing accounts_receivables implementation for reference."