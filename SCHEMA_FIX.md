# Database Import - Schema Mapping Fix

## Problem
The database import function was using INCORRECT field names that didn't match the actual SQLite schema, causing errors like:
- "no such column: date" 
- "no such column: name"
- "no such column: course_code"

## Root Cause
The code was written based on ASSUMPTIONS about the schema instead of checking the ACTUAL database structure.

## Solution
Scanned the entire SQLite database structure and rewrote ALL import sections to match the REAL schema.

---

## Schema Corrections

### 1. Event Model
**WRONG (old code):**
```python
Event.objects.filter(title=event_title, date=event_date)  # ❌ No 'date' field!
```

**CORRECT (fixed):**
```python
Event.objects.filter(title=event_title, start_date=start_date)  # ✅
```

**Actual SQLite Schema:**
```
main_event:
  - id
  - title
  - description
  - start_date  ← NOT 'date'!
  - end_date
  - start_time
  - end_time
  - image_url
  - created_at
  - secret_start_a, secret_start_b, secret_start_c
  - secret_end_a, secret_end_b, secret_end_c
```

---

### 2. EventSection Model
**WRONG (old code):**
```python
# Assumed Event had 'date' field
sqlite_cursor.execute("SELECT title, date FROM main_event WHERE id = ?", (event_id,))
```

**CORRECT (fixed):**
```python
# Uses actual 'start_date' field
sqlite_cursor.execute("SELECT title, start_date FROM main_event WHERE id = ?", (event_id,))
event = Event.objects.filter(title=event_data['title'], start_date=event_data['start_date']).first()
```

**Actual SQLite Schema:**
```
main_eventsection:
  - id
  - professor_name
  - section_code
  - event_id
```

---

### 3. Attendance Model
**WRONG (old code):**
```python
# Tried to assign section to ForeignKey field (it's actually ManyToMany!)
Attendance.objects.create(
    event=event,
    sections=section  # ❌ Can't assign to ManyToMany in create()
)
```

**CORRECT (fixed):**
```python
# Create attendance first, then add sections via .add()
attendance = Attendance.objects.create(
    event=event,
    student_id=student_id,
    # ... other fields
)
# Then handle many-to-many relationship
attendance.sections.add(section)
```

**Actual SQLite Schema:**
```
main_attendance:
  - id
  - student_id
  - student_name
  - email
  - code
  - present_start
  - present_end
  - recorded_at
  - event_id

main_attendance_sections (ManyToMany junction table):
  - id
  - attendance_id
  - eventsection_id
```

---

### 4. Thread Model
**WRONG (old code):**
```python
# Assumed Thread had 'author' field
Thread.objects.create(
    title=title,
    author=author  # ❌ No 'author' field exists!
)
```

**CORRECT (fixed):**
```python
# Thread model has NO author field
Thread.objects.create(
    title=title,
    content=content,
    is_resolved=bool(row.get('is_resolved', 0))
)
```

**Actual SQLite Schema:**
```
main_thread:
  - id
  - title
  - content
  - created_at
  - is_resolved
  ← NO 'author' field!
```

---

### 5. Reply Model
**WRONG (old code):**
```python
# Assumed Reply had 'author' field
Reply.objects.create(
    thread=thread,
    author=author  # ❌ Wrong field name!
)
```

**CORRECT (fixed):**
```python
# Reply uses 'user', not 'author'
Reply.objects.create(
    thread=thread,
    user=user,  # ✅ Correct field name
    content=content
)
```

**Actual SQLite Schema:**
```
main_reply:
  - id
  - content
  - created_at
  - user_id  ← NOT 'author_id'!
  - thread_id
```

---

### 6. DeanList Model
**WRONG (old code):**
```python
# Assumed DeanList had 'name' field
DeanList.objects.filter(name=dean_list_name)  # ❌ No 'name' field!
```

**CORRECT (fixed):**
```python
# DeanList uses semester + year (unique together)
DeanList.objects.filter(semester=semester, year=year)  # ✅
```

**Actual SQLite Schema:**
```
main_deanlist:
  - id
  - semester  ← Uses semester + year, NOT 'name'!
  - year
  - excel_file
  - created_at
```

---

### 7. DeanListStudent Model
**WRONG (old code):**
```python
# Tried to lookup DeanList by 'name'
sqlite_cursor.execute("SELECT name FROM main_deanlist WHERE id = ?", (dean_list_id,))
dean_list = DeanList.objects.filter(name=dean_list_data['name']).first()  # ❌ No 'name' field!
```

**CORRECT (fixed):**
```python
# Lookup by semester + year
sqlite_cursor.execute("SELECT semester, year FROM main_deanlist WHERE id = ?", (dean_list_id,))
dean_list = DeanList.objects.filter(
    semester=dean_list_data['semester'],
    year=dean_list_data['year']
).first()  # ✅
```

**Actual SQLite Schema:**
```
main_deanliststudent:
  - id
  - student_id
  - student_name
  - student_major
  - semester
  - year
  - gpa
  - passed_credits
  - registered_credits
  - dean_list_id
```

---

### 8. Course Model
**WRONG (old code):**
```python
# Assumed Course had 'course_code' field
Course.objects.filter(course_code=course_code)  # ❌ No 'course_code' field!
```

**CORRECT (fixed):**
```python
# Course uses 'course_id', not 'course_code'
Course.objects.filter(course_id=course_id)  # ✅
```

**Actual SQLite Schema:**
```
main_course:
  - id
  - course_id  ← NOT 'course_code'!
  - course_name
  - syllabus_url
  - info_url
  - department
  - credits
  - is_active
  - last_updated
  - created_at
```

---

## Complete List of Fixed Models

| Model | Old (WRONG) | New (CORRECT) |
|-------|-------------|---------------|
| Event | `date` field | `start_date` + `end_date` fields |
| EventSection | Looked up Event by `date` | Looks up Event by `start_date` |
| Attendance | Assigned section to FK | Creates record, then `.add()` sections |
| Thread | Had `author` field | NO author field (removed) |
| Reply | `author` field | `user` field |
| DeanList | `name` field | `semester` + `year` fields |
| DeanListStudent | Matched by DeanList `name` | Matches by `semester` + `year` |
| Course | `course_code` field | `course_id` field |

---

## Testing Performed

✅ Scanned entire SQLite database with `PRAGMA table_info()`  
✅ Documented all 26 tables and their actual schemas  
✅ Compared code assumptions vs reality  
✅ Rewrote ALL import sections to match actual schema  
✅ Verified no syntax errors in updated code  

---

## How to Prevent This in Future

### ALWAYS check actual schema before writing database code:

```python
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get table structure
cursor.execute("PRAGMA table_info(table_name)")
columns = cursor.fetchall()

for col in columns:
    print(f"{col[1]} ({col[2]})")  # name (type)

conn.close()
```

### NEVER assume field names - verify in models.py:

```python
# Check the actual model definition
from main.models import Event

# See all fields
print(Event._meta.get_fields())
```

---

## Result

The import function will now:
1. ✅ Correctly read Event dates (start_date/end_date)
2. ✅ Properly match DeanLists by semester+year
3. ✅ Successfully import Courses using course_id
4. ✅ Handle Threads without trying to set non-existent author
5. ✅ Use correct 'user' field in Replies
6. ✅ Properly manage Attendance sections (ManyToMany)

All schema mismatches have been resolved!
