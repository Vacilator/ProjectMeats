# PowerApps to Django Migration Mapping

This document provides detailed mappings between PowerApps/Dataverse entities and their Django equivalents in the ProjectMeats application.

## Overview

ProjectMeats was originally built as a PowerApps Canvas application with Dataverse as the backend. This migration preserves all business logic and data while providing a modern, scalable Django REST + React architecture.

## Migration Strategy

### Data Preservation
- **Zero Data Loss**: All PowerApps data and relationships are preserved
- **Field Mapping**: Direct 1:1 mapping where possible, with clear documentation for transformations
- **Audit Trail**: PowerApps audit fields (Created/Modified/Owner) mapped to Django User model
- **Status Management**: PowerApps statecode/statuscode pattern preserved as Django choices

### Architecture Transformation

```
PowerApps Canvas App        →    React Frontend
         ↕                            ↕
    Dataverse               →    Django REST API
         ↕                            ↕
   SQL Database             →    PostgreSQL/SQLite
```

## Entity Mappings

### 1. Accounts Receivables (✅ Completed)

**PowerApps Entity**: `cr7c4_accountsreceivables`  
**Django Model**: `AccountsReceivable`  
**Django App**: `apps.accounts_receivables`

#### Field Mappings

| PowerApps Field | Type | Django Field | Type | Notes |
|----------------|------|--------------|------|--------|
| `cr7c4_accountsreceivablesid` | Primary Key | `id` | AutoField | Django auto-generated |
| `cr7c4_names` | Text (850) | `name` | CharField(850) | Primary field, required |
| `cr7c4_email` | Email (100) | `email` | EmailField(100) | Optional, validated |
| `cr7c4_phone` | Text (100) | `phone` | CharField(100) | Optional phone format |
| `cr7c4_terms` | Text (100) | `terms` | CharField(100) | Payment terms |
| `statecode` | State | `status` | TextChoices | Active/Inactive |
| `statuscode` | Status | `status` | TextChoices | Combined with statecode |
| `createdon` | DateTime | `created_on` | DateTimeField | Auto timestamp |
| `modifiedon` | DateTime | `modified_on` | DateTimeField | Auto update |
| `createdby` | Lookup | `created_by` | ForeignKey(User) | User reference |
| `modifiedby` | Lookup | `modified_by` | ForeignKey(User) | User reference |
| `ownerid` | Owner | `owner` | ForeignKey(User) | User reference |

#### API Endpoints
- `GET /api/v1/accounts-receivables/` - List with pagination/filtering
- `POST /api/v1/accounts-receivables/` - Create new record
- `GET /api/v1/accounts-receivables/{id}/` - Get specific record
- `PUT /api/v1/accounts-receivables/{id}/` - Update record
- `DELETE /api/v1/accounts-receivables/{id}/` - Soft delete (inactive)
- `GET /api/v1/accounts-receivables/migration_info/` - PowerApps migration data

### 2. Suppliers (✅ Completed)

**PowerApps Entity**: `cr7c4_supplier`  
**Django Model**: `Supplier`  
**Django App**: `apps.suppliers`

#### Field Mappings

| PowerApps Field | Type | Django Field | Type | Notes |
|----------------|------|--------------|------|--------|
| `cr7c4_supplierid` | Primary Key | `id` | AutoField | Django auto-generated |
| `cr7c4_nameofsupplier` | Text (850) | `name` | CharField(850) | Primary field, required |
| `cr7c4_datewhencreditapplicationwassent` | DateTime | `credit_application_date` | DateTimeField | Optional, tracks credit app |
| `cr7c4_profileofsupplierdeliverytype` | Boolean | `delivery_type_profile` | BooleanField | Delivery type tracking |
| `cr7c4_accountsreceivablesid` | Lookup | `accounts_receivable` | ForeignKey(AccountsReceivable) | Optional relationship |
| `statecode` | State | `status` | TextChoices | Active/Inactive |
| `statuscode` | Status | `status` | TextChoices | Combined with statecode |
| `createdon` | DateTime | `created_on` | DateTimeField | Auto timestamp |
| `modifiedon` | DateTime | `modified_on` | DateTimeField | Auto update |
| `createdby` | Lookup | `created_by` | ForeignKey(User) | User reference |
| `modifiedby` | Lookup | `modified_by` | ForeignKey(User) | User reference |
| `ownerid` | Owner | `owner` | ForeignKey(User) | User reference |

#### API Endpoints
- `GET /api/v1/suppliers/` - List with pagination/filtering
- `POST /api/v1/suppliers/` - Create new record
- `GET /api/v1/suppliers/{id}/` - Get specific record
- `PUT /api/v1/suppliers/{id}/` - Update record
- `DELETE /api/v1/suppliers/{id}/` - Soft delete (inactive)
- `GET /api/v1/suppliers/migration_info/` - PowerApps migration data

### 3. Customers (✅ Completed)

**PowerApps Entity**: `pro_customer`  
**Django Model**: `Customer`  
**Django App**: `apps.customers`

#### Field Mappings

| PowerApps Field | Type | Django Field | Type | Notes |
|----------------|------|--------------|------|--------|
| `pro_customerid` | Primary Key | `id` | AutoField | Django auto-generated |
| `pro_customername` | Text (850) | `name` | CharField(850) | Primary field, required |
| `statecode` | State | `status` | TextChoices | Active/Inactive |
| `statuscode` | Status | `status` | TextChoices | Combined with statecode |
| `createdon` | DateTime | `created_on` | DateTimeField | Auto timestamp |
| `modifiedon` | DateTime | `modified_on` | DateTimeField | Auto update |
| `createdby` | Lookup | `created_by` | ForeignKey(User) | User reference |
| `modifiedby` | Lookup | `modified_by` | ForeignKey(User) | User reference |
| `ownerid` | Owner | `owner` | ForeignKey(User) | User reference |

#### API Endpoints
- `GET /api/v1/customers/` - List with pagination/filtering
- `POST /api/v1/customers/` - Create new record
- `GET /api/v1/customers/{id}/` - Get specific record
- `PUT /api/v1/customers/{id}/` - Update record
- `DELETE /api/v1/customers/{id}/` - Soft delete (inactive)
- `GET /api/v1/customers/migration_info/` - PowerApps migration data

### 4. Contact Info (✅ Completed)

**PowerApps Entity**: `pro_contactinfo`  
**Django Model**: `ContactInfo`  
**Django App**: `apps.contacts`

#### Field Mappings

| PowerApps Field | Type | Django Field | Type | Notes |
|----------------|------|--------------|------|--------|
| `pro_contactinfoid` | Primary Key | `id` | AutoField | Django auto-generated |
| `pro_name` | Text (850) | `name` | CharField(850) | Primary field, required |
| `pro_email` | Email (100) | `email` | EmailField(100) | Optional, validated |
| `pro_phone` | Text (100) | `phone` | CharField(100) | Optional phone format |
| `pro_position` | Text (200) | `position` | CharField(200) | Job position/title |
| `pro_contacttype` | Text (100) | `contact_type` | CharField(100) | Contact category |
| `pro_customer_lookup` | Lookup | `customer` | ForeignKey(Customer) | Optional relationship |
| `pro_cr7c4_supplier` | Lookup | `supplier` | ForeignKey(Supplier) | Optional relationship |
| `statecode` | State | `status` | TextChoices | Active/Inactive |
| `statuscode` | Status | `status` | TextChoices | Combined with statecode |
| `createdon` | DateTime | `created_on` | DateTimeField | Auto timestamp |
| `modifiedon` | DateTime | `modified_on` | DateTimeField | Auto update |
| `createdby` | Lookup | `created_by` | ForeignKey(User) | User reference |
| `modifiedby` | Lookup | `modified_by` | ForeignKey(User) | User reference |
| `ownerid` | Owner | `owner` | ForeignKey(User) | User reference |

#### API Endpoints
- `GET /api/v1/contacts/` - List with pagination/filtering
- `POST /api/v1/contacts/` - Create new record
- `GET /api/v1/contacts/{id}/` - Get specific record
- `PUT /api/v1/contacts/{id}/` - Update record
- `DELETE /api/v1/contacts/{id}/` - Soft delete (inactive)
- `GET /api/v1/contacts/migration_info/` - PowerApps migration data

### 5. Purchase Orders (🔄 Planned)

**PowerApps Entity**: `pro_purchaseorder`  
**Django Model**: `PurchaseOrder` (planned)  
**Django App**: `apps.purchase_orders` (planned)

### 6. Plants (🔄 Planned)

**PowerApps Entity**: `cr7c4_plant`  
**Django Model**: `Plant` (planned)  
**Django App**: `apps.plants` (planned)

### 7. Carrier Info (🔄 Planned)

**PowerApps Entity**: `cr7c4_carrierinfo`  
**Django Model**: `CarrierInfo` (planned)  
**Django App**: `apps.carriers` (planned)

### 8. Supplier Locations (🔄 Planned)

**PowerApps Entity**: `pro_supplier_locations`  
**Django Model**: `SupplierLocation` (planned)  
**Django App**: `apps.suppliers` (planned)

### 9. Supplier Plant Mapping (🔄 Planned)

**PowerApps Entity**: `pro_supplierplantmapping`  
**Django Model**: `SupplierPlantMapping` (planned)  
**Django App**: `apps.suppliers` (planned)

## Relationship Mappings

### PowerApps Lookup Fields
PowerApps uses lookup fields for relationships. Django uses ForeignKey relationships.

#### Pattern:
```
PowerApps: Entity1[LookupField] → Entity2
Django:   Model1.foreign_key → Model2
```

### Many-to-Many Relationships
PowerApps intersection tables become Django ManyToManyField relationships.

#### Example:
```
PowerApps: pro_ContactInfo_pro_PurchaseOrder (intersection table)
Django:   ContactInfo.purchase_orders = ManyToManyField(PurchaseOrder)
```

## Data Type Mappings

### Standard Mappings

| PowerApps Type | Django Type | Notes |
|---------------|-------------|--------|
| `Text` | `CharField` | max_length from PowerApps |
| `Email` | `EmailField` | Built-in validation |
| `Phone` | `CharField` | Format validation optional |
| `Number` | `IntegerField` | Or `DecimalField` for currency |
| `Decimal` | `DecimalField` | Preserve precision |
| `DateTime` | `DateTimeField` | UTC timezone aware |
| `Date` | `DateField` | Date only |
| `Choice` | `TextChoices` | Enum-like choices |
| `Boolean` | `BooleanField` | True/False |
| `Lookup` | `ForeignKey` | Reference to related model |
| `Owner` | `ForeignKey(User)` | Django User model |

### Special Cases

#### Status Fields
PowerApps uses separate `statecode` and `statuscode` fields:
```
PowerApps: statecode=0, statuscode=1 (Active)
Django:   status='active'
```

#### Audit Fields
PowerApps audit fields map to Django patterns:
```
PowerApps: CreatedOn, CreatedBy, ModifiedOn, ModifiedBy, OwnerId
Django:   created_on, created_by, modified_on, modified_by, owner
```

## Migration Validation

### Data Integrity Checks

1. **Record Count Verification**
   ```python
   # Django management command
   python manage.py verify_migration --entity=accounts_receivables
   ```

2. **Field Value Validation**
   ```python
   # Check for data consistency
   AccountsReceivable.objects.filter(name__isnull=True).count()  # Should be 0
   ```

3. **Relationship Integrity**
   ```python
   # Verify all lookups resolved
   AccountsReceivable.objects.filter(owner__isnull=True).count()  # Should be 0
   ```

### API Verification Endpoints

Each migrated entity includes a `/migration_info/` endpoint:

```json
GET /api/v1/accounts-receivables/migration_info/
{
  "powerapps_entity_name": "cr7c4_accountsreceivables",
  "django_model_name": "AccountsReceivable",
  "total_records": 150,
  "active_records": 142,
  "field_mappings": {
    "cr7c4_names": "name",
    "cr7c4_email": "email"
  }
}
```

## Migration Process

### Step-by-Step Entity Migration

1. **Analyze PowerApps XML Export**
   ```bash
   # Extract entity definition
   grep -A 100 "Entity Name=\"entity_name\"" powerapps_export/customizations.xml
   ```

2. **Create Django App**
   ```bash
   python manage.py startapp entity_name apps/entity_name
   ```

3. **Define Django Model**
   ```python
   # Use base classes for consistent patterns
   class EntityModel(OwnedModel, StatusModel):
       name = models.CharField(max_length=XXX)  # From PowerApps MaxLength
       # ... other fields
   ```

4. **Create Migrations**
   ```bash
   python manage.py makemigrations entity_name
   python manage.py migrate
   ```

5. **Data Migration Script**
   ```python
   # Custom management command to import PowerApps data
   python manage.py import_powerapps_data --entity=entity_name --file=export.xml
   ```

6. **Create API Endpoints**
   ```python
   # Serializers, ViewSets, URLs
   # Include migration_info endpoint
   ```

7. **Build React Components**
   ```typescript
   // Screen component for entity management
   // Service classes for API communication
   ```

8. **Validation and Testing**
   ```bash
   # Verify data integrity
   python manage.py test apps.entity_name
   npm test -- EntityScreen.test.tsx
   ```

## Development Guidelines

### Model Definition Standards

```python
class EntityModel(OwnedModel, StatusModel):
    """
    Entity description migrated from PowerApps entity_name.
    
    PowerApps Entity Name: powerapps_entity_name
    Original description: "From PowerApps export"
    """
    
    # Primary field (equivalent to PowerApps primary name field)
    name = models.CharField(
        max_length=XXX,  # From PowerApps specification
        help_text="Equivalent to PowerApps primary_field_name"
    )
    
    # Other fields with PowerApps documentation
    field_name = models.FieldType(
        max_length=XXX,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps powerapps_field_name"
    )
    
    class Meta:
        verbose_name = "Entity Name"
        verbose_name_plural = "Entity Names"
        db_table = "entity_table_name"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_powerapps_entity_name(cls):
        return "powerapps_entity_name"
```

### API Endpoint Standards

```python
@extend_schema_view(
    list=extend_schema(
        summary="List Entities",
        description="Retrieve entities migrated from PowerApps entity_name.",
        tags=["Entity Management"]
    )
)
class EntityViewSet(viewsets.ModelViewSet):
    """ViewSet for Entity management."""
    
    @action(detail=False, methods=['get'])
    def migration_info(self, request):
        """PowerApps migration information endpoint."""
        return Response({
            "powerapps_entity_name": "powerapps_entity_name",
            "django_model_name": "EntityModel",
            # ... migration details
        })
```

### React Component Standards

```typescript
// types/entities.ts
export interface Entity extends OwnedEntity, StatusEntity {
  id: number;
  name: string;
  // ... other fields matching Django serializer
}

// services/api.ts
export class EntityService {
  static async getMigrationInfo(): Promise<MigrationInfo> {
    const response = await apiClient.get('/entities/migration_info/');
    return response.data;
  }
}

// screens/EntityScreen.tsx
const EntityScreen: React.FC = () => {
  // Include migration info display
  const [migrationInfo, setMigrationInfo] = useState<MigrationInfo | null>(null);
  
  useEffect(() => {
    EntityService.getMigrationInfo().then(setMigrationInfo);
  }, []);
  
  // ... component implementation
};
```

## Future Considerations

### Scalability
- **Database Optimization**: Add indexes based on PowerApps query patterns
- **API Performance**: Implement caching for frequently accessed data
- **Frontend Performance**: Lazy loading and virtualization for large datasets

### Security
- **Authentication**: Migrate PowerApps user management to Django auth
- **Authorization**: Implement role-based permissions matching PowerApps security
- **API Security**: Rate limiting and input validation

### Maintenance
- **Documentation**: Keep PowerApps mappings updated as schema evolves
- **Testing**: Comprehensive test coverage for all migrated entities
- **Monitoring**: Track API usage and performance metrics

## Migration Timeline

### Phase 1: Core Entities (✅ COMPLETED)
- ✅ Accounts Receivables (`cr7c4_accountsreceivables`) - Full Django + React implementation
- ✅ Suppliers (`cr7c4_supplier`) - Full Django + React implementation
- ✅ Customers (`pro_customer`) - Full Django + React implementation

### Phase 2: Contact Management (✅ COMPLETED)
- ✅ Contact Info (`pro_contactinfo`) - Full Django + React implementation with relationships

### Phase 3: Transaction Data (🔄 Planned)
- 🔄 Purchase Orders (`pro_purchaseorder`)
- 🔄 Supplier Plant Mapping (`pro_supplierplantmapping`)

### Phase 4: Reference Data (🔄 Planned)
- 🔄 Plants (`cr7c4_plant`)
- 🔄 Carrier Info (`cr7c4_carrierinfo`)
- 🔄 Supplier Locations (`pro_supplier_locations`)

### Phase 5: Advanced Features (🔄 Planned)
- 🔄 Document management
- 🔄 Workflows and approvals
- 🔄 Reporting and analytics

## Current Migration Status

### ✅ Completed (4/9 entities)
1. **Accounts Receivables** - Complete backend + frontend
2. **Suppliers** - Complete backend + frontend  
3. **Customers** - Complete backend + frontend
4. **Contact Info** - Complete backend + frontend

### 📊 Implementation Statistics
- **Backend**: 4 Django apps with 27 passing tests
- **Frontend**: 4 React screens with API integration
- **API Endpoints**: 20+ REST endpoints with OpenAPI documentation
- **Database**: All migrations applied, relationships established
- **Admin Interface**: Full Django admin with PowerApps field documentation

---

This document is living documentation that will be updated as the migration progresses. Each completed entity will have its mappings fully documented with examples and validation results.