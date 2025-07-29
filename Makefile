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
	@echo "Agent Orchestration System:"
	@echo "  make agent-help        - Show all agent orchestration commands"
	@echo "  make agent-tasks       - List available tasks for assignment"
	@echo "  make agent-status      - View agent activity and task status"
	@echo "  make agent-assign      - Assign task to agent (requires TASK and AGENT)"
	@echo "  make agent-update      - Update task progress (requires TASK, AGENT, STATUS)"

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
	@python agent_orchestrator.py agent-status
	@echo ""
	@echo "To view full log: make agent-log"
	@echo "To add entry: make agent-log-edit"

# Agent orchestration commands
agent-tasks:
	@echo "📋 Available Agent Tasks:"
	@python agent_orchestrator.py list-tasks

agent-tasks-priority:
	@echo "🎯 High Priority Tasks:"
	@python agent_orchestrator.py list-tasks --priority P0
	@python agent_orchestrator.py list-tasks --priority P1

agent-assign:
	@echo "🎯 Assign Task to Agent"
	@echo "Usage: make agent-assign TASK=TASK-001 AGENT=agent_name"
	@if [ "$(TASK)" = "" ] || [ "$(AGENT)" = "" ]; then \
		echo "❌ Both TASK and AGENT must be specified"; \
		echo "Example: make agent-assign TASK=TASK-001 AGENT=john_doe"; \
	else \
		python agent_orchestrator.py assign-task $(TASK) $(AGENT); \
	fi

agent-update:
	@echo "📝 Update Task Status"
	@echo "Usage: make agent-update TASK=TASK-001 AGENT=agent_name STATUS=in_progress NOTES='Progress description'"
	@if [ "$(TASK)" = "" ] || [ "$(AGENT)" = "" ] || [ "$(STATUS)" = "" ]; then \
		echo "❌ TASK, AGENT, and STATUS must be specified"; \
		echo "Example: make agent-update TASK=TASK-001 AGENT=john_doe STATUS=completed NOTES='Fixed the issue'"; \
	else \
		python agent_orchestrator.py update-task $(TASK) $(AGENT) $(STATUS) --notes "$(NOTES)"; \
	fi

agent-conflicts:
	@echo "⚠️ Check Task Conflicts"
	@echo "Usage: make agent-conflicts TASK=TASK-001 AGENT=agent_name"
	@if [ "$(TASK)" = "" ] || [ "$(AGENT)" = "" ]; then \
		echo "❌ Both TASK and AGENT must be specified"; \
		echo "Example: make agent-conflicts TASK=TASK-001 AGENT=john_doe"; \
	else \
		python agent_orchestrator.py check-conflicts $(TASK) $(AGENT); \
	fi

agent-project-status:
	@echo "📊 ProjectMeats Overall Status:"
	@python agent_orchestrator.py project-status

agent-progress-report:
	@echo "📈 Generating Progress Report..."
	@python agent_orchestrator.py progress-report

agent-dashboard:
	@echo "📊 Generating Visual Progress Dashboard..."
	@python agent_dashboard.py
	@echo "✅ Dashboard saved to AGENT_PROGRESS_DASHBOARD.md"
	@echo "🔗 View at: file://$(PWD)/AGENT_PROGRESS_DASHBOARD.md"

agent-dashboard-json:
	@echo "📈 Generating Dashboard with JSON Metrics..."
	@python agent_dashboard.py --json
	@echo "✅ Dashboard and metrics generated"

agent-help:
	@echo "🤖 Agent Orchestration Commands:"
	@echo ""
	@echo "📋 Task Management:"
	@echo "  make agent-tasks              - List all available tasks"
	@echo "  make agent-tasks-priority     - Show high priority tasks only"
	@echo "  make agent-assign TASK=... AGENT=... - Assign task to agent"
	@echo "  make agent-update TASK=... AGENT=... STATUS=... NOTES=... - Update task status"
	@echo "  make agent-conflicts TASK=... AGENT=... - Check for conflicts"
	@echo ""
	@echo "📊 Status & Reporting:"
	@echo "  make agent-status             - Agent activity summary"
	@echo "  make agent-project-status     - Overall project status"
	@echo "  make agent-progress-report    - Detailed progress report"
	@echo "  make agent-dashboard          - Generate visual progress dashboard"
	@echo "  make agent-dashboard-json     - Generate dashboard with JSON metrics"
	@echo ""
	@echo "📝 Documentation:"
	@echo "  make agent-log                - View recent activity log"
	@echo "  make agent-log-edit           - Edit activity log"
	@echo ""
	@echo "Valid task statuses: available, in_progress, blocked, completed, cancelled"
	@echo "Valid priorities: P0 (critical), P1 (high), P2 (medium), P3 (low)"
	@echo ""
	@echo "Examples:"
	@echo "  make agent-assign TASK=TASK-001 AGENT=john_doe"
	@echo "  make agent-update TASK=TASK-001 AGENT=john_doe STATUS=completed NOTES='Fixed the bug'"
	@echo "  make agent-conflicts TASK=TASK-006 AGENT=jane_smith"

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