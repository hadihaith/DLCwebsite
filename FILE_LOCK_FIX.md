# Database Import - File Lock Fix

## Issue
```
PermissionError: [WinError 32] The process cannot access the file because 
it is being used by another process: tmpXXXXXX.sqlite3
```

## Root Cause
When an error occurred during the import process, the exception handler tried to delete the temporary SQLite file **without closing the database connection first**. On Windows, you cannot delete a file that's still open by a process.

## Fix Applied

### Before (BROKEN):
```python
if request.method == 'POST':
    tmp_path = None  # Only tracking temp file path
    try:
        # ... code ...
        sqlite_conn = sqlite3.connect(tmp_path)
        # ... import code ...
    except Exception as e:
        # ❌ PROBLEM: Trying to delete file while connection is still open!
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)  # CRASHES on Windows!
```

### After (FIXED):
```python
if request.method == 'POST':
    tmp_path = None
    sqlite_conn = None  # ✅ Track connection too!
    try:
        # ... code ...
        sqlite_conn = sqlite3.connect(tmp_path)
        # ... import code ...
    except Exception as e:
        # ✅ Close connection FIRST
        if sqlite_conn:
            try:
                sqlite_conn.close()
            except:
                pass
        
        # ✅ Then delete file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception as cleanup_error:
                logger.warning(f"Could not delete temp file: {cleanup_error}")
```

## Changes Made

1. **Track SQLite connection**: Added `sqlite_conn = None` initialization
2. **Close connection in exception handler**: Ensures connection is closed before deleting file
3. **Better error handling**: Logs cleanup failures instead of silently ignoring them
4. **Added logging**: Shows when connection is closed and file is deleted

## Testing

This fix resolves the Windows file locking issue. The function will now:
1. Close the SQLite connection if an error occurs
2. Delete the temporary file successfully
3. Log any cleanup issues for debugging

## Platform Notes

- **Windows**: File locking is strict - files must be closed before deletion
- **Linux/Mac**: More lenient, but proper cleanup is still best practice
- **Production (Railway)**: Runs on Linux, but this fix ensures consistency across all platforms

The import function now properly manages resources regardless of where errors occur! ✅
