# Database Import Function - Critical Fixes Applied

## Date: October 25, 2025

## Problem
The database import/merge function was causing **Internal Server Error 500** in production due to multiple critical issues:

### Critical Issues Fixed:

1. **Non-existent Model Import**
   - ❌ **OLD**: Tried to import `MembershipApplication` model which doesn't exist
   - ✅ **FIXED**: Removed `MembershipApplication` from imports and code

2. **Wrong Field Names in Application Model**
   - ❌ **OLD**: Used fields like `full_name`, `year`, `phone_number`, `why_join`, `what_expect`, etc.
   - ✅ **FIXED**: Now uses actual fields: `name`, `student_id`, `phone`, `email`, `passed_credits`, `GPA`, `major`, `anything_else`

3. **Wrong Field Names in EventSection Model**
   - ❌ **OLD**: Used `section_name` (doesn't exist)
   - ✅ **FIXED**: Now uses `section_code` and `professor_name` (actual fields)

4. **Wrong Field Names in ExchangeApplication Model**
   - ❌ **OLD**: Used old schema with `student_id`, `destination_university`, `phone_number`, etc.
   - ✅ **FIXED**: Now uses current schema: `first_name`, `last_name`, `date_of_birth`, `home_institution` (ForeignKey), `passport_number`, `exchange_semester`, etc.

5. **Broken Foreign Key Lookups**
   - ❌ **OLD**: Tried to match records using IDs from source database (Event.objects.filter(id=row['event_id']))
   - ✅ **FIXED**: Now properly looks up the related record in source DB first, then matches by unique fields in target DB

## Changes Made

### 1. Model Imports
```python
# Removed MembershipApplication, added PartnerUniversity
from main.models import (
    User, Application, Event, Attendance,
    Thread, Reply, DeanList, DeanListStudent, Course, 
    EventSection, ExchangeApplication, PartnerUniversity
)
```

### 2. Application Import
Now matches actual Application model fields:
- `name` (not `full_name`)
- `phone` (not `phone_number`)
- `GPA` (not `gpa`)
- `passed_credits`
- `major`
- `anything_else` (not `why_join`, `what_expect`, etc.)

### 3. EventSection Import
- Properly finds the parent Event by looking up title/date from source DB
- Uses `section_code` and `professor_name` fields
- Correctly handles foreign key relationship

### 4. ExchangeApplication Import
- Handles `PartnerUniversity` foreign key properly
- Creates/finds PartnerUniversity if needed
- Uses correct field names: `first_name`, `last_name`, `passport_number`, `home_institution`, etc.
- Only imports if valid home institution exists

### 5. Attendance Import
- Looks up Event by title/date (not by ID)
- Looks up EventSection by section_code (not by ID)
- Properly links foreign keys

### 6. Thread Import
- Finds author by student_id lookup chain (source DB ID → student_id → target DB User)
- Avoids broken ID-based lookups

### 7. Reply Import
- Complex lookup chain to find both Thread and Author
- Properly resolves foreign keys through source DB lookups

## How Foreign Key Resolution Works Now

**OLD (BROKEN):**
```python
event = Event.objects.filter(id=row['event_id']).first()  # ❌ Wrong ID!
```

**NEW (FIXED):**
```python
# 1. Get the foreign key ID from row
event_id = row.get('event_id')

# 2. Look up the referenced record in SOURCE database
sqlite_cursor.execute("SELECT title, date FROM main_event WHERE id = ?", (event_id,))
event_data = sqlite_cursor.fetchone()

# 3. Find matching record in TARGET database using unique fields
event = Event.objects.filter(title=event_data['title'], date=event_data['date']).first()
```

## Testing Checklist

Before deploying, verify:
- ✅ No import errors (MembershipApplication removed)
- ✅ Application fields match model
- ✅ EventSection uses correct fields
- ✅ ExchangeApplication handles PartnerUniversity FK
- ✅ All foreign key lookups use proper resolution
- ✅ No hard-coded ID lookups from source DB

## Deployment Steps

1. **Commit changes**: `git add .` and `git commit -m "Fix database import function - resolve model field mismatches and FK lookups"`
2. **Push to production**: `git push origin main`
3. **Test import**: Upload a SQLite file in production
4. **Monitor logs**: Check Railway logs for any remaining errors

## Notes

- The function now properly handles differences between SQLite source and PostgreSQL target
- Foreign keys are resolved by looking up unique identifiers (student_id, title+date, etc.)
- Missing or invalid foreign key references are gracefully skipped
- Stats tracking remains intact for all import operations
