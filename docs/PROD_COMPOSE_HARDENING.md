# Production Docker Compose Hardening Guide

This document explains the comprehensive security hardening measures implemented in ProjectMeats' production Docker Compose setup.

## Overview

ProjectMeats production deployment implements a defense-in-depth security approach with the following principles:

- **Secure by Default**: All services run with minimal privileges and security-hardened configurations
- **Network Isolation**: Backend services are isolated from internet access
- **Automatic TLS**: Let's Encrypt integration for automatic HTTPS certificates
- **Resource Governance**: Memory and CPU limits prevent resource exhaustion
- **Comprehensive Monitoring**: Health checks and logging for all services

## Architecture

```
Internet
    │
    ▼
┌─────────────────────────────────────────────────┐
│              Frontend Network                   │
│  ┌─────────────┐    ┌─────────────┐            │
│  │   Traefik   │    │  Frontend   │            │
│  │   Proxy     │◄───┤   (React)   │            │
│  │ (TLS Term.) │    │             │            │
│  └─────────────┘    └─────────────┘            │
│         │                                       │
└─────────┼───────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────┐
│             Backend Network (Internal)          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Django    │ │ PostgreSQL  │ │   Redis     ││
│  │  Backend    │ │  Database   │ │   Cache     ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
│  ┌─────────────┐                                │
│  │   Celery    │                                │
│  │   Worker    │                                │
│  └─────────────┘                                │
└─────────────────────────────────────────────────┘
```

## Security Hardening Measures

### 1. Reverse Proxy with Automatic TLS

**Traefik Reverse Proxy** replaces traditional nginx for automatic TLS management:

- **Automatic Let's Encrypt**: HTTP-01 challenge for certificate provisioning
- **HTTP to HTTPS Redirect**: All traffic automatically upgraded to HTTPS
- **TLS Termination**: SSL/TLS handled at the edge
- **No Manual Certificate Management**: Certificates automatically renewed

```yaml
# Traefik configuration highlights
traefik:
  command:
    - --certificatesresolvers.letsencrypt.acme.httpchallenge=true
    - --certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}
    - --entrypoints.web.http.redirections.entrypoint.to=websecure
```

### 2. Network Isolation

**Two-tier network architecture** ensures complete backend isolation:

- **Frontend Network**: External-facing, only Traefik and frontend containers
- **Backend Network**: Internal-only, no direct internet access
- **Service Discovery**: Containers communicate via Docker's internal DNS

```yaml
networks:
  frontend:
    driver: bridge
    internal: false  # Internet access for Traefik
  backend:
    driver: bridge
    internal: true   # No internet access
```

### 3. Container Security Context

**Every container runs with security hardening**:

- **Non-root Users**: All services run as unprivileged users
- **No New Privileges**: Prevents privilege escalation
- **Capability Dropping**: Removes unnecessary Linux capabilities
- **Read-only Root Filesystem**: Prevents runtime modifications

```yaml
# Example security context
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE  # Only for Traefik
read_only: true
user: "1000:1000"
```

### 4. Resource Governance

**Memory and CPU limits** prevent resource exhaustion attacks:

```yaml
# Resource limits per service
mem_limit: 512m
cpus: 1.0
```

Service allocations:
- **Traefik**: 256MB RAM, 0.5 CPU
- **Database**: 512MB RAM, 1.0 CPU  
- **Backend**: 1GB RAM, 2.0 CPU
- **Frontend**: 512MB RAM, 1.0 CPU
- **Redis**: 256MB RAM, 0.5 CPU
- **Celery**: 512MB RAM, 1.0 CPU

### 5. Health Monitoring

**Comprehensive health checks** for all services:

```yaml
healthcheck:
  test: ["CMD", "curl", "--fail", "http://localhost:8000/health/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 120s
```

### 6. Logging and Observability

**Structured logging** with automatic rotation:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 7. Secrets Management

**External environment file** prevents secrets in compose file:

- All secrets in `.env.prod` (excluded from version control)
- No hardcoded passwords or keys
- Strong password requirements enforced

## Deployment Process

### 1. Environment Setup

Copy and configure the environment template:

```bash
cp .env.prod.template .env.prod
nano .env.prod
```

Required configurations:
- `DOMAIN`: Your production domain
- `ACME_EMAIL`: Email for Let's Encrypt
- `POSTGRES_PASSWORD`: Strong database password
- `REDIS_PASSWORD`: Strong cache password  
- `DJANGO_SECRET_KEY`: Django secret key

### 2. Preflight Validation

Run comprehensive validation before deployment:

```bash
make prod-validate
```

This validates:
- Environment variables completeness and strength
- Docker availability and configuration
- Port availability (80, 443)
- System resources (memory, disk)
- Domain DNS configuration
- Docker Compose syntax

### 3. Production Deployment

Deploy with validated configuration:

```bash
make prod-up
```

This will:
- Re-run validation checks
- Build production images
- Start all services in correct order
- Configure Traefik routing and TLS

### 4. Monitoring

Monitor deployment status:

```bash
make prod-status    # Service status and resource usage
make prod-logs      # Real-time logs
```

## Security Checklist

Before going live, verify:

- [ ] All default passwords changed
- [ ] Domain DNS points to server
- [ ] Firewall allows only ports 80/443
- [ ] `.env.prod` file has secure values
- [ ] SSL certificates automatically provisioned
- [ ] All services healthy
- [ ] No direct backend access from internet

## TLS Configuration

### Automatic (Recommended)

Traefik handles TLS automatically:

1. **HTTP-01 Challenge**: Validates domain ownership
2. **Certificate Provisioning**: Downloads certificates from Let's Encrypt
3. **Automatic Renewal**: Certificates renewed before expiration
4. **HTTPS Redirect**: HTTP traffic redirected to HTTPS

### Manual (Alternative)

For manual certificate management, replace Traefik with nginx:

1. Copy `docker-compose.prod.yml` to `docker-compose.prod.manual.yml`
2. Replace Traefik service with nginx
3. Place certificates in `./ssl/` directory
4. Configure nginx for TLS termination

## Troubleshooting

### Common Issues

**"Port already in use"**
```bash
sudo netstat -tlpn | grep :80
sudo netstat -tlpn | grep :443
```

**"Let's Encrypt challenge failed"**
- Verify domain DNS points to server
- Ensure ports 80/443 are accessible from internet
- Check ACME_EMAIL is valid

**"Container fails health check"**
```bash
docker compose -f docker-compose.prod.yml logs [service-name]
```

**"Database connection failed"**
- Verify PostgreSQL password in `.env.prod`
- Check database service health
- Review network connectivity

### Log Locations

- **Application Logs**: `./logs/`
- **Container Logs**: `docker compose logs`
- **Traefik Logs**: Access and error logs in container
- **Database Logs**: PostgreSQL logs in container

### Recovery Procedures

**Complete stack restart**:
```bash
make prod-down
make prod-up
```

**Service-specific restart**:
```bash
docker compose -f docker-compose.prod.yml restart [service-name]
```

**Emergency shutdown**:
```bash
docker compose -f docker-compose.prod.yml down --remove-orphans
```

## Performance Optimization

### Resource Scaling

Scale backend workers:
```bash
docker compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Database Optimization

- Connection pooling via Django settings
- Regular vacuum and analyze
- Monitor slow queries

### Cache Optimization

- Redis persistence enabled
- Cache hit rate monitoring
- Memory usage optimization

## Backup Strategy

### Automated Backups

Database backups run daily (activate with backup profile):

```bash
docker compose -f docker-compose.prod.yml --profile backup up -d
```

### Manual Backup

```bash
docker exec projectmeats-db pg_dump -U projectmeats projectmeats > backup.sql
```

### Volume Backup

```bash
docker run --rm -v projectmeats_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
```

## Compliance and Auditing

### Security Standards

- **OWASP Top 10**: Addressed through framework security
- **CIS Docker Benchmarks**: Container hardening implemented
- **SOC 2**: Logging and monitoring capabilities
- **GDPR**: Data encryption and access controls

### Audit Trail

- All container access logged
- Application access via Django admin
- Database transactions logged
- File access monitoring

## Support and Maintenance

### Regular Tasks

- Monitor certificate expiration (automatic)
- Review security logs weekly
- Update base images monthly
- Test backup restoration quarterly

### Updates

Update production images:
```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### Monitoring Integration

Production setup supports optional monitoring:
```bash
docker compose -f docker-compose.prod.yml --profile monitoring up -d
```

This adds Prometheus and Grafana for comprehensive observability.

## Security Contacts

For security issues:
- Email: security@your-domain.com
- Incident Response: Follow internal procedures
- Vulnerability Reports: Responsible disclosure policy

---

This hardening guide ensures ProjectMeats production deployment meets enterprise security standards while maintaining operational simplicity.