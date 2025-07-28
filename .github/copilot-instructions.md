# GitHub Copilot Instructions for ProjectMeats

## Project Overview
ProjectMeats is a comprehensive business management application migrated from PowerApps/Dataverse to Django REST Framework (backend) and React TypeScript (frontend). The system manages suppliers, customers, purchase orders, accounts receivables, and related business entities.

## Architecture
- **Backend**: Django 4.2.7 + Django REST Framework 3.14.0
- **Frontend**: React 18.2.0 + TypeScript 4.9.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **API Documentation**: DRF Spectacular (OpenAPI/Swagger)

## Key Coding Patterns

### Django Backend Patterns
1. **Model Structure**: All models inherit from `OwnedModel` and `StatusModel` base classes in `apps.core.models`
2. **PowerApps Migration**: Include PowerApps field mappings in model docstrings
3. **API Structure**: Use DRF ViewSets with filtering, pagination, and proper serializers
4. **File Organization**: Each app follows Django conventions: `models.py`, `serializers.py`, `views.py`, `urls.py`, `tests.py`

### React Frontend Patterns
1. **TypeScript**: All components use TypeScript with proper type definitions
2. **Functional Components**: Use React hooks, avoid class components
3. **Styled Components**: Use styled-components for styling
4. **API Services**: Centralized API calls in `src/services/`
5. **Component Structure**: Reusable components in `src/components/`, screen components in `src/screens/`

### Code Style Guidelines
- **Python**: Black formatting, flake8 linting, isort imports
- **TypeScript**: ESLint with React rules, Prettier formatting
- **Documentation**: Inline comments for PowerApps migrations, comprehensive docstrings
- **Testing**: pytest for backend, Jest/React Testing Library for frontend

## Entity Migration Patterns

When migrating PowerApps entities, follow this pattern:

### Django Model Template
```python
"""
Entity description from PowerApps.

Migrated from PowerApps entity: {powerapps_entity_name}
Original description: "{original_description}"

PowerApps Entity Name: {PowerAppsEntityName}
Django Model Name: {DjangoModelName}
"""
from django.db import models
from apps.core.models import OwnedModel, StatusModel

class EntityName(OwnedModel, StatusModel):
    """
    Entity description.

    PowerApps Field Mappings:
    - powerapps_field -> django_field (Description)
    + Standard PowerApps audit fields via OwnedModel base class
    """
    
    # Fields with PowerApps mappings in help_text
    field_name = models.CharField(
        max_length=100,
        help_text="Equivalent to PowerApps {field_name} field",
    )
```

### React Component Template
```tsx
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { EntityType } from '../types';
import { entityService } from '../services/api';

const EntityScreen: React.FC = () => {
  const [entities, setEntities] = useState<EntityType[]>([]);
  const [loading, setLoading] = useState(true);

  // Component logic here
  
  return (
    <Container>
      {/* Component JSX */}
    </Container>
  );
};

const Container = styled.div`
  /* Styled components styling */
`;

export default EntityScreen;
```

## API Patterns

### DRF Serializer Pattern
```python
from rest_framework import serializers
from .models import ModelName

class ModelNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelName
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
```

### DRF ViewSet Pattern
```python
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ModelName
from .serializers import ModelNameSerializer

class ModelNameViewSet(viewsets.ModelViewSet):
    queryset = ModelName.objects.all()
    serializer_class = ModelNameSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['field1', 'field2']
    search_fields = ['name', 'email']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
```

## Common Commands
- **Setup**: `python setup.py` (cross-platform setup)
- **Development**: `make dev` (starts both backend and frontend)
- **Testing**: `make test` (runs all tests)
- **Backend Tests**: `cd backend && python manage.py test`
- **Frontend Tests**: `cd frontend && npm test`
- **Linting**: `cd backend && black . && flake8 .` or `cd frontend && npm run lint`

## File Locations
- **Backend**: `/backend/` - Django application
- **Frontend**: `/frontend/` - React TypeScript application
- **Documentation**: `/docs/` - Project documentation
- **PowerApps Export**: `/powerapps_export/` - Original PowerApps solution reference

## Migration Status
Check `docs/migration_mapping.md` for current entity migration status and `docs/agent_activity_log.md` for recent development activity.

## Important Notes
1. Always include PowerApps field mappings in model docstrings
2. Follow existing patterns from `accounts_receivables` app
3. Use base models (`OwnedModel`, `StatusModel`) for consistency
4. Maintain comprehensive test coverage
5. Update documentation when adding new entities
6. Log significant changes in `docs/agent_activity_log.md`

## Security Considerations
- Use Django's built-in security features
- Validate all user inputs
- Use proper authentication and permissions
- Follow OWASP security guidelines
- Environment variables for sensitive configuration

## Performance Guidelines
- Use `select_related()` and `prefetch_related()` for database queries
- Implement proper database indexes
- Use pagination for large datasets
- Optimize API responses with appropriate serializer fields
- Use caching where appropriate