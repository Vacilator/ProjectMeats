# ProjectMeats Production Deployment

## Quick Start

### Docker Deployment (Recommended)
```bash
# Interactive setup
./deploy.py --interactive

# Direct deployment  
./deploy.py --server myserver.com --domain mydomain.com --docker

# With monitoring
./deploy.py --server myserver.com --domain mydomain.com --docker --monitoring
```

### Using AI Orchestrator Directly
```bash  
# Full automated deployment
python3 ai_deployment_orchestrator.py --server myserver.com --domain mydomain.com --docker --auto

# Interactive setup
python3 ai_deployment_orchestrator.py --interactive
```

## Features

✅ **Docker Deployment**: Industry-standard containerization with security hardening
✅ **Auto SSL/HTTPS**: Automatic SSL certificate generation and renewal
✅ **Security Hardening**: Non-root containers, security headers, rate limiting
✅ **DigitalOcean Optimized**: Optimized for DigitalOcean droplet performance
✅ **Monitoring**: Optional Prometheus/Grafana monitoring stack  
✅ **Health Checks**: Comprehensive health monitoring and alerting
✅ **Backup Strategy**: Automated database backups and retention
✅ **Zero Downtime**: Rolling updates and graceful shutdowns

## Architecture  

- **Frontend**: React TypeScript app served via nginx
- **Backend**: Django REST API with gunicorn
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis for sessions and caching
- **Reverse Proxy**: nginx with SSL termination
- **Background Tasks**: Celery worker processes
- **Monitoring**: Prometheus + Grafana (optional)

## File Structure

```
├── ai_deployment_orchestrator.py  # Primary deployment tool
├── deploy.py                      # Simple launcher
├── docker-compose.prod.yml        # Production Docker config
├── .env.prod.template             # Environment template
├── nginx/                         # nginx configurations
├── monitoring/                    # Prometheus/Grafana configs
└── legacy-deployment/             # Archived legacy scripts
```

## Support

For issues or questions, see the troubleshooting guides in `/docs/` or create an issue.
