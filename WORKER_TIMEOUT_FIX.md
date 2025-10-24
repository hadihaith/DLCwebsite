# Database Import - Worker Timeout Fix

## Issue: WORKER TIMEOUT

### Error:
```
[CRITICAL] WORKER TIMEOUT (pid:104)
[ERROR] Error handling request /portal/database/restore/
SystemExit: 1
```

### Root Cause:
Gunicorn's default worker timeout is **30 seconds**. Large database imports take longer than this, causing the worker to be killed mid-process.

### Contributing Factors:
1. **Slow Foreign Key Lookups**: Each DeanListStudent was doing `DeanList.objects.filter(id=row['dean_list_id'])` with wrong ID
2. **Many Database Queries**: One query per row instead of batch operations
3. **Large Dataset**: Importing thousands of records sequentially

## Fixes Applied

### 1. Fixed DeanListStudent Import Logic

**Before (BROKEN):**
```python
# ❌ Tried to match by ID from source DB - will never work!
dean_list = DeanList.objects.filter(id=row['dean_list_id']).first()
```

**After (FIXED):**
```python
# ✅ Look up dean list name from source, then match by name
dean_list_id = row.get('dean_list_id')
if dean_list_id:
    # Get the name from source database
    sqlite_cursor.execute("SELECT name FROM main_deanlist WHERE id = ?", (dean_list_id,))
    dean_list_data = sqlite_cursor.fetchone()
    
    if dean_list_data:
        dean_list_data = dict(dean_list_data)
        # Find in target DB by name (not ID!)
        dean_list = DeanList.objects.filter(name=dean_list_data['name']).first()
```

### 2. Added Warning Message

Users are now warned that large imports may timeout:
```python
messages.warning(request, '⚠️ Large imports may timeout. Keep database files under 1000 records for best results.')
```

## Solutions for Large Imports

### Option 1: Increase Gunicorn Timeout (Recommended)

Add to your `Procfile` or Gunicorn config:
```
web: gunicorn Dlcweb.wsgi --timeout 300 --bind 0.0.0.0:8080
```

This increases timeout from 30 seconds to 5 minutes (300 seconds).

### Option 2: Use Celery for Background Processing

For very large imports, use Celery to process imports in the background:
1. User uploads file
2. Task starts in background
3. User sees progress page
4. Email notification when complete

### Option 3: Split Large Databases

Instead of importing everything at once:
1. Export data in smaller chunks (by date range, model type, etc.)
2. Import each chunk separately
3. Merge results

### Option 4: Use Django's bulk_create()

For future optimization, use bulk operations:
```python
# Instead of:
for row in rows:
    User.objects.create(...)  # ❌ Slow - one query per row

# Use:
users_to_create = [User(...) for row in rows]
User.objects.bulk_create(users_to_create)  # ✅ Fast - one query for all
```

## Immediate Fix for Your Deployment

Update your `Procfile`:

**Before:**
```
web: python manage.py collectstatic --noinput; python manage.py migrate; python manage.py init_superuser; gunicorn Dlcweb.wsgi --bind 0.0.0.0:$PORT
```

**After:**
```
web: python manage.py collectstatic --noinput; python manage.py migrate; python manage.py init_superuser; gunicorn Dlcweb.wsgi --timeout 300 --bind 0.0.0.0:$PORT
```

This gives the import process 5 minutes instead of 30 seconds.

## Why the Timeout Happened

1. **DeanListStudent loop was slow**: Each iteration did multiple queries
2. **Wrong ID matching**: IDs from source DB don't exist in target DB → slow queries returning nothing
3. **No result found**: Query had to scan entire table to find non-existent ID
4. **Multiplied by thousands of rows**: Each row = multiple slow queries
5. **30 second timeout exceeded**: Gunicorn killed the worker

## Testing Recommendations

1. **Start with small databases** (< 100 records) to verify functionality
2. **Gradually increase size** to find your timeout threshold
3. **Monitor Railway logs** to see how long imports take
4. **Adjust timeout** based on actual import times

## Current Status

- ✅ Fixed DeanListStudent lookup logic (matches by name, not ID)
- ✅ Added warning message about timeouts
- ⚠️ Still need to update Procfile with `--timeout 300` for large imports

## Next Steps

1. Update `Procfile` with increased timeout
2. Test with your database file
3. Monitor import time in logs
4. Consider batch operations for future optimization
