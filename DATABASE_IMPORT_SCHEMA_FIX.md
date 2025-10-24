# Database Import - Complete Schema Fix

## Problem Summary
The database import function was using **incorrect field names** that didn't match the actual SQLite database schema, causing errors like:
- `no such column: date`
- `no such column: name` 
- Worker timeout errors

## Root Cause Analysis

### What Was Wrong:
The import code was written based on **assumed** model fields, not the **actual** database schema. This happened because:
1. Models were modified over time
2. Import code wasn't updated to match
3. No schema validation before import

### How We Fixed It:
1. **Scanned entire SQLite database** using `PRAGMA table_info()` 
2. **Identified ALL schema mismatches** between code and reality
3. **Rewrote every import section** to use correct field names
4. **Added proper error handling** for missing foreign keys

## Complete Schema Corrections

### 1. Event Model ✅
**WRONG:**
```python
Event.objects.filter(title=event_title, date=event_date)
```

**CORRECT:**
```python
Event.objects.filter(title=event_title, start_date=start_date)
```

**Actual Schema:**
- `start_date` (date)
- `end_date` (date)
- `start_time` (time)
- `end_time` (time)
- `secret_start_a`, `secret_start_b`, `secret_start_c` (INTEGER)
- `secret_end_a`, `secret_end_b`, `secret_end_c` (INTEGER)

### 2. DeanList Model ✅
**WRONG:**
```python
DeanList.objects.filter(name=dean_list_name)
```

**CORRECT:**
```python
DeanList.objects.filter(semester=semester, year=year)
```

**Actual Schema:**
- `semester` (varchar(10)) - CHOICES: 'fall', 'spring'
- `year` (INTEGER)
- `excel_file` (varchar(100))
- `created_at` (datetime)
- **UNIQUE TOGETHER:** `(semester, year)`

### 3. DeanListStudent Model ✅
**WRONG:**
```python
# Tried to match DeanList by non-existent 'name' field
SELECT name FROM main_deanlist WHERE id = ?
```

**CORRECT:**
```python
# Match DeanList by semester + year
SELECT semester, year FROM main_deanlist WHERE id = ?
DeanList.objects.filter(semester=semester, year=year).first()
```

**Actual Schema:**
- `student_id` (varchar(20))
- `student_name` (varchar(200))
- `student_major` (varchar(50))
- `semester` (varchar(10))
- `year` (INTEGER)
- `gpa` (decimal)
- `passed_credits` (INTEGER)
- `registered_credits` (INTEGER)
- `dean_list_id` (bigint) - ForeignKey

### 4. Course Model ✅
**WRONG:**
```python
Course.objects.filter(course_code=course_code)
```

**CORRECT:**
```python
Course.objects.filter(course_id=course_id)
```

**Actual Schema:**
- `course_id` (varchar(20)) - UNIQUE - e.g., "FIN301"
- `course_name` (varchar(255))
- `syllabus_url` (varchar(200))
- `info_url` (varchar(200))
- `department` (varchar(10))
- `credits` (INTEGER)
- `is_active` (bool)

### 5. Thread Model ✅
**WRONG:**
```python
Thread.objects.create(
    title=title,
    content=content,
    author=author  # ❌ Field doesn't exist!
)
```

**CORRECT:**
```python
Thread.objects.create(
    title=title,
    content=content,
    is_resolved=bool(is_resolved)
)
```

**Actual Schema:**
- `title` (varchar(200))
- `content` (TEXT)
- `created_at` (datetime)
- `is_resolved` (bool)
- **NO AUTHOR FIELD**

### 6. Reply Model ✅
**WRONG:**
```python
Reply.objects.create(
    thread=thread,
    author=author  # ❌ Wrong field name!
)
```

**CORRECT:**
```python
Reply.objects.create(
    thread=thread,
    user=user  # ✅ Correct field name
)
```

**Actual Schema:**
- `content` (TEXT)
- `created_at` (datetime)
- `user_id` (bigint) - ForeignKey to User
- `thread_id` (bigint) - ForeignKey to Thread

### 7. Attendance Model ✅
**WRONG:**
```python
Attendance.objects.create(
    event=event,
    sections=section  # ❌ Can't assign to ManyToMany!
)
```

**CORRECT:**
```python
attendance = Attendance.objects.create(
    event=event,
    student_id=student_id,
    code=code,
    present_start=bool(present_start),
    present_end=bool(present_end)
)
# Then add sections via ManyToMany
attendance.sections.add(section)
```

**Actual Schema:**
- `student_id` (varchar(50))
- `student_name` (varchar(200))
- `email` (VARCHAR(254))
- `code` (varchar(50))
- `present_start` (bool)
- `present_end` (bool)
- `recorded_at` (datetime)
- `event_id` (bigint) - ForeignKey
- **MANY-TO-MANY:** `sections` via `main_attendance_sections` table

### 8. EventSection Model ✅
**WRONG:**
```python
# Queried event with wrong field name
SELECT title, date FROM main_event WHERE id = ?
```

**CORRECT:**
```python
# Query with correct field names
SELECT title, start_date FROM main_event WHERE id = ?
Event.objects.filter(title=title, start_date=start_date).first()
```

**Actual Schema:**
- `professor_name` (varchar(200))
- `section_code` (varchar(50))
- `event_id` (bigint) - ForeignKey
- **UNIQUE TOGETHER:** `(event, section_code)`

## Import Logic Improvements

### 1. DeanList: get_or_create Pattern
**Before:**
```python
if not DeanList.objects.filter(semester=semester, year=year).exists():
    DeanList.objects.create(...)
```

**After:**
```python
dean_list, created = DeanList.objects.get_or_create(
    semester=semester,
    year=year,
    defaults={'excel_file': file, 'created_at': created_at}
)
```

**Benefits:**
- Atomic operation (no race conditions)
- Returns the object whether new or existing
- Ensures DeanList exists before importing students

### 2. Better Error Handling
**Added:**
- Null checks for all foreign key lookups
- Skip counter for missing foreign keys
- Detailed logging for debugging
- Try-except blocks for each model import

**Example:**
```python
if dean_list:
    # Import student
else:
    logger.warning(f"DeanList not found for semester={semester}, year={year}")
    stats['dean_students']['skipped'] += 1
```

### 3. Comprehensive Logging
**Added logging at key points:**
```python
logger.info(f"Found {len(dean_student_rows)} dean list students to import")
logger.info(f"Looking for DeanList with semester={semester}, year={year}")
logger.warning(f"DeanList not found for semester={semester}, year={year}")
logger.error(f"Dean list student import error: {e}", exc_info=True)
```

## Testing Checklist

Before importing a database, verify:

- [ ] DeanLists are imported BEFORE DeanListStudents
- [ ] Events are imported BEFORE EventSections and Attendance
- [ ] Users are imported BEFORE Replies
- [ ] Threads are imported BEFORE Replies
- [ ] All foreign key relationships resolve correctly
- [ ] get_or_create is used for DeanList to ensure existence

## Performance Optimizations

### Current Implementation:
- Row-by-row processing
- Individual database queries per row
- FK lookups via source DB queries

### Future Improvements:
1. **Bulk Operations:** Use `bulk_create()` for batch inserts
2. **FK Caching:** Cache FK lookups in memory
3. **Transaction Batching:** Commit every N records
4. **Progress Indicators:** Show import progress to user

## Common Errors & Solutions

### Error: "no such column: date"
**Cause:** Event table uses `start_date`, not `date`
**Solution:** Use `start_date` and `end_date` fields

### Error: "no such column: name" 
**Cause:** DeanList table uses `semester` + `year`, not `name`
**Solution:** Match by `(semester, year)` unique constraint

### Error: Worker Timeout
**Cause:** Import taking >30 seconds (default Gunicorn timeout)
**Solution:** Increased timeout to 300s in Procfile

### Error: "cannot assign to ManyToManyField"
**Cause:** Trying to assign directly to `sections` field
**Solution:** Create object first, then use `.add()` method

## Files Modified

1. **main/views.py** - restore_database() function
   - Lines 3000-3600: Complete rewrite of import logic
   - All 8 model import sections corrected

2. **Procfile** - Gunicorn configuration
   - Added `--timeout 300` to allow long imports

3. **check_schema.py** - Schema inspection utility
   - Created to verify actual database structure

## Verification Steps

1. Check DeanList count before import
2. Run import with SQLite file
3. Check DeanList count after import
4. Verify DeanListStudents are linked correctly
5. Check logs for any warnings/errors
6. Confirm all FK relationships are valid

## Summary

This fix ensures the database import function works with the **actual** database schema, not assumptions. Every field name, foreign key relationship, and model constraint has been verified against the real SQLite database structure.

**Result:** Import now works correctly without schema-related errors.
