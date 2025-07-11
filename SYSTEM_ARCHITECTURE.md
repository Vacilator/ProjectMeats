# ProjectMeats System Architecture & Requirements

## 🏗️ System Architecture Overview

ProjectMeats is a modern web application migrated from PowerApps/Dataverse to a scalable Django REST Framework backend with React TypeScript frontend. This document outlines the complete system architecture and requirements for production deployment.

## 📊 Application Structure Analysis

### Backend (Django REST Framework)
- **Framework**: Django 4.2.7 with Django REST Framework 3.14.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **API**: RESTful API with OpenAPI documentation
- **Authentication**: Django's built-in authentication system
- **File Handling**: Django FileField for document uploads
- **Testing**: 76 comprehensive tests covering all entities

### Frontend (React TypeScript)
- **Framework**: React 18.2.0 with TypeScript 4.9.0
- **Styling**: Styled Components 6.1.0
- **Routing**: React Router DOM 6.8.0
- **HTTP Client**: Axios 1.6.0
- **Design System**: Custom component library with modern UI

### Entity Management System
ProjectMeats manages 9 core business entities:

1. **Accounts Receivables** - Customer payment tracking
2. **Suppliers** - Supplier information and relationships
3. **Customers** - Customer management
4. **Plants** - Processing facilities and locations
5. **Supplier Locations** - Supplier facility management
6. **Contact Info** - Contact relationship management
7. **Carrier Info** - Transportation provider management
8. **Purchase Orders** - Order processing with file attachments
9. **Supplier Plant Mappings** - Relationship mapping

## 🖥️ Infrastructure Requirements

### Minimum Production Requirements

**Single Server Deployment:**
- **CPU**: 2 vCPUs (3.0 GHz)
- **RAM**: 4GB (8GB recommended)
- **Storage**: 50GB SSD
- **Network**: 100Mbps connection
- **OS**: Ubuntu 20.04 LTS or 22.04 LTS

**Multi-Server Production (Recommended):**
- **Web Server**: 2 vCPUs, 4GB RAM (Nginx + React)
- **App Server**: 4 vCPUs, 8GB RAM (Django + Gunicorn)
- **Database Server**: 4 vCPUs, 8GB RAM (PostgreSQL)
- **Load Balancer**: 2 vCPUs, 2GB RAM (Optional)

### Scalability Requirements

**Small Business (< 100 users):**
- Single server deployment
- SQLite or small PostgreSQL instance
- Local file storage

**Medium Business (100-1000 users):**
- Multi-server deployment
- Dedicated database server
- Redis caching
- CDN for static files

**Enterprise (1000+ users):**
- Load-balanced application servers
- Database clustering/read replicas
- Distributed file storage (S3)
- Monitoring and alerting systems

## 🔧 Technology Stack

### Core Technologies
```
Backend:
├── Django 4.2.7
├── Django REST Framework 3.14.0
├── PostgreSQL 12+
├── Gunicorn 21.2.0
├── Redis (caching)
└── Celery (background tasks)

Frontend:
├── React 18.2.0
├── TypeScript 4.9.0
├── Styled Components 6.1.0
├── React Router DOM 6.8.0
└── Axios 1.6.0

Infrastructure:
├── Nginx (reverse proxy)
├── Let's Encrypt (SSL)
├── UFW (firewall)
├── Fail2Ban (security)
└── Systemd (process management)
```

### Development Tools
```
Code Quality:
├── ESLint (JavaScript/TypeScript)
├── Prettier (code formatting)
├── Black (Python formatting)
├── Flake8 (Python linting)
└── pytest (Python testing)

Build Tools:
├── Webpack (bundling)
├── npm/yarn (package management)
├── pip (Python packages)
└── Git (version control)
```

## 🌐 Network Architecture

### Production Network Topology
```
Internet
    │
    ▼
┌─────────────┐
│ Load        │
│ Balancer    │ (Optional)
│ (HAProxy)   │
└─────────────┘
    │
    ▼
┌─────────────┐
│ Web Server  │
│ (Nginx)     │
│ - React App │
│ - SSL Term  │
└─────────────┘
    │
    ▼
┌─────────────┐
│ App Server  │
│ (Django)    │
│ - API       │
│ - Business  │
│   Logic     │
└─────────────┘
    │
    ▼
┌─────────────┐
│ Database    │
│ (PostgreSQL)│
│ - Data      │
│ - Backups   │
└─────────────┘
```

### Port Configuration
- **80**: HTTP (redirects to HTTPS)
- **443**: HTTPS (public web access)
- **8000**: Django application (internal)
- **5432**: PostgreSQL (internal)
- **6379**: Redis (internal)
- **22**: SSH (administrative access)

## 🔒 Security Architecture

### Security Layers

**1. Network Security:**
- UFW firewall configuration
- Fail2Ban intrusion prevention
- SSH key-based authentication
- VPN access for administration

**2. Application Security:**
- HTTPS with TLS 1.2+
- Security headers (HSTS, CSP, etc.)
- CSRF protection
- SQL injection prevention
- XSS protection

**3. Data Security:**
- Database encryption at rest
- Encrypted backups
- Secure file uploads
- User authentication and authorization

**4. Infrastructure Security:**
- Regular security updates
- Security monitoring
- Access logging
- Incident response procedures

### Authentication & Authorization

**User Management:**
- Django's built-in user system
- Role-based access control
- Session management
- Password policies

**API Security:**
- Token-based authentication
- Rate limiting
- CORS configuration
- API versioning

## 📊 Performance Architecture

### Caching Strategy
```
Browser Cache
    │
    ▼
CDN Cache (Static Files)
    │
    ▼
Nginx Cache (Reverse Proxy)
    │
    ▼
Redis Cache (Database Queries)
    │
    ▼
PostgreSQL (Primary Data)
```

### Performance Optimizations

**Frontend Optimizations:**
- Code splitting and lazy loading
- Static asset optimization
- Bundle size analysis
- Service worker caching

**Backend Optimizations:**
- Database query optimization
- Redis caching for frequent queries
- Static file serving via CDN
- Background task processing

**Database Optimizations:**
- Proper indexing strategy
- Connection pooling
- Read replicas for scaling
- Regular maintenance tasks

## 📈 Monitoring & Observability

### Monitoring Stack

**System Monitoring:**
- Server resource utilization
- Network performance
- Disk space and I/O
- Process monitoring

**Application Monitoring:**
- Response times and throughput
- Error rates and logs
- Database performance
- User activity tracking

**Business Monitoring:**
- Entity creation/modification rates
- User engagement metrics
- Feature usage analytics
- Business process completion times

### Logging Strategy
```
Application Logs:
├── Django application logs
├── Nginx access/error logs
├── PostgreSQL logs
├── System logs (syslog)
└── Security logs (auth.log)

Log Management:
├── Log rotation (logrotate)
├── Log aggregation (optional)
├── Error alerting
└── Log analysis tools
```

## 💾 Data Architecture

### Database Design

**Entity Relationships:**
- Suppliers ↔ Supplier Locations (1:N)
- Suppliers ↔ Plants (N:M via Supplier Plant Mappings)
- Customers ↔ Purchase Orders (1:N)
- Purchase Orders ↔ File Attachments (1:N)
- All entities ↔ Contact Info (1:N)

**Data Integrity:**
- Foreign key constraints
- Validation at model level
- Business logic enforcement
- Audit trail maintenance

### Backup Strategy

**Database Backups:**
- Automated daily backups
- Point-in-time recovery capability
- Backup encryption
- Off-site backup storage

**Application Backups:**
- Full system snapshots
- Configuration backups
- Uploaded file backups
- Documentation backups

## 🚀 Deployment Strategy

### Deployment Pipeline

**Development → Staging → Production:**
1. Code development and testing
2. Automated testing (76 backend tests)
3. Staging environment validation
4. Production deployment
5. Post-deployment verification

**Deployment Methods:**
- **Blue-Green Deployment**: Zero-downtime deployments
- **Rolling Updates**: Gradual service updates
- **Feature Flags**: Controlled feature rollouts
- **Rollback Procedures**: Quick reversion capabilities

### CI/CD Integration

**Continuous Integration:**
- Automated testing on code commits
- Code quality checks
- Security scanning
- Build artifact creation

**Continuous Deployment:**
- Automated deployment to staging
- Manual approval for production
- Deployment verification
- Monitoring and alerting

## 📋 Operational Procedures

### Regular Maintenance

**Daily Tasks:**
- Monitor system health
- Review error logs
- Check backup completion
- Verify SSL certificate status

**Weekly Tasks:**
- Security update installation
- Performance review
- Capacity planning
- User access review

**Monthly Tasks:**
- Full system backup verification
- Security audit
- Performance optimization
- Documentation updates

### Disaster Recovery

**Recovery Time Objectives (RTO):**
- Critical systems: 1 hour
- Non-critical systems: 4 hours
- Full system restore: 24 hours

**Recovery Point Objectives (RPO):**
- Database: 1 hour (automated backups)
- Files: 24 hours (daily backups)
- Configuration: 24 hours

**Recovery Procedures:**
1. Incident assessment and communication
2. System isolation and damage assessment
3. Backup restoration procedures
4. Service validation and testing
5. User communication and service restoration

## 🔧 Development Environment

### Local Development Setup

**Requirements:**
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+ (optional, SQLite for basic dev)
- Git

**Quick Setup:**
```bash
# Clone repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Backend setup
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend setup (new terminal)
cd frontend
npm install
npm start
```

### Testing Strategy

**Backend Testing:**
- Unit tests for models
- Integration tests for APIs
- Performance tests
- Security tests

**Frontend Testing:**
- Component unit tests
- Integration tests
- End-to-end tests
- Accessibility tests

## 📚 Documentation Structure

```
Documentation:
├── README.md (Project overview)
├── SETUP_OVERVIEW.md (Setup guidance)
├── PRODUCTION_DEPLOYMENT.md (This document)
├── backend/
│   ├── docs/backend_setup.md
│   ├── docs/api_reference.md
│   └── docs/migration_mapping.md
└── frontend/
    ├── docs/frontend_setup.md
    └── docs/component_library.md
```

This architecture document provides the foundation for understanding ProjectMeats' system design and implementing a robust production environment that can scale with your business needs.