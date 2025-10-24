# Test Database Import Function Locally

## How to Test:

1. **Start Django shell:**
```bash
python manage.py shell
```

2. **Test model fields exist:**
```python
from main.models import User, Application, EventSection, PartnerUniversity

# Check User fields
print("User fields:", [f.name for f in User._meta.get_fields()])
# Should NOT have 'student_id'

# Check Application fields  
print("Application fields:", [f.name for f in Application._meta.get_fields()])
# Should have: name, student_id, phone, email, passed_credits, GPA, major, anything_else

# Check EventSection fields
print("EventSection fields:", [f.name for f in EventSection._meta.get_fields()])
# Should have: event, section_code, professor_name

# Check PartnerUniversity fields
print("PartnerUniversity fields:", [f.name for f in PartnerUniversity._meta.get_fields()])
# Should have: name, logo, created_at
```

3. **Test the view can be imported:**
```python
from main.views import restore_database
print("restore_database function imported successfully!")
```

## Check Railway Logs:

After deploying, check Railway logs for these messages:

- ✅ `"=== DATABASE IMPORT STARTED ==="`
- ✅ `"File uploaded: <filename>, size: <size>"`
- ✅ `"SQLite file is valid"`
- ✅ `"Models imported successfully"`
- ❌ `"=== DATABASE IMPORT ERROR ==="`  (if error occurs)

## Common Issues to Check:

1. **ALLOWED_HOSTS**: Make sure Railway domain is in ALLOWED_HOSTS in settings.py
2. **CSRF**: Check if CSRF_TRUSTED_ORIGINS includes Railway URL
3. **File Upload Size**: Check if uploaded file size exceeds Railway limits
4. **Memory**: Large SQLite files may exceed Railway memory limits

## Quick Fix if Still Failing:

Add this to your Railway environment variables:
```
DEBUG=True
```

This will show detailed error messages on the error page instead of white screen.
