# ProjectMeats Deployment with DigitalOcean PostgreSQL

This guide explains how to deploy ProjectMeats using the AI deployment orchestrator with a DigitalOcean managed PostgreSQL database.

## 🎯 Overview

The AI deployment orchestrator now supports external managed databases, allowing you to use DigitalOcean's managed PostgreSQL service instead of running PostgreSQL in a Docker container. This provides:

- **Better Performance**: Dedicated database resources
- **Automated Backups**: Built-in backup and recovery
- **High Availability**: Automatic failover and redundancy
- **Managed Maintenance**: Automatic updates and patches
- **SSL Security**: Required SSL connections for security

## 📋 Prerequisites

1. **DigitalOcean Managed PostgreSQL Database** - Set up and configured
2. **Server Access** - SSH access to your deployment server
3. **Domain Name** - Configured and pointing to your server
4. **SSL Certificates** - For HTTPS (handled automatically by the orchestrator)

## 🔧 Configuration

### 1. Database Credentials

The production configuration file `ai_deployment_config.production.json` contains the DigitalOcean PostgreSQL credentials:

```json
{
  "database": {
    "type": "postgresql",
    "host": "db-postgresql-nyc1-23354-do-user-24316406-0.h.db.ondigitalocean.com",
    "port": 25060,
    "name": "defaultdb", 
    "user": "doadmin",
    "password": "AVNS_Cxsh8ohPL3kbg-fZhQf",
    "external_managed": true,
    "ssl_mode": "require"
  },
  "docker": {
    "skip_database_container": true
  }
}
```

### 2. Security Features

- **SSL Required**: All database connections use SSL encryption
- **Managed Access**: Database access controlled through DigitalOcean's security groups
- **Secure Passwords**: Strong authentication credentials
- **Connection Pooling**: Optimized database connections

## 🚀 Deployment Methods

### Method 1: Using the Deployment Script (Recommended)

```bash
# Make sure you're in the ProjectMeats directory
cd /path/to/ProjectMeats

# Run the deployment script
./deploy_with_digitalocean_postgres.sh
```

The script will prompt you for:
- Server hostname/IP
- Domain name
- SSH username
- SSH key file (optional)

### Method 2: Using the Orchestrator Directly

```bash
python3 ai_deployment_orchestrator.py \
  --config ai_deployment_config.production.json \
  --server your-server.com \
  --domain your-domain.com \
  --username root \
  --key-file ~/.ssh/id_rsa \
  --docker \
  --external-db
```

### Method 3: Using Command Line Database Parameters

You can also override database settings via command line:

```bash
python3 ai_deployment_orchestrator.py \
  --server your-server.com \
  --domain your-domain.com \
  --docker \
  --external-db \
  --db-host db-postgresql-nyc1-23354-do-user-24316406-0.h.db.ondigitalocean.com \
  --db-port 25060 \
  --db-name defaultdb \
  --db-user doadmin \
  --db-password AVNS_Cxsh8ohPL3kbg-fZhQf \
  --db-ssl-mode require
```

## 🔍 Testing Configuration

Before deploying, validate your configuration:

```bash
python3 test_digitalocean_config.py
```

This will check:
- ✅ Configuration file exists and is valid
- ✅ Database credentials are complete
- ✅ External database settings are correct
- ✅ SSL mode is properly configured
- ✅ Docker settings skip local database container

## 📊 Docker Compose Changes

With external database configuration, the generated `docker-compose.prod.yml` will:

- **Skip PostgreSQL container** - No local database container
- **External DATABASE_URL** - Points to DigitalOcean PostgreSQL
- **SSL-enabled connections** - Uses `sslmode=require`
- **Backup service** - Configured for external database
- **Reduced resource usage** - Lower memory and CPU requirements

### Example Generated DATABASE_URL:
```
postgresql://doadmin:AVNS_Cxsh8ohPL3kbg-fZhQf@db-postgresql-nyc1-23354-do-user-24316406-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require
```

## 🔒 Security Considerations

1. **SSL Enforcement**: All database connections require SSL
2. **Credential Management**: Database password stored securely in environment files
3. **Network Security**: Database accessible only from authorized sources
4. **Access Control**: DigitalOcean manages database user permissions
5. **Audit Logging**: Connection and query logging enabled

## 📈 Performance Benefits

- **Dedicated Resources**: Database runs on dedicated hardware
- **Connection Pooling**: Optimized database connections
- **SSD Storage**: High-performance storage backend
- **Memory Optimization**: Tuned for production workloads
- **Query Optimization**: Built-in query performance monitoring

## 🛠 Troubleshooting

### Connection Issues
```bash
# Test database connectivity from your server
apt-get update && apt-get install -y postgresql-client
psql "postgresql://doadmin:AVNS_Cxsh8ohPL3kbg-fZhQf@db-postgresql-nyc1-23354-do-user-24316406-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
```

### SSL Certificate Issues
```bash
# Verify SSL connection
psql "postgresql://doadmin:AVNS_Cxsh8ohPL3kbg-fZhQf@db-postgresql-nyc1-23354-do-user-24316406-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require&sslcert=client-cert.pem&sslkey=client-key.pem&sslrootcert=ca-cert.pem"
```

### Configuration Validation
```bash
# Validate configuration before deployment
python3 test_digitalocean_config.py
```

## 📚 Additional Resources

- [DigitalOcean Managed Databases Documentation](https://docs.digitalocean.com/products/databases/)
- [PostgreSQL SSL Documentation](https://www.postgresql.org/docs/current/ssl-tcp.html)
- [Django Database Configuration](https://docs.djangoproject.com/en/4.2/ref/settings/#databases)

## 🤝 Support

For deployment issues or questions:
1. Check the orchestrator logs: `/opt/projectmeats/logs/`
2. Validate configuration: `python3 test_digitalocean_config.py`
3. Monitor services: `docker-compose ps`
4. Check database connectivity: Test with `psql` command above

---

**Note**: The DigitalOcean PostgreSQL credentials in this configuration are production credentials and should be kept secure. Never commit these credentials to public repositories.