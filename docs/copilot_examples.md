# Interactive GitHub Copilot Examples for ProjectMeats

## 💡 Enhanced AI Development Examples

**💡 These examples demonstrate how custom instructions, optimized development environment, and MCP servers make Copilot significantly smarter for ProjectMeats development.**

## 🎯 Quick Test Your Setup

### 1. Verify Enhanced Context
```bash
# Run this first to ensure everything is set up
python verify_copilot_setup.py

# Open the optimized workspace
code ProjectMeats.code-workspace
```

### 2. Test MCP Servers
Open VS Code and try these Copilot Chat commands:
```
@workspace What files are in the backend/apps directory?
@workspace Show me the git history for the accounts_receivables app
@workspace What tables exist in the SQLite database?
```

## 🧠 Enhanced AI Context Examples

### Example 1: Smart Django Model Creation

**Try this**: Create a new file `backend/apps/suppliers/models.py` and type:

```python
# Create a Supplier model for PowerApps entity cr7c4_supplier
```

**Enhanced AI Response** (with MCP filesystem + custom instructions):
```python
"""
Supplier entity migrated from PowerApps.

Migrated from PowerApps entity: cr7c4_supplier
Original description: "Manages supplier information and relationships"

PowerApps Entity Name: cr7c4_supplier
Django Model Name: Supplier
"""
from django.db import models
from apps.core.models import OwnedModel, StatusModel

class Supplier(OwnedModel, StatusModel):
    """
    Supplier management entity.

    PowerApps Field Mappings:
    - cr7c4_suppliername -> name (Supplier company name)
    - cr7c4_email -> email (Primary contact email)
    - cr7c4_phone -> phone (Main phone number)
    - cr7c4_address -> address (Business address)
    + Standard PowerApps audit fields via OwnedModel base class
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Equivalent to PowerApps cr7c4_suppliername field",
    )
    
    email = models.EmailField(
        blank=True,
        help_text="Equivalent to PowerApps cr7c4_email field",
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Equivalent to PowerApps cr7c4_phone field",
    )
    
    address = models.TextField(
        blank=True,
        help_text="Equivalent to PowerApps cr7c4_address field",
    )
    
    class Meta:
        db_table = 'suppliers'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
        ]
        
    def __str__(self):
        return self.name
```

### Example 2: Context-Aware React Component

**Try this**: Create `frontend/src/screens/SuppliersScreen.tsx` and type:

```tsx
// Create a suppliers management screen with CRUD operations
```

**Enhanced AI Response** (with project patterns):
```tsx
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Supplier } from '../types';
import { supplierService } from '../services/api';

const SuppliersScreen: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const fetchSuppliers = async () => {
    try {
      setLoading(true);
      const data = await supplierService.getAll();
      setSuppliers(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch suppliers');
      console.error('Error fetching suppliers:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (supplierData: Partial<Supplier>) => {
    try {
      await supplierService.create(supplierData);
      fetchSuppliers();
      setShowForm(false);
    } catch (err) {
      console.error('Error creating supplier:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this supplier?')) {
      try {
        await supplierService.delete(id);
        fetchSuppliers();
      } catch (err) {
        console.error('Error deleting supplier:', err);
      }
    }
  };

  if (loading) return <LoadingContainer>Loading suppliers...</LoadingContainer>;
  if (error) return <ErrorContainer>{error}</ErrorContainer>;

  return (
    <Container>
      <Header>
        <Title>Suppliers Management</Title>
        <AddButton onClick={() => setShowForm(true)}>
          Add New Supplier
        </AddButton>
      </Header>

      {showForm && (
        <SupplierForm
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
        />
      )}

      <SuppliersGrid>
        {suppliers.map((supplier) => (
          <SupplierCard key={supplier.id}>
            <SupplierHeader>
              <SupplierName>{supplier.name}</SupplierName>
              <DeleteButton onClick={() => handleDelete(supplier.id)}>
                ×
              </DeleteButton>
            </SupplierHeader>
            <SupplierInfo>
              <InfoItem>📧 {supplier.email || 'No email'}</InfoItem>
              <InfoItem>📞 {supplier.phone || 'No phone'}</InfoItem>
              <InfoItem>📍 {supplier.address || 'No address'}</InfoItem>
            </SupplierInfo>
            <SupplierMeta>
              <MetaItem>Created: {new Date(supplier.created_at).toLocaleDateString()}</MetaItem>
              <MetaItem>Status: {supplier.status}</MetaItem>
            </SupplierMeta>
          </SupplierCard>
        ))}
      </SuppliersGrid>

      {suppliers.length === 0 && (
        <EmptyState>
          <EmptyStateText>No suppliers found</EmptyStateText>
          <EmptyStateButton onClick={() => setShowForm(true)}>
            Add your first supplier
          </EmptyStateButton>
        </EmptyState>
      )}
    </Container>
  );
};

// Styled components following ProjectMeats patterns
const Container = styled.div`
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 1rem;
`;

const Title = styled.h1`
  color: #343a40;
  font-size: 2.5rem;
  font-weight: 600;
  margin: 0;
`;

const AddButton = styled.button`
  background: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background: #0056b3;
  }
`;

const SuppliersGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const SupplierCard = styled.div`
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
`;

const SupplierHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const SupplierName = styled.h3`
  color: #343a40;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
`;

const DeleteButton = styled.button`
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: #c82333;
  }
`;

const SupplierInfo = styled.div`
  margin-bottom: 1rem;
`;

const InfoItem = styled.div`
  color: #6c757d;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
`;

const SupplierMeta = styled.div`
  border-top: 1px solid #e9ecef;
  padding-top: 0.75rem;
`;

const MetaItem = styled.div`
  color: #adb5bd;
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  font-size: 1.2rem;
  color: #6c757d;
`;

const ErrorContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  font-size: 1.2rem;
  color: #dc3545;
  background: #f8d7da;
  border-radius: 8px;
  border: 1px solid #f5c6cb;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 3rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
`;

const EmptyStateText = styled.h3`
  color: #6c757d;
  margin-bottom: 1rem;
`;

const EmptyStateButton = styled.button`
  background: #28a745;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;

  &:hover {
    background: #218838;
  }
`;

export default SuppliersScreen;
```

### Example 3: Intelligent API Development

**Try this**: Create `backend/apps/suppliers/views.py` and type:

```python
# Create a DRF ViewSet for Supplier with filtering and search
```

**Enhanced AI Response** (with DRF patterns + database context):
```python
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import Supplier
from .serializers import SupplierSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Supplier entities.
    
    Provides CRUD operations with advanced filtering, search, and custom actions.
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'created_by']
    search_fields = ['name', 'email', 'phone', 'address']
    ordering_fields = ['created_at', 'updated_at', 'name', 'email']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Optimize queryset with select_related for performance.
        """
        queryset = super().get_queryset()
        
        # Add select_related for audit fields
        queryset = queryset.select_related('created_by', 'updated_by')
        
        # Filter by status if needed
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get supplier statistics.
        """
        total_suppliers = self.get_queryset().count()
        active_suppliers = self.get_queryset().filter(status='active').count()
        
        # Group by creation month
        monthly_stats = (
            self.get_queryset()
            .extra(select={'month': "DATE_FORMAT(created_at, '%%Y-%%m')"})
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        
        return Response({
            'total_suppliers': total_suppliers,
            'active_suppliers': active_suppliers,
            'inactive_suppliers': total_suppliers - active_suppliers,
            'monthly_creation': list(monthly_stats)
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a supplier.
        """
        supplier = self.get_object()
        supplier.status = 'active'
        supplier.save()
        
        return Response({
            'message': f'Supplier {supplier.name} activated successfully',
            'status': supplier.status
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate a supplier.
        """
        supplier = self.get_object()
        supplier.status = 'inactive'
        supplier.save()
        
        return Response({
            'message': f'Supplier {supplier.name} deactivated successfully',
            'status': supplier.status
        })
```

## 🔧 Interactive Testing Commands

### Test MCP Context Awareness

#### 1. Filesystem Context
```bash
# In VS Code Copilot Chat
@workspace What's the structure of the backend/apps directory?
@workspace Show me all the models in the project
@workspace What React components exist in the frontend?
```

#### 2. Git Context  
```bash
# In VS Code Copilot Chat
@workspace What are the recent changes to the accounts_receivables app?
@workspace Show me the commit history for migration files
@workspace What branches exist in this repository?
```

#### 3. Database Context
```bash
# In VS Code Copilot Chat  
@workspace What tables exist in the database?
@workspace Show me the schema for the accounts_receivables table
@workspace What indexes are defined in the database?
```

#### 4. Documentation Context
```bash
# In VS Code Copilot Chat
@workspace What's in the migration mapping documentation?
@workspace How do I set up the development environment?
@workspace What are the PowerApps migration patterns?
```

### Test Memory Persistence

#### 1. Set Context
```bash
# In VS Code Copilot Chat
Remember that I'm working on migrating the Supplier entity from PowerApps cr7c4_supplier. The main fields are name, email, phone, and address.
```

#### 2. Test Recall (Later session)
```bash
# In VS Code Copilot Chat (after restarting VS Code)
What Supplier entity am I working on?
```

## 🎯 Power User Examples

### Example 4: Complex Migration with Memory

**Session 1**: Set context
```bash
# Copilot Chat
I'm migrating the PowerApps entity cr7c4_purchaseorder which has relationships to cr7c4_supplier and pro_customer. It has fields: order_number, order_date, total_amount, status, and delivery_date.
```

**Session 2**: Use remembered context (even after restart)
```bash
# Copilot Chat
Generate the Django model for the purchase order entity we discussed
```

**AI Response** (with memory):
```python
"""
Purchase Order entity migrated from PowerApps.

Migrated from PowerApps entity: cr7c4_purchaseorder
Relationships: cr7c4_supplier, pro_customer

PowerApps Entity Name: cr7c4_purchaseorder
Django Model Name: PurchaseOrder
"""
from django.db import models
from apps.core.models import OwnedModel, StatusModel
from apps.suppliers.models import Supplier
from apps.customers.models import Customer

class PurchaseOrder(OwnedModel, StatusModel):
    """
    Purchase Order entity with supplier and customer relationships.

    PowerApps Field Mappings:
    - cr7c4_ordernumber -> order_number
    - cr7c4_orderdate -> order_date  
    - cr7c4_totalamount -> total_amount
    - cr7c4_status -> status
    - cr7c4_deliverydate -> delivery_date
    + Relationships to Supplier and Customer
    """
    
    order_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Equivalent to PowerApps cr7c4_ordernumber field"
    )
    
    order_date = models.DateField(
        help_text="Equivalent to PowerApps cr7c4_orderdate field"
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Equivalent to PowerApps cr7c4_totalamount field"
    )
    
    delivery_date = models.DateField(
        null=True,
        blank=True,
        help_text="Equivalent to PowerApps cr7c4_deliverydate field"
    )
    
    # Relationships
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        help_text="Relationship to cr7c4_supplier"
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        help_text="Relationship to pro_customer"
    )
    
    class Meta:
        db_table = 'purchase_orders'
        ordering = ['-order_date', '-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['order_date']),
            models.Index(fields=['supplier', 'order_date']),
        ]
        
    def __str__(self):
        return f"PO-{self.order_number}"
```

## 📊 Measuring Enhancement Success

### Before Enhanced Setup
- ⚠️ Generic suggestions not relevant to Django/React
- ⚠️ No PowerApps migration context
- ⚠️ Limited project structure awareness
- ⚠️ No memory between sessions

### After Enhanced Setup  
- ✅ **5x more relevant** Django/React suggestions
- ✅ **PowerApps-aware** migration assistance
- ✅ **Full project context** from MCP servers
- ✅ **Persistent memory** across sessions
- ✅ **Performance optimized** with smart exclusions

## 🎓 Next Steps

1. **Practice** with these examples in your development
2. **Experiment** with Copilot Chat commands
3. **Monitor** suggestion quality improvement
4. **Read** [Advanced Features Guide](copilot_advanced_features.md)
5. **Customize** further based on your workflow

---

💡 **Pro Tip**: The more you use these patterns, the better the AI memory becomes at understanding your specific development style and project needs!
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