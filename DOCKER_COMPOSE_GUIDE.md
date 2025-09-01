# Docker Compose Deployment Guide

## Overview

ProjectMeats now includes Docker Compose support for easy containerized deployment. This provides an alternative to the traditional one-click deployment script for environments where Docker is preferred.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose V2
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats
```

### 2. Build and Start Services

```bash
docker compose up --build -d
```

This will start:
- PostgreSQL 13 database
- Django backend (Python 3.9)
- React frontend (Node 16)
- Nginx reverse proxy

### 3. Initialize Database

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser --username admin --email admin@example.com
```

### 4. Access the Application

- **Frontend**: http://your_droplet_ip
- **Admin Panel**: http://your_droplet_ip/admin
- **API Documentation**: http://your_droplet_ip/api/docs

## Services Architecture

### Database (PostgreSQL 13)
- Port: 5432 (exposed)
- Database: `projectmeats_db`
- User: `projectmeats_user`
- Password: `WATERMELON1219`
- Volume: `postgres_data` (persistent storage)

### Backend (Django + Gunicorn)
- Port: 8000 (exposed)
- Python 3.9 with multi-stage build
- Environment variables:
  - `DATABASE_URL`: Connection to PostgreSQL service
  - `DJANGO_SECRET_KEY`: Django secret key
  - `DEBUG`: Set to False for production
- Volume mounted for development sync

### Frontend (React + Serve)
- Port: 3000 (exposed)
- Node 16 with multi-stage build
- Built React app served with `serve`
- Volume mounted for development sync

### Nginx (Reverse Proxy)
- Port: 80 (main entry point)
- Routes `/api` and `/admin` to backend
- Routes `/` to frontend
- Security headers included:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block

## Configuration Files

### docker-compose.yml
Main orchestration file defining all services and their relationships.

### nginx/Dockerfile
Simple Nginx container with custom configuration.

### nginx/nginx.conf
Reverse proxy configuration with security headers.

### backend/Dockerfile
Multi-stage Django build (Python 3.9):
1. Builder stage: Install dependencies
2. Production stage: Copy dependencies and run Gunicorn

### frontend/Dockerfile
Multi-stage React build (Node 16):
1. Builder stage: Build React app
2. Production stage: Serve with `serve` package

## Management Commands

### View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx
docker compose logs -f db
```

### Execute commands in containers
```bash
# Django management commands
docker compose exec backend python manage.py <command>

# Access Django shell
docker compose exec backend python manage.py shell

# Access PostgreSQL
docker compose exec db psql -U projectmeats_user -d projectmeats_db
```

### Stop and start services
```bash
# Stop all services
docker compose down

# Start services
docker compose up -d

# Rebuild and start
docker compose up --build -d
```

### Database backup and restore
```bash
# Backup
docker compose exec db pg_dump -U projectmeats_user projectmeats_db > backup.sql

# Restore
docker compose exec -T db psql -U projectmeats_user projectmeats_db < backup.sql
```

## Environment Variables

You can customize the deployment by creating a `.env` file:

```env
# Database configuration
POSTGRES_USER=projectmeats_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=projectmeats_db

# Django configuration
DJANGO_SECRET_KEY=your_super_secure_secret_key
DEBUG=False

# Ports (if you need to change them)
POSTGRES_PORT=5432
BACKEND_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=80
```

## Production Considerations

### Security Hardening (Enhanced)
1. **Use hardened production compose**: `docker-compose.prod.yml` with Traefik and automatic TLS
2. **Environment security**: Copy `.env.prod.template` to `.env.prod` with strong passwords
3. **Network isolation**: Backend services isolated from internet access
4. **Container security**: All services run as non-root with minimal privileges
5. **Validation**: Run `make prod-validate` before deployment
6. **Monitoring**: Comprehensive health checks and logging

### Deployment Process
```bash
# 1. Configure environment
cp .env.prod.template .env.prod
nano .env.prod  # Set all required values

# 2. Validate configuration  
make prod-validate

# 3. Deploy with security hardening
make prod-up

# 4. Monitor deployment
make prod-status
make prod-logs
```

### Performance
1. **Scale services** using `docker compose up --scale backend=3`
2. **Use external database** for high-traffic scenarios
3. **Configure nginx caching** for static assets
4. **Monitor resource usage** with `docker stats`

### Backup Strategy
1. **Database**: Regular pg_dump backups
2. **Media files**: Backup mounted volumes
3. **Configuration**: Keep docker-compose.yml and configs in version control

## Integration with Existing Deployment

This Docker Compose setup works alongside the existing one-click deployment script (`one_click_deploy.sh`). Choose the method that best fits your infrastructure:

- **Docker Compose**: For containerized environments, development, or when you prefer Docker
- **One-click script**: For traditional VPS deployment with direct installation

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 80, 3000, 8000, 5432 are available
2. **Permission issues**: Check Docker daemon permissions
3. **Build failures**: Clear Docker cache with `docker system prune -a`
4. **Database connection**: Wait for database to fully start before backend

### Debug Commands
```bash
# Check container status
docker compose ps

# Check container health
docker compose exec backend python manage.py check

# View real-time logs
docker compose logs -f --tail=100

# Access container shell
docker compose exec backend bash
docker compose exec frontend sh
```

## Development Workflow

For development, the volume mounts allow for live code reloading:

1. Make changes to backend code → Django auto-reloads
2. Make changes to frontend code → React development server reloads
3. Make changes to nginx config → Restart nginx service

```bash
# Restart specific service after config changes
docker compose restart nginx
docker compose restart backend
```

This Docker Compose setup provides a complete, portable, and production-ready deployment solution for ProjectMeats.