# Backend Setup Guide

This guide helps you set up the Django REST Framework backend for ProjectMeats, migrated from PowerApps/Dataverse.

## Prerequisites

- Python 3.9+
- pip (Python package manager)
- PostgreSQL 12+ (for production) or SQLite (for development)

## Quick Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your specific settings
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server:**
   ```bash
   python manage.py runserver
   ```

## Development Workflow

### Adding New Entities (PowerApps Migration)

1. **Analyze PowerApps Entity:**
   - Review XML export in `powerapps_export/`
   - Document field mappings and relationships

2. **Create Django App:**
   ```bash
   python manage.py startapp entity_name apps/entity_name
   ```

3. **Define Models:**
   - Use `OwnedModel` and `StatusModel` base classes
   - Map PowerApps fields to Django fields
   - Add comprehensive field documentation

4. **Create Migrations:**
   ```bash
   python manage.py makemigrations entity_name
   python manage.py migrate
   ```

5. **Add Serializers and Views:**
   - Create list, detail, and create serializers
   - Implement ViewSet with filtering and search
   - Add PowerApps migration information endpoint

6. **Register in Admin:**
   - Configure admin interface with PowerApps field mappings
   - Add helpful actions and filters

### API Development

#### URLs and Routing
- All APIs follow `/api/v1/` prefix
- Use REST conventions: `GET`, `POST`, `PUT`, `DELETE`
- Include filtering, searching, and pagination

#### Serializers
- **List**: Lightweight for performance
- **Detail**: Complete with relationships
- **Create**: Minimal required fields

#### ViewSets
- Extend `ModelViewSet` for full CRUD
- Add custom actions for business logic
- Include PowerApps migration info endpoints

### Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts_receivables

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Database Management

#### Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback migrations
python manage.py migrate app_name migration_name
```

#### Data Management
```bash
# Create test data
python manage.py shell
>>> from apps.accounts_receivables.models import AccountsReceivable
>>> # Create test records

# Export data
python manage.py dumpdata accounts_receivables > test_data.json

# Import data
python manage.py loaddata test_data.json
```

## Production Deployment

### Environment Configuration

1. **Update settings:**
   ```bash
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Security settings:**
   ```bash
   SECURE_SSL_REDIRECT=True
   SECURE_HSTS_SECONDS=31536000
   CORS_ALLOWED_ORIGINS=https://yourdomain.com
   ```

### Database Setup

```bash
# PostgreSQL setup
createdb projectmeats
python manage.py migrate
python manage.py collectstatic
```

### Web Server

```bash
# Using Gunicorn
pip install gunicorn
gunicorn projectmeats.wsgi:application --bind 0.0.0.0:8000

# Using Docker
# See Dockerfile in project root
```

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## PowerApps Migration Notes

### Field Mapping Patterns

| PowerApps | Django | Notes |
|-----------|--------|-------|
| Primary field (e.g., cr7c4_names) | name | Required, max_length from PowerApps |
| Email fields | EmailField | Validation included |
| Phone fields | CharField | Format validation optional |
| statecode/statuscode | status (TextChoices) | Active/Inactive pattern |
| CreatedOn | created_on | Auto timestamp |
| ModifiedOn | modified_on | Auto update |
| CreatedBy | created_by | ForeignKey to User |
| ModifiedBy | modified_by | ForeignKey to User |
| OwnerId | owner | ForeignKey to User |

### Best Practices

1. **Always document PowerApps origins** in model docstrings
2. **Preserve field lengths** from PowerApps specifications
3. **Map ownership fields** to Django User model
4. **Use soft deletes** (status=inactive) instead of hard deletes
5. **Include migration info endpoints** for verification

## Troubleshooting

### Common Issues

1. **Import errors with apps:**
   - Ensure `apps/` directory has `__init__.py`
   - Check `INSTALLED_APPS` settings

2. **Migration conflicts:**
   ```bash
   python manage.py migrate --fake-initial
   python manage.py migrate
   ```

3. **Database connection errors:**
   - Verify `DATABASE_URL` in `.env`
   - Check database server is running

4. **CORS issues:**
   - Update `CORS_ALLOWED_ORIGINS` in settings
   - Ensure `corsheaders` is in `MIDDLEWARE`

### Development Tools

```bash
# Django shell with models
python manage.py shell_plus

# Database shell
python manage.py dbshell

# Show SQL queries
python manage.py shell
>>> from django.db import connection
>>> connection.queries

# Generate API schema
python manage.py spectacular --file schema.yml
```

## Next Steps

1. Migrate remaining PowerApps entities (suppliers, customers, etc.)
2. Implement authentication and permissions
3. Add comprehensive test coverage
4. Set up CI/CD pipeline
5. Deploy to production environment

For more information, see the main [README.md](../README.md) and [API Reference](api_reference.md).