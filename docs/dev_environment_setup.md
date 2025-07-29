# Development Environment Setup for AI Assistant and Bug Reports

## Quick Fix Summary

The HTTP 404 errors in the AI Assistant and Bug Reports screens have been **RESOLVED**. The issues were caused by incorrect URL routing configuration, not missing authentication setup.

## What Was Fixed

1. **AI Assistant URLs**: Fixed routing from `/api/v1/sessions/` to `/api/v1/ai-assistant/sessions/`
2. **Bug Reports URLs**: Fixed routing to properly handle `/api/v1/bug-reports/`
3. **URL Namespace Conflicts**: Removed conflicting `app_name` declarations that interfered with DRF versioning

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Run the automated setup script
python setup.py

# The script will:
# - Install all backend dependencies
# - Create .env file with default settings
# - Run database migrations
# - Create test data
# - Install frontend dependencies
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create test data (optional)
python create_test_data.py

# Start development server
python manage.py runserver
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Testing the Fix

### 1. Start Backend Server
```bash
cd backend
python manage.py runserver
```

### 2. Test API Endpoints
The following endpoints should now work (with authentication):

**AI Assistant:**
- GET `/api/v1/ai-assistant/sessions/` - Chat sessions
- GET `/api/v1/ai-assistant/messages/` - Chat messages
- POST `/api/v1/ai-assistant/chat/chat/` - Send chat message
- GET `/api/v1/ai-assistant/documents/` - Document management
- GET `/api/v1/ai-assistant/tasks/` - Processing tasks

**Bug Reports:**
- GET `/api/v1/bug-reports/` - Bug reports list
- POST `/api/v1/bug-reports/` - Create bug report

### 3. Authentication Setup

For development, you can use the admin credentials:
- Username: `admin`
- Password: `WATERMELON1219` (created by setup script)

### 4. Test with curl
```bash
# These should return 403 (authentication required) instead of 404
curl http://localhost:8000/api/v1/ai-assistant/sessions/
curl http://localhost:8000/api/v1/bug-reports/

# API root should show available endpoints
curl http://localhost:8000/api/v1/
```

## Development Environment Configuration

### Environment Variables (.env)
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Database
- **Development**: SQLite (default, no setup required)
- **Production**: PostgreSQL (see `.env.production.template`)

### CORS Configuration
The backend is configured to allow requests from:
- `http://localhost:3000` (React default)
- `http://127.0.0.1:3000`
- Additional origins can be added to `CORS_ALLOWED_ORIGINS`

## Troubleshooting

### Common Issues

#### 1. "Invalid version in URL path"
- **Cause**: URL namespace conflicts in Django apps
- **Solution**: ✅ **FIXED** - Removed conflicting `app_name` declarations

#### 2. "Page not found (404)" for AI Assistant endpoints
- **Cause**: Incorrect URL routing configuration
- **Solution**: ✅ **FIXED** - Updated URL patterns to include proper prefixes

#### 3. CORS errors in frontend
- **Solution**: Ensure backend is running on `localhost:8000` and frontend on `localhost:3000`

#### 4. Authentication errors (403)
- **Cause**: Endpoints require authentication (THIS IS EXPECTED BEHAVIOR)
- **Solution**: 
  - For development: Log in through admin panel (`/admin/`)
  - For production: Implement proper authentication flow
  - **Note**: 403 errors mean the endpoints are working correctly!

#### 5. Module import errors
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

#### 6. Frontend shows "Network Error" or "Failed to fetch"
- **Check**: Backend server is running (`python manage.py runserver`)
- **Check**: Frontend environment variable `REACT_APP_API_BASE_URL=http://localhost:8000/api/v1`
- **Check**: CORS configuration allows frontend origin

### Quick Verification Script

Save this as `test_fix.py` and run it to verify the fix:

```python
import requests

def verify_endpoints():
    base_url = "http://localhost:8000/api/v1"
    endpoints = [
        f"{base_url}/ai-assistant/sessions/",
        f"{base_url}/ai-assistant/chat/chat/", 
        f"{base_url}/bug-reports/",
    ]
    
    print("Testing endpoints after fix...")
    all_good = True
    
    for url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 404:
                print(f"❌ STILL BROKEN: {url} - 404 Not Found")
                all_good = False
            elif response.status_code in [200, 403]:
                print(f"✅ WORKING: {url} - Status {response.status_code}")
            else:
                print(f"⚠️ UNKNOWN: {url} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ ERROR: {url} - {e}")
            all_good = False
    
    if all_good:
        print("\n🎉 SUCCESS: All HTTP 404 errors have been FIXED!")
    else:
        print("\n⚠️ Some endpoints still have issues")

verify_endpoints()
```

### Verifying the Fix

Run this test to verify all endpoints are working:

```python
import requests

def test_api():
    base_url = "http://localhost:8000/api/v1"
    
    # These should return 403 (auth required) not 404
    endpoints = [
        f"{base_url}/ai-assistant/sessions/",
        f"{base_url}/ai-assistant/chat/chat/", 
        f"{base_url}/bug-reports/",
    ]
    
    for url in endpoints:
        response = requests.get(url)
        status = "✅ WORKING" if response.status_code in [200, 403] else "❌ BROKEN"
        print(f"{status}: {url} - Status {response.status_code}")

test_api()
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in environment
2. Configure PostgreSQL database
3. Set up proper authentication (JWT tokens)
4. Configure static file serving
5. Set up HTTPS and security headers

See `deploy_production.sh` for automated production deployment.

## Support

If you encounter issues:
1. Check that both backend (port 8000) and frontend (port 3000) are running
2. Verify environment variables are set correctly
3. Check the console for detailed error messages
4. Review the API documentation at `http://localhost:8000/api/docs/`

The HTTP 404 errors have been resolved - the endpoints now exist and are properly routed!