# ProjectMeats Troubleshooting Guide

## Python 3.13+ Setup Issues (Windows)

### PostgreSQL Adapter Compatibility Issue

If you encounter errors during setup with Python 3.13+ on Windows, particularly errors related to `psycopg2-binary` requiring Microsoft Visual C++ 14.0:

```
error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**Solutions** (choose one):

#### Option 1: Use Development Requirements (Recommended)
```bash
cd backend
pip install -r requirements-dev.txt
```
The application will use SQLite database (recommended for development).

#### Option 2: Install Visual C++ Build Tools
1. Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Run the regular setup: `python setup.py`

#### Option 3: Skip PostgreSQL for Development
1. Remove the psycopg line from `requirements.txt`
2. Run setup normally - the app uses SQLite by default

## Common Setup Issues

### "python: command not found"
- **Solution**: Try `python3 setup.py` or install Python from python.org

### "node: command not found"  
- **Solution**: Install Node.js from nodejs.org

### Windows users experiencing "true is not recognized"
- **Solution**: Use `python setup.py` instead of make commands

### Permission errors during setup
- **Linux/macOS**: Try using `sudo` for global installations
- **Windows**: Run command prompt as Administrator

## Database Issues

### SQLite vs PostgreSQL
- **Development**: SQLite works fine and requires no additional setup
- **Production**: PostgreSQL is recommended for better performance

### Migration errors
```bash
cd backend
python manage.py migrate --run-syncdb
```

### Database reset (if needed)
```bash
cd backend
rm db.sqlite3  # Remove SQLite database
python manage.py migrate
python manage.py createsuperuser
```

## Development Server Issues

### Port already in use
- **Backend (8000)**: Kill existing Django processes or use different port
- **Frontend (3000)**: Kill existing React processes or use different port

### CORS errors
Ensure your `.env` file has:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## Testing Issues

### Test database errors
```bash
cd backend
python manage.py test --keepdb  # Reuse test database
```

### Specific test failures
```bash
cd backend
python manage.py test apps.specific_app  # Test specific app
```

## Frontend Issues

### npm install errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Build errors
```bash
cd frontend
npm run build  # Check for TypeScript errors
```

## Getting Help

1. Check this troubleshooting guide first
2. Review error messages carefully
3. Search existing GitHub issues
4. Create a new issue with:
   - Operating system and versions
   - Complete error message
   - Steps to reproduce