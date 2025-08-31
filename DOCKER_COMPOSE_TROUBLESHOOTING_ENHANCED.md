# Docker Compose Production Troubleshooting Guide

## Enhanced Docker Deployment with AI Orchestrator Improvements

This guide covers troubleshooting for the enhanced Docker deployment system implemented by the AI Deployment Orchestrator with comprehensive preemptive error handling.

## Common Docker Compose Issues and Enhanced Solutions

### Issue: "Variable not set" warnings during docker-compose build

**Symptoms:**
```
WARN[0000] The "POSTGRES_USER" variable is not set. Defaulting to a blank string.
WARN[0000] The "qh5puqj2f2s" variable is not set. Defaulting to a blank string.
```

**Root Cause:**
Docker Compose cannot find the required environment variables defined in `.env.prod` file.

**Enhanced Solution (AI Orchestrator v2.0):**
The AI deployment script now includes comprehensive environment variable validation:

1. **Automatic validation** - All environment variables are validated before deployment
2. **Atomic file creation** - Environment files are created atomically to prevent corruption  
3. **Security validation** - Passwords are validated for minimum complexity
4. **Backup and recovery** - Automatic backup of existing environment files

**For AI Deployment Orchestrator users:**
The enhanced AI deployment script automatically:
- Creates validated `.env` file during deployment
- Validates all required variables exist and meet security requirements
- Creates symbolic link from `.env.prod` to `.env` for Docker Compose compatibility

**Manual fix (if needed):**
```bash
cp .env.prod .env
# Verify all required variables are set
python scripts/testing/test_docker_deployment_comprehensive.py
```

### Issue: "mapping key already defined" errors

**Symptoms:**
```
line 42: mapping key "image" already defined at line 39
```

**Root Cause:**
YAML syntax error due to duplicate keys in the docker-compose file.

**Enhanced Solution:**
The enhanced docker-compose.prod.yml now includes:
- ✅ **Syntax validation** - All YAML is validated before writing
- ✅ **Security hardening** - Resource limits, security options, logging
- ✅ **Health checks** - Comprehensive health monitoring for all services
- ✅ **Network isolation** - Proper frontend/backend network separation

### Issue: Environment variables not being loaded properly

**Symptoms:**
Services fail to start due to missing database credentials or other configuration.

**Root Cause:**
Services need explicit `env_file` references and proper variable defaults.

**Enhanced Solution:**
The enhanced docker-compose configuration now includes:
```yaml
services:
  backend:
    env_file:
      - .env.prod
    environment:
      - DATABASE_URL=postgres://${POSTGRES_USER:-projectmeats}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB:-projectmeats}
      # All variables now include proper defaults
```

### NEW: Docker Repository Configuration Issues

**Symptoms:**
```
E: The repository 'https://download.docker.com/linux/ubuntu $(lsb_release Release' not found
W: Failed to fetch https://download.docker.com/linux/ubuntu/dists/$(lsb_release Release/InRelease
```

**Root Cause:**
Malformed Docker repository entries with incorrect lsb_release patterns.

**Enhanced Solution (AI Orchestrator v2.0):**
The AI deployment script now includes:
- ✅ **Comprehensive repository cleanup** - Removes all known malformed patterns
- ✅ **Multi-method Ubuntu detection** - Fallback methods for Ubuntu codename detection  
- ✅ **Repository validation** - Validates repository URLs before adding
- ✅ **Retry logic** - Automatic retry with repository fixes

**Detected malformed patterns:**
- `$(lsb_release Release` (missing closing ) and -cs)
- `$(lsb_release)` (missing -cs flag)
- `$(lsb_release -cs ` (missing closing ))
- `$(lsb_release -c)` (wrong flag, should be -cs)

### NEW: Docker Build Process Failures

**Enhanced Build Process (AI Orchestrator v2.0):**
- ✅ **Pre-build validation** - Disk space, network connectivity, prerequisites
- ✅ **Base image pulling with retry** - Robust image pulling with timeout handling
- ✅ **Build error analysis** - Intelligent analysis of build failures
- ✅ **Comprehensive validation** - Image verification after builds
- ✅ **Resource monitoring** - Memory and disk usage monitoring during builds

**Common build issues automatically handled:**
- Insufficient disk space → Automatic cleanup
- Network timeouts → Retry with exponential backoff
- Permission issues → Automatic permission fixes
- Missing dependencies → Package repository updates

### NEW: Container Security Validation

**Enhanced Security (AI Orchestrator v2.0):**
- ✅ **Non-root execution** - All containers run as non-root users
- ✅ **Read-only root filesystem** - Prevents runtime modifications
- ✅ **No new privileges** - Prevents privilege escalation
- ✅ **Resource limits** - Memory and CPU limits for all services
- ✅ **Network isolation** - Backend network is internal-only
- ✅ **Security scanning** - Automatic validation of security settings

## Production Deployment Best Practices

1. **Use the Enhanced AI Deployment Orchestrator**: 
   ```bash
   python ai_deployment_orchestrator.py --interactive --docker
   ```

2. **Comprehensive pre-deployment testing**:
   ```bash
   python scripts/testing/test_docker_deployment_comprehensive.py
   ```

3. **Validate configuration before deployment**: 
   ```bash
   docker compose -f docker-compose.prod.yml config --quiet
   ```

4. **Ensure environment files exist and are validated**: 
   The AI orchestrator automatically validates all environment variables

5. **Test build process with validation**: 
   The AI orchestrator includes comprehensive build validation

## Enhanced Monitoring and Logging

### Centralized Logging
All containers now include structured logging:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Health Monitoring
Comprehensive health checks for all critical services:
- Database connectivity validation
- Redis connectivity validation  
- Backend API health endpoints
- Nginx proxy health checks

### Automated Backup System
Enhanced backup system includes:
- Database backups with compression
- Volume backups for persistent data
- Configuration backups
- Automated cleanup of old backups

## Troubleshooting Tools

### 1. Comprehensive Testing Suite
```bash
python scripts/testing/test_docker_deployment_comprehensive.py --verbose
```

### 2. Health Check Monitoring
```bash
/opt/projectmeats/monitoring/health-check.sh
```

### 3. Backup and Recovery
```bash
# Create backup
/opt/projectmeats/monitoring/backup.sh

# Restore from backup
/opt/projectmeats/monitoring/recovery.sh BACKUP_DATE
```

### 4. Container Diagnostics
```bash
# Check container health
docker compose -f docker-compose.prod.yml ps

# View container logs
docker logs projectmeats-backend --tail 50

# Execute commands in containers
docker exec -it projectmeats-backend bash
```

## Security Validation

The enhanced system includes automatic security validation:

1. **Container Security Checks**
   - Non-root user execution
   - Read-only root filesystem
   - No privileged containers
   - Security options applied

2. **Network Security Checks**
   - Backend network isolation
   - Proper port exposure
   - No unnecessary network access

3. **Data Security Checks**
   - Environment variable encryption
   - Secret management validation
   - Password complexity requirements

## Emergency Recovery

If deployment fails completely:

1. **Automated cleanup**:
   ```bash
   python ai_deployment_orchestrator.py --cleanup-failed
   ```

2. **Manual cleanup**:
   ```bash
   docker compose -f docker-compose.prod.yml down --remove-orphans --volumes
   docker system prune -f
   ```

3. **Restore from backup**:
   ```bash
   /opt/projectmeats/monitoring/recovery.sh LATEST_BACKUP
   ```

## Enhanced Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Enhanced Docker Architecture              │
├─────────────────────────────────────────────────────────────┤
│  Frontend Network (External)                               │
│  ┌─────────────┐    ┌─────────────┐                       │
│  │   Nginx     │    │  Frontend   │                       │
│  │  (Proxy)    │    │  (React)    │                       │
│  └─────────────┘    └─────────────┘                       │
├─────────────────────────────────────────────────────────────┤
│  Backend Network (Internal Only)                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Backend    │ │ PostgreSQL  │ │   Redis     │          │
│  │ (Django)    │ │ (Database)  │ │  (Cache)    │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  Monitoring & Backup (Optional)                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Prometheus  │ │   Grafana   │ │   Backup    │          │
│  │(Metrics)    │ │(Dashboard)  │ │ (Automated) │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Contact and Support

For deployment issues:
1. Run comprehensive testing suite first
2. Check deployment logs at `/opt/projectmeats/logs/`
3. Use health monitoring scripts for diagnostics
4. Consult backup and recovery procedures if needed

The enhanced AI Deployment Orchestrator provides comprehensive error handling and preemptive fixes for all known Docker deployment issues.