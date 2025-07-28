#!/bin/bash
# ProjectMeats Unix/Linux/macOS Setup Script
# Alternative to Makefile for users who prefer shell scripts

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_step "🔍 Checking prerequisites..."
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        log_success "✓ Python3 found: $(python3 --version)"
    elif command -v python >/dev/null 2>&1; then
        log_success "✓ Python found: $(python --version)"
    else
        log_error "✗ Python not found. Please install Python 3.9+ from https://python.org"
        return 1
    fi
    
    # Check Node.js
    if command -v node >/dev/null 2>&1; then
        log_success "✓ Node.js found: $(node --version)"
    else
        log_error "✗ Node.js not found. Please install Node.js 16+ from https://nodejs.org"
        return 1
    fi
    
    # Check npm
    if command -v npm >/dev/null 2>&1; then
        log_success "✓ npm found: $(npm --version)"
    else
        log_error "✗ npm not found. Should come with Node.js"
        return 1
    fi
    
    # Check pip
    if command -v pip3 >/dev/null 2>&1; then
        log_success "✓ pip3 found"
    elif command -v pip >/dev/null 2>&1; then
        log_success "✓ pip found"
    else
        log_error "✗ pip not found. Should come with Python"
        return 1
    fi
    
    log_success "✅ Prerequisites check passed!"
    return 0
}

# Setup backend
setup_backend() {
    log_step "🔧 Setting up Django backend..."
    
    if [ ! -d "backend" ]; then
        log_error "Backend directory not found"
        return 1
    fi
    
    cd backend
    
    # Copy environment file
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "✓ Created .env file"
        else
            log_error "✗ .env.example not found"
            return 1
        fi
    else
        log_warning "ℹ️  .env file already exists"
    fi
    
    # Install Python dependencies
    log_info "📦 Installing Python dependencies..."
    
    # Determine pip command
    if command -v pip3 >/dev/null 2>&1; then
        pip3 install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
    
    # Run migrations
    log_info "🗃️  Running database migrations..."
    if command -v python3 >/dev/null 2>&1; then
        python3 manage.py migrate
    else
        python manage.py migrate
    fi
    
    log_success "✅ Backend setup complete!"
    cd ..
    return 0
}

# Setup frontend
setup_frontend() {
    log_step "🔧 Setting up React frontend..."
    
    if [ ! -d "frontend" ]; then
        log_error "Frontend directory not found"
        return 1
    fi
    
    cd frontend
    
    # Install Node.js dependencies
    log_info "📦 Installing Node.js dependencies..."
    npm install
    
    # Create environment file if needed
    if [ ! -f ".env.local" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env.local
            log_success "✓ Created .env.local from example"
        else
            cat > .env.local << EOF
# React Environment Variables
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
EOF
            log_success "✓ Created basic .env.local"
        fi
    else
        log_warning "ℹ️  .env.local already exists"
    fi
    
    log_success "✅ Frontend setup complete!"
    cd ..
    return 0
}

# Show next steps
show_next_steps() {
    log_success "🎉 Setup completed successfully!"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Start the backend server:"
    echo -e "   ${BLUE}cd backend && python manage.py runserver${NC}"
    echo ""
    echo "2. Start the frontend server (in another terminal):"
    echo -e "   ${BLUE}cd frontend && npm start${NC}"
    echo ""
    echo "3. Access the application:"
    echo -e "   ${BLUE}Backend API: http://localhost:8000${NC}"
    echo -e "   ${BLUE}Frontend:    http://localhost:3000${NC}"
    echo -e "   ${BLUE}API Docs:    http://localhost:8000/api/docs/${NC}"
    echo ""
    echo -e "${YELLOW}Alternative commands:${NC}"
    echo -e "   ${BLUE}make dev${NC}      - Start both servers"
    echo -e "   ${BLUE}make backend${NC}  - Start backend only"
    echo -e "   ${BLUE}make frontend${NC} - Start frontend only"
    echo ""
    echo -e "${YELLOW}For best experience, consider using:${NC}"
    echo -e "   ${BLUE}python setup.py${NC}"
}

# Show help
show_help() {
    echo "ProjectMeats Unix/Linux/macOS Setup Script"
    echo ""
    echo "Usage:"
    echo "  ./setup.sh                # Full setup (backend + frontend)"
    echo "  ./setup.sh backend        # Backend only"
    echo "  ./setup.sh frontend       # Frontend only"
    echo "  ./setup.sh --help         # Show this help"
    echo ""
    echo "Alternative (recommended):"
    echo "  python setup.py           # Cross-platform Python script"
    echo "  make setup                # Using Makefile"
    echo ""
    echo "For more information, see docs/setup_guide.md"
}

# Main function
main() {
    echo "============================================"
    echo " ProjectMeats Unix/Linux/macOS Setup Script"
    echo "============================================"
    echo ""
    
    case "${1:-full}" in
        "help" | "--help" | "-h")
            show_help
            exit 0
            ;;
        "backend")
            if ! check_prerequisites; then
                exit 1
            fi
            if ! setup_backend; then
                log_error "Backend setup failed"
                exit 1
            fi
            ;;
        "frontend")
            if ! check_prerequisites; then
                exit 1
            fi
            if ! setup_frontend; then
                log_error "Frontend setup failed"
                exit 1
            fi
            ;;
        "full" | *)
            if ! check_prerequisites; then
                exit 1
            fi
            if ! setup_backend; then
                log_error "Backend setup failed"
                exit 1
            fi
            if ! setup_frontend; then
                log_error "Frontend setup failed"
                exit 1
            fi
            ;;
    esac
    
    show_next_steps
}

# Run main function
main "$@"