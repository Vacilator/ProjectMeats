# GitHub Copilot Setup Test Examples

This file demonstrates how the Copilot setup enhances development in ProjectMeats.

## Example 1: Django Model Creation

When you type the following comment in a Django models.py file:

```python
# Create a Supplier model migrated from PowerApps cr7c4_supplier with fields: name, email, phone, address
```

Copilot, with our custom instructions, will suggest:

```python
"""
Supplier entity migrated from PowerApps cr7c4_supplier.

PowerApps Entity Name: cr7c4_supplier
Django Model Name: Supplier
"""
from django.db import models
from apps.core.models import OwnedModel, StatusModel

class Supplier(OwnedModel, StatusModel):
    """
    Supplier entity migrated from PowerApps cr7c4_supplier.
    
    PowerApps Field Mappings:
    - cr7c4_suppliername -> name
    - cr7c4_email -> email
    - cr7c4_phone -> phone
    - cr7c4_address -> address
    + Standard PowerApps audit fields via OwnedModel base class
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Equivalent to PowerApps cr7c4_suppliername field"
    )
    
    email = models.EmailField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_email field"
    )
    
    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_phone field"
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_address field"
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'suppliers'
        ordering = ['-created_at']
```

## Example 2: React Component Creation

When you type:

```tsx
// Create a SuppliersScreen component with CRUD operations following ProjectMeats patterns
```

Copilot will suggest:

```tsx
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Supplier } from '../types';
import { supplierService } from '../services/api';

interface SuppliersScreenProps {
  onSupplierSelect?: (supplier: Supplier) => void;
}

const SuppliersScreen: React.FC<SuppliersScreenProps> = ({ onSupplierSelect }) => {
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

  const handleCreate = async (supplierData: Omit<Supplier, 'id'>) => {
    try {
      const newSupplier = await supplierService.create(supplierData);
      setSuppliers(prev => [newSupplier, ...prev]);
    } catch (err) {
      setError('Failed to create supplier');
    }
  };

  if (loading) return <LoadingContainer>Loading suppliers...</LoadingContainer>;
  if (error) return <ErrorContainer>{error}</ErrorContainer>;

  return (
    <Container>
      <Header>
        <Title>Suppliers</Title>
        <CreateButton onClick={() => handleCreate}>Add Supplier</CreateButton>
      </Header>
      
      <SupplierList>
        {suppliers.map(supplier => (
          <SupplierCard 
            key={supplier.id} 
            onClick={() => onSupplierSelect?.(supplier)}
          >
            <SupplierName>{supplier.name}</SupplierName>
            <SupplierEmail>{supplier.email}</SupplierEmail>
          </SupplierCard>
        ))}
      </SupplierList>
    </Container>
  );
};

const Container = styled.div`
  padding: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const Title = styled.h1`
  color: #333;
  margin: 0;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
`;

const ErrorContainer = styled.div`
  color: red;
  text-align: center;
  padding: 20px;
`;

export default SuppliersScreen;
```

## Key Benefits

1. **Context Awareness**: Copilot understands the PowerApps migration context
2. **Pattern Consistency**: Follows established ProjectMeats architectural patterns
3. **Security Built-in**: Includes proper error handling and validation
4. **Documentation**: Automatically includes PowerApps field mappings
5. **Type Safety**: Generates proper TypeScript interfaces and types
6. **Testing Ready**: Code structure supports easy unit testing

This setup makes Copilot significantly more effective for ProjectMeats development!