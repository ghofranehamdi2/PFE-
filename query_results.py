#!/usr/bin/env python3
"""
Query and display model output from PostgreSQL database
and show sample JSON snapshot output
"""
import psycopg2
import json
from datetime import datetime
import sys

# Database connection
def connect_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="smart_focus",
            user="postgres",
            password="postgres",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def format_json(obj):
    """Pretty print JSON output"""
    return json.dumps(obj, indent=2, default=str)

def display_results():
    conn = connect_db()
    if not conn:
        print("Attempting to use SQLite instead...")
        display_sqlite_results()
        return
    
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 LATEST WORK SESSIONS")
    print("="*80)
    cursor.execute("""
        SELECT id, start_time, end_time, is_active 
        FROM work_sessions 
        ORDER BY start_time DESC 
        LIMIT 3
    """)
    sessions = cursor.fetchall()
    for row in sessions:
        print(f"  Session ID: {row[0]}")
        print(f"  Started: {row[1]}")
        print(f"  Ended: {row[2]}")
        print(f"  Active: {row[3]}\n")
    
    print("="*80)
    print("📈 LATEST SNAPSHOTS & SCORES")
    print("="*80)
    cursor.execute("""
        SELECT session_id, timestamp, work_mode, attention_score, posture_score, 
               vigilance_score, stress_risk_score, global_focus_score
        FROM snapshots 
        ORDER BY timestamp DESC 
        LIMIT 5
    """)
    snapshots = cursor.fetchall()
    if snapshots:
        for row in snapshots:
            print(f"  [{row[1]}]")
            print(f"    Session: {row[0]}")
            print(f"    Work Mode: {row[2]}")
            print(f"    Attention Score: {row[3]}")
            print(f"    Posture Score: {row[4]}")
            print(f"    Vigilance Score: {row[5]}")
            print(f"    Stress Risk Score: {row[6]}")
            print(f"    🎯 Global Focus Score: {row[7]}\n")
    else:
        print("  No snapshots found in database\n")
    
    print("="*80)
    print("⚠️  LATEST EVENTS/ALERTS")
    print("="*80)
    cursor.execute("""
        SELECT timestamp, event_type, level, description 
        FROM events 
        ORDER BY timestamp DESC 
        LIMIT 5
    """)
    events = cursor.fetchall()
    if events:
        for row in events:
            print(f"  [{row[0]}] {row[2].upper()}: {row[1]}")
            print(f"    Description: {row[3]}\n")
    else:
        print("  No events found in database\n")
    
    # Get the raw JSON payload from latest snapshot
    print("="*80)
    print("📄 LATEST JSON SNAPSHOT PAYLOAD")
    print("="*80)
    cursor.execute("""
        SELECT raw_payload_json
        FROM snapshots 
        ORDER BY timestamp DESC 
        LIMIT 1
    """)
    result = cursor.fetchone()
    if result:
        payload = result[0]
        print(format_json(payload))
    else:
        print("  No snapshot data available")
    
    conn.close()

def display_sqlite_results():
    """Fallback to SQLite if PostgreSQL unavailable"""
    import sqlite3
    
    db_path = "backend/sql_app_v3.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n" + "="*80)
        print("📊 LATEST WORK SESSIONS (SQLite)")
        print("="*80)
        cursor.execute("""
            SELECT id, start_time FROM work_sessions 
            ORDER BY start_time DESC LIMIT 3
        """)
        for row in cursor.fetchall():
            print(f"  Session: {row[0]}\n  Started: {row[1]}\n")
        
        print("="*80)
        print("📈 LATEST SNAPSHOTS & SCORES (SQLite)")
        print("="*80)
        cursor.execute("""
            SELECT session_id, timestamp, work_mode, global_focus_score, posture_score
            FROM snapshots 
            ORDER BY timestamp DESC LIMIT 5
        """)
        for row in cursor.fetchall():
            print(f"  [{row[1]}] Mode: {row[2]}")
            print(f"    Focus: {row[3]}, Posture: {row[4]}\n")
        
        print("="*80)
        print("⚠️  LATEST EVENTS (SQLite)")
        print("="*80)
        cursor.execute("""
            SELECT timestamp, event_type, description 
            FROM events ORDER BY timestamp DESC LIMIT 5
        """)
        for row in cursor.fetchall():
            print(f"  [{row[0]}] {row[1]}: {row[2]}\n")
        
        conn.close()
    except Exception as e:
        print(f"❌ SQLite query failed: {e}")

if __name__ == "__main__":
    display_results()
