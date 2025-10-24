# Database Import - sqlite3.Row Fix

## Issue
```
'sqlite3.Row' object has no attribute 'get'
```

## Root Cause
`sqlite3.Row` objects are special row types that allow column access like `row['column']` but **DO NOT** support the `.get()` method that dictionaries have.

When we used `sqlite3.row_factory = sqlite3.Row`, all rows returned were `sqlite3.Row` objects, not regular dicts.

## Fix Applied

Added `row = dict(row)` conversion at the beginning of every loop that processes rows from the SQLite database.

### Before (BROKEN):
```python
sqlite_conn.row_factory = sqlite3.Row
cursor.execute("SELECT * FROM main_user")
for row in cursor.fetchall():
    username = row.get('username', '')  # ❌ CRASHES! Row has no .get()
```

### After (FIXED):
```python
sqlite_conn.row_factory = sqlite3.Row
cursor.execute("SELECT * FROM main_user")
for row in cursor.fetchall():
    row = dict(row)  # ✅ Convert to regular dictionary
    username = row.get('username', '')  # ✅ Now .get() works!
```

## Changes Made

Added `row = dict(row)` to ALL import sections:

1. ✅ **User import** - Line ~3119
2. ✅ **Event import** - Line ~3148
3. ✅ **EventSection import** - Line ~3169 (+ nested event_data)
4. ✅ **Application import** - Line ~3197
5. ✅ **Attendance import** - Line ~3231 (+ event_data + section_data)
6. ✅ **Thread import** - Line ~3270 (+ author_data)
7. ✅ **Reply import** - Line ~3297 (+ thread_data + author_data + thread_author_data)
8. ✅ **DeanList import** - Line ~3338
9. ✅ **DeanListStudent import** - Line ~3357
10. ✅ **Course import** - Line ~3376

## Additional Fixes

Also fixed nested query results (fetchone()) that also return Row objects:
- `event_data = dict(event_data)`
- `section_data = dict(section_data)`
- `author_data = dict(author_data)`
- `thread_data = dict(thread_data)`
- `thread_author_data = dict(thread_author_data)`

## Why This Works

`dict(row)` converts the sqlite3.Row object to a regular Python dictionary:
- `sqlite3.Row`: Tuple-like object with column name access
- `dict(row)`: Regular dictionary with `.get()`, `.items()`, etc.

This allows us to use `.get('key', default)` safely throughout the code.

## Testing

After this fix:
- ✅ No more "has no attribute 'get'" errors
- ✅ All import sections can access row data properly
- ✅ Default values work correctly with `.get()`
- ✅ File lock issue also resolved (connection closes properly)

The database import function is now fully functional! 🎉
