# Django Migration Timeout Fix & Troubleshooting Guide

## Issue Description
The ProjectMeats deployment was hanging during Django migrations due to timeout issues. Database index creation migrations can take longer than the default 5-minute command timeout, causing deployments to fail or hang.

## Root Cause
- Django migrations with database index creation operations take longer than expected
- The AI deployment orchestrator had a 5-minute timeout for all commands
- Complex migrations (like those in `suppliers.0005_supplier_suppliers_name_ed482a_idx_and_more.py` and `contacts.0002_contactinfo_contact_inf_name_05b51f_idx_and_more.py`) were timing out

## Solution Implemented

### 1. Extended Migration Timeout
- **Increased migration timeout from 5 minutes to 20 minutes**
- **Separated migration commands from other Django management commands**
- **Added verbose logging for migration progress tracking**

### 2. Safe Migration Execution
- **Added migration status checking before execution**
- **Implemented migration resume capability for interrupted deployments**
- **Added detailed error logging and recovery guidance**

### 3. Better Monitoring
- **Added progress indicators for long-running migrations**
- **Improved error messages with specific troubleshooting steps**
- **Added validation of migration completion**

## Files Modified
- `ai_deployment_orchestrator.py` - Main deployment orchestrator with migration handling improvements

## Testing
- Validated migration command syntax
- Confirmed timeout values are appropriate
- Tested migration status checking functionality

## Usage

### For Fresh Deployments
The enhanced deployment orchestrator will automatically:
1. Check for pending migrations
2. Run migrations with 20-minute timeout
3. Provide progress updates during execution
4. Verify successful completion

### For Resuming Failed Deployments
If a deployment fails during migrations:
1. **The orchestrator will detect partially applied migrations**
2. **Resume from the last successful migration point**
3. **Show progress for remaining migrations**

## Manual Troubleshooting

### Check Migration Status
```bash
cd /opt/projectmeats/backend
./venv/bin/python manage.py showmigrations --plan
```

### Run Migrations Manually with Timeout
```bash
cd /opt/projectmeats/backend
timeout 1200 ./venv/bin/python manage.py migrate --verbosity=2 --no-input
```

### Check for Long-Running Migrations
```bash
# Check which migrations create database indexes (these take longer)
cd /opt/projectmeats/backend
find . -name "*.py" -path "*/migrations/*" -exec grep -l "AddIndex" {} \;
```

### Monitor Migration Progress
```bash
# Watch Django logs during migration
tail -f /var/log/projectmeats/django.log

# Watch PostgreSQL activity
sudo -u postgres psql -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active';"
```

## Prevention Tips

1. **Always use the AI deployment orchestrator** for deployments - it now handles migration timeouts properly
2. **For large migrations**, consider running them manually first during low-traffic periods
3. **Monitor deployment logs** for migration progress indicators
4. **Test migrations locally** before deploying to production

## Common Migration Issues & Solutions

### Issue: "Migration timed out"
**Solution**: Re-run the deployment - it will resume from the last successful migration

### Issue: "Some migrations still pending after completion"
**Solution**: Check the migration output for specific errors and run specific migrations manually:
```bash
cd /opt/projectmeats/backend
./venv/bin/python manage.py migrate <app_name> <migration_name>
```

### Issue: "Database locked during migration"
**Solution**: Ensure no other processes are accessing the database:
```bash
# Stop services temporarily
sudo systemctl stop projectmeats nginx
# Run migrations
cd /opt/projectmeats/backend && ./venv/bin/python manage.py migrate
# Restart services  
sudo systemctl start projectmeats nginx
```

## Recovery Commands

### If deployment is completely stuck:
```bash
# Check what's running
ps aux | grep python | grep manage.py

# Kill hanging migration process (if found)
sudo pkill -f "manage.py migrate"

# Resume deployment
python3 ai_deployment_orchestrator.py --resume
```

### Database recovery check:
```bash
# Check Django migration table
sudo -u postgres psql -d projectmeats_prod -c "SELECT * FROM django_migrations ORDER BY applied DESC LIMIT 10;"
```

This fix ensures that Django migrations complete successfully even when database index creation takes longer than expected, preventing deployment hangs and improving overall deployment reliability.