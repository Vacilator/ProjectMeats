# ProjectMeats API Reference

REST API documentation for the ProjectMeats backend, migrated from PowerApps/Dataverse to Django REST Framework.

## Base URL

- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://api.yourproductiondomain.com/api/v1`

## Authentication

Currently configured for development with `AllowAny` permissions. In production, implement:

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}
```

## Performance Optimizations

### Database Indexes
The API has been optimized with strategic database indexes:

- **Suppliers**: Indexed on name, status, delivery_type_profile, accounts_receivable, credit_application_date
- **Customers**: Indexed on name, status
- **Contacts**: Indexed on name, status, contact_type, customer, supplier, email
- **Purchase Orders**: Indexed on po_number, purchase_date, status, customer, supplier
- **Accounts Receivables**: Indexed on name, status, email, created_on

### Query Optimization
All ViewSets use `select_related()` to minimize database queries:

```python
# Example: Supplier queries optimized
queryset = Supplier.objects.select_related(
    'accounts_receivable', 'created_by', 'modified_by', 'owner'
).all()
```

### Pagination
All list endpoints use pagination (20 items per page by default):

```json
{
  "count": 156,
  "next": "http://localhost:8000/api/v1/suppliers/?page=3",
  "previous": "http://localhost:8000/api/v1/suppliers/?page=1",
  "results": [...]
}
```

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Accounts Receivables API

### Overview
Manages accounts receivable records migrated from PowerApps `cr7c4_accountsreceivables` entity.

### Endpoints

#### List Accounts Receivables
```http
GET /api/v1/accounts-receivables/
```

**Query Parameters:**
- `page` (integer): Page number for pagination
- `search` (string): Search in name and email fields
- `status` (string): Filter by status (`active`, `inactive`)
- `email` (string): Filter by exact email
- `phone` (string): Filter by exact phone
- `active` (boolean): Show only active records (`true`)
- `has_contact` (boolean): Show only records with contact info (`true`)

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/accounts-receivables/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "status": "active",
      "has_contact_info": true,
      "created_on": "2024-01-15T10:30:00Z",
      "modified_on": "2024-01-20T14:45:00Z"
    }
  ]
}
```

#### Get Accounts Receivable Details
```http
GET /api/v1/accounts-receivables/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "terms": "Net 30",
  "status": "active",
  "has_contact_info": true,
  "powerapps_entity_name": "cr7c4_accountsreceivables",
  "created_on": "2024-01-15T10:30:00Z",
  "modified_on": "2024-01-20T14:45:00Z",
  "created_by": 1,
  "modified_by": 1,
  "owner": 1,
  "created_by_username": "admin",
  "modified_by_username": "admin",
  "owner_username": "admin"
}
```

#### Create Accounts Receivable
```http
POST /api/v1/accounts-receivables/
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1-555-0456",
  "terms": "Net 15",
  "status": "active"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1-555-0456",
  "terms": "Net 15",
  "status": "active",
  "has_contact_info": true,
  "created_on": "2024-01-21T09:15:00Z",
  "modified_on": "2024-01-21T09:15:00Z"
}
```

#### Update Accounts Receivable
```http
PUT /api/v1/accounts-receivables/{id}/
Content-Type: application/json

{
  "name": "Jane Smith Updated",
  "email": "jane.updated@example.com",
  "phone": "+1-555-0789",
  "terms": "Net 30",
  "status": "active"
}
```

```http
PATCH /api/v1/accounts-receivables/{id}/
Content-Type: application/json

{
  "terms": "Net 45"
}
```

#### Delete Accounts Receivable (Soft Delete)
```http
DELETE /api/v1/accounts-receivables/{id}/
```

**Response:** `204 No Content`

Note: This performs a soft delete by setting `status` to `inactive`.

#### Get Migration Information
```http
GET /api/v1/accounts-receivables/migration_info/
```

**Response:**
```json
{
  "powerapps_entity_name": "cr7c4_accountsreceivables",
  "django_model_name": "AccountsReceivable",
  "django_app_name": "accounts_receivables",
  "total_records": 150,
  "active_records": 142,
  "field_mappings": {
    "cr7c4_names": "name",
    "cr7c4_email": "email",
    "cr7c4_phone": "phone",
    "cr7c4_terms": "terms",
    "statecode/statuscode": "status",
    "CreatedOn": "created_on",
    "ModifiedOn": "modified_on",
    "CreatedBy": "created_by",
    "ModifiedBy": "modified_by",
    "OwnerId": "owner"
  },
  "api_endpoints": {
    "list": "/api/v1/accounts-receivables/",
    "detail": "/api/v1/accounts-receivables/{id}/",
    "migration_info": "/api/v1/accounts-receivables/migration_info/"
  }
}
```

## Common Response Patterns

### Success Responses

#### 200 OK
Successful GET request with data.

#### 201 Created
Successful POST request creating a new resource.

#### 204 No Content
Successful DELETE request.

### Error Responses

#### 400 Bad Request
```json
{
  "name": ["This field is required."],
  "email": ["Enter a valid email address."],
  "non_field_errors": ["Custom validation error."]
}
```

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

#### 500 Internal Server Error
```json
{
  "detail": "A server error occurred."
}
```

## Data Types and Validation

### Accounts Receivable Fields

| Field | Type | Required | Max Length | Validation |
|-------|------|----------|------------|------------|
| `name` | string | Yes | 850 | Non-empty string |
| `email` | string | No | 100 | Valid email format |
| `phone` | string | No | 100 | Any format |
| `terms` | string | No | 100 | Any text |
| `status` | string | No | 20 | `active` or `inactive` |

### Read-Only Fields

| Field | Description |
|-------|-------------|
| `id` | Primary key |
| `created_on` | Auto-set timestamp |
| `modified_on` | Auto-update timestamp |
| `created_by` | Set by API on creation |
| `modified_by` | Set by API on updates |
| `owner` | Set by API on creation |
| `has_contact_info` | Computed field |
| `powerapps_entity_name` | Migration reference |

## Filtering and Search

### Query Examples

```bash
# Search by name or email
GET /api/v1/accounts-receivables/?search=john

# Filter by status
GET /api/v1/accounts-receivables/?status=active

# Only records with contact information
GET /api/v1/accounts-receivables/?has_contact=true

# Combine filters
GET /api/v1/accounts-receivables/?status=active&has_contact=true&search=smith
```

### Ordering

```bash
# Order by name (default)
GET /api/v1/accounts-receivables/?ordering=name

# Order by creation date (newest first)
GET /api/v1/accounts-receivables/?ordering=-created_on

# Multiple ordering
GET /api/v1/accounts-receivables/?ordering=status,name
```

## Pagination

All list endpoints use page-based pagination:

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/accounts-receivables/?page=3",
  "previous": "http://localhost:8000/api/v1/accounts-receivables/?page=1",
  "results": []
}
```

- Default page size: 20 items
- Configure in Django settings: `REST_FRAMEWORK['PAGE_SIZE']`

## Rate Limiting

Currently no rate limiting in development. For production:

```python
# Install django-ratelimit
pip install django-ratelimit

# Apply to views
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='GET')
def api_view(request):
    pass
```

## CORS Configuration

Configured for React frontend on localhost:3000:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourproductiondomain.com"
]
```

## User Profiles API

### Overview
Manages user profile information including personal details, preferences, and profile images. This system enables user account management and authentication within ProjectMeats.

### Endpoints

#### List User Profiles
```http
GET /api/v1/user-profiles/
```

**Query Parameters:**
- `page` (integer): Page number for pagination
- `search` (string): Search in username, first_name, last_name, email fields

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/user-profiles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "first_name": "Admin",
      "last_name": "User",
      "email": "admin@projectmeats.com",
      "display_name": "Admin User",
      "phone": "+1-555-0123",
      "department": "Administration",
      "job_title": "System Administrator",
      "profile_image_url": "http://localhost:8000/media/profiles/admin.jpg",
      "timezone": "America/New_York",
      "email_notifications": true,
      "bio": "System administrator for ProjectMeats",
      "has_complete_profile": true,
      "created_on": "2024-01-15T10:30:00Z",
      "modified_on": "2024-01-20T14:45:00Z"
    }
  ]
}
```

#### Get User Profile Details
```http
GET /api/v1/user-profiles/{id}/
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "first_name": "Admin",
  "last_name": "User",
  "email": "admin@projectmeats.com",
  "display_name": "Admin User",
  "phone": "+1-555-0123",
  "department": "Administration",
  "job_title": "System Administrator",
  "profile_image": "profiles/admin.jpg",
  "profile_image_url": "http://localhost:8000/media/profiles/admin.jpg",
  "timezone": "America/New_York",
  "email_notifications": true,
  "bio": "System administrator for ProjectMeats",
  "has_complete_profile": true,
  "created_on": "2024-01-15T10:30:00Z",
  "modified_on": "2024-01-20T14:45:00Z"
}
```

#### Get Current User Profile
```http
GET /api/v1/user-profiles/me/
```

Returns the profile of the currently authenticated user. Same response format as individual user profile.

#### Update Current User Profile
```http
PATCH /api/v1/user-profiles/me/
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1-555-0789",
  "department": "Sales",
  "job_title": "Sales Manager",
  "bio": "Experienced sales professional in the meat industry",
  "timezone": "America/Chicago",
  "email_notifications": false
}
```

#### Update User Profile with Image
```http
PATCH /api/v1/user-profiles/{id}/
Content-Type: multipart/form-data

{
  "first_name": "Jane",
  "last_name": "Smith",
  "profile_image": [FILE_UPLOAD]
}
```

**Response:** `200 OK`
```json
{
  "id": 2,
  "username": "jsmith",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@projectmeats.com",
  "display_name": "Jane Smith",
  "profile_image_url": "http://localhost:8000/media/profiles/jane_smith.jpg",
  "has_complete_profile": true,
  "created_on": "2024-01-21T09:15:00Z",
  "modified_on": "2024-01-21T16:30:00Z"
}
```

### User Profile Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Read-only | Django username (unique) |
| `first_name` | string | No | User's first name |
| `last_name` | string | No | User's last name |
| `email` | string | Yes | Email address (unique) |
| `display_name` | string | Read-only | Computed display name |
| `phone` | string | No | Phone number |
| `department` | string | No | Department/division |
| `job_title` | string | No | Job title/position |
| `profile_image` | file | No | Profile image upload |
| `profile_image_url` | string | Read-only | Full URL to profile image |
| `timezone` | string | No | User's timezone |
| `email_notifications` | boolean | No | Email notification preference |
| `bio` | text | No | User biography/description |
| `has_complete_profile` | boolean | Read-only | Profile completion status |

### Authentication Integration

The User Profiles API integrates with Django's authentication system:

```javascript
// Frontend authentication check
import { UserProfilesService } from '../services/api';

const checkAuth = async () => {
  try {
    const profile = await UserProfilesService.getCurrentUserProfile();
    return profile;
  } catch (error) {
    // User not authenticated
    throw error;
  }
};
```

## Future Entities

As more PowerApps entities are migrated, they will follow the same API patterns:

### Planned Endpoints
- `/api/v1/suppliers/` - Supplier management
- `/api/v1/customers/` - Customer management  
- `/api/v1/purchase-orders/` - Purchase order management
- `/api/v1/contacts/` - Contact information
- `/api/v1/plants/` - Plant/facility data
- `/api/v1/carriers/` - Carrier information

Each will include:
- Standard CRUD operations
- PowerApps migration info endpoint
- Filtering, search, and pagination
- Comprehensive documentation

## Client Examples

### JavaScript/TypeScript

```typescript
// Using fetch
const response = await fetch('http://localhost:8000/api/v1/accounts-receivables/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
});
const data = await response.json();

// Using axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

const accounts = await api.get('/accounts-receivables/');

// User profile examples
const currentUser = await api.get('/user-profiles/me/');

// Update user profile
const updatedProfile = await api.patch('/user-profiles/me/', {
  job_title: 'Senior Manager',
  department: 'Operations'
});

// Upload profile image
const formData = new FormData();
formData.append('profile_image', fileInput.files[0]);
formData.append('first_name', 'Updated Name');

const profileWithImage = await api.patch('/user-profiles/me/', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});
```

### Python

```python
import requests

# Get list
response = requests.get('http://localhost:8000/api/v1/accounts-receivables/')
accounts = response.json()

# Create new
data = {
    'name': 'New Account',
    'email': 'new@example.com',
    'status': 'active'
}
response = requests.post(
    'http://localhost:8000/api/v1/accounts-receivables/',
    json=data
)
new_account = response.json()
```

### cURL

```bash
# List accounts
curl -X GET http://localhost:8000/api/v1/accounts-receivables/

# Create account
curl -X POST http://localhost:8000/api/v1/accounts-receivables/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Account", "email": "test@example.com"}'

# Update account
curl -X PATCH http://localhost:8000/api/v1/accounts-receivables/1/ \
  -H "Content-Type: application/json" \
  -d '{"terms": "Net 60"}'

# User profile examples
# Get current user profile
curl -X GET http://localhost:8000/api/v1/user-profiles/me/

# Update user profile
curl -X PATCH http://localhost:8000/api/v1/user-profiles/me/ \
  -H "Content-Type: application/json" \
  -d '{"job_title": "Senior Manager", "department": "Operations"}'

# Upload profile image
curl -X PATCH http://localhost:8000/api/v1/user-profiles/me/ \
  -H "Content-Type: multipart/form-data" \
  -F "profile_image=@profile.jpg" \
  -F "first_name=Updated Name"

# List all user profiles (admin only)
curl -X GET http://localhost:8000/api/v1/user-profiles/
```

## Development and Testing

### API Testing Tools
- **Swagger UI**: http://localhost:8000/api/docs/ (interactive testing)
- **Postman**: Import OpenAPI schema for collection
- **curl**: Command-line testing
- **Django Rest Framework Browsable API**: Built-in web interface

### Validation Testing

```bash
# Test required field validation
curl -X POST http://localhost:8000/api/v1/accounts-receivables/ \
  -H "Content-Type: application/json" \
  -d '{}'

# Test email validation
curl -X POST http://localhost:8000/api/v1/accounts-receivables/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "email": "invalid-email"}'
```

---

This API reference will be updated as new entities are migrated and features are added. For the most up-to-date information, always refer to the Swagger UI documentation.