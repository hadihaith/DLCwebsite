import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("=" * 80)
print("ALL TABLES IN SQLITE DATABASE")
print("=" * 80)
for table in tables:
    table_name = table[0]
    print(f"\n📋 {table_name}")
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = cursor.fetchall()
    for col in cols:
        print(f"   - {col[1]} ({col[2]})")

conn.close()
