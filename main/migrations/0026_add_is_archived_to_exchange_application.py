from django.db import migrations


def add_is_archived_column(apps, schema_editor):
    """
    Add is_archived column if it doesn't exist.
    Works with both SQLite and PostgreSQL.
    """
    connection = schema_editor.connection
    cursor = connection.cursor()
    
    # Check database type
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
    
    else:
        # For other databases (MySQL, etc.)
        try:
            cursor.execute("ALTER TABLE main_exchangeapplication ADD COLUMN is_archived BOOLEAN NOT NULL DEFAULT 0;")
        except Exception:
            # Column might already exist
            pass


def remove_is_archived_column(apps, schema_editor):
    """
    Remove is_archived column.
    Note: SQLite doesn't support DROP COLUMN easily, so this is a no-op for SQLite.
    """
    connection = schema_editor.connection
    db_vendor = connection.vendor
    
    if db_vendor == 'postgresql':
        cursor = connection.cursor()
        cursor.execute("ALTER TABLE main_exchangeapplication DROP COLUMN IF EXISTS is_archived;")
    # SQLite: no-op (can't easily drop columns)


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_rename_accommodation_required_exchangeapplication_accommodation_needed_and_more'),
    ]

    operations = [
        migrations.RunPython(add_is_archived_column, remove_is_archived_column),
    ]
