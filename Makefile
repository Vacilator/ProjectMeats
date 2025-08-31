# ProjectMeats Development Makefile
# Provides essential development commands for Django + React application

.PHONY: help setup dev test clean docs format lint docker-build docker-up docker-down prod-validate prod-up prod-down prod-logs prod-status

# Default target
help:
	@echo "ProjectMeats Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup         - Complete project setup (backend + frontend)"
	@echo "  make setup-backend - Setup Django backend only"
	@echo "  make setup-frontend- Setup React frontend only"
	@echo ""
	@echo "Recommended Setup:"
	@echo "  python setup.py           - Cross-platform setup (recommended)"
	@echo "  python setup.py --backend - Backend only"
	@echo "  python setup.py --frontend- Frontend only"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev       - Start both backend and frontend servers"
	@echo "  make backend   - Start Django development server"
	@echo "  make frontend  - Start React development server"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-build  - Build Docker Compose services"
	@echo "  make docker-up     - Start Docker Compose stack"
	@echo "  make docker-down   - Stop Docker Compose stack"
	@echo "  make docker-logs   - View Docker Compose logs"
	@echo ""
	@echo "Production Commands:"
	@echo "  make prod-validate - Validate production configuration"
	@echo "  make prod-up       - Start production stack"
	@echo "  make prod-down     - Stop production stack"
	@echo "  make prod-logs     - View production logs"
	@echo "  make prod-status   - Check production status"
	@echo ""
	@echo "Database Commands:"
	@echo "  make migrate   - Run Django migrations"
	@echo "  make migrations- Create new Django migrations"
	@echo "  make shell     - Open Django shell"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test      - Run all tests (backend + frontend)"
	@echo "  make test-backend  - Run Django tests only"
	@echo "  make test-frontend - Run React tests only"
	@echo "  make test-deployment - Test deployment configuration"
	@echo "  make test-service   - Run service diagnostics (requires sudo)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format    - Format code (black, isort)"
	@echo "  make lint      - Lint code (flake8)"
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

# Docker commands
docker-build:
	@echo "🐳 Building Docker Compose services..."
	docker compose build

docker-up:
	@echo "🚀 Starting Docker Compose stack..."
	docker compose up -d
	@echo "✅ Services started! Run 'make docker-logs' to view logs"

docker-down:
	@echo "🛑 Stopping Docker Compose stack..."
	docker compose down

docker-logs:
	@echo "📋 Viewing Docker Compose logs..."
	docker compose logs -f

# Production deployment commands
prod-validate:
	@echo "🔍 Validating production configuration..."
	./scripts/preflight/validate_prod_compose.sh

prod-up: prod-validate
	@echo "🚀 Starting production stack..."
	@echo "This will start ProjectMeats in production mode with Traefik reverse proxy"
	@echo "Services will be available at: https://${DOMAIN:-localhost}"
	docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
	@echo "✅ Production stack started!"
	@echo ""
	@echo "Monitor with: make prod-logs"
	@echo "Check status: make prod-status"

prod-down:
	@echo "🛑 Stopping production stack..."
	docker compose --env-file .env.prod -f docker-compose.prod.yml down
	@echo "✅ Production stack stopped"

prod-logs:
	@echo "📋 Viewing production logs..."
	docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f

prod-status:
	@echo "📊 Production stack status..."
	docker compose --env-file .env.prod -f docker-compose.prod.yml ps
	@echo ""
	@echo "📈 Resource usage:"
	docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

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

# Deployment testing
test-deployment:
	@echo "🧪 Testing deployment configuration..."
	./deployment/scripts/test_service_start.sh

test-service:
	@echo "🔍 Running service diagnostics..."
	sudo ./deployment/scripts/diagnose_service.sh

# Code quality
format:
	@echo "🎨 Formatting code..."
	cd backend && black . --exclude=migrations
	cd backend && isort . --skip=migrations

lint:
	@echo "🔍 Linting code..."
	cd backend && flake8 . --exclude=migrations

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