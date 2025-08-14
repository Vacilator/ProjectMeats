# Docker Compose Setup Guide for ProjectMeats

This guide provides comprehensive instructions for setting up and running ProjectMeats using Docker Compose. The setup supports both development and production environments.

## Prerequisites

- Docker (version 20.0 or higher)
- Docker Compose (version 2.0 or higher)
- Git

## Quick Start

### Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Vacilator/ProjectMeats.git
   cd ProjectMeats
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Start development services:**
   ```bash
   # For development with hot reload
   docker compose -f docker-compose.dev.yml up --build -d
   
   # Or for production-like environment
   docker compose up --build -d
   ```

4. **Initialize the application:**
   ```bash
   # Run database migrations
   docker compose exec backend python manage.py migrate
   
   # Create superuser account
   docker compose exec backend python manage.py createsuperuser --username admin --email admin@example.com
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Django Admin: http://localhost:8000/admin/

## Environment Configurations

### Development (.env file for development)
```bash
# Database
POSTGRES_DB=projectmeats_dev
POSTGRES_USER=projectmeats_user
POSTGRES_PASSWORD=dev_password_123

# Django
DJANGO_SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=*
```

### Production (.env file for production)
```bash
# Database
POSTGRES_DB=projectmeats_prod
POSTGRES_USER=projectmeats_user
POSTGRES_PASSWORD=secure_production_password_here

# Django
DJANGO_SECRET_KEY=your_very_secure_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost

# Security (for production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Docker Compose Files Overview

### docker-compose.yml (Default - Production-ready)
- Uses multi-stage builds for optimized images
- nginx-served frontend
- Health checks for all services
- Gunicorn for backend serving

### docker-compose.dev.yml (Development)
- Uses Django development server
- npm start for frontend with hot reload
- Volume mounts for live code changes
- Debug mode enabled

### docker-compose.prod.yml (High-Availability Production)
- Additional security headers
- Static and media file volumes
- Optimized for production deployment
- Includes nginx reverse proxy

## Available Commands

### Service Management
```bash
# Start all services
docker compose up -d

# Start with logs visible
docker compose up

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ destroys data)
docker compose down --volumes

# Restart specific service
docker compose restart [service_name]

# View service logs
docker compose logs -f [service_name]

# Build specific service
docker compose build [service_name]
```

### Backend Commands
```bash
# Django management commands
docker compose exec backend python manage.py [command]

# Common Django commands
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic
docker compose exec backend python manage.py shell

# Run tests
docker compose exec backend python manage.py test
```

### Database Commands
```bash
# Access PostgreSQL shell
docker compose exec db psql -U projectmeats_user -d projectmeats_db

# Create database backup
docker compose exec db pg_dump -U projectmeats_user projectmeats_db > backup.sql

# Restore from backup
docker compose exec -i db psql -U projectmeats_user projectmeats_db < backup.sql
```

### Frontend Commands
```bash
# Access frontend container
docker compose exec frontend sh

# Install new npm packages (development)
docker compose exec frontend npm install [package-name]

# Run frontend tests
docker compose exec frontend npm test
```

## Testing Your Setup

Run the comprehensive test script:
```bash
./test_docker.sh
```

This script will:
- Validate Docker installation
- Build and start all services
- Check health endpoints
- Verify database connectivity
- Test frontend and backend responses

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using the port
   sudo lsof -i :8000
   # Change port in docker-compose.yml if needed
   ```

2. **Permission issues:**
   ```bash
   # Fix ownership of files
   sudo chown -R $USER:$USER .
   ```

3. **Database connection issues:**
   ```bash
   # Check database logs
   docker compose logs db
   # Ensure environment variables are correct
   ```

4. **Frontend build issues:**
   ```bash
   # Clear npm cache and rebuild
   docker compose build --no-cache frontend
   ```

### Health Checks

The setup includes health checks for all services:
- Database: `pg_isready` command
- Backend: HTTP check on `/health/` endpoint
- Services won't start until dependencies are healthy

### Logs and Debugging

```bash
# View all service logs
docker compose logs

# Follow logs for specific service
docker compose logs -f backend

# View container resource usage
docker stats

# Inspect service configuration
docker compose config
```

## Production Deployment

For production deployment:

1. Use `docker-compose.prod.yml`
2. Set strong passwords in `.env`
3. Configure SSL certificates
4. Set up proper DNS
5. Configure backups
6. Set up monitoring

```bash
# Production deployment
docker compose -f docker-compose.prod.yml up --build -d
```

## File Structure

```
ProjectMeats/
├── docker-compose.yml          # Main production setup
├── docker-compose.dev.yml      # Development setup
├── docker-compose.prod.yml     # High-availability production
├── .env.example               # Environment template
├── test_docker.sh             # Testing script
├── backend/
│   ├── Dockerfile            # Backend container
│   ├── .dockerignore         # Backend build exclusions
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── Dockerfile            # Production frontend
│   ├── Dockerfile.dev        # Development frontend
│   ├── .dockerignore         # Frontend build exclusions
│   └── nginx.conf           # nginx configuration
└── nginx/                    # Reverse proxy (for prod)
```

## Security Considerations

- Change default passwords
- Use strong Django secret keys
- Enable SSL in production
- Regular security updates
- Limit database access
- Use environment-specific configurations

## Performance Optimization

- Use multi-stage Docker builds
- Enable gzip compression (nginx)
- Configure proper caching headers
- Use PostgreSQL connection pooling
- Monitor resource usage
- Regular database maintenance

For additional help, refer to the main README or create an issue in the GitHub repository.