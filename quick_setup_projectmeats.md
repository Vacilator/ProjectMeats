# ProjectMeats – Fast Setup Guide (Dev & Prod)

This guide helps you install everything and get ProjectMeats running in both development and production—no experience required!

---

## 1. Prerequisites (Install These First)

**You must have:**

- Python 3.9+ ([Download](https://www.python.org/downloads/))
- Node.js 16+ ([Download](https://nodejs.org/en/download/))
- Git ([Download](https://git-scm.com/downloads))
- PostgreSQL 12+ ([Download](https://www.postgresql.org/download/))  
  _(For production; optional for dev)_

**How to check/install:**  
Open your terminal (Command Prompt, PowerShell, or Terminal):

```bash
python --version      # Should print 3.9 or higher
node --version        # Should print 16 or higher
git --version         # Should print a version
psql --version        # Should print 12 or higher (if using Postgres)
```

---

## 2. Clone the Repository

```bash
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats
```

---

## 3. Easiest Setup: One Command for Dev Environment

Run this from the root folder:

```bash
make setup
make dev
```

- This installs backend & frontend dependencies, sets up your database, and starts both servers.
- Visit:
  - Backend: http://localhost:8000
  - Frontend: http://localhost:3000

---

## 4. Manual Setup Steps (If You Can't Use `make`)

**A. Backend (API):**

```bash
cd backend
cp .env.example .env         # Copy example environment config
pip install -r requirements.txt
python manage.py migrate     # Set up the database
python manage.py runserver   # Start backend server (Ctrl+C to stop)
```
- API docs: http://localhost:8000/api/docs/

**B. Frontend (Web App):**

Open a new terminal window, then:

```bash
cd frontend
npm install
npm start                    # Starts frontend on http://localhost:3000
```

---

## 5. Environment Files

Edit your `.env` files to set keys, DB info, etc.

**Development Example:**

- **backend/.env**
  ```
  DEBUG=True
  SECRET_KEY=your-secret-key
  DATABASE_URL=sqlite:///db.sqlite3   # Or use Postgres
  CORS_ALLOWED_ORIGINS=http://localhost:3000
  ```

- **frontend/.env.local**
  ```
  REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
  REACT_APP_ENVIRONMENT=development
  ```

---

## 6. Production Setup (Essentials Only)

**A. Backend:**

1. Set up PostgreSQL and create a production DB.
2. In `backend/.env`:
   ```
   DEBUG=False
   SECRET_KEY=your-production-secret
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ALLOWED_HOSTS=yourdomain.com
   ```
3. Install Gunicorn & collect static files:
   ```bash
   pip install gunicorn
   python manage.py collectstatic
   ```
4. Run Gunicorn:
   ```bash
   gunicorn projectmeats.wsgi:application --bind 0.0.0.0:8000
   ```

**B. Frontend:**

1. Set up `frontend/.env.production`:
   ```
   REACT_APP_API_BASE_URL=https://api.yourdomain.com/api/v1
   REACT_APP_ENVIRONMENT=production
   ```
2. Build for production:
   ```bash
   npm run build
   ```
3. Deploy `frontend/build/` folder to your hosting provider.

---

## 7. Required Reading for All Contributors

- [docs/agent_quick_start.md](docs/agent_quick_start.md) (**MANDATORY**)
- [docs/agent_activity_log.md](docs/agent_activity_log.md) (**MANDATORY** – log all your work!)

---

## 8. Getting Help

- Start with [ProjectMeats Setup Overview](SETUP_OVERVIEW.md)
- See [Backend Setup](docs/backend_setup.md) & [Frontend Setup](docs/frontend_setup.md) for details
- Log all activity in [docs/agent_activity_log.md](docs/agent_activity_log.md)
- For any problems, check the `/docs` folder

---

### **You're done!**  
You now have ProjectMeats running locally and know how to prep for production.