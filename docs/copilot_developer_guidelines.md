# Developer Guidelines for GitHub Copilot in ProjectMeats

## 🎯 Purpose
This document provides specific guidelines for developers using GitHub Copilot on the ProjectMeats migration project. Following these guidelines ensures consistent, secure, and high-quality code generation.

## 🚨 Security Guidelines

### 1. Sensitive Data Protection
```bash
# ✅ GOOD: Use environment variables
SECRET_KEY = os.getenv('SECRET_KEY')

# ❌ BAD: Never include secrets in code
SECRET_KEY = 'hardcoded-secret-key-123'
```

### 2. Authentication and Authorization
```python
# ✅ GOOD: Always include permission checks
class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
# ❌ BAD: Open endpoints without authentication
class SupplierViewSet(viewsets.ModelViewSet):
    # No permission classes
```

### 3. Input Validation
```python
# ✅ GOOD: Validate all inputs
def create_supplier(self, validated_data):
    # Django serializer automatically validates
    return Supplier.objects.create(**validated_data)

# ❌ BAD: Direct database operations without validation
def create_supplier(self, request_data):
    return Supplier.objects.create(**request_data)  # No validation
```

## 🏗️ Code Architecture Guidelines

### 1. Django Backend Patterns

#### Model Inheritance
```python
# ✅ GOOD: Use base models for consistency
class Supplier(OwnedModel, StatusModel):
    """Supplier entity migrated from PowerApps cr7c4_supplier."""
    name = models.CharField(max_length=100)

# ❌ BAD: Recreating common fields
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)  # Duplicate pattern
    updated_at = models.DateTimeField(auto_now=True)      # Duplicate pattern
```

#### PowerApps Documentation
```python
# ✅ GOOD: Include PowerApps field mappings
class Supplier(OwnedModel, StatusModel):
    """
    Supplier entity migrated from PowerApps cr7c4_supplier.
    
    PowerApps Field Mappings:
    - cr7c4_suppliername -> name
    - cr7c4_email -> email
    - cr7c4_phone -> phone
    """
    name = models.CharField(
        max_length=100,
        help_text="Equivalent to PowerApps cr7c4_suppliername field"
    )

# ❌ BAD: No PowerApps documentation
class Supplier(OwnedModel, StatusModel):
    name = models.CharField(max_length=100)  # No context
```

#### API ViewSets
```python
# ✅ GOOD: Complete ViewSet with filtering and permissions
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'created_by']
    search_fields = ['name', 'email']
    ordering = ['-created_at']

# ❌ BAD: Minimal ViewSet without proper configuration
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
```

### 2. React Frontend Patterns

#### Component Structure
```tsx
// ✅ GOOD: Proper TypeScript component with hooks
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Supplier } from '../types';
import { supplierService } from '../services/api';

interface SupplierScreenProps {
  onSupplierSelect?: (supplier: Supplier) => void;
}

const SupplierScreen: React.FC<SupplierScreenProps> = ({ onSupplierSelect }) => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const fetchSuppliers = async () => {
    try {
      setLoading(true);
      const data = await supplierService.getAll();
      setSuppliers(data);
    } catch (err) {
      setError('Failed to fetch suppliers');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      {/* Component JSX */}
    </Container>
  );
};

// ❌ BAD: No TypeScript, no error handling
const SupplierScreen = () => {
  const [suppliers, setSuppliers] = useState([]);
  
  useEffect(() => {
    fetch('/api/suppliers').then(res => res.json()).then(setSuppliers);
  }, []);

  return <div>{/* Component JSX */}</div>;
};
```

#### API Services
```typescript
// ✅ GOOD: Centralized API service with error handling
import axios from 'axios';
import { Supplier } from '../types';

class SupplierService {
  private baseURL = '/api/v1/suppliers/';

  async getAll(): Promise<Supplier[]> {
    try {
      const response = await axios.get<Supplier[]>(this.baseURL);
      return response.data;
    } catch (error) {
      console.error('Error fetching suppliers:', error);
      throw new Error('Failed to fetch suppliers');
    }
  }

  async create(supplier: Omit<Supplier, 'id'>): Promise<Supplier> {
    try {
      const response = await axios.post<Supplier>(this.baseURL, supplier);
      return response.data;
    } catch (error) {
      console.error('Error creating supplier:', error);
      throw new Error('Failed to create supplier');
    }
  }
}

export const supplierService = new SupplierService();

// ❌ BAD: Direct fetch calls without error handling
export const getSuppliers = () => {
  return fetch('/api/suppliers').then(res => res.json());
};
```

## 📝 Copilot Prompt Guidelines

### 1. Effective Prompts

#### Django Model Generation
```
# ✅ GOOD: Specific with context
Create a Django model for Customer entity migrated from PowerApps pro_customer. 
Include PowerApps field mappings in docstring and help_text. 
Use OwnedModel and StatusModel base classes. 
Fields: name (cr7c4_customername), email (cr7c4_email), phone (cr7c4_phone), 
address (cr7c4_address), status (cr7c4_status).

# ❌ BAD: Too vague
Create a customer model
```

#### React Component Generation
```
# ✅ GOOD: Detailed requirements
Create a React TypeScript component called CustomerScreen for managing customers. 
Include CRUD operations, search functionality, and error handling. 
Use styled-components for styling. Follow the pattern from AccountsReceivablesScreen. 
Include proper TypeScript interfaces and API service integration.

# ❌ BAD: Minimal context
Create a customer component
```

#### API Test Generation
```
# ✅ GOOD: Comprehensive test requirements
Create pytest tests for CustomerViewSet API endpoints following ProjectMeats patterns. 
Include tests for: CRUD operations, filtering, search, permissions, validation errors. 
Use factory_boy for test data. Follow the pattern from accounts_receivables tests.

# ❌ BAD: Basic request
Write tests for customer API
```

### 2. Context-Providing Prompts

#### Migration Context
```
# Always mention PowerApps migration context
"Following the PowerApps to Django migration patterns in ProjectMeats..."
"Migrating from PowerApps entity cr7c4_customer to Django Customer model..."
"Using the same patterns as the completed accounts_receivables migration..."
```

#### Existing Pattern References
```
# Reference existing implementations
"Following the pattern from AccountsReceivable model in apps/accounts_receivables/models.py..."
"Similar to AccountsReceivablesScreen component structure..."
"Using the same API service pattern as accountsReceivableService..."
```

### 3. Code Quality Prompts

#### Request Best Practices
```
# Always include quality requirements
"Include proper error handling and TypeScript types"
"Add comprehensive docstrings and comments"
"Include input validation and security considerations"
"Follow Django/React best practices"
"Add unit tests following existing patterns"
```

## 🧪 Testing Guidelines

### 1. Backend Testing
```python
# ✅ GOOD: Comprehensive test class
class SupplierViewSetTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.supplier = SupplierFactory()

    def test_list_suppliers(self):
        """Test retrieving list of suppliers."""
        response = self.client.get('/api/v1/suppliers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_supplier_valid_data(self):
        """Test creating supplier with valid data."""
        data = {'name': 'Test Supplier', 'email': 'test@example.com'}
        response = self.client.post('/api/v1/suppliers/', data)
        self.assertEqual(response.status_code, 201)

    def test_create_supplier_invalid_email(self):
        """Test creating supplier with invalid email."""
        data = {'name': 'Test Supplier', 'email': 'invalid-email'}
        response = self.client.post('/api/v1/suppliers/', data)
        self.assertEqual(response.status_code, 400)
```

### 2. Frontend Testing
```typescript
// ✅ GOOD: Complete component test
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SupplierScreen from './SupplierScreen';
import { supplierService } from '../services/api';

jest.mock('../services/api');

describe('SupplierScreen', () => {
  const mockSuppliers = [
    { id: 1, name: 'Test Supplier', email: 'test@example.com' }
  ];

  beforeEach(() => {
    (supplierService.getAll as jest.Mock).mockResolvedValue(mockSuppliers);
  });

  it('displays suppliers after loading', async () => {
    render(<SupplierScreen />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Supplier')).toBeInTheDocument();
    });
  });

  it('handles create supplier', async () => {
    const user = userEvent.setup();
    render(<SupplierScreen />);
    
    await user.click(screen.getByText('Add Supplier'));
    await user.type(screen.getByLabelText('Name'), 'New Supplier');
    await user.click(screen.getByText('Save'));
    
    expect(supplierService.create).toHaveBeenCalledWith({
      name: 'New Supplier'
    });
  });
});
```

## 🔄 Code Review Guidelines

### 1. Copilot-Generated Code Review
Always review Copilot-generated code for:
- **Security**: No hardcoded secrets or unsafe operations
- **Patterns**: Follows ProjectMeats architectural patterns
- **Documentation**: Includes PowerApps mappings and proper comments
- **Testing**: Has appropriate test coverage
- **Performance**: Uses efficient database queries and React patterns

### 2. Common Issues to Check

#### Django Issues
```python
# ❌ Check for: Missing select_related/prefetch_related
def get_queryset(self):
    return Supplier.objects.all()  # N+1 queries

# ✅ Should be:
def get_queryset(self):
    return Supplier.objects.select_related('created_by').all()
```

#### React Issues
```tsx
// ❌ Check for: Missing dependency arrays
useEffect(() => {
  fetchData();
}); // Missing dependency array

// ✅ Should be:
useEffect(() => {
  fetchData();
}, []); // Empty dependency array for mount-only
```

## 📊 Metrics and Quality

### 1. Code Quality Metrics
- **Test Coverage**: Maintain >90% for new code
- **Linting**: Zero flake8/ESLint errors
- **Type Coverage**: 100% TypeScript coverage
- **Documentation**: All models and components documented

### 2. Performance Metrics
- **API Response Time**: <200ms for CRUD operations
- **Frontend Bundle Size**: <500KB for main chunks
- **Database Queries**: <5 queries per API endpoint
- **Page Load Time**: <2 seconds for all screens

## 📚 Resources

### Internal Documentation
- [Copilot Usage Guide](copilot_usage_guide.md)
- [Migration Mapping](migration_mapping.md)
- [API Reference](api_reference.md)

### External Resources
- [Django Best Practices](https://django-best-practices.readthedocs.io/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot/using-github-copilot/best-practices-for-using-github-copilot)

---

**Remember**: Copilot is a powerful tool, but human review and judgment are essential for maintaining code quality, security, and architectural consistency.