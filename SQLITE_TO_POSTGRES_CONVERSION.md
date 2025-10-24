# SQLite to PostgreSQL Database Conversion

## 🎯 Overview

The DLC Portal now supports **automatic database conversion** from SQLite to PostgreSQL during the restore process. This makes migrating from local development (SQLite) to production (PostgreSQL) seamless.

## ✨ Features

### Supported Operations

| Source File | Target Database | Method | Status |
|------------|-----------------|--------|---------|
| SQLite (.sqlite3, .db, .sqlite) | SQLite | Direct file copy | ✅ Supported |
| SQLite (.sqlite3, .db, .sqlite) | PostgreSQL | Automatic conversion | ✅ **NEW!** |
| PostgreSQL (.backup, .sql, .dump) | PostgreSQL | pg_restore | ✅ Supported |
| PostgreSQL (.backup, .sql, .dump) | SQLite | - | ❌ Not supported |

### How It Works

The SQLite → PostgreSQL conversion uses Django's built-in `dumpdata` and `loaddata` management commands:

1. **Backup Current Data**: Creates JSON backup of current PostgreSQL database
2. **Extract SQLite Data**: Temporarily mounts SQLite file and exports all data to JSON
3. **Clear PostgreSQL**: Flushes current PostgreSQL database
4. **Import Data**: Loads SQLite data into PostgreSQL
5. **Run Migrations**: Ensures schema is up-to-date
6. **Cleanup**: Removes temporary files

## 🚀 Usage

### Via Portal Interface

1. **Login** as superuser or staff member
2. **Navigate** to Portal → "Restore Database"
3. **Upload** your SQLite database file (`.sqlite3`, `.db`, or `.sqlite`)
4. The system will:
   - Detect you're using PostgreSQL
   - Automatically convert SQLite → PostgreSQL
   - Show progress messages
   - Create backup (`.json` format)
5. **Login again** with credentials from the restored database

### What Happens During Conversion

```
┌─────────────────────────────────────────────────────────┐
│  1. Upload SQLite file (e.g., db.sqlite3)               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. Validate SQLite file (PRAGMA schema_version)        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. Backup current PostgreSQL to JSON                   │
│     → database_backups/auto_backup_before_restore_      │
│       YYYYMMDD_HHMMSS.json                              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. Mount SQLite as temporary database                  │
│     → settings.DATABASES['temp_sqlite']                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  5. Export SQLite data to JSON                          │
│     → database_backups/temp_sqlite_export_              │
│       YYYYMMDD_HHMMSS.json                              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  6. Flush PostgreSQL database                           │
│     → python manage.py flush --noinput                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  7. Load SQLite data into PostgreSQL                    │
│     → python manage.py loaddata [json_file]             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  8. Run migrations                                      │
│     → python manage.py migrate                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  9. Cleanup temporary files                             │
│     → Remove temp_sqlite_export_*.json                  │
│     → Remove uploaded SQLite file                       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  ✅ SUCCESS! SQLite data now in PostgreSQL              │
└─────────────────────────────────────────────────────────┘
```

## 📋 Step-by-Step Example

### Scenario: Migrate Local Development DB to Railway Production

**Local Environment:**
- Database: SQLite (`db.sqlite3`)
- Users, events, applications, dean list data

**Railway Production:**
- Database: PostgreSQL (Railway-managed)
- Currently empty or test data

### Steps:

#### 1. Download Local SQLite Database

From your local project:
```powershell
# Your SQLite database is at:
C:\Users\hadi\Desktop\DLC\Dlcweb\db.sqlite3

# Copy to a safe location
Copy-Item "db.sqlite3" "C:\Users\hadi\Downloads\dlc_backup.sqlite3"
```

#### 2. Access Railway Production

Navigate to your deployed app:
```
https://your-app.railway.app/login
```

Login with your current production credentials.

#### 3. Go to Restore Database Page

Click: **Portal** → **Restore Database**

#### 4. Upload SQLite File

- Click "Choose File"
- Select `dlc_backup.sqlite3`
- Check the confirmation box
- Click "Restore Database"

#### 5. Monitor Progress

You'll see messages like:
```
ℹ️ Converting SQLite to PostgreSQL... This may take a few minutes.
✅ SQLite database successfully converted and restored to PostgreSQL!
ℹ️ JSON backup saved: database_backups/auto_backup_before_restore_20251025_143022.json
⚠️ Please verify all data migrated correctly. Sequences may need reset.
```

#### 6. Login with Restored Credentials

After restoration, you'll be redirected to login.

**Use credentials from your LOCAL database** (the one you uploaded):
- Username: Your local admin username
- Password: Your local admin password

#### 7. Verify Data

Check that everything migrated:
- Users → User Management
- Events → Events Dashboard
- Applications → Exchange Applications
- Dean List students

## ⚠️ Important Notes

### What Gets Converted

✅ **Included:**
- All user accounts (with passwords)
- All applications (exchange, membership)
- All events and attendance
- All dean list data
- All threads and replies
- All courses
- Custom user fields (student_id, role, etc.)

❌ **Excluded:**
- Django's content types (auto-regenerated)
- Auth permissions (auto-regenerated)
- Media files (images, uploads) - use Cloudinary separately

### Data Types

Django handles most type conversions automatically:
- `INTEGER` → `integer`
- `TEXT` → `text`/`varchar`
- `REAL` → `numeric`/`float`
- `BLOB` → `bytea`
- `BOOLEAN` → `boolean`
- `DATETIME` → `timestamp`

### Sequences (Auto-Increment IDs)

After conversion, PostgreSQL sequences **may need to be reset** if you plan to add new records.

To reset sequences:
```bash
# On Railway terminal or via railway run
python manage.py sqlsequencereset main | python manage.py dbshell
```

Or reset specific tables:
```sql
-- Find current max ID
SELECT MAX(id) FROM main_user;

-- Reset sequence (replace 123 with actual max + 1)
SELECT setval('main_user_id_seq', 123);
```

## 🛡️ Safety Features

### Automatic Backups

Before any conversion, the system creates:

1. **PostgreSQL Backup** (JSON format)
   ```
   database_backups/auto_backup_before_restore_20251025_143022.json
   ```

2. **Temporary Export** (deleted after success)
   ```
   database_backups/temp_sqlite_export_20251025_143022.json
   ```

### Error Recovery

If conversion fails:
1. PostgreSQL database is automatically restored from backup
2. Error message shown with details
3. Original SQLite file preserved
4. No data loss on production

### Validation

- SQLite file validated before processing (`PRAGMA schema_version`)
- Django migrations ensure schema compatibility
- `dumpdata` uses `--natural-foreign` and `--natural-primary` for better compatibility

## 🔧 Manual Conversion (Alternative Method)

If you prefer manual control or need to customize:

### Step 1: Export from SQLite

On your local machine:
```powershell
# Export to JSON
python manage.py dumpdata --natural-foreign --natural-primary --exclude=contenttypes --exclude=auth.permission > data_export.json
```

### Step 2: Transfer to Production

Upload `data_export.json` to your Railway app via:
- Railway volume
- Temporary URL upload
- Git repository (if small)

### Step 3: Import to PostgreSQL

On Railway:
```bash
# Flush current database
python manage.py flush --noinput

# Load data
python manage.py loaddata data_export.json

# Run migrations
python manage.py migrate
```

## 🐛 Troubleshooting

### Error: "Uploaded file is not a valid SQLite database"

**Cause:** File corrupted or not a SQLite file

**Solution:**
- Verify file integrity: `sqlite3 db.sqlite3 "PRAGMA integrity_check;"`
- Re-download from source
- Check file isn't compressed (`.zip`, `.tar.gz`)

### Error: "SQLite to PostgreSQL conversion failed"

**Cause:** Data incompatibility or schema mismatch

**Solution:**
1. Check Django version matches between local/production
2. Run migrations locally first: `python manage.py migrate`
3. Export fresh JSON: `python manage.py dumpdata > fresh.json`
4. Try manual method (see above)

### Warning: "Sequences may need reset"

**Cause:** PostgreSQL auto-increment sequences out of sync

**Solution:**
```bash
# Reset all sequences
python manage.py sqlsequencereset main auth contenttypes | python manage.py dbshell
```

### Error: "Could not restore backup"

**Cause:** Backup restoration failed after conversion error

**Solution:**
1. Check `database_backups/` folder for JSON backup
2. Manually restore: `python manage.py loaddata auto_backup_before_restore_*.json`
3. Contact support with error logs

## 📊 Performance

### Conversion Time

Depends on database size:

| Records | Estimated Time |
|---------|---------------|
| < 1,000 | 10-30 seconds |
| 1,000 - 10,000 | 30-90 seconds |
| 10,000 - 100,000 | 2-5 minutes |
| > 100,000 | 5-15 minutes |

### Progress Indicators

During conversion, you'll see:
```
ℹ️ Converting SQLite to PostgreSQL... This may take a few minutes.
```

The page will appear to "hang" - this is normal! Wait for completion.

## 🎓 Best Practices

### Before Conversion

1. **Test locally first**
   ```powershell
   # Create test PostgreSQL database
   createdb test_dlc
   
   # Update settings temporarily
   # Run conversion locally
   ```

2. **Backup everything**
   - Download current PostgreSQL backup
   - Keep SQLite file safe
   - Save uploaded file copy

3. **Check data integrity**
   ```bash
   # Count records in SQLite
   sqlite3 db.sqlite3 "SELECT COUNT(*) FROM main_user;"
   
   # After conversion, verify in PostgreSQL
   python manage.py dbshell
   SELECT COUNT(*) FROM main_user;
   ```

### After Conversion

1. **Verify all data migrated**
   - User count matches
   - Events present
   - Applications intact
   - Dean list complete

2. **Test functionality**
   - Login with multiple users
   - Create test event
   - Submit test application
   - Upload test file (Cloudinary)

3. **Reset sequences if needed**
   ```bash
   python manage.py sqlsequencereset main | python manage.py dbshell
   ```

4. **Update credentials**
   - Change admin password
   - Update user emails if needed

## 🔗 Related Documentation

- [DATABASE_BACKUP_RESTORE.md](DATABASE_BACKUP_RESTORE.md) - Original backup/restore docs
- [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md) - PostgreSQL configuration
- [CLOUDINARY_SETUP.md](CLOUDINARY_SETUP.md) - File storage setup
- [MIGRATION_FIX.md](MIGRATION_FIX.md) - Database compatibility fixes

## 💡 Use Cases

### 1. Initial Production Deployment

You've built your app locally with SQLite and real data. Now deploying to Railway with PostgreSQL.

**Solution:** Upload SQLite file → automatic conversion → production ready!

### 2. Environment Migration

Moving from one hosting platform to another (both using different databases).

**Solution:** Download SQLite backup → upload to new platform → converted to PostgreSQL.

### 3. Data Recovery

Production PostgreSQL corrupted, but you have old SQLite backup.

**Solution:** Upload SQLite backup → converts to PostgreSQL → data restored.

### 4. Testing with Production Data

Want to test locally with real production data (but production uses PostgreSQL).

**Solution:** Download PostgreSQL backup → restore locally to SQLite → test away!

*(Note: PostgreSQL → SQLite not automated yet, use manual export/import)*

## 🎉 Summary

The SQLite to PostgreSQL conversion feature:

✅ **Automated** - No manual export/import needed
✅ **Safe** - Automatic backups, error recovery
✅ **Fast** - Optimized Django commands
✅ **Validated** - Schema checks, integrity tests
✅ **User-friendly** - Portal interface, clear messages

Perfect for deploying your local development database to production PostgreSQL!

---

**Questions?** Check the troubleshooting section or contact support.

**Last Updated:** October 25, 2025
