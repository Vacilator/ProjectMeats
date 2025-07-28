# Python 3.13+ Setup Issues and Solutions

## PostgreSQL Adapter Compatibility Issue

If you encounter errors during setup with Python 3.13+ on Windows, particularly errors related to `psycopg2-binary` requiring Microsoft Visual C++ 14.0, this document provides solutions.

### The Problem

```
error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

This occurs because:
- `psycopg2-binary` doesn't have precompiled wheels for Python 3.13 on Windows
- pip attempts to build from source, requiring Visual C++ build tools
- This affects Windows users specifically

### Solutions (Choose One)

#### Option 1: Use Development Requirements (Recommended)
The project includes `requirements-dev.txt` without PostgreSQL dependencies:

```bash
cd backend
pip install -r requirements-dev.txt
```

The application will use SQLite database (recommended for development).

#### Option 2: Install Visual C++ Build Tools
1. Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Run the regular setup: `python setup.py`

#### Option 3: Use Alternative PostgreSQL Adapter
Replace `psycopg[binary]==3.2.9` in `requirements.txt` with:
```
psycopg2-binary==2.9.10
```
(May still require build tools but sometimes works)

#### Option 4: Skip PostgreSQL for Development
1. Remove the psycopg line from `requirements.txt`
2. Run setup normally
3. The app uses SQLite by default

### Production PostgreSQL Setup

For production with PostgreSQL:
```bash
pip install "psycopg[binary]>=3.2.0"
```

Then set your `DATABASE_URL` environment variable:
```
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Enhanced Setup Script

The setup script now automatically:
- Detects Python 3.13+ on Windows
- Uses development requirements when available
- Provides fallback installation without PostgreSQL
- Gives clear error messages and solutions

### Verification

After setup, verify the backend works:
```bash
cd backend
python manage.py check
python manage.py runserver
```

The application should start successfully using SQLite database.