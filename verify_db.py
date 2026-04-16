import sqlite3
import json
import os

db_path = "backend/sql_app_v2.db"

if not os.path.exists(db_path):
    print(f"Error: Database {db_path} not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- LATEST WORK SESSIONS ---")
cursor.execute("SELECT id, start_time FROM work_sessions ORDER BY start_time DESC LIMIT 5")
for row in cursor.fetchall():
    print(f"Session: {row[0]} | Started: {row[1]}")

print("\n--- LATEST SNAPSHOTS & SCORES ---")
cursor.execute("""
    SELECT session_id, timestamp, work_mode, global_focus_score, posture_score 
    FROM snapshots 
    ORDER BY timestamp DESC 
    LIMIT 3
""")
for row in cursor.fetchall():
    print(f"[{row[1]}] Mode: {row[2]} | Focus: {row[3]} | Posture: {row[4]}")

print("\n--- LATEST EVENTS/ALERTS ---")
cursor.execute("SELECT timestamp, event_type, description FROM events ORDER BY timestamp DESC LIMIT 3")
for row in cursor.fetchall():
    print(f"[{row[0]}] {row[1].upper()}: {row[2]}")

conn.close()
