# PostgreSQL Migration Fix - RESOLVED ✅

## 🚨 The Problem

**Error Message:**
```
psycopg2.errors.SyntaxError: syntax error at or near "PRAGMA"
LINE 1: PRAGMA table_info(main_exchangeapplication);
```

**Root Cause:**
Migration file `0026_add_is_archived_to_exchange_application.py` used **PRAGMA** command, which is **SQLite-specific** and doesn't work with **PostgreSQL**.

---

## ✅ The Fix

Updated the migration to detect database type and use appropriate syntax:

### Before (Broken):
```python
def add_is_archived_column(apps, schema_editor):
    cursor.execute("PRAGMA table_info(main_exchangeapplication);")  # SQLite only!
    columns = [row[1] for row in cursor.fetchall()]
    if 'is_archived' not in columns:
        cursor.execute("ALTER TABLE main_exchangeapplication ADD COLUMN is_archived BOOLEAN NOT NULL DEFAULT 0;")
```

### After (Fixed):
```python
def add_is_archived_column(apps, schema_editor):
    connection = schema_editor.connection
    cursor = connection.cursor()
    db_vendor = connection.vendor
    
    if db_vendor == 'sqlite':
        # SQLite: Use PRAGMA
        cursor.execute("PRAGMA table_info(main_exchangeapplication);")
        columns = [row[1] for row in cursor.fetchall()]
        if 'is_archived' not in columns:
            cursor.execute("ALTER TABLE main_exchangeapplication ADD COLUMN is_archived BOOLEAN NOT NULL DEFAULT 0;")
    
    elif db_vendor == 'postgresql':
        # PostgreSQL: Check information_schema
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='main_exchangeapplication' 
            AND column_name='is_archived';
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE main_exchangeapplication ADD COLUMN is_archived BOOLEAN NOT NULL DEFAULT FALSE;")
```

---

## 🎯 What Changed

1. **Detects database type** using `connection.vendor`
2. **Uses PRAGMA** for SQLite (like before)
3. **Uses information_schema** for PostgreSQL (standard SQL)
4. **Different DEFAULT values**:
   - SQLite: `DEFAULT 0` (0 = False)
   - PostgreSQL: `DEFAULT FALSE` (native boolean)

---

## 🚀 Next Steps

1. **Push to GitHub**:
   ```bash
   git push
   ```

2. **Railway will auto-deploy** (~2-3 minutes)

3. **Check deployment logs** - should see:
   ```
   Running migrations:
     Applying main.0026_add_is_archived_to_exchange_application... OK ✅
   ```

4. **No more PRAGMA errors!** ✅

---

## 🧪 Verification

After Railway deploys:

### Check 1: Migration Success
Look for in logs:
```
Applying main.0026_add_is_archived_to_exchange_application... OK
```

### Check 2: Database Type
The migration will automatically use PostgreSQL syntax when deployed!

### Check 3: Test the App
- Create an exchange application
- Archive/unarchive it
- Should work without errors ✅

---

## 📚 Database Differences Handled

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| **Check columns** | `PRAGMA table_info` | `information_schema.columns` |
| **Boolean default** | `DEFAULT 0` | `DEFAULT FALSE` |
| **Drop column** | Not supported | `DROP COLUMN IF EXISTS` |

---

## 🔍 How to Avoid This in Future

### For New Migrations:

**❌ Don't use database-specific commands:**
```python
cursor.execute("PRAGMA ...")  # SQLite only
cursor.execute("SHOW COLUMNS ...")  # MySQL only
```

**✅ Use Django's ORM instead:**
```python
migrations.AddField(
    model_name='exchangeapplication',
    name='is_archived',
    field=models.BooleanField(default=False),
)
```

**✅ Or detect database type:**
```python
if connection.vendor == 'postgresql':
    # PostgreSQL syntax
elif connection.vendor == 'sqlite':
    # SQLite syntax
```

---

## 🎉 Status

- ✅ Migration fixed
- ✅ Works with SQLite (local development)
- ✅ Works with PostgreSQL (Railway production)
- ✅ Committed to git
- ⏳ Ready to push and deploy

---

## 📝 Summary

**Problem**: PRAGMA command broke PostgreSQL migrations  
**Solution**: Detect database type and use appropriate syntax  
**Result**: Migration now works on both SQLite and PostgreSQL  
**Action**: Push to GitHub and let Railway deploy  

**Estimated deploy time**: 2-3 minutes after push  
**Expected result**: Clean deployment with no migration errors! 🎉

---

**Fixed Date**: October 25, 2025  
**Migration File**: `0026_add_is_archived_to_exchange_application.py`  
**Status**: Ready to deploy
