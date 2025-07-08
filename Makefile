# ProjectMeats Development Makefile
# Provides common development commands for Django + React monorepo

.PHONY: help setup dev test clean docs

# Default target
help:
	@echo "ProjectMeats Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup     - Complete project setup (backend + frontend)"
	@echo "  make setup-backend  - Setup Django backend only"
	@echo "  make setup-frontend - Setup React frontend only"
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

# Setup commands
setup: setup-backend setup-frontend
	@echo "✅ Complete setup finished! Run 'make dev' to start development."

setup-backend:
	@echo "🔧 Setting up Django backend..."
	cd backend && cp -n .env.example .env 2>/dev/null || true
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