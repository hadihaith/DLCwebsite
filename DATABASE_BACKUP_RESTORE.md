# Database Backup and Restore System

## Overview
A complete database backup and restore system for the DLC Portal, allowing superusers and staff to download the entire database as a file and restore from a backup when needed.

## Features

### ✅ Database Backup (Download)
- Download the entire SQLite database as a file
- Timestamped filenames for easy organization
- Instant download via browser
- No data loss or corruption
- Preserves all tables, relationships, and data

### ✅ Database Restore (Upload)
- Upload a database file to replace the current database
- Automatic backup before restoration
- Safety confirmations and warnings
- Validation of file types
- Auto-backups stored in `database_backups/` folder

## Access Control

**Who Can Use This:**
- ✅ **Superusers** (is_superuser=True)
- ✅ **Staff** (is_staff=True)

**Restrictions:**
- ❌ Regular members
- ❌ Non-authenticated users
- ❌ Mobile/tablet devices (desktop only)

## How to Use

### Backup Database (Download)

**Steps:**
1. Log in as superuser or staff
2. Navigate to **Portal** (sidebar menu)
3. Scroll to **"Database"** section
4. Click **"Download Database"**
5. Browser will download: `dlc_database_backup_YYYYMMDD_HHMMSS.sqlite3`

**Example Filename:**
```
dlc_database_backup_20251009_143022.sqlite3
```

**What Gets Downloaded:**
- Complete SQLite database file
- All tables and data
- All user accounts
- All events and attendance records
- All applications and threads
- All dean's list data
- All courses and sections

**File Size:** Typically 1-10 MB depending on data volume

**Use Cases:**
- Regular backups before major changes
- Before database restore operations
- Before system updates
- Archive for institutional records
- Transfer database between environments

---

### Restore Database (Upload)

**Steps:**
1. Log in as superuser or staff
2. Navigate to **Portal** → **"Restore Database"**
3. Read the **WARNING** carefully
4. Click **"Choose File"** and select a SQLite database file
5. Check the confirmation box:
   - ☑️ "I understand that this will replace the entire current database..."
6. Click **"Restore Database"**
7. Confirm the final warning dialog
8. System will:
   - Create automatic backup of current database
   - Replace database with uploaded file
   - Redirect to login page
9. **Log in using credentials from the restored database**

**Important Notes:**
- ⚠️ **Complete Replacement**: All current data will be replaced
- ⚠️ **Automatic Backup**: Current database is backed up automatically
- ⚠️ **Re-login Required**: You must log in again after restoration
- ⚠️ **Use Restored Credentials**: Use usernames/passwords from the restored database

**Accepted File Types:**
- `.sqlite3`
- `.db`
- `.sqlite`

---

## Safety Features

### Automatic Backup on Restore
Before any restore operation, the system automatically creates a backup:

**Backup Location:**
```
database_backups/auto_backup_before_restore_YYYYMMDD_HHMMSS.sqlite3
```

**Example:**
```
database_backups/auto_backup_before_restore_20251009_143530.sqlite3
```

### Multiple Confirmation Levels
1. **Visual Warning Banner** - Red gradient with warning icon
2. **Checkbox Confirmation** - Must check to enable button
3. **JavaScript Confirmation** - Final "Are you ABSOLUTELY SURE?" dialog

### File Validation
- Only SQLite database files accepted
- File extension validation (.sqlite3, .db, .sqlite)
- Engine type check (SQLite only)

### Error Handling
- Permission checks
- File existence validation
- Database engine verification
- Graceful error messages
- Automatic rollback on failure

---

## Portal Integration

### Sidebar Menu
New **"Database"** section appears for superusers/staff:

```
Tools
├── Search for a student
├── Manage Applications
├── Add a member
├── Manage members
├── Thread Settings
├── Events Dashboard
├── Refresh Courses
└── Create a New Dean's list

Database  ← New Section
├── Download Database
└── Restore Database
```

### Visual Indicators
- Download icon (cloud with down arrow)
- Restore icon (cloud with up arrow)
- Color-coded by importance

---

## Technical Details

### Database Type Support
- ✅ **SQLite** - Fully supported (default for development)
- ❌ **PostgreSQL** - Not supported (use pg_dump instead)
- ❌ **MySQL** - Not supported (use mysqldump instead)

### File Operations
```python
# Backup: Read binary file
with open(db_path, 'rb') as db_file:
    db_content = db_file.read()

# Restore: Write binary file
with open(db_path, 'wb') as destination:
    for chunk in uploaded_file.chunks():
        destination.write(chunk)
```

### Backup Directory Structure
```
dlcweb/
├── db.sqlite3                          ← Active database
├── database_backups/                   ← Auto-backups folder
│   ├── auto_backup_before_restore_20251009_143530.sqlite3
│   ├── auto_backup_before_restore_20251009_151245.sqlite3
│   └── auto_backup_before_restore_20251010_092015.sqlite3
└── manage.py
```

---

## Use Cases

### 1. Regular Backups
**Schedule:** Daily or before major operations
```
Action: Download Database
Frequency: Daily at end of day
Storage: External drive or cloud storage
Naming: Add date prefix for easy identification
```

### 2. Development Testing
**Scenario:** Test new features safely
```
1. Download current database (backup)
2. Test new features with real data
3. If issues occur, restore from backup
4. If successful, keep new database
```

### 3. Environment Migration
**Scenario:** Move from development to production
```
1. Download from development environment
2. Test backup file
3. Upload to production environment
4. Verify data integrity
```

### 4. Disaster Recovery
**Scenario:** Database corruption or accidental deletion
```
1. Identify most recent backup
2. Navigate to Restore Database
3. Upload backup file
4. Verify restored data
5. Resume operations
```

### 5. Semester Rollover
**Scenario:** Start fresh semester with base data
```
1. Download current database (archive)
2. Create clean database with base data
3. Upload clean database
4. Archive old database for records
```

### 6. Data Forensics
**Scenario:** Investigate past issues
```
1. Download multiple dated backups
2. Compare databases locally
3. Identify when issue occurred
4. Restore pre-issue database if needed
```

---

## Best Practices

### Backup Strategy
1. **Daily Backups**: Download database daily
2. **Before Changes**: Backup before major updates
3. **Version Control**: Name backups with dates
4. **Multiple Locations**: Store in multiple places
5. **Test Restores**: Periodically test restore process

### File Organization
```
backups/
├── 2025/
│   ├── 10_October/
│   │   ├── dlc_database_backup_20251001_090000.sqlite3
│   │   ├── dlc_database_backup_20251002_090000.sqlite3
│   │   └── dlc_database_backup_20251009_143022.sqlite3
│   ├── 11_November/
│   └── 12_December/
└── critical_milestones/
    ├── before_migration_20251015.sqlite3
    ├── before_semester_end_20251220.sqlite3
    └── before_system_upgrade_20251105.sqlite3
```

### Security
- ✅ Store backups in secure location
- ✅ Encrypt sensitive backups
- ✅ Limit access to backup files
- ✅ Don't commit backups to version control
- ✅ Regular backup testing

---

## Troubleshooting

### Error: "You do not have permission"
**Cause:** User is not superuser or staff
**Solution:** Log in with superuser/staff account

### Error: "Database backup is only available for SQLite"
**Cause:** Using PostgreSQL or MySQL
**Solution:** 
- For PostgreSQL: Use `pg_dump` command
- For MySQL: Use `mysqldump` command

### Error: "Invalid file type"
**Cause:** Uploaded file is not a SQLite database
**Solution:** Ensure file has `.sqlite3`, `.db`, or `.sqlite` extension

### Error: "Database file not found"
**Cause:** Database path is incorrect
**Solution:** Check `settings.py` DATABASES configuration

### Restore Doesn't Work
**Cause:** Wrong credentials after restore
**Solution:** Use username/password from the restored database

### Can't Login After Restore
**Cause:** Restored database has different user accounts
**Solution:** 
1. Restore the auto-backup from `database_backups/`
2. Or reset password via Django admin command

---

## Advanced Operations

### Manual Backup via Command Line
```bash
# Copy database file directly
copy db.sqlite3 backups\manual_backup_20251009.sqlite3

# Or use SQLite dump
sqlite3 db.sqlite3 .dump > backup.sql
```

### Restore from Command Line
```bash
# Replace database file
copy backups\manual_backup_20251009.sqlite3 db.sqlite3

# Or restore from SQL dump
sqlite3 db.sqlite3 < backup.sql
```

### View Auto-Backups
```bash
# List auto-backups
dir database_backups\

# View most recent
dir database_backups\ /O-D
```

### Clean Old Backups
```python
# Keep only last 10 backups
import os
from pathlib import Path

backup_dir = Path('database_backups')
backups = sorted(backup_dir.glob('*.sqlite3'), reverse=True)

# Delete all except last 10
for old_backup in backups[10:]:
    old_backup.unlink()
```

---

## Production Considerations

### PostgreSQL Production Environment
If using PostgreSQL in production (Heroku, etc.):

**Backup Command:**
```bash
heroku pg:backups:capture --app dlc-website
heroku pg:backups:download --app dlc-website
```

**Restore Command:**
```bash
heroku pg:backups:restore [BACKUP_URL] DATABASE_URL --app dlc-website
```

### Environment Variables
Check which database is active:
```python
# In settings.py
if os.environ.get('DATABASE_URL'):
    # Production: PostgreSQL
else:
    # Development: SQLite
```

---

## Security Warnings

⚠️ **Database files contain sensitive information:**
- User passwords (hashed)
- Email addresses
- Student IDs
- Personal information
- Application data

**Always:**
- ✅ Store backups securely
- ✅ Encrypt backup files
- ✅ Don't share publicly
- ✅ Don't commit to GitHub
- ✅ Use secure transfer methods

**Add to .gitignore:**
```
# Database files
*.sqlite3
database_backups/
*.db
```

---

## Future Enhancements

Potential improvements:
- Scheduled automatic backups
- Cloud storage integration (Google Drive, Dropbox)
- Backup encryption
- Backup comparison tools
- Database health checks
- Automated cleanup of old backups
- Email notifications on backup/restore
- Backup integrity verification
- Incremental backups
- Backup rotation policy

---

## Support

For issues:
1. Verify you have superuser/staff permissions
2. Check database type (SQLite only)
3. Ensure sufficient disk space
4. Check `database_backups/` folder permissions
5. Review Django logs for errors
6. Contact system administrator

## Summary

This system provides a complete backup and restore solution for SQLite databases, with automatic safety features, multiple confirmation levels, and comprehensive error handling. It's perfect for development environments and small-scale deployments using SQLite.
