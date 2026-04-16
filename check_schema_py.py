import sqlite3

db_path = "backend/sql_app.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = ["work_sessions", "snapshots", "events"]
for table in tables:
    print(f"--- Schema for {table} ---")
    cursor.execute(f"PRAGMA table_info({table})")
    for row in cursor.fetchall():
        print(row)
    print()

conn.close()
