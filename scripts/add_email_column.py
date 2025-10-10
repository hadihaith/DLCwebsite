import sqlite3
import os
import sys

base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_path = os.path.join(base, 'db.sqlite3')

if not os.path.exists(db_path):
    print(f"ERROR: database not found at {db_path}")
    sys.exit(2)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

try:
    cur.execute("PRAGMA table_info('main_attendance')")
    cols = [r[1] for r in cur.fetchall()]
    if 'email' in cols:
        print('Column "email" already exists on main_attendance')
    else:
        # SQLite allows adding a column with ALTER TABLE
        cur.execute("ALTER TABLE main_attendance ADD COLUMN email VARCHAR(254);")
        conn.commit()
        print('Added column "email" to main_attendance')
except Exception as e:
    print('ERROR:', e)
    sys.exit(3)
finally:
    conn.close()
