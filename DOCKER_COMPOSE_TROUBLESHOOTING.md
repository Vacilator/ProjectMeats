# Docker Compose Production Troubleshooting Guide

## Common Docker Compose Issues and Solutions

### Issue: "Variable not set" warnings during docker-compose build

**Symptoms:**
```
WARN[0000] The "POSTGRES_USER" variable is not set. Defaulting to a blank string.
WARN[0000] The "qh5puqj2f2s" variable is not set. Defaulting to a blank string.
```

**Root Cause:**
Docker Compose cannot find the required environment variables defined in `.env.prod` file.

**Solution:**
1. Ensure that a `.env` file exists in the same directory as `docker-compose.prod.yml`
2. The `.env` file should contain the same variables as `.env.prod`

**For AI Deployment Orchestrator users:**
The AI deployment script automatically creates the `.env` file during deployment. If you're running docker-compose manually, create the `.env` file:

```bash
cp .env.prod .env
```

### Issue: Corrupted environment variable names (e.g., "nNfJ")

**Symptoms:**
```
WARN[0000] The "nNfJ" variable is not set. Defaulting to a blank string.
```

**Root Cause:**
Environment file contains corrupted or non-ASCII variable names, often due to encoding issues.

**Solution:**
1. **Use the quick fix script** (recommended):
   ```bash
   ./docker_production_quickfix.sh
   ```

2. **Manual fix**:
   ```bash
   # Recreate environment file from template
   cp .env.prod.example .env.prod
   
   # Clean any non-ASCII characters
   iconv -f utf-8 -t ascii//IGNORE .env.prod > .env.prod.clean
   mv .env.prod.clean .env.prod
   ```

### Issue: Files not found during Docker build

**Symptoms:**
```
ERROR: failed to calculate checksum: "/nginx.prod.conf": not found
ERROR: failed to calculate checksum: "/requirements-prod.txt": not found
```

**Root Cause:**
Required files are missing from build context or .env.prod doesn't exist.

**Solution:**
1. **Run the validation script**:
   ```bash
   ./validate_docker_production.sh
   ```

2. **Verify all required files exist**:
   ```bash
   ls nginx/nginx.prod.conf backend/requirements-prod.txt frontend/nginx.prod.conf
   ```

### Issue: "mapping key already defined" errors

**Symptoms:**
```
line 42: mapping key "image" already defined at line 39
```

**Root Cause:**
YAML syntax error due to duplicate keys in the docker-compose file.

**Solution:**
This has been resolved in the current version. All services now properly reference the `.env.prod` file via `env_file` directives.

### Issue: Environment variables not being loaded properly

**Symptoms:**
Services fail to start due to missing database credentials or other configuration.

**Root Cause:**
Services need explicit `env_file` references to load variables from `.env.prod`.

**Solution:**
Each service that uses environment variables now includes:
```yaml
env_file:
  - .env.prod
```

## Production Deployment Best Practices

1. **Use the AI Deployment Orchestrator**: `python ai_deployment_orchestrator.py --interactive`
2. **Verify configuration before deployment**: `docker compose -f docker-compose.prod.yml config --quiet`
3. **Ensure environment files exist**: Check that `.env.prod` contains all required variables
4. **Test build process**: Run `docker compose -f docker-compose.prod.yml build --dry-run` first

## Manual Docker Compose Deployment

If you need to deploy manually (not recommended for production):

### Quick Fix for Common Issues
```bash
# Use the quick fix script to resolve common deployment issues
./docker_production_quickfix.sh
```

### Manual Deployment Steps
```bash
# 1. Ensure environment file exists
cp .env.prod.example .env.prod

# 2. Edit with your production values
nano .env.prod

# 3. Validate the environment and configuration
./validate_docker_production.sh

# 4. Build and deploy
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# Note: .env.prod is already in .gitignore and won't be committed
```

## Required Environment Variables

The following variables must be defined in `.env.prod`:

- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user  
- `POSTGRES_PASSWORD` - Database password
- `REDIS_PASSWORD` - Redis password
- `DJANGO_SECRET_KEY` - Django secret key
- `ALLOWED_HOSTS` - Comma-separated allowed hosts
- `DOMAIN` - Primary domain name
- `GRAFANA_PASSWORD` - Grafana admin password

## Support

For deployment issues, use the AI Deployment Orchestrator which handles these configuration details automatically and provides comprehensive error recovery.