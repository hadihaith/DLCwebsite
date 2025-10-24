# Database Import - Deployment Checklist

## ✅ All Fixes Applied

1. **User Model** - Changed from `student_id` to `username`
2. **Application Model** - Fixed all field names to match current schema
3. **EventSection Model** - Fixed to use `section_code` and `professor_name`
4. **PartnerUniversity Model** - Fixed to use `name` instead of `university_name`
5. **ExchangeApplication** - Skipped (requires file uploads)
6. **Error Handling** - Added comprehensive logging and error messages

## 🚀 Deploy Steps

1. **Commit changes:**
```bash
git add .
git commit -m "Fix database import - all model field mismatches resolved"
git push origin main
```

2. **Check Railway deployment logs** for:
   - ✅ Build successful
   - ✅ No import errors
   - ✅ Server started successfully

3. **Test the import page:**
   - Navigate to `/restore-database/` (or whatever your URL is)
   - Check if page loads (should show upload form)
   - Try uploading a SQLite file

## 🔍 If You Still Get Internal Server Error:

### Step 1: Check Settings

Make sure your `settings.py` has:

```python
# For Railway
ALLOWED_HOSTS = ['*']  # Or specific Railway domain

CSRF_TRUSTED_ORIGINS = [
    'https://your-railway-app.up.railway.app',
]

# Turn on DEBUG temporarily to see error details
DEBUG = True  # ONLY FOR DEBUGGING - Turn off after!
```

### Step 2: Check Railway Logs

In Railway dashboard:
1. Click on your deployment
2. Go to "Deployments" tab
3. Click on latest deployment
4. Check logs for:
   - `=== DATABASE IMPORT STARTED ===`
   - Any error messages
   - Python traceback

### Step 3: Common Errors and Fixes

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `ModuleNotFoundError: user_agents` | Missing package | Add `user-agents==2.2.0` to requirements.txt |
| `OperationalError: no such table` | Migration not run | Run `python manage.py migrate` |
| `FieldError: Unknown field` | Model field mismatch | Double-check model field names |
| `IntegrityError` | Required field missing | Check model for required fields |
| `MemoryError` | File too large | Reduce SQLite file size or upgrade Railway plan |

### Step 4: Enable Debug Mode Temporarily

In Railway environment variables, add:
```
DEBUG=True
```

This will show detailed error page instead of white screen.

⚠️ **IMPORTANT:** Turn DEBUG back to False after finding the issue!

### Step 5: Test Locally First

```bash
# Run development server
python manage.py runserver

# Navigate to http://localhost:8000/restore-database/
# Try uploading a small SQLite file
# Check console for logs
```

## 📋 What Changed in Code

### views.py (restore_database function):

**Before (BROKEN):**
```python
# ❌ User model doesn't have student_id
User.objects.filter(student_id=row['student_id'])

# ❌ Wrong field names
Application.objects.create(
    full_name=...,  # Should be 'name'
    phone_number=...,  # Should be 'phone'
    gpa=...,  # Should be 'GPA' (uppercase)
)

# ❌ ExchangeApplication missing required files
ExchangeApplication.objects.create(...)  # Crashes
```

**After (FIXED):**
```python
# ✅ Use username instead
User.objects.filter(username=row['username'])

# ✅ Correct field names
Application.objects.create(
    name=...,
    phone=...,
    GPA=...,
)

# ✅ Skip ExchangeApplications
messages.info(request, 'Skipping Exchange Applications...')
```

## 🎯 Final Verification

After deploying, verify:

- [ ] Page loads without error (GET request)
- [ ] Can select SQLite file
- [ ] Submit button works
- [ ] Either success message OR detailed error message shows
- [ ] Railway logs show detailed import process
- [ ] No white screen / generic 500 error

## 🆘 Still Not Working?

If you still get errors after all this:

1. **Copy the EXACT error message** from Railway logs
2. **Check which line** the error occurs on
3. **Take a screenshot** of the error
4. Share the error message for further debugging

The logging is now so comprehensive that we'll see exactly where it fails!
