from django.db import migrations


def add_is_archived_column(apps, schema_editor):
    connection = schema_editor.connection
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(main_exchangeapplication);")
    columns = [row[1] for row in cursor.fetchall()]
    if 'is_archived' not in columns:
        cursor.execute("ALTER TABLE main_exchangeapplication ADD COLUMN is_archived BOOLEAN NOT NULL DEFAULT 0;")


def remove_is_archived_column(apps, schema_editor):
    # SQLite lacks easy column drop; leave as no-op.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_rename_accommodation_required_exchangeapplication_accommodation_needed_and_more'),
    ]

    operations = [
        migrations.RunPython(add_is_archived_column, remove_is_archived_column),
    ]
